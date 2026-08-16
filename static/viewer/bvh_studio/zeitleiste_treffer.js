/**
 * Zeitleistentreffer — was liegt an dieser Stelle der Zeitleiste?
 *
 * Aus timeline.js herausgeloest (Umbau 16.08.2026).
 *
 * Die Umrechnung Mausposition → Bildnummer stand dort DREIMAL wortgleich
 * (Abspielkopf setzen, Kontextmenue der Spur, Kontextmenue des Clips) — hier
 * einmal als `bildBei`.
 */
import { state, TRACK_HEIGHT, HEADER_WIDTH, RULER_HEIGHT } from './state.js';
import { Reihen } from './zeitleiste_reihen.js';

/** Breite der Anfasszone an den Clipraendern in Pixeln. */
const RANDZONE = 6;

/** Halbe Kantenlaenge des Klickfelds eines Schluesselbilds. */
const MARKE = 8;

export class Zeitleistentreffer {
    /** Bildnummer unter der Mausposition. */
    static bildBei(mx) {
        const x = mx - HEADER_WIDTH + state.timelineScrollX;
        return Math.max(0, Math.round((x / state.timelineZoom) * state.project.fps));
    }

    /**
     * Clip oder Schluesselbild unter der Maus.
     * @returns {{trackIdx, clipIdx, clipX, clipW, edge?}|null}
     */
    static clipBei(mx, my) {
        const pps = state.timelineZoom;
        const reihen = Reihen.liste();
        for (let ri = 0; ri < reihen.length; ri++) {
            const reihe = reihen[ri];
            if (reihe.header) continue;
            const ti = reihe.trackIdx;
            const spur = state.project.tracks[ti];
            const y = RULER_HEIGHT + ri * TRACK_HEIGHT;
            for (let ci = 0; ci < spur.clips.length; ci++) {
                const clip = spur.clips[ci];
                const cx = HEADER_WIDTH
                    + (clip.startFrame / state.project.fps) * pps - state.timelineScrollX;
                const treffer = (clip.type === 'camera_kf' || clip.type === 'light_kf')
                    ? Zeitleistentreffer._schluesselbild(clip, mx, my, cx, y)
                    : Zeitleistentreffer._clip(clip, mx, my, cx, y, pps);
                if (treffer) return { trackIdx: ti, clipIdx: ci, ...treffer };
            }
        }
        return null;
    }

    /**
     * Schluesselbilder eines Paares sitzen versetzt (oben/unten), damit sich
     * beide einzeln anklicken lassen.
     */
    static _schluesselbild(clip, mx, my, cx, y) {
        const lage = clip.data?.trackPosition;
        const mitte = lage === 'upper' ? y + TRACK_HEIGHT * 0.28
                    : lage === 'lower' ? y + TRACK_HEIGHT * 0.72
                    : y + TRACK_HEIGHT / 2;
        const drin = mx >= cx - MARKE && mx <= cx + MARKE
                  && my >= mitte - MARKE && my <= mitte + MARKE;
        return drin ? { clipX: cx, clipW: 0 } : null;
    }

    static _clip(clip, mx, my, cx, y, pps) {
        const breite = Math.max(clip.duration * pps, 4);
        const oben = y + 4;
        const hoehe = TRACK_HEIGHT - 8;
        if (mx < cx || mx > cx + breite || my < oben || my > oben + hoehe) return null;
        let rand = null;
        if (mx - cx < RANDZONE && breite > 16) rand = 'left';
        else if (cx + breite - mx < RANDZONE && breite > 16) rand = 'right';
        return { clipX: cx, clipW: breite, edge: rand };
    }
}
