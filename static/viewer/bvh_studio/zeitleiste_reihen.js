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
import { state, TRACK_HEIGHT, RULER_HEIGHT } from './state.js';

export class Reihen {
    /**
     * Anzeigereihen: erst die Nutzerspuren, dann die Gruppe „Licht", dann die
     * Gruppe „Szene". Jede Reihe ist entweder { trackIdx } oder { header, label }.
     */
    static liste() {
        const reihen = [];
        const spuren = state.project.tracks;
        for (let i = 0; i < spuren.length; i++) {
            const t = spuren[i];
            if (t.type !== 'light' && t.type !== 'scene_object') reihen.push({ trackIdx: i });
        }
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

    /** Reihe unter einer Maus-Y-Position, oder null ausserhalb. */
    static beiY(my) {
        const idx = Math.floor((my - RULER_HEIGHT) / TRACK_HEIGHT);
        const reihen = this.liste();
        return (idx >= 0 && idx < reihen.length) ? reihen[idx] : null;
    }

    /** Obere Kante der Reihe einer Spur, oder -1 wenn sie nicht gezeigt wird. */
    static yFuerSpur(trackIdx) {
        const reihen = this.liste();
        for (let i = 0; i < reihen.length; i++) {
            if (reihen[i].trackIdx === trackIdx) return RULER_HEIGHT + i * TRACK_HEIGHT;
        }
        return -1;
    }

    /**
     * Hoehe, die ALLE Reihen brauchen — mindestens die des sichtbaren Bereichs.
     *
     * Im Browser gemessen (15.08.2026): Der Rahmen ist in der Vorgabehoehe
     * 175 px hoch, eine Spur 40 px. Sichtbar waren drei Spuren; ein Projekt mit
     * 14 Reihen versteckte elf davon, ohne Scrollbalken.
     */
    static noetigeHoehe(rahmen) {
        return Math.max(rahmen.clientHeight,
                        RULER_HEIGHT + this.liste().length * TRACK_HEIGHT);
    }
}
