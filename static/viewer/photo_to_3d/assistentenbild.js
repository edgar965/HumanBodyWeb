import { drawSmoothContourTransformed } from './kontur.js';
import { wizardState } from './wizard.js';
import { transformPtGlobal } from './wizard_umrechnung.js';

/**
 * Assistentenbild — die Leinwand des Ausricht-Assistenten: Foto, Umrisse,
 * Erkennungsrahmen und im Bearbeitungsmodus die Punktgriffe.
 *
 * Aus photo_to_3d/wizard_zeichnen.js herausgeloest (Umbau 16.08.2026):
 * `renderWizardCanvas()` hatte 141 Zeilen. Zwei Dinge fielen auf:
 *
 *  * Die Punktumrechnung stand ZWEIMAL in derselben Datei — als exportierte
 *    `transformPtGlobal()` und als innere `transformPt()`, Zeile für Zeile
 *    gleich, nur einmal mit `canvasScale` als Parameter und einmal über die
 *    Closure. Jetzt eine Fassung in `wizard_umrechnung.js`.
 *  * Drei gleich gebaute Umriss-Blöcke und zwei Rahmen-Blöcke, die sich nur in
 *    Farbe und Strichbreite unterschieden — jetzt die Tabellen `UMRISSE` und
 *    `RAHMEN`.
 */
export class Assistentenbild {

    /** Kleinste Leinwandmaße, damit auch in engen Fenstern etwas zu sehen ist. */
    static MIN_BREITE = 300;
    static MIN_HOEHE = 200;
    /** Rand zwischen Leinwand und Rahmen. */
    static RAND = 24;

    /**
     * Umrisse je Schritt: Feld, Füllfarbe, Strichfarbe, Strichbreite.
     * Im Gesichtsschritt wird der Körper nur blass angedeutet.
     */
    static UMRISSE = {
        koerperschritt: [
            ['body_contour', 'bodyTransform', 'rgba(233, 69, 96, 0.25)',
             'rgba(233, 69, 96, 0.8)', 2],
        ],
        gesichtsschritt: [
            ['body_contour', 'bodyTransform', 'rgba(150, 150, 150, 0.15)',
             'rgba(150, 150, 150, 0.3)', 1],
            ['face_contour', 'faceTransform', 'rgba(155, 89, 182, 0.25)',
             'rgba(155, 89, 182, 0.8)', 2],
        ],
    };

    /** Rahmen je Schritt: Feld, Strichfarbe, Strichbreite, Strichmuster. */
    static RAHMEN = {
        koerperschritt: [['yolo_bbox', 'rgba(255, 255, 255, 0.6)', 1.5, [6, 4]]],
        gesichtsschritt: [['face_bbox_detected', 'rgba(46, 204, 113, 0.7)', 1.5,
                           [5, 3]]],
    };

    /** Punktgriffe im Bearbeitungsmodus. */
    static GRIFF_RADIUS = 5;
    static GRIFF_FARBE = 'rgba(255,255,255,0.7)';
    static GRIFF_STRICH = 1.5;
    static GEWAEHLT_FARBE = '#fff';
    static GEWAEHLT_STRICH_FARBE = '#e94560';
    static GEWAEHLT_STRICH = 2.5;
    static GRIFF_RAND = { body: 'rgba(233,69,96,0.9)', face: 'rgba(155,89,182,0.9)' };

    zeichnen() {
        const leinwand = document.getElementById('wizard-canvas');
        if (!leinwand || !wizardState.data || !wizardState.photoImg) return null;
        this.leinwand = leinwand;
        this.daten = wizardState.data;
        this.stift = leinwand.getContext('2d');
        this.imKoerperschritt = wizardState.step === 0;

        this._einpassen();
        this._mittenBestimmen();
        const schritt = this.imKoerperschritt ? 'koerperschritt' : 'gesichtsschritt';
        for (const angabe of Assistentenbild.RAHMEN[schritt]) this._rahmen(...angabe);
        for (const angabe of Assistentenbild.UMRISSE[schritt]) this._umriss(...angabe);
        if (wizardState.editMode) this._griffe();
        return this;
    }

    /** Foto so groß wie möglich in den Rahmen legen und den Maßstab merken. */
    _einpassen() {
        const bild = wizardState.photoImg;
        const rahmen = this.leinwand.parentElement;
        const breite = Math.max(rahmen.clientWidth - Assistentenbild.RAND,
                                Assistentenbild.MIN_BREITE);
        const hoehe = Math.max(rahmen.clientHeight - Assistentenbild.RAND,
                               Assistentenbild.MIN_HOEHE);
        this.maszstab = Math.min(breite / bild.naturalWidth,
                                 hoehe / bild.naturalHeight);
        this.leinwand.width = Math.round(bild.naturalWidth * this.maszstab);
        this.leinwand.height = Math.round(bild.naturalHeight * this.maszstab);
        wizardState.canvasScale = this.maszstab;
        this.stift.drawImage(bild, 0, 0, this.leinwand.width, this.leinwand.height);
    }

    /**
     * Mittelpunkte: Der Netzrahmen gibt die Mitte für die unbewegte Figur, bei
     * einer posierten Figur ist es die Mitte des jeweiligen Umrisses.
     */
    _mittenBestimmen() {
        const rahmen = this.daten.mesh_bbox;
        this.netzmitte = [rahmen.x + rahmen.w / 2, rahmen.y + rahmen.h / 2];
        this.posiert = !!this.daten.use_posed;
        this.mitten = {
            body_contour: this.posiert
                ? Assistentenbild.mitte(this.daten.body_contour) : [0, 0],
            face_contour: this.posiert
                ? Assistentenbild.mitte(this.daten.face_contour) : [0, 0],
        };
    }

    static mitte(umriss) {
        if (!umriss?.length) return [0, 0];
        let x = 0, y = 0;
        for (const [px, py] of umriss) {
            x += px;
            y += py;
        }
        return [x / umriss.length, y / umriss.length];
    }

    /** Punkt des Umrisses auf die Leinwand rechnen. */
    _punkt(px, py, verschiebung, mitte) {
        return transformPtGlobal(px, py, verschiebung, this.netzmitte[0],
                                 this.netzmitte[1], this.posiert, mitte[0],
                                 mitte[1], this.maszstab);
    }

    _umriss(feld, verschiebungsfeld, fuellung, farbe, strich) {
        const umriss = this.daten[feld];
        if (!umriss || umriss.length <= 2) return;
        const verschiebung = wizardState[verschiebungsfeld];
        if (!verschiebung) return;
        const mitte = this.mitten[feld] || [0, 0];
        this.stift.save();
        this.stift.fillStyle = fuellung;
        this.stift.strokeStyle = farbe;
        this.stift.lineWidth = strich;
        drawSmoothContourTransformed(this.stift, umriss,
            (px, py) => this._punkt(px, py, verschiebung, mitte));
        this.stift.fill();
        this.stift.stroke();
        this.stift.restore();
    }

    _rahmen(feld, farbe, strich, muster) {
        const roh = this.daten[feld];
        if (!roh) return;
        const kasten = Array.isArray(roh)
            ? { x: roh[0], y: roh[1], w: roh[2] - roh[0], h: roh[3] - roh[1] }
            : roh;
        this.stift.save();
        this.stift.setLineDash(muster);
        this.stift.strokeStyle = farbe;
        this.stift.lineWidth = strich;
        this.stift.strokeRect(kasten.x * this.maszstab, kasten.y * this.maszstab,
                              kasten.w * this.maszstab, kasten.h * this.maszstab);
        this.stift.restore();
    }

    /** Im Bearbeitungsmodus jeden Umrisspunkt als Kreis zum Anfassen. */
    _griffe() {
        const feld = this.imKoerperschritt ? 'body_contour' : 'face_contour';
        const umriss = this.daten[feld];
        const verschiebung = wizardState[
            this.imKoerperschritt ? 'bodyTransform' : 'faceTransform'];
        if (!umriss || umriss.length <= 2 || !verschiebung) return;
        const mitte = this.mitten[feld] || [0, 0];
        const rand = Assistentenbild.GRIFF_RAND[
            this.imKoerperschritt ? 'body' : 'face'];

        this.stift.save();
        umriss.forEach(([px, py], nummer) => {
            const [x, y] = this._punkt(px, py, verschiebung, mitte);
            this.stift.beginPath();
            this.stift.arc(x, y, Assistentenbild.GRIFF_RADIUS, 0, Math.PI * 2);
            const gewaehlt = nummer === wizardState.editPointIdx;
            this.stift.fillStyle = gewaehlt ? Assistentenbild.GEWAEHLT_FARBE
                                            : Assistentenbild.GRIFF_FARBE;
            this.stift.strokeStyle = gewaehlt
                ? Assistentenbild.GEWAEHLT_STRICH_FARBE : rand;
            this.stift.lineWidth = gewaehlt ? Assistentenbild.GEWAEHLT_STRICH
                                            : Assistentenbild.GRIFF_STRICH;
            this.stift.fill();
            this.stift.stroke();
        });
        this.stift.restore();
    }
}
