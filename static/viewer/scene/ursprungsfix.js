/**
 * Ursprungsfix — „Animation immer auf Ursprungspunkt" (Menü Animation der Szene).
 *
 * Edgar (12.09.2026): „es gab eine Funktion: Animation immer auf
 * Ursprungspunkt, findest du die noch? ich brauche die in /humanbody/scene/
 * im Menü Animation". Die gab es im BVH Studio als „Feste Position"
 * (Werkzeuge, `bvh_studio/werkzeug_position.js`, seit April 2026): Die
 * Wurzel bleibt in jedem Bild innerhalb eines Kreises um ihren Startpunkt
 * (Bild 0) — wer weiter tanzt, wird auf den Rand gezogen, kleine Schritte
 * bleiben. Vorgabe 50 cm wie dort; der Radius wird je Aufruf im Dialog
 * (`_ursprungsfix_dialog.html`) eingestellt (Edgar: „mach den Radius
 * einstellbar"), 0 cm hält die Wurzel genau auf dem Startpunkt. Der zuletzt
 * gewählte Wert bleibt im Browser (`localStorage`, eine Bequemlichkeit, kein
 * Projektzustand — wie `bereichsgedaechtnis.js`).
 *
 * Der Weg ist der von „Animation immer auf Bodenniveau" (`animation.js`):
 * Die BVH-Datei der Bibliothek wird geändert, gespeichert und neu geladen.
 * Gerechnet wird auf dem Server (`Bvhtext.effekte_sichern` →
 * `BvhDatei.wurzel_festhalten`, Meter → BVH-Zentimeter) — dieselbe Rechnung,
 * die das Studio beim „BVH speichern (mit allen Effekten)" nimmt.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { closeDialog, openDialog } from './utils.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Ursprungsfix {
    /** Vorgabe, wenn noch nie gewählt — wie „Feste Position" im Studio (0,5 m). */
    static VORGABE_CM = 50;
    static SCHLUESSEL = 'hb_szene_ursprungsradius_cm';
    static ENDPUNKT = '/api/retarget/save-bvh-effects/';
    /** Bibliotheksadresse einer Animation: `/api/character/bvh/<Kategorie>/<Name>/`. */
    static BIBLIOTHEK = /\/api\/character\/bvh\/([^/?]+)\/([^/?]+)/;
    static #verdrahtet = false;

    /** Kategorie und Name aus der Adresse der laufenden Animation — oder null. */
    static quelle(url) {
        const treffer = (url || '').match(Ursprungsfix.BIBLIOTHEK);
        if (!treffer) return null;
        return { category: decodeURIComponent(treffer[1]),
                 name: decodeURIComponent(treffer[2]) };
    }

    /** Die laufende Animation als Bibliotheksquelle — oder null, und der Grund steht auf dem Schirm. */
    static #quelleDerAnimation() {
        if (!state.currentAnimUrl) { alert('Keine Animation geladen.'); return null; }
        const quelle = Ursprungsfix.quelle(state.currentAnimUrl);
        if (!quelle) alert('Nur für Animationen aus der BVH-Bibliothek — diese kommt nicht daher.');
        return quelle;
    }

    /** Menüpunkt: erst prüfen, ob es eine Bibliotheksanimation gibt, dann den Radius erfragen. */
    static fragen() {
        if (!Ursprungsfix.#quelleDerAnimation()) return false;
        Ursprungsfix.#verdrahten();
        const regler = document.getElementById('ursprungsfix-radius');
        regler.value = Ursprungsfix.gemerkt();
        Ursprungsfix.#anzeigen(regler.value);
        openDialog(document.getElementById('ursprungsfix-dialog'));
        return true;
    }

    /** Der zuletzt gewählte Radius in cm — oder die Vorgabe. */
    static gemerkt() {
        try {
            const cm = parseInt(localStorage.getItem(Ursprungsfix.SCHLUESSEL), 10);
            return Number.isFinite(cm) && cm >= 0 ? cm : Ursprungsfix.VORGABE_CM;
        } catch (fehler) {
            return Ursprungsfix.VORGABE_CM;
        }
    }

    static merken(cm) {
        try {
            localStorage.setItem(Ursprungsfix.SCHLUESSEL, String(cm));
        } catch (fehler) {
            // stumm gewollt: privates Fenster oder gesperrte Seitendaten — dann eben die Vorgabe beim nächsten Mal
        }
    }

    static #anzeigen(cm) {
        document.getElementById('ursprungsfix-radius-val').textContent =
            Number(cm) > 0 ? `${cm} cm` : '0 cm — genau auf dem Startpunkt';
    }

    static #verdrahten() {
        if (Ursprungsfix.#verdrahtet) return;
        Ursprungsfix.#verdrahtet = true;
        document.getElementById('ursprungsfix-radius')
            .addEventListener('input', ereignis => Ursprungsfix.#anzeigen(ereignis.target.value));
        document.getElementById('ursprungsfix-confirm').addEventListener('click', () => {
            const cm = parseInt(document.getElementById('ursprungsfix-radius').value, 10);
            closeDialog(document.getElementById('ursprungsfix-dialog'));
            Ursprungsfix.merken(cm);
            Ursprungsfix.anwenden(cm / 100);
        });
    }

    /** Die Datei der Bibliothek ändern lassen und neu laden. `radiusM` in Metern, 0 = festgenagelt. */
    static async anwenden(radiusM) {
        const quelle = Ursprungsfix.#quelleDerAnimation();
        if (!quelle) return false;
        try {
            const antwort = await Serverabruf.senden(Ursprungsfix.ENDPUNKT, {
                ...quelle, fixed_radius: radiusM });
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
        const wo = radiusM > 0 ? `innerhalb ${Math.round(radiusM * 100)} cm um Bild 0`
                               : 'genau auf dem Startpunkt (Bild 0)';
        alert(`Ursprungspunkt: Wurzel bleibt ${wo} (${quelle.category}/${quelle.name} gespeichert).`);
        return true;
    }
}
