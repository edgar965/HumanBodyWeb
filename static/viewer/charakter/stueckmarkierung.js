import { fn } from '../gemeinsam/registrierung.js';
import { Reiterzuordnung } from '../gemeinsam/reiterzuordnung.js';
import { Reiterinhalt } from './reiterinhalt.js';

/**
 * Stueckmarkierung — das angeklickte Stück in SEINEM Reiter zeigen, mit
 * SEINER Zeile markiert.
 *
 * Edgar, 20.09.2026: „wenn ich auf ein Asset oder Garment Code oder was auch
 * immer klicke, soll in der Toolbar genau das ausgewählt sein. das hatte ich
 * schon oft so als Auftrag vergeben!" Bis dahin tat das nur GarmentCode
 * (`Reiterzuordnung`, 09.09.2026); die Daz-Garderobe, MakeHuman, Garment Fit
 * und die Kleider blieben im Modell-Reiter, ihre Zeile unmarkiert.
 *
 * Der Reiter wird GEKLICKT, nicht nur umgeschaltet: am Klick hängen
 * `Figurmerker` und `Reitergedaechtnis` (`szene.md`). Die Zeile wird erst
 * gesucht, wenn der Reiter gebaut ist (`Reiterinhalt.bauen` liefert das
 * Versprechen) — beim ersten Öffnen steht die Liste sonst noch nicht.
 * Welche Zeile: je Liste ihr eigenes Kennzeichen (`Reiterzuordnung.stueckVon`).
 * Der Zustand (`state`, hängt an Three) kommt herein — so läuft die Klasse im
 * Node-Test mit einer DOM-Attrappe (`test_js_stueckmarkierung.py`).
 */
export class Stueckmarkierung {

    /** @param zustand `scene/state.js` — trägt `_selectedGarmentId`, `_selectedMHId` */
    constructor(zustand) {
        this.zustand = zustand;
    }

    /** Zeile je Liste: `(kennung) => Element | null`. */
    static ZEILEN = {
        garment: k => document.querySelector(`#garment-list .garment-item[data-garment-id="${CSS.escape(k)}"]`),
        makehuman: k => document.querySelector(`#mh-list .anim-item[data-garment-id="${CSS.escape(k)}"]`),
        daz: k => document.getElementById(`g9-kleid-${k}`)?.closest('.slider-row'),
    };

    /** Reiter öffnen und das Stück darin markieren; ohne Stück (Abwahl) nur der Reiter. */
    zeigen(ziel) {
        const reiter = Reiterzuordnung.fuer(ziel?.key);
        Stueckmarkierung.reiterKlicken(reiter);
        const stueck = Reiterzuordnung.stueckVon(ziel?.key);
        if (!stueck) { Stueckmarkierung.loeschen(); return Promise.resolve(); }
        return Reiterinhalt.bauen(reiter).then(() => this.markieren(stueck, ziel));
    }

    /** Die gemerkte Herkunft (Vorbild/Form) des angeklickten GC-Stücks —
     *  `null` ohne Ziel, ohne `charId` (Testaufrufe) oder ohne bekannte
     *  Herkunft (freie Regler). */
    static gcQuelle(zustand, ziel) {
        const inst = ziel && zustand?.characters?.get(ziel.charId);
        return inst?.gcStuecke?.[ziel.key]?.quelle || null;
    }

    /** Abwahl: die Daz-Zeile ist nur unsere Marke — weg damit. Kleider, MakeHuman und
     *  Garment Fit führen ihre Listenwahl selbst und behalten sie. */
    static loeschen() {
        document.querySelectorAll('.slider-row.selected').forEach(el => el.classList.remove('selected'));
    }

    static reiterKlicken(reiter) {
        const knopf = document.querySelector(`.panel-tab[data-tab="${reiter}"]`);
        if (!knopf) { fn.switchTab?.(reiter); return; }
        if (!knopf.classList.contains('active')) knopf.click();
    }

    /** Die Daz-Garderobe füllt sich nach dem Wählen der Figur vom Server — so lange warten. */
    static WARTEN_MS = 250;
    static VERSUCHE = 12;

    async markieren({ liste, kennung }, ziel = null) {
        if (liste === 'garmentcode') {
            // Vorbild-Knopf oder Form-Häkchen des angeklickten Stücks mit-
            // zeigen (24.09.2026) — gemerkt beim Bau, in `inst.gcStuecke`.
            fn.garmentcodeQuelleZeigen?.(kennung, Stueckmarkierung.gcQuelle(this.zustand, ziel));
            return;
        }
        if (liste === 'kleider') { fn.kleiderSelectById?.(kennung); return; }
        if (liste === 'garment') this.zustand._selectedGarmentId = kennung;
        if (liste === 'makehuman') this.zustand._selectedMHId = kennung;
        const zeile = await Stueckmarkierung.zeile(liste, kennung);
        if (!zeile) return;
        Stueckmarkierung.hervorheben(zeile, liste === 'garment' ? 'active' : 'selected');
        if (liste === 'makehuman') fn.mhAuswahlGeaendert?.();
    }

    /** Die Zeile des Stücks — oder `null`, wenn sie auch nach 3 s nicht da ist. */
    static async zeile(liste, kennung) {
        const suchen = Stueckmarkierung.ZEILEN[liste];
        if (!suchen) return null;
        for (let versuch = 0; versuch < Stueckmarkierung.VERSUCHE; versuch += 1) {
            const zeile = suchen(kennung);
            if (zeile) return zeile;
            await new Promise(weiter => setTimeout(weiter, Stueckmarkierung.WARTEN_MS));
        }
        return null;
    }

    /** Die Zeile allein markiert, ihr Ordner offen, sie im Blick. */
    static hervorheben(zeile, klasse) {
        const liste = zeile.closest('.anim-tree, #garment-list, #mh-list') || zeile.parentElement;
        liste.querySelectorAll(`.${klasse}`).forEach(el => el.classList.remove(klasse));
        zeile.classList.add(klasse);
        Stueckmarkierung.aufklappen(zeile);
        zeile.scrollIntoView({ block: 'nearest' });
    }

    /** Der Bereich (`.panel-section`, `collapsed` aus `expanded_panels_scene`), dann `<details>`
     *  (Daz-Kategorien), `.anim-category` (Garment Fit), `.anim-folder` (MakeHuman). */
    static aufklappen(zeile) {
        zeile.closest('.panel-section')?.classList.remove('collapsed');
        const kasten = zeile.closest('details');
        if (kasten) kasten.open = true;
        zeile.closest('.anim-category')?.classList.add('open');
        const ordner = zeile.closest('.anim-folder');
        if (ordner) {
            const rumpf = ordner.querySelector('.anim-folder-body');
            if (rumpf) rumpf.style.display = '';
            const pfeil = ordner.querySelector('.chevron');
            if (pfeil) pfeil.textContent = '▼';
        }
    }
}
