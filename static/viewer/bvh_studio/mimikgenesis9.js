import * as THREE from 'three';
import { Dazachsen } from '../gemeinsam/dazachsen.js';
import { Genesis9felder } from '../gemeinsam/genesis9felder.js';
import { Genesis9mimikformen } from '../gemeinsam/genesis9mimikformen.js';

/**
 * Mimikgenesis9 — Gesichtsausdruck einer Genesis-9-Figur, je Bild aus der
 * Mimik-/Script-Spur (MB-Lab-Einheiten, `Genesis9mimikformen`) UND der
 * Lippensynchronisation (Daz' Visemes, `facs_ctrl_vAA` …).
 *
 * Edgar, 18.09.2026: „mach Lipsync" — zuerst nur die 17 Viseme-Regler
 * (`Genesis9/visemes.py`); jeder Regler ist bei Daz ein Morphfeld UND eine
 * Knochenstellung — `Vis AA` öffnet den Kiefer (`lowerjaw` 5,2°) und schiebt
 * die Lippenknochen um Millimeter. Beides liefert `felder/<gruppe>/`
 * (`Genesis9/reglerfelder.py`): die Felder gehen wie die JCMs ins Netz
 * (`Genesis9felder`, Körper und Mund-Anhang mit Zähnen und Zunge), die
 * Knochen werden aus den Daz-Winkeln gestellt (`Dazachsen.quaternion`/
 * `versatz`, linear gemischt — Kieferwinkel unter 8°).
 *
 * Edgar, 22.09.2026: „ich hatte das ALLES in Auftrag gegeben" — die
 * allgemeine Mimik (Posen der Mimikspur, Zuschlag der Script-Spur, dieselben
 * MB-Lab-Einheiten wie bei DEF/SMPL-X) fehlte bis dahin: `setzen()` bekam
 * `visemes` UND `gewichte` (roh verworfen). Jetzt zwei Reglergruppen
 * (`visemes`, `mimik` — `Genesis9/mimik.py`), zusammen am Netz UND am
 * Skelett gesetzt: Ein Knochen, der beim letzten Mal gestellt war und jetzt
 * in KEINER der beiden Gruppen mehr ein Gewicht hat, geht in die Ruhe; die
 * BVH-Bewegung fasst die Gesichtsknochen nicht an (`g9_zuordnung`: kein
 * DEF-Gegenstück).
 */
export class Mimikgenesis9 {

    static GRUPPEN = ['visemes', 'mimik'];
    static _figuren = new WeakMap();        // modell -> {skelett, stufen, gruppen, knochen, gestellt}
    static _q = new THREE.Quaternion();
    static _v = new THREE.Vector3();

    /** Trägt diese Figur (`{modell, quelle}`) ihre Mimik als Daz-Regler? */
    static passt(figur) {
        return figur?.quelle === 'genesis9' && !!figur?.modell?.bodyMesh;
    }

    /**
     * `visemes` (Daz-Kanal-Gewichte, Lipsync) UND `gewichte` (MB-Lab-Einheiten
     * der Mimik-/Script-Spur, über `Genesis9mimikformen` übersetzt) auf die
     * Figur legen — beide Gruppen zusammen, damit ein Knochen nicht von der
     * einen Gruppe gesetzt und von der anderen sofort zurückgesetzt wird.
     */
    static setzen(modell, visemes, gewichte) {
        const e = Mimikgenesis9._eintrag(modell);
        const mimikKanaele = Genesis9mimikformen.uebersetzen(gewichte);
        const kombiniert = {};
        const kombinierteKnochen = {};
        let etwasDa = false;
        for (const [gruppe, kanalGewichte] of
             [['visemes', visemes || {}], ['mimik', mimikKanaele]]) {
            const felder = e.gruppen[gruppe];
            if (!felder) continue;
            etwasDa = true;
            Genesis9felder.anwenden(modell.bodyMesh, gruppe, felder.koerper, kanalGewichte);
            for (const [schluessel, netz] of Object.entries(modell.anhangNetze || {})) {
                const eigene = felder.anhaenge[schluessel];
                if (eigene) Genesis9felder.anwenden(netz, gruppe, eigene, kanalGewichte);
            }
            Object.assign(kombiniert, kanalGewichte);
            Object.assign(kombinierteKnochen, felder.knochen);
        }
        if (!etwasDa) return false;
        Mimikgenesis9._knochen(e, kombiniert, kombinierteKnochen);
        return true;
    }

    /** Die Knochenstellung: Summe gewicht · Winkel/Versatz je Kanal (beide Gruppen), dann setzen. */
    static _knochen(e, gewichte, knochenTabelle) {
        /** @type {Object<string, {rot: number[], pos: number[]}>} */
        const summe = {};
        for (const [kanal, w] of Object.entries(gewichte || {})) {
            const knochen = knochenTabelle[kanal];
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
        e = { skelett: modell.skelett, stufen: modell.stufen, knochen: {},
              gestellt: new Set(), gruppen: {}, _knochenVorbereitet: false };
        Mimikgenesis9._figuren.set(modell, e);
        for (const gruppe of Mimikgenesis9.GRUPPEN) {
            Genesis9felder.holen(gruppe, modell.stufen).then(felder => {
                if (!felder || Mimikgenesis9._figuren.get(modell) !== e || !modell.skelett) return;
                e.gruppen[gruppe] = felder;
                // Die Achsen (Orientierung je Knochen) sind gruppenunabhängig —
                // einmal vorbereiten reicht, welche Gruppe zuerst ankommt.
                if (!e._knochenVorbereitet) {
                    e.knochen = Dazachsen.vorbereiten(modell.skelett, felder.achsen);
                    e._knochenVorbereitet = true;
                }
            });
        }
        return e;
    }
}
