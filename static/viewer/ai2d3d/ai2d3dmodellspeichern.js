import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Ai2d3dmodellspeichern — „Als Modell speichern“ der Exportleiste auf der Jobseite von 2d-3d-AI (31.10.2026, Server `Ai2d3dmodell`; bis dahin gesperrt, „noch nicht gebaut“).
 *
 * Wie „Übernehmen und als Modell speichern“ auf Mesh3D-AI (`Mesh3daitestkleider.speichern`): Name aus dem Feld der Leiste, Start mit POST, danach alle 2 s der Stand des Prozesses, der die
 * Stücke aus den Fotos zu eigenen Genesis-Stücken macht (Minuten). Das Modell steht danach unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle“.
 */
export class Ai2d3dmodellspeichern {

    /** @param adresse `/api/2d3dai/<job>/figur/`; @param standardname Vorgabe für das leere Namensfeld */
    static binden(adresse, standardname) {
        const s = new Ai2d3dmodellspeichern(adresse);
        if (!s.name.value) s.name.value = standardname || '';
        s._standHolen();
        return s;
    }

    constructor(adresse) {
        this.adresse = `${adresse}modell/`;
        this.knopf = document.getElementById('exportleiste-modell-speichern');
        this.name = document.getElementById('exportleiste-modell-name');
        this.stand = document.getElementById('exportleiste-modell-meldung');
        this.knopf.addEventListener('click', () => this.speichern());
    }

    async speichern() {
        const name = this.name.value.trim();
        if (!name) {
            this.stand.textContent = 'Bitte einen Namen für das Modell eingeben.';
            return;
        }
        this.knopf.disabled = true;
        try {
            await Serverabruf.senden(this.adresse, { name });
        } catch (fehler) {
            this.stand.textContent = `Nicht gestartet: ${fehler.daten?.error || fehler.message}`;
            this.knopf.disabled = false;
            return;
        }
        this._standHolen();
    }

    async _standHolen() {
        clearTimeout(this._takt);
        try {
            const antwort = await fetch(this.adresse);
            const s = await antwort.json();
            if (!antwort.ok) throw new Error(s.error || `HTTP ${antwort.status}`);
            this.stand.textContent = {
                nie: 'Speichert die Figur aus den Fotos mit ihren Stücken als Genesis-Modell (Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle). Dauert einige Minuten.',
                laeuft: `Speichern läuft (${s.name}): ${s.meldung || ''}`,
                fertig: `${s.meldung} — unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle“.`,
                fehler: `Speichern gescheitert: ${s.fehler || s.meldung}`,
            }[s.status] ?? '';
            this.knopf.disabled = s.status === 'laeuft';
            if (s.status === 'laeuft') this._takt = setTimeout(() => this._standHolen(), 2000);
        } catch (fehler) {
            this.stand.textContent = `Stand nicht lesbar: ${fehler.message}`;
            this.knopf.disabled = true;
        }
    }
}
