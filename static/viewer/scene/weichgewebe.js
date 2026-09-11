/**
 * Weichgewebe — Velocity Skinning LIVE an der Figur der Szene.
 *
 * Der Regler „Weichgewebe" im Animations-Reiter wirkt sofort: Bei
 * laufender Animation bekommt jeder Punkt des Körpers und seiner
 * gehäuteten Kleidungsstücke einen Zuschlag aus den Knochengeschwindig-
 * keiten. Rechnung: `gemeinsam/weichgewebekoerper.js` (ohne Three.js,
 * geprüft gegen die Python-Fassung); hier nur das Holen der Knochen aus
 * Three.js und das Schreiben des Zuschlags in den Shader. Der Aufbau je
 * Figur steht in `weichgewebeaufbau.js`.
 *
 * DER SHADER ADDIERT NACH DEM SKINNING. `transformed += zuschlag;` steht
 * hinter `#include <skinning_vertex>` — genau die Zeile 194 des Originals
 * (`position[k] += deformation[k]`). Ein Morph-Ziel wäre falsch: Three.js
 * addiert Morphs VOR dem Skinning, und der Zuschlag würde mitgedreht.
 *
 * DIE STÄRKE WIRD NACHGEFÜHRT, nicht vorab kalibriert: Im Browser gibt es
 * die Bahn nicht im Voraus. Ein gleitendes Maximum des Zuschlags zieht die
 * Stärke gedämpft auf den Millimeterwert des Reglers; nach ein bis zwei
 * Sekunden Bewegung sitzt sie. Kleidung bekommt DIESELBE Stärke wie der
 * Körper und wird je Bild gegen ihn gekürzt (`Stoffgrenze`, 6 mm zur
 * Haut) — wie im Server-Weg. Die halbe Stärke ohne Grenze, die bis zum
 * 11.09.2026 hier stand, war ein Notbehelf.
 */
import { state } from './state.js';
import { Weichgewebekoerper } from '../gemeinsam/weichgewebekoerper.js';
import { Weichgewebeaufbau } from './weichgewebeaufbau.js';

export class Weichgewebe {
    /** Anteil je Bild, mit dem die Stärke dem Ziel folgt — gedämpft, sonst
     *  pumpt sie mit jeder Schrittphase. */
    static NACHFUEHRUNG = 0.08;
    /** Startwert der Stärke — aus dem Server-Weg gemessen: 25 mm brauchen
     *  an dieser Figur rund 0,03. Nur der Anfangswert; danach geregelt. */
    static START_STAERKE_JE_M = 1.25;
    /** Fenster des gleitenden Maximums in Sekunden. */
    static FENSTER_S = 1.5;

    static _figuren = new Map();          // inst -> Eintrag

    /** Der Regler in Millimetern — für die gewählte Figur. */
    static setzen(inst, mm) {
        if (!inst?.bodyMesh?.isSkinnedMesh) return false;
        const ziel = Math.max(0, Number(mm) || 0) / 1000;
        let eintrag = Weichgewebe._figuren.get(inst);
        if (!eintrag) {
            eintrag = Weichgewebeaufbau.anlegen(inst);
            if (!eintrag) return false;
            Weichgewebe._figuren.set(inst, eintrag);
        }
        eintrag.ziel = ziel;
        if (ziel <= 0) Weichgewebe._nullen(eintrag);
        return true;
    }

    static ziel(inst) { return (Weichgewebe._figuren.get(inst)?.ziel || 0) * 1000; }

    // --------------------------------------------------------------- Takt

    /** Höchstens so viel Rechenzeit je Sekunde für die Physik — der Rest
     *  gehört dem Rendern. Gemessen in Node: 69 ms je Bild bei 70.851
     *  Punkten und Kettentiefe 8; jedes Bild zu rechnen hieße 14 Bilder je
     *  Sekunde für alles. Mit dem Budget läuft die Physik mit rund 8 Hz und
     *  das Bild bleibt flüssig. */
    static BUDGET_ANTEIL = 0.5;

    /** Aus der Szenenschleife, nach `mixer.update(dt)`. */
    static takt(dt) {
        for (const eintrag of Weichgewebe._figuren.values()) {
            if (eintrag.ziel <= 0) continue;
            if (!state.playing || dt <= 0) {
                // Steht die Animation, ist das Tempo null — und ein Neustart
                // darf nicht aus „letztes Bild → erstes Bild" ein Tempo machen.
                eintrag.tempo.zuruecksetzen();
                continue;
            }
            // Zeitbudget: Nach einem Bild, das `d` ms gekostet hat, ruht die
            // Physik, bis mindestens `d / BUDGET_ANTEIL` ms vergangen sind.
            const jetzt = performance.now();
            if (eintrag.messung) eintrag.messung.bilder += 1;
            if (jetzt < (eintrag.naechstes || 0)) { eintrag.dtAngesammelt = (eintrag.dtAngesammelt || 0) + dt; continue; }
            const dtGesamt = (eintrag.dtAngesammelt || 0) + dt;
            eintrag.dtAngesammelt = 0;
            const t0 = performance.now();
            Weichgewebe._bild(eintrag, dtGesamt);
            const dauer = performance.now() - t0;
            eintrag.naechstes = performance.now() + dauer / Weichgewebe.BUDGET_ANTEIL;
            eintrag.dauerMs = dauer;
            // Laufende Messung (auslesbar nach einem Tabwechsel): Dauer je
            // Physikbild und Bilder je Sekunde der Zeichenschleife.
            eintrag.messung = eintrag.messung || { bilder: 0, physik: 0, ms: 0, seit: performance.now() };
            eintrag.messung.physik += 1; eintrag.messung.ms += dauer;
            if (!eintrag.gemeldet) {
                eintrag.gemeldet = true;
                let paare = 0;
                for (const teil of eintrag.netze) for (const p of teil.koerper.punkteJeKnochen) paare += p.idx.length;
                console.info(`Weichgewebe: ${eintrag.netze.length} Netze, ${eintrag.b} Knochen, `
                    + `${paare} Punkt-Knochen-Paare, erstes Bild ${dauer.toFixed(0)} ms`);
            }
        }
    }

    static _bild(e, dt) {
        const { skelett, inst } = e;
        inst.bodyMesh.updateMatrixWorld(true);
        skelett.update();
        e._bindInv.copy(inst.bodyMesh.bindMatrixInverse);
        const bind = inst.bodyMesh.bindMatrix;
        for (let k = 0; k < e.b; k++) {
            const bone = skelett.bones[k];
            e.pos[3 * k] = bone.position.x; e.pos[3 * k + 1] = bone.position.y; e.pos[3 * k + 2] = bone.position.z;
            e.quat[4 * k] = bone.quaternion.x; e.quat[4 * k + 1] = bone.quaternion.y;
            e.quat[4 * k + 2] = bone.quaternion.z; e.quat[4 * k + 3] = bone.quaternion.w;
            // Weltdrehung des Elternteils, in den Netzraum gebracht.
            const p = e.eltern[k] >= 0 ? skelett.bones[e.eltern[k]] : null;
            if (p) {
                e._m.multiplyMatrices(e._bindInv, p.matrixWorld);
                e._m.decompose(e._v, e._q, e._s);
                e._m2.makeRotationFromQuaternion(e._q);
                const m = e._m2.elements;
                // zeilenweise 3x3 aus spaltenweiser 4x4
                e.elternDreh.set([m[0], m[4], m[8], m[1], m[5], m[9], m[2], m[6], m[10]], 9 * k);
            } else {
                e.elternDreh.set([1, 0, 0, 0, 1, 0, 0, 0, 1], 9 * k);
            }
            // Knochenmatrix im Netzraum: bindInv * boneMatrix * bind
            e._m.fromArray(skelett.boneMatrices, 16 * k);
            e._m.premultiply(e._bindInv).multiply(bind);
            e.matrizen.set(e._m.elements, 16 * k);
        }
        e.tempo.takt(e.pos, e.quat, e.elternDreh, dt);
        const koerper = e.netze[0].koerper;
        for (const teil of e.netze) {
            const k = teil.koerper;
            for (let j = 0; j < e.b; j++) {
                const g = k.gelenkeRuhe;
                const p = Weichgewebekoerper._anwenden(e.matrizen, 16 * j, g[3 * j], g[3 * j + 1], g[3 * j + 2]);
                e.gelenke[3 * j] = p[0]; e.gelenke[3 * j + 1] = p[1]; e.gelenke[3 * j + 2] = p[2];
            }
            k.takt(e.matrizen, e.gelenke, e.tempo.linear, e.tempo.winkel,
                   e.staerke * teil.anteil);
            // Der Körper (netze[0]) ist fertig, bevor ein Stück gekürzt wird —
            // die Grenze gilt gegen SEINE verformte Lage dieses Bildes.
            if (teil.grenze && e.staerke > 0) {
                teil.grenze.kuerzen(k._lbs, k.zuschlag, koerper._lbs, koerper.zuschlag);
            }
            teil.attribut.needsUpdate = true;
        }
        Weichgewebe._nachfuehren(e, koerper.groesster(), dt);
    }

    /** Die Stärke gedämpft auf den Reglerwert ziehen. */
    static _nachfuehren(e, groesster, dt) {
        if (e.staerke <= 0) {
            e.staerke = Weichgewebe.START_STAERKE_JE_M * e.ziel;
            return;
        }
        e.maxima.push({ t: performance.now() / 1000, m: groesster });
        const grenze = performance.now() / 1000 - Weichgewebe.FENSTER_S;
        while (e.maxima.length && e.maxima[0].t < grenze) e.maxima.shift();
        const max = e.maxima.reduce((a, x) => Math.max(a, x.m), 0);
        if (max < 1e-6) return;
        const soll = e.staerke * e.ziel / max;
        e.staerke += (soll - e.staerke) * Weichgewebe.NACHFUEHRUNG;
        e.staerke = Math.min(e.staerke, 3.0);
    }

    // ------------------------------------------------- Bild fuer Bild

    /**
     * Ein Bild ERZWUNGEN rechnen — für die Aufnahme, ohne Zeitbudget und mit
     * FESTER Stärke. Die Nachführung über `performance.now()` taugt dort
     * nicht: Bild für Bild vergeht Rechenzeit, keine Animationszeit.
     * Gibt den größten Zuschlag des Körpers zurück (Meter).
     */
    static bildErzwingen(inst, dt, staerke) {
        const e = Weichgewebe._figuren.get(inst);
        if (!e) return 0;
        const alt = e.staerke;
        e.staerke = staerke;
        Weichgewebe._bild(e, dt);
        e.staerke = alt;
        return e.netze[0]?.koerper.groesster() || 0;
    }

    /** Vor einer Bild-für-Bild-Folge: Tempo vergessen, Aufbau sicherstellen. */
    static vorbereiten(inst, mm) {
        if (!Weichgewebe._figuren.has(inst)) Weichgewebe.setzen(inst, mm);
        const e = Weichgewebe._figuren.get(inst);
        if (e) { e.ziel = Math.max(0, mm) / 1000; e.tempo.zuruecksetzen(); }
        return !!e;
    }

    static _nullen(e) {
        for (const teil of e.netze) { teil.koerper.zuschlag.fill(0); teil.attribut.needsUpdate = true; }
        e.staerke = 0; e.maxima = [];
    }

    /** Messwerte der gewählten Figur — für Konsole und Tests. */
    static stand(inst) {
        const e = Weichgewebe._figuren.get(inst);
        if (!e) return null;
        const m = e.messung;
        return { ziel_mm: e.ziel * 1000, staerke: e.staerke,
                 groesster_mm: (e.netze[0]?.koerper.groesster() || 0) * 1000,
                 tempo: e.tempo.spitzen(), netze: e.netze.length,
                 stuecke: e.netze.slice(1).map((t) => ({
                     schluessel: t.schluessel, punkte: t.koerper.n,
                     zuschlag_mm: t.koerper.groesster() * 1000,
                     gekuerzt: t.grenze ? t.grenze.gekuerzt : null })),
                 physik_ms: m ? m.ms / Math.max(m.physik, 1) : null,
                 bilder_je_s: m ? m.bilder / ((performance.now() - m.seit) / 1000) : null,
                 physik_je_s: m ? m.physik / ((performance.now() - m.seit) / 1000) : null };
    }
}

// Für Messungen aus der Konsole (`__weichgewebe.stand(__characters[0])`):
// Die Szene lädt als EIN Bündel, die Klasse ist sonst von aussen nicht
// erreichbar — dieselbe Handhabe wie `window.__characters` in `pose_apply.js`.
window.__weichgewebe = Weichgewebe;
