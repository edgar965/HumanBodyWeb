import { Serverabruf } from '/static/djangobase/js/serverabruf.js';

/**
 * Alle übrigen Stellschrauben der Drapierung — aufklappbar unter „Bauen".
 *
 * AUFTRAG (Edgar, 09.09.2026): „mach alle an den Regler bzw. Regler für die
 * es noch keine gibt. mach die in einem aufklappbaren Bereich unter Bauen".
 *
 * DIE FELDER KOMMEN VOM SERVER (`Simulationsfelder`), nicht aus dieser Datei:
 * Es sind 42, und stünden sie hier zusätzlich, liefen die beiden Listen beim
 * ersten Vergessen auseinander. Hier steht nur, wie sie aussehen.
 *
 * GESCHICKT WIRD NUR, WAS ABWEICHT. Ein Auftrag mit allen 42 Werten
 * überschriebe auch die, die niemand angefasst hat — und verdeckte damit
 * jede spätere Änderung an den Vorgaben der Simulation.
 *
 * ZUGEKLAPPT BEIM START: Der Bereich ist ein Werkzeugkasten, kein Formular.
 * Wer ihn braucht, klappt ihn auf; wer baut, sieht die Bauknöpfe.
 */
export class GarmentcodeSimulation {

    static ADRESSE = '/api/garmentcode/simulationsregler/';

    /** Vorsilbe der Formularfelder — der Server erwartet genau diese. */
    static VORSILBE = 'sim_';

    /** {schluessel: vorgabe} — zum Vergleich beim Abschicken. */
    static vorgaben = {};

    static async laden() {
        const ziel = document.getElementById('gc-simulation');
        if (!ziel) return 0;
        let antwort;
        try {
            antwort = await Serverabruf.json(GarmentcodeSimulation.ADRESSE);
        } catch (fehler) {
            ziel.innerHTML = '<div class="hb-hinweis">Simulationsregler nicht '
                + `abrufbar: ${fehler.message || fehler}</div>`;
            return 0;
        }
        return GarmentcodeSimulation._zeichnen(ziel, antwort);
    }

    static _zeichnen(ziel, antwort) {
        const gruppen = antwort.gruppen || [];
        ziel.innerHTML = '';
        if (!gruppen.length) return 0;
        const kasten = document.createElement('details');
        const kopf = document.createElement('summary');
        kopf.textContent = `Simulation (${antwort.anzahl} Regler)`;
        kopf.title = 'Alle übrigen Stellschrauben der Stoffsimulation. Sie '
            + 'wirken beim nächsten Bau mit 3D. Was auf der Vorgabe steht, '
            + 'wird nicht mitgeschickt.';
        kasten.appendChild(kopf);
        for (const gruppe of gruppen) {
            kasten.appendChild(GarmentcodeSimulation._gruppe(gruppe));
        }
        kasten.appendChild(GarmentcodeSimulation._zuruecksetzen());
        ziel.appendChild(kasten);
        return antwort.anzahl;
    }

    static _gruppe(gruppe) {
        const block = document.createElement('div');
        const kopf = document.createElement('div');
        kopf.className = 'hb-font-size-0-72rem hb-abstand-oben';
        kopf.textContent = gruppe.titel;
        block.appendChild(kopf);
        for (const feld of gruppe.felder) {
            GarmentcodeSimulation.vorgaben[feld.schluessel] = feld.vorgabe;
            block.appendChild(feld.schalter
                ? GarmentcodeSimulation._schalter(feld)
                : GarmentcodeSimulation._regler(feld));
        }
        return block;
    }

    /** Eine Reglerzeile wie `_schieberegler.html` sie baut. */
    static _regler(feld) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.title = feld.hinweis || '';
        const name = document.createElement('label');
        name.textContent = feld.titel;
        const schieber = document.createElement('input');
        schieber.type = 'range';
        schieber.id = GarmentcodeSimulation.VORSILBE + feld.schluessel;
        schieber.min = feld.min;
        schieber.max = feld.max;
        schieber.step = feld.schritt;
        schieber.value = feld.vorgabe;
        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        anzeige.id = `${schieber.id}-val`;
        const nachziehen = () => {
            anzeige.textContent = GarmentcodeSimulation._text(schieber.value,
                                                              feld);
        };
        schieber.addEventListener('input', nachziehen);
        nachziehen();
        zeile.append(name, schieber, anzeige);
        return zeile;
    }

    static _schalter(feld) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.title = feld.hinweis || '';
        const name = document.createElement('label');
        name.textContent = feld.titel;
        const kasten = document.createElement('input');
        kasten.type = 'checkbox';
        kasten.id = GarmentcodeSimulation.VORSILBE + feld.schluessel;
        kasten.checked = Boolean(feld.vorgabe);
        zeile.append(name, kasten);
        return zeile;
    }

    /**
     * Alles zurück auf die Vorgaben.
     *
     * Bei 42 Reglern führt sonst der einzige Weg zurück über das Neuladen
     * der Seite — und das wirft auch den gebauten Stand weg.
     */
    static _zuruecksetzen() {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn-toggle hb-abstand-oben';
        knopf.textContent = 'Alle auf Vorgabe zurück';
        knopf.addEventListener('click', () => {
            for (const [schluessel, vorgabe]
                 of Object.entries(GarmentcodeSimulation.vorgaben)) {
                const feld = document.getElementById(
                    GarmentcodeSimulation.VORSILBE + schluessel);
                if (!feld) continue;
                if (feld.type === 'checkbox') feld.checked = Boolean(vorgabe);
                else feld.value = vorgabe;
                feld.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
        return knopf;
    }

    /** Nur die abweichenden Werte an die Drapieranfrage hängen. */
    static anhaengen(daten) {
        if (!daten || typeof daten.append !== 'function') return 0;
        let gesetzt = 0;
        for (const [schluessel, vorgabe]
             of Object.entries(GarmentcodeSimulation.vorgaben)) {
            const feld = document.getElementById(
                GarmentcodeSimulation.VORSILBE + schluessel);
            if (!feld) continue;
            const ist = feld.type === 'checkbox' ? feld.checked
                : parseFloat(feld.value);
            if (ist === vorgabe) continue;
            daten.append(GarmentcodeSimulation.VORSILBE + schluessel,
                         feld.type === 'checkbox' ? String(ist) : feld.value);
            gesetzt += 1;
        }
        return gesetzt;
    }

    /** Wie viele Regler stehen anders als vorgesehen? Für die Meldung. */
    static abweichend() {
        const attrappe = [];
        GarmentcodeSimulation.anhaengen({ append: () => attrappe.push(1) });
        return attrappe.length;
    }

    static _text(wert, feld) {
        const zahl = parseFloat(wert);
        if (!Number.isFinite(zahl)) return String(wert);
        // Die Nachkommastellen aus dem Schritt: Ein Schritt von 0,01 ohne
        // zwei Stellen zeigte jede Bewegung als dieselbe Zahl.
        const stellen = String(feld.schritt).includes('.')
            ? String(feld.schritt).split('.')[1].length : 0;
        return zahl.toFixed(stellen).replace('.', ',');
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded',
                              () => GarmentcodeSimulation.laden());
} else {
    GarmentcodeSimulation.laden();
}
