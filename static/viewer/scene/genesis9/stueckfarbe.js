import { Dazkleidung } from './dazkleidung.js';
import { Umfaerbung } from '../../gemeinsam/umfaerbung.js';
import { markDirty } from '../undo.js';
import { Stueckfarbdialog } from './stueckfarbdialog.js';

/**
 * Stueckfarbe — die eigene Farbe eines Daz-Stücks: fürs ganze Stück
 * (`werte.farbe`) und je Materialgruppe (`werte.gruppenfarben`, schlägt die
 * des Stücks). Beide liegen in den Werten des getragenen Stücks
 * (`inst.kleidung[kennung]` bzw. `inst.dazKleidung`) und werden damit wie
 * Variante und Regler mit der Figur gespeichert; gerechnet wird im Shader
 * (`Umfaerbung`), ohne Serveranfrage und ohne Neubau.
 *
 * Zwei Orte zeigen dieselben Werte: die Zeile im Assets-Reiter
 * (`genesis9garderobe.js`, nur die Farbe des Stücks) und die Eigenschaften
 * des gewählten Stücks (`dazeigenschaften.js`, dazu jede Gruppe). Jedes Feld
 * trägt `data-stueckfarbe` (und `data-gruppe`), `abgleichen` stellt nach einer
 * Änderung alle nach.
 */
export class Stueckfarbe {

    /** Anzeige ohne eigene Farbe — das Feld steht dann halb durchsichtig. */
    static LEER = '#808080';

    /** Farbe des ganzen Stücks ('' = aus); wirkt nur auf ein getragenes Stück. */
    static ganz(inst, kennung, hex) {
        const werte = Dazkleidung.kleidung(inst)[kennung];
        if (!werte) return false;
        werte.farbe = hex || '';
        return Stueckfarbe._anwenden(inst, kennung, werte);
    }

    /** Farbe einer Materialgruppe ('' = wieder die des Stücks). */
    static gruppe(inst, kennung, gruppe, hex) {
        const werte = Dazkleidung.kleidung(inst)[kennung];
        if (!werte || !gruppe) return false;
        // Neues Objekt: die gespeicherte Figur hält eine flache Kopie der Werte.
        const neu = { ...(werte.gruppenfarben || {}) };
        if (hex) neu[gruppe] = hex; else delete neu[gruppe];
        werte.gruppenfarben = neu;
        return Stueckfarbe._anwenden(inst, kennung, werte);
    }

    static _anwenden(inst, kennung, werte) {
        Umfaerbung.stueck(inst, kennung, werte);
        markDirty();
        Stueckfarbe.abgleichen(inst, kennung);
        return true;
    }

    /**
     * Ein Farbknopf mit „×": Der Knopf zeigt die Farbe und öffnet die
     * Farbwahl (`Stueckfarbdialog`, 24.09.2026 — das Farbfeld in der Zeile
     * stand abgeschnitten hinter der Variantenauswahl). `gruppe` wählt das
     * Ziel vor; `ganz(hex)` merkt die Farbe eines NICHT getragenen Stücks.
     * Das Element trägt `wert` und `zeigen(hex)` (für `abgleichen`).
     */
    static feld({ inst, kennung, gruppe = '', wert = '', titel = 'Farbe', ganz = null }) {
        const kasten = document.createElement('span');
        kasten.className = 'hb-stueckfarbe';
        kasten.dataset.stueckfarbe = kennung;
        if (gruppe) kasten.dataset.gruppe = gruppe;
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'hb-stueckfarbe-knopf';
        const weg = document.createElement('button');
        weg.type = 'button';
        weg.className = 'hb-stueckfarbe-weg';
        weg.textContent = '×';
        weg.title = 'Eigene Farbe entfernen — wieder die Farbe aus Daz';
        kasten.zeigen = (hex) => {
            kasten.wert = hex || '';
            knopf.style.background = hex || '';
            kasten.classList.toggle('gesetzt', Boolean(hex));
            weg.hidden = !hex;
            knopf.title = `${titel}: ${hex || 'Farbe aus Daz'} — klicken zum Wählen`;
        };
        kasten.zeigen(wert);
        const merken = (hex) => { kasten.zeigen(hex); ganz?.(hex); };
        knopf.addEventListener('click', (e) => {
            e.stopPropagation();
            Stueckfarbdialog.oeffnen({ inst, kennung, gruppe, wert: kasten.wert,
                                       ganz: gruppe ? null : merken });
        });
        weg.addEventListener('click', (e) => {
            e.stopPropagation();
            if (gruppe) Stueckfarbe.gruppe(inst, kennung, gruppe, '');
            else if (!Stueckfarbe.ganz(inst, kennung, '')) merken('');
        });
        kasten.append(knopf, weg);
        return kasten;
    }

    /** Alle Felder dieses Stücks auf den gespeicherten Stand. */
    static abgleichen(inst, kennung) {
        const werte = Dazkleidung.kleidung(inst)[kennung] || {};
        for (const kasten of document.querySelectorAll('.hb-stueckfarbe[data-stueckfarbe]')) {
            if (kasten.dataset.stueckfarbe !== kennung || typeof kasten.zeigen !== 'function') continue;
            const gruppe = kasten.dataset.gruppe;
            kasten.zeigen(gruppe ? (werte.gruppenfarben?.[gruppe] || '') : (werte.farbe || ''));
        }
    }
}
