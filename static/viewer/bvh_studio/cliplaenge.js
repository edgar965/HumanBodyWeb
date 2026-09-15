/**
 * Cliplaenge — die Länge eines Clips setzen, in Sekunden oder in Prozent.
 *
 * WARUM (Edgar, 13.09.2026): „keine Längenvorgaben! mach kontextmenüs wo man
 * die Länge der Clips setzen kann (in s oder in %)". Bis dahin schnitt das
 * Spurmenü jeden Clip auf zehn Sekunden, und kürzen ging nur in Schritten
 * von zehn Bildern oder durch Ziehen am Rand.
 *
 * Bewegungsclips (`bvh`): Die Länge ist `totalFrames − trimIn − trimOut`
 * Bilder der Quelle; in der Zeitleiste dauert das `/ (fps · speed)`
 * Sekunden. Gesetzt wird nur `trimOut` — der Anfang (`trimIn`) bleibt, wo
 * er ist. Sekunden meinen die Zeitleiste (also mit `speed`), Prozent die
 * ganze Quelle (100 % = alle Bilder ab `trimIn`).
 *
 * Modellclips (`model`, 13.09.2026): Sie haben keine Quelle, die begrenzt —
 * Sekunden setzen `totalFrames` (auch länger), Prozent beziehen sich auf
 * `bezug` (die Projektdauer in Bildern, vom Aufrufer mitgegeben).
 *
 * Tonclips (`audio`): Die Länge ist `data.audioDuration` Sekunden; ganz ist
 * `data.audioVoll` (beim Laden gemerkt), sonst die längste bekannte Dauer.
 *
 * Ohne Import von `state.js` (Three.js): Der Clip kommt als Objekt, das
 * Modul läuft in Node (`test_js_cliplaenge.py`).
 */
export class Cliplaenge {

    /** Wenigstens ein Bild bzw. eine Zehntelsekunde bleibt immer. */
    static MINDESTBILDER = 1;
    static MINDESTSEKUNDEN = 0.1;

    /** Wie lang der Clip jetzt ist: `{sekunden, prozent, bilder, ganz}` (ganz = Sekunden ungekürzt). */
    static stand(clip, bezug = null) {
        if (clip.type === 'audio') {
            const ganz = Cliplaenge._tonGanz(clip);
            const sekunden = (clip.data?.audioDuration || 0) / (clip.speed || 1);
            return { sekunden, prozent: ganz ? 100 * (clip.data.audioDuration || 0) / ganz : 100,
                     bilder: null, ganz: ganz / (clip.speed || 1) };
        }
        const bilder = clip.totalFrames - (clip.trimIn || 0) - (clip.trimOut || 0);
        const teiler = (clip.fps || 30) * (clip.speed || 1);
        if (clip.type === 'model') {
            const ganz = bezug || clip.totalFrames;
            return { sekunden: bilder / teiler, prozent: 100 * bilder / ganz,
                     bilder, ganz: ganz / teiler };
        }
        return { sekunden: bilder / teiler, prozent: 100 * bilder / clip.totalFrames,
                 bilder, ganz: (clip.totalFrames - (clip.trimIn || 0)) / teiler };
    }

    /** Länge in Sekunden der Zeitleiste setzen. Rückgabe: die gesetzte Länge (`stand`). */
    static sekunden(clip, sekunden, bezug = null) {
        if (clip.type === 'audio') {
            const ganz = Cliplaenge._tonGanz(clip);
            const roh = sekunden * (clip.speed || 1);
            clip.data.audioDuration = Math.max(Cliplaenge.MINDESTSEKUNDEN, ganz ? Math.min(roh, ganz) : roh);
            return Cliplaenge.stand(clip);
        }
        const teiler = (clip.fps || 30) * (clip.speed || 1);
        if (clip.type === 'model') return Cliplaenge.modell(clip, sekunden * teiler, bezug);
        return Cliplaenge.bilder(clip, Math.round(sekunden * teiler));
    }

    /** Länge in Prozent der ganzen Quelle setzen. */
    static prozent(clip, prozent, bezug = null) {
        if (clip.type === 'audio') {
            const ganz = Cliplaenge._tonGanz(clip);
            clip.data.audioDuration = Math.max(Cliplaenge.MINDESTSEKUNDEN, Math.min(ganz, ganz * prozent / 100));
            return Cliplaenge.stand(clip);
        }
        if (clip.type === 'model') {
            return Cliplaenge.modell(clip, (bezug || clip.totalFrames) * prozent / 100, bezug);
        }
        return Cliplaenge.bilder(clip, Math.round(clip.totalFrames * prozent / 100));
    }

    /** Bilder eines Modellclips setzen — er hat keine Quelle, `totalFrames` IST die Länge. */
    static modell(clip, bilder, bezug = null) {
        clip.trimOut = 0;
        clip.totalFrames = (clip.trimIn || 0) + Math.max(Cliplaenge.MINDESTBILDER, Math.round(bilder));
        return Cliplaenge.stand(clip, bezug);
    }

    /** Sichtbare Bilder eines Bewegungsclips setzen — über `trimOut`, der Anfang bleibt. */
    static bilder(clip, bilder) {
        const hoechstens = clip.totalFrames - (clip.trimIn || 0);
        const gesetzt = Math.max(Cliplaenge.MINDESTBILDER, Math.min(hoechstens, Math.round(bilder)));
        clip.trimOut = hoechstens - gesetzt;
        return Cliplaenge.stand(clip);
    }

    /** Eine Eingabe wie „12,5" oder „12.5 s" als Zahl — `null`, wenn keine. */
    static zahl(eingabe) {
        if (eingabe == null) return null;
        const wert = parseFloat(String(eingabe).replace(',', '.').replace(/[^0-9.\-]/g, ''));
        return Number.isFinite(wert) && wert > 0 ? wert : null;
    }

    static _tonGanz(clip) {
        const d = clip.data || {};
        return d.audioVoll || d.audioBuffer?.duration || d.audioDuration || 0;
    }
}
