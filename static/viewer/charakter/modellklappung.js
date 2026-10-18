import { state } from './state.js';
import { Figurmerker } from './figurmerker.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Modellklappung — welche Bereiche im Reiter „Modell" (`#tab-eigenschaften`) offen stehen.
 *
 * AUFTRAG (Edgar, 18.10.2026): „Die Kategorien beim Tab Modell sind aufgeklappt, wenn ich auf das Modell im View
 * klicke. Diese Kategorien sollen immer zugeklappt sein. Nur die letzte hinzugefügte oder geänderte Eigenschaft soll
 * aufgeklappt sein."
 *
 * Vorher öffnete jeder Füller seine eigenen Bereiche: die Vorlagen per `open` (Haut, Form, Hautebenen …), Genesis 9
 * den Bereich „Figur", UMA „Körper", der gemeinsame Block jede Gruppe, und die `panel-section`s standen offen.
 * `anwenden` läuft nach dem Füllen (`properties.js`, `_gemerktesHerstellen`), klappt ALLES zu — `panel-section`
 * (`collapsed`) und `<details>` — und öffnet nur die Kette über der zuletzt geänderten Eigenschaft DIESER Figur.
 *
 * Gemerkt wird je Figur im `Figurmerker`: der Selektor des Feldes (Id, sonst `data-regler`/`data-morph`/`data-meta`)
 * und die Titel der Bereiche darüber — die Titel sind der Rückweg, wenn das Feld beim nächsten Füllen nicht mehr da ist;
 * Zähler wie „(57)" zählen nicht mit. „Hinzugefügt" merkt, wer eine Eigenschaft hinzufügt, über `merken` — bis jetzt
 * das Körpermorph-Formular („Nachformung (Ort)") seinen neuen Regler. Ein Stück, das in die Liste „Assets" kommt, zählt
 * NICHT: Dieselbe Liste füllt sich auch beim Laden der Szene, ohne dass jemand etwas hinzugefügt hat.
 *
 * NUR BEIM AUSWÄHLEN, nicht während der Arbeit: Ein Bereich, der beim Ziehen eines Schiebers darüber zuklappte,
 * schöbe den Schieber unter dem Mauszeiger weg.
 *
 * KLICK AUF DEN KÖRPER IM VIEWER (Edgar, 18.10.2026): „wenn ich auf das Modell klicke im Viewer, soll der Modell Tab
 * ausgewählt sein und ausgeklappt werden". `vomViewer` merkt der Figur den Reiter „Modell" (den stellt danach
 * `_gemerktesHerstellen` her) und öffnet beim nächsten `anwenden` den Hauptbereich ihrer Figurart (`HAUPTBEREICHE`,
 * der erste sichtbare) — die Kategorien darin bleiben zu, bis auf die Kette der zuletzt geänderten Eigenschaft.
 */
export class Modellklappung {

    static INHALT = 'prop-content';
    /** Felder, die etwas BAUEN, statt selbst eine Eigenschaft zu sein — die gebaute merkt der Bauer. */
    static AUSGENOMMEN = '.genesis9-morphformular';
    static MERKMALE = ['regler', 'morph', 'meta'];
    static KASTEN = '.panel-section, details';
    /** Je Figurart ihr Hauptbereich; HumanBody hat keinen eigenen Block, dort ist es der Körpertyp. */
    static HAUPTBEREICHE = ['prop-genesis9-section', 'prop-uma-section', 'prop-umapython-section', 'prop-smpl-section',
                            'prop-makehuman-section', 'prop-bodytype-section'];
    static _verdrahtet = false;
    static _vomViewer = null;

    /** Ein Klick auf den Körper der Figur `id` im Viewer — vor `selectCharacter` zu rufen. */
    static vomViewer(id) {
        Figurmerker.tabMerken(id, 'eigenschaften');
        Modellklappung._vomViewer = id;
    }

    /** Alles zu, nur die Kette über der zuletzt geänderten Eigenschaft der Figur `id` auf — nach einem Viewer-Klick dazu der Hauptbereich. */
    static anwenden(id) {
        Modellklappung._verdrahten();
        const inhalt = document.getElementById(Modellklappung.INHALT);
        if (!inhalt) return;
        for (const bereich of inhalt.querySelectorAll('.panel-section')) bereich.classList.add('collapsed');
        for (const kasten of inhalt.querySelectorAll('details')) kasten.open = false;
        const ziel = Modellklappung._finden(inhalt, Figurmerker.eigenschaft(id));
        for (let k = ziel; k && k !== inhalt; k = k.parentElement) {
            if (k.classList.contains('panel-section')) k.classList.remove('collapsed');
            if (k.tagName === 'DETAILS') k.open = true;
        }
        if (Modellklappung._vomViewer !== id) return;
        Modellklappung._vomViewer = null;
        const haupt = Modellklappung.HAUPTBEREICHE.map(k => document.getElementById(k))
            .find(el => el && inhalt.contains(el) && !el.closest('.hb-versteckt'));
        haupt?.classList.remove('collapsed');
    }

    /** `feld` (ein Element im Reiter) als zuletzt geänderte Eigenschaft der Figur merken. */
    static merken(feld, id = state.currentPropsCharId) {
        const inhalt = document.getElementById(Modellklappung.INHALT);
        if (!feld || !id || !inhalt?.contains(feld)) return;
        const pfad = [];
        for (let k = feld; k && k !== inhalt; k = k.parentElement) {
            if (k.matches(Modellklappung.KASTEN)) pfad.unshift(Modellklappung._titel(k));
        }
        Figurmerker.eigenschaftMerken(id, { ziel: Modellklappung._selektor(feld), pfad });
    }

    /** Einmal je Seite. `change` statt `input`: ein Schieberzug schreibt so einmal, nicht je Pixel. */
    static _verdrahten() {
        const inhalt = document.getElementById(Modellklappung.INHALT);
        if (!inhalt || Modellklappung._verdrahtet) return;
        Modellklappung._verdrahtet = true;
        inhalt.addEventListener('change', (ereignis) => {
            // Nur der Nutzer — ein Preset stellt Schieber per `dispatchEvent`, das ist keine Wahl im Reiter.
            if (!ereignis.isTrusted || ereignis.target.closest(Modellklappung.AUSGENOMMEN)) return;
            Modellklappung.merken(ereignis.target);
        });
    }

    static _selektor(feld) {
        if (feld.id) return `#${CSS.escape(feld.id)}`;
        for (const merkmal of Modellklappung.MERKMALE) {
            const wert = feld.dataset?.[merkmal];
            if (wert) return `[data-${merkmal}="${CSS.escape(wert)}"]`;
        }
        return null;
    }

    static _titel(kasten) {
        const kopf = kasten.querySelector(kasten.tagName === 'DETAILS' ? ':scope > summary' : ':scope > h3');
        return (kopf?.textContent || '').replace(/\(\d[\d.,]*\)|[▼▶]/g, '').replace(/\s+/g, ' ').trim();
    }

    /** Das Feld selbst (sichtbar), sonst der innerste Bereich, den die Titel noch finden. */
    static _finden(inhalt, wo) {
        if (!wo) return null;
        const sichtbar = el => !el.closest('.hb-versteckt');
        if (wo.ziel) {
            try {
                const treffer = [...inhalt.querySelectorAll(wo.ziel)].find(sichtbar);
                if (treffer) return treffer;
            } catch (fehler) {
                Protokoll.debug('modellklappung', 'Selektor ungültig', fehler);
            }
        }
        let ort = inhalt;
        let gefunden = null;
        for (const titel of wo.pfad || []) {
            const kasten = [...ort.querySelectorAll(Modellklappung.KASTEN)]
                .find(k => sichtbar(k) && Modellklappung._titel(k) === titel);
            if (!kasten) break;
            gefunden = ort = kasten;
        }
        return gefunden;
    }
}
