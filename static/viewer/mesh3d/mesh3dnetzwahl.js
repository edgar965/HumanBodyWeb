import * as THREE from 'three';
import { Mesh3dnetzfarbe } from './mesh3dnetzfarbe.js';
import { Mesh3dnetzinseln } from './mesh3dnetzinseln.js';

/**
 * Mesh3dnetzwahl — die Auswahl auf dem Netz der Mesh-Ansicht: markieren, entfernen, zurücknehmen (13.10.2026, „Netz bearbeiten“, Konzept `Docu/konzepte/2026-10-13_mesh-3d-netz-ausschneiden-konzept.md`).
 *
 * Der Browser wählt auf dem Netz, das er zeigt (bei großen Netzen die vereinfachte Kopie), und merkt sich die Auswahl als ORTE in den Koordinaten der Szene der Datei (`wurzel.worldToLocal`) — nie als Flächennummern: die der
 * Kopie sind keine des Originals. Der Server (`Mesh3dnetzauswahl`) übersetzt dieselben Orte auf dem Original. Schritte, wie der Server sie liest:
 *     {art: 'insel', punkt}   {art: 'rahmen', ebenen}   {art: 'farbe', punkt, radius, toleranz, flaeche}   {art: 'umkehren'}      je mit `aktion` 'plus' (Vorgabe) oder 'minus'
 * `schritte` ist die Auswahl, an der gearbeitet wird; „Entfernen“ legt sie als Schnitt in `schnitte` ab — erst „Speichern“ schreibt etwas (`Mesh3dnetzwerkzeug`).
 *
 * Gezeigt wird: die Auswahl als rote Hülle auf dem Netz, das Entfernte gar nicht mehr (der Index des Netzes wird ohne diese Flächen neu aufgebaut; das Original der Daten bleibt unberührt).
 * Zurück (Strg+Z) nimmt den letzten Schritt, den letzten Schnitt („Entfernen“) oder das Aufheben zurück (bis `HISTORIE_MAX` Schritte), Wiederholen (Strg+Y) stellt ihn wieder her.
 */
export class Mesh3dnetzwahl {
    static HISTORIE_MAX = 40;
    static FARBE = 0xff3030;

    /**
     * @param {THREE.Mesh} netz das einzige Netz der Datei
     * @param {THREE.Object3D} wurzel die Szene des glTF (ihr Koordinatensystem gilt für die Orte)
     * @param {Function} geaendert wird nach jeder Änderung gerufen (Bild neu, Zahlen)
     */
    constructor(netz, wurzel, geaendert) {
        this.netz = netz;
        this.wurzel = wurzel;
        this.geaendert = geaendert;
        this.geometrie = netz.geometry;
        this.index0 = this.geometrie.index ? this.geometrie.index.array : null;
        this.zerlegung = Mesh3dnetzinseln.zerlegen(this.geometrie);
        this.flaechen = this.zerlegung.flaechen;
        this.auswahl = new Uint8Array(this.flaechen);
        this.entfernt = new Uint8Array(this.flaechen);
        this.schritte = [];
        this.schnitte = [];
        this.historie = [];
        /** Die zurückgenommenen Stände (Strg+Y); leer, sobald ein neuer Schritt kommt. */
        this.zukunft = [];
        /** Original-Flächennummer zu jeder Fläche des (verkleinerten) Index; `null`, solange nichts entfernt ist. */
        this.nummern = null;
        this._mitten = null;
        /** Lab-Farbe je Fläche, erst beim ersten Farbschritt gelesen; `null` = keine lesbare Textur. */
        this._lab = undefined;
        this._huelle = null;
        this._raycaster = new THREE.Raycaster();
    }

    // ------------------------------------------------------------------ Zahlen

    zaehlen(feld) { let n = 0; for (let i = 0; i < feld.length; i++) n += feld[i]; return n; }

    get nAuswahl() { return this.zaehlen(this.auswahl); }

    get nEntfernt() { return this.zaehlen(this.entfernt); }

    /** Die Teile mit mindestens `ab` Flächen: `[{nr, flaechen, anteil, entfernt}]`, größter zuerst. */
    teile(ab = 50) {
        const z = this.zerlegung;
        const weg = new Int32Array(z.groessen.length);
        for (let f = 0; f < this.flaechen; f++) if (this.entfernt[f]) weg[z.insel[f]]++;
        return Array.from(z.groessen, (n, nr) => ({ nr, flaechen: n, anteil: n / this.flaechen, entfernt: weg[nr] }))
            .filter(t => t.flaechen >= ab || t.nr === 0);
    }

    // ------------------------------------------------------------------ Ort → Fläche

    /** Der erste Treffer eines Strahls durch den Punkt `ndc` (-1…1) der Ansicht: `{flaeche, punkt}` oder `null`. Entfernte Flächen sind nicht mehr im Index und werden nicht getroffen. */
    treffer(ndc, kamera) {
        this._raycaster.setFromCamera(ndc, kamera);
        const t = this._raycaster.intersectObject(this.netz, false)[0];
        if (!t || t.faceIndex == null) return null;
        return { flaeche: this.nummern ? this.nummern[t.faceIndex] : t.faceIndex, punkt: this.wurzel.worldToLocal(t.point.clone()) };
    }

    /** Mitte jeder Fläche in den Koordinaten der Szene (Float32Array, einmal gerechnet). */
    mitten() {
        if (this._mitten) return this._mitten;
        this.wurzel.updateWorldMatrix(true, false);
        this.netz.updateWorldMatrix(true, false);
        const m = new THREE.Matrix4().copy(this.wurzel.matrixWorld).invert().multiply(this.netz.matrixWorld);
        const pos = this.geometrie.attributes.position;
        const v = new THREE.Vector3(), summe = new THREE.Vector3();
        const aus = new Float32Array(this.flaechen * 3);
        for (let f = 0; f < this.flaechen; f++) {
            summe.set(0, 0, 0);
            for (let k = 0; k < 3; k++) {
                v.fromBufferAttribute(pos, this.index0 ? this.index0[f * 3 + k] : f * 3 + k).applyMatrix4(m);
                summe.add(v);
            }
            aus.set([summe.x / 3, summe.y / 3, summe.z / 3], f * 3);
        }
        return (this._mitten = aus);
    }

    // ------------------------------------------------------------------ Schritte

    /** Der ganze Teil, zu dem die Fläche gehört (Klick oder Listenzeile); `punkt` ist ein Ort auf ihm in Koordinaten der Szene. */
    insel(flaeche, punkt, plus = true) {
        const nr = this.zerlegung.insel[flaeche];
        this._schritt({ art: 'insel', punkt: [punkt.x, punkt.y, punkt.z], aktion: plus ? 'plus' : 'minus' }, f => this.zerlegung.insel[f] === nr);
    }

    inselNr(nr, plus = true) {
        const f = this.zerlegung.erste[nr], m = this.mitten();
        this.insel(f, new THREE.Vector3(m[f * 3], m[f * 3 + 1], m[f * 3 + 2]), plus);
    }

    /** Alles, dessen Mitte hinter allen Ebenen liegt (`THREE.Plane` in Koordinaten der Szene; innen = `distanceToPoint ≥ 0`). */
    rahmen(ebenen, plus = true) {
        const m = this.mitten(), v = new THREE.Vector3();
        this._schritt({ art: 'rahmen', ebenen: ebenen.map(e => [e.normal.x, e.normal.y, e.normal.z, e.constant]), aktion: plus ? 'plus' : 'minus' },
            f => { v.set(m[f * 3], m[f * 3 + 1], m[f * 3 + 2]); return ebenen.every(e => e.distanceToPoint(v) >= 0); });
    }

    /**
     * Alle Flächen im Umkreis `radius` (Einheiten der Szene der Datei) um den Klick, deren Farbe höchstens ΔE `toleranz` von der Fläche unter dem Klick abweicht — ohne Zusammenhang über Kanten
     * (`Mesh3dnetzfarbe`). `false`, wenn das Netz keine lesbare Farbtextur hat.
     */
    farbe(flaeche, punkt, radius, toleranz, plus = true) {
        const enthaelt = this.farbPraedikat(flaeche, punkt, radius, toleranz);
        if (!enthaelt) return false;
        this._schritt({ art: 'farbe', punkt: [punkt.x, punkt.y, punkt.z], radius, toleranz, flaeche, aktion: plus ? 'plus' : 'minus' }, enthaelt);
        return true;
    }

    /** Lab-Farbe je Fläche (`Mesh3dnetzfarbe`), beim ersten Aufruf gelesen; `null` = keine lesbare Farbtextur. */
    labfarben() {
        if (this._lab === undefined) this._lab = Mesh3dnetzfarbe.labfarben(this.netz, this.index0, this.flaechen);
        return this._lab;
    }

    /**
     * Das Urteil „Fläche f gehört zur Auswahl nach Farbe“ — dasselbe für den Schritt `farbe` und für die Vorschau unter dem Zeiger (`Mesh3dnetzhover`): Mitte höchstens `radius` vom Punkt, Farbe höchstens ΔE `toleranz`
     * von der Fläche `flaeche`. Entfernte Flächen prüft der Aufrufer. `null`, wenn das Netz keine lesbare Farbtextur hat.
     */
    farbPraedikat(flaeche, punkt, radius, toleranz) {
        const lab = this.labfarben();
        if (!lab) return null;
        const m = this.mitten(), r2 = radius * radius;
        return f => {
            const dx = m[f * 3] - punkt.x, dy = m[f * 3 + 1] - punkt.y, dz = m[f * 3 + 2] - punkt.z;
            return dx * dx + dy * dy + dz * dz <= r2 && Mesh3dnetzfarbe.abstand(lab, f, flaeche) <= toleranz;
        };
    }

    umkehren() {
        this._sichern();
        this.schritte.push({ art: 'umkehren' });
        for (let f = 0; f < this.flaechen; f++) this.auswahl[f] = this.auswahl[f] ? 0 : 1;
        this._fertig();
    }

    aufheben() {
        if (!this.schritte.length) return;
        this._sichern();
        this.schritte = [];
        this.auswahl.fill(0);
        this._fertig();
    }

    /** Die Auswahl als Schnitt ablegen und aus der Ansicht nehmen. */
    entfernen() {
        const weg = this.nAuswahl;
        if (!weg) return 0;
        this._sichern(true);
        this.schnitte.push(this.schritte);
        for (let f = 0; f < this.flaechen; f++) if (this.auswahl[f]) this.entfernt[f] = 1;
        this.schritte = [];
        this.auswahl.fill(0);
        this._indexNeu();
        this._fertig();
        return weg;
    }

    /** Den letzten Schritt (auch ein „Entfernen“) zurücknehmen — Strg+Z. */
    zurueck() {
        const z = this.historie.pop();
        if (!z) return false;
        this.zukunft.push(this._stand(!!z.entfernt));
        this._setzen(z);
        return true;
    }

    /** Einen zurückgenommenen Schritt wiederholen — Strg+Y. Jeder neue Schritt leert die Liste der zurückgenommenen. */
    wiederholen() {
        const z = this.zukunft.pop();
        if (!z) return false;
        this.historie.push(this._stand(!!z.entfernt));
        this._setzen(z);
        return true;
    }

    /** Alles zurück auf das Original (nach dem Speichern oder bei einem neuen Netz). */
    zuruecksetzen() {
        this.historie = [];
        this.zukunft = [];
        this.schritte = [];
        this.schnitte = [];
        this.auswahl.fill(0);
        this.entfernt.fill(0);
        this._indexNeu();
        this._fertig();
    }

    /** Die Anzeige freigeben und den Index des Netzes wieder auf das Geladene setzen. */
    freigeben() {
        this._huelleWeg();
        if (this.index0 && this.geometrie.index) this.geometrie.setIndex(new THREE.BufferAttribute(this.index0, 1));
    }

    // ------------------------------------------------------------------ Innenleben

    _schritt(schritt, enthaelt) {
        this._sichern();
        const plus = schritt.aktion !== 'minus';
        for (let f = 0; f < this.flaechen; f++) if (enthaelt(f)) this.auswahl[f] = plus ? 1 : 0;
        this.schritte.push(schritt);
        this._fertig();
    }

    /** Der jetzige Stand; `mitEntfernt` auch die Liste der entfernten Flächen (nur das Entfernen ändert sie). */
    _stand(mitEntfernt) {
        return { auswahl: this.auswahl.slice(), schritte: [...this.schritte], schnitte: [...this.schnitte], entfernt: mitEntfernt ? this.entfernt.slice() : null };
    }

    /** Einen gemerkten Stand wieder einsetzen. */
    _setzen(z) {
        this.auswahl = z.auswahl;
        this.schritte = z.schritte;
        this.schnitte = z.schnitte;
        if (z.entfernt) { this.entfernt = z.entfernt; this._indexNeu(); }
        this._fertig();
    }

    /** Den Stand für „Zurück“ merken; ein neuer Schritt verwirft die zurückgenommenen (`zukunft`). */
    _sichern(mitEntfernt = false) {
        this.historie.push(this._stand(mitEntfernt));
        this.zukunft = [];
        if (this.historie.length > Mesh3dnetzwahl.HISTORIE_MAX) this.historie.shift();
    }

    /** Den Index ohne die entfernten Flächen neu aufbauen. */
    _indexNeu() {
        const index = this.index0;
        const behalten = [];
        for (let f = 0; f < this.flaechen; f++) if (!this.entfernt[f]) behalten.push(f);
        if (behalten.length === this.flaechen) {
            this.nummern = null;
            if (this.index0) this.geometrie.setIndex(new THREE.BufferAttribute(this.index0, 1));
            else this.geometrie.setIndex(null);
            return;
        }
        const neu = new Uint32Array(behalten.length * 3);
        behalten.forEach((f, i) => { for (let k = 0; k < 3; k++) neu[i * 3 + k] = index ? index[f * 3 + k] : f * 3 + k; });
        this.nummern = Int32Array.from(behalten);
        this.geometrie.setIndex(new THREE.BufferAttribute(neu, 1));
    }

    _fertig() {
        this._huelleBauen();
        this.geaendert();
    }

    _huelleWeg() {
        if (!this._huelle) return;
        this.netz.remove(this._huelle);
        this._huelle.geometry.dispose();
        this._huelle.material.dispose();
        this._huelle = null;
    }

    /** Die Auswahl als rote Hülle: dieselben Punkte wie das Netz, nur die gewählten (nicht entfernten) Flächen. */
    _huelleBauen() {
        this._huelleWeg();
        const faces = [];
        for (let f = 0; f < this.flaechen; f++) if (this.auswahl[f] && !this.entfernt[f]) faces.push(f);
        if (!faces.length) return;
        const index = new Uint32Array(faces.length * 3);
        faces.forEach((f, i) => { for (let k = 0; k < 3; k++) index[i * 3 + k] = this.index0 ? this.index0[f * 3 + k] : f * 3 + k; });
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', this.geometrie.attributes.position);
        geo.setIndex(new THREE.BufferAttribute(index, 1));
        const material = new THREE.MeshBasicMaterial({ color: Mesh3dnetzwahl.FARBE, transparent: true, opacity: 0.6, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
        this._huelle = new THREE.Mesh(geo, material);
        this._huelle.raycast = () => {};
        this.netz.add(this._huelle);
    }
}
