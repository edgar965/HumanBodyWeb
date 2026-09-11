import { Serverabruf } from './serverabruf.js';

/**
 * Figurkataloge — die Listen der fünf Figurarten, ohne Szene-Zustand.
 *
 * WARUM HIER (11.09.2026): Der Dialog „Charakter hinzufügen" der Szene-Seite
 * las seine Listen über `Umakatalog`, `Smplkatalog`, `Mhkatalog` und
 * `Umapythonkatalog` — jede dieser Klassen hängt an `scene/state.js`, und
 * damit an der Szene-Seite. Das Theatre sollte denselben Dialog bekommen
 * („mit dem gleichen Popup"), kann aber keinen Szene-Zustand importieren.
 * Hier stehen nur die Abrufe und die Zeilen, die daraus werden; wer die
 * gewählte Figur in seine Bühne stellt, sagt der Dialog selbst (`lader`).
 *
 * Jede Zeile hat `name` (Schlüssel für den Lader), `anzeige` und eine
 * `unterzeile` — die Texte sind die der Szene-Seite.
 */
export class Figurkataloge {

    /** Reihenfolge und Namen der Reiter nach Ansage (Edgar, 07.09.2026). */
    static REIHENFOLGE = ['modell', 'smpl', 'makehuman', 'uma', 'umapython'];

    static QUELLEN = {
        modell: { titel: 'HumanBody', adresse: '/api/character/models/',
                  leer: 'Keine Modelle vorhanden.', pflege: true },
        // SMPL-Referenzkörper von GarmentCode: Upstream-Dateien, deshalb
        // ohne Umbenennen und Löschen.
        smpl: { titel: 'SMPL', adresse: '/api/character/smpl-figur/',
                leer: 'Keine SMPL-Körper im GarmentCode-Klon.', pflege: false },
        // MakeHuman-Basiskörper: eine Datei des Projekts, ohne Pflege.
        makehuman: { titel: 'MakeHuman', adresse: '/api/character/mh-figur/',
                     leer: 'MakeHuman/base.obj fehlt.', pflege: false },
        uma: { titel: 'UMA', adresse: '/api/character/uma-figur/',
               leer: 'Keine UMA-Figur im Katalog (Figuren/uma/).', pflege: true },
        // UMAs Rassen, in Python gebaut — sie gehören dem Unity-Projekt.
        umapython: { titel: 'UMA Python', adresse: '/api/umapython/rassen/',
                     leer: 'Kein UMA-Katalog gefunden (UMA_PROJEKT).', pflege: false },
    };

    /** Die Zeilen einer Quelle: [{name, anzeige, unterzeile}]. */
    static async liste(quelle) {
        const angaben = Figurkataloge.QUELLEN[quelle];
        if (!angaben) throw new Error(`Unbekannte Figurart: ${quelle}`);
        const daten = await Serverabruf.json(angaben.adresse);
        return Figurkataloge.zeilen(quelle, daten);
    }

    /** Aus der Serverantwort die Zeilen — getrennt, damit es prüfbar ist. */
    static zeilen(quelle, daten) {
        const bau = Figurkataloge.ZEILEN[quelle];
        return bau ? bau(daten || {}) : [];
    }

    static ZEILEN = {
        modell: (daten) => (daten.presets || []).map(p => ({
            name: p.name, anzeige: p.label || p.name, unterzeile: '',
        })),
        uma: (daten) => (daten.figuren || []).map(f => ({
            name: f.name,
            anzeige: String(f.name).replace(/\.glb$/i, ''),
            unterzeile: `${f.geschlecht} · ${(f.bytes / 1048576).toFixed(1)} MB · ${f.stand}`,
        })),
        smpl: (daten) => (daten.figuren || []).map(f => ({
            name: f.name,
            anzeige: f.anzeige || f.name,
            unterzeile: `${f.geschlecht} · ${f.smpl ? 'SMPL' : 'GarmentCode-Modell'} · `
                + (f.masse_vorhanden ? 'Maße vorgegeben' : 'ohne Maße'),
        })),
        makehuman: (daten) => (daten.figuren || []).map(f => ({
            name: f.name,
            anzeige: f.anzeige || f.name,
            unterzeile: `${Number(f.punkte || 0).toLocaleString()} Punkte · `
                + `${(Number(f.hoehe || 0) * 100).toFixed(1)} cm · `
                + 'Kleidung sitzt ohne Nacharbeit',
        })),
        umapython: (daten) => (daten.rassen || []).map(name => ({
            name,
            anzeige: name,
            unterzeile: 'UMA-Rasse, in Python gebaut — ohne Unity',
        })),
    };
}
