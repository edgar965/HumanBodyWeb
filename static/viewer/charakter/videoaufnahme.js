/**
 * Videoaufnahme — Weg 2: die Szene selbst wird zum Video, Bild für Bild.
 *
 * NICHT in Echtzeit mit `MediaRecorder`. Der Weichgewebe-Zuschlag kostet
 * je Bild rund 75 ms (70.851 Punkte, gemessen in Node), und ein Video, das
 * aufzeichnet, was gerade auf dem Schirm ist, bekäme dann jedes Bild
 * halbfertig oder gar nicht. Bild für Bild heißt: Animation auf die Zeit
 * setzen, Physik rechnen, rendern, Leinwand abgreifen — gleich, wie schnell
 * der Rechner ist. Dasselbe Verfahren wie `TheatreJS/src/studio/
 * bildexport.js`; kodiert wird am Server (ffmpeg, `Figurvideo.
 * aus_bildfolge`), und das MP4 liegt neben denen des Server-Wegs unter
 * `media/figurvideos/` — mit fester Adresse statt einer Blob-URL, die mit
 * dem Tab stirbt.
 *
 * ZWEI DURCHLÄUFE, wie beim Server-Weg (`kalibrierung.py`): Der erste
 * rechnet nur die Physik und misst den größten Zuschlag; daraus die
 * Stärke für den Millimeterwert des Reglers. Der zweite rendert. Ohne den
 * ersten müsste die Stärke geraten werden — und 700 mm statt 25 waren beim
 * Server-Weg das Ergebnis einer geratenen.
 */
import { state, THREE } from './state.js';
import { _selectedInst } from './utils.js';
import { Weichgewebe } from './weichgewebe.js';
import { Kamerafolge } from './kamerafolge.js';
import { Bodenstand } from './bodenstand.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Videoaufnahme {
    static FPS = 24;
    /** Bilder vor dem ersten, damit die Tempoglättung (0,75) eingeschwungen
     *  ist — nach zehn Bildern sind 94 % des Sprungs abgebaut. */
    static VORLAUF = 10;
    /** „Video erzeugen default": die ganze Animation von Anfang bis Ende, Kamera nach dem Häkchen „folgt der Figur". */
    static GANZ = 'ganz';
    /** „Video erzeugen": was hier im Browser läuft — ab der Abspielstelle bis zum Ende, mit der Kamera, wie Edgar sie von Hand stellt. */
    static SICHTBAR = 'sichtbar';

    constructor(anzeige) {
        // { zeigen(text, anteil), melden(text, fehler),
        //   fertig({url, pfad}, info), ablage() → {ablage, dateiname, figur, animation} }
        this.anzeige = anzeige;
        this.laeuft = false;
        this._abbruch = false;
        this._kodiert = false;
        this._arbeitsvektor = new THREE.Vector3();
    }

    /**
     * Knopf „Abbrechen" (Edgar, 08.10.2026): Die Aufnahme hört vor dem nächsten Bild auf, nichts geht an den
     * Server, die Wiedergabe steht wieder, wie sie war. Ab dem Senden (`_kodiert`) geht es nicht mehr — das ist
     * EINE Anfrage, die der Server zu Ende kodiert; der Knopf ist dann gesperrt (`anzeige.abbruchFrei`).
     */
    abbrechen() {
        if (this.laeuft && !this._kodiert) this._abbruch = true;
    }

    /** @param {string} modus  `Videoaufnahme.GANZ` oder `Videoaufnahme.SICHTBAR`. */
    async starten(modus = Videoaufnahme.GANZ) {
        if (this.laeuft) return;
        const inst = _selectedInst();
        if (!inst?.isSkinned) { this.anzeige.melden('Keine gehäutete Figur gewählt.', true); return; }
        if (!state.mixer || !state.currentAction) {
            this.anzeige.melden('Keine Animation geladen — erst eine aus der Liste starten.', true);
            return;
        }
        const mm = Number(document.getElementById('figurvideo-physik')?.value || 0);
        this.laeuft = true;
        this._abbruch = false;
        this._kodiert = false;
        const liefWeiter = state.playing;
        state.playing = false;
        // ZWEI KNÖPFE (Edgar, 08.10.2026: „mach einen zweiten Button: Video erzeugen default, der das
        // ganze Video der Animation erzeugt. Der Video erzeugen soll mir das erzeugen, was im Browser
        // läuft, mit der Kamera Einstellung die ich manuell mache"):
        // - GANZ: die ganze Animation, egal ob sie läuft oder nicht („der button Video erzeugen soll das
        //   ganze Video für diese animation erzeugen, egal ob sie läuft oder nicht!").
        // - SICHTBAR: ab der Abspielstelle bis zum Ende, Kamera unverändert.
        // Die Aufnahme setzt die Zeit selbst (`_zeit`) und hängt nicht an der Wiedergabe. Dafür muss sie
        // den Stand der Wiedergabe freigeben und danach zurückgeben:
        // - PAUSIERT: Eine pausierte Aktion rechnet mit Zeitmaß 0, `mixer.setTime(t)` stellt dann bei
        //   jedem t dieselbe Haltung (gemessen am Modell „Edgar", Dance1_smplx, Knochen l_upperarm:
        //   Quaternion bei t = 1, 2 und 3 s identisch; mit `paused = false` drei verschiedene). Das
        //   Video „Edgar.mp4" (DanceLang, 120 Bilder, mittlerer Unterschied zum ersten Bild 0,05 von
        //   255) zeigte darum keine Bewegung.
        // - TEMPO: `setTime(t)` rechnet mit `mixer.timeScale`; der Tempo-Regler verschöbe jede Zeit.
        // - ABSPIELSTELLE: danach steht die Animation wieder dort, wo der Nutzer sie hatte.
        const aktion = state.currentAction;
        const vorher = { pausiert: aktion.paused, tempo: state.mixer.timeScale, zeit: aktion.time };
        aktion.paused = false;
        state.mixer.timeScale = 1;
        try {
            const bilder = await this._aufnehmen(inst, mm, modus, vorher.zeit);
            if (!bilder) { this.anzeige.abgebrochen(); return; }
            this._kodiert = true;
            this.anzeige.zeigen('Sende an Server für ffmpeg …', 0.97);
            this.anzeige.abbruchFrei(false);
            const antwort = await this._kodieren(bilder, mm);
            this.anzeige.fertig(antwort, { bilder: bilder.length, mm });
        } catch (fehler) {
            this.anzeige.melden(`Aufnahme fehlgeschlagen: ${fehler.message}`, true);
        } finally {
            aktion.time = vorher.zeit;
            state.mixer.timeScale = vorher.tempo;
            state.mixer.update(0);
            aktion.paused = vorher.pausiert;
            this.laeuft = false;
            state.playing = liefWeiter;
        }
    }

    /**
     * Animation auf eine Zeit setzen — ohne Abspielen. Der Bodenfix gehört
     * dazu: Die Schleife stellt ihn nur bei Wiedergabe, hier steht sie.
     */
    _zeit(t) {
        state.mixer.setTime(t);
        state.mixer.update(0);
        if (state.currentAnimGroundFixed) Bodenstand.richten(state, this._arbeitsvektor);
    }

    async _aufnehmen(inst, mm, modus, abspielstelle) {
        const fps = Videoaufnahme.FPS, dt = 1 / fps;
        const clip = state.currentAction.getClip();
        // Ab dem Vorlauf, nicht ab null: Bild 0 des Retargets ist ein
        // STARTZUSTAND (T-Pose), kein Bewegungsbild — es stand als erstes
        // Bild im Video. Der Vorlauf läuft über die ersten Bilder und
        // schwingt dabei die Tempoglättung ein. Bis zum Ende des Clips.
        // GANZ: von vorn, unabhängig von der Abspielstelle. SICHTBAR: ab der
        // Abspielstelle; steht sie am Ende (keine zwei Bilder mehr), von vorn —
        // ein leeres Video hülfe niemandem.
        const anfang = Videoaufnahme.VORLAUF / fps;
        const ab = modus === Videoaufnahme.SICHTBAR ? Math.max(abspielstelle, anfang) : anfang;
        const von = clip.duration - ab >= 2 * dt ? ab : anfang;
        const dauer = Math.max(clip.duration - von, 0);
        const zahl = Math.round(dauer * fps);
        let staerke = 0;
        if (mm > 0 && Weichgewebe.vorbereiten(inst, mm)) {
            staerke = await this._kalibrieren(inst, mm, von, zahl, dt);
            if (this._abbruch) return null;
        }
        // Durchlauf 2: rendern.
        Weichgewebe.vorbereiten(inst, mm);
        const aufnahmen = [];
        const { renderer, scene, camera } = state;
        const canvas = renderer.domElement;
        // Gizmo und Knochenlinien gehören nicht ins Video.
        const verborgen = this._hilfenVerbergen();
        // „Kamera folgt": ab der Startstellung der Figur, nicht ab Bild 0 —
        // der Vorlauf läuft ohne Bild, die Kamera darf aber schon mit.
        this._zeit(von - Videoaufnahme.VORLAUF / fps);
        // SICHTBAR: die Kamera bleibt, wie Edgar sie von Hand eingestellt hat — ohne Nachführen.
        const folge = modus === Videoaufnahme.SICHTBAR ? null : this._kamerafolge(inst);
        try {
            for (let n = -Videoaufnahme.VORLAUF; n < zahl; n++) {
                if (this._abbruch) return null;
                const t = von + n / fps;
                this._zeit(t);
                if (mm > 0) Weichgewebe.bildErzwingen(inst, dt, staerke);
                folge?.nachfuehren();
                if (n < 0) continue;
                renderer.render(scene, camera);
                aufnahmen.push(await new Promise((ok) => canvas.toBlob(ok, 'image/png')));
                if (n % 6 === 0 || n === zahl - 1) {
                    this.anzeige.zeigen(`Bild ${n + 1} von ${zahl}`, 0.3 + 0.65 * (n + 1) / zahl);
                }
                // Der Oberfläche Luft lassen — sonst friert die Seite ein.
                await new Promise((weiter) => setTimeout(weiter, 0));
            }
        } finally {
            folge?.beenden();
            this._hilfenZeigen(verborgen);
        }
        return aufnahmen;
    }

    /** Die Kamerafolge, wenn das Häkchen gesetzt ist — sonst null. */
    _kamerafolge(inst) {
        if (!document.getElementById('figurvideo-kamera')?.checked) return null;
        return new Kamerafolge(inst, state.camera, state.controls).starten();
    }

    /** Gizmo, Knochenlinien, Hilfslinien ausblenden; gibt zurück, was an war. */
    _hilfenVerbergen() {
        const kandidaten = [state.transformControls, state.transformControls?.getHelper?.()];
        (state.scene?.children || []).forEach((o) => {
            if (o.isSkeletonHelper || o.name === 'gizmo' || o.userData?.hilfslinie) kandidaten.push(o);
        });
        const war = [];
        for (const o of kandidaten) {
            if (o && o.visible !== false) { war.push(o); o.visible = false; }
        }
        return war;
    }

    _hilfenZeigen(liste) { for (const o of liste) o.visible = true; }

    /** Durchlauf 1: nur Physik, größter Zuschlag bei Stärke 1 → Dreisatz. */
    async _kalibrieren(inst, mm, von, zahl, dt) {
        const fps = Videoaufnahme.FPS;
        let max = 0;
        // Jedes vierte Bild genügt: Der Ausschlag hängt an der schnellsten
        // Bewegung, und die dauert länger als vier Bilder.
        for (let n = -Videoaufnahme.VORLAUF; n < zahl; n++) {
            if (this._abbruch) return 0;
            this._zeit(von + n / fps);
            const g = Weichgewebe.bildErzwingen(inst, dt, 1.0);
            if (n >= 0 && n % 4 === 0) max = Math.max(max, g);
            if (n % 12 === 0) {
                const anteil = (n + Videoaufnahme.VORLAUF) / (zahl + Videoaufnahme.VORLAUF);
                this.anzeige.zeigen(`Kalibrierung ${Math.max(n, 0)} / ${zahl}`, 0.3 * anteil);
                await new Promise((weiter) => setTimeout(weiter, 0));
            }
        }
        if (max < 1e-9) return 0;
        return Math.min((mm / 1000) / max, 3.0);
    }

    /** Bilder an den Server, MP4 landet unter `media/figurvideos/` — wie
     *  der Server-Weg — und als Kopie in der gewählten Ablage. */
    async _kodieren(aufnahmen, mm) {
        const daten = new FormData();
        aufnahmen.forEach((bild, i) => daten.append('frames', bild, `${String(i).padStart(6, '0')}.png`));
        daten.append('fps', String(Videoaufnahme.FPS));
        daten.append('physik_mm', String(mm));
        for (const [name, wert] of Object.entries(this.anzeige.ablage?.() || {})) {
            daten.append(name, wert);
        }
        const ergebnis = await Serverabruf.formular('/api/animation/video/aufnahme/', daten);
        if (ergebnis.fehler) throw new Error(ergebnis.fehler);
        return { url: `${ergebnis.video_url}?t=${Date.now()}`, pfad: ergebnis.pfad };
    }
}
