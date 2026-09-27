import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Meshfigurspeicher — „Als Genesis-Figur speichern" auf der Auftragsseite „Mesh to 3D" (27.09.2026).
 *
 * Edgar: „mach eine Option zum Speichern der Genesis-Datei in unserem Format, damit die bei den
 * gespeicherten Genesis-Figuren vorkommt." Dasselbe Format wie „Modell speichern" der Szene
 * (`data/models/<Name>.json`, `quelle: genesis9`) — der Lauf legt es schon als „<Name> Mesh" an
 * (Option „Als Modell speichern"); hier unter einem frei gewählten Namen. Eine fremde Figur gleichen
 * Namens wird nie überschrieben, der Server lehnt ab (`Meshfigurspeichern.modell_speichern`).
 */
export class Meshfigurspeicher {

    constructor(seite) {
        this.seite = seite;
        this.name = document.getElementById('modell-name');
        this.knopf = document.getElementById('modell-speichern');
        this.meldung = document.getElementById('modell-meldung');
        this.knopf?.addEventListener('click', () => this.speichern());
    }

    zeigen(z) {
        if (!this.knopf) return;
        this.knopf.disabled = !!z.laeuft || !Object.keys(z.stellung || {}).length || this._laeuft;
        if (this.name && !this.name.value) this.name.value = z.modell || `${z.name} Mesh`;
    }

    _melden(text, fehler = false) {
        if (!this.meldung) return;
        this.meldung.textContent = text;
        this.meldung.classList.toggle('hb-schlecht', fehler);
    }

    async speichern() {
        const name = this.name?.value.trim();
        if (!name) { this._melden('Bitte einen Namen angeben', true); return; }
        this._laeuft = true;
        this.knopf.disabled = true;
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('modell/'), { name });
            if (antwort.error) throw new Error(antwort.error);
            this.seite.zustand.modell = antwort.modell;
            this._melden(`Gespeichert als „${antwort.modell}" — unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle".`);
        } catch (fehler) {
            this._melden(`Speichern fehlgeschlagen: ${fehler.message}`, true);
        } finally {
            this._laeuft = false;
            this.zeigen(this.seite.zustand);
        }
    }
}
