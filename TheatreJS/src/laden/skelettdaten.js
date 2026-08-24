/**
 * Skelettdaten — Rigify-Skelett, Hautgewichte und Rig-Knochen vom Server.
 *
 * Herausgelöst aus `asset-loader.js` (318 Zeilen). Alle drei sind gross
 * (Gewichte mehrere MB) und ändern sich während einer Sitzung nicht, deshalb
 * werden sie beim ersten Zugriff geholt und dann gemerkt.
 *
 * Ein fehlgeschlagener Abruf wird NICHT gemerkt: Beim nächsten Mal versucht es
 * die Klasse erneut, statt dauerhaft `null` zu liefern.
 */
export class Skelettdaten {

    static QUELLEN = {
        rigify: '/api/character/rigify-skeleton/',
        gewichte: '/api/character/skin-weights/',
        rigknochen: '/api/character/rig/',
    };

    static _gemerkt = {};

    static async _holen(name) {
        if (!Skelettdaten._gemerkt[name]) {
            const antwort = await fetch(Skelettdaten.QUELLEN[name]);
            if (antwort.ok) Skelettdaten._gemerkt[name] = await antwort.json();
        }
        return Skelettdaten._gemerkt[name] || null;
    }

    static rigify() { return Skelettdaten._holen('rigify'); }
    static gewichte() { return Skelettdaten._holen('gewichte'); }
    static rigknochen() { return Skelettdaten._holen('rigknochen'); }
}
