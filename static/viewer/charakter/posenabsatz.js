import { state } from './state.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Posenabsatz — der Absatzschuh als Teil der Pose einer Figur.
 *
 * WARUM (Edgar, 11.09.2026: „der Betrachter soll bei einem Absatzschuh gar
 * nichts tun, sondern das Programm soll die Pose ändern!"): Die Beugung
 * rechnet der Server in jede Pose hinein (`core/dienste/absatzpose.py`,
 * `GET /api/character/pose/<id>/?winkel_grad=…`). Hier steht nur, WAS die
 * Figur gerade trägt (`figur.absatz`), damit jede Pose — auch die
 * Ruhelage — mit diesen Zahlen geholt wird, und der Hub, den eine Pose
 * nicht ausdrücken kann: `hebung_m` hebt die Figurgruppe, damit die Zehen
 * auf dem Boden bleiben. `Character._lage` zieht ihn beim Speichern ab.
 *
 * `figur.absatz` = `{winkel_grad, sprengung_grad, hebung_cm, plateau_cm,
 * quelle}` oder null; `quelle` sagt, ob die Zahlen vom getragenen Schuh
 * (`schuh:<stueck>`) oder von den Reglern (`regler`) kommen.
 *
 * BEI EINER ANIMATION (Edgar, 11.09.2026: „Der Schuh sollte ja die Pose
 * nur an der Ferse ändern, jetzt hebt er das ganze Modell gleichmässig",
 * dann „Schau doch nach, wie MakeHuman das macht"): MakeHuman mischt die
 * Fusspose eines Schuhs in JEDE Pose (`plugins/2_foot_posing.py`,
 * `animation.mixPoses` über die Fussknochen). Hier stellte der Mixer die
 * Füsse je Bild neu — die Beugung war weg, nur der Hub blieb, und die Figur
 * schwebte mit flachen Füssen. `takt` mischt deshalb nach jedem Mixer-Bild
 * die Fussdeltas des Servers (`absatz_deltas`) nach, und nur, wenn der
 * Mixer den Knochen in diesem Bild angefasst hat — sonst summierte sich die
 * Drehung Bild für Bild.
 */
export class Posenabsatz {

    static FELDER = ['winkel_grad', 'sprengung_grad', 'hebung_cm', 'plateau_cm'];

    /** Trägt diese Figur einen Absatz? */
    static aktiv(figur) {
        const a = figur?.absatz;
        return !!a && (a.winkel_grad > 0 || a.sprengung_grad > 0);
    }

    /** Die Abfrage für `/api/character/pose/<id>/` — Absatz und Skelett. */
    static abfrage(figur) {
        const teile = [];
        const koerpertyp = figur?.bodyType || figur?.body_type;
        if (koerpertyp) teile.push(`body_type=${encodeURIComponent(koerpertyp)}`);
        if (Posenabsatz.aktiv(figur)) {
            for (const feld of Posenabsatz.FELDER) {
                teile.push(`${feld}=${encodeURIComponent(figur.absatz[feld] || 0)}`);
            }
        }
        return teile.length ? `?${teile.join('&')}` : '';
    }

    /** Die Figur um den Hub der Pose heben (oder wieder senken). */
    static heben(figur, hebungM) {
        const bisher = figur.group.userData.absatzHub || 0;
        const hub = Number(hebungM) || 0;
        figur.group.position.y += hub - bisher;
        figur.group.userData.absatzHub = hub;
        if (hub !== bisher) {
            Protokoll.info('Pose', hub
                ? `Absatz: Figur steht ${(hub * 100).toFixed(1)} cm höher`
                : 'Absatz abgesetzt: Figur steht wieder flach');
        }
    }

    /**
     * Den Absatz einer Figur setzen (oder mit null nehmen) und ihre Pose
     * neu vom Server holen — die trägt die Beugung dann mit. `stellen` ist
     * `Posenanwendung.vomServer`, hereingereicht, damit die beiden Module
     * einander nicht im Kreis importieren.
     */
    static async setzen(figur, info, stellen) {
        const neu = info ? { ...info } : null;
        const gleich = JSON.stringify(Posenabsatz._zahlen(figur.absatz))
            === JSON.stringify(Posenabsatz._zahlen(neu));
        figur.absatz = neu;
        if (gleich && !figur.absatzOffen) return { ok: true, unveraendert: true };
        figur.absatzOffen = true;
        const ergebnis = await stellen(figur.poseId || 'ruhelage', figur);
        if (ergebnis.ok) figur.absatzOffen = false;
        else Protokoll.warnung('Pose', `Absatz nicht gestellt: ${ergebnis.grund}`);
        return ergebnis;
    }

    // ------------------------------------------------------- Animation

    /** Die reinen Fussdeltas der letzten Pose an der Figur merken. */
    static deltasMerken(figur, deltas) {
        figur.absatzDeltas = deltas && Object.keys(deltas).length ? deltas : null;
        figur._absatzGemischt = {};
    }

    /** Nach dem Mixer: die Fussdeltas auf die animierte Figur mischen. */
    static takt() {
        if (!state.mixer || !state.playing) return 0;
        const wurzel = state.mixer.getRoot();
        let gemischt = 0;
        for (const figur of state.characters.values()) {
            if (!figur.absatzDeltas || !Posenabsatz._traegt(figur, wurzel)) continue;
            gemischt += Posenabsatz.mischen(figur);
        }
        return gemischt;
    }

    /** Fussdeltas auf die Knochen multiplizieren, die der Mixer neu gesetzt hat. */
    static mischen(figur) {
        let skelett = null;
        figur.group.traverse((teil) => {
            if (!skelett && teil.isSkinnedMesh && teil.skeleton) skelett = teil.skeleton;
        });
        if (!skelett) return 0;
        const gemischt = figur._absatzGemischt || (figur._absatzGemischt = {});
        let n = 0;
        for (const [name, wert] of Object.entries(figur.absatzDeltas)) {
            const knochen = skelett.getBoneByName(name.replace(/\./g, '_'));
            if (!knochen) continue;
            const vorher = gemischt[name];
            if (vorher && knochen.quaternion.equals(vorher)) continue;
            const Quat = knochen.quaternion.constructor;
            knochen.quaternion.multiply(new Quat(wert[0], wert[1], wert[2], wert[3]));
            gemischt[name] = knochen.quaternion.clone();
            n++;
        }
        return n;
    }

    /** Hängt die Mixer-Wurzel in der Gruppe dieser Figur? */
    static _traegt(figur, wurzel) {
        for (let o = wurzel; o; o = o.parent) if (o === figur.group) return true;
        return false;
    }

    static _zahlen(info) {
        if (!info || !(info.winkel_grad > 0 || info.sprengung_grad > 0)) return null;
        return Posenabsatz.FELDER.map((f) => Number(info[f] || 0).toFixed(3));
    }
}
