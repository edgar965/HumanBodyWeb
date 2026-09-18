/**
 * Netzstufe — Strg+Alt+H schaltet diesen Browser auf die hohe Auflösung.
 *
 * Edgar (17.09.2026): „mach mir eine Tastenkombination, z.B. Strg-Alt-H, mit
 * der ich im Browser die hohe Resolution sehe." Die Einstellung
 * (Einstellungen → Modell) gibt dem Browser 2 Unterteilungsstufen, dem Film
 * 3 — wie MB-Lab (Viewport 2, Render 3). Wer die Filmstufe SEHEN will, setzt
 * hier den Keks `netzstufen=3`; der Server (`core/dienste/netzstufenwahl.py`)
 * nimmt ihn vor der Einstellung, für Netz, Hautgewichte, Lippen und den
 * WebSocket-Kanal gleichermassen.
 *
 * Die Seite lädt danach NEU: Mit der Stufe ändern sich Dreiecke, UVs,
 * Hautgewichte und alles, was an Punktnummern hängt — ein Umbau im laufenden
 * Zustand hiesse, jeden dieser Wege einzeln nachzuziehen.
 *
 * Solange der Keks steht, zeigt ein Abzeichen unten rechts die Stufe, damit
 * niemand „langsam" meldet, ohne zu wissen, warum.
 */
export class Netzstufe {

    static KEKS = 'netzstufen';
    /** Die Filmstufe von MB-Lab (`render_levels 3`). */
    static HOCH = 3;
    /** Ein Jahr — der Keks ist eine Wahl, keine Sitzung. */
    static DAUER_S = 365 * 24 * 3600;
    static TASTE = 'KeyH';
    static ABZEICHEN_ID = 'netzstufe-abzeichen';

    /** Die gewählte Stufe (1–3) oder null, wenn die Einstellung gilt. */
    static gewaehlt(keks = document.cookie) {
        const treffer = new RegExp('(?:^|; *)' + Netzstufe.KEKS + '=([0-9])').exec(keks || '');
        const wert = treffer ? Number(treffer[1]) : NaN;
        return wert >= 1 && wert <= 3 ? wert : null;
    }

    /** Den Keks setzen (1–3) oder mit null löschen; liefert den Keks-Text. */
    static keksText(stufe) {
        if (stufe === null) return `${Netzstufe.KEKS}=; path=/; max-age=0; SameSite=Lax`;
        return `${Netzstufe.KEKS}=${stufe}; path=/; max-age=${Netzstufe.DAUER_S}; SameSite=Lax`;
    }

    static setzen(stufe) {
        document.cookie = Netzstufe.keksText(stufe);
    }

    /** Ob das Ereignis Strg+Alt+H ist (AltGr zählt unter Windows als Strg+Alt). */
    static istTaste(ereignis) {
        return !!ereignis.ctrlKey && !!ereignis.altKey && !ereignis.shiftKey
            && ereignis.code === Netzstufe.TASTE;
    }

    /** Hoch ↔ Einstellung; liefert die neue Wahl (3 oder null). */
    static naechste(bisher) {
        return bisher === Netzstufe.HOCH ? null : Netzstufe.HOCH;
    }

    static umschalten() {
        const neu = Netzstufe.naechste(Netzstufe.gewaehlt());
        Netzstufe.setzen(neu);
        Netzstufe.abzeichen(neu, true);
        location.reload();
    }

    /**
     * Das Abzeichen unten rechts — bei `laedt` mit Hinweis auf den Neustart.
     * @returns {HTMLElement|null} das Element, null wenn nichts zu zeigen ist
     */
    static abzeichen(stufe = Netzstufe.gewaehlt(), laedt = false) {
        let feld = document.getElementById(Netzstufe.ABZEICHEN_ID);
        if (stufe === null && !laedt) { feld?.remove(); return null; }
        if (!feld) {
            feld = document.createElement('div');
            feld.id = Netzstufe.ABZEICHEN_ID;
            Object.assign(feld.style, {
                position: 'fixed', right: '12px', bottom: '12px', zIndex: '9000',
                padding: '6px 10px', borderRadius: '6px', font: '12px/1.4 sans-serif',
                background: 'rgba(255, 153, 64, 0.92)', color: '#1a1a1a',
                pointerEvents: 'none', boxShadow: '0 2px 8px rgba(0,0,0,.4)',
            });
            document.body.appendChild(feld);
        }
        feld.textContent = Netzstufe.text(stufe, laedt);
        return feld;
    }

    static text(stufe, laedt = false) {
        const was = stufe === null
            ? 'Netz: Einstellung' : `Netz: hohe Auflösung (${stufe} Stufen)`;
        return laedt ? `${was} — Seite lädt neu …` : `${was} · Strg+Alt+H schaltet um`;
    }

    /** Auf jeder Figurseite einmal rufen: Taste anbinden, Abzeichen zeigen. */
    static einrichten(fenster = window) {
        fenster.addEventListener('keydown', ereignis => {
            if (!Netzstufe.istTaste(ereignis)) return;
            ereignis.preventDefault();
            ereignis.stopImmediatePropagation();
            Netzstufe.umschalten();
        }, true);
        Netzstufe.abzeichen();
    }
}
