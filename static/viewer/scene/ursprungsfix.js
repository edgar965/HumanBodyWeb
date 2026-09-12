/**
 * Ursprungsfix — „Animation immer auf Ursprungspunkt" (Menü Animation der Szene).
 *
 * Edgar (12.09.2026): „es gab eine Funktion: Animation immer auf
 * Ursprungspunkt, findest du die noch? ich brauche die in /humanbody/scene/
 * im Menü Animation". Die gab es im BVH Studio als „Feste Position"
 * (Werkzeuge, `bvh_studio/werkzeug_position.js`, seit April 2026): Die
 * Wurzel bleibt in jedem Bild innerhalb eines Kreises um ihren Startpunkt
 * (Bild 0) — wer weiter tanzt, wird auf den Rand gezogen, kleine Schritte
 * bleiben. Radius dort 0,5 m; derselbe hier.
 *
 * Der Weg ist der von „Animation immer auf Bodenniveau" (`animation.js`):
 * Die BVH-Datei der Bibliothek wird geändert, gespeichert und neu geladen.
 * Gerechnet wird auf dem Server (`Bvhtext.effekte_sichern` →
 * `BvhDatei.wurzel_festhalten`, Meter → BVH-Zentimeter) — dieselbe Rechnung,
 * die das Studio beim „BVH speichern (mit allen Effekten)" nimmt.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Ursprungsfix {
    /** So weit darf die Wurzel vom Startpunkt weg — wie „Feste Position" im Studio. */
    static RADIUS_M = 0.5;
    static ENDPUNKT = '/api/retarget/save-bvh-effects/';
    /** Bibliotheksadresse einer Animation: `/api/character/bvh/<Kategorie>/<Name>/`. */
    static BIBLIOTHEK = /\/api\/character\/bvh\/([^/?]+)\/([^/?]+)/;

    /** Kategorie und Name aus der Adresse der laufenden Animation — oder null. */
    static quelle(url) {
        const treffer = (url || '').match(Ursprungsfix.BIBLIOTHEK);
        if (!treffer) return null;
        return { category: decodeURIComponent(treffer[1]),
                 name: decodeURIComponent(treffer[2]) };
    }

    static async anwenden() {
        if (!state.currentAnimUrl) { alert('Keine Animation geladen.'); return false; }
        const quelle = Ursprungsfix.quelle(state.currentAnimUrl);
        if (!quelle) {
            alert('Nur für Animationen aus der BVH-Bibliothek — diese kommt nicht daher.');
            return false;
        }
        try {
            const antwort = await Serverabruf.senden(Ursprungsfix.ENDPUNKT, {
                ...quelle, fixed_radius: Ursprungsfix.RADIUS_M });
            if (!antwort.ok) throw new Error(antwort.error || 'Unbekannter Fehler');
            Protokoll.debug('Szene', 'Ursprungsfix:', quelle.category, quelle.name,
                            antwort.applied, antwort.frames, 'Bilder');
        } catch (fehler) {
            alert('Ursprungspunkt: ' + (fehler.message || fehler));
            return false;
        }
        // Frisch laden — die Datei ist geändert, die Adresse dieselbe.
        const trenner = state.currentAnimUrl.includes('?') ? '&' : '?';
        fn.loadBVHAnimation(state.currentAnimUrl + trenner + '_fixed=' + Date.now(),
                            state.currentAnimName, 0);
        alert(`Ursprungspunkt: Wurzel bleibt innerhalb ${Ursprungsfix.RADIUS_M} m um Bild 0`
              + ` (${quelle.category}/${quelle.name} gespeichert).`);
        return true;
    }
}
