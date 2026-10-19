import { Anatomiehash } from './anatomiehash.js';
import { Anatomietextur } from './anatomietextur.js';
import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { Genesis9vorrat } from './genesis9vorrat.js';

/**
 * Anatomievorrat — die gerechneten Karten des Anatomie-Stücks (`Anatomiebacken`) dauerhaft auf dem Server (19.10.2026, `core/dienste/g9anatomiekarten.py`).
 *
 * Edgar, 19.10.2026: „warum muss die immer neu gerechnet werden? kannst du die im modell nicht speichern?" — gemessen an Damira0 (Mesh3D-AI, zwei Figuren, grob):
 * „Hautfarbe" stand 9,6 s nach den Texturen noch offen, bei jedem Laden. Die Karten hängen nur an der Eingabe; der Schlüssel ist ein Hash darüber:
 *
 *   die Lage (`Anatomiehash` wie die Zuordnung: Stück mit Einzug, Ruhe-Normalen, Haut darunter, Größe der Karte), die ADRESSEN der Bilder der Haut-Gruppen
 *   (Farbe, Normalen, Rauheit — `Genesis9texturen` trägt sie an der Textur), die eigene Karte des Stücks als Vorlage und `FASSUNG` der Rechnung.
 *
 * Fehlt eine Adresse (ein Bild, das nicht aus dem Vorrat kommt), wird nicht abgelegt und nicht gesucht — dann rechnet es wie bisher. Ein Fehler beim Holen oder
 * Ablegen steht im Protokoll und lässt die Rechnung laufen. PNG ist hier verlustfrei: jedes Texel der Karten ist deckend (`Anatomiebild`, `Anatomiefuellung`).
 */
export class Anatomievorrat {

    static ADRESSE = '/api/character/genesis9-figur/anatomiekarten/';
    /** Hochzählen, wenn `Anatomiebild`/`Anatomiefuellung`/`Anatomiezuordnung` anders rechnen — sonst kämen alte Karten. */
    static FASSUNG = 1;
    /** Die Einstellung „Aus" (`Genesis9vorrat.wahl`) schaltet ab — der Server nimmt dann ohnehin nichts an. */
    static an() {
        return Genesis9vorrat.wahl !== 'aus';
    }

    /**
     * Woran ein Bild im Schlüssel erkannt wird: seine Adresse (`Genesis9texturen`) oder, bei einem kleinen erzeugten Bild, sein Inhalt — sonst null.
     * Gemessen 19.10.2026 an DamiraAlt (/Charakter/, F5): die Körpergruppe hat keine eigene Normalenkarte, die Hautebenen setzen die flache 1×1 von
     * `Genesis9haut.platzhalter` ein — ohne Adresse gab es keinen Schlüssel, und die Scham wurde bei jedem Laden neu gerechnet („Hautfarbe" 8,5 s nach dem Rest).
     */
    static kennung(bild) {
        if (bild.userData?.adresse) return bild.userData.adresse;
        const d = bild.isDataTexture ? bild.image?.data : null;
        return d && d.length <= 16 ? `daten:${bild.image.width}x${bild.image.height}:${Array.from(d).join(',')}:${bild.colorSpace}` : null;
    }

    /** Der Schlüssel zu `eingabe` (`Anatomiebacken.eingabe`) — oder null (ein Bild ohne Adresse, das kein kleiner Platzhalter ist). */
    static schluessel(netz, e, original) {
        const adressen = [];
        for (const t of e.quelle.texturen) {
            for (const bild of [t.map, t.normalMap, t.roughnessMap]) {
                if (!bild) { adressen.push('-'); continue; }
                const kennung = Anatomievorrat.kennung(bild);
                if (!kennung) return null;
                adressen.push(kennung);
            }
        }
        const vorlage = original.karte ? Anatomievorrat.kennung(original.karte) : 'haut';
        if (!vorlage) return null;
        const ruhe = netz.geometry?.userData?.nahtRuhe;
        const lage = Anatomiehash.schluessel({ ...e.stueck, normal: ruhe || e.stueck.normal }, e.quelle.haut, e.breite, e.hoehe);
        const text = JSON.stringify([Anatomievorrat.FASSUNG, lage, adressen, vorlage]);
        const zeichen = Uint32Array.from(text, c => c.codePointAt(0));
        return [Anatomiehash.SEED_A, Anatomiehash.SEED_B].map(s => Anatomiehash.feld(s, zeichen).toString(36).padStart(7, '0')).join('');
    }

    /**
     * Die abgelegten Karten als Texturen mit den Einstellungen ihrer Vorlagen: `{map, normalMap, roughnessMap, nr}` — oder null.
     * @param vorlagen  `{farbe, normal, rauheit}`: dieselben Vorlagen wie beim Rechnen
     */
    static async holen(schluessel, vorlagen, breite, hoehe) {
        if (!schluessel || !Anatomievorrat.an()) return null;
        try {
            const antwort = await fetch(`${Anatomievorrat.ADRESSE}${schluessel}/`);
            if (!antwort.ok) return null;
            const meta = await antwort.json();
            const karte = async (art, vorlage) => {
                if (!vorlage || !meta.arten?.includes(art)) return null;
                const blob = await (await fetch(`${Anatomievorrat.ADRESSE}${schluessel}/${art}.png`)).blob();
                const bild = await createImageBitmap(blob, { premultiplyAlpha: 'none', colorSpaceConversion: 'none' });
                return Anatomietextur.ausBild(vorlage, bild, breite, hoehe);
            };
            const [map, normalMap, roughnessMap] = await Promise.all([karte('farbe', vorlagen.farbe), karte('normal', vorlagen.normal), karte('rauheit', vorlagen.rauheit)]);
            return map ? { map, normalMap, roughnessMap, nr: meta.nr } : null;
        } catch (fehler) {
            Protokoll.warnung('Anatomievorrat', `Karten nicht geholt: ${fehler.message}`);
            return null;
        }
    }

    /** Gerechnete Karten ablegen (im Hintergrund): `gebacken` aus `Anatomiebacken.backen`, `nr` die Haut-Gruppe ihrer Farbe. */
    static async ablegen(schluessel, gebacken, nr) {
        if (!schluessel || !Anatomievorrat.an() || !gebacken?.map?.image?.toBlob) return false;
        try {
            const formular = new FormData();
            formular.append('nr', String(nr));
            for (const [art, t] of [['farbe', gebacken.map], ['normal', gebacken.normalMap], ['rauheit', gebacken.roughnessMap]]) {
                if (!t?.image?.toBlob) continue;
                formular.append(art, await new Promise(fertig => t.image.toBlob(fertig, 'image/png')), `${art}.png`);
            }
            const antwort = await fetch(`${Anatomievorrat.ADRESSE}${schluessel}/`, { method: 'POST', body: formular, headers: Serverabruf._csrfKopf() });
            return antwort.ok;
        } catch (fehler) {
            Protokoll.warnung('Anatomievorrat', `Karten nicht abgelegt: ${fehler.message}`);
            return false;
        }
    }
}
