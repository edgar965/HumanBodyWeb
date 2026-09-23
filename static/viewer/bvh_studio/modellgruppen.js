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
 *
 * UMBAU 22.09.2026 (Edgar: „Effekte Spur soll als Unterspur zum Modell
 * angelegt werden, wie Animation"): Eine Effekte-Spur hängt selbst an einer
 * ANIMATION (`_linkedAnimIdx`, `effektschluessel.js`), nicht direkt am Modell —
 * sie steht darum eingerückt NEBEN der Animation, wenn (und nur wenn) diese
 * Animation ihrerseits unter einem Modell steht. Ohne Modell (Animation frei
 * in der Liste) bleibt die Effekte-Spur ebenfalls an ihrem eigenen Platz.
 */
export class Modellgruppen {

    /** Spurarten, die in eigenen Gruppen stehen — nicht Teil der Nutzerreihen. */
    static GRUPPIERT = ['light', 'scene_object'];
    /** Spurarten, die an einer Modellspur hängen (`_modellIdx`). */
    static AM_MODELL = ['mimik', 'script'];

    /** Die Modellspur, unter der die Animationsspur `stelle` steht — oder -1. */
    static traeger(spuren, stelle) {
        if (spuren[stelle]?.type !== 'bvh') return -1;
        return spuren.findIndex(s => s.type === 'model' && s._linkedAnimIdx === stelle);
    }

    /**
     * Die Modellspur, deren Zuklappen die Reihe `stelle` mit verbirgt — oder
     * -1, wenn sie an keiner hängt. Anders als `traeger` (nur die Animation
     * selbst) deckt das auch Mimik/Script (`_modellIdx`) und Effekte
     * (`_linkedAnimIdx` → deren Animation → deren Modell) ab.
     *
     * ANLASS (22.09.2026, Edgar: „ein Effekte Ereignis erscheint nicht", „ein
     * Script Ereignis erscheint nicht im Track"): `Spurauswahl.einblenden`
     * klappte beim Anlegen eines Ereignisses nur eine zugeklappte MODELLSPUR
     * auf, wenn die ausgewählte Reihe selbst die Animation war — bei Mimik,
     * Script und Effekte blieb die Gruppe zu, das neue Ereignis unsichtbar.
     */
    static eigentuemerModell(spuren, stelle) {
        const spur = spuren[stelle];
        if (!spur) return -1;
        if (spur.type === 'bvh') return Modellgruppen.traeger(spuren, stelle);
        if (Modellgruppen.AM_MODELL.includes(spur.type)) {
            return spuren[spur._modellIdx]?.type === 'model' ? spur._modellIdx : -1;
        }
        if (spur.type === 'effekte') {
            return Modellgruppen.traeger(spuren, spur._linkedAnimIdx);
        }
        return -1;
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
            // Mimik- und Script-Spuren stehen unter ihrer Modellspur (14./15.09.2026).
            if (Modellgruppen.AM_MODELL.includes(spur.type)
                && spuren[spur._modellIdx]?.type === 'model') continue;
            // Effekte-Spur unter dem Modell ihrer Animation (22.09.2026).
            if (spur.type === 'effekte' && Modellgruppen._effekteEingebettet(spuren, i)) continue;
            const reihe = { trackIdx: i };
            const unter = spur.type === 'model' ? Modellgruppen._unterreihe(spuren, i) : -1;
            if (unter >= 0) {
                reihe.unterreihe = unter;
                reihe.collapsed = Boolean(spur.zugeklappt);
            }
            reihen.push(reihe);
            if (unter >= 0 && !reihe.collapsed) {
                reihen.push({ trackIdx: unter, indent: true });
                spuren.forEach((s, j) => {
                    if (s.type === 'effekte' && s._linkedAnimIdx === unter) {
                        reihen.push({ trackIdx: j, indent: true });
                    }
                });
            }
            if (spur.type === 'model' && !reihe.collapsed) {
                spuren.forEach((s, j) => {
                    if (Modellgruppen.AM_MODELL.includes(s.type) && s._modellIdx === i) {
                        reihen.push({ trackIdx: j, indent: true });
                    }
                });
            }
        }
        return reihen;
    }

    /** Die Animation, die unter der Modellspur `i` steht — oder -1. */
    static _unterreihe(spuren, i) {
        const ziel = spuren[i]._linkedAnimIdx;
        if (!(ziel >= 0) || Modellgruppen.traeger(spuren, ziel) !== i) return -1;
        return ziel;
    }

    /** True, wenn die Effekte-Spur `i` unter einem Modell eingerückt erscheint. */
    static _effekteEingebettet(spuren, i) {
        const ziel = spuren[i]._linkedAnimIdx;
        return ziel >= 0 && Modellgruppen.traeger(spuren, ziel) >= 0;
    }
}
