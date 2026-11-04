import { Knopfsanduhr } from '../gemeinsam/knopfsanduhr.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Exportleisteaufloesung } from './exportleisteaufloesung.js';
import { Exportleistefigur } from './exportleistefigur.js';

/**
 * Exportleisteexport — der Block „Exportieren" der Exportleiste (31.10.2026): GLB, OBJ, Blender; mit oder ohne Animation (BVH-Pfad) und Audio (Pfad); Ordner und Dateiname vorbelegt.
 *
 * Edgar: „export als glb, obj, blend mit Checkbox mit oder ohne Animation", „bitte auch pfad für den Export vorbelegen". Ordner = Vorgabe des Bereichs (`zustand.exportordner`),
 * Dateiname = Name des Modells, BVH = Vorschlag der Seite (Standardanimation), Audio = Tonspur des jüngsten Studio-Projekts — jeweils einmal vorbelegt, danach gehören die Felder dem Nutzer.
 * Haken und Audio-Pfad merkt sich der Browser (`MERKEN`). GLB und Blender: Der Browser schickt die Figur als GLB, der Server baut Animation und Blender ein (`Exportleiste.exportieren`);
 * OBJ: ganz im Browser (`Exportleistefigur.obj`), ohne Animation.
 */
export class Exportleisteexport {

    static MERKEN = 'exportleiste.';
    static ORDNERSUCHE = '/api/character/modellexport/ordnersuche/';

    constructor(leiste) {
        this.leiste = leiste;
        const $ = id => leiste.wurzel.querySelector(`#${id}`);
        this.animation = $('exportleiste-animation');
        this.bvh = $('exportleiste-bvh');
        this.audio = $('exportleiste-audio');
        this.audioPfad = $('exportleiste-audio-pfad');
        this.ordner = $('exportleiste-ordner');
        this.suchen = $('exportleiste-suchen');
        this.name = $('exportleiste-name');
        this.meldung = $('exportleiste-export-meldung');
        this.knoepfe = [...leiste.wurzel.querySelectorAll('[data-format]')];
        this.mp4Groesse = new Exportleisteaufloesung($('exportleiste-mp4-groesse'), $('exportleiste-mp4-breite'), $('exportleiste-mp4-hoehe'));
        this.mp4Physik = $('exportleiste-mp4-physik');
        this._hand = { bvh: false, ordner: false, name: false, audio: false };
        this._laeuft = false;
        this.animation.checked = this._gemerkt('animation') !== '0';
        this.audio.checked = this._gemerkt('audio') === '1';
        for (const [feld, art] of [[this.bvh, 'bvh'], [this.ordner, 'ordner'], [this.name, 'name'], [this.audioPfad, 'audio']]) {
            feld.addEventListener('input', () => { this._hand[art] = !!feld.value.trim(); });
        }
        this.bvh.addEventListener('change', () => leiste.laden());
        for (const feld of [this.animation, this.audio, this.audioPfad]) feld.addEventListener('change', () => this._merken());
        this.suchen.addEventListener('click', () => this._ordnerSuchen());
        for (const knopf of this.knoepfe) knopf.addEventListener('click', () => this.exportieren(knopf.dataset.format));
    }

    _gemerkt(art) {
        try { return localStorage.getItem(Exportleisteexport.MERKEN + art); } catch { return null; }
    }

    _merken() {
        try {
            localStorage.setItem(`${Exportleisteexport.MERKEN}animation`, this.animation.checked ? '1' : '0');
            localStorage.setItem(`${Exportleisteexport.MERKEN}audio`, this.audio.checked ? '1' : '0');
            if (this._hand.audio) localStorage.setItem(`${Exportleisteexport.MERKEN}audiopfad`, this.audioPfad.value.trim());
        } catch { /* stumm gewollt: ohne Speicher gilt die Wahl nur in dieser Sitzung */ }
    }

    /** Der BVH-Wert für den Zustand: nur was der Nutzer selbst eingetragen hat (sonst fragt die Leiste mit dem Vorschlag der Seite). */
    bvhWert() {
        return this._hand.bvh ? this.bvh.value.trim() : '';
    }

    /** Die Seite hat eine andere Standardanimation: Das Feld folgt, solange es nicht von Hand geändert wurde. */
    vorschlagGeaendert() {
        if (!this._hand.bvh) this.bvh.value = '';
    }

    zeigen(z) {
        if (z.bvh?.pfad && !this._hand.bvh) this.bvh.value = z.bvh.pfad;
        this.bvh.title = z.bvh?.fehler || (z.bvh ? `${z.bvh.bilder} Bilder, ${z.bvh.sekunden} s` : 'Keine BVH');
        if (!this._hand.ordner && !this.ordner.value) this.ordner.value = z.exportordner || '';
        if (!this._hand.name && !this.name.value) this.name.value = z.name || '';
        if (!this._hand.audio && !this.audioPfad.value) this.audioPfad.value = this._gemerkt('audiopfad') || z.ton_vorgabe || '';
        // `sperre`: der Bereich rechnet gerade (2D3D Kleider) — GLB und Blender kommen vom Server und warten; OBJ schreibt die Seite selbst
        // Sanduhr (Edgar 31.10.2026): am Knopf des laufenden Exports, und an „MP4“, solange SEIN Video rechnet; startete „Rendern“ das Video, ist „MP4“ nur gesperrt (eine Karte, ein Video
        // nach dem anderen — 01.11.2026, Edgar: „warum sind zwei Sanduhren am laufen? ich habe nur den Render button geklickt“)
        const rechnet = z.render?.status === 'laeuft' ? z.render.quelle || 'rendern' : null;
        for (const knopf of this.knoepfe) {
            const f = knopf.dataset.format;
            const video = f === 'mp4' && rechnet === 'mp4';
            const an = (this._laeuft && f === this._format) || video;
            Knopfsanduhr.setzen(knopf, an, video ? 'Video rechnet …' : '', this._laeuft || (f === 'mp4' && (!z.render?.moeglich || !!rechnet)) || (!!z.sperre && f !== 'obj'));
            knopf.dataset.titel ??= knopf.title;
            if (z.sperre && f !== 'obj') knopf.title = z.sperre;
            else if (f === 'mp4') knopf.title = rechnet === 'rendern' ? 'Ein Video aus dem Block „Rendern“ rechnet gerade — ein Video nach dem anderen' : knopf.dataset.titel;
        }
    }

    /** MP4: die ganze BVH als Video in Ordner und Namen dieses Blocks (`<Name>_<BVH>.mp4`), gerechnet wie „Rendern" (`Exportleisterender.mp4`). */
    async _mp4() {
        if (!this.animation.checked || !this.bvh.value.trim()) { this.melden('MP4 braucht eine Animation: Haken „Mit Animation“ und eine BVH-Datei.', true); return; }
        const stamm = this.bvh.value.trim().split(/[\\/]/).pop().replace(/\.bvh$/i, '');
        const ordner = this.ordner.value.trim();
        const datei = `${this.name.value.trim() || 'figur'}_${stamm}`;
        const { breite, hoehe } = this.mp4Groesse.wert();
        const physik = this.mp4Physik.checked;
        this.melden(`MP4 wird gestartet (${breite} × ${hoehe}, ${physik ? 'mit' : 'ohne'} Physik) …`);
        this._laeuft = true;
        this._format = 'mp4';
        this.zeigen(this.leiste.zustand || {});
        let ok = false;
        try {
            ok = await this.leiste.render.mp4({ breite, hoehe, physik, ordner, datei });
        } finally {
            this._laeuft = false;
            this.zeigen(this.leiste.zustand || {});
        }
        this.melden(ok ? `MP4 wird gerechnet: ganze BVH, ${breite} × ${hoehe}, ${physik ? 'mit' : 'ohne'} Physik — Stand im Block „Rendern“, gespeichert wird es als ${ordner}\\${datei}.mp4`
            : 'MP4 nicht gestartet — der Grund steht im Block „Rendern“', !ok);
    }

    melden(text, fehler = false) {
        this.meldung.textContent = text;
        this.meldung.classList.toggle('hb-schlecht', fehler);
    }

    async _ordnerSuchen() {
        if (await Exportleisteexport.ordnerSuchen(this.ordner, this.suchen, text => this.melden(text, true))) this._hand.ordner = true;
    }

    /** Fenster „Ordner suchen" für ein Ordnerfeld (auch das Ziel des Videos, `Exportleisterender`) → true, wenn ein Ordner gewählt wurde. */
    static async ordnerSuchen(feld, knopf, melden) {
        knopf.disabled = true;
        try {
            const antwort = await Serverabruf.senden(Exportleisteexport.ORDNERSUCHE, { start: feld.value.trim() });
            if (antwort.ordner) feld.value = antwort.ordner;
            return !!antwort.ordner;
        } catch (fehler) {
            melden(`Ordner suchen ging nicht: ${fehler.message}`);
            return false;
        } finally {
            knopf.disabled = false;
        }
    }

    async exportieren(format) {
        if (format === 'mp4') return this._mp4();
        const animation = this.animation.checked && format !== 'obj';
        if (animation && !this.bvh.value.trim()) { this.melden('Mit Animation braucht eine BVH-Datei (Feld neben dem Haken).', true); return; }
        this._laeuft = true;
        this._format = format;
        this.zeigen(this.leiste.zustand || {});
        const art = { glb: 'GLB', obj: 'OBJ', blend: 'Blender-Datei' }[format];
        this.melden(`${art} wird geschrieben — die Figur wird erst ganz gebaut …`);
        try {
            const ordner = this.ordner.value.trim();
            const name = this.name.value.trim();
            const b = format === 'obj' ? await this.leiste.figur.obj(ordner, name, this.leiste.adresse('obj/')) : await this._server(format, animation, ordner, name);
            if (b.error) throw new Error(b.error);
            // OBJ bringt ein Bild je Materialzone mit (Genesis: rund 20) — die Meldung nennt die ersten und die Zahl
            const liste = b.dateien || [];
            const dateien = liste.slice(0, 3).map(d => `${d.name}${d.bytes ? ` (${(d.bytes / 1048576).toFixed(1)} MB)` : ''}`).join(', ')
                + (liste.length > 3 ? ` … ${liste.length} Dateien` : '');
            const inhalt = format === 'obj' ? 'ohne Animation (OBJ kann keine)' : animation ? `Animation ${b.bilder} Bilder (${b.sekunden} s), ${b.kanaele} Knochen` : 'ohne Animation';
            const fehlend = b.fehlend?.length ? ` · ohne Knoten: ${b.fehlend.join(', ')}` : '';
            const warnungen = b.warnungen?.length ? ` · ${b.warnungen.join(' · ')}` : '';
            this.melden(`${art} fertig, ${inhalt}${fehlend}${warnungen}. Abgelegt in ${b.ordner}: ${dateien}`, !!b.fehlend?.length);
            this.leiste.laden();
        } catch (fehler) {
            this.melden(`Export fehlgeschlagen: ${fehler.daten?.error || fehler.message}`, true);
        } finally {
            this._laeuft = false;
            this.zeigen(this.leiste.zustand || {});
        }
    }

    async _server(format, animation, ordner, name) {
        const { blob, stellung } = await this.leiste.figur.fuerServer();
        const figur = blob ? `Figur gebaut (${(blob.size / 1048576).toFixed(1)} MB)` : 'Das Modell des Bereichs';
        this.melden(`${figur} — der Server schreibt${format === 'blend' ? ' die Blender-Datei (~10 s)' : ''} …`);
        const daten = Exportleistefigur.formular(blob, {
            format, animation, bvh: this.bvh.value.trim(), stellung,
            audio: this.audio.checked && !!this.audioPfad.value.trim(), audio_pfad: this.audioPfad.value.trim(), name, ordner,
        });
        return Serverabruf.formular(this.leiste.adresse('export/'), daten);
    }
}
