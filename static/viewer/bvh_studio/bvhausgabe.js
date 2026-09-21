import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Bvhtext } from './bvhtext.js';
import { pushUndo } from './undo.js';
import { Bibliothekskanal } from '../gemeinsam/bibliothekskanal.js';

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
 *
 * TRIM GEHÖRT IN DEN EXPORT (Befund 21.09.2026)
 * ==============================================
 * `text()` holte bisher immer die VOLLE Quelldatei — ein geteilter Clip (Split)
 * exportierte damit jedes Mal die ganze ungeschnittene Animation, `trimIn`/
 * `trimOut` wurden schlicht ignoriert. Jetzt schneidet `Bvhtext.ausschnitt()`
 * den Text, bevor er das Modul verlässt.
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

    /** Der Clip-Text — mit `trimIn`/`trimOut` angewendet, nicht die volle Quelle. */
    static async text(clip) {
        const voll = await Serverabruf.text(
            `${Bvhausgabe.QUELLE}/${encodeURIComponent(clip.category)}`
            + `/${encodeURIComponent(clip.name)}/`);
        if (!clip.trimIn && !clip.trimOut) return voll;
        return new Bvhtext(voll).ausschnitt(clip.trimIn, clip.trimOut).text();
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

    // ------------------------------------------------- In Bibliothek speichern

    /**
     * Den (getrimmten) Clip als NEUE Datei in der BVH-Bibliothek ablegen —
     * anders als `speichernUnter()` (reiner lokaler Download, siehe Klassendoku
     * oben) landet die Datei serverseitig unter `3DObjects/animations/bvh/…`,
     * und der Clip im Projekt zeigt danach auf sie (Trim ist eingerechnet,
     * `trimIn`/`trimOut` also 0). Das ist der Weg für „Teil einer geschnittenen
     * Animation dauerhaft weiterverwenden" (Edgar, 21.09.2026).
     */
    static async inBibliothekSpeichern() {
        if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) {
            alert('Clip auswählen.');
            return;
        }
        const spur = state.project.tracks[state.selectedTrackIdx];
        const clip = spur.clips[state.selectedClipIdx];
        if (clip.type !== 'bvh') {
            alert('Nur bei einem BVH-Clip möglich.');
            return;
        }
        const eingabe = prompt('In Bibliothek speichern unter (Ordner/Name):',
                               `${clip.category}/${clip.name}`);
        if (!eingabe) return;
        const trenner = eingabe.lastIndexOf('/');
        const kategorie = trenner >= 0 ? eingabe.slice(0, trenner).trim() : '';
        const name = trenner >= 0 ? eingabe.slice(trenner + 1).trim() : '';
        if (!kategorie || !name) {
            alert('Format: Ordner/Name — z. B. A_Results/Tanz Teil 1');
            return;
        }
        if (kategorie === clip.category && name === clip.name) {
            alert('Das ist die bestehende Datei — für einen Ausschnitt einen anderen Namen wählen.');
            return;
        }
        try {
            if (await Bvhausgabe._existiert(kategorie, name)
                && !confirm(`"${kategorie}/${name}.bvh" gibt es schon in der Bibliothek — überschreiben?`)) {
                return;
            }
            const text = await Bvhausgabe.text(clip);
            await Serverabruf.senden('/api/character/save-bvh-text/',
                                     { category: kategorie, name, bvh_text: text });
            pushUndo('BVH in Bibliothek speichern');
            clip.totalFrames = clip.totalFrames - clip.trimIn - clip.trimOut;
            clip.trimIn = 0;
            clip.trimOut = 0;
            clip.category = kategorie;
            clip.name = name;
            clip.animClip = null;
            fn.loadClipAnimation?.(spur, clip);
            fn.renderTimeline?.();
            Bibliothekskanal.melden('save', { category: kategorie, name });
            Protokoll.info('BVH Studio', `In Bibliothek gespeichert: ${kategorie}/${name}`);
        } catch (fehler) {
            alert('In Bibliothek speichern fehlgeschlagen: ' + fehler.message);
        }
    }

    /** `true`, wenn unter Ordner/Name schon eine BVH in der Bibliothek liegt. */
    static async _existiert(kategorie, name) {
        try {
            await Serverabruf.text(`${Bvhausgabe.QUELLE}/${encodeURIComponent(kategorie)}`
                                   + `/${encodeURIComponent(name)}/`);
            return true;
        } catch (fehler) {
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
