/**
 * Texturskalierung — Werkstoff-Klone mit verkleinerten Bildkarten, für die
 * Auflösung-Auswahl im Export-Dialog.
 *
 * GLEICHES MUSTER WIE `Werkstoffvariante` (26.09.2026): Nur für die Dauer
 * des Exports `obj.material` gegen Klone tauschen, danach zurückstellen —
 * die lebende Szene bleibt unberührt. Anders als `Werkstoffvariante`
 * (Bildkarten GANZ weg) bleibt hier die Bildkarte da, nur kleiner: eine
 * neue Canvas-Textur, mit `Werkstoffbild`s Skalierungslogik gezeichnet.
 * Für OBJ/DAE reicht die Skalierung beim PNG-Schreiben (`Werkstoffbild.png`
 * mit `maxSeite`); GLB bettet die Bildkarte dagegen selbst beim Export ein
 * (`GLTFExporter` liest `material.map.image` direkt) — dafür muss VOR dem
 * Export schon eine kleinere Textur im Werkstoff stecken.
 */
export class Texturskalierung {

    //: Dieselbe Liste wie `Werkstoffvariante.BILDSLOTS` — beide Klassen
    //: behandeln dieselben Bildkarten-Slots, nur unterschiedlich (weg vs.
    //: verkleinert). Absichtlich zweimal geführt, nicht importiert: ein
    //: gemeinsames Modul dafür wäre für zwei Konstantenlisten mehr Kopplung
    //: als Nutzen.
    static BILDSLOTS = [
        'map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap',
        'bumpMap', 'alphaMap', 'displacementMap', 'clearcoatMap', 'clearcoatNormalMap',
        'clearcoatRoughnessMap', 'sheenColorMap', 'sheenRoughnessMap', 'specularMap',
        'specularColorMap', 'specularIntensityMap', 'transmissionMap', 'thicknessMap',
        'iridescenceMap', 'iridescenceThicknessMap',
    ];

    /** Dieselbe Textur, wenn sie schon klein genug ist — sonst ein Klon mit Canvas-Bild. */
    static _verkleinert(textur, maxSeite) {
        const bild = textur.image;
        if (!bild) return textur;
        const breite = bild.width || bild.videoWidth || bild.naturalWidth || 0;
        const hoehe = bild.height || bild.videoHeight || bild.naturalHeight || 0;
        if (!breite || !hoehe || Math.max(breite, hoehe) <= maxSeite) return textur;
        const faktor = maxSeite / Math.max(breite, hoehe);
        const canvas = document.createElement('canvas');
        canvas.width = Math.max(1, Math.round(breite * faktor));
        canvas.height = Math.max(1, Math.round(hoehe * faktor));
        canvas.getContext('2d').drawImage(bild, 0, 0, canvas.width, canvas.height);
        const klon = textur.clone();
        klon.image = canvas;
        klon.needsUpdate = true;
        return klon;
    }

    static klon(werkstoff, maxSeite) {
        const klon = werkstoff.clone();
        for (const feld of Texturskalierung.BILDSLOTS) {
            if (feld in klon && klon[feld]) klon[feld] = Texturskalierung._verkleinert(klon[feld], maxSeite);
        }
        klon.needsUpdate = true;
        return klon;
    }

    /**
     * `obj.material` je Objekt gegen verkleinerte Klone tauschen.
     * @param maxSeite  0 = Originalauflösung — dann wird NICHTS getauscht,
     *                  `tauschen` gibt `null` zurück (kein Rücksetzen nötig).
     * @returns Rücksetz-Funktion, oder `null` bei `maxSeite === 0`.
     */
    static tauschen(objekte, maxSeite) {
        if (!maxSeite) return null;
        const original = objekte.map((obj) => obj.material);
        objekte.forEach((obj) => {
            obj.material = Array.isArray(obj.material)
                ? obj.material.map((m) => Texturskalierung.klon(m, maxSeite))
                : Texturskalierung.klon(obj.material, maxSeite);
        });
        return () => objekte.forEach((obj, i) => { obj.material = original[i]; });
    }
}
