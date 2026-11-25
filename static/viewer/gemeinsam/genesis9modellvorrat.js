import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { Genesis9vorrat } from './genesis9vorrat.js';
import { Genesis9materialabruf } from './genesis9materialabruf.js';

/**
 * Genesis9modellvorrat — die Anzeigen eines eben GESPEICHERTEN Modells vorab auf dem Server ablegen lassen, auch wenn es auf dieser Seite gar nicht steht (24.11.2026).
 *
 * Edgar, 19.10.2026: „bei jedem Modell, das gespeichert ist, direkt alles speichern für alle Anzeigen“ und 24.11.2026: „EdgarNeu laden im Charakter dauert ewig, das muss in 2 s laden“.
 * Der Charakter füllt nach „Modell speichern“ und nach dem Laden (`Genesis9vorrat.fuellen`); „Als Modell speichern“ der Exportleiste (Mesh-/Foto-Genesis, 2D3D Kleider) schrieb das Modell
 * in einem eigenen Prozess, und die erste Ladung im Charakter rechnete alles neu (gemessen: erstes Bild 2,8 s, fein 7,8 s statt 0,9/0,9 s aus dem Vorrat). Hier entstehen dieselben
 * Anfragen, die der Charakter beim Laden stellt — dieselben Klassen (`Genesis9materialabruf.nutzlast`, `Genesis9kleidung.anfrage`), ohne ein Netz zu bauen.
 */
export class Genesis9modellvorrat {

    /** Fein zuerst: damit lädt der Charakter (`Genesis9aufbau.progressiv`), der Käfig ist dann nur noch der Ersatz nach einer Code-Änderung. */
    static REIHENFOLGE = ['fein', 'grob', 'ultrafein'];

    /** Alle Stufen bis zur Einstellung für das gespeicherte Modell `name`. Gibt die Zahl der abgelegten Anzeigen; ein anderes als ein Genesis-Modell: 0. */
    static async fuellen(name) {
        if (!name || Genesis9vorrat.wahl === 'aus') return 0;
        const t0 = performance.now(), daten = await Serverabruf.json(`/api/character/model/${encodeURIComponent(name)}/`);
        if (daten?.quelle !== 'genesis9' || !daten.figur?.regler) return 0;
        const anzeigen = await Genesis9modellvorrat.anzeigen(name, daten.figur);
        let n = 0;
        for (const stufe of Genesis9modellvorrat.REIHENFOLGE) {
            if (Genesis9vorrat.STUFEN.indexOf(stufe) > Genesis9vorrat.STUFEN.indexOf(Genesis9vorrat.wahl)) continue;
            // je Stufe alle zugleich: verlässt Edgar die Seite, rechnet der Server die schon gestellten zu Ende
            n += (await Promise.all(anzeigen.map(([teil, anfrage]) => Genesis9vorrat.ablegen(anfrage, stufe, teil)))).filter(Boolean).length;
        }
        Protokoll.info('Genesis9modellvorrat', `${name}: ${n} Anzeigen vorab abgelegt (${Math.round(performance.now() - t0)} ms)`);
        return n;
    }

    /** `[[teil, {adresse, nutzlast, stellung}], …]` — die Anfragen, die das Laden dieser Figur stellt. */
    static async anzeigen(name, figur) {
        const [{ Genesis9Modell }, { Genesis9kleidung }] = await Promise.all([import('./genesis9modell.js'), import('./genesis9kleidung.js')]);
        const inst = new Genesis9Modell(`vorrat_${name}`, figur), aus = [];
        const eintragen = (teil, adresse, nutzlast) => aus.push([teil, { adresse, nutzlast, stellung: Genesis9vorrat.stellung(adresse, nutzlast) }]);
        eintragen('koerper', `${Genesis9Modell.ADRESSE}${encodeURIComponent(inst.figur)}/netz/`, Genesis9materialabruf.nutzlast(inst));
        for (const kennung of inst.getragen()) eintragen(`kleid:${kennung}`, ...Genesis9kleidung.anfrage(inst, kennung, inst.kleidung[kennung], 0));
        return aus;
    }
}
