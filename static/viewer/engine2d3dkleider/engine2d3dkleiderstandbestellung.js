import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderstandbestellung — die GLB des letzten Stands beim Server bestellen, wenn sie fehlt oder veraltet ist
 * (01.10.2026, `POST /api/engine2d3dkleider/<id>/standmodell/`, `Engine2d3dKleiderstandmodell`).
 *
 * Der Zustand meldet `standmodell: {datei, fassung, soll, aktuell, fehler?}`. Ist `aktuell` falsch und läuft kein Lauf
 * (der baut sie an seinem Ende selbst), geht EINE Bestellung je Stand (`soll`) hinaus; der Bau dauert in einem eigenen Prozess
 * 50–60 s (kalt, gemessen 05.10.2026; die Meldung „wird gebaut …" steht so lange), danach steht die neue Datei im Zustand und
 * `Engine2d3dKleiderbuehnenmodell` lädt sie. Bis dahin bleibt die alte Fassung stehen. Ist der Bau dieses Stands gescheitert
 * (`fehler`), wird nicht wieder bestellt. Seit 05.10.2026 bestellt die Bühne nur noch, wenn der Knopf „Modell" an ist (Standard aus).
 */
export class Engine2d3dKleiderstandbestellung {

    constructor(seite, melden) {
        this.seite = seite;
        this.melden = melden;
        this._bestellt = null;
        this._gemeldet = false;
    }

    /** Ersetzt ein Modell des Stands die Genesis-Figur — schon da, oder gleich gebaut? */
    static kommt(z) {
        const s = z.standmodell;
        return !!s && !s.fehler && (!!s.datei || !z.laeuft);
    }

    pruefen(z) {
        const s = z.standmodell;
        if (!s) return;
        if (s.fehler) {
            this._melden(s.datei ? '' : `Modell des letzten Stands nicht gebaut: ${s.fehler} — die Figur wird im Browser gebaut`);
            return;
        }
        if (s.aktuell) {
            this._melden('');
            return;
        }
        if (z.laeuft || this._bestellt === s.soll) return;
        this._bestellt = s.soll;
        this._bestellen(s);
    }

    /** Nur eigene Meldungen wieder wegnehmen — die Bühne meldet auch anderes. */
    _melden(text) {
        if (!text && !this._gemeldet) return;
        this._gemeldet = !!text;
        this.melden(text);
    }

    async _bestellen(s) {
        if (!s.datei) this._melden('Modell des letzten Stands wird gebaut …');
        try {
            // Die neue Datei bringt der nächste Zustand (die Seite fragt auch bei ruhendem Auftrag alle 6 s nach).
            await Serverabruf.senden(this.seite.adresse('standmodell/'), {});
        } catch (fehler) {
            this._bestellt = null;
            this._melden(`Modell des letzten Stands nicht bestellt: ${fehler.message}`);
        }
    }
}
