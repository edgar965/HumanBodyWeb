import { Modellexport } from '../charakter/modellexport.js';

/**
 * Meshfigurexport — die angepasste Figur als GLB (Rig, Textur, Augen, Wimpern) in die Ablage des
 * Auftrags unter `output/Export/MeshTo3D/<Name>_<Zeit>/` (Edgar: „Das Ergebnis dann hier").
 *
 * Derselbe Weg wie im Kontextmenü der Szene (`Modellexport`: der Browser schreibt die GLB, der
 * Server legt sie ab und macht daraus einen eigenen Unterordner) — mit der Figur der Bühne, auf
 * der die Kacheln aus dem Netz liegen; `Modellexport` wartet selbst, bis die Figur ganz gebaut ist.
 */
export class Meshfigurexport {

    constructor(seite) {
        this.seite = seite;
        this.knopf = document.getElementById('exportieren');
        this.meldung = document.getElementById('export-meldung');
        this.knopf?.addEventListener('click', () => this.exportieren());
    }

    zeigen(z) {
        if (!this.knopf) return;
        const bereit = !z.laeuft && Object.keys(z.stellung || {}).length > 0;
        this.knopf.disabled = !bereit || this._laeuft;
        this.knopf.title = bereit ? `Nach ${z.exportordner}` : 'Erst wenn die Figur fertig ist';
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
        this._laeuft = true;
        this.knopf.disabled = true;
        this._melden('Figur wird exportiert …');
        try {
            const ergebnis = await Modellexport.exportieren(modell, {
                formate: ['glb'], rig: true, textur: true, assets: true, animation: false, pose: 'ruhelage',
                aufloesung: 0, ordner: z.exportordner, name: z.name,
            });
            if (ergebnis.error) throw new Error(ergebnis.error);
            const dateien = (ergebnis.dateien || []).map(d => d.name).join(', ');
            this._melden(`Exportiert nach ${ergebnis.ordner}: ${dateien}`);
        } catch (fehler) {
            this._melden(`Export fehlgeschlagen: ${fehler.message}`, true);
        } finally {
            this._laeuft = false;
            this.zeigen(this.seite.zustand);
        }
    }
}
