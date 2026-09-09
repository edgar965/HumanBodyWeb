import { state } from './state.js';
import { _selectedInst } from './utils.js';
import { convertInstToSkinned } from './skeleton.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Posenanwendung — eine gespeicherte Pose auf die ausgewählte Figur legen.
 *
 * Herausgelöst aus `pose_apply.js` (236 Zeilen). Das ist der rechnende Teil, und
 * er hat vier Eigenheiten, die man kennen muss:
 *
 * 1. **Die A-Pose wird beim ersten Mal gesichert** (`_aPoseBones`). Posen sind
 *    DELTAS auf die Ruhelage; ohne die Sicherung addiert jede weitere Pose auf
 *    die vorige, und die Figur verdreht sich mit jedem Klick weiter.
 * 2. **Punkte in Knochennamen werden zu Unterstrichen.** Three.js liest einen
 *    Punkt als Trenner (`DEF-thigh.L` -> Objekt „DEF-thigh", Eigenschaft „L").
 * 3. **Gliedmaßen-Wurzeln werden nachkorrigiert.** Oberarm und Oberschenkel
 *    hängen an einem Elternknochen, den die Pose mitgedreht hat. Ohne die
 *    Korrektur (`premultiply` mit der Differenz der Elterndrehung) wandern Arme
 *    und Beine doppelt — der Grund für „die Figur macht Spagat".
 * 4. **T-Pose richtet die Oberschenkel gerade nach unten.** MB-Labs T-Pose
 *    spreizt die Beine weniger als Rigify; ohne diese Korrektur stehen sie
 *    schräg (siehe `leg_multiplier` im Kern).
 */
export class Posenanwendung {

    /** Knochen, deren Elterndrehung nachkorrigiert werden muss. */
    static GLIEDWURZELN = ['DEF-upper_arm.L', 'DEF-upper_arm.R',
                           'DEF-thigh.L', 'DEF-thigh.R'];
    /** Oberschenkel und ihr Kind — für die T-Pose-Korrektur. */
    static OBERSCHENKEL = [['DEF-thigh_L', 'DEF-thigh_L_001'],
                           ['DEF-thigh_R', 'DEF-thigh_R_001']];
    /** Ab dieser Übereinstimmung gilt die Richtung als schon richtig. */
    static GENAU_GENUG = 0.9999;

    constructor(figur) {
        this.figur = figur;
        this.skelett = Posenanwendung.skelett(figur);
    }

    /** Das erste `SkinnedMesh`-Skelett der Figur — oder `null`. */
    static skelett(figur) {
        let gefunden = null;
        figur.group.traverse(teil => {
            if (!gefunden && teil.isSkinnedMesh && teil.skeleton) {
                gefunden = teil.skeleton;
            }
        });
        return gefunden;
    }

    static jsName(name) {
        return name.replace(/\./g, '_');
    }

    // --------------------------------------------------------------- Ruhelage

    /** Die Ruhelage sichern (einmal) und die Knochen darauf zurücksetzen. */
    ruhelageHerstellen() {
        if (!this.figur._aPoseBones) {
            this.figur._aPoseBones = {};
            for (const knochen of this.skelett.bones) {
                this.figur._aPoseBones[knochen.name] = knochen.quaternion.clone();
            }
        }
        for (const knochen of this.skelett.bones) {
            const gesichert = this.figur._aPoseBones[knochen.name];
            if (gesichert) knochen.quaternion.copy(gesichert);
        }
    }

    // ------------------------------------------------------------------ Anwenden

    /** Die Drehungen einer Pose anwenden; liefert die Zahl der Knochen. */
    anwenden(drehungen) {
        const Quat = this.skelett.bones[0].quaternion.constructor;
        this.ruhelageHerstellen();
        this.skelett.bones[0].updateWorldMatrix(true, true);
        const elternVorher = this._elterndrehungen(Quat);
        let gesetzt = 0;
        for (const [name, wert] of Object.entries(drehungen || {})) {
            const knochen = this.skelett.getBoneByName(
                Posenanwendung.jsName(name));
            if (!knochen) continue;
            knochen.quaternion.multiply(
                new Quat(wert[0], wert[1], wert[2], wert[3]));
            gesetzt++;
        }
        this.skelett.bones[0].updateWorldMatrix(true, true);
        this._gliederKorrigieren(elternVorher, Quat);
        this.skelett.bones[0].updateWorldMatrix(true, true);
        return gesetzt;
    }

    /** Weltdrehung der Eltern der Gliedwurzeln VOR der Pose. */
    _elterndrehungen(Quat) {
        const drehungen = {};
        for (const name of Posenanwendung.GLIEDWURZELN) {
            const knochen = this.skelett.getBoneByName(
                Posenanwendung.jsName(name));
            if (!knochen?.parent) continue;
            const drehung = new Quat();
            knochen.parent.getWorldQuaternion(drehung);
            drehungen[name] = drehung;
        }
        return drehungen;
    }

    /**
     * Die doppelte Drehung der Gliedmaßen herausrechnen.
     *
     * Die Pose hat den Elternknochen (Schulter, Hüfte) mitgedreht; der Arm hat
     * seine eigene Drehung dazu. Beides zusammen ist zu viel — deshalb wird die
     * DIFFERENZ der Elterndrehung vorne wieder herausmultipliziert.
     */
    _gliederKorrigieren(elternVorher, Quat) {
        for (const name of Posenanwendung.GLIEDWURZELN) {
            const vorher = elternVorher[name];
            if (!vorher) continue;
            const knochen = this.skelett.getBoneByName(
                Posenanwendung.jsName(name));
            if (!knochen?.parent) continue;
            const nachher = new Quat();
            knochen.parent.getWorldQuaternion(nachher);
            knochen.quaternion.premultiply(
                nachher.clone().invert().multiply(vorher));
        }
    }

    // ------------------------------------------------------------- T-Pose-Beine

    /** Oberschenkel gerade nach unten drehen — nur bei einer T-Pose. */
    oberschenkelGeradeStellen(poseId) {
        if (!poseId.includes('t-pose') && !poseId.includes('tpose')) return 0;
        let korrigiert = 0;
        for (const [name, kindname] of Posenanwendung.OBERSCHENKEL) {
            if (this._oberschenkel(name, kindname)) korrigiert++;
        }
        return korrigiert;
    }

    _oberschenkel(name, kindname) {
        const knochen = this.skelett.getBoneByName(name);
        const kind = this.skelett.getBoneByName(kindname);
        if (!knochen || !kind) return false;
        const Vec3 = knochen.position.constructor;
        const Quat = knochen.quaternion.constructor;
        const kopf = new Vec3();
        const fuss = new Vec3();
        knochen.getWorldPosition(kopf);
        kind.getWorldPosition(fuss);
        const ist = fuss.clone().sub(kopf).normalize();
        const soll = new Vec3(0, -1, 0);
        if (ist.dot(soll) > Posenanwendung.GENAU_GENUG) return false;
        const korrektur = new Quat().setFromUnitVectors(ist, soll);
        const eltern = new Quat();
        if (knochen.parent) knochen.parent.getWorldQuaternion(eltern);
        // Die Korrektur ist in WELT-Koordinaten gemeint; sie muss in den
        // Elternraum des Knochens übersetzt werden.
        knochen.quaternion.premultiply(
            eltern.clone().invert().multiply(korrektur).multiply(eltern));
        return true;
    }

    // ----------------------------------------------------------------- Ablauf

    /**
     * Taugt diese Figur für eine Pose? — `{ok}` oder `{ok: false, grund}`.
     *
     * Posen sind Deltas auf RIGIFY-Knochennamen (`DEF-thigh.L`). Eine SMPL-,
     * MakeHuman- oder UMA-Figur führt ihr EIGENES Skelett mit eigenen Namen
     * (`Pelvis`, `Spine1`); dort trifft kein einziger Name, `anwenden` setzt
     * null Knochen, und die Figur bleibt stehen — ohne Fehler und ohne
     * Meldung. Die HumanBody-Figur ist die einzige ohne `quelle`.
     */
    static pruefen(figur) {
        if (!figur) {
            return { ok: false, grund: 'Keine Figur gewählt.' };
        }
        if (figur.quelle) {
            return { ok: false,
                     grund: 'Posen gelten für HumanBody-Figuren; diese Figur '
                            + `kommt von ${figur.quelle}.` };
        }
        return { ok: true };
    }

    /**
     * Eine Pose vom Server holen und anwenden.
     *
     * Liefert `{ok, grund, gesetzt}`: **jeder** Ausstieg nennt seinen Grund.
     * Bis zum 09.09.2026 kehrte die Methode an fünf Stellen wortlos zurück
     * (keine Figur, nicht gehäutet, Serverfehler, kein Skelett, kein Treffer)
     * — im Bild sieht das genauso aus wie ein Knopf, der nicht funktioniert.
     *
     * Ohne Fänger um den Abruf endet ein Serverfehler in einer stillen
     * „Unhandled promise rejection". Der Aufruf kommt aus der Liste, aus dem
     * Kontextmenü, aus dem Hauptmenü und aus dem Szenenaufbau.
     */
    static async vomServer(poseId) {
        const figur = _selectedInst();
        const befund = Posenanwendung.pruefen(figur);
        if (!befund.ok) return befund;
        if (!figur.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
            convertInstToSkinned(figur);
        }
        if (!figur.isSkinned) {
            return { ok: false, grund: 'Figur hat kein Skelett zum Stellen.' };
        }
        const antwort = await Posenanwendung._holen(poseId);
        if (antwort.grund) return { ok: false, grund: antwort.grund };
        if (!antwort.daten?.bones) {
            return { ok: false, grund: 'Die Pose führt keine Knochen.' };
        }
        return Posenanwendung._stellen(figur, poseId, antwort.daten);
    }

    /** Die geholte Pose auf die Figur legen. */
    static _stellen(figur, poseId, daten) {
        const anwendung = new Posenanwendung(figur);
        if (!anwendung.skelett) {
            return { ok: false, grund: 'Kein gehäutetes Netz an dieser Figur.' };
        }
        const gesetzt = anwendung.anwenden(daten.threejs || {});
        const beine = anwendung.oberschenkelGeradeStellen(poseId);
        Protokoll.debug('Pose', `${poseId}: ${gesetzt} Knochen, `
                        + `${beine} Beinkorrekturen`);
        if (!gesetzt) {
            return { ok: false,
                     grund: 'Kein Knochen der Pose passt zu diesem Skelett.' };
        }
        return { ok: true, gesetzt, beine };
    }

    static async _holen(poseId) {
        try {
            return { daten: await Serverabruf.json(
                `/api/character/pose/${poseId}/`) };
        } catch (fehler) {
            Protokoll.fehler('Pose', poseId, fehler);
            return { grund: 'Pose nicht ladbar: ' + fehler.message };
        }
    }

    /** Die Figur zurück in die gesicherte Ruhelage. */
    static zuruecksetzen() {
        const figur = _selectedInst();
        const befund = Posenanwendung.pruefen(figur);
        if (!befund.ok) return befund;
        if (!figur.isSkinned || !figur._aPoseBones) {
            return { ok: false,
                     grund: 'Noch keine Pose gestellt — nichts zurückzunehmen.' };
        }
        const anwendung = new Posenanwendung(figur);
        if (!anwendung.skelett) {
            return { ok: false, grund: 'Kein gehäutetes Netz an dieser Figur.' };
        }
        anwendung.ruhelageHerstellen();
        return { ok: true };
    }
}
