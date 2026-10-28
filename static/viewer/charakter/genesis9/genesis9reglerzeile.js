import { escapeHtml } from '../utils.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Genesis9skala } from './genesis9skala.js';
import { Genesis9seiten } from './genesis9seiten.js';
import { Genesis9groessehalten } from './genesis9groessehalten.js';

/**
 * Genesis9reglerzeile — EIN Regler des Genesis-Bedienfelds: Schieber, Anzeige, Lauf (aus `genesis9eigenschaften.js` herausgelöst, 18.10.2026 — die Datei
 * stand bei 343 Zeilen).
 *
 * Seit der Gliederung nach Körperteil (`Genesis9/reglergliederung.py`) kann ein Regler für MEHRERE Kanäle stehen:
 *   aliase  `[{name, faktor}]` — gleiche Wirkung, gemessen (`G9reglerorte`). Ein gespeicherter Alias-Wert `w` zeigt sich hier als `w × faktor`; der erste
 *           Zug stellt den Hauptregler und räumt die Aliasse ab — sonst wirkten beide zusammen.
 *   paar    Name des linken Morphs eines Gegenstück-Paars („Ears Move Backward ↔ Forward“): links (< 0) stellt `paar`, rechts (> 0) `name`.
 */
export class Genesis9reglerzeile {

    /**
     * Der Wert, den ein Regler zeigt: was der Nutzer gestellt hat, sonst der WIRKSAME Wert aus dem Formelgraphen (`inst.morphwerte`, vom Server).
     * Edgar (18.09.2026): „bei Ursula9 ist der Ursula Head gerade bei 0 %" — das Preset stellt nur den Steuerregler, Kopf und Körper bekommen ihre 100 %
     * über Formeln. Daz zeigt bei so einem Kanal die Summe. `gesteuert` = nicht selbst gestellt, aber wirksam.
     */
    static wert(inst, regler) {
        if (regler.paar) {
            const rechts = Genesis9reglerzeile._kanal(inst, regler.name, 0);
            const links = Genesis9reglerzeile._kanal(inst, regler.paar, 0);
            return { wert: rechts.wert - links.wert, gesteuert: rechts.gesteuert || links.gesteuert };
        }
        const eigen = Genesis9reglerzeile._kanal(inst, regler.name, regler.vorgabe ?? 0);
        if (eigen.gestellt || Math.abs(eigen.wert) > 1e-9) return eigen;
        for (const alias of regler.aliase || []) {
            const w = inst.regler?.[alias.name];
            if (w !== undefined && w !== null) return { wert: w * alias.faktor, gesteuert: false };
        }
        return eigen;
    }

    static _kanal(inst, name, vorgabe) {
        const eigen = inst.regler?.[name];
        const gestellt = eigen !== undefined && eigen !== null;
        const wirksam = inst.morphwerte?.[name];
        // Ein Kanal mit Deltas zeigt seine SUMME (eigener Wert + Formeln, wie Daz) — auch nach einem eigenen Zug.
        if (wirksam !== undefined && Math.abs(wirksam) > 1e-9) return { wert: wirksam, gesteuert: !gestellt, gestellt };
        return { wert: gestellt ? eigen : vorgabe, gesteuert: false, gestellt };
    }

    /** Dazʼ Grenzen — steht der Wert darüber (Spielraum `weit_min`/`weit_max`, 08.10.2026), reicht der Schieber bis dorthin. */
    static bereich(regler, wert) {
        let unten = regler.min;
        let oben = regler.max;
        if (wert > oben) oben = Math.max(wert, regler.weit_max ?? wert);
        if (wert < unten) unten = Math.min(wert, regler.weit_min ?? wert);
        return { unten, oben };
    }

    /** Daz zeigt die Kanäle als Prozent — hier auch; gesteuerte mit Stern. */
    static text(wert, gesteuert = false, regler = null) {
        const eigene = Genesis9skala.text(wert, regler);     // Lebensalter in Jahren (`G9lebensalter`)
        if (eigene) return `${eigene}${gesteuert ? ' *' : ''}`;
        return `${Math.round(wert * 100)} %${gesteuert ? ' *' : ''}`;
    }

    /** Die Zeile. `nachher` läuft nach jedem fertigen Lauf (Kopf und gesteuerte Schieber nachziehen). */
    static bauen(inst, regler, nachher, praefix = 'g9-') {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const { wert, gesteuert } = Genesis9reglerzeile.wert(inst, regler);
        const kennung = `${praefix}${regler.name}`;
        // `hinweis`: ein Sammelregler (Alter, `G9alter`) sagt, was er stellt; ein gemessener Platz, warum er dort steht (`G9reglerplatz`).
        const titel = gesteuert ? `${regler.name} — über Formeln gestellt` : (regler.hinweis || regler.name);
        const { unten, oben } = Genesis9reglerzeile.bereich(regler, wert);
        // für die KI gesperrt (`G9reglersperre`, 28.10.2026): von Hand bedienbar, mit Schloss — der Grund steht im Hinweis
        const schloss = regler.ki_gesperrt ? '<i class="fas fa-lock" style="opacity:.55;margin-right:3px" aria-label="für KI gesperrt"></i>' : '';
        zeile.innerHTML = `
            <label for="${kennung}" title="${escapeHtml(titel)}">${schloss}${escapeHtml(regler.anzeige)}</label>
            <input type="range" id="${kennung}" min="${unten}" max="${oben}"
                   step="0.01" value="${wert}" data-regler="${escapeHtml(regler.name)}">
            <span class="slider-value">${Genesis9reglerzeile.text(wert, gesteuert, regler)}</span>`;
        const schieber = zeile.querySelector('input');
        const anzeige = zeile.querySelector('.slider-value');
        schieber.addEventListener('input', () => {
            const neu = parseFloat(schieber.value);
            anzeige.textContent = Genesis9reglerzeile.text(neu, false, regler);
            const partner = Genesis9seiten.partner(regler);
            Genesis9lauf.planen(inst, () => Genesis9reglerzeile.setzen(inst, regler, neu, partner), nachher,
                                `regler:${regler.name}`);
            if (partner) Genesis9seiten.anzeigen(partner, neu, Genesis9reglerzeile.text(neu, false, partner));
        });
        return zeile;
    }

    /** Wert stellen — bei einem Paar die passende Seite, bei Aliassen sie abräumen; `partner` (Seiten gekoppelt) bekommt denselben Wert. */
    static setzen(inst, regler, wert, partner = null) {
        inst.regler = inst.regler || {};
        for (const r of partner ? [regler, partner] : [regler]) {
            for (const alias of r.aliase || []) delete inst.regler[alias.name];
            if (r.paar) {
                if (wert < 0) inst.regler[r.paar] = -wert;
                else delete inst.regler[r.paar];
            }
            if (r !== regler) {
                const w = r.paar ? Math.max(wert, 0) : wert;
                if (Math.abs(w) < 1e-6) delete inst.regler[r.name];
                else inst.regler[r.name] = w;
            }
        }
        const w = regler.paar ? Math.max(wert, 0) : wert;
        // „Größe halten" (R8, 25.10.2026): erst rechnet der Server den Ausgleich, dann baut die Figur EINMAL (`genesis9groessehalten.js`).
        return Genesis9groessehalten.zug(inst, regler.name, w, () => inst.reglerSetzen(regler.name, w));
    }

    /** Nach einem Lauf die Schieber auf den neuen Wert (Liste `g9-` UND Popup „Form" `g9d-` tragen denselben `data-regler`). */
    static nachziehen(inst, plan) {
        const alle = (plan?.bereiche || []).flatMap(b => b.regler || []);
        for (const regler of alle) {
            for (const schieber of document.querySelectorAll(`input[data-regler="${CSS.escape(regler.name)}"]`)) {
                if (schieber === document.activeElement) continue;
                const { wert, gesteuert } = Genesis9reglerzeile.wert(inst, regler);
                const { unten, oben } = Genesis9reglerzeile.bereich(regler, wert);
                if (parseFloat(schieber.min) !== unten) schieber.min = unten;
                if (parseFloat(schieber.max) !== oben) schieber.max = oben;
                if (Math.abs(parseFloat(schieber.value) - wert) < 1e-6) continue;
                schieber.value = wert;
                const anzeige = schieber.parentElement?.querySelector('.slider-value');
                if (anzeige) anzeige.textContent = Genesis9reglerzeile.text(wert, gesteuert, regler);
            }
        }
    }
}
