import { Auftragduplizieren } from '../gemeinsam/auftragduplizieren.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Zeilenwahl } from '../../js/auftraege/zeilenwahl.js';

/**
 * Blendermodellliste — die Seite „BlenderModel": die Tabelle der Aufträge (Duplizieren, Löschen).
 *
 * Das Formular „Neues Modell aus Fotos" (TRELLIS.2/Hunyuan3D → Netz → Genesis-9-Figur) ist am
 * 29.09.2026 wieder ausgebaut (Edgar: „mach das endlich weg aus der Hauptseite" — die Vorlagen
 * dieses Bereichs sind gemalte Illustrationen, keine Fotos; TRELLIS/Hunyuan3D liefern darauf
 * nachweislich kein brauchbares Netz, siehe `hilfe/2d-3d/`). Neue Aufträge entstehen bis auf
 * Weiteres über die Skripte in `ProjektTemp/kostuem/zauberer/` (Grundfigur + Blender-Kostüm).
 */
export class Blendermodellliste {

    static LOESCHEN = '/api/blendermodell/loeschen/';

    static aufbauen() {
        if (!document.getElementById('blendermodell-liste')) return null;
        const liste = new Blendermodellliste();
        liste.tabelleBinden();
        return liste;
    }

    // ----------------------------------------------------------- Tabelle

    tabelleBinden() {
        const tabelle = document.querySelector('#blendermodell-liste table');
        if (!tabelle) return;
        const knopf = document.getElementById('blendermodell-bulk-delete');
        const zaehler = document.getElementById('blendermodell-bulk-count');
        this.wahl = new Zeilenwahl(tabelle, anzahl => {
            if (knopf) knopf.disabled = anzahl === 0;
            if (zaehler) zaehler.textContent = String(anzahl);
            this.duplikat?.anzeigen(anzahl);
        });
        this.duplikat = new Auftragduplizieren('blendermodell', 'blendermodell-duplizieren',
            'blendermodell-duplizieren-count', this.wahl);
        this.wahl.binden();
        // Eigenes Kopfkästchen (`#blendermodell-select-all`): `Zeilenwahl` kennt nur `#select-all`, und die
        // anderen Bereiche haben eigene Kennungen, damit keine doppelte ID entsteht.
        document.getElementById('blendermodell-select-all')?.addEventListener('click', () => {
            const alle = this.wahl.kaesten();
            this.wahl.alleSetzen(!(alle.length > 0 && alle.every(k => k.checked)));
            this.wahl.nachziehen();
        });
        tabelle.addEventListener('click', e => {
            const zeile = e.target.closest('tr[data-id]');
            if (!zeile || e.target.closest('input, a, button, select')) return;
            const link = zeile.querySelector('a[href]');
            if (link) window.location.href = link.getAttribute('href');
        });
        knopf?.addEventListener('click', () => this.loeschen());
    }

    async loeschen() {
        const ids = this.wahl.kennungen();
        if (!ids.length) return;
        if (!window.confirm(`${ids.length} Auftrag/Aufträge löschen? Gespeicherte Modelle und die Ablage in BlenderModel bleiben.`)) return;
        try {
            const antwort = await Serverabruf.senden(Blendermodellliste.LOESCHEN, { ids });
            if (antwort.error) throw new Error(antwort.error);
            window.location.reload();
        } catch (fehler) {
            window.alert(`Löschen fehlgeschlagen: ${fehler.message}`);
        }
    }
}
