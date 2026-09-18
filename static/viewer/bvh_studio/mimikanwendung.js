import * as THREE from 'three';
import { state } from './state.js';
import { sharedState } from '../character_core.js';
import { Mimikbasis } from './mimikbasis.js';
import { Mimikkurve } from './mimikkurve.js';
import { Mimiksmplx } from './mimiksmplx.js';
import { Mimikgenesis9 } from './mimikgenesis9.js';
import { Scriptzuschlag } from './scriptzuschlag.js';
import { Lipsyncspur } from './lipsyncspur.js';
import { Lipsynckurve } from '../gemeinsam/lipsynckurve.js';
import { Lipsyncformen } from '../gemeinsam/lipsyncformen.js';

/**
 * Mimikanwendung — je Bild die Gesichtsknochen der Figur aus der Mimikspur setzen.
 *
 * Läuft NACH den Bewegungsspuren (`applyPlayhead`, zweiter Durchlauf): Der
 * Mischer der Körperanimation schreibt seine Knochen zuerst, die Mimik
 * überschreibt danach die Gesichtsknochen — auch den Kiefer und die
 * Ausdrücke, die ein Video mitgebracht hat. Rechnung je Bild:
 * Schlüsselbilder → Gewichte (`Mimikkurve`) + Scripts der Script-Spur
 * (`Scriptzuschlag`, 15.09.2026) → Bewegungen je Knochen (`Mimikbasis`) →
 * `quaternion = ruhe · rot`, `position = ruhe + pos`. Gerechnet wird JE
 * MODELL: Mimik- und Script-Spur hängen beide an der Modellspur. Nur ein
 * Script ohne Mimikspur (Blinzeln beim Tanzen) setzt allein die Knochen,
 * an denen es dreht — das Gesicht aus dem Video bleibt sonst stehen.
 * Die Ruhelage kommt aus den Rigify-Daten (`sharedState.rigifySkeletonData`,
 * Blender-Achsen [w,x,y,z] → Three.js (x,z,−y,w), wie der Skelettbauer).
 * Eine SMPL-X-Figur hat keine Gesichtsknochen — dieselben Gewichte gehen
 * dort als Netzverschiebung (`Mimiksmplx`, 16.09.2026); `anwenden` wählt.
 * Die Lippensynchronisation (18.09.2026, `lipsync`-Clips der Mimikspur)
 * liefert je Bild Mundformen: als MB-Lab-Einheiten zu den Gewichten dazu
 * (DEF, SMPL-X) und als Daz-Visemes für Genesis 9 (`Mimikgenesis9` —
 * Felder im Netz plus Kieferknochen; Genesis 9 kennt die MB-Lab-Posen nicht).
 */
export class Mimikanwendung {

    /** Ruhelage je Knochenname: `{q: Quaternion, p: Vector3}` (einmal gebaut). */
    static _ruhe = null;

    static ruhe() {
        if (Mimikanwendung._ruhe) return Mimikanwendung._ruhe;
        const daten = sharedState.rigifySkeletonData;
        if (!daten?.bones) return null;
        const aus = {};
        for (const b of daten.bones) {
            const q = b.local_quaternion, p = b.local_position;
            aus[b.name] = {
                q: new THREE.Quaternion(q[1], q[3], -q[2], q[0]),
                p: new THREE.Vector3(p[0], p[2], -p[1]),
            };
        }
        Mimikanwendung._ruhe = aus;
        return aus;
    }

    /** Die Figur zur Modellspur `modellIdx` — `{skelett, mesh, quelle}` der verknüpften Spur. */
    static figur(modellIdx) {
        const modell = state.project.tracks[modellIdx];
        if (!modell || modell.type !== 'model') return null;
        const animation = state.project.getLinkedAnimation(modell);
        if (!animation) return null;
        return { skelett: animation.skeleton || animation.mesh?.skeleton || null,
                 mesh: animation.mesh || null, quelle: animation.quelle || 'modell',
                 modell: animation.modell || null };
    }

    /** Das Skelett zur Modellspur (DEF-Weg) — oder null. */
    static skelett(modellIdx) {
        return Mimikanwendung.figur(modellIdx)?.skelett || null;
    }

    /**
     * Gewichte auf die Figur der Modellspur legen — Knochen (DEF), Netz (SMPL-X)
     * oder Daz-Visemes (`visemes`, Genesis 9).
     */
    static anwenden(modellIdx, gewichte, ganz = true, visemes = null) {
        const figur = Mimikanwendung.figur(modellIdx);
        if (!figur) return;
        if (Mimikgenesis9.passt(figur)) { Mimikgenesis9.setzen(figur.modell, visemes || {}); return; }
        if (Mimiksmplx.passt(figur)) { Mimiksmplx.setzen(figur.mesh, gewichte); return; }
        if (figur.skelett && Mimikbasis.bereit) Mimikanwendung.setzen(figur.skelett, gewichte, ganz);
    }

    /** Die (nicht abgeschaltete) Spur der Art `art` zur Modellspur — oder null. */
    static spurZu(modellIdx, art) {
        return state.project.tracks.find(
            s => s.type === art && s._modellIdx === modellIdx && !s.muted) || null;
    }

    /** Gewichte der Posen (Mimikspur) an der Zeit `t` (Sekunden) — ohne Scripts. */
    static posen(spur, t) {
        const schluessel = spur.clips.filter(c => c.type === 'mimik_kf')
            .map(c => ({ frame: c.startFrame, ...c.data }));
        return Mimikkurve.gewichte(schluessel, t * state.project.fps, state.project.fps);
    }

    /**
     * Mundformen der `lipsync`-Clips einer Mimikspur an der Zeit `t`, in der
     * Tabelle `tabelle` (`Lipsyncformen`) — leer, wenn kein Clip die Zeit deckt.
     */
    static lipsync(spur, t, tabelle) {
        const fps = state.project.fps, frame = Math.round(t * fps);
        /** @type {Object<string, number>} */
        let aus = {};
        for (const clip of spur.clips) {
            if (clip.type !== 'lipsync' || !clip.data?.cues) continue;
            const tonzeit = Lipsyncspur.tonzeit(clip, frame, fps);
            if (tonzeit === null) continue;
            aus = Lipsynckurve.addieren(aus, Lipsynckurve.gewichte(clip.data.cues, tonzeit, tabelle));
        }
        return aus;
    }

    /**
     * Gewichte des Modells an der Zeit `t`: Posen der Mimikspur plus die
     * Scripts der Script-Spur plus die Lippensynchronisation.
     * `{gewichte, visemes, mimik, script}` — `visemes` sind die Daz-Regler für
     * Genesis 9; die Marken sagen, ob eine Mimikspur da ist und ob ein Script wirkt.
     */
    static gewichteModell(modellIdx, t) {
        const fps = state.project.fps;
        const mimik = Mimikanwendung.spurZu(modellIdx, 'mimik');
        /** @type {Object<string, number>} */
        let gewichte = mimik ? Mimikanwendung.posen(mimik, t) : {};
        const script = Mimikanwendung.spurZu(modellIdx, 'script');
        const dazu = script ? Scriptzuschlag.gewichte(script.clips, Math.round(t * fps), fps, gewichte)
                            : { aktiv: false, zuschlag: {} };
        for (const [einheit, g] of Object.entries(dazu.zuschlag)) {
            gewichte[einheit] = Math.max(-1, Math.min(1, (gewichte[einheit] || 0) + g));
        }
        let visemes = {};
        if (mimik) {
            gewichte = Lipsynckurve.addieren(gewichte, Mimikanwendung.lipsync(mimik, t, Lipsyncformen.MBLAB));
            visemes = Mimikanwendung.lipsync(mimik, t, Lipsyncformen.GENESIS9);
        }
        return { gewichte, visemes, mimik: Boolean(mimik), script: dazu.aktiv };
    }

    /** Alle Modelle an der Zeit `t`: Mimik- und Script-Spuren anwenden. */
    static alle(t) {
        state.project.tracks.forEach((modell, i) => {
            if (modell.type !== 'model') return;
            const vorschau = Mimikanwendung.spurZu(i, 'mimik')?._vorschau;
            if (vorschau) { Mimikanwendung.anwenden(i, vorschau); return; }
            const stand = Mimikanwendung.gewichteModell(i, t);
            if (!stand.mimik && !stand.script) return;
            Mimikanwendung.anwenden(i, stand.gewichte, stand.mimik, stand.visemes);
        });
    }

    /**
     * Gewichte auf ein Skelett legen. `ganz`: alle Gesichtsknochen — die ohne
     * Anteil in die Ruhelage (Mimikspur); sonst nur die Knochen mit Anteil
     * (ein Script allein lässt das übrige Gesicht der Animation).
     */
    static setzen(skelett, gewichte, ganz = true) {
        const ruhe = Mimikanwendung.ruhe();
        if (!ruhe) return;
        const bewegungen = Mimikbasis.bewegungen(gewichte);
        for (const name of Mimikbasis.knochen()) {
            const knochen = Mimikanwendung._knochen(skelett, name);
            const lage = ruhe[name];
            if (!knochen || !lage) continue;
            const b = bewegungen[name];
            if (!ganz && !b) continue;
            knochen.quaternion.copy(lage.q);
            knochen.position.copy(lage.p);
            if (b) {
                knochen.quaternion.multiply(b.rot);
                knochen.position.add(b.pos);
            }
        }
    }

    static _knochen(skelett, name) {
        if (!skelett._mimikKnochen) {
            skelett._mimikKnochen = {};
            for (const b of skelett.bones) {
                skelett._mimikKnochen[b.name] = b;
                skelett._mimikKnochen[b.name.replace(/_/g, '.')] = b;
            }
        }
        return skelett._mimikKnochen[name] || null;
    }
}
