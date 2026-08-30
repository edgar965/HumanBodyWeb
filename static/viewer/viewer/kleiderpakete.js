import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Auswahlfeld } from '../gemeinsam/auswahlfeld.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Kleiderliste } from './kleiderliste.js';
import { Kategoriewahl } from '../gemeinsam/kategoriewahl.js';

/**
 * Kleiderpakete — herunterladbare Kleidungspakete anbieten und installieren.
 *
 * Herausgelöst aus `garment_liste.js` (229 Zeilen). Nach dem Herunterladen wird
 * der Katalog NEU vom Server geholt: Das Paket bringt eigene Kategorien mit, und
 * die Auswahlliste oben zeigt sonst weiter die alten — die neuen Teile wären da,
 * aber nicht auffindbar.
 */
export class Kleiderpakete {

    static WAHL = 'garment-pack-select';
    static STATUS = 'garment-download-status';
    static KNOPF = 'garment-pack-download';
    static KATEGORIEWAHL = 'garment-category';

    /** Die verfügbaren Pakete in die Auswahlliste. */
    static async listeLaden() {
        const wahl = document.getElementById(Kleiderpakete.WAHL);
        if (!wahl) return;
        try {
            const daten = await Serverabruf.json(
                '/api/character/garment/download/available/');
            wahl.innerHTML = '';
            Auswahlfeld.fuellen(wahl, (daten.packs || []).map(
                (paket) => ({ wert: paket.name,
                              text: `${paket.label} (${paket.category})` })));
        } catch (fehler) {
            Protokoll.warnung('kleiderpakete', 'Pakete nicht ladbar', fehler);
        }
    }

    /** Das gewählte Paket installieren und den Katalog auffrischen. */
    static async herunterladen() {
        const wahl = document.getElementById(Kleiderpakete.WAHL);
        if (!wahl?.value) return;
        const knopf = document.getElementById(Kleiderpakete.KNOPF);
        if (knopf) knopf.disabled = true;
        Kleiderpakete._melden(`Lade ${wahl.value}...`);
        try {
            const daten = await Serverabruf.senden(
                '/api/character/garment/download/', { pack_name: wahl.value });
            if (daten.ok) {
                Kleiderpakete._melden(`${daten.count} Garments installiert!`);
                await Kleiderpakete.katalogAuffrischen();
            } else {
                Kleiderpakete._melden(`Fehler: ${daten.error || 'Unbekannt'}`);
            }
        } catch (fehler) {
            Protokoll.fehler('kleiderpakete', 'Herunterladen fehlgeschlagen', fehler);
            Kleiderpakete._melden(`Fehler: ${fehler.message}`);
        }
        if (knopf) knopf.disabled = false;
    }

    static async katalogAuffrischen() {
        const buecherei = await Serverabruf.json('/api/character/garment/library/');
        state._garmentCatalog = [];
        for (const kategorie of Object.keys(buecherei.garments || {})) {
            state._garmentCatalog.push(...buecherei.garments[kategorie]);
        }
        Kleiderpakete._kategorien(buecherei.categories);
        Kleiderliste.zeichnen();
    }

    /** Die Kategorieliste neu füllen — siehe `Kategoriewahl`. */
    static _kategorien(namen) {
        Kategoriewahl.fuellen(Kleiderpakete.KATEGORIEWAHL, namen);
    }

    static _melden(text) {
        const feld = document.getElementById(Kleiderpakete.STATUS);
        if (feld) feld.textContent = text;
    }
}
