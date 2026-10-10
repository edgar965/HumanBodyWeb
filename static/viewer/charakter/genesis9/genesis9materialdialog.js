import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Genesis9teilmaterial } from '../../gemeinsam/genesis9teilmaterial.js';
import { Genesis9teilregler } from './genesis9teilregler.js';

/**
 * Genesis9materialdialog — der Zahnradknopf neben einer Auswahl und das Popup mit Glanz, Rauheit, Relief,
 * Deckkraft und Feuchte des Teils (Haut, Augen, Augenbrauen, Wimpern, Nägel, Mund). Darunter der Block „Form" mit den
 * Formreglern des Teils (Brauen, Wimpern, Nägel, Augengröße/Pupille — `genesis9teilregler.js`); die Zeilen baut
 * `Genesis9eigenschaften` (`form`), damit es derselbe Weg bleibt wie in der Reglerliste.
 *
 * WARUM (Edgar, 09.10.2026, mit Bild der Auswahllisten: „mach die Combo kleiner, daneben einen
 * Einstellungsknopf mit Popup wo ich das ändern kann"): Die Daz-Presets bringen Glanz und Rauheit mit; die
 * Augen sahen glasig aus (`genesis9teilmaterial.js`). Die Zeile behält ihre Auswahl, der Knopf daneben öffnet das Popup
 * (Rahmen wie der Farbdialog, `stueckfarbdialog.js`: Hintergrund frei, damit man die Figur beim Verstellen sieht).
 * Esc, „Fertig" und „×" schließen; ein zweiter Klick auf denselben Knopf auch. Die Werte gelten sofort, gehen mit
 * der Figur in die Datei (`inst.teilmaterial`) und kommen nach jedem Neubau wieder (`Genesis9Modell.koerperAufbauen`).
 */
export class Genesis9materialdialog {

    /** Preset-Kategorie der Zeilen → Teil, wo sie einen Zahnradknopf bekommen (`plan.praesets[].kategorie`). */
    static KATEGORIE = { wimpern: 'wimpern', nagellack: 'naegel', mund: 'mund' };

    static _offen = null;

    /** Von `Genesis9eigenschaften._haut` gesetzt: `{ inst, plan, zeile(regler) }` — die Quelle des Blocks „Form". */
    static form = null;

    /** Den Zahnradknopf an eine Zeile hängen und die Zeile zurückgeben. */
    static knopf(inst, teil, zeile) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'hb-materialknopf';
        knopf.textContent = '⚙';
        knopf.title = `Material · ${Genesis9teilmaterial.TEILE[teil].titel}: Glanz, Rauheit …`;
        knopf.addEventListener('click', () => Genesis9materialdialog.umschalten(inst, teil));
        zeile.appendChild(knopf);
        return zeile;
    }

    /** Wie `knopf`, aber für die Zeilen der Preset-Kategorien — nur die, zu denen ein Teil gehört. */
    static fuerKategorie(inst, kategorie, zeile) {
        const teil = Genesis9materialdialog.KATEGORIE[kategorie];
        return teil ? Genesis9materialdialog.knopf(inst, teil, zeile) : zeile;
    }

    static umschalten(inst, teil) {
        const offen = Genesis9materialdialog._offen;
        const gleich = offen && offen.inst === inst && offen.teil === teil;
        Genesis9materialdialog.schliessen();
        if (!gleich) Genesis9materialdialog.oeffnen(inst, teil);
    }

    static oeffnen(inst, teil) {
        Genesis9materialdialog.schliessen();
        const huelle = document.createElement('div');
        huelle.className = 'scene-modal-overlay visible stueckfarb-huelle';
        huelle.innerHTML = `
            <div class="scene-modal stueckfarb-dialog hb-materialdialog" role="dialog" aria-label="Material einstellen">
                <div class="scene-modal-header">
                    <h4>Material · ${escapeHtml(Genesis9teilmaterial.TEILE[teil].titel)}</h4>
                    <button type="button" class="scene-modal-close" title="Schließen">×</button>
                </div>
                <div class="scene-modal-body"></div>
                <div class="scene-modal-footer">
                    <button type="button" class="btn-toggle hb-material-alles">Alles auf Standard</button>
                    <button type="button" class="primary hb-material-fertig">Fertig</button>
                </div>
            </div>`;
        document.body.appendChild(huelle);
        const taste = (e) => { if (e.key === 'Escape') Genesis9materialdialog.schliessen(); };
        document.addEventListener('keydown', taste);
        Genesis9materialdialog._offen = { huelle, inst, teil, taste };
        Genesis9materialdialog._zeichnen();
        huelle.querySelector('.scene-modal-close').addEventListener('click', Genesis9materialdialog.schliessen);
        huelle.querySelector('.hb-material-fertig').addEventListener('click', Genesis9materialdialog.schliessen);
        huelle.querySelector('.hb-material-alles').addEventListener('click', () => {
            Genesis9teilmaterial.zuruecksetzen(inst, teil);
            markDirty();
            Genesis9materialdialog._zeichnen();
        });
    }

    static schliessen() {
        const offen = Genesis9materialdialog._offen;
        if (!offen) return;
        document.removeEventListener('keydown', offen.taste);
        offen.huelle.remove();
        Genesis9materialdialog._offen = null;
    }

    /** Die Zeilen des offenen Dialogs aus dem Stand der Figur neu bauen. */
    static _zeichnen() {
        const { huelle, inst, teil } = Genesis9materialdialog._offen;
        const koerper = huelle.querySelector('.scene-modal-body');
        koerper.innerHTML = '';
        const felder = Genesis9teilmaterial.felder(inst, teil);
        if (!felder.some(f => f.verfuegbar)) {
            koerper.innerHTML = '<div class="gedaempft">Dieses Teil ist noch nicht geladen oder hat an diesem Modell kein eigenes Material.</div>';
        }
        for (const f of felder) koerper.appendChild(Genesis9materialdialog._zeile(inst, teil, f));
        const form = Genesis9materialdialog.form;
        const block = form?.inst === inst ? Genesis9teilregler.block(form.plan, teil, form.zeile) : null;
        if (block) koerper.appendChild(block);
        huelle.querySelector('.hb-material-alles').disabled = !felder.some(f => f.eigen);
    }

    static _zeile(inst, teil, f) {
        const zeile = document.createElement('div');
        zeile.className = 'hb-materialzeile';
        zeile.title = f.hilfe;
        const standard = typeof f.standard === 'number' ? ` · Standard ${f.standard.toFixed(2)}` : '';
        zeile.innerHTML = `
            <label>${escapeHtml(f.titel)}</label>
            <input type="range" min="${f.min}" max="${f.max}" step="${f.schritt}" value="${f.wert}"${f.verfuegbar ? '' : ' disabled'}>
            <span class="slider-value">${f.verfuegbar ? f.wert.toFixed(2) : '–'}</span>
            <button type="button" class="hb-materialzurueck" title="Auf Standard${escapeHtml(standard)}"${f.eigen ? '' : ' disabled'}>↺</button>`;
        const regler = zeile.querySelector('input');
        const anzeige = zeile.querySelector('.slider-value');
        const zurueck = zeile.querySelector('button');
        regler.addEventListener('input', () => {
            const wert = parseFloat(regler.value);
            anzeige.textContent = wert.toFixed(2);
            zurueck.disabled = false;
            Genesis9teilmaterial.setzen(inst, teil, f.feld, wert);
            markDirty();
            Genesis9materialdialog._alles(inst);
        });
        zurueck.addEventListener('click', () => {
            Genesis9teilmaterial.setzen(inst, teil, f.feld, null);
            markDirty();
            Genesis9materialdialog._zeichnen();
        });
        return zeile;
    }

    /** „Alles auf Standard" ist erst gültig, sobald ein Feld eigen ist — ohne die Zeilen neu zu bauen (der Schieber wird gezogen). */
    static _alles(inst) {
        const offen = Genesis9materialdialog._offen;
        if (offen?.inst === inst) offen.huelle.querySelector('.hb-material-alles').disabled = false;
    }
}
