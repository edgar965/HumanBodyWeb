import { Engine2d3dKleiderlaufzeit } from './engine2d3dkleiderlaufzeit.js';

/**
 * Engine2d3dKleiderlaufanzeige — die sichtbare Anzeige „läuft" in der Zeile des Render-Laufs, der gerade rechnet (04.10.2026).
 *
 * Edgar: „mach eine sichtbare UI wenn ein Render lauf läuft, in der Zeile wo der läuft". Ein Block aus drehendem Symbol, Text (Prozent, Schritt, vergangene Zeit,
 * Warteschlange) und einem Balken. Der Block wird einmal gebaut (`block`); der Zustand kommt im Takt, `zeigen(render)` schreibt nur Text und Balkenbreite um,
 * ohne die Tabelle neu zu bauen.
 */
export class Engine2d3dKleiderLaufanzeige {

    constructor() {
        this.block = document.createElement('div');
        this.block.className = 'engine2d3dkleider-laeuft-anzeige';
        const kopf = document.createElement('div');
        kopf.className = 'engine2d3dkleider-laeuft-kopf';
        const symbol = document.createElement('i');
        symbol.className = 'fas fa-spinner fa-spin';
        this.text = document.createElement('span');
        kopf.append(symbol, this.text);
        const balken = document.createElement('div');
        balken.className = 'engine2d3dkleider-laeuft-balken';
        this.fuellung = document.createElement('div');
        balken.appendChild(this.fuellung);
        this.block.append(kopf, balken);
    }

    /** @param r der Render-Stand (`render` im Zustand): `fortschritt` 0…1, `schritt`, `start` (Sekunden seit 1970), `wartend` (Läufe danach) */
    zeigen(r) {
        const prozent = Math.round((Number(r.fortschritt) || 0) * 100);
        const vergangen = r.start ? Math.round(Date.now() / 1000 - r.start) : 0;
        const teile = [`läuft · ${prozent} %`, r.schritt, vergangen > 0 ? Engine2d3dKleiderlaufzeit.dauer(vergangen) : '', r.wartend ? `danach noch ${r.wartend}` : ''];
        this.text.textContent = teile.filter(Boolean).join(' · ');
        this.fuellung.style.width = `${prozent}%`;
    }
}
