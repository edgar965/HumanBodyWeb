/**
 * Genesis9fototextur — die Fotokacheln eines gespeicherten Modells statt der Daz-Albedo.
 *
 * Edgar, 27.09.2026: „die Szene soll natürlich mit Textur gezeigt und gespeichert werden."
 * Ein Modell aus „Mesh to 3D" oder „Modell aus Bildern" trägt `figur.fototextur`
 * (`{1001: Adresse, …}`, je UDIM-Kachel ein Bild — `core/dienste/modelltexturen.py` legt sie
 * neben das Modell). Bis dahin legte nur die Auftragsseite sie auf (`bildmodell/texturauflage.js`);
 * Szene, Studio und Theatre zeigten die Daz-Haut.
 *
 * Hier wird die Kachel VOR dem Bau als Albedo der Materialgruppe eingesetzt: Sie läuft dann
 * durch denselben Texturvorrat wie jedes Daz-Bild (`Genesis9texturen`, eigene Adressen gehen
 * unverändert durch), der Körper wird nicht erst mit der Daz-Haut gezeichnet und dann
 * übermalt, und der Export wartet auf sie (`Modellexport`: `wartenAufAlle`) — GLB, OBJ und DAE
 * tragen die Fototextur. Die Diffusfarbe des Presets fällt weg: Der Hautton steckt in der Kachel
 * (wie `Texturauflage`, die die Farbe auf Weiß stellt). Normalen, Rauheit und Schminke bleiben.
 */
export class Genesis9fototextur {

    /** Die Gruppen des Körpers mit der Kachel des Modells als Albedo — neue Objekte, die
     *  Serverantwort bleibt unberührt. Ohne Kacheln dieselbe Liste. */
    static gruppen(gruppen, kacheln) {
        if (!kacheln || !Object.keys(kacheln).length) return gruppen;
        return (gruppen || []).map(gruppe => {
            const adresse = kacheln[String(gruppe.kachel)];
            if (!adresse) return gruppe;
            const bilder = { ...(gruppe.bilder || {}), albedo: adresse };
            delete bilder.farbe;
            return { ...gruppe, bilder };
        });
    }

    /** Der Anhang „augen" mit dem Augenbild des Modells (`kacheln.augen`: Daz-Iris in der Farbe des
     *  Netzes, `core/dienste/meshfiguraugenbild.py`, 27.09.2026) als Albedo der beiden Augäpfel.
     *  Andere Anhänge und Modelle ohne Augenbild bleiben, wie sie sind. */
    static anhang(anhang, kacheln) {
        const adresse = (kacheln || {}).augen;
        if (!adresse || anhang.schluessel !== 'augen') return anhang;
        const gruppen = (anhang.gruppen || []).map(gruppe => (Genesis9fototextur.AUGAPFEL.test(gruppe.name)
            ? { ...gruppe, bilder: { ...(gruppe.bilder || {}), albedo: adresse } } : gruppe));
        return { ...anhang, gruppen };
    }

    static AUGAPFEL = /^Eye (Left|Right)$/;
}
