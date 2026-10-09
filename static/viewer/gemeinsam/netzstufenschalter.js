import { Netzstufe } from './netzstufe.js';
import { Netzstufenstand } from './netzstufenstand.js';

/**
 * Netzstufenschalter — Strg+Alt+H schaltet grob → fein → ultrafein → grob, die Stufe steht IMMER rechts unten.
 *
 * Edgar, 09.10.2026 (siehe `Netzstufenstand`). Vorher schaltete die Taste nur zwischen der Einstellung und der Filmstufe
 * (`Netzstufe.umschalten`) und das Abzeichen stand nur bei der Filmstufe da; wer nicht wusste, dass die Figur noch nachlud,
 * sah eine grobe Figur ohne Erklärung. Jetzt zeigt die Anzeige die fertige Stufe, beim Nachladen den Fortschritt, und immer
 * den Hinweis auf die Taste.
 *
 * Die Stufen sind nur für Genesis-9-Figuren verschieden. Steht keine in der Szene, bleibt der Neustart wie bisher
 * (`Netzstufe`: Keks, Seite lädt neu) — „grob" und „fein" sind dort dieselbe Einstellung.
 */
export class Netzstufenschalter {

    static HINWEIS = 'Strg+Alt+H zum Ändern';

    /**
     * Auf der Szene-Seite einmal rufen.
     * @param umbauen `(ziel) => Promise<boolean>` — baut die Figuren im Stand um; true, wenn erledigt
     */
    static einrichten(fenster = window, umbauen = null) {
        fenster.addEventListener('keydown', ereignis => {
            if (!Netzstufe.istTaste(ereignis)) return;
            ereignis.preventDefault();
            ereignis.stopImmediatePropagation();
            Netzstufenschalter.weiter(umbauen);
        }, true);
        document.addEventListener(Netzstufenstand.EREIGNIS, () => Netzstufenschalter.zeigen());
        Netzstufenschalter.zeigen();
    }

    /** Eine Stufe weiter, ausgehend von der ANGEZEIGTEN. */
    static async weiter(umbauen) {
        const ziel = Netzstufenstand.naechste(Netzstufenstand.zusammen().stufe);
        Netzstufenstand.wahl = ziel;
        // Der Keks gilt für den Server: nur die Filmstufe braucht ihn; grob und fein sind seine Einstellung.
        Netzstufe.setzen(ziel === 'ultrafein' ? Netzstufe.HOCH : null);
        Netzstufenschalter.zeigen();
        let fertig = false;
        if (umbauen) {
            try { fertig = await umbauen(ziel); } catch (fehler) { console.warn('[Netzstufe]', fehler); }
        }
        if (fertig) { Netzstufenschalter.zeigen(); return false; }
        // Keine Genesis-Figur in der Szene: wie bisher neu laden (die Filmstufe behält der Einmal-Keks).
        if (ziel === 'ultrafein') document.cookie = `${Netzstufe.NEULADEN}=1; path=/; max-age=60; SameSite=Lax`;
        location.reload();
        return true;
    }

    /** Der Text der Anzeige. */
    static text(stand = Netzstufenstand.zusammen(), wahl = Netzstufenstand.wahl) {
        if (stand.laedt) {
            const zaehler = stand.gesamt ? ` (${stand.fertig}/${stand.gesamt})` : '';
            return `Netz: ${stand.stufe} → ${wahl} lädt …${zaehler} · ${Netzstufenschalter.HINWEIS}`;
        }
        return `Netz: ${stand.stufe} · ${Netzstufenschalter.HINWEIS}`;
    }

    /** Die Anzeige rechts unten anlegen oder auffrischen. */
    static zeigen() {
        if (typeof document === 'undefined' || !document.body) return null;
        const stand = Netzstufenstand.zusammen();
        let feld = document.getElementById(Netzstufe.ABZEICHEN_ID);
        if (!feld) {
            feld = document.createElement('div');
            feld.id = Netzstufe.ABZEICHEN_ID;
            Object.assign(feld.style, {
                position: 'fixed', right: '12px', bottom: '12px', zIndex: '9000',
                padding: '6px 10px', borderRadius: '6px', font: '12px/1.4 sans-serif',
                pointerEvents: 'none', boxShadow: '0 2px 8px rgba(0,0,0,.4)',
            });
            document.body.appendChild(feld);
        }
        feld.textContent = Netzstufenschalter.text(stand);
        feld.dataset.stufe = stand.stufe;
        feld.dataset.laedt = stand.laedt ? '1' : '0';
        // grob hell-gelb (Warnung: noch nicht scharf), fein dezent, ultrafein orange wie bisher die hohe Stufe.
        const farben = {
            grob: ['rgba(255, 224, 140, 0.95)', '#1a1a1a'],
            fein: ['rgba(40, 44, 60, 0.85)', '#c8cedc'],
            ultrafein: ['rgba(255, 153, 64, 0.92)', '#1a1a1a'],
        }[stand.stufe] || ['rgba(40, 44, 60, 0.85)', '#c8cedc'];
        [feld.style.background, feld.style.color] = farben;
        return feld;
    }
}
