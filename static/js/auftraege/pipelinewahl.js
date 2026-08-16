import { Pipelinevorgaben } from './pipelinevorgaben.js';

/**
 * Pipelinewahl — die Karten oben auf der Seite: welche Pipeline gewaehlt ist,
 * welcher Einstellungsblock sichtbar ist, welches Koerper-Backend der
 * Hybrid-Zweig nutzt, und die drei Qualitaetsknoepfe je Karte.
 *
 * Herausgeloest aus templates/upload_v4.html (Umbau 16.08.2026):
 * `updatePipelineCards`, `updateHybridBackend` und die 15 `onclick`-Attribute
 * der Qualitaetsknoepfe. Die Knoepfe haengen jetzt an `data-vorgabe`, damit
 * kein globaler Name im Fenster gebraucht wird — ein `onclick` findet aus einem
 * ES-Modul heraus nichts.
 */
export class Pipelinewahl {

    /** Der Hybrid-Zweig hat mehrere Backends; der Wert traegt sie als Suffix. */
    static HYBRID = 'hybrid';

    static aufbauen() {
        return new Pipelinewahl().aufbauen();
    }

    aufbauen() {
        document.querySelectorAll('input[name="pipeline"]').forEach(feld => {
            feld.addEventListener('change', () => this.kartenZeigen());
        });
        document.getElementById('hybridBodyBackend')
            ?.addEventListener('change', () => this.hybridBackend());
        document.querySelectorAll('[data-vorgabe]').forEach(knopf => {
            knopf.addEventListener('click', () => {
                const [pipeline, stufe] = knopf.dataset.vorgabe.split(':');
                Pipelinevorgaben.anwenden(pipeline, stufe,
                                          () => this.hybridBackend());
            });
        });
        this.kartenZeigen();
        this.hybridBackend();
        return this;
    }

    /** Name der gewaehlten Pipeline, z.B. 'v4' oder 'hybrid_gvhmr'. */
    gewaehlt() {
        return document.querySelector('input[name="pipeline"]:checked')?.value
               || '';
    }

    /** Gewaehlte Karte hervorheben, ihren Einstellungsblock einblenden. */
    kartenZeigen() {
        const wert = this.gewaehlt();
        const istHybrid = wert.startsWith(Pipelinewahl.HYBRID + '_');
        document.querySelectorAll('.pipeline-card').forEach(karte => {
            const name = karte.dataset.pipeline;
            const passt = (istHybrid && name === Pipelinewahl.HYBRID)
                          || name === wert;
            karte.classList.toggle('selected', passt);
            document.getElementById('settings-' + name)
                ?.classList.toggle('visible', passt);
        });
    }

    /**
     * Das Auswahlfeld "Koerper-Backend" bestimmt den Wert des Hybrid-Radios
     * (`hybrid_gvhmr` / `hybrid_prompthmr`) und welcher der beiden
     * Einstellungsbloecke sichtbar ist.
     */
    hybridBackend() {
        const feld = document.getElementById('hybridBodyBackend');
        if (!feld) return;
        const backend = feld.value;
        const radio = document.getElementById('hybridRadio');
        if (radio) radio.value = Pipelinewahl.HYBRID + '_' + backend;
        for (const name of ['gvhmr', 'prompthmr']) {
            document.getElementById(`hybrid-${name}-settings`)
                ?.classList.toggle('hb-versteckt', backend !== name);
        }
    }
}
