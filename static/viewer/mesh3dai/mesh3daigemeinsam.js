/**
 * Mesh3daigemeinsam — geteilte Geometrien und Materialien der Zeichner auf der Seite „Mesh3D-AI“ (14.10.2026).
 * Bei der Animation (Edgar: „bei Taste / Klick auf Play in den einzelnen Zeilen möchte ich die animiert sehen“) wird jedes Bild neu gebaut. Gemessen im Chrome (RTX PRO 4500, ein Feld mit 71 Objekten):
 * Bauen allein 1,9 ms, Rendern eines fertigen Bildes 0,3 ms, aber Bauen + Rendern 28,7 ms — die Zeit geht in das Hochladen immer neuer Geometrien und das Anlegen immer neuer Materialien, nicht ins Zeichnen.
 * Die Knochenlängen einer starren Bewegung ändern sich von Bild zu Bild nicht: dieselbe Kapsel, nur anders gestellt. Darum liefert diese Klasse zu jedem Schlüssel EIN Objekt und gibt es immer wieder her.
 * Geteilte Objekte tragen `userData.gemeinsam` und werden von `freigeben` NICHT entsorgt (das tut nur der Überlauf der Ablage). Wer ein geteiltes Material verändert, verändert es überall — Zeichner setzen es nur ein.
 */
export class Mesh3daigemeinsam {
    /** Obergrenze je Ablage: die Ausgabe des Netzes hat Rauschen, ihre Längen sind selten gleich — ohne Grenze wüchse die Ablage mit jeder Bewegung. */
    static GRENZE = 1200;
    static _geometrien = new Map();
    static _materialien = new Map();

    static _holen(ablage, schluessel, fabrik) {
        let objekt = ablage.get(schluessel);
        if (objekt) return objekt;
        if (ablage.size >= Mesh3daigemeinsam.GRENZE) {
            for (const alt of ablage.values()) alt.dispose();
            ablage.clear();
        }
        objekt = fabrik();
        objekt.userData.gemeinsam = true;
        ablage.set(schluessel, objekt);
        return objekt;
    }

    /** @param {string} schluessel Art und Maße, z. B. `kapsel:0.0500:0.2150` @param {() => THREE.BufferGeometry} fabrik */
    static geometrie(schluessel, fabrik) {
        return Mesh3daigemeinsam._holen(Mesh3daigemeinsam._geometrien, schluessel, fabrik);
    }

    /** @param {string} schluessel alles, was das Material unterscheidet (Art, Farbe, Deckkraft, Karte …) @param {() => THREE.Material} fabrik */
    static material(schluessel, fabrik) {
        return Mesh3daigemeinsam._holen(Mesh3daigemeinsam._materialien, schluessel, fabrik);
    }

    /** Länge auf 0,5 mm gerundet — gleiche Knochen verschiedener Bilder treffen so denselben Schlüssel, der Unterschied (< 0,25 mm) ist unsichtbar. */
    static laenge(l) {
        return (Math.round(l * 2000) / 2000).toFixed(4);
    }

    /** Ein Objekt der Szene entsorgen, aber nichts, was geteilt wird. */
    static freigeben(objekt) {
        objekt.traverse(o => {
            if (o.geometry && !o.geometry.userData.gemeinsam) o.geometry.dispose();
            if (o.material) [].concat(o.material).forEach(m => { if (!m.userData.gemeinsam) m.dispose(); });
            if (o.isInstancedMesh) o.dispose();
        });
    }
}
