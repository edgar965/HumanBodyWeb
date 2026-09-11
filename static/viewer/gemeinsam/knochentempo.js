/**
 * Knochentempo — Geschwindigkeit je Knochen, exponentiell geglättet.
 *
 * Spiegelt `VelocitySkinning_Python/knochentempo.py` und damit
 * `velocity_tracker.cpp` samt `skinning.cpp` Zeile 279–290:
 *
 *     lokale Aenderung des Knochens gegen sein Elternteil   -> Tempo
 *     Weltdrehung DES ELTERNTEILS                          -> in den Raum
 *
 * Nicht die Weltgeschwindigkeit des Knochens: Die Bewegung der Kette kommt
 * über die Ahnengewichte herein (`weichgewebekoerper.js`); wer hier die
 * Weltgeschwindigkeit nähme, zählte sie doppelt.
 *
 * Eingabe je Bild sind flache Felder — die Three.js-Seite (`scene/
 * weichgewebe.js`) füllt sie aus `bone.position`, `bone.quaternion` und
 * der Weltdrehung des Elternteils.
 */
export class Knochentempo {
    /** `velocity_tracker.hpp` Zeile 28. */
    static GLAETTUNG = 0.75;

    constructor(b) {
        this.b = b;
        this.letztePos = new Float64Array(b * 3);
        this.letzteQuat = new Float64Array(b * 4);
        this.mittelV = new Float64Array(b * 3);
        this.mittelW = new Float64Array(b * 3);
        this.linear = new Float64Array(b * 3);
        this.winkel = new Float64Array(b * 3);
        this.bereit = false;
    }

    /** Alles vergessen — nach einem Sprung in der Animation. Ohne das
     *  erzeugt ein Neustart bei Bild 0 einen Geschwindigkeitsausschlag aus
     *  der Differenz „letztes Bild → erstes Bild". */
    zuruecksetzen() { this.bereit = false; this.mittelV.fill(0); this.mittelW.fill(0); }

    /**
     * @param pos     Float64Array b*3, lokale Position je Knochen
     * @param quat    Float64Array b*4, lokale Drehung [x,y,z,w]
     * @param eltern  Float64Array b*9, Weltdrehung des ELTERNTEILS als 3x3
     *                zeilenweise (Einheit für die Wurzel)
     * @param dt      Sekunden seit dem letzten Bild
     */
    takt(pos, quat, eltern, dt) {
        const a = Knochentempo.GLAETTUNG;
        const b = this.b;
        if (!this.bereit || dt <= 0) {
            this.letztePos.set(pos);
            this.letzteQuat.set(quat);
            this.bereit = true;
            this.linear.fill(0);
            this.winkel.fill(0);
            return;
        }
        for (let k = 0; k < b; k++) {
            // Lineares Tempo aus der lokalen Positionsdifferenz.
            const vx = (pos[3 * k] - this.letztePos[3 * k]) / dt;
            const vy = (pos[3 * k + 1] - this.letztePos[3 * k + 1]) / dt;
            const vz = (pos[3 * k + 2] - this.letztePos[3 * k + 2]) / dt;
            this.mittelV[3 * k] = a * this.mittelV[3 * k] + (1 - a) * vx;
            this.mittelV[3 * k + 1] = a * this.mittelV[3 * k + 1] + (1 - a) * vy;
            this.mittelV[3 * k + 2] = a * this.mittelV[3 * k + 2] + (1 - a) * vz;
            // Winkeltempo: q = neu * konj(alt), Achse mal Winkel je Sekunde.
            const w = Knochentempo._winkeltempo(this.letzteQuat, quat, k, dt);
            this.mittelW[3 * k] = a * this.mittelW[3 * k] + (1 - a) * w[0];
            this.mittelW[3 * k + 1] = a * this.mittelW[3 * k + 1] + (1 - a) * w[1];
            this.mittelW[3 * k + 2] = a * this.mittelW[3 * k + 2] + (1 - a) * w[2];
            // In den Raum drehen — mit der Drehung des ELTERNTEILS.
            const o = 9 * k;
            for (let r = 0; r < 3; r++) {
                this.linear[3 * k + r] = eltern[o + 3 * r] * this.mittelV[3 * k]
                    + eltern[o + 3 * r + 1] * this.mittelV[3 * k + 1]
                    + eltern[o + 3 * r + 2] * this.mittelV[3 * k + 2];
                this.winkel[3 * k + r] = eltern[o + 3 * r] * this.mittelW[3 * k]
                    + eltern[o + 3 * r + 1] * this.mittelW[3 * k + 1]
                    + eltern[o + 3 * r + 2] * this.mittelW[3 * k + 2];
            }
        }
        this.letztePos.set(pos);
        this.letzteQuat.set(quat);
    }

    /** `quaternion_to_axis_angle` mit `2*atan2(|sin|, w)` und kürzerem Weg. */
    static _winkeltempo(alt, neu, k, dt) {
        const ax = alt[4 * k], ay = alt[4 * k + 1], az = alt[4 * k + 2], aw = alt[4 * k + 3];
        const bx = neu[4 * k], by = neu[4 * k + 1], bz = neu[4 * k + 2], bw = neu[4 * k + 3];
        // q = neu * konj(alt); konj(alt) = (-ax, -ay, -az, aw)
        const cx = -ax, cy = -ay, cz = -az, cw = aw;
        const qx = bw * cx + bx * cw + by * cz - bz * cy;
        const qy = bw * cy - bx * cz + by * cw + bz * cx;
        const qz = bw * cz + bx * cy - by * cx + bz * cw;
        const qw = bw * cw - bx * cx - by * cy - bz * cz;
        const s = Math.hypot(qx, qy, qz);
        if (s < 1e-6) return [0, 0, 0];
        let winkel = 2 * Math.atan2(s, qw);
        if (winkel > Math.PI) winkel -= 2 * Math.PI;
        const f = winkel / (s * dt);
        return [qx * f, qy * f, qz * f];
    }

    /** Größtes lineares und Winkeltempo — die Probe, dass etwas anliegt. */
    spitzen() {
        let v = 0, w = 0;
        for (let k = 0; k < this.b; k++) {
            v = Math.max(v, Math.hypot(this.linear[3 * k], this.linear[3 * k + 1], this.linear[3 * k + 2]));
            w = Math.max(w, Math.hypot(this.winkel[3 * k], this.winkel[3 * k + 1], this.winkel[3 * k + 2]));
        }
        return { linear: v, winkel: w };
    }
}
