/**
 * Modellgruppen — die verknüpfte Animation steht UNTER ihrer Modellspur.
 *
 * ANLASS (Edgar, 11.09.2026): „ich möchte zu jedem Modell im BVH-Studio die
 * Animation die dafür zugeordnet ist, darunter sehen, etwas eingeklappt z.B.
 * wie bei dem Licht, ein aufklappbarer Unterbereich."
 *
 * Bis dahin standen alle Nutzerspuren in Anlegereihenfolge untereinander;
 * welche Animation ein Modell stellt, sah man nur im Eigenschaften-Feld
 * („Verknüpft: Animation 1"). Jetzt ist die Modellspur der Kopf und die
 * verknüpfte Animationsspur ihre eingerückte Unterreihe — zum Zuklappen wie
 * die Gruppen „Licht" und „Szene", nur je Modell (`spur.zugeklappt`).
 *
 * Ohne DOM und ohne `state`: Die Reihenfolge ist eine Rechnung über die
 * Spurliste, und sie muss in Kopfspalte, Leinwand und Maustreffer DIESELBE
 * sein — deshalb steht sie einmal hier (`test_js_modellgruppen.py`).
 *
 * Zeigen zwei Modellspuren auf dieselbe Animation (die zweite stellt sie ab
 * einem späteren Clip), trägt die ERSTE die Unterreihe; sonst stünde die
 * Animation zweimal in der Zeitleiste. Eine Animation, auf die kein Modell
 * zeigt, bleibt an ihrem Platz.
 */
export class Modellgruppen {

    /** Spurarten, die in eigenen Gruppen stehen — nicht Teil der Nutzerreihen. */
    static GRUPPIERT = ['light', 'scene_object'];

    /** Die Modellspur, unter der die Animationsspur `stelle` steht — oder -1. */
    static traeger(spuren, stelle) {
        if (spuren[stelle]?.type !== 'bvh') return -1;
        return spuren.findIndex(s => s.type === 'model' && s._linkedAnimIdx === stelle);
    }

    /**
     * Die Nutzerreihen in Anzeigereihenfolge. Eine Modellspur mit Unterreihe
     * trägt `unterreihe` (Index der Animation) und `collapsed`; die Animation
     * folgt ihr eingerückt, wenn nicht zugeklappt.
     */
    static reihen(spuren) {
        const reihen = [];
        for (let i = 0; i < spuren.length; i++) {
            const spur = spuren[i];
            if (Modellgruppen.GRUPPIERT.includes(spur.type)) continue;
            if (spur.type === 'bvh' && Modellgruppen.traeger(spuren, i) >= 0) continue;
            const reihe = { trackIdx: i };
            const unter = spur.type === 'model' ? Modellgruppen._unterreihe(spuren, i) : -1;
            if (unter >= 0) {
                reihe.unterreihe = unter;
                reihe.collapsed = Boolean(spur.zugeklappt);
            }
            reihen.push(reihe);
            if (unter >= 0 && !reihe.collapsed) reihen.push({ trackIdx: unter, indent: true });
        }
        return reihen;
    }

    /** Die Animation, die unter der Modellspur `i` steht — oder -1. */
    static _unterreihe(spuren, i) {
        const ziel = spuren[i]._linkedAnimIdx;
        if (!(ziel >= 0) || Modellgruppen.traeger(spuren, ziel) !== i) return -1;
        return ziel;
    }
}
