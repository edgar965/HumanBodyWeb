/**
 * Fotogenesisloeschen — Auswahl und „Gewählte löschen“ auf `/foto-genesis/` (24.10.2026): `Meshgenesisloeschen` (Kästchen, Zähler, Klick in die Zelle) mit eigenem Endpunkt und eigenem Text.
 * `POST /api/fotogenesis/loeschen/` (`Fotogenesispapierkorb`): Tests werden nach `3DObjects/fotogenesis/_beiseite/<Zeit>_geloescht/` verschoben, Jobs (Exporte) nur ausgeblendet.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshgenesisloeschen } from '../meshgenesis/meshgenesisloeschen.js';

export class Fotogenesisloeschen extends Meshgenesisloeschen {
    static aufbauen() {
        return [...document.querySelectorAll('[data-loeschen]')].map(feld => new Fotogenesisloeschen(feld));
    }

    async loeschen() {
        const ids = this.gewaehlt();
        if (!ids.length) return;
        const jobs = this.art === 'jobs';
        const wie = jobs ? 'Die Exporte bleiben in 3DObjects/modelsExport (Quelle von Mesh-Genesis); Foto-Genesis blendet sie aus (3DObjects/fotogenesis/_ausgeblendet.json).'
            : 'Die Ordner werden nach 3DObjects/fotogenesis/_beiseite/<Zeit>_geloescht/ verschoben (nicht endgültig gelöscht); die Fotos selbst bleiben, wo sie liegen.';
        if (!window.confirm(`${ids.length} ${jobs ? 'Jobs' : 'Tests'} löschen?\n\n${ids.join(', ')}\n\n${wie}`)) return;
        this.knopf.disabled = true;
        try {
            const antwort = await Serverabruf.senden('/api/fotogenesis/loeschen/', { art: this.art, ids });
            const fehler = (antwort.ergebnis || []).filter(e => !e.ok);
            if (fehler.length) window.alert(`Nicht gelöscht:\n${fehler.map(e => `${e.kennung}: ${e.fehler}`).join('\n')}`);
        } catch (fehler) {
            window.alert(`Löschen fehlgeschlagen: ${fehler.message}`);
        }
        window.location.reload();
    }
}
