import * as THREE from 'three';
import { Dazachsen } from '../gemeinsam/dazachsen.js';
import { Genesis9felder } from '../gemeinsam/genesis9felder.js';

/**
 * Mimikgenesis9 — Daz' Visemes auf einer Genesis-9-Figur, je Bild aus der Mimikspur.
 *
 * Edgar, 18.09.2026: „mach Lipsync." Die Lippensynchronisation gibt Gewichte
 * auf den 17 Viseme-Reglern (`facs_ctrl_vAA` …, `Lipsyncformen.GENESIS9`);
 * jeder Regler ist bei Daz ein Morphfeld UND eine Knochenstellung — `Vis AA`
 * öffnet den Kiefer (`lowerjaw` 5,2°) und schiebt die Lippenknochen um
 * Millimeter. Beides liefert `felder/visemes/` (`Genesis9/visemes.py`): die
 * Felder gehen wie die JCMs ins Netz (`Genesis9felder`, Gruppe `visemes`,
 * Körper und Mund-Anhang mit Zähnen und Zunge), die Knochen werden aus den
 * Daz-Winkeln gestellt (`Dazachsen.quaternion`/`versatz`, linear gemischt —
 * Kieferwinkel unter 8°). Ein Knochen, der beim letzten Mal gestellt war und
 * jetzt kein Gewicht mehr hat, geht in die Ruhe; die BVH-Bewegung fasst die
 * Gesichtsknochen nicht an (`g9_zuordnung`: kein DEF-Gegenstück).
 */
export class Mimikgenesis9 {

    static GRUPPE = 'visemes';
    static _figuren = new WeakMap();        // modell -> {skelett, stufen, felder, knochen, gestellt}
    static _q = new THREE.Quaternion();
    static _v = new THREE.Vector3();

    /** Trägt diese Figur (`{modell, quelle}`) ihre Mimik als Daz-Visemes? */
    static passt(figur) {
        return figur?.quelle === 'genesis9' && !!figur?.modell?.bodyMesh;
    }

    /** Gewichte `{facs_ctrl_vAA: 0…1, …}` auf die Figur legen; holt die Felder beim ersten Mal. */
    static setzen(modell, gewichte) {
        const e = Mimikgenesis9._eintrag(modell);
        if (!e?.felder) return false;
        const { felder } = e;
        Genesis9felder.anwenden(modell.bodyMesh, Mimikgenesis9.GRUPPE, felder.koerper, gewichte);
        for (const [schluessel, netz] of Object.entries(modell.anhangNetze || {})) {
            const eigene = felder.anhaenge[schluessel];
            if (eigene) Genesis9felder.anwenden(netz, Mimikgenesis9.GRUPPE, eigene, gewichte);
        }
        Mimikgenesis9._knochen(e, gewichte);
        return true;
    }

    /** Die Knochenstellung: Summe gewicht · Winkel/Versatz je Viseme, dann setzen. */
    static _knochen(e, gewichte) {
        /** @type {Object<string, {rot: number[], pos: number[]}>} */
        const summe = {};
        for (const [kanal, w] of Object.entries(gewichte || {})) {
            const knochen = e.felder.knochen[kanal];
            if (!knochen || !w) continue;
            for (const [name, kanaele] of Object.entries(knochen)) {
                if (!e.knochen[name]) continue;
                const s = summe[name] || (summe[name] = { rot: [0, 0, 0], pos: [0, 0, 0] });
                for (const [pfad, wert] of Object.entries(kanaele)) {
                    const achse = 'xyz'.indexOf(pfad.slice(-1));
                    if (achse < 0) continue;
                    if (pfad.startsWith('rotation/')) s.rot[achse] += wert * w;
                    else if (pfad.startsWith('translation/')) s.pos[achse] += wert * w;
                }
            }
        }
        for (const name of e.gestellt) {
            if (summe[name]) continue;
            const k = e.knochen[name];
            k.bone.quaternion.copy(k.ruheQuat);
            k.bone.position.copy(k.ruhePos);
        }
        e.gestellt = new Set(Object.keys(summe));
        for (const [name, s] of Object.entries(summe)) {
            const k = e.knochen[name];
            Dazachsen.quaternion(k, s.rot, k.bone.quaternion);
            k.bone.position.copy(k.ruhePos).add(Dazachsen.versatz(k, s.pos, Mimikgenesis9._v));
        }
    }

    static _eintrag(modell) {
        let e = Mimikgenesis9._figuren.get(modell);
        if (e && e.skelett === modell.skelett && e.stufen === modell.stufen) return e;
        e = { skelett: modell.skelett, stufen: modell.stufen, felder: null, knochen: {},
              gestellt: new Set() };
        Mimikgenesis9._figuren.set(modell, e);
        Genesis9felder.holen(Mimikgenesis9.GRUPPE, modell.stufen).then(felder => {
            if (!felder || Mimikgenesis9._figuren.get(modell) !== e || !modell.skelett) return;
            e.knochen = Dazachsen.vorbereiten(modell.skelett, felder.achsen);
            e.felder = felder;
        });
        return e;
    }
}
