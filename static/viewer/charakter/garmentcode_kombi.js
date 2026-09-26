import { Kombiliste } from '../gemeinsam/kombiliste.js';
import { GarmentcodeTitel } from './garmentcode_titel.js';
import { garmentcodeRegler } from './garmentcode_regler.js';
import { GarmentcodeBauregler } from './garmentcode_bauregler.js';
import { GarmentcodeMaterial } from './garmentcode_material.js';
import { GarmentcodeAblauf } from './garmentcode_ablauf.js';
import { GarmentcodeGemeinsam } from './garmentcode_gemeinsam.js';
import { GarmentcodeKombiBearbeiten } from './garmentcode_kombi_bearbeiten.js';

/**
 * Der Bedienteil für „Mehrere Stücke gemeinsam".
 *
 * DIE LISTE IST NÖTIG, WEIL DER REITER NUR EIN STÜCK ZEIGT: Beim T-Shirt
 * stehen 71 Feineinstellungen im Panel, bei der Hose andere. Wer beide
 * gemeinsam anziehen will, stellt erst das eine ein, übernimmt es, stellt
 * dann das zweite. Was übernommen wurde, ist ein Abzug der Reglerwerte von
 * DIESEM Augenblick — spätere Züge am Panel ändern den Eintrag nicht mehr.
 *
 * EIN EINTRAG LÄSST SICH NACHBEARBEITEN — über den Reiter, nicht in der
 * Zeile (Edgar, 20.09.2026: „kann ich die Eigenschaften des Stücks nicht
 * mehr nachträglich ändern. Fixe"): Der Stift lädt den Eintrag in den
 * Reiter (`garmentcode_kombi_bearbeiten.js`), die Zeile ist solange
 * markiert, und „Übernehmen" schreibt ihn an seiner Stelle zurück. Der
 * Eintrag folgt keinem Reglerzug von selbst — zwei Quellen für dieselben
 * Zahlen liefen auseinander; was drinsteht, sagt der Tooltip. Wer die
 * Vorlage wechselt, verlässt die Bearbeitung.
 *
 * Die Liste selbst (ohne DOM) steht in `gemeinsam/kombiliste.js`.
 */
class GarmentcodeKombi {

    constructor() {
        this.liste = new Kombiliste();
        this.reiter = null;
        /** Nummer des Eintrags, der gerade im Reiter steht — oder null. */
        this.bearbeitet = null;
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
        // Eine andere Vorlage im Reiter heisst: nicht mehr dieser Eintrag.
        document.getElementById('gc-vorlage')?.addEventListener('change', (ereignis) => {
            const eintrag = this.bearbeitet === null
                ? null : this.liste.eintraege[this.bearbeitet];
            if (eintrag && ereignis.target.value !== eintrag.vorlage) this.abbrechen();
        });
        // Was beim letzten Mal in der Liste stand (Edgar, 09.09.2026:
        // „merke dir die letzten Einstellungen auf allen Tabs").
        this.liste.laden();
        this.zeichnen();
        return true;
    }

    /** Das gerade eingestellte Stück in die Liste nehmen — oder den
     *  bearbeiteten Eintrag an seiner Stelle ersetzen. */
    uebernehmen() {
        const auswahl = document.getElementById('gc-vorlage');
        const vorlage = auswahl ? auswahl.value : '';
        // Das Aussehen: vom getragenen Stück dieser Vorlage, wenn es eines
        // gibt — das ist die Farbe, die der Nutzer ihm gegeben hat. Sonst
        // der Stand des Panels (11.09.2026: „es wurde nur 1 Farbe genommen").
        const getragen = GarmentcodeMaterial.getragen(GarmentcodeMaterial.figur(), vorlage);
        // Der bestellte Name: Vorbild, Form oder Vorlage (20.09.2026,
        // `garmentcode_titel.js`) — so heisst das Stueck dann auch in der Szene.
        const titel = GarmentcodeTitel.aktuell(vorlage);
        const nummer = this.bearbeitet;
        const ersetzt = nummer !== null && this.liste.eintraege[nummer]?.vorlage === vorlage;
        // Beim Ersetzen ohne getragenes Stück bleibt das Material des Eintrags.
        const stand = ersetzt
            ? this.liste.ersetzen(nummer, vorlage, titel, garmentcodeRegler.werte,
                                  GarmentcodeBauregler.werte(), getragen)
            : this.liste.hinzufuegen(vorlage, titel, garmentcodeRegler.werte,
                                     GarmentcodeBauregler.werte(),
                                     getragen || GarmentcodeMaterial.stand);
        const wieviel = this.liste.anzahl === 1
            ? 'ein Stück' : `${this.liste.anzahl} Stücke`;
        let text = stand.grund;
        if (stand.ok) {
            text = ersetzt ? `„${titel}" (${nummer + 1}.) geändert übernommen.`
                : `„${titel}" übernommen — ${wieviel} in der Kombination.`;
            this.bearbeitet = null;
        }
        this.melden(text);
        this.liste.sichern();
        this.zeichnen();
    }

    /** Einen Eintrag in den Reiter laden, um ihn zu ändern. */
    async bearbeiten(nummer) {
        const eintrag = this.liste.eintraege[nummer];
        if (!eintrag) return false;
        this.bearbeitet = nummer;
        this.zeichnen();
        this.melden(`„${eintrag.titel}" (${nummer + 1}.) wird geladen …`);
        const da = await GarmentcodeKombiBearbeiten.laden(eintrag);
        if (this.bearbeitet !== nummer) return false;      // inzwischen abgebrochen
        this.melden(da
            ? `„${eintrag.titel}" (${nummer + 1}.) steht im Reiter — ändern, `
              + 'dann schreibt „Übernehmen" es an seine Stelle zurück.'
            : `„${eintrag.titel}" liess sich nicht laden — die Regler der Vorlage fehlen.`);
        if (!da) this.abbrechen();
        return da;
    }

    /** Die Bearbeitung verlassen, ohne etwas zu ändern. */
    abbrechen() {
        if (this.bearbeitet === null) return;
        this.bearbeitet = null;
        this.zeichnen();
    }

    /** Eine Zeile herausnehmen. */
    entfernen(nummer) {
        this.liste.entfernen(nummer);
        if (this.bearbeitet !== null) {
            if (this.bearbeitet === nummer) this.bearbeitet = null;
            else if (this.bearbeitet > nummer) this.bearbeitet -= 1;
        }
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
        const hinzu = document.getElementById('gc-kombi-hinzu');
        if (hinzu) {
            hinzu.innerHTML = this.bearbeitet === null
                ? '<i class="fas fa-plus"></i> Stück übernehmen'
                : `<i class="fas fa-check"></i> Änderung übernehmen (${this.bearbeitet + 1}.)`;
        }
    }

    _zeile(eintrag, nummer) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row' + (nummer === this.bearbeitet ? ' gc-kombi-aktiv' : '');
        zeile.dataset.vorlage = eintrag.vorlage;
        const name = document.createElement('label');
        // Die Nummer ist die LAGE in der Liste, keine Aussage darüber, was
        // aussen liegt — das entscheidet die Simulation. Deshalb steht sie
        // nur als Ordnungszahl da und nicht als „Schicht".
        name.textContent = `${nummer + 1}. ${eintrag.titel}`;
        // Klick auf den Eintrag lädt ihn zum Ändern (Edgar, 20.09.2026:
        // „Wenn ich also auf einen der Jobs klicke, soll ich die
        // Einstellungen dazu ändern können") — der Stift daneben tut dasselbe.
        name.title = 'Anklicken: in den Reiter laden und ändern.\n'
            + GarmentcodeKombi._reglertext(eintrag);
        name.className = 'gc-kombi-name';
        name.addEventListener('click', () => this.bearbeiten(nummer));
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
        const stift = document.createElement('button');
        stift.className = 'btn-toggle hb-fest';
        stift.title = 'In den Reiter laden und ändern — „Übernehmen" schreibt '
            + 'den Eintrag dann an seine Stelle zurück';
        stift.innerHTML = '<i class="fas fa-pen"></i>';
        stift.addEventListener('click', () => this.bearbeiten(nummer));
        const weg = document.createElement('button');
        weg.className = 'btn-toggle hb-fest';
        weg.title = 'Aus der Kombination nehmen';
        weg.innerHTML = '<i class="fas fa-times"></i>';
        weg.addEventListener('click', () => this.entfernen(nummer));
        zeile.append(name, rechts, stift, weg);
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
