/**
 * Exportreiter — die Bedienung des Reiters „Export".
 *
 * Herausgelöst aus `main.js` (788 Zeilen). Vier kleine Regeln:
 *
 * * Der Güte-Regler (CRF) zeigt seinen Wert daneben an.
 * * „Eigene Auflösung" blendet zwei Zahlenfelder ein.
 * * Der Bereichsabschnitt gilt nur für den Server-Weg — der Browser-Weg nimmt
 *   auf, was er sieht, und kann keinen Ausschnitt rechnen.
 * * Beim Öffnen des Reiters werden Name und Dauer der laufenden Animation
 *   nachgetragen und die Endzeit vorbelegt, SOLANGE sie leer ist. Wer eine
 *   Endzeit eingetippt hat, will sie behalten.
 */
export class Exportreiter {

    static REITER = 'tab-export';

    /**
     * @param {Object} lauf { name(), dauer() }
     */
    constructor(lauf) {
        this.lauf = lauf;
    }

    verdrahten() {
        this._gueteregler();
        this._aufloesung();
        this._verfahren();
        this._reiterwechsel();
        return this;
    }

    _gueteregler() {
        const regler = document.getElementById('export-crf');
        const anzeige = document.getElementById('export-crf-val');
        if (!regler || !anzeige) return;
        regler.addEventListener('input',
                                () => { anzeige.textContent = regler.value; });
    }

    _aufloesung() {
        const wahl = document.getElementById('export-resolution');
        const eigene = document.getElementById('export-custom-res');
        if (!wahl || !eigene) return;
        wahl.addEventListener('change', () => {
            eigene.style.display = wahl.value === 'custom' ? 'flex' : 'none';
        });
    }

    _verfahren() {
        const wahl = document.getElementById('export-method');
        const bereich = document.getElementById('export-region-section');
        if (!wahl) return;
        wahl.addEventListener('change', () => {
            if (bereich) {
                bereich.style.display = wahl.value === 'server' ? '' : 'none';
            }
        });
    }

    _reiterwechsel() {
        document.querySelectorAll('.panel-tab').forEach(reiter => {
            reiter.addEventListener('click', () => {
                if (reiter.getAttribute('data-tab') === Exportreiter.REITER) {
                    this.angabenAuffrischen();
                }
            });
        });
    }

    angabenAuffrischen() {
        const name = document.getElementById('export-anim-name');
        if (name) name.textContent = this.lauf.name() || '—';
        const dauer = this.lauf.dauer();
        const anzeige = document.getElementById('export-anim-dur');
        if (anzeige) anzeige.textContent = dauer ? dauer.toFixed(1) : '—';
        const ende = document.getElementById('export-end');
        if (ende && (!ende.value || ende.value === '0') && dauer) {
            ende.value = dauer.toFixed(1);
        }
    }
}
