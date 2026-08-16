import { state, API } from './state.js';
import { drawSmoothContour } from './kontur.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Ausrichtungsvorschau — zeichnet über das Foto, was die Erkennung gefunden
 * hat: Körper- und Gesichtsumriss, die Rahmen von Netz, Gesicht und
 * YOLO-Person.
 *
 * Aus photo_to_3d/alignment_preview.js herausgeloest (Umbau 16.08.2026):
 * `renderAlignmentPreview()` hatte 152 Zeilen, davon VIER gleich gebaute
 * Rahmen-Blöcke (Netz, Gesicht aus Netz, Gesicht aus Foto, YOLO) — jeder mit
 * `setLineDash`, `strokeStyle`, `lineWidth`, `strokeRect`, Schriftgröße,
 * Beschriftung, `restore`. Sie stehen jetzt in `RAHMEN`; die zwei Umrisse in
 * `UMRISSE`. Eine neue Erkennung anzuzeigen ist eine Tabellenzeile.
 */
export class Ausrichtungsvorschau {

    /**
     * Umrisse: Datenfeld, Füllfarbe, Strichfarbe, Strichbreite als Anteil der
     * Grundbreite.
     */
    static UMRISSE = [
        ['body_contour', 'rgba(233, 69, 96, 0.2)', 'rgba(233, 69, 96, 0.7)', 1.0],
        ['face_contour', 'rgba(155, 89, 182, 0.15)', 'rgba(155, 89, 182, 0.6)', 0.8],
    ];

    /**
     * Rahmen: Datenfeld, Farbe, Beschriftung, Strichbreitenanteil,
     * Strichmuster (Vielfache der Grundbreite), Schrift [Mindestgröße, Anteil].
     */
    static RAHMEN = [
        ['mesh_bbox', 'rgba(0, 102, 255, ', 'SMPL-X Mesh', 0.7, [3, 2],
         [14, 0.025], [4, 6]],
        ['face_bbox_mesh', 'rgba(204, 0, 0, ', 'Gesicht (Mesh)', 0.6, [2, 2],
         [11, 0.018], [3, 4]],
        ['face_bbox_detected', 'rgba(204, 0, 204, ', 'Gesicht (Foto)', 0.6, [3, 2],
         [11, 0.018], [3, 4]],
        ['yolo_bbox', 'rgba(0, 204, 68, ', 'YOLO Person', 0.7, [3, 2],
         [11, 0.018], [3, 4]],
    ];

    /** Deckkraft von Strich und Beschriftung der Rahmen. */
    static RAHMEN_STRICH = 0.5;
    static RAHMEN_SCHRIFT = 0.6;
    /** Grundstrichbreite: dieser Anteil der Bildbreite, mindestens 3 Punkte. */
    static STRICH_ANTEIL = 0.006;
    static STRICH_MIN = 3;
    /** Güte, mit der die Vorschau gesichert wird. */
    static JPEG_GUETE = 0.85;

    async zeichnen() {
        const bereich = document.getElementById('alignment-preview');
        const leinwand = document.getElementById('preview-projection');
        const foto = document.getElementById('photo-img')?.src;
        if (!bereich || !leinwand || !state.currentJobId || !foto) return null;

        const original = document.getElementById('preview-original');
        if (original) original.src = foto;
        bereich.style.display = 'block';

        try {
            const daten = await this.silhouette();
            if (!daten?.ok) return null;
            const bild = await Ausrichtungsvorschau.bildLaden(foto);
            this._malen(leinwand, bild, daten);
            this._status(bereich, daten);
            this._vergroessern(leinwand);
            await this.sichern(leinwand);
            return daten;
        } catch (fehler) {
            console.warn('Ausrichtungsvorschau fehlgeschlagen:', fehler);
            return null;
        }
    }

    /** Silhouettendaten — je Auftrag nur einmal geholt. */
    async silhouette() {
        const gemerkt = state._previewDataCache;
        if (gemerkt && gemerkt._jobId === state.currentJobId) return gemerkt;
        const daten = await Serverabruf.json(
            `${API}/photo-job/${state.currentJobId}/silhouette/`);
        state._previewDataCache = { ...daten, _jobId: state.currentJobId };
        return state._previewDataCache;
    }

    static bildLaden(quelle) {
        return new Promise((fertig, fehler) => {
            const bild = new Image();
            bild.crossOrigin = 'anonymous';
            bild.onload = () => fertig(bild);
            bild.onerror = fehler;
            bild.src = quelle;
        });
    }

    // ------------------------------------------------------------------ Malen

    _malen(leinwand, bild, daten) {
        const breite = daten.photo_width;
        const hoehe = daten.photo_height;
        leinwand.width = breite;
        leinwand.height = hoehe;
        const stift = leinwand.getContext('2d');
        stift.drawImage(bild, 0, 0, breite, hoehe);

        const strich = Math.max(Ausrichtungsvorschau.STRICH_MIN,
                                breite * Ausrichtungsvorschau.STRICH_ANTEIL);
        for (const [feld, fuellung, farbe, anteil]
                of Ausrichtungsvorschau.UMRISSE) {
            this._umriss(stift, daten[feld], fuellung, farbe, strich * anteil);
        }
        for (const angabe of Ausrichtungsvorschau.RAHMEN) {
            this._rahmen(stift, daten, angabe, strich, breite);
        }
    }

    _umriss(stift, punkte, fuellung, farbe, strich) {
        if (!punkte || punkte.length <= 2) return;
        stift.save();
        stift.fillStyle = fuellung;
        stift.strokeStyle = farbe;
        stift.lineWidth = strich;
        drawSmoothContour(stift, punkte);
        stift.fill();
        stift.stroke();
        stift.restore();
    }

    /**
     * Ein gestrichelter Rahmen mit Beschriftung darüber. `yolo_bbox` kommt als
     * [x1, y1, x2, y2], die anderen als {x, y, w, h}.
     */
    _rahmen(stift, daten, [feld, farbe, text, anteil, muster, schrift, versatz],
            strich, breite) {
        const kasten = Ausrichtungsvorschau.kasten(daten[feld]);
        if (!kasten) return;
        // Das erkannte Gesicht wird nicht zweimal gezeichnet, wenn es dasselbe
        // Objekt wie der Netzrahmen ist.
        if (feld === 'face_bbox_detected'
            && daten.face_bbox_detected === daten.face_bbox_mesh) return;

        stift.save();
        stift.setLineDash([strich * muster[0], strich * muster[1]]);
        stift.strokeStyle = farbe + Ausrichtungsvorschau.RAHMEN_STRICH + ')';
        stift.lineWidth = strich * anteil;
        stift.strokeRect(kasten.x, kasten.y, kasten.w, kasten.h);
        stift.setLineDash([]);
        stift.font = `bold ${Math.max(schrift[0], breite * schrift[1])}px sans-serif`;
        stift.fillStyle = farbe + Ausrichtungsvorschau.RAHMEN_SCHRIFT + ')';
        stift.fillText(text, kasten.x + versatz[0], kasten.y - versatz[1]);
        stift.restore();
    }

    /** Beide Rahmenformen auf {x, y, w, h} bringen. */
    static kasten(roh) {
        if (!roh) return null;
        if (Array.isArray(roh)) {
            const [x1, y1, x2, y2] = roh;
            return { x: x1, y: y1, w: x2 - x1, h: y2 - y1 };
        }
        return roh;
    }

    _status(bereich, daten) {
        const anzeige = bereich.querySelector('.alignment-status');
        if (!anzeige) return;
        anzeige.textContent = daten.has_alignment
            ? `Auto-Alignment aktiv (${daten.alignment_method || 'pipeline'})`
            : 'Standard-Projektion (Bild-Mitte)';
    }

    _vergroessern(leinwand) {
        leinwand.style.cursor = 'zoom-in';
        leinwand.onclick = () => this.beiKlick?.(leinwand);
    }

    /** Die Vorschau beim Auftrag ablegen, damit sie später wieder erscheint. */
    async sichern(leinwand) {
        try {
            const bild = leinwand.toDataURL('image/jpeg',
                                            Ausrichtungsvorschau.JPEG_GUETE);
            await Serverabruf.senden(
                `${API}/photo-job/${state.currentJobId}/save-projection/`,
                { image: bild });
            Protokoll.debug('Photo->3D', 'Projektionsvorschau gesichert');
        } catch (fehler) {
            console.warn('Projektionsvorschau nicht sicherbar:', fehler);
        }
    }
}
