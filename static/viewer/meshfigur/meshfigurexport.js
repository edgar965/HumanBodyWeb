import { Modellexport } from '../charakter/modellexport.js';

/**
 * Meshfigurexport — die angepasste Figur als GLB (Rig, Textur, Augen, Wimpern) in die Ablage des
 * Auftrags unter `output/Export/MeshTo3D/<Name>_<Zeit>/` (Edgar: „Das Ergebnis dann hier").
 *
 * Derselbe Weg wie im Kontextmenü der Szene (`Modellexport`: der Browser schreibt die GLB, der
 * Server legt sie ab und macht daraus einen eigenen Unterordner, bei gleichem Namen `_2`) — mit der
 * Figur der Bühne, auf der die Kacheln aus dem Netz liegen; `Modellexport` wartet selbst, bis die
 * Figur ganz gebaut ist.
 *
 * Optionen (Edgar, 27.09.2026: „mach Optionen für unterschiedlichen GLB-Export"): Texturauflösung
 * (Original = die Daz-Bilder, bis 35 MB je PNG; 2048/1024/512 px), mit/ohne Textur, mit/ohne Rig.
 * Der Dateiname trägt die Fassung (`Damira_2048_ohneRig`) — zwei Fassungen liegen nie unter
 * demselben Namen, solange der Name nicht von Hand gesetzt wird.
 */
export class Meshfigurexport {

    constructor(seite) {
        this.seite = seite;
        this.knopf = document.getElementById('exportieren');
        this.meldung = document.getElementById('export-meldung');
        this.aufloesung = document.getElementById('export-aufloesung');
        this.textur = document.getElementById('export-textur');
        this.rig = document.getElementById('export-rig');
        this.name = document.getElementById('export-name');
        this._handname = false;
        this.knopf?.addEventListener('click', () => this.exportieren());
        for (const feld of [this.aufloesung, this.textur, this.rig]) {
            feld?.addEventListener('change', () => this.nameVorschlagen());
        }
        this.name?.addEventListener('input', () => { this._handname = !!this.name.value.trim(); });
    }

    optionen() {
        return {
            aufloesung: Number(this.aufloesung?.value || 0),
            textur: this.textur ? this.textur.checked : true,
            rig: this.rig ? this.rig.checked : true,
        };
    }

    /** `<Name>[_<px>][_ohneTextur][_ohneRig]` — die Fassung im Namen. */
    static fassungsname(name, o) {
        const teile = [name || 'figur'];
        if (o.textur && o.aufloesung) teile.push(String(o.aufloesung));
        if (!o.textur) teile.push('ohneTextur');
        if (!o.rig) teile.push('ohneRig');
        return teile.join('_');
    }

    nameVorschlagen() {
        if (this.aufloesung) this.aufloesung.disabled = !this.textur?.checked;
        if (!this.name || this._handname) return;
        this.name.value = Meshfigurexport.fassungsname((this.seite.zustand || {}).name, this.optionen());
    }

    zeigen(z) {
        if (!this.knopf) return;
        const bereit = !z.laeuft && Object.keys(z.stellung || {}).length > 0;
        this.knopf.disabled = !bereit || this._laeuft;
        this.knopf.title = bereit ? `Nach ${z.exportordner}` : 'Erst wenn die Figur fertig ist';
        if (this.name && !this.name.value) this.nameVorschlagen();
    }

    _melden(text, fehler = false) {
        if (!this.meldung) return;
        this.meldung.textContent = text;
        this.meldung.classList.toggle('hb-schlecht', fehler);
    }

    async exportieren() {
        const modell = this.seite.buehne?.modell;
        const z = this.seite.zustand;
        if (!modell) { this._melden('Die Figur ist noch nicht gebaut.', true); return; }
        const o = this.optionen();
        const name = this.name?.value.trim() || Meshfigurexport.fassungsname(z.name, o);
        this._laeuft = true;
        this.knopf.disabled = true;
        this._melden(`Figur wird exportiert (${name}) …`);
        try {
            const ergebnis = await Modellexport.exportieren(modell, {
                formate: ['glb'], rig: o.rig, textur: o.textur, assets: true, animation: false, pose: 'ruhelage',
                aufloesung: o.aufloesung, ordner: z.exportordner, name,
            });
            if (ergebnis.error) throw new Error(ergebnis.error);
            const dateien = (ergebnis.dateien || [])
                .map(d => `${d.name}${d.bytes ? ` (${(d.bytes / 1048576).toFixed(1)} MB)` : ''}`).join(', ');
            this._melden(`Exportiert nach ${ergebnis.ordner}: ${dateien}`);
        } catch (fehler) {
            this._melden(`Export fehlgeschlagen: ${fehler.message}`, true);
        } finally {
            this._laeuft = false;
            this.zeigen(this.seite.zustand);
        }
    }
}
