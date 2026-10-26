import { escapeHtml } from '../utils.js';
import { Umfaerbung } from '../../gemeinsam/umfaerbung.js';
import { Dazkleidung } from './dazkleidung.js';
import { Dazeigenschaften } from './dazeigenschaften.js';
import { Genesis9stueckregler } from './genesis9stueckregler.js';
import { Stueckfarbe } from './stueckfarbe.js';
import { Stueckstoff } from './stueckstoff.js';

/**
 * Genesis9eigenstueck — EIN getragenes Stück in Assets → Eigen, in der Kategorie der Garderobe (Stufe K1, 25.10.2026, Edgar: je Stück die Blöcke
 * Form, Sitz, Stoff, Textur; je Frisur Form, Strähnen, Farbe — seit K2a in Assets → Eigen statt im Reglerfeld „Eigen“, `Genesis9eigengarderobe`).
 *
 * KEINE EIGENEN REGLER: Jede Zeile kommt von einem vorhandenen Zeilenbauer, mit dessen Handler und dessen Zustand — die Reglerzeilen von
 * `Genesis9stueckregler._zeile` (wie „Einstellungen“ in der Garderobe und die Kästen der Genitalien; Wert in `inst.kleidung[kennung].regler`,
 * ein Zug zieht das Stück über `Dazkleidung.anziehenAuf` neu an), Stoffart, Rauheit, Glanz, Glanzsaum, Relief, Gewebe von `Stueckstoff.felder`, die Farbe des Stücks und
 * je Materialgruppe von `Stueckfarbe.feld` bzw. `Dazeigenschaften._gruppenzeile` (Shader, ohne Neubau). Gibt es für einen Block nichts,
 * steht dort „noch keine Regler (Stufe K2/K3)“.
 *
 * Welcher Block, entscheidet der Name des Reglers (der Server gibt ihn mit, `Genesis9/…`), bei den Sammeleinträgen („Haar – Generisch“)
 * hinter dem Vorsatz `<sorte>.`:
 *     Sitz      `drapierung:*`                                       (`G9drapierung`: Abstand, Ausbreitung, Glättung)
 *     Strähnen  `profil.*`, `str.*`                                  (`G9haarprofil` Wurzel/Spitze, `G9haarzusatz`) — nur Frisuren
 *     Stoff     `bild.falten_*`, Gruppe „Material“ (Transparenz)     (`G9faltenkarte` über `G9kleidtexturen`, `G9kleidtransparenz`)
 *     Textur    `bild.*`, `textur:*`, Gruppe „Textur“                (`G9kleidtexturen` Foto/Decal/Grau, `Kleidfarbmischung`)
 *     Form      alles andere: `passform:*`, `eigen.*` (eigene Morphe, Form (Ort), Operationen), `achse.*`, `GC_*`, Daz' eigene Kanäle
 *
 * Die Zeilen entstehen erst beim ersten Aufklappen (wie `Genesis9genitalien._stueck`) — „Haar – Generisch“ trägt die Regler ALLER Sorten.
 */
export class Genesis9eigenstueck {

    static BLOECKE = {
        kleidung: [['form', 'Form'], ['sitz', 'Sitz'], ['stoff', 'Stoff'], ['textur', 'Textur']],
        haar: [['form', 'Form'], ['straehnen', 'Strähnen'], ['textur', 'Farbe und Textur']],
    };
    static LEER = 'noch keine Regler (Stufe K2/K3)';

    /** Der Block eines Reglers der Garderobenliste (siehe Kopf). */
    static block(regler, art) {
        const name = String(regler.name || '');
        const hat = muster => new RegExp(`(^|\\.)${muster}`).test(name);
        if (hat('drapierung:')) return 'sitz';
        if (hat('(profil|str)\\.')) return art === 'haar' ? 'straehnen' : 'stoff';
        if (hat('bild\\.falten_') || regler.gruppe === 'Material' || hat('Transparenz$')) return art === 'haar' ? 'textur' : 'stoff';
        if (hat('bild\\.') || hat('textur:') || regler.gruppe === 'Textur') return 'textur';
        return 'form';
    }

    /** Der Klappkasten des Stücks; `inhalt` trägt `genesis9-stueckregler` (dort sucht `_aufteilen` die Sortenanteile) und die Kennung (`Genesis9eigenabgleich`). */
    static kasten(inst, stueck) {
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe g9-untergruppe g9-eigenkleid-stueck';
        kasten.dataset.stueck = stueck.id;
        kasten.innerHTML = `<summary>${escapeHtml(stueck.name || stueck.id)} <span class="gedaempft">(${stueck.regler?.length || 0})</span></summary>`;
        const inhalt = document.createElement('div');
        inhalt.className = 'genesis9-stueckregler';
        inhalt.dataset.eigenStueck = stueck.id;
        kasten.appendChild(inhalt);
        kasten.addEventListener('toggle', () => {
            if (kasten.open && !inhalt.childElementCount) Genesis9eigenstueck._bloecke(inhalt, inst, stueck);
        });
        return kasten;
    }

    static _bloecke(inhalt, inst, stueck) {
        const art = stueck.art === 'haar' ? 'haar' : 'kleidung';
        // Dieselbe Lesefunktion wie die Garderobe (`Genesis9garderobe._eintrag`): die Werte des getragenen Stücks, als Kopie.
        const werteLesen = () => ({ ...(Dazkleidung.kleidung(inst)[stueck.id] || {}) });
        const nach = {};
        for (const r of stueck.regler || []) (nach[Genesis9eigenstueck.block(r, art)] ||= []).push(r);
        for (const [schluessel, titel] of Genesis9eigenstueck.BLOECKE[art]) {
            inhalt.insertAdjacentHTML('beforeend', `<div class="gedaempft g9-eigenregler-unter">${escapeHtml(titel)}</div>`);
            const zusatz = Genesis9eigenstueck._zusatz(inst, stueck, schluessel, art);
            const regler = nach[schluessel] || [];
            for (const z of zusatz) inhalt.appendChild(z);
            Genesis9eigenstueck._reglerzeilen(inhalt, inst, stueck, regler, werteLesen);
            if (!zusatz.length && !regler.length) {
                inhalt.insertAdjacentHTML('beforeend', `<div class="gedaempft g9-eigenregler-leer">${escapeHtml(Genesis9eigenstueck.LEER)}</div>`);
            }
        }
    }

    /** Die Felder, die nicht aus der Reglerliste kommen: Stoff (`Stueckstoff`) bei Kleidung, Farbe des Stücks und je Materialgruppe. */
    static _zusatz(inst, stueck, block, art) {
        if (block === 'stoff' && art === 'kleidung') return [Stueckstoff.felder(inst, stueck.id)];
        if (block !== 'textur') return [];
        const werte = Dazkleidung.kleidung(inst)[stueck.id] || {};
        const titel = art === 'haar' ? 'Haarfarbe' : 'Farbe des Stücks';
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = `<label class="stueckname">${escapeHtml(titel)}</label>`;
        zeile.appendChild(Stueckfarbe.feld({ inst, kennung: stueck.id, wert: werte.farbe || '', titel }));
        const gruppen = [];
        for (const { netz } of Umfaerbung.netze(inst, stueck.id)) {
            for (const g of Dazeigenschaften.gruppen(netz)) if (!gruppen.includes(g)) gruppen.push(g);
        }
        return [zeile, ...gruppen.map(g => Dazeigenschaften._gruppenzeile(inst, stueck.id, g, werte))];
    }

    /** Die Reglerzeilen eines Blocks; mehrere Gruppen (Passform, Form (Ort), Daz' eigene …) je als Klappkasten wie unter „Einstellungen“. */
    static _reglerzeilen(ziel, inst, stueck, regler, werteLesen) {
        const gruppen = new Map();
        for (const r of regler) {
            if (!gruppen.has(r.gruppe)) gruppen.set(r.gruppe, []);
            gruppen.get(r.gruppe).push(r);
        }
        for (const [gruppe, eigene] of gruppen) {
            const kasten = gruppen.size > 1 ? Genesis9stueckregler._gruppe(ziel, gruppe || 'Weitere', eigene.length) : ziel;
            for (const r of eigene) kasten.appendChild(Genesis9stueckregler._zeile(inst, stueck, r, werteLesen));
        }
    }
}
