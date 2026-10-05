/**
 * Engine2d3dKleiderNachbesserungKi — die Auswahl der KI im Block „Nachbesserungen" (05.10.2026).
 *
 * Edgar: „Füge ein als Combo, welche KI genommen wird. Erstmal Lokal – Remote. Remote: Claude Sonnet und die (kostenlose) Nemotron, daneben die Stufen
 * (gering bis extra high). Für lokale KI: Qwen 3.8." Drei Auswahlfelder — KI (Lokal | Remote), Modell (je Ort) und Stufe (nur bei Modellen, die Stufen kennen) —
 * und ein Hinweis zum gewählten Modell (wohin Prompt und Bilder gehen). Der Katalog kommt vom Server (`GET …/nachbesserung/` → `ki`, aus `Agentenwahl`);
 * hier steht keine Modellliste. Gesendet wird `{ort, modell, stufe}`, geprüft wird auf dem Server.
 */
export class Engine2d3dKleiderNachbesserungKi {

    constructor() {
        const $ = id => document.getElementById(id);
        this.ort = $('nachbesserung-ort');
        this.modell = $('nachbesserung-modell');
        this.stufe = $('nachbesserung-stufe');
        this.stufeFeld = $('nachbesserung-stufe-feld');
        this.hinweis = $('nachbesserung-ki-hinweis');
        this.katalog = null;
        this.ort?.addEventListener('change', () => this.modelleFuellen());
        this.modell?.addEventListener('change', () => this.stufenZeigen());
    }

    static optionen(feld, liste) {
        feld.replaceChildren(...liste.map(e => {
            const option = document.createElement('option');
            option.value = e.wert;
            option.textContent = e.text;
            return option;
        }));
    }

    /** Den Katalog einsetzen — nur beim ersten Mal (was der Nutzer danach wählt, bleibt über die Abfragen des Blocks hinweg). */
    laden(katalog) {
        if (this.katalog || !katalog || !this.ort) return;
        this.katalog = katalog;
        Engine2d3dKleiderNachbesserungKi.optionen(this.ort, katalog.orte);
        Engine2d3dKleiderNachbesserungKi.optionen(this.stufe, katalog.stufen);
        const vorgabe = katalog.vorgabe || {};
        this.ort.value = vorgabe.ort || katalog.orte[0].wert;
        this.modelleFuellen(vorgabe.modell);
        this.stufe.value = vorgabe.stufe || katalog.stufen[0].wert;
    }

    modelleFuellen(gewuenscht) {
        const passend = this.katalog.modelle.filter(m => m.ort === this.ort.value);
        Engine2d3dKleiderNachbesserungKi.optionen(this.modell, passend);
        if (gewuenscht && passend.some(m => m.wert === gewuenscht)) this.modell.value = gewuenscht;
        this.stufenZeigen();
    }

    /** Die Stufe nur zeigen, wenn das Modell sie kennt; der Hinweis nennt, wohin Prompt und Bilder gehen. */
    stufenZeigen() {
        const eintrag = this.katalog?.modelle.find(m => m.wert === this.modell.value && m.ort === this.ort.value);
        this.stufeFeld.hidden = !eintrag?.stufen;
        this.hinweis.textContent = eintrag?.hinweis || '';
    }

    sperren(gesperrt) {
        for (const feld of [this.ort, this.modell, this.stufe]) if (feld) feld.disabled = gesperrt;
    }

    /** Die Wahl für den Server; `stufe` nur, wenn das Modell sie kennt. */
    wahl() {
        if (!this.katalog) return null;
        const eintrag = this.katalog.modelle.find(m => m.wert === this.modell.value);
        return { ort: this.ort.value, modell: this.modell.value, stufe: eintrag?.stufen ? this.stufe.value : null };
    }
}
