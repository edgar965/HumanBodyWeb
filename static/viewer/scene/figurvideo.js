/**
 * Figurvideo — „Video" im Animations-Reiter, der Server-Weg.
 *
 * Sammelt, was der Server braucht — die gewählte Figur mit ihren Morphs und
 * allen gehäuteten Kleidungsstücken (`figurvideo_stuecke.js`), die laufende
 * Animation, Länge und Weichgewebe —, startet den Lauf und fragt den Stand
 * ab, bis das MP4 da ist.
 *
 * Der Browser-Weg (Aufzeichnen der Leinwand) steht in `videoaufnahme.js`;
 * beide teilen sich die Bedienelemente und diese Klasse verdrahtet sie.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _selectedInst } from './utils.js';
import { Figurvideostuecke } from './figurvideo_stuecke.js';
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
        // Der Regler wirkt LIVE auf die gewählte Figur — Weg 2. Der
        // Server-Weg liest denselben Wert beim Start.
        physik.addEventListener('input', () => {
            const inst = _selectedInst();
            if (inst?.isSkinned) Weichgewebe.setzen(inst, Number(physik.value));
        });
        sekunden.addEventListener('input', anzeigen);
        anzeigen();
        document.getElementById('figurvideo-server')
            ?.addEventListener('click', () => this.serverStarten());
        // Weg 2: die Szene selbst, Bild für Bild (`videoaufnahme.js`).
        // Teilt sich Balken, Meldung und Ergebnisfeld mit dem Server-Weg.
        this.aufnahme = new Videoaufnahme({
            zeigen: (text, anteil) => this.zeigen(text, anteil),
            melden: (text, fehler) => this.melden(text, fehler),
            fertig: (url, info) => this.browserFertig(url, info),
        });
        document.getElementById('figurvideo-browser')
            ?.addEventListener('click', () => this.aufnahme.starten());
    }

    /** Das MP4 des Browser-Wegs — kommt als Blob-Adresse, nicht vom Server. */
    browserFertig(url, info) {
        const ergebnis = document.getElementById('figurvideo-ergebnis');
        const video = document.getElementById('figurvideo-video');
        const laden = document.getElementById('figurvideo-laden');
        video.src = url;
        laden.href = url;
        laden.download = `figur_szene_${Date.now()}.mp4`;
        ergebnis.classList.remove('hb-versteckt');
        const bilanz = document.getElementById('figurvideo-bilanz');
        if (bilanz) {
            bilanz.textContent = `${info.bilder} Bilder · Weichgewebe ${info.mm} mm · aus der Szene`;
            bilanz.title = 'Aufgezeichnet aus der Szene, Bild für Bild, mit Kamera, '
                + 'Licht und Texturen wie hier zu sehen.';
        }
        this.zeigen('Fertig', 1);
        this.aufraeumen();
    }

    // ------------------------------------------------------------ Eingabe

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
            this.melden(`${starre.length} Kleidungsstück(e) hängen starr `
                + `(${starre.join(', ')}) und kommen nicht ins Video.`, false);
        }
        return {
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
            this.melden(daten.fehler, true);
            return;
        }
        this.zeigen('Start …', 0);
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
            this.melden(`Start fehlgeschlagen: ${fehler.message}`, true);
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
            this.melden(`Abgebrochen: ${stand.fehler.split('\n')[0]}`, true);
            this.aufraeumen();
            return;
        }
        this.zeigen(`${stand.phase} · ${Math.round(stand.sekunden || 0)} s`,
                    stand.anteil || 0);
        if (stand.fertig) {
            this.fertig(stand);
            this.aufraeumen();
        }
    }

    // ------------------------------------------------------------ Anzeige

    zeigen(text, anteil) {
        const kasten = document.getElementById('figurvideo-stand');
        kasten?.classList.remove('hb-versteckt');
        const balken = document.getElementById('figurvideo-anteil');
        if (balken) balken.style.width = `${Math.round(anteil * 100)}%`;
        const phase = document.getElementById('figurvideo-phase');
        if (phase) phase.textContent = text;
        Figurvideo._sperren(true);
    }

    static _sperren(zu) {
        for (const id of ['figurvideo-server', 'figurvideo-browser']) {
            const k = document.getElementById(id);
            if (k) k.disabled = zu;
        }
    }

    melden(text, fehler = false) {
        this.zeigen(text, 0);
        const phase = document.getElementById('figurvideo-phase');
        if (phase) phase.style.color = fehler ? 'var(--danger, #d44)' : '';
        if (fehler) Figurvideo._sperren(false);
    }

    /** Das MP4 einbetten, die Messwerte als Tooltip daneben. */
    fertig(stand) {
        const ergebnis = document.getElementById('figurvideo-ergebnis');
        const video = document.getElementById('figurvideo-video');
        const laden = document.getElementById('figurvideo-laden');
        // `?t=` an der DATENadresse, nicht an Statik: dieselbe Kennung
        // liefert nach einem zweiten Lauf ein anderes Video.
        const url = `${stand.video_url}?t=${Date.now()}`;
        video.src = url;
        laden.href = url;
        laden.download = `figur_${this.kennung}.mp4`;
        ergebnis.classList.remove('hb-versteckt');
        const bilanz = document.getElementById('figurvideo-bilanz');
        if (bilanz && stand.bilanz) {
            bilanz.textContent = Figurvideo.kurz(stand.bilanz);
            bilanz.title = Figurvideo.lang(stand.bilanz);
        }
        this.zeigen(`Fertig in ${Math.round(stand.sekunden || 0)} s`, 1);
    }

    static kurz(b) {
        const koerper = b.teile?.[0];
        const stuecke = (b.teile || []).slice(1);
        const teile = [`${b.bilder} Bilder`];
        if (koerper?.zuschlag_mm) teile.push(`Weichgewebe ${koerper.zuschlag_mm} mm`);
        // Die Stueckzahl IMMER, auch null: „nur Koerper" ist ein Befund,
        // den man sehen muss.
        teile.push(stuecke.length === 1 ? '1 Stück' : `${stuecke.length} Stücke`);
        return teile.join(' · ');
    }

    static lang(b) {
        const zeilen = [`Wurzelweg ${(b.wurzelweg_m || 0).toFixed(2)} m, `
            + `Quelle ${Math.round(b.quell_fps || 0)} fps, Zeitschritt ${b.schritt}`];
        for (const t of b.teile || []) {
            let z = `${t.name}: ${t.punkte} Punkte, Ruheprobe ${t.ruheprobe_mm} mm`;
            if (t.sitz_mm != null) z += `, Sitz ${t.sitz_mm} mm`;
            if (t.gleichlauf_mm) z += `, zur Haut ${t.gleichlauf_mm.join(' / ')} mm`;
            if (t.zuschlag_mm != null) z += `, Zuschlag ${t.zuschlag_mm} mm`;
            if (t.stoff_im_koerper_prozent != null) {
                z += `, im Körper ${t.stoff_im_koerper_prozent} %`;
            }
            zeilen.push(z);
        }
        return zeilen.join('\n');
    }

    aufraeumen() {
        if (this.uhr) clearInterval(this.uhr);
        this.uhr = null;
        this.kennung = null;
        Figurvideo._sperren(false);
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
