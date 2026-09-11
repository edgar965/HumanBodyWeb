import { Kombiliste } from '../gemeinsam/kombiliste.js';
import { garmentcodeRegler } from './garmentcode_regler.js';
import { GarmentcodeBauregler } from './garmentcode_bauregler.js';
import { GarmentcodeMaterial } from './garmentcode_material.js';
import { GarmentcodeAblauf } from './garmentcode_ablauf.js';
import { GarmentcodeGemeinsam } from './garmentcode_gemeinsam.js';

/**
 * Der Bedienteil für „Mehrere Stücke gemeinsam".
 *
 * DIE LISTE IST NÖTIG, WEIL DER REITER NUR EIN STÜCK ZEIGT: Beim T-Shirt
 * stehen 71 Feineinstellungen im Panel, bei der Hose andere. Wer beide
 * gemeinsam anziehen will, stellt erst das eine ein, übernimmt es, stellt
 * dann das zweite. Was übernommen wurde, ist ein Abzug der Reglerwerte von
 * DIESEM Augenblick — spätere Züge am Panel ändern den Eintrag nicht mehr.
 *
 * EIN EINTRAG LÄSST SICH NICHT NACHBEARBEITEN, und das ist eine
 * Entscheidung: Die Werte in den Reiter zurückzuladen hiesse, die Vorlage
 * zu wechseln (`garmentcodeRegler.laden` ist asynchron und stellt danach
 * das Gedächtnis dieser Vorlage her, nicht den Eintrag). Zwei Quellen für
 * dieselben Zahlen liefen auseinander. Wer etwas ändern will, nimmt den
 * Eintrag heraus und übernimmt neu; was drinsteht, sagt der Tooltip.
 *
 * Die Liste selbst (ohne DOM) steht in `gemeinsam/kombiliste.js`.
 */
class GarmentcodeKombi {

    constructor() {
        this.liste = new Kombiliste();
        this.reiter = null;
    }

    /** @param reiter der `GarmentcodeReiter` */
    einhaengen(reiter) {
        this.reiter = reiter;
        const hinzu = document.getElementById('gc-kombi-hinzu');
        if (!hinzu) return false;
        hinzu.addEventListener('click', () => this.uebernehmen());
        document.getElementById('gc-kombi-leeren')
            ?.addEventListener('click', () => {
                this.liste.leeren();
                this.liste.sichern();
                this.zeichnen();
            });
        document.getElementById('gc-kombi-bauen')
            ?.addEventListener('click',
                               () => GarmentcodeGemeinsam.bauen(reiter,
                                                                this.liste));
        // Was beim letzten Mal in der Liste stand (Edgar, 09.09.2026:
        // „merke dir die letzten Einstellungen auf allen Tabs").
        this.liste.laden();
        this.zeichnen();
        return true;
    }

    /** Das gerade eingestellte Stück in die Liste nehmen. */
    uebernehmen() {
        const auswahl = document.getElementById('gc-vorlage');
        const vorlage = auswahl ? auswahl.value : '';
        // Das Aussehen: vom getragenen Stück dieser Vorlage, wenn es eines
        // gibt — das ist die Farbe, die der Nutzer ihm gegeben hat. Sonst
        // der Stand des Panels (11.09.2026: „es wurde nur 1 Farbe genommen").
        const material = GarmentcodeMaterial.getragen(
            GarmentcodeMaterial.figur(), vorlage) || GarmentcodeMaterial.stand;
        const stand = this.liste.hinzufuegen(
            vorlage, GarmentcodeAblauf.titel(vorlage), garmentcodeRegler.werte,
            GarmentcodeBauregler.werte(), material);
        const wieviel = this.liste.anzahl === 1
            ? 'ein Stück' : `${this.liste.anzahl} Stücke`;
        this.melden(stand.ok
            ? `„${GarmentcodeAblauf.titel(vorlage)}" übernommen — `
              + `${wieviel} in der Kombination.`
            : stand.grund);
        this.liste.sichern();
        this.zeichnen();
    }

    /** Eine Zeile herausnehmen. */
    entfernen(nummer) {
        this.liste.entfernen(nummer);
        this.liste.sichern();
        this.zeichnen();
    }

    melden(text) {
        const feld = document.getElementById('gc-meldung');
        if (feld) { feld.textContent = text; feld.title = ''; }
    }

    // ------------------------------------------------------------- zeichnen

    zeichnen() {
        const ziel = document.getElementById('gc-kombi-liste');
        if (!ziel) return;
        ziel.innerHTML = '';
        if (!this.liste.anzahl) {
            ziel.appendChild(GarmentcodeKombi._hinweis(this.liste.verworfen
                ? 'Die gemerkte Kombination stammt aus einer älteren Fassung '
                  + '(ohne Farbe und Bauwerte je Stück) und wurde verworfen — '
                  + 'die Stücke bitte neu übernehmen.'
                : 'Noch nichts übernommen. Stück einstellen, dann '
                  + '„Übernehmen" — ab zwei Stücken kann gebaut werden.'));
        }
        this.liste.eintraege.forEach((eintrag, nummer) => {
            ziel.appendChild(this._zeile(eintrag, nummer));
        });
        const bauen = document.getElementById('gc-kombi-bauen');
        if (bauen) bauen.disabled = !this.liste.darfBauen().ok;
    }

    _zeile(eintrag, nummer) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.dataset.vorlage = eintrag.vorlage;
        const name = document.createElement('label');
        // Die Nummer ist die LAGE in der Liste, keine Aussage darüber, was
        // aussen liegt — das entscheidet die Simulation. Deshalb steht sie
        // nur als Ordnungszahl da und nicht als „Schicht".
        name.textContent = `${nummer + 1}. ${eintrag.titel}`;
        name.title = GarmentcodeKombi._reglertext(eintrag);
        // Die Farbe des Stücks als Punkt — sichtbar, nicht nur im Tooltip.
        // Vom getragenen Stück, wenn es eines gibt (das gewinnt beim Bau),
        // sonst vom Eintrag. `Garmentstoff.werte` liefert die Farbe als
        // Zahl, der Farbwähler als `#rrggbb` — beides wird zu CSS.
        const farbe = GarmentcodeKombi._css(
            GarmentcodeMaterial.getragen(GarmentcodeMaterial.figur(),
                                         eintrag.vorlage)?.farbe
            ?? eintrag.material?.farbe);
        if (farbe) {
            const punkt = document.createElement('span');
            punkt.className = 'gc-kombi-farbe';
            punkt.style.background = farbe;
            name.prepend(punkt);
        }
        const rechts = document.createElement('span');
        rechts.className = 'slider-val';
        rechts.textContent = GarmentcodeKombi._kurztext(eintrag);
        const weg = document.createElement('button');
        weg.className = 'btn-toggle hb-fest';
        weg.title = 'Aus der Kombination nehmen';
        weg.innerHTML = '<i class="fas fa-times"></i>';
        weg.addEventListener('click', () => this.entfernen(nummer));
        zeile.append(name, rechts, weg);
        return zeile;
    }

    /** „3 eigene · 2,0 mm anliegend" — was die Zeile über den Bau sagt. */
    static _kurztext(eintrag) {
        const anzahl = Object.keys(eintrag.regler || {}).length;
        const teile = [anzahl ? `${anzahl} eigene` : 'Vorgaben'];
        const anliegen = Number(eintrag.bau?.anliegen_mm);
        if (Number.isFinite(anliegen) && anliegen >= GarmentcodeBauregler.ANLIEGEN_MIN) {
            teile.push(`${anliegen.toFixed(1).replace('.', ',')} mm anliegend`);
        }
        return teile.join(' · ');
    }

    /** Was an dem Eintrag eingestellt war — als Tooltip, nicht als Liste. */
    static _reglertext(eintrag) {
        const werte = eintrag.regler || {};
        const pfade = Object.keys(werte).sort();
        const bau = Object.entries(eintrag.bau || {})
            .map(([name, wert]) => `bau.${name} = ${wert}`);
        if (!pfade.length && !bau.length) return `${eintrag.titel}: alles auf Vorgabe`;
        return `${eintrag.titel}\n`
            + pfade.map((p) => `${p} = ${werte[p]}`).concat(bau).join('\n');
    }

    /** Eine Farbe als CSS: Zahl (`0x212121`) oder Zeichenkette (`#212121`). */
    static _css(farbe) {
        if (typeof farbe === 'number' && Number.isFinite(farbe)) {
            return `#${farbe.toString(16).padStart(6, '0')}`;
        }
        return (typeof farbe === 'string' && farbe) ? farbe : null;
    }

    static _hinweis(text) {
        const kasten = document.createElement('div');
        kasten.className = 'hb-hinweis';
        kasten.textContent = text;
        return kasten;
    }
}

export const garmentcodeKombi = new GarmentcodeKombi();
