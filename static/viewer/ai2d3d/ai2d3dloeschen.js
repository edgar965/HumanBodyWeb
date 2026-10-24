/**
 * Ai2d3dloeschen — Auswahl und „Gewählte löschen“ auf `/2d-3d-AI/` (24.10.2026): `Mesh3dailoeschen` (Kästchen, Zähler, Klick in die Zelle) mit eigenem Endpunkt und eigenem Text.
 * `POST /api/2d3dai/loeschen/` (`Ai2d3dpapierkorb`): Tests werden nach `3DObjects/ai2d3d/_beiseite/<Zeit>_geloescht/` verschoben, Jobs (Exporte) nur ausgeblendet.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3dailoeschen } from '../mesh3dai/mesh3dailoeschen.js';

export class Ai2d3dloeschen extends Mesh3dailoeschen {
    static aufbauen() {
        return [...document.querySelectorAll('[data-loeschen]')].map(feld => new Ai2d3dloeschen(feld));
    }

    async loeschen() {
        const ids = this.gewaehlt();
        if (!ids.length) return;
        const jobs = this.art === 'jobs';
        const wie = jobs ? 'Die Exporte bleiben in 3DObjects/modelsExport (Quelle von Mesh3D-AI); 2d-3d-AI blendet sie aus (3DObjects/ai2d3d/_ausgeblendet.json).'
            : 'Die Ordner werden nach 3DObjects/ai2d3d/_beiseite/<Zeit>_geloescht/ verschoben (nicht endgültig gelöscht); die Fotos selbst bleiben, wo sie liegen.';
        if (!window.confirm(`${ids.length} ${jobs ? 'Jobs' : 'Tests'} löschen?\n\n${ids.join(', ')}\n\n${wie}`)) return;
        this.knopf.disabled = true;
        try {
            const antwort = await Serverabruf.senden('/api/2d3dai/loeschen/', { art: this.art, ids });
            const fehler = (antwort.ergebnis || []).filter(e => !e.ok);
            if (fehler.length) window.alert(`Nicht gelöscht:\n${fehler.map(e => `${e.kennung}: ${e.fehler}`).join('\n')}`);
        } catch (fehler) {
            window.alert(`Löschen fehlgeschlagen: ${fehler.message}`);
        }
        window.location.reload();
    }
}
