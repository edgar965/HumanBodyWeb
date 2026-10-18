/**
 * Genesis9seiten — „Seiten koppeln": ein Zug an einem linken Regler stellt den rechten mit und umgekehrt (18.10.2026, Konzept D,
 * `Docu/konzepte/2026-10-18_genesis9-regler-vereinfachen-konzept.md`: 654 Regler tragen Left/Right im Namen).
 *
 * Umschaltbar, Vorgabe AUS — wer eine Seite allein formen will, merkt sonst nicht, warum die andere mitläuft. Der Schalter ist eine Vorliebe des
 * Betrachters und liegt im Browser (`localStorage`), nicht in der Szene. Das Gegenstück wird am NAMEN erkannt (Left↔Right, `_l`↔`_r` am Ende,
 * MakeHumans `l-`↔`r-`) und muss im Plan stehen — sonst bleibt der Zug einseitig.
 */
export class Genesis9seiten {

    static SCHLUESSEL = 'scene_genesis9_seiten_koppeln';
    static MUSTER = [[/Left/g, 'Right'], [/Right/g, 'Left'], [/_l$/, '_r'], [/_r$/, '_l'], [/([_:])l-/g, '$1r-'], [/([_:])r-/g, '$1l-']];
    /** Dazʼ Kennung am Ende (`-0xa37fe31`) — links und rechts tragen oft verschiedene (gesehen 18.10.2026: `EyeBlinkCrescentLeft-0xa37fe31` ↔ `…Right-0xa37fe21`). */
    static KENNUNG = /-0x[0-9a-f]+$/i;
    static _reglerJeName = new Map();
    static _reglerJeStamm = new Map();
    static _an = null;

    /** Den Plan kennenlernen (einmal je Aufbau der Liste). */
    static kennen(plan) {
        const alle = (plan?.bereiche || []).flatMap(b => b.regler || []);
        Genesis9seiten._reglerJeName = new Map(alle.map(r => [r.name, r]));
        Genesis9seiten._reglerJeStamm = new Map(alle.map(r => [r.name.replace(Genesis9seiten.KENNUNG, ''), r]));
    }

    static an() {
        if (Genesis9seiten._an === null) {
            try { Genesis9seiten._an = localStorage.getItem(Genesis9seiten.SCHLUESSEL) === '1'; }
            catch { Genesis9seiten._an = false; }       // Privatfenster oder gesperrter Speicher: Vorgabe aus
        }
        return Genesis9seiten._an;
    }

    static schalten(an) {
        Genesis9seiten._an = Boolean(an);
        try { localStorage.setItem(Genesis9seiten.SCHLUESSEL, an ? '1' : '0'); }
        catch { /* stumm gewollt: ohne Speicher gilt der Schalter nur bis zum Neuladen */ }
    }

    /** Name des Gegenstücks oder null. */
    static gegenname(name) {
        for (const [muster, ersatz] of Genesis9seiten.MUSTER) {
            muster.lastIndex = 0;
            if (muster.test(name)) {
                muster.lastIndex = 0;
                return name.replace(muster, ersatz);
            }
        }
        return null;
    }

    /** Das Gegenstück im Plan, wenn gekoppelt ist — sonst null. */
    static partner(regler) {
        if (!Genesis9seiten.an()) return null;
        const name = Genesis9seiten.gegenname(regler.name);
        if (!name || name === regler.name) return null;
        return Genesis9seiten._reglerJeName.get(name)
            || Genesis9seiten._reglerJeStamm.get(name.replace(Genesis9seiten.KENNUNG, '')) || null;
    }

    /** Schieber und Anzeige des Gegenstücks nachstellen (Liste und Popup). */
    static anzeigen(partner, wert, text) {
        for (const schieber of document.querySelectorAll(`input[data-regler="${CSS.escape(partner.name)}"]`)) {
            schieber.value = wert;
            const anzeige = schieber.parentElement?.querySelector('.slider-value');
            if (anzeige) anzeige.textContent = text;
        }
    }
}
