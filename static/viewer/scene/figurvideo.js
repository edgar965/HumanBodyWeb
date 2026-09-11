/**
 * Figurvideo — „Video" im Animations-Reiter.
 *
 * EIN Knopf, „Video erzeugen". Wo gerechnet wird, sagt die Auswahl
 * `figurvideo-weg`: „in dieser Szene" zeichnet die Leinwand Bild für Bild
 * auf (`videoaufnahme.js`), „auf dem Server" schickt Figur, Kleider und
 * Animation nach Python (`core/dienste/figurvideo.py`) und fragt den Stand
 * ab, bis das MP4 da ist. Balken, Meldung und Ergebnis teilen sich beide
 * (`figurvideo_anzeige.js`).
 *
 * Die Kleidung geht als Binärpaket mit (`figurvideo_stuecke.js`), das
 * fertige Video wird in den gewählten Ordner kopiert (`figurvideoablage.py`).
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _selectedInst } from './utils.js';
import { Figurvideostuecke } from './figurvideo_stuecke.js';
import { Figurvideoanzeige as Anzeige } from './figurvideo_anzeige.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Weichgewebe } from './weichgewebe.js';
import { Videoaufnahme } from './videoaufnahme.js';

export class Figurvideo {
    /** Abstand der Standabfragen. Der Lauf dauert Minuten; jede Sekunde
     *  zu fragen brächte nichts als Log-Zeilen. */
    static ABFRAGE_MS = 2000;

    constructor() {
        this.kennung = null;
        this.uhr = null;
    }

    /** Elemente verdrahten — einmal, beim Aufbau des Reiters. */
    einrichten() {
        const physik = document.getElementById('figurvideo-physik');
        const sekunden = document.getElementById('figurvideo-sekunden');
        if (!physik || !sekunden) return;
        const anzeigen = () => {
            document.getElementById('figurvideo-physik-wert').textContent =
                `${physik.value} mm`;
            document.getElementById('figurvideo-sekunden-wert').textContent =
                `${sekunden.value} s`;
        };
        physik.addEventListener('input', anzeigen);
        // Der Regler wirkt LIVE auf die gewählte Figur. Der Server-Weg
        // liest denselben Wert beim Start.
        physik.addEventListener('input', () => {
            const inst = _selectedInst();
            if (inst?.isSkinned) Weichgewebe.setzen(inst, Number(physik.value));
        });
        sekunden.addEventListener('input', anzeigen);
        anzeigen();
        const weg = document.getElementById('figurvideo-weg');
        weg?.addEventListener('change', () => Anzeige.hinweisZeigen(weg.value));
        Anzeige.hinweisZeigen(weg?.value || 'szene');
        this.ablageVorgabe();
        this.aufnahme = new Videoaufnahme({
            zeigen: (text, anteil) => Anzeige.zeigen(text, anteil),
            melden: (text, fehler) => Anzeige.melden(text, fehler),
            fertig: (antwort, info) => this.browserFertig(antwort, info),
            ablage: () => this.ablage(),
        });
        document.getElementById('figurvideo-start')
            ?.addEventListener('click', () => this.starten());
        document.getElementById('figurvideo-abspielen')
            ?.addEventListener('click', () => Anzeige.abspielen());
        document.getElementById('figurvideo-pfad')
            ?.addEventListener('click', () => Anzeige.pfadKopieren());
    }

    /** Der Vorgabeordner steht als Platzhalter im Feld — so sieht man,
     *  wohin ein Video geht, wenn man nichts einträgt. */
    async ablageVorgabe() {
        const feld = document.getElementById('figurvideo-ablage');
        if (!feld) return;
        try {
            const antwort = await Serverabruf.json('/api/animation/video/ablage/');
            if (antwort.ordner) feld.placeholder = antwort.ordner;
        } catch (fehler) {
            Protokoll.warnen?.(`Figurvideo: Vorgabeordner nicht lesbar (${fehler.message})`);
        }
    }

    /** Je nach Auswahl: die Szene selbst oder der Server. */
    starten() {
        const weg = document.getElementById('figurvideo-weg')?.value || 'szene';
        if (weg === 'server') this.serverStarten();
        else this.aufnahme.starten();
    }

    // ------------------------------------------------------------ Eingabe

    /** Ordner, Dateiname, Figur und Animation — für die Kopie des Videos. */
    ablage() {
        const inst = _selectedInst();
        return {
            ablage: document.getElementById('figurvideo-ablage')?.value.trim() || '',
            dateiname: document.getElementById('figurvideo-datei')?.value.trim() || '',
            figur: inst?.presetName || inst?.id || '',
            animation: Figurvideo.animationsname(state.currentAnimUrl),
        };
    }

    /** `/api/character/bvh/Walk/136_28/` → `Walk_136_28`. */
    static animationsname(url) {
        const teile = String(url || '').split('/').filter(Boolean);
        return teile.slice(-2).join('_');
    }

    /** Was der Server braucht, aus der Szene gelesen — oder ein Grund. */
    anfrage() {
        const inst = _selectedInst();
        if (!inst) return { fehler: 'Keine Figur gewählt.' };
        if (inst.quelle && inst.quelle !== 'humanbody') {
            return { fehler: `Der Server-Weg gilt für HumanBody-Figuren; `
                + `diese kommt von ${inst.quelle}.` };
        }
        if (!state.currentAnimUrl) {
            return { fehler: 'Keine Animation gewählt — erst eine aus der '
                + 'Liste starten.' };
        }
        // ALLE gehäuteten Stücke gehen mit, so wie sie in der Szene hängen.
        // Was starr hängt (kein Skelett, keine Gewichte), bewegt sich auch
        // hier nicht — das wird gesagt, statt dass die Figur still ohne
        // dieses Stück ankommt.
        const { stuecke, starre } = Figurvideostuecke.sammeln(inst);
        if (starre.length) {
            Anzeige.melden(`${starre.length} Kleidungsstück(e) hängen starr `
                + `(${starre.join(', ')}) und kommen nicht ins Video.`, false);
        }
        return {
            ...this.ablage(),
            body_type: inst.bodyType,
            morphs: inst.morphs || {},
            stuecke,
            bvh_url: state.currentAnimUrl,
            // Ab HIER: wo die Animation in der Szene gerade steht. Bild 0
            // ist ein Startzustand, und `136_28` läuft erst nach zwei
            // Sekunden Einlaufen — wer das Video ab null startet, sieht
            // erst eine stehende Figur.
            ab_sekunden: state.mixer ? state.mixer.time : 0,
            sekunden: Number(document.getElementById('figurvideo-sekunden').value),
            physik_mm: Number(document.getElementById('figurvideo-physik').value),
        };
    }

    // ------------------------------------------------------------- Server

    async serverStarten() {
        if (this.kennung) return;             // ein Lauf zur Zeit
        const daten = this.anfrage();
        if (daten.fehler) {
            Anzeige.melden(daten.fehler, true);
            return;
        }
        Anzeige.zeigen('Start …', 0);
        try {
            // Als Formular (Auftrag als JSON, je Stück ein Binärpaket), über
            // `Serverabruf.formular` — das schickt das CSRF-Token mit. Ohne
            // das antwortet Django 403 als HTML-Seite, und die Fehlermeldung
            // lautet „Unexpected token '<'" — das sagt nichts ueber die
            // Ursache.
            const { stuecke, ...auftrag } = daten;
            const ergebnis = await Serverabruf.formular(
                '/api/animation/video/',
                Figurvideostuecke.formular(auftrag, stuecke,
                                           state.skinWeightData?.bone_names || []));
            if (ergebnis.fehler) throw new Error(ergebnis.fehler);
            this.kennung = ergebnis.kennung;
            this.uhr = setInterval(() => this.abfragen(), Figurvideo.ABFRAGE_MS);
        } catch (fehler) {
            Anzeige.melden(`Start fehlgeschlagen: ${fehler.message}`, true);
            this.aufraeumen();
        }
    }

    async abfragen() {
        if (!this.kennung) return;
        let stand;
        try {
            stand = await Serverabruf.json(
                `/api/animation/video/${this.kennung}/`, { cache: 'no-store' });
        } catch (fehler) {
            // Ein einzelner Aussetzer ist kein Abbruch — der Server kann
            // gerade neu starten. Beim nächsten Tick wieder versuchen.
            Protokoll.warnen?.(`Figurvideo: Stand nicht lesbar (${fehler.message})`);
            return;
        }
        if (stand.fehler) {
            Anzeige.melden(`Abgebrochen: ${stand.fehler.split('\n')[0]}`, true);
            this.aufraeumen();
            return;
        }
        Anzeige.zeigen(`${stand.phase} · ${Math.round(stand.sekunden || 0)} s`,
                       stand.anteil || 0);
        if (stand.fertig) {
            this.serverFertig(stand);
            this.aufraeumen();
        }
    }

    // ----------------------------------------------------------- Ergebnis

    serverFertig(stand) {
        // `?t=` an der DATENadresse, nicht an Statik: dieselbe Kennung
        // liefert nach einem zweiten Lauf ein anderes Video.
        const url = `${stand.video_url}?t=${Date.now()}`;
        Anzeige.ergebnis({
            url, download: `figur_${this.kennung}.mp4`,
            pfad: stand.pfad, ablageFehler: stand.ablage_fehler,
            kurz: stand.bilanz ? Anzeige.kurz(stand.bilanz) : '',
            lang: stand.bilanz ? Anzeige.lang(stand.bilanz) : '',
        });
        Anzeige.zeigen(`Fertig in ${Math.round(stand.sekunden || 0)} s`, 1);
    }

    /** Der Szenen-Weg: das MP4 liegt schon unter `media/figurvideos/`. */
    browserFertig(antwort, info) {
        Anzeige.ergebnis({
            url: antwort.url, download: `figur_szene_${Date.now()}.mp4`,
            pfad: antwort.pfad,
            kurz: `${info.bilder} Bilder · Weichgewebe ${info.mm} mm · aus der Szene`,
            lang: 'Aufgezeichnet aus der Szene, Bild für Bild, mit Kamera, '
                + 'Licht und Texturen wie hier zu sehen.',
        });
        Anzeige.zeigen('Fertig', 1);
        this.aufraeumen();
    }

    aufraeumen() {
        if (this.uhr) clearInterval(this.uhr);
        this.uhr = null;
        this.kennung = null;
        Anzeige.sperren(false);
    }
}

/** Beim Aufbau des Animations-Reiters (`Reiterinhalt.AUFBAUTEN`). */
export function initFigurvideo() {
    if (!fn._figurvideo) {
        fn._figurvideo = new Figurvideo();
        fn._figurvideo.einrichten();
    }
    return fn._figurvideo;
}
fn.initFigurvideo = initFigurvideo;
