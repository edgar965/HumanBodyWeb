/**
 * Genesis9bauartwahl — im Kasten „Einstellungen“ eines Stücks: wie es sich bewegt (starr, anliegend, lose) und bis zu welcher Tiefe die Haut
 * darunter nachgibt (12.11.2026).
 *
 * Edgar, 12.11.2026: „man könnte doch einen Parameter setzen bis zu dem das mesh eingedrückt werden kann bei den animationen oder Ruhelage,
 * oder schuhe?“ und „mach alles, mit deinen Empfehlungen, mit dem Feature haut nachgeben lassen“. Beides ist ein Datum der Bibliothek, nicht
 * des Modells: Es gilt für jede Figur, die das Stück trägt (Server `G9bauart`, `garderobe_bauarten.json`). Leer heißt Vorschlag — starr nach
 * Kategorie (Schuhe, Requisiten, Kopfbedeckung), sonst die Entscheidung über dForce und Hautabstand; die Tiefe der Bauart steht im Feld als
 * Platzhalter (`Bauart.NACHGEBEN_MM`).
 *
 * Nach dem Setzen wird das Stück neu geholt: Der Speicher der Figur vergisst seine Antwort (`inst._antworten`), der Server hat den Stand im
 * Schlüssel (`G9antworten.schluessel`).
 */
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Bauart } from '../../gemeinsam/bauart.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Dazkleidung } from './dazkleidung.js';

export class Genesis9bauartwahl {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/';
    static NAMEN = { starr: 'starr (ein Knochen, behält die Form)', anliegend: 'anliegend (gehäutet)', lose: 'lose (Stoffschwung)' };

    /** Der gemerkte Stand der Bibliothek (`GET …/bauarten/`), einmal je Seitenleben. */
    static _stand = null;

    static passt(stueck) {
        return ['kleidung', 'requisit'].includes(stueck?.art) && !stueck.mischbar && !/^(haar_generisch|kleidung_generisch)/.test(stueck.id || '');
    }

    static stand() {
        Genesis9bauartwahl._stand ??= Serverabruf.json(`${Genesis9bauartwahl.ADRESSE}bauarten/`).catch((fehler) => {
            Genesis9bauartwahl._stand = null;
            Protokoll.warnung('Genesis9bauartwahl', `Bauarten nicht lesbar: ${fehler.message}`);
            return { bauart: {}, nachgeben_mm: {} };
        });
        return Genesis9bauartwahl._stand;
    }

    /** Die Bauart, die das getragene Stück gerade hat (vom Server, `Bauart.von`) — oder null, wenn es nicht getragen wird. */
    static wirksam(inst, kennung) {
        const netz = Object.entries(inst?.clothMeshes || {}).find(([schluessel]) => schluessel.startsWith(`${kennung}/`))?.[1];
        return netz ? Bauart.von(netz) : null;
    }

    static bauen(inst, stueck, werteLesen) {
        const kasten = document.createElement('div');
        kasten.className = 'genesis9-bauart';
        kasten.innerHTML = `
            <label class="genesis9-bauart-zeile">Bewegung
                <select class="genesis9-bauart-art"><option value="">Vorschlag</option>
                    ${Bauart.ARTEN.map((a) => `<option value="${a}">${Genesis9bauartwahl.NAMEN[a]}</option>`).join('')}</select></label>
            <label class="genesis9-bauart-zeile" title="Verdeckte Haut zieht unter dem Stück bis zu dieser Tiefe ein (an der Stoffkante 1 mm, nach innen mehr) — so kommt sie in der Bewegung nicht durch den Stoff.">Haut gibt nach bis
                <input type="number" class="genesis9-bauart-tiefe" min="1" max="50" step="1"> mm</label>`;   // 0 hieße im Einzug „keine Angabe“ (`Hauteinzugrechnung`)
        const wahl = kasten.querySelector('.genesis9-bauart-art');
        const tiefe = kasten.querySelector('.genesis9-bauart-tiefe');
        const vorschlagZeigen = () => {
            const art = wahl.value || Genesis9bauartwahl.wirksam(inst, stueck.id) || 'anliegend';
            tiefe.placeholder = String(Bauart.NACHGEBEN_MM[art] ?? '');
            wahl.options[0].textContent = `Vorschlag${Genesis9bauartwahl.wirksam(inst, stueck.id) ? ` (jetzt: ${Genesis9bauartwahl.wirksam(inst, stueck.id)})` : ''}`;
        };
        Genesis9bauartwahl.stand().then((stand) => {
            wahl.value = stand.bauart?.[stueck.id] || '';
            const mm = stand.nachgeben_mm?.[stueck.id];
            tiefe.value = mm == null ? '' : String(mm);
            vorschlagZeigen();
        });
        const senden = async () => {
            const nutzlast = { bauart: wahl.value || null, nachgeben_mm: tiefe.value === '' ? null : Number(tiefe.value) };
            try {
                const antwort = await Serverabruf.senden(`${Genesis9bauartwahl.ADRESSE}${encodeURIComponent(stueck.id)}/bauart/`, nutzlast);
                if (antwort?.fehler) throw new Error(antwort.fehler);
            } catch (fehler) {
                Protokoll.warnung('Genesis9bauartwahl', `${stueck.id}: ${fehler.message}`);
                return;
            }
            Genesis9bauartwahl._stand = null;                         // neu lesen beim nächsten Kasten
            inst?._antworten?.delete(`kleid:${stueck.id}`);           // die alte Antwort nicht aus dem Speicher der Figur bauen
            const getragen = Dazkleidung.kleidung(inst)?.[stueck.id];
            if (getragen) {
                const werte = werteLesen(); werte.regler = { ...(getragen.regler || {}) };      // wie ein Reglerzug (`Genesis9stueckregler._zeile`)
                Genesis9lauf.planen(inst, () => Dazkleidung.anziehenAuf(inst, stueck.id, werte), () => vorschlagZeigen(), `stueck:${stueck.id}`);
            }
            vorschlagZeigen();
        };
        wahl.addEventListener('change', senden);
        tiefe.addEventListener('change', senden);
        return kasten;
    }
}
