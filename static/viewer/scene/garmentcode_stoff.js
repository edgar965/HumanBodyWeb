import * as THREE from 'three';
import { Gewebe } from '../gemeinsam/gewebe.js';

/**
 * Garmentstoff — wie ein GarmentCode-Stück aussieht.
 *
 * EIGENES MODUL (09.09.2026), weil das Material an DREI Stellen entsteht
 * oder gelesen wird und dabei zweimal auseinandergelaufen ist:
 *
 *   garmentcode_anziehen   baut das Netz und braucht ein Material dafür
 *   garmentcode_material   die drei Regler im Reiter
 *   garmentcode_ablage     speichert und stellt wieder her
 *
 * DER BEFUND, DER DAS MODUL AUSGELÖST HAT (Edgar: „modell gespeichert
 * (farbe rot des T-Shirt), neu geladen - Farbe ist weg"): `einhaengen`
 * baute bei JEDEM Aufruf ein frisches Material mit der Vorgabefarbe — und
 * es läuft nicht nur beim Bauen, sondern auch aus `nachbinden`, sobald das
 * Skelett entsteht. Beim Laden einer Szene passiert das direkt nachdem die
 * gespeicherte Farbe gesetzt wurde. Im Browser gemessen: Das Einhängen
 * eines zweiten Stücks setzte das erste von #ff0000 auf #dcd8d0 zurück.
 *
 * Deshalb nimmt `neu()` die bisherigen Werte entgegen. Ein Stück, das schon
 * hängt, behält damit sein Aussehen über jedes Neu-Einhängen hinweg.
 *
 * SEIT DEM 10.09.2026 IST ES STOFF, NICHT PLASTIK
 * ===============================================
 * Edgar: „Meine Kleider sehen mir noch zu schlecht aus." Ein Teil davon war
 * das Material: ein `MeshStandardMaterial` mit Farbe und Rauheit, sonst
 * nichts. Zwei Dinge unterscheiden Stoff von lackiertem Blech, und beide
 * fehlten:
 *
 * * **Glanzsaum** (`sheen`). Ein Gewebe steht aus lauter Fasern, die das
 *   Licht am streifenden Rand zurückwerfen — deshalb hat Stoff einen hellen
 *   Saum, wo er sich von der Kamera wegdreht. `MeshPhysicalMaterial` kann
 *   das; `MeshStandardMaterial` nicht. Das ist der Grund für den Wechsel.
 * * **Bindung** (`normalMap`). Kette und Schuss brechen das Licht in feinen
 *   Reihen. Die Kachel wird gerechnet (`gemeinsam/gewebe.js`), nicht
 *   geladen.
 *
 * OHNE UV KEINE BINDUNG, UND DAS IST KEIN FEHLER. Eine Normalkarte braucht
 * UV-Koordinaten; die Rig-Dateien führen sie erst seit dem 10.09.2026
 * (`GarmentCode/stoffuv.py`). Ein Stück aus einem älteren Ergebnisordner
 * bekommt deshalb nur den Glanzsaum — sichtbar besser als vorher, und wer
 * es neu baut, bekommt beides. Die Karte wird nur gesetzt, wenn UVs da
 * sind: Three.js meldet eine wirkungslose Normalkarte nicht, sie wäre
 * stumm nichts.
 */
export class Garmentstoff {

    /** Stoff-Farbe, solange GarmentCode keine mitgibt. */
    static FARBE = 0xdcd8d0;

    /** Rauheit und Metallanteil der Vorgabe — Stoff glänzt nicht. */
    static RAUHEIT = 0.85;
    static METALL = 0.0;

    /**
     * Glanzsaum: Anteil, Streuung und Farbe.
     *
     * Die Streuung ist hoch (0,8), weil ein Gewebe den Saum breit und weich
     * zeichnet — ein niedriger Wert ergibt den harten Schimmer von Satin.
     * Die Farbe bleibt weiß: Die Fasern streuen unabhängig davon, wie der
     * Stoff gefärbt ist.
     */
    static GLANZ = 0.6;
    static GLANZ_STREUUNG = 0.8;
    static GLANZ_FARBE = 0xffffff;

    /**
     * Wie stark die Bindung sich abzeichnet.
     *
     * 0,45 ist bewusst zurückhaltend: Die Kachel läuft rund fünfzigmal über
     * ein T-Shirt, und bei voller Stärke liest sich das aus der Entfernung
     * als Rauschen statt als Gewebe.
     */
    static GEWEBE_STAERKE = 0.45;

    /** Die gerechnete Kachel — einmal je Sitzung, dann geteilt. */
    static _kachel = null;

    /**
     * Ein Material für ein Stück; `bisher` sind die Werte, die es schon
     * trug (aus `werte()`), sonst die Vorgabe.
     *
     * `angaben` kommt aus der Rig-Datei: `uvMeter` sagt, wie viele Meter
     * Stoff eine UV-Einheit sind, `hatUv`, ob das Netz überhaupt UVs führt.
     */
    static neu(bisher = null, angaben = null) {
        const material = new THREE.MeshPhysicalMaterial({
            color: bisher?.farbe ?? Garmentstoff.FARBE,
            roughness: bisher?.rauheit ?? Garmentstoff.RAUHEIT,
            metalness: bisher?.metall ?? Garmentstoff.METALL,
            sheen: Garmentstoff.GLANZ,
            sheenRoughness: Garmentstoff.GLANZ_STREUUNG,
            sheenColor: new THREE.Color(Garmentstoff.GLANZ_FARBE),
            // Stoff wird von beiden Seiten gesehen — ein Rock von innen,
            // ein Ärmel im Durchblick.
            side: THREE.DoubleSide,
        });
        if (angaben?.hatUv) Garmentstoff.gewebeAuflegen(material, angaben.uvMeter);
        return material;
    }

    /**
     * Die Gewebe-Normalkarte auf ein Material legen.
     *
     * Je Stück eine eigene Textur-Instanz, aber DASSELBE Bild: `clone()`
     * teilt die Bilddaten und lässt jedem seine eigene Wiederholung. Ohne
     * den Klon hätten alle Stücke die Kachelung des zuletzt gebauten — und
     * eine Hose bräuchte eine andere als ein T-Shirt (1,70 gegen 1,07 Meter
     * Stoff je UV-Einheit).
     */
    static gewebeAuflegen(material, uvMeter) {
        const karte = Garmentstoff.kachel().clone();
        const wie_oft = Gewebe.wiederholung(uvMeter);
        karte.repeat.set(wie_oft, wie_oft);
        karte.needsUpdate = true;
        material.normalMap = karte;
        material.normalScale = new THREE.Vector2(Garmentstoff.GEWEBE_STAERKE,
                                                 Garmentstoff.GEWEBE_STAERKE);
        material.needsUpdate = true;
        return wie_oft;
    }

    /** Die Kachel als Three.js-Textur — gerechnet, einmal. */
    static kachel() {
        if (Garmentstoff._kachel) return Garmentstoff._kachel;
        const karte = new THREE.DataTexture(
            Gewebe.normalfeld(), Gewebe.GROESSE, Gewebe.GROESSE,
            THREE.RGBAFormat);
        karte.wrapS = THREE.RepeatWrapping;
        karte.wrapT = THREE.RepeatWrapping;
        // Ohne Mipmaps flimmert die Kachel bei fünfzig Wiederholungen; ohne
        // Anisotropie verschwindet sie an flach stehenden Flächen ganz.
        // 16 ist das übliche Maximum der Hardware — Three.js klemmt einen
        // zu hohen Wert selbst auf das, was die GPU kann.
        karte.generateMipmaps = true;
        karte.minFilter = THREE.LinearMipmapLinearFilter;
        karte.magFilter = THREE.LinearFilter;
        karte.anisotropy = 16;
        karte.needsUpdate = true;
        Garmentstoff._kachel = karte;
        return karte;
    }

    /**
     * Die Werte eines vorhandenen Materials — oder `null`.
     *
     * Muss gelesen werden, BEVOR das Netz entfernt wird: `entfernen` gibt
     * das Material frei, und danach sind die Werte nicht mehr zu holen.
     */
    static werte(netz) {
        const m = netz?.material;
        if (!m) return null;
        return {
            farbe: m.color ? m.color.getHex() : null,
            rauheit: typeof m.roughness === 'number' ? m.roughness : null,
            metall: typeof m.metalness === 'number' ? m.metalness : null,
        };
    }

    /** Werte auf ein Material legen; liefert 1, wenn etwas gesetzt wurde. */
    static auflegen(netz, werte) {
        const m = netz?.material;
        if (!m || !werte) return 0;
        if (werte.farbe !== null && werte.farbe !== undefined) {
            m.color?.set(werte.farbe);
        }
        if (typeof werte.rauheit === 'number') m.roughness = werte.rauheit;
        if (typeof werte.metall === 'number') m.metalness = werte.metall;
        return 1;
    }
}
