import { state, API } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { wizardState, showWizardModal } from './wizard.js';
import { renderWizardCanvas } from './wizard_zeichnen.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Ausrichtungsvorschau } from './ausrichtungsvorschau.js';

/**
 * Ausrichtassistent — startet den Assistenten, mit dem der Umriss des Modells
 * von Hand auf die Person im Foto gelegt wird.
 *
 * Aus wizard_ablauf.js herausgeloest (Umbau 16.08.2026): `startWizard()` hatte
 * 104 Zeilen — Daten holen, Foto laden, drei Fälle für die Anfangslage des
 * Körpers, zwei für das Gesicht, dann das Übernehmen einer gespeicherten
 * Ausrichtung.
 *
 * FEHLER dabei gefunden: Bei einer POSIERTEN Figur ist `bodyTransform` eine
 * VERSCHIEBUNG (Start 0/0), bei einer unbewegten die ZIELMITTE. Das gespeicherte
 * `body_transform` des Servers enthält aber immer eine Zielmitte — es wurde
 * ungeprüft übernommen. Für den Auftrag im Test bedeutete das dx=959 bei einem
 * 1920 breiten Foto: Der Umriss lag eine halbe Bildbreite daneben, halb
 * außerhalb der Leinwand. Im posierten Fall zählt jetzt nur `proj_2d_offset`,
 * das der Assistent selbst schreibt und das der Server genauso versteht
 * (siehe `Texturbacken.versatz_anwenden`).
 */
export class Ausrichtassistent {

    /** Der Umriss soll etwas kleiner als der erkannte Rahmen sein. */
    static EINPASS_ANTEIL = 0.95;
    /** Anfangslage einer posierten Figur: keine Verschiebung, keine Skalierung. */
    static OHNE_VERSCHIEBUNG = { center_x: 0, center_y: 0, scale: 1.0 };

    async starten() {
        if (!state.currentJobId) return null;
        const knopf = document.getElementById('btn-start-wizard');
        if (knopf) {
            knopf.classList.add('loading');
            knopf.disabled = true;
        }
        try {
            const daten = await this._silhouette();
            if (!daten) return null;
            wizardState.data = daten;
            if (!await this._foto()) return null;
            this._anfangslage(daten);
            this._gespeichertesUebernehmen(daten);
            wizardState.step = 0;
            showWizardModal();
            renderWizardCanvas();
            return wizardState;
        } catch (fehler) {
            console.error('Assistent nicht startbar:', fehler);
            alert('Wizard konnte nicht gestartet werden: ' + fehler.message);
            return null;
        } finally {
            if (knopf) {
                knopf.classList.remove('loading');
                knopf.disabled = false;
            }
            fn.enableTextureButtons();
        }
    }

    async _silhouette() {
        const daten = await Serverabruf.json(
            `${API}/photo-job/${state.currentJobId}/silhouette/`);
        if (daten.ok) return daten;
        alert('Silhouette-Daten konnten nicht geladen werden: '
              + (daten.error || ''));
        return null;
    }

    async _foto() {
        const quelle = document.getElementById('photo-img')?.src;
        if (!quelle) {
            alert('Kein Foto geladen');
            return false;
        }
        // Dasselbe Laden wie in `Ausrichtungsvorschau` — dort steht es
        // (Befund `doppelcode`, 30.08.2026). `crossOrigin` gehoert dazu: Ohne
        // das faerbt das Bild die Leinwand ein, und `getImageData` wirft
        // danach — an einer ganz anderen Stelle.
        wizardState.photoImg = await Ausrichtungsvorschau.bildLaden(quelle);
        return true;
    }

    // ------------------------------------------------------------- Anfangslage

    _anfangslage(daten) {
        const rahmen = daten.mesh_bbox;
        const netzmitte = [rahmen.x + rahmen.w / 2, rahmen.y + rahmen.h / 2];
        wizardState.bodyTransform = daten.use_posed
            ? { ...Ausrichtassistent.OHNE_VERSCHIEBUNG }
            : this._koerperlage(daten, rahmen, netzmitte);
        wizardState.bodyTransformInit = { ...wizardState.bodyTransform };
        wizardState.faceTransform = daten.use_posed
            ? { ...Ausrichtassistent.OHNE_VERSCHIEBUNG }
            : this._gesichtslage(daten, netzmitte);
        wizardState.faceTransformInit = { ...wizardState.faceTransform };
    }

    /**
     * Unbewegte Figur: Der Umriss wird in den YOLO-Rahmen der Person gepasst.
     * Ohne YOLO-Rahmen bleibt er in der Mitte des Netzrahmens.
     */
    _koerperlage(daten, rahmen, netzmitte) {
        if (!daten.yolo_bbox) {
            return { center_x: netzmitte[0], center_y: netzmitte[1], scale: 1.0 };
        }
        const [x1, y1, x2, y2] = daten.yolo_bbox;
        const breite = rahmen.w > 0 ? (x2 - x1) / rahmen.w : 1;
        const hoehe = rahmen.h > 0 ? (y2 - y1) / rahmen.h : 1;
        return {
            center_x: (x1 + x2) / 2,
            center_y: (y1 + y2) / 2,
            scale: Math.min(breite, hoehe) * Ausrichtassistent.EINPASS_ANTEIL,
        };
    }

    /**
     * Gesicht: in den erkannten Gesichtsrahmen passen. Der Gesichtsrahmen des
     * Netzes sitzt nicht in der Netzmitte, deshalb wird sein Versatz
     * mitskaliert — sonst wandert das Gesicht beim Skalieren weg.
     */
    _gesichtslage(daten, netzmitte) {
        const erkannt = daten.face_bbox_detected || daten.face_bbox_mesh;
        const imNetz = daten.face_bbox_mesh;
        if (!erkannt || !imNetz) return { ...wizardState.bodyTransform };
        const breite = imNetz.w > 0 ? erkannt.w / imNetz.w : 1;
        const hoehe = imNetz.h > 0 ? erkannt.h / imNetz.h : 1;
        const maszstab = Math.min(breite, hoehe);
        const versatzX = (imNetz.x + imNetz.w / 2) - netzmitte[0];
        const versatzY = (imNetz.y + imNetz.h / 2) - netzmitte[1];
        return {
            center_x: erkannt.x + erkannt.w / 2 - versatzX * maszstab,
            center_y: erkannt.y + erkannt.h / 2 - versatzY * maszstab,
            scale: maszstab,
        };
    }

    // --------------------------------------------------- Gespeicherte Ausrichtung

    _gespeichertesUebernehmen(daten) {
        const gespeichert = daten.saved_alignment;
        if (!gespeichert) return;
        if (daten.use_posed) {
            // Nur die eigene Feinkorrektur des Assistenten übernehmen. Ein
            // `body_transform` ist hier eine Zielmitte und keine Verschiebung —
            // es würde den Umriss um seinen ganzen Betrag versetzen.
            const versatz = gespeichert.proj_2d_offset;
            if (versatz) {
                wizardState.bodyTransform = {
                    center_x: versatz.dx || 0,
                    center_y: versatz.dy || 0,
                    scale: versatz.scale || 1,
                };
            }
        } else if (gespeichert.body_transform) {
            wizardState.bodyTransform = { ...gespeichert.body_transform };
        }
        this._gesichtUebernehmen(gespeichert.face_transform);
        this._umrisseUebernehmen(gespeichert);
        Protokoll.info('Wizard', 'Gespeicherte Ausrichtung übernommen');
    }

    /** Eine Gesichtslage von 0/0/1 ist die Vorgabe und sagt nichts aus. */
    _gesichtUebernehmen(lage) {
        if (!lage) return;
        const vorgabe = lage.center_x === 0 && lage.center_y === 0
                        && lage.scale === 1;
        if (!vorgabe) wizardState.faceTransform = { ...lage };
    }

    _umrisseUebernehmen(gespeichert) {
        if (gespeichert.body_contour_edited) {
            wizardState.data.body_contour = gespeichert.body_contour_edited;
            wizardState.pointsEdited = true;
        }
        if (gespeichert.face_contour_edited) {
            wizardState.data.face_contour = gespeichert.face_contour_edited;
            wizardState.pointsEdited = true;
        }
    }
}
