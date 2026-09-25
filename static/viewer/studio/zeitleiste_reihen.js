/**
 * Reihen — die Zuordnung zwischen Bildschirmzeilen und Spuren.
 *
 * Aus timeline.js herausgeloest (Umbau 15.08.2026). Vier kleine Funktionen, die
 * ueber die ganze Datei verstreut waren und doch zusammengehoeren: Welche Reihen
 * zeigt die Zeitleiste, welche Reihe liegt an einem Mauszeiger, wo beginnt die
 * Reihe einer Spur, und wie hoch muss die Leinwand sein.
 *
 * Hin- und Rueckrechnung MUESSEN dieselbe Reihenliste benutzen — sonst greift man
 * neben den Clip. Genau darum stehen sie jetzt in einer Klasse.
 */
import { state, RULER_HEIGHT } from './state.js';
import { Modellgruppen } from './modellgruppen.js';
import { Spurhoehe } from './spurhoehe.js';

export class Reihen {
    /**
     * Anzeigereihen: erst die Nutzerspuren (eine verknüpfte Animation
     * eingerückt unter ihrer Modellspur, `Modellgruppen`), dann die Gruppe
     * „Licht", dann die Gruppe „Szene". Jede Reihe ist entweder { trackIdx }
     * oder { header, label }.
     */
    static liste() {
        const spuren = state.project.tracks;
        const reihen = Modellgruppen.reihen(spuren);
        this._gruppe(reihen, spuren, 'light', 'Licht', state.lightGroupCollapsed);
        this._gruppe(reihen, spuren, 'scene_object', 'Szene', state.sceneGroupCollapsed);
        return reihen;
    }

    static _gruppe(reihen, spuren, typ, label, zugeklappt) {
        const vorhanden = spuren.some((t) => t.type === typ);
        if (!vorhanden) return;
        reihen.push({ header: typ === 'light' ? 'light' : 'scene', label,
                      collapsed: !!zugeklappt });
        if (zugeklappt) return;
        for (let i = 0; i < spuren.length; i++) {
            if (spuren[i].type === typ) reihen.push({ trackIdx: i, indent: true });
        }
    }

    /**
     * Reihen mit Lage: `[{reihe, y, h}]`. Seit dem 25.09.2026 hat jede Spur ihre
     * eigene Höhe (`Spurhoehe`) — `y` ist die Summe der Höhen darüber, nicht
     * mehr `Nummer × TRACK_HEIGHT`. Zeichnen und Treffer nehmen BEIDE diese Liste.
     */
    static lagen() {
        const spuren = state.project.tracks;
        let y = RULER_HEIGHT;
        return this.liste().map((reihe) => {
            const h = Spurhoehe.reihe(reihe, spuren);
            const lage = { reihe, y, h };
            y += h;
            return lage;
        });
    }

    /** Reihe unter einer Maus-Y-Position, oder null ausserhalb. */
    static beiY(my) {
        const lage = this.lagen().find((l) => my >= l.y && my < l.y + l.h);
        return lage ? lage.reihe : null;
    }

    /** Obere Kante der Reihe einer Spur, oder -1 wenn sie nicht gezeigt wird. */
    static yFuerSpur(trackIdx) {
        const lage = this.lagen().find((l) => l.reihe.trackIdx === trackIdx);
        return lage ? lage.y : -1;
    }

    /**
     * Hoehe, die ALLE Reihen brauchen — mindestens die des sichtbaren Bereichs.
     *
     * Im Browser gemessen (15.08.2026): Der Rahmen ist in der Vorgabehoehe
     * 175 px hoch, eine Spur 40 px. Sichtbar waren drei Spuren; ein Projekt mit
     * 14 Reihen versteckte elf davon, ohne Scrollbalken.
     */
    static noetigeHoehe(rahmen) {
        const lagen = this.lagen();
        const letzte = lagen[lagen.length - 1];
        return Math.max(rahmen.clientHeight, letzte ? letzte.y + letzte.h : RULER_HEIGHT);
    }
}
