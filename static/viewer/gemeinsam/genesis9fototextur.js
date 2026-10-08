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
 * (wie `Texturauflage`, die die Farbe auf Weiß stellt). Normalen, Rauheit und Schminke bleiben — außer das
 * Modell bringt eigene mit (`KANAELE`).
 */
import { Netzstufe } from './netzstufe.js';

export class Genesis9fototextur {

    /** Weitere Kanäle je Kachel (Blender-Import, 08.10.2026: `{'1001:normalen': …, '1001:rauheit': …}`,
     *  `core/dienste/blendimporthaut.py`) — die Originalhaut bringt Normalen und Rauheit mit. */
    static KANAELE = ['normalen', 'rauheit'];

    /** Die Adresse für diesen Browser: mit Strg+Alt+H (`Netzstufe.HOCH`) `hoch=1` — der Server liefert dann die
     *  volle Kachel, sonst eine verkleinerte, wenn das Modell eine hat (`G9fototextur`, Edgar 08.10.2026: „geringe
     *  Auflösung im Browser, mit Strg+Alt+H umschaltbar auf die höchste"). Eigene Adresse je Stufe, damit weder
     *  Browser noch Texturvorrat die andere Fassung behalten. */
    static adresse(adresse) {
        if (!adresse || Netzstufe.gewaehlt() !== Netzstufe.HOCH) return adresse;
        return adresse + (adresse.includes('?') ? '&' : '?') + 'hoch=1';
    }

    /** Welche Kacheln eine Wahl im Genesis-Bedienfeld freigibt (Edgar, 08.10.2026: „Nägel färben sich nicht, wenn ich
     *  die über Genesis setze, auch Skin nicht"): Wer ein Hautpreset, einen Kopf- oder Nagellack-Preset wählt, will DAS
     *  sehen — die Fotokachel dieser Gruppen tritt dann zurück, die Serverantwort (Preset) gilt. Die Kachel 1005
     *  (Fingernägel, Zehennägel) wird vom Blender-Import nicht mehr gebacken; ältere Modelle tragen sie noch. */
    static FREIGABE = { haut: [1001, 1002, 1003, 1004], kopf: [1001], nagellack: [1005] };

    /** Die Kacheln, die der Nutzer selbst gewählt hat: `wahl` = `{haut, praesets}` der Figur. */
    static frei(wahl) {
        const aus = new Set();
        const gewaehlt = { haut: wahl?.haut, ...(wahl?.praesets || {}) };
        for (const [kategorie, kacheln] of Object.entries(Genesis9fototextur.FREIGABE)) {
            if (gewaehlt[kategorie]) kacheln.forEach(kachel => aus.add(kachel));
        }
        return aus;
    }

    /** Die Gruppen des Körpers mit der Kachel des Modells als Albedo — neue Objekte, die
     *  Serverantwort bleibt unberührt. Ohne Kacheln dieselbe Liste. Eine Gruppe, deren Preset der Nutzer
     *  gewählt hat (`frei`), bleibt, wie der Server sie liefert. `Hautton` (Preset `hautton`) behält die Diffusfarbe
     *  als Tönung über der Fotokachel, `Hautglanz` (`hautglanz`) die Rauheit des Presets statt der des Modells. */
    static gruppen(gruppen, kacheln, wahl = null) {
        if (!kacheln || !Object.keys(kacheln).length) return gruppen;
        const frei = Genesis9fototextur.frei(wahl);
        const praesets = wahl?.praesets || {};
        return (gruppen || []).map(gruppe => {
            const adresse = kacheln[String(gruppe.kachel)];
            if (!adresse || frei.has(Number(gruppe.kachel))) return gruppe;
            const bilder = { ...(gruppe.bilder || {}), albedo: Genesis9fototextur.adresse(adresse) };
            if (!praesets.hautton) delete bilder.farbe;
            for (const kanal of Genesis9fototextur.KANAELE) {
                const weitere = kacheln[`${gruppe.kachel}:${kanal}`];
                if (weitere && !(kanal === 'rauheit' && praesets.hautglanz)) bilder[kanal] = Genesis9fototextur.adresse(weitere);
            }
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
            ? { ...gruppe, bilder: { ...(gruppe.bilder || {}), albedo: Genesis9fototextur.adresse(adresse) } }
            : gruppe));
        return { ...anhang, gruppen };
    }

    static AUGAPFEL = /^Eye (Left|Right)$/;
}
