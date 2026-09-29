import { Modellexport } from '../charakter/modellexport.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Meshfigurspeicher — „Modell speichern" auf der Auftragsseite (27.09.2026, Format-Auswahl 29.09.2026).
 *
 * Edgar: „mach eine Option zum Speichern der Genesis-Datei in unserem Format, damit die bei den
 * gespeicherten Genesis-Figuren vorkommt." Vorgabe „Eigenes Format" ist dasselbe wie „Modell
 * speichern" der Szene (`data/models/<Name>.json`, `quelle: genesis9`) — der Lauf legt es schon als
 * „<Name> Mesh" an (Option „Als Modell speichern"); hier unter einem frei gewählten Namen. Eine
 * fremde Figur gleichen Namens wird nie überschrieben, der Server lehnt ab
 * (`Meshfigurspeichern.modell_speichern`).
 *
 * Edgar (29.09.2026): „biete Optionen an für Modell als glb, blender, obj, eigenes Format" — GLB/
 * Blender/OBJ gehen denselben Weg wie „Figur als GLB exportieren" (`Meshfigurexport`,
 * `Modellexport.exportieren`), nur mit der hier gewählten Fassung statt fest `['glb']`.
 */
export class Meshfigurspeicher {

    constructor(seite) {
        this.seite = seite;
        this.format = document.getElementById('modell-format');
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
            const format = this.format?.value || 'genesis';
            if (format === 'genesis') await this._alsGenesisPreset(name);
            else await this._alsDatei(format, name);
        } catch (fehler) {
            this._melden(`Speichern fehlgeschlagen: ${fehler.message}`, true);
        } finally {
            this._laeuft = false;
            this.zeigen(this.seite.zustand);
        }
    }

    async _alsGenesisPreset(name) {
        const antwort = await Serverabruf.senden(this.seite.adresse('modell/'), { name });
        if (antwort.error) throw new Error(antwort.error);
        this.seite.zustand.modell = antwort.modell;
        this._melden(`Gespeichert als „${antwort.modell}" — unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle".`);
    }

    async _alsDatei(format, name) {
        const modell = this.seite.buehne?.modell;
        if (!modell) { this._melden('Die Figur ist noch nicht gebaut.', true); return; }
        const z = this.seite.zustand;
        const ergebnis = await Modellexport.exportieren(modell, {
            formate: [format], rig: true, textur: true, assets: true, animation: false, pose: 'ruhelage',
            ordner: z.exportordner, name,
        });
        if (ergebnis.error) throw new Error(ergebnis.error);
        const dateien = (ergebnis.dateien || [])
            .map(d => `${d.name}${d.bytes ? ` (${(d.bytes / 1048576).toFixed(1)} MB)` : ''}`).join(', ');
        this._melden(`Exportiert nach ${ergebnis.ordner}: ${dateien}`);
    }
}
