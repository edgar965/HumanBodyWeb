import { fn } from '../gemeinsam/registrierung.js';
import { Spurhoehe } from './spurhoehe.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';

/**
 * Spurhoehengriff — der Ziehgriff an der Unterkante einer Spur-Kopfzeile.
 *
 * Ziehen ändert NUR diese Spur (`Spurhoehe.setzen`). Während des Ziehens wird
 * die Kopfzeile direkt nachgeführt und die Leinwand neu gezeichnet; erst beim
 * Loslassen baut die Kopfspalte neu (sonst verlöre der Griff mitten im Zug
 * sein Element). Doppelklick setzt die Vorgabehöhe zurück.
 */
export class Spurhoehengriff {
    static anbringen(el, spur) {
        const griff = document.createElement('div');
        griff.className = 'spurhoehe-griff';
        griff.title = 'Spurhöhe ziehen (Doppelklick: Vorgabe)';
        griff.addEventListener('click', (e) => e.stopPropagation());
        griff.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            spur.hoehe = undefined;
            Spurhoehe.setzen(spur, Spurhoehe.von({}));
            fn.updateTrackHeaders();
            fn.renderTimeline();
        });
        griff.addEventListener('mousedown', (e) => Spurhoehengriff._ziehen(e, el, spur));
        el.appendChild(griff);
    }

    static _ziehen(e, el, spur) {
        if (e.button !== 0) return;
        e.preventDefault();
        e.stopPropagation();
        const startY = e.clientY;
        const startH = Spurhoehe.von(spur);
        const behaelter = el.parentElement;
        const bewegen = (ev) => {
            const h = Spurhoehe.setzen(spur, startH + ev.clientY - startY);
            el.style.height = h + 'px';
            fn.renderTimeline();
            const leinwand = Zeitleistenflaeche.canvas;
            if (behaelter && leinwand) behaelter.style.height = leinwand.height + 'px';
        };
        const ende = () => {
            window.removeEventListener('mousemove', bewegen);
            window.removeEventListener('mouseup', ende);
            document.body.style.cursor = '';
            fn.updateTrackHeaders();
            fn.renderTimeline();
        };
        document.body.style.cursor = 'row-resize';
        window.addEventListener('mousemove', bewegen);
        window.addEventListener('mouseup', ende);
    }
}
