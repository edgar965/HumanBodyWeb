/**
 * Fotogenesisansicht — ein 3D-Feld der Seite „Foto-Genesis“ (24.10.2026): `Meshgenesisansicht` mit EINEM Grund für alle Felder und gekoppeltem Drehen relativ zur eigenen Figur.
 *
 * Edgar: „der hintergrund bei den 3D Views sollte auch heller sein, und gleich, damit man vergleichen kann“ — Mesh-Genesis wechselt zwischen zwei dunklen Gründen (Netz 1b1f27, Figur 5a6170);
 * hier gilt `Fotogenesisansicht.grund` (gesetzt von `Fotogenesisseite`: weiß wie die freigestellten Fotos, bei Exporten der Grund der Exportfotos).
 * Edgar: „dass sich die Modelle alle synchron drehen im View in einer Zeile, so wie bei Mesh3d-AI“ — Mesh-Genesis kopiert Kamera und Drehpunkt absolut; das geht hier nicht, weil das Netz (Tripo,
 * ~1 m hoch, im Rahmen der Fotos) und die Genesis-Figur (~1,75 m, bei Exporten im Rahmen des Datensatzes) verschieden groß sind und verschieden stehen. Übernommen wird darum der Blick RELATIV
 * zum eigenen Drehpunkt: Richtung im Rahmen der Fotos (`rahmen`) und Abstand im Verhältnis der Hüllen (`groesse`, beide setzt `Fotogenesiskamera.feldStellen`).
 */
import * as THREE from 'three';
import { Meshgenesisansicht } from '../meshgenesis/meshgenesisansicht.js';
import { Fotogenesisansichtsart } from './fotogenesisansichtsart.js';

export class Fotogenesisansicht extends Meshgenesisansicht {
    static grund = 0xffffff;
    /** „Normale“ / „Netz farbig“ der Leiste oben (`Fotogenesissteuerung.art`, gesetzt von `Fotogenesisseite`) — gilt für jedes Feld ohne eigene Zeilenleiste (`zeilenart` null). */
    static seitenart = null;
    /**
     * Fotolicht (24.10.2026 abends, Edgar: „jetzt hast du alle unterschiede, fixe!“): die Haut und die Stücke tragen die Farben der Fotos samt deren Schattierung. Unter dem Licht von
     * Mesh-Genesis (Halbkugel 1,1 + Richtung 1,6) kam die Haut auf der Seite 48–71 sRGB-Stufen dunkler als im Foto, Sapiens hielt die Beine dort für Hose (Abnahme `lauf6_messpunkte`).
     * Gemessen im Chrome (three.js r170, ohne Tone-Mapping, MeshStandardMaterial rau, nicht metallisch, Farbe 128): Umgebungslicht 1 → 74, π → 127 — π gibt die Texturfarbe wieder.
     * Gilt für die Ansichtsart „Textur“ und alle Renderings mit echten Materialien (`Fotogenesisvergleich`, `Fotogenesisseitenbild`); die anderen Ansichtsarten behalten das Licht von Mesh-Genesis.
     */
    static FOTOLICHT = Math.PI;
    /** Kein Licht der Charakterseite (`Meshgenesisansicht.STUDIO`): hier gilt das Fotolicht, und die Abnahme misst das Rendering der Seite. */
    static STUDIO = false;

    constructor(...argumente) {
        super(...argumente);
        this.modelllicht = this.szene.children.filter(o => o.isLight);
        this.fotolicht = new THREE.AmbientLight(0xffffff, Fotogenesisansicht.FOTOLICHT);
        this.fotolicht.layers.enableAll();
        this.szene.add(this.fotolicht);
        this.licht(true);
        this.zeilenart = null;          // Ansicht der Zeilenleiste (`Fotogenesiszeilenleiste`, 04.11.2026) — null: das Feld folgt allein seinem `modus`
    }

    /** Fotolicht (true) oder das Licht von Mesh-Genesis. */
    licht(foto) {
        if (!this.fotolicht) return;
        this.fotolicht.visible = foto;
        for (const l of this.modelllicht) l.visible = !foto;
    }

    /**
     * Sofort füllen, auch außerhalb des Bildes (04.11.2026, Edgar: „mach die Ergebnisse in ALLEN views sofort sichtbar, kein langes nachberechnen“): `Meshgenesisansicht` baut ein
     * verdecktes Feld erst beim Hineinscrollen — bis dahin war seine Hülle leer, „Ergebnis“ maß „Keine sichtbare Genesis-Figur.“ (marta-wave: Zeile unter der PSHuman-Eingabe,
     * im Chrome nachgestellt) und die Kameras fassten alle 250 ms nach. Gerendert wird weiter erst im Bild (`zeichnen`).
     */
    zeigen(d, leer = null) {
        super.zeigen(d, leer);
        this.jetztFuellen();
    }

    /** Beim tatsächlichen Rendern (seit 08.11.2026 gebündelt, `Meshgenesisansicht.zeichnen`) Grund und Licht setzen. */
    zeichnenJetzt() {
        this.grund = Fotogenesisansicht.grund;
        // „Netz farbig“ mit dem Licht von Mesh-Genesis, damit die Form zu sehen ist (PSHuman beleuchtet es auch); Fotolicht nur für „Textur“
        this.licht(!this.inhalt.userData.genesisErsatz && !Fotogenesisansichtsart.getauscht(this.ansichtsart));
        super.zeichnenJetzt();
    }

    /** Die Ansicht dieses Feldes: die seiner Zeilenleiste, ohne sie die der Leiste oben (nicht `art`: das ist bei `Meshgenesisansicht` 'eingabe' | 'ausgabe'). */
    get ansichtsart() {
        return this.zeilenart ?? Fotogenesisansicht.seitenart;
    }

    /** „Normale“ und „Netz farbig“: Materialien nur für diesen Durchgang getauscht (`Fotogenesisansichtsart.malen`); ebenso die Hautbilder von „Haut angleichen“ (`hauttausch`, `Fotogenesishautangleich._tauschen`). */
    _malen(renderer) {
        if (Fotogenesisansichtsart.getauscht(this.ansichtsart)) Fotogenesisansichtsart.malen(this, renderer, this.ansichtsart);
        else super._malen(renderer);
    }

    _uebernehmen(von) {
        // Ohne eigene Hülle (Feld noch nicht eingepasst) gibt es kein Verhältnis: übernommen hätte das Feld den Abstand des Netzes (~1 m Figur) für die Genesis-Figur (1,7 m) —
        // Feld 3 zeigte dann nur den Rumpf (24.10.2026, Edgar: „in der oberen View hast du noch nicht das Genesis modell (kopf) drin“).
        if (this.groesse === undefined || von.groesse === undefined) return;
        const eins = new THREE.Quaternion();
        const versatz = von.kamera.position.clone().sub(von.steuerung.target).applyQuaternion((von.rahmen ?? eins).clone().invert());
        versatz.multiplyScalar((this.groesse ?? 1) / (von.groesse ?? 1)).applyQuaternion(this.rahmen ?? eins);
        this._sperre = true;
        this.kamera.position.copy(this.steuerung.target).add(versatz);
        const entfernung = versatz.length();
        this.kamera.near = entfernung / 50;
        this.kamera.far = entfernung * 4;
        this.kamera.updateProjectionMatrix();
        this.steuerung.update();
        this.zeichnen();
        this._sperre = false;
    }
}
