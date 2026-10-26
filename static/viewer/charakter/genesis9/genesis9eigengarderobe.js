import { escapeHtml } from '../utils.js';
import { Stueckereignis } from '../../gemeinsam/stueckereignis.js';
import { Eigenkleidwerte } from '../../gemeinsam/eigenkleidwerte.js';
import { Dazkleidung } from './dazkleidung.js';
import { Genesis9garderobe } from './genesis9garderobe.js';
import { Genesis9garderobekategorien } from './genesis9garderobekategorien.js';
import { Genesis9eigenstueck } from './genesis9eigenstueck.js';
import { Genesis9eigenabgleich } from './genesis9eigenabgleich.js';
import { Genesis9eigenkleidkasten } from './genesis9eigenkleidkasten.js';

/**
 * Genesis9eigengarderobe — der Bereich Assets → Eigen einer Genesis-9-Figur (`_genesis9_garderobe.html`, neben „Genesis“).
 *
 * Edgar, 25.10.2026 (K1): je getragenes Stück die Blöcke Form, Sitz, Stoff, Textur; Unterabteilungen nach den Genesis-Kategorien. Dann (K2a): „Die neuen Kleider-Regler
 * sollen in den Tab Assets → Eigen, darunter die Unterteilung wie bei Assets → Genesis.“ Bis dahin standen „Kleider“ und „Haare“ als Gruppen im Reglerfeld „Eigen“
 * (`Genesis9eigenregler`); dort bleiben nur die Körper-Eigenregler und die Hauttextur.
 *
 * AUFBAU wie die Garderobe (`Genesis9garderobe.fuellen`): oben der Sammeleintrag „Alle Kategorien“ (falls getragen), darunter die Kategorien in Edgars Einteilung
 * (`Genesis9garderobekategorien`, gleiche Kästen `g9-kategorie`, Vorgabe ZU) — nur besetzte, wie dort. Besetzt heißt: die eigenen Stücke (`Eigenkleidwerte.ARTEN`:
 * Oberteil → „Oberteile“, Hose → „Hosen“, immer da, mit Anlegen/Ablegen — `Genesis9eigenkleidkasten`) und die getragenen Daz-Stücke der Kategorie (Kleidung ohne
 * Anatomie und Frisuren, die unter „Haare“ stehen; je Stück `Genesis9eigenstueck`). Requisiten und Genital-Stücke stehen nicht hier.
 *
 * Kommt ein Stück dazu oder geht eines (`Stueckereignis`), wird neu gebaut — nur bei geändertem Bestand (ein Reglerzug zieht das Stück neu an und meldet ebenfalls).
 */
export class Genesis9eigengarderobe {

    static BEREICH = 'assets-genesis9-eigen';
    static _stand = null;
    static _hoert = false;

    /** Den Bereich für `inst` füllen (gerufen von `Genesis9eigenschaften.fuellen`). */
    static fuellen(inst, behaelter) {
        if (!behaelter) return Promise.resolve();
        Genesis9eigenabgleich.verdrahten();
        Genesis9eigengarderobe._hoeren();
        const stand = { inst, behaelter, bestand: null, lauf: 0 };
        Genesis9eigengarderobe._stand = stand;
        return Genesis9eigengarderobe._bauen(stand);
    }

    /** Die Kennungen der getragenen Stücke, sortiert, als Text — ändert er sich, wird neu gebaut. */
    static bestand(inst) {
        return Object.keys(Dazkleidung.kleidung(inst)).sort().join('|');
    }

    static async _bauen(stand) {
        const lauf = ++stand.lauf;
        stand.bestand = Genesis9eigengarderobe.bestand(stand.inst);
        stand.behaelter.innerHTML = '<div class="gedaempft g9-eigenregler-leer">Lade Garderobe …</div>';
        let katalog = [], einteilung = { kategorien: [], zuordnung: {} }, fehler = null;
        try {
            [katalog, einteilung] = await Promise.all([Genesis9garderobe.liste(), Genesis9garderobekategorien.stand()]);
        } catch (f) {
            fehler = f;
        }
        if (lauf !== stand.lauf || Genesis9eigengarderobe._stand !== stand) return;        // überholt: neu angestoßen oder andere Figur gewählt
        stand.behaelter.innerHTML = '';
        // Die eigenen Stücke kommen auch ohne Katalog — nur die getragenen Daz-Stücke fehlen dann (mit Meldung).
        if (fehler) Genesis9eigengarderobe._hinweis(stand.behaelter, `Garderobe nicht geladen: ${fehler.message}`, 'fehlertext');
        else if (!katalog?.length) stand.bestand = null;          // leerer Katalog: beim nächsten Stückereignis neu versuchen
        const nach = new Map((katalog || []).map(s => [s.id, s]));
        const stuecke = Object.keys(Dazkleidung.kleidung(stand.inst)).map(k => nach.get(k) || { id: k, name: k, fehlt: true });
        const daz = stuecke.filter(s => (s.art === 'kleidung' && !s.anatomie) || s.art === 'haar');
        for (const stueck of daz.filter(s => s.oben)) stand.behaelter.appendChild(Genesis9eigenstueck.kasten(stand.inst, stueck));
        for (const [titel, eigene, fremde] of Genesis9eigengarderobe.kategorien(daz, einteilung)) {
            const kasten = document.createElement('details');
            kasten.className = 'g9-kategorie g9-eigen-kategorie';
            kasten.dataset.kategorie = titel;
            kasten.innerHTML = `<summary class="aufklappkopf">${escapeHtml(titel)} <span class="gedaempft">(${eigene.length + fremde.length})</span></summary>`;
            for (const art of eigene) kasten.appendChild(Genesis9eigenkleidkasten.kasten(stand.inst, art));
            for (const stueck of fremde) kasten.appendChild(Genesis9eigenstueck.kasten(stand.inst, stueck));
            stand.behaelter.appendChild(kasten);
        }
        // Getragen, aber nicht im Katalog (gelöscht, umbenannt, Katalog unvollständig): sichtbar statt still weggelassen.
        for (const s of stuecke.filter(s => s.fehlt && katalog?.length)) {
            Genesis9eigengarderobe._hinweis(stand.behaelter, `„${s.id}“ wird getragen, steht aber nicht in der Garderobe.`, 'fehlertext');
        }
    }

    /** `[[Kategorie, [eigene Arten], [getragene Daz-Stücke]]]` in der Reihenfolge der Einteilung — nur besetzte. */
    static kategorien(daz, einteilung) {
        const eigene = new Map();
        for (const [art, a] of Object.entries(Eigenkleidwerte.ARTEN)) {
            if (!eigene.has(a.kategorie)) eigene.set(a.kategorie, []);
            eigene.get(a.kategorie).push(art);
        }
        const fremde = new Map(Genesis9garderobekategorien.gruppen(daz, einteilung));
        const namen = [...new Set([...(einteilung.kategorien || []), ...eigene.keys(), ...fremde.keys()])];
        return namen.map(n => [n, eigene.get(n) || [], fremde.get(n) || []]).filter(([, e, f]) => e.length || f.length);
    }

    static _hinweis(behaelter, text, klasse = 'gedaempft') {
        const zeile = document.createElement('div');
        zeile.className = `${klasse} g9-eigenregler-leer`;
        zeile.textContent = text;
        behaelter.appendChild(zeile);
    }

    /** Einmal: auf jedes Stück hören, das an der Figur des Bereichs kommt oder geht; neu gebaut wird nur bei geändertem Bestand. */
    static _hoeren() {
        if (Genesis9eigengarderobe._hoert) return;
        Genesis9eigengarderobe._hoert = true;
        Stueckereignis.hoeren(({ inst }) => {
            const stand = Genesis9eigengarderobe._stand;
            if (!stand || inst !== stand.inst || !stand.behaelter.isConnected) return;
            if (Genesis9eigengarderobe.bestand(inst) !== stand.bestand) Genesis9eigengarderobe._bauen(stand);
        });
    }
}
