import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Dazkleidung } from './dazkleidung.js';
import { Sortenanteile } from './sortenanteile.js';
import { Kleidfarbmischung } from '../../gemeinsam/kleidfarbmischung.js';
import { Genesis9morphformular } from './genesis9morphformular.js';

/**
 * Genesis9stueckregler — die Anpassungsregler EINES Daz-Kleidungsstücks.
 *
 * Edgar, 18.09.2026: „es fehlen die Einstellungen für die Kleider". Jedes
 * Stück bringt eigene Morphkanäle mit (`Genesis9/anhangmorphe.py`: Viking-
 * Shirt *Adj Inflate Collar*, Worker-Overall *Loosen Back Upper*, Eirgrid
 * *Adjust Hairline*, Mavick *Wind*); der Server nennt sie in der Garderoben-
 * liste (`regler`, gruppiert nach Daz' Gruppe). Sie stehen aufklappbar unter
 * der Zeile des Stücks und wirken nur, wenn es angezogen ist — die Werte
 * liegen in `inst.kleidung[kennung].regler` und werden mitgespeichert.
 */
export class Genesis9stueckregler {

    /**
     * Der Kasten „Einstellungen" eines Stücks — mit dem Kopf; die Zeilen entstehen erst beim ERSTEN Aufklappen.
     *
     * Edgar, 09.10.2026: „warum dauert laden des Characters ewig … ich brauche schnelles Anzeigen, damit ich drehen und
     * vergrößern kann". Gemessen (Chrome, `/Charakter/`): Die Garderobe baute für alle 634 Stücke ihre Regler und das Formular
     * „Neuer Morph" sofort — 18.017 Schieber, 2.281 Auswahllisten, 130.529 DOM-Elemente, 568 Abrufe von `landmarken/` (je
     * Formular einer, doppelt gebaut: 1.137), und der Hauptfaden stand danach ~44 s. Zu sehen ist davon nichts, solange die
     * Kästen zu sind (alle stehen ZU, `Genesis9garderobe`).
     */
    static bauen(inst, stueck, werteLesen) {
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe genesis9-stueckregler';
        kasten.innerHTML = `<summary class="gedaempft">Einstellungen `
            + `<span class="gedaempft">(${stueck.regler.length})</span></summary>`;
        let gebaut = false;
        kasten.addEventListener('toggle', () => {
            if (!kasten.open || gebaut) return;
            gebaut = true;
            Genesis9stueckregler._zeilen(kasten, inst, stueck, werteLesen);
        });
        return kasten;
    }

    /** Die Zeilen, Gruppen und das Morph-Formular in den aufgeklappten Kasten. */
    static _zeilen(kasten, inst, stueck, werteLesen) {
        const gruppen = new Map();
        for (const r of stueck.regler) {
            if (!gruppen.has(r.gruppe)) gruppen.set(r.gruppe, []);
            gruppen.get(r.gruppe).push(r);
        }
        for (const [gruppe, regler] of gruppen) {
            const ziel = gruppen.size > 1
                ? Genesis9stueckregler._gruppe(kasten, gruppe, regler.length)
                : kasten;
            for (const r of regler) ziel.appendChild(Genesis9stueckregler._zeile(inst, stueck, r, werteLesen));
        }
        // Das freie Morph-Formular (01.10.2026) unter den Reglern jedes echten Stücks — Sammeleinträge („Haar –
        // Generisch", „Kleidung – Generisch") haben kein eigenes Netz, dort nicht.
        if (['kleidung', 'haar'].includes(stueck.art) && !stueck.mischbar && !/^(haar_generisch|kleidung_generisch)/.test(stueck.id)) {
            kasten.appendChild(Genesis9morphformular.bauen(inst, stueck, werteLesen,
                regler => Genesis9stueckregler._zeile(inst, stueck, regler, werteLesen)));
        }
    }

    /** Eine Gruppe als eigener Klappkasten (Edgar, 30.09.2026: „in Kategorien der jeweiligen
     *  Hauptsorte … und aufklappbar"). Kopf wie die Kategorien der Garderobe.
     *
     *  IMMER ZU, OHNE GEDÄCHTNIS (Edgar, 30.09.2026: „ALLE Einträge in den Tabs zu Assets und
     *  anderen sollen beim Laden IMMER zugeklappt sein. das hatte ich schon 10 Mal in Auftrag
     *  gegeben"). Ein `localStorage`-Gedächtnis stand hier zwischenzeitlich — genau das hält
     *  Kästen über Seitenaufrufe hinweg offen und ist der Grund, warum die Bitte immer wieder
     *  kommt. Aufgeklappt wird nur, was der Nutzer JETZT anklickt. */
    static _gruppe(kasten, gruppe, anzahl) {
        const eigen = document.createElement('details');
        eigen.className = 'g9-kategorie genesis9-reglergruppe';
        eigen.open = false;
        eigen.innerHTML = `<summary class="aufklappkopf">${escapeHtml(gruppe)} `
            + `<span class="gedaempft">(${anzahl})</span></summary>`;
        kasten.appendChild(eigen);
        return eigen;
    }

    static _zeile(inst, stueck, regler, werteLesen) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const wert = Dazkleidung.kleidung(inst)[stueck.id]?.regler?.[regler.name] ?? regler.vorgabe ?? 0;
        const mischen = stueck.mischbar && Sortenanteile.ist(regler.name);
        // Der Server nennt den Hinweis am Regler (`hinweis`, „Kleidung – Generisch": Anteile ohne feste Summe).
        const hinweis = mischen ? ' — Summe aller Anteile ist immer 100 %; eine andere Sorte hochziehen, um zu mischen'
            : (regler.hinweis ? ` — ${regler.hinweis}` : '');
        zeile.innerHTML = `
            <label title="${escapeHtml(regler.name + hinweis)}">${escapeHtml(regler.anzeige)}</label>
            <input type="range" min="${regler.min}" max="${regler.max}" step="${regler.schritt || 0.01}" value="${wert}"
                   data-regler="${escapeHtml(regler.name)}">
            <span class="slider-value">${Genesis9stueckregler.text(wert, regler)}</span>`;
        const schieber = zeile.querySelector('input');
        const anzeige = zeile.querySelector('.slider-value');
        schieber.addEventListener('input', () => {
            const neu = parseFloat(schieber.value); anzeige.textContent = Genesis9stueckregler.text(neu, regler);
            const getragen = Dazkleidung.kleidung(inst)[stueck.id];
            if (!getragen) return;                       // nicht angezogen: nur merken
            const werte = werteLesen(); werte.regler = { ...(getragen.regler || {}) };
            if (Kleidfarbmischung.ist(regler.name)) {
                // Textur-Regler von „Kleidung – Generisch": wirkt nur im Shader — kein Neubau, keine Anfrage.
                if (Math.abs(neu - (regler.vorgabe ?? 0)) < 1e-6) delete werte.regler[regler.name];
                else werte.regler[regler.name] = neu;
                getragen.regler = werte.regler;
                Kleidfarbmischung.anwenden(inst, stueck.id, werte.regler);
                markDirty();
                return;
            }
            if (mischen) {
                Genesis9stueckregler._aufteilen(schieber, stueck, regler, neu, werte.regler);
            } else {
                // Weggelassen wird nur, was auf seiner VORGABE steht — nicht, was auf 0 steht.
                // Bei „Haar – Generisch" hat die getragene Sorte die Vorgabe 1,0: Wer sie auf 0
                // zog, löschte damit den Eintrag, und der Server nahm wieder 1,0 an — die
                // Grundfrisur war nicht herunterzudrehen (Edgar, 30.09.2026).
                const vorgabe = regler.vorgabe ?? 0;
                if (Math.abs(neu - vorgabe) < 1e-6) delete werte.regler[regler.name];
                else werte.regler[regler.name] = neu;
            }
            Genesis9stueckregler._zuletzt(werte.regler, regler.name);
            Genesis9lauf.planen(inst, () => Dazkleidung.anziehenAuf(inst, stueck.id, werte), () => {},
                                `stueck:${stueck.id}`);
            markDirty();
        });
        return zeile;
    }

    /**
     * „Haar – Generisch": die anderen Sortenregler proportional nachziehen, damit die Summe
     * 100 % bleibt (Edgar, 30.09.2026), und zwar SICHTBAR — jeder Schieber und jede Anzeige
     * des Stücks springt auf seinen neuen Anteil, auch in zugeklappten Gruppen.
     *
     * Gerechnet wird mit den GESPEICHERTEN Werten (Vorgabe, wo keiner steht), nicht mit den
     * Schiebern: Ein Schieber rundet auf seinen Schritt (0,01), und über mehrere Züge liefe
     * die Summe davon. Die Schieber zeigen nur an.
     */
    static _aufteilen(schieber, stueck, regler, neu, werteRegler) {
        const vorgaben = Object.fromEntries(stueck.regler
            .filter(r => Sortenanteile.ist(r.name)).map(r => [r.name, r.vorgabe ?? 0]));
        const aktuell = {};
        for (const name of Object.keys(vorgaben)) aktuell[name] = werteRegler[name] ?? vorgaben[name];
        const aufteilung = Sortenanteile.ziehen(aktuell, regler.name, neu);
        Sortenanteile.eintragen(werteRegler, aufteilung, vorgaben);
        const kasten = schieber.closest('.genesis9-stueckregler');
        for (const s of kasten?.querySelectorAll('input[data-regler^="sorte."]') || []) {
            const wert = aufteilung[s.dataset.regler] ?? 0;
            s.value = String(wert);
            const text = s.closest('.slider-row')?.querySelector('.slider-value');
            if (text) text.textContent = Genesis9stueckregler.text(wert);
        }
    }

    /**
     * Welchen Sortenregler der Nutzer zuletzt bewegt hat („Haar – Generisch").
     *
     * Zwei Frisuren auf 100 % sind serverseitig nicht zu unterscheiden — beide Netze
     * wären gleich „gewollt", und ohne diese Angabe müsste eine feste Reihenfolge
     * entscheiden, also der Zufall der Garderobenliste. Der Browser weiß es: Es ist der
     * Regler unter der Hand des Nutzers (`G9haargenerisch.ZULETZT`).
     */
    static _zuletzt(regler, name) {
        if (!name.startsWith('sorte.')) return;
        regler.sorte_zuletzt = name.slice('sorte.'.length);
    }

    /** Daz-Regler in Prozent; Passform-Regler (`einheit: cm`, `Genesis9/passform.py`) in Zentimetern. */
    static text(wert, regler = null) {
        if (regler?.einheit === 'cm') return `${(Math.round(wert * 10) / 10).toFixed(1)} cm`;
        return `${Math.round(wert * 100)} %`;
    }
}
