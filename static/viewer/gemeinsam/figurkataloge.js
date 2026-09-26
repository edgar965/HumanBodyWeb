import { Serverabruf } from './serverabruf.js';

/**
 * Figurkataloge — die Listen der sechs Figurarten, ohne Szene-Zustand.
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
    static REIHENFOLGE = ['modell', 'smpl', 'makehuman', 'uma', 'umapython',
                          'genesis9'];

    /**
     * Die zwei Bereiche je Reiter (Edgar, 17.09.2026: „mach zwei zugeklappte
     * Bereiche - die Standard Modelle …, zweiter bereich - die gespeicherten
     * Modelle"). Jede Zeile trägt `bereich`; `Figurwahldialog` sortiert sie
     * ein. Standard = was das Programm mitbringt (Körpertypen, Daz-Katalog,
     * SMPL-X/MakeHuman/UMA-Python-Kataloge); gespeichert = Dateien von der
     * Platte (`data/models/*.json` je `quelle`, die UMA-Figuren).
     */
    static BEREICHE = [['standard', 'Standard-Modelle'],
                       ['gespeichert', 'Gespeicherte Modelle']];

    static QUELLEN = {
        modell: { titel: 'HumanBody', adresse: '/api/character/models/',
                  leer: 'Keine Modelle vorhanden.', pflege: true },
        // GarmentCodes Referenzkörper und die SMPL-X-Durchschnitte (seit
        // 15.09.2026 SMPL-X: Kiefer, Augen, Finger) — Upstream- bzw. erzeugte
        // Dateien, deshalb ohne Umbenennen und Löschen.
        smpl: { titel: 'SMPL-X', adresse: '/api/character/smpl-figur/',
                leer: 'Keine SMPL-X-Körper (Modelldateien fehlen).', pflege: false },
        // MakeHuman-Basiskörper: eine Datei des Projekts, ohne Pflege.
        makehuman: { titel: 'MakeHuman', adresse: '/api/character/mh-figur/',
                     leer: 'MakeHuman/base.obj fehlt.', pflege: false },
        uma: { titel: 'UMA', adresse: '/api/character/uma-figur/',
               leer: 'Keine UMA-Figur im Katalog (Figuren/uma/).', pflege: true },
        // UMAs Rassen, in Python gebaut — sie gehören dem Unity-Projekt.
        umapython: { titel: 'UMA Python', adresse: '/api/umapython/rassen/',
                     leer: 'Kein UMA-Katalog gefunden (UMA_PROJEKT).', pflege: false },
        // Daz Genesis 9 (17.09.2026): Reglerstellungen mit Haut aus der
        // installierten Daz-Bibliothek — nichts davon im Repo. Pflege gibt es
        // trotzdem (20.09.2026), denn sie gilt nur für den Bereich „gespeichert"
        // (`Figurwahldialog._zeile`): ein gespeichertes Genesis-9-Modell ist eine
        // Datei `data/models/<name>.json` wie ein HumanBody-Modell, und Edgar
        // will sie aus dem Dialog löschen können.
        genesis9: { titel: 'Genesis 9', adresse: '/api/character/genesis9-figur/',
                    leer: 'Daz-Bibliothek mit Genesis 9 fehlt (Genesis9/HERKUNFT.md).',
                    pflege: true },
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
        // HumanBody: die 13 Körpertypen von MB-Lab als Standard, die
        // Modelldateien ohne fremde `quelle` als gespeichert — ein gespeichertes
        // Genesis-9-Modell steht NUR im Genesis-9-Reiter (17.09.2026).
        modell: (daten) => [
            ...(daten.koerpertypen || []).map(k => ({
                name: k.name, anzeige: k.anzeige || k.name,
                unterzeile: `${k.geschlecht} · Körpertyp (MB-Lab), ohne Morphs`,
                bereich: 'standard',
            })),
            ...(daten.presets || [])
                .filter(p => !p.quelle || p.quelle === 'modell')
                .map(p => ({
                    name: p.name, anzeige: p.label || p.name, unterzeile: '',
                    bereich: 'gespeichert',
                })),
        ],
        uma: (daten) => (daten.figuren || []).map(f => ({
            name: f.name,
            anzeige: String(f.name).replace(/\.glb$/i, ''),
            unterzeile: `${f.geschlecht} · ${(f.bytes / 1048576).toFixed(1)} MB · ${f.stand}`,
            bereich: 'gespeichert',
        })),
        // `gespeichert` (25.09.2026): eine ueber „Modell speichern" abgelegte
        // SMPL-X-Figur (eigener Name, Regler, Haut) steht im zweiten Bereich,
        // wie bei Genesis 9 — vorher zeigte dieser Reiter NUR den Katalog.
        smpl: (daten) => (daten.figuren || []).map(f => ({
            name: f.name,
            anzeige: f.anzeige || f.name,
            unterzeile: f.gespeichert
                ? `${f.geschlecht} · gespeicherte Figur`
                : `${f.geschlecht} · ${f.smpl ? 'SMPL-X' : 'GarmentCode-Modell'} · `
                    + (f.masse_vorhanden ? 'Maße vorgegeben' : 'ohne Maße'),
            bereich: f.gespeichert ? 'gespeichert' : 'standard',
            gespeichert: Boolean(f.gespeichert),
        })),
        makehuman: (daten) => (daten.figuren || []).map(f => ({
            name: f.name,
            anzeige: f.anzeige || f.name,
            unterzeile: `${Number(f.punkte || 0).toLocaleString()} Punkte · `
                + `${(Number(f.hoehe || 0) * 100).toFixed(1)} cm · `
                + 'Kleidung sitzt ohne Nacharbeit',
            bereich: 'standard',
        })),
        umapython: (daten) => (daten.rassen || []).map(name => ({
            name,
            anzeige: name,
            unterzeile: 'UMA-Rasse, in Python gebaut — ohne Unity',
            bereich: 'standard',
        })),
        genesis9: (daten) => (daten.figuren || []).map(f => ({
            name: f.name,
            anzeige: f.anzeige || f.name,
            unterzeile: f.gespeichert
                ? `gespeichert · ${Object.keys(f.regler || {}).length} Regler · `
                    + `${Object.keys(f.kleidung || {}).length} Stücke`
                : `${f.geschlecht} · `
                    + `${Number(daten.punkte?.punkte || 0).toLocaleString()} Punkte · `
                    + `${Object.keys(f.regler || {}).length} Regler gesetzt`,
            bereich: f.gespeichert ? 'gespeichert' : 'standard',
            gespeichert: Boolean(f.gespeichert),
        })),
    };
}
