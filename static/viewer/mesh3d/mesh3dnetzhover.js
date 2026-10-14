import * as THREE from 'three';

/**
 * Mesh3dnetzhover — der Bereich unter dem Zeiger leuchtet, bevor man klickt (14.10.2026, „Netz bearbeiten“).
 *
 * Edgar: „per Hover im 3D View, wenn ich über das Mesh fahre, werden einzelne Bereiche highlightet — so ähnlich wie das Highlight der Objekte auf der Charakter-Seite. Dann eine Einstellung über einen Slider, mit dem ich die
 * Granularität anpassen kann (Farbbereich, Texturähnlichkeit). Bei der Ballerina möchte ich den Flügel auswählen können: der Flügel ist weiß, der Hintergrund schwarz, die Figur gelblich.“
 *
 * Der Bereich ist genau die Auswahl „Farbe im Umkreis“ (`Mesh3dnetzwahl.farbPraedikat`): alle Flächen im Umkreis um den Punkt unter dem Zeiger, deren Farbe (Lab an der UV der Flächenmitte) höchstens um ΔE von der Fläche unter
 * dem Zeiger abweicht. ΔE ist der Regler „Granularität" — kleiner = feiner. Ein Klick übernimmt genau diesen Bereich als Schritt `farbe` (Umschalt+Klick nimmt ihn weg); dieselbe Rechnung macht der Server auf dem Original,
 * die Vorschau hier und die Auswahl dort können also nicht auseinanderlaufen, nur durch die vereinfachte Kopie der Ansicht.
 *
 * Gezeigt wird er in hellem Orange (Charakter-Seite: Hover hell, Auswahl dunkel; hier Auswahl rot), über dem roten Rand der Auswahl. Die Hülle teilt die Punkte des Netzes und hat einen EIGENEN Index in voller Länge, der bei jedem
 * Zeigerschritt nur neu gefüllt wird (`setDrawRange`) — keine neue Geometrie je Bewegung.
 *
 * Gedrosselt: höchstens ein Treffertest je `PAUSE_MS` (bei langsamen Tests das `DAUER_FAKTOR`fache ihrer Dauer) und erst ab `MIN_PX` Bewegung; mit gedrückter Taste (Drehen, Verschieben) gibt es keinen Hover.
 * Ein Raycast ohne Suchbaum kostet bei 200.000 Flächen 38–56 ms (gemessen am Zauberer, 14.10.2026).
 */
export class Mesh3dnetzhover {
    static FARBE = 0xffb04a;
    static DECKUNG = 0.62;
    static PAUSE_MS = 45;
    /** Die Pause nach einem Test ist mindestens so viel mal seine Rechenzeit (Setzung: die Hauptschleife bleibt zu zwei Dritteln frei). */
    static DAUER_FAKTOR = 2;
    static MIN_PX = 2;

    /**
     * @param {Mesh3dnetzwahl} wahl die Auswahl auf dem Netz (Flächen, Farben, Treffertest)
     * @param {object} buehne die Bühne der Mesh-Ansicht (`kamera`, `takt`)
     * @param {Mesh3dnetzfarbwahl} farbwahl Umkreis und Farbabstand der Leiste
     * @param {Function} anzeige bekommt den Text zum Bereich (leer = nichts unter dem Zeiger)
     */
    constructor(wahl, buehne, farbwahl, anzeige) {
        this.wahl = wahl;
        this.buehne = buehne;
        this.farbwahl = farbwahl;
        this.anzeige = anzeige;
        this.an = false;
        /** Der Bereich, der gerade leuchtet: `{flaeche, punkt, n}` oder `null`. */
        this.bereich = null;
        this._zeiger = null;
        this._letzter = null;
        this._zeit = null;
        this._stand = 0;
        this._dauer = 0;
        this._mesh = null;
        this._index = null;
    }

    /** Hover ein- oder ausschalten (der Modus der Leiste). */
    aktiv(ja) {
        this.an = !!ja;
        if (!this.an) this.weg();
    }

    /** Der Zeiger bewegt sich: `ndc` (-1…1) der Ansicht und die Bildschirmlage `x`, `y` (für die Mindestbewegung). */
    bewegt(ndc, x, y) {
        if (!this.an) return;
        const l = this._letzter;
        if (l && Math.hypot(x - l.x, y - l.y) < Mesh3dnetzhover.MIN_PX) return;
        this._zeiger = { ndc, x, y };
        this._planen();
    }

    /** Regler, Umkreis oder Auswahl haben sich geändert: dieselbe Stelle noch einmal rechnen. */
    neu() {
        if (!this.an || !this._zeiger) return;
        this._letzter = null;
        this._planen();
    }

    /** Nichts mehr unter dem Zeiger (Zeiger verlässt die Ansicht, Taste gedrückt, Modus gewechselt). */
    weg() {
        window.clearTimeout(this._zeit);
        this._zeit = null;
        this._zeiger = null;
        this._letzter = null;
        this._leeren();
    }

    freigeben() {
        this.weg();
        if (!this._mesh) return;
        this.wahl.netz.remove(this._mesh);
        this._mesh.geometry.dispose();
        this._mesh.material.dispose();
        this._mesh = null;
        this._index = null;
    }

    // ------------------------------------------------------------------ Innenleben

    _planen() {
        if (this._zeit !== null) return;
        // Die Pause wächst mit der Dauer des letzten Tests (gemessen 14.10.2026 am Zauberer, 199.999 Flächen: der Raycast allein 38–56 ms): ab da wartet der Hover das Doppelte seiner Rechenzeit,
        // die Hauptschleife bleibt zu zwei Dritteln frei — sonst liefe ein Test nach dem anderen und die Ansicht ruckelte bei jeder Mausbewegung.
        const pause = Math.max(Mesh3dnetzhover.PAUSE_MS, Mesh3dnetzhover.DAUER_FAKTOR * this._dauer);
        const warte = Math.max(0, pause - (performance.now() - this._stand));
        this._zeit = window.setTimeout(() => { this._zeit = null; this._rechnen(); }, warte);
    }

    /** Ein Treffertest samt Anzeige; misst seine Dauer, die die nächste Pause bestimmt. */
    _rechnen() {
        const t0 = performance.now();
        try {
            this._bereichZeigen();
        } finally {
            this._dauer = performance.now() - t0;
            this._stand = performance.now();
        }
    }

    _bereichZeigen() {
        const z = this._zeiger;
        if (!this.an || !z) return;
        this._letzter = { x: z.x, y: z.y };
        const t = this.wahl.treffer(z.ndc, this.buehne.kamera);
        if (!t) { this._leeren(); return; }
        const enthaelt = this.wahl.farbPraedikat(t.flaeche, t.punkt, this.farbwahl.radiusSzene(this.wahl.wurzel), this.farbwahl.farbabstand());
        if (!enthaelt) { this._leeren('Dieses Netz hat keine lesbare Farbtextur — der Bereich unter dem Zeiger lässt sich nicht bestimmen.'); return; }
        const w = this.wahl, i0 = w.index0, idx = this._huelle().array;
        let n = 0;
        for (let f = 0; f < w.flaechen; f++) {
            if (w.entfernt[f] || !enthaelt(f)) continue;
            const o = n * 3;
            if (i0) { idx[o] = i0[f * 3]; idx[o + 1] = i0[f * 3 + 1]; idx[o + 2] = i0[f * 3 + 2]; } else { idx[o] = f * 3; idx[o + 1] = f * 3 + 1; idx[o + 2] = f * 3 + 2; }
            n++;
        }
        this._zeigen(n);
        this.bereich = { flaeche: t.flaeche, punkt: t.punkt, n };
        const anteil = (100 * n / w.flaechen).toLocaleString('de-DE', { maximumFractionDigits: 1 });
        this.anzeige(`Bereich unter dem Zeiger: ${n.toLocaleString('de-DE')} Flächen (${anteil} %) — Klick wählt ihn.`);
    }

    _zeigen(n) {
        this._index.needsUpdate = true;
        this._mesh.geometry.setDrawRange(0, n * 3);
        this._mesh.visible = n > 0;
        this.buehne.takt?.wach();
    }

    _leeren(text = '') {
        this.bereich = null;
        if (this._mesh && this._mesh.visible) {
            this._mesh.visible = false;
            this._mesh.geometry.setDrawRange(0, 0);
            this.buehne.takt?.wach();
        }
        this.anzeige(text);
    }

    /** Der Index der Hülle (einmal angelegt, Länge = alle Ecken des Netzes). */
    _huelle() {
        if (this._mesh) return this._index;
        const w = this.wahl;
        this._index = new THREE.BufferAttribute(new Uint32Array(w.flaechen * 3), 1);
        this._index.setUsage(THREE.DynamicDrawUsage);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', w.geometrie.attributes.position);
        geo.setIndex(this._index);
        geo.setDrawRange(0, 0);
        const material = new THREE.MeshBasicMaterial({ color: Mesh3dnetzhover.FARBE, transparent: true, opacity: Mesh3dnetzhover.DECKUNG, side: THREE.DoubleSide, depthWrite: false,
            polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });
        this._mesh = new THREE.Mesh(geo, material);
        this._mesh.raycast = () => {};
        this._mesh.frustumCulled = false;
        this._mesh.visible = false;
        w.netz.add(this._mesh);
        return this._index;
    }
}
