import { escapeHtml } from '../utils.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Dazkleidung } from './dazkleidung.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Genesis9garderobe } from './genesis9garderobe.js';
import { Genesis9stueckregler } from './genesis9stueckregler.js';
import { Genesis9garderobekategorien } from './genesis9garderobekategorien.js';
import { Genesis9genitalmenue } from './genesis9genitalmenue.js';

/**
 * Genesis9genitalien — der Bereich „Genitalien" unter Genesis 9 im Modell-Reiter (18.10.2026).
 *
 * Edgar, 18.10.2026: „mach eine extra Abteilung bei Genesis Morphs für die Genitalien" — „darin sollen auch die männlichen Genitalien kommen, und
 * von MakeHuman gibt es noch welche, sowie die eigene Implementierung" — „ein Eigener Bereich direkt unter Genesis (auf Ebene Haut, Augen ...)".
 * Ein eigener Klappbereich (`_genesis9_eigenschaften.html`, `#prop-genesis9-genitalien`), NICHT in der Reglerliste: der Server liefert die
 * Körperregler als Block `genitalien` im Reglerplan (Daz' Beule der Grundfigur, MakeHumans Volumen, die Körperform einer Scham aus einem Import —
 * `Genesis9/genitalregler.py`), `teilen` nimmt ihn aus der Liste. Dazu kommen die Stücke — alles aus der Garderobe mit einer Anatomie
 * (`anatomie`: vagina | penis, aus der `.ersetzt.json`), je Stück ein Klappkasten:
 *
 *     Daz        „Daz Anatomie Frau|Mann" — Daz' Geograft (`Dazgeograft`), weiblich und männlich
 *     MakeHuman  „MakeHuman Penis" — MakeHumans Genitalhelfer mit seinen drei Zielen (`Makehumangenital`)
 *     Eigene     Scham und Genitalien der Blender-Importe (`Blendimportstuecke`), Regler `sch_*`/`pen_*` (`G9vagina`/`G9penis`)
 *
 * Im Kasten „angelegt" (dasselbe wie das Häkchen in der Garderobe) und die Regler des Stücks — dieselben Zeilen wie unter „Einstellungen"
 * (`Genesis9stueckregler`), gebaut erst beim Aufklappen. Ein Regler wirkt nur am angelegten Stück; abgelegt wird sein Wert nur gemerkt.
 *
 * Rechtsklick auf den Kopf eines Kastens (oder die Zeile „angelegt"): Verschieben, Umbenennen, Löschen wie in der Garderobe
 * (Edgar, 18.10.2026: „Kontextmenü … mit dem ich die Assets löschen, verschieben und umbenennen kann") — `Genesis9genitalmenue`.
 */
export class Genesis9genitalien {

    static SCHLUESSEL = 'genitalien';
    static REIHE = ['Daz', 'MakeHuman', 'Eigene'];
    static ANATOMIE = { vagina: 'weiblich', penis: 'männlich', anus: 'Anus' };

    /** Woher das Stück kommt — an der Kennung (die Garderobe führt keine Herkunft für eigene Stücke). */
    static herkunft(stueck) {
        if (stueck.id.startsWith('daz_anatomie_')) return 'Daz';
        if (stueck.id.startsWith('makehuman_')) return 'MakeHuman';
        return 'Eigene';
    }

    /** Die zeigbaren Stücke mit Anatomie: Daz, MakeHuman, eigene; darin weiblich vor männlich, dann nach Namen. */
    static stuecke(alle) {
        const rang = s => Genesis9genitalien.REIHE.indexOf(Genesis9genitalien.herkunft(s));
        const art = s => (s.anatomie === 'vagina' ? 0 : 1);
        return (alle || []).filter(s => s.anatomie && s.zeigbar)
            .sort((a, b) => rang(a) - rang(b) || art(a) - art(b) || a.name.localeCompare(b.name, 'de'));
    }

    static getragen(inst, kennung) {
        return Boolean(Dazkleidung.kleidung(inst)[kennung]);
    }

    /** `[Plan ohne den Block „Genitalien", der Block]` — der Block leer, wenn der Server keinen schickt. */
    static teilen(plan) {
        const bereiche = plan?.bereiche || [];
        const block = bereiche.find(b => b.schluessel === Genesis9genitalien.SCHLUESSEL) || { schluessel: Genesis9genitalien.SCHLUESSEL, regler: [] };
        return [{ ...plan, bereiche: bereiche.filter(b => b !== block) }, block];
    }

    /** Den Bereich füllen: die Körperregler nach Gruppe (Daz, MakeHuman, eigene), darunter die Stücke. Wer zuletzt füllt, gewinnt (Figurwechsel beim Laden). */
    static async fuellen(behaelter, block, inst, zeileBauen) {
        if (!behaelter) return;
        const lauf = behaelter._lauf = (behaelter._lauf || 0) + 1;
        behaelter.innerHTML = '';
        let gruppe = null;
        for (const r of block.regler || []) {
            if (gruppe?.dataset.gruppe !== r.gruppe) {
                gruppe = Genesis9genitalien._kasten(r.gruppe, block.regler.filter(x => x.gruppe === r.gruppe).length);
                gruppe.dataset.gruppe = r.gruppe;
                behaelter.appendChild(gruppe);
            }
            gruppe.appendChild(zeileBauen(r));
        }
        let stuecke;
        try {
            // Der Stand der Kategorien gehört dazu: ohne ihn bietet das Menü kein „Verschieben" an, solange die Garderobe nicht gebaut ist.
            const [alle] = await Promise.all([Genesis9garderobe.liste(), Genesis9garderobekategorien.stand()]);
            stuecke = Genesis9genitalien.stuecke(alle);
        } catch (fehler) {
            stuecke = null;
            behaelter.appendChild(Genesis9genitalien._hinweis('fehlertext', `Genital-Stücke nicht geladen: ${fehler.message}`));
        }
        if (behaelter._lauf !== lauf || !stuecke) return;
        if (!stuecke.length) behaelter.appendChild(Genesis9genitalien._hinweis('gedaempft', 'Keine Genital-Stücke in der Garderobe.'));
        for (const stueck of stuecke) behaelter.appendChild(Genesis9genitalien._stueck(inst, stueck));
    }

    static _kasten(titel, anzahl) {
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe g9-untergruppe';
        kasten.innerHTML = `<summary>${escapeHtml(titel)} <span class="gedaempft">(${anzahl})</span></summary>`;
        return kasten;
    }

    static _hinweis(klasse, text) {
        const hinweis = document.createElement('div');
        hinweis.className = klasse;
        hinweis.textContent = text;
        return hinweis;
    }

    /** „Daz · weiblich — Daz Anatomie Frau": Herkunft, Art, Name — wie der Kopf des Kastens. */
    static titel(stueck) {
        const art = Genesis9genitalien.ANATOMIE[stueck.anatomie] || stueck.anatomie;
        return `${Genesis9genitalien.herkunft(stueck)} · ${art} — ${stueck.name}`;
    }

    static _stueck(inst, stueck) {
        const kasten = Genesis9genitalien._kasten(Genesis9genitalien.titel(stueck), stueck.regler?.length || 0);
        kasten.classList.add('g9-genitalstueck');
        kasten.dataset.stueck = stueck.id;
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const kennung = `g9-genital-${stueck.id}`;
        zeile.innerHTML = `<input type="checkbox" id="${escapeHtml(kennung)}"><label for="${escapeHtml(kennung)}" class="stueckname">angelegt</label>`;
        const haken = zeile.querySelector('input');
        haken.checked = Genesis9genitalien.getragen(inst, stueck.id);
        haken.addEventListener('change', () => Genesis9genitalien._schalten(inst, stueck, haken.checked));
        const regler = document.createElement('div');
        regler.className = 'genesis9-stueckregler';
        kasten.append(zeile, regler);
        Genesis9genitalmenue.binden(kasten, zeile, inst, stueck, Genesis9genitalien.titel);
        kasten.addEventListener('toggle', () => {
            haken.checked = Genesis9genitalien.getragen(inst, stueck.id);      // in der Garderobe umgeschaltet: hier nachziehen
            if (!kasten.open || regler.childElementCount || !stueck.regler?.length) return;
            Genesis9stueckregler._zeilen(regler, inst, stueck, () => ({ ...(Dazkleidung.kleidung(inst)[stueck.id] || {}) }));
        });
        return kasten;
    }

    /** Anlegen oder ablegen — derselbe Wunsch wie das Häkchen der Garderobe (`stueck:<kennung>`); danach ihre Liste nachziehen. */
    static _schalten(inst, stueck, an) {
        const fertig = () => { fn.updateVertexCount?.(); Genesis9garderobe.aktualisieren(inst); };
        if (!an) {
            Genesis9lauf.planen(inst, () => Dazkleidung.ausziehenAuf(inst, stueck.id), fertig, `stueck:${stueck.id}`);
            return;
        }
        const werte = Genesis9genitalien.werte(inst, stueck);
        Genesis9lauf.planen(inst,
            () => Dazkleidung.anziehenAuf(inst, stueck.id, werte).catch(fehler => Genesis9garderobe._misslungen(inst, stueck.id, fehler)),
            fertig, `stueck:${stueck.id}`);
    }

    /** Die Werte zum Anlegen wie `Genesis9garderobe.werte` — ohne Zeile: was gemerkt ist (Regler, Variante, Farbe), sonst die Vorgabe. */
    static werte(inst, stueck) {
        const bisher = Dazkleidung.kleidung(inst)[stueck.id] || {};
        return {
            variante: bisher.variante || '', stil: bisher.stil || '', stile: { ...(bisher.stile || {}) },
            regler: { ...(bisher.regler || {}) }, farbe: bisher.farbe || '', gruppenfarben: { ...(bisher.gruppenfarben || {}) },
            griff: Boolean(stueck.griff), knochen: Boolean(stueck.eigene_knochen),
        };
    }
}
