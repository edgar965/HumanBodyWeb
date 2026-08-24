import { state } from './state.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Bvhausgabe — BVH-Dateien herunterladen (ganze Spur oder ein Clip).
 *
 * Herausgelöst aus `export_video.js` (236 Zeilen), das zwei völlig verschiedene
 * Ausgaben führte: BVH-Text und Video. Der Download-Weg stand darin dreimal
 * (Blob, Objekt-URL, unsichtbarer Link, URL freigeben).
 *
 * WARUM MEHRERE CLIPS ALS EINZELNE DATEIEN GEHEN
 * =============================================
 * BVH kennt genau EIN Skelett je Datei. Zwei Clips zusammenzuhängen ergäbe eine
 * Datei, die kein Programm richtig liest. Deshalb eine Datei je Clip — mit einer
 * kurzen Pause dazwischen, weil Browser mehrere Downloads in derselben
 * Ereignisrunde verwerfen.
 *
 * WARUM DIE OBJEKT-URL FREIGEGEBEN WIRD
 * =====================================
 * `URL.createObjectURL` hält den Blob im Speicher, bis die Seite neu lädt. Bei
 * 30 Exporten einer 40-MB-BVH ist das über ein Gigabyte.
 */
export class Bvhausgabe {

    static QUELLE = '/api/character/bvh';
    static TYP = 'text/plain';

    /** Alle Clips der ausgewählten Spur herunterladen. */
    static async spur() {
        if (state.selectedTrackIdx < 0) {
            alert('Track auswählen.');
            return;
        }
        const spur = state.project.tracks[state.selectedTrackIdx];
        if (spur.clips.length === 0) {
            alert('Track hat keine Clips.');
            return;
        }
        const texte = await Bvhausgabe._holen(spur.clips);
        if (texte.length === 0) {
            alert('Keine BVH Daten.');
            return;
        }
        for (const [nummer, { clip, text }] of texte.entries()) {
            Bvhausgabe.herunterladen(text, `${spur.name}_${clip.name}.bvh`);
            // Pause: Mehrere Downloads in derselben Runde verwirft der Browser.
            if (nummer < texte.length - 1) {
                await new Promise(weiter => setTimeout(weiter, Zeiten.BILDPAUSE_MS));
            }
        }
        Protokoll.info('BVH Studio',
                       `Exported ${texte.length} BVH file(s) for track "${spur.name}"`);
    }

    static async _holen(clips) {
        const texte = [];
        for (const clip of clips) {
            try {
                texte.push({ clip, text: await Bvhausgabe.text(clip) });
            } catch (fehler) {
                Protokoll.fehler('BVH Studio',
                                 `BVH zu ${clip.name} nicht geladen`, fehler);
            }
        }
        return texte;
    }

    static async text(clip) {
        return Serverabruf.text(
            `${Bvhausgabe.QUELLE}/${encodeURIComponent(clip.category)}`
            + `/${encodeURIComponent(clip.name)}/`);
    }

    // ------------------------------------------------------- Speichern unter

    /** Den ausgewählten Clip mit dem Dateidialog speichern. */
    static async speichernUnter() {
        if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) {
            alert('Clip auswählen.');
            return;
        }
        const clip = state.project.tracks[state.selectedTrackIdx]
            .clips[state.selectedClipIdx];
        try {
            const text = await Bvhausgabe.text(clip);
            const name = `${clip.name}.bvh`;
            if (await Bvhausgabe._mitDialog(text, name)) return;
            Bvhausgabe.herunterladen(text, name);
            Protokoll.debug('BVH Studio', `BVH downloaded: ${name}`);
        } catch (fehler) {
            alert('BVH speichern fehlgeschlagen: ' + fehler.message);
        }
    }

    /**
     * Über den nativen „Speichern unter"-Dialog. `true`, wenn erledigt.
     *
     * Bricht der Nutzer ab (`AbortError`), gilt das als erledigt: Ein Download
     * hinterher wäre genau das, was er gerade verhindert hat.
     */
    static async _mitDialog(text, name) {
        if (!window.showSaveFilePicker) return false;
        try {
            const griff = await window.showSaveFilePicker({
                suggestedName: name,
                types: [{ description: 'BVH Motion Capture',
                          accept: { 'text/plain': ['.bvh'] } }],
            });
            const schreiber = await griff.createWritable();
            await schreiber.write(new Blob([text], { type: Bvhausgabe.TYP }));
            await schreiber.close();
            Protokoll.info('BVH Studio', `BVH saved via picker: ${griff.name}`);
            return true;
        } catch (fehler) {
            if (fehler.name === 'AbortError') return true;
            Protokoll.warnung('BVH Studio',
                              'Dateidialog gescheitert — Download stattdessen',
                              fehler);
            return false;
        }
    }

    // ------------------------------------------------------------- Download

    /** Text als Datei herunterladen — EINE Fassung (siehe Klassendoku). */
    static herunterladen(text, dateiname) {
        const adresse = URL.createObjectURL(
            new Blob([text], { type: Bvhausgabe.TYP }));
        const link = document.createElement('a');
        link.href = adresse;
        link.download = dateiname;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(adresse);          // sonst bleibt der Blob liegen
    }
}
