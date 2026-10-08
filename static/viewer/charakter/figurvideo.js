/**
 * Figurvideo — „Video" im Animations-Reiter.
 *
 * ZWEI Knöpfe (Edgar, 08.10.2026):
 * - „Video erzeugen": was hier im Browser läuft, ab der Abspielstelle, mit der
 *   Kamera, wie sie von Hand steht — immer die Szene (`videoaufnahme.js`).
 * - „Video erzeugen default": die ganze Animation. Wo gerechnet wird, sagt die
 *   Auswahl `figurvideo-weg`: „in dieser Szene" zeichnet die Leinwand Bild für
 *   Bild auf (`videoaufnahme.js`), „auf dem Server" schickt Figur, Kleider und
 *   Animation nach Python (`core/dienste/figurvideo.py`) und fragt den Stand
 *   ab, bis das MP4 da ist.
 * Balken, Meldung und Ergebnis teilen sich beide (`figurvideo_anzeige.js`).
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
        if (!physik) return;
        const anzeigen = () => {
            document.getElementById('figurvideo-physik-wert').textContent =
                `${physik.value} mm`;
        };
        physik.addEventListener('input', anzeigen);
        // Der Regler wirkt LIVE auf die gewählte Figur. Der Server-Weg
        // liest denselben Wert beim Start.
        physik.addEventListener('input', () => {
            const inst = _selectedInst();
            if (inst?.isSkinned) Weichgewebe.setzen(inst, Number(physik.value));
        });
        anzeigen();
        const weg = document.getElementById('figurvideo-weg');
        weg?.addEventListener('change', () => Anzeige.hinweisZeigen(weg.value));
        Anzeige.hinweisZeigen(weg?.value || 'szene');
        this.ablageVorgabe();
        document.getElementById('figurvideo-ablage')
            ?.addEventListener('change', () => this.ablageAufteilen());
        this.aufnahme = new Videoaufnahme({
            zeigen: (text, anteil) => Anzeige.zeigen(text, anteil),
            melden: (text, fehler) => Anzeige.melden(text, fehler),
            fertig: (antwort, info) => this.browserFertig(antwort, info),
            ablage: () => this.ablage(),
            abgebrochen: () => Anzeige.abgebrochen(),
            abbruchFrei: (frei) => Anzeige.abbruchFrei(frei),
        });
        document.getElementById('figurvideo-abbrechen')
            ?.addEventListener('click', () => this.abbrechen());
        document.getElementById('figurvideo-start')
            ?.addEventListener('click', () => this.starten());
        document.getElementById('figurvideo-start-ganz')
            ?.addEventListener('click', () => this.ganzStarten());
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

    /** „Video erzeugen": was im Browser läuft, mit der Kamera von Hand — immer die Szene selbst, der Server hat seine eigene Kamera. */
    starten() {
        this.aufnahme.starten(Videoaufnahme.SICHTBAR);
    }

    /** „Video erzeugen default": die ganze Animation; je nach Auswahl die Szene selbst oder der Server. */
    ganzStarten() {
        const weg = document.getElementById('figurvideo-weg')?.value || 'szene';
        if (weg === 'server') this.serverStarten();
        else this.aufnahme.starten(Videoaufnahme.GANZ);
    }

    /**
     * Knopf „Abbrechen" (Edgar, 08.10.2026): bricht den laufenden Lauf ab und beendet den Job. Szene: die
     * Aufnahme hört auf (`Videoaufnahme.abbrechen`). Server: der Unterprozess wird beendet
     * (`POST …/<kennung>/abbrechen/`), erst danach hört die Abfrage auf — schlägt der Abbruch fehl, läuft der
     * Job noch, und der Balken muss weiter laufen.
     */
    async abbrechen() {
        if (this.aufnahme.laeuft) { this.aufnahme.abbrechen(); return; }
        if (!this.kennung) return;
        const kennung = this.kennung;
        Anzeige.abbruchFrei(false);
        try {
            const antwort = await Serverabruf.senden(`/api/animation/video/${kennung}/abbrechen/`, {});
            if (antwort.fehler) throw new Error(antwort.fehler);
            if (!antwort.abgebrochen) { Anzeige.melden(antwort.grund, false); return; }
            this.aufraeumen();
            Anzeige.abgebrochen();
        } catch (fehler) {
            Anzeige.melden(`Abbrechen fehlgeschlagen: ${fehler.message}`, false);
            Anzeige.abbruchFrei(true);
        }
    }

    // ------------------------------------------------------------ Eingabe

    /** Ordner, Dateiname, Figur und Animation — für die Kopie des Videos. */
    ablage() {
        const inst = _selectedInst();
        const geteilt = Figurvideo.pfadTeilen(document.getElementById('figurvideo-ablage')?.value);
        return {
            ablage: geteilt.ordner,
            dateiname: document.getElementById('figurvideo-datei')?.value.trim() || geteilt.datei,
            figur: inst?.presetName || inst?.id || '',
            animation: Figurvideo.animationsname(state.currentAnimUrl),
        };
    }

    /**
     * Ein GANZER Pfad im Feld „Ablage" (Edgar, 08.10.2026: „den Pfad des Verzeichnisses und den
     * Dateinamen kopieren können in dem Feld Ablage"): `A:\Videos\Edgar.mp4` → Ordner `A:\Videos`,
     * Datei `Edgar.mp4`. Ohne diese Trennung hätte der Server `Edgar.mp4` als ORDNER angelegt.
     * Als Datei gilt nur, was auf `.mp4` endet — ein Ordner `A:\Videos\v1.2` bleibt ein Ordner.
     */
    static pfadTeilen(text) {
        const roh = String(text || '').trim().replace(/^"|"$/g, '').trim();
        const treffer = /^(.*)[\\/]([^\\/]+\.mp4)$/i.exec(roh);
        if (!treffer) return { ordner: roh, datei: '' };
        const ordner = /^[A-Za-z]:$/.test(treffer[1]) ? `${treffer[1]}\\` : treffer[1];   // `A:\Edgar.mp4` → `A:\`
        return { ordner, datei: treffer[2] };
    }

    /** Nach dem Einfügen eines ganzen Pfads: Ordner im Feld „Ablage", Name im Feld „Datei" — sichtbar, nicht nur beim Start. */
    ablageAufteilen() {
        const feld = document.getElementById('figurvideo-ablage');
        const datei = document.getElementById('figurvideo-datei');
        if (!feld || !datei) return;
        const geteilt = Figurvideo.pfadTeilen(feld.value);
        if (!geteilt.datei) return;
        feld.value = geteilt.ordner;
        datei.value = geteilt.datei;
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
            meta: inst.meta || {},
            // Farben, Hauttextur und Braue der Figur — der Film baut daraus
            // Haut, Augen, Wimpern und Lippen (`ModelPhysik/filmhaut.py`).
            details: inst.details || {},
            stuecke,
            bvh_url: state.currentAnimUrl,
            // Die GANZE Animation (Edgar, 08.10.2026), gleich wo sie in der
            // Szene gerade steht — wie beim Szenen-Weg (`Videoaufnahme`): ab
            // dem Vorlauf (Bild 0 ist ein Startzustand) bis zum Ende des
            // Clips; der Server kappt bei `HOECHSTE_SEKUNDEN`.
            ab_sekunden: Videoaufnahme.VORLAUF / Videoaufnahme.FPS,
            sekunden: state.currentAction
                ? Math.max(state.currentAction.getClip().duration - Videoaufnahme.VORLAUF / Videoaufnahme.FPS, 1)
                : 5,
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
        Anzeige.abbruchFrei(false);               // noch keine Kennung — der Start lädt die Kleidung hoch
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
            Anzeige.abbruchFrei(true);            // erst jetzt gibt es einen Job, den man abbrechen kann
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
