/**
 * Stoffgrenze — hält den Weichgewebe-Zuschlag der Kleidung aus dem Körper.
 *
 * Die JavaScript-Fassung von `TheatreJS/ModelPhysik/stoffgrenze.py`, für
 * das Weichgewebe LIVE in der Szene (11.09.2026). Bis dahin bekam die
 * Kleidung im Browser die HALBE Stärke, weil die Grenze fehlte — mit voller
 * Stärke schob ein 25-mm-Zuschlag das T-Shirt mit 13 mm Hautabstand durch
 * die Haut. Dieselbe Rechnung wie in Python, je Punkt:
 *
 *     aussen     = <stoff − körper', n>         (körper' = Körper + sein Zuschlag)
 *     ist        = aussen − (−<versatz, n>)      (wo der Punkt MIT Zuschlag läge)
 *     soll       = min(Ruheabstand, MINDESTABSTAND)
 *     ist < soll → versatz += (soll − ist) · n
 *
 * Angehoben wird nur ENTLANG DER NORMALE; ein Stück, das seitlich
 * mitschwingt, darf das weiter tun.
 *
 * DER KÖRPER KOMMT AUCH VON INNEN (Edgar, 11.09.2026, mit Bild: „bei einer
 * animation kommt der Körper durch die Kleidung hindurch"). Die erste
 * Fassung kürzte nur den einwärts gerichteten Anteil des STOFFzuschlags;
 * bekam der Körper einen größeren Zuschlag als der Stoff darüber, stand die
 * Haut durch — bei 13 mm Hautabstand (T-Shirt) nie sichtbar, bei einer
 * Leggings auf 2 mm sofort. Gemessen (Dance1, Sprung aus der T-Pose):
 * Körperzuschlag 188 mm, Stoff 109 mm, 6,3 % der Leggingspunkte im Körper.
 * Deshalb der SOLLABSTAND je Punkt aus der Ruhelage: eine Leggings bleibt
 * auf ihren 2 mm, ein T-Shirt wird nicht näher als 6 mm gelassen.
 *
 * EINE NÄHERUNG gegenüber Python, wegen der Bildrate: Welcher Körperpunkt
 * der nächste ist, wird EINMAL in Ruhe bestimmt (`Punktgitter`), nicht je
 * Bild neu. Der Stoff hängt über seine Hautgewichte ohnehin am nächsten
 * Dreieck — Punkt und Körperpunkt bewegen sich gemeinsam (Gleichlauf
 * 13 / 13 / 13 mm, `hbfilm.py`). Die NORMALE dagegen kommt je Bild aus dem
 * verformten Körper: Sie ist es, die beim Gehen ihre Richtung ändert.
 *
 * DIE RICHTUNG KOMMT AUS DEM KÖRPER, nie aus dem Stoff — die Flächennormale
 * eines Schnittteils hängt an seiner Wickelrichtung (viermal im Projekt
 * zugeschlagen, `stoffkorrektur.py`). Ob das Körpernetz nach außen
 * gewickelt ist, wird geprüft, nicht angenommen.
 */
import { Punktgitter } from './punktgitter.js';

export class Stoffgrenze {
    /** Wie in Python: der Kollisionsabstand der Drapierung (6 mm). */
    static MINDESTABSTAND = 0.006;
    /** Tiefer als das muss ein Punkt stecken, um als „im Körper" zu zählen. */
    static TOLERANZ = 0.001;

    /**
     * @param koerperRuhe    Float32Array nK*3, Körper in Ruhe (Netzraum)
     * @param koerperDreiecke Uint16/Uint32Array m*3
     * @param stoffRuhe      Float32Array nS*3, Stoff in Ruhe (derselbe Raum)
     */
    constructor(koerperRuhe, koerperDreiecke, stoffRuhe) {
        this.nK = koerperRuhe.length / 3;
        this.nS = stoffRuhe.length / 3;
        this.dreiecke = koerperDreiecke;
        this.naechster = new Punktgitter(koerperRuhe).alleNaechsten(stoffRuhe);
        this._flaechen();
        this.normalen = new Float64Array(this.benutzt.length * 3);
        this._normalen(koerperRuhe, null);
        this.aussen = this._aussen(koerperRuhe);
        this.soll = this._sollabstand(koerperRuhe, stoffRuhe);
        this.gekuerzt = 0;
    }

    /** Je Stoffpunkt: sein Ruheabstand zur Haut, höchstens MINDESTABSTAND. */
    _sollabstand(koerperRuhe, stoffRuhe) {
        const n = this.normalen, vz = this.aussen, MIN = Stoffgrenze.MINDESTABSTAND;
        const soll = new Float64Array(this.nS).fill(MIN);
        for (let i = 0; i < this.nS; i++) {
            const s = this.platz[i];
            if (s < 0) continue;
            const j = this.benutzt[s];
            const a = (stoffRuhe[3 * i] - koerperRuhe[3 * j]) * vz * n[3 * s]
                + (stoffRuhe[3 * i + 1] - koerperRuhe[3 * j + 1]) * vz * n[3 * s + 1]
                + (stoffRuhe[3 * i + 2] - koerperRuhe[3 * j + 2]) * vz * n[3 * s + 2];
            soll[i] = Math.min(a, MIN);
        }
        return soll;
    }

    /** Die BENUTZTEN Körperpunkte und je Punkt seine Dreiecke (CSR). */
    _flaechen() {
        const platz = new Int32Array(this.nK).fill(-1);
        const benutzt = [];
        this.platz = new Int32Array(this.nS);
        for (let i = 0; i < this.nS; i++) {
            const j = this.naechster[i];
            if (j < 0) { this.platz[i] = -1; continue; }
            if (platz[j] < 0) { platz[j] = benutzt.length; benutzt.push(j); }
            this.platz[i] = platz[j];
        }
        this.benutzt = Int32Array.from(benutzt);
        const anzahl = new Int32Array(benutzt.length + 1);
        const d = this.dreiecke, m = d.length / 3;
        for (let t = 0; t < m; t++) {
            for (let e = 0; e < 3; e++) { const s = platz[d[3 * t + e]]; if (s >= 0) anzahl[s + 1] += 1; }
        }
        for (let s = 0; s < benutzt.length; s++) anzahl[s + 1] += anzahl[s];
        this.flStart = anzahl;
        this.flDreieck = new Int32Array(anzahl[benutzt.length]);
        const fuell = new Int32Array(benutzt.length);
        for (let t = 0; t < m; t++) {
            for (let e = 0; e < 3; e++) {
                const s = platz[d[3 * t + e]];
                if (s >= 0) { this.flDreieck[this.flStart[s] + fuell[s]] = t; fuell[s] += 1; }
            }
        }
    }

    /** Punktnormalen der benutzten Körperpunkte aus dem Körper DIESES Bildes. */
    _normalen(koerper, zuschlag) {
        const d = this.dreiecke, n = this.normalen;
        const px = (i) => koerper[3 * i] + (zuschlag ? zuschlag[3 * i] : 0);
        const py = (i) => koerper[3 * i + 1] + (zuschlag ? zuschlag[3 * i + 1] : 0);
        const pz = (i) => koerper[3 * i + 2] + (zuschlag ? zuschlag[3 * i + 2] : 0);
        for (let s = 0; s < this.benutzt.length; s++) {
            let nx = 0, ny = 0, nz = 0;
            for (let f = this.flStart[s]; f < this.flStart[s + 1]; f++) {
                const t = this.flDreieck[f];
                const a = d[3 * t], b = d[3 * t + 1], c = d[3 * t + 2];
                const ax = px(a), ay = py(a), az = pz(a);
                const bx = px(b) - ax, by = py(b) - ay, bz = pz(b) - az;
                const cx = px(c) - ax, cy = py(c) - ay, cz = pz(c) - az;
                nx += by * cz - bz * cy; ny += bz * cx - bx * cz; nz += bx * cy - by * cx;
            }
            const l = Math.hypot(nx, ny, nz) || 1e-12;
            n[3 * s] = nx / l; n[3 * s + 1] = ny / l; n[3 * s + 2] = nz / l;
        }
    }

    /**
     * +1 oder −1: zeigen die Normalen nach außen? Über das SIGNIERTE
     * VOLUMEN des ganzen Körpers, nicht die Mehrheit gegen die Mitte: Die
     * Mehrheit kippt in manchen Posen (gemessen 11.09.2026 am Server-Weg,
     * der die Grenze je Bild neu baute — der Stoff wurde dann in den Körper
     * GEZOGEN, im Bild lag die Leggings innen). Das Volumen hängt an der
     * Wicklung, und die ändert keine Pose.
     */
    _aussen(koerper) {
        const d = this.dreiecke;
        let vol = 0;
        for (let t = 0; t + 2 < d.length; t += 3) {
            const a = d[t], b = d[t + 1], c = d[t + 2];
            const ax = koerper[3 * a], ay = koerper[3 * a + 1], az = koerper[3 * a + 2];
            const bx = koerper[3 * b], by = koerper[3 * b + 1], bz = koerper[3 * b + 2];
            const cx = koerper[3 * c], cy = koerper[3 * c + 1], cz = koerper[3 * c + 2];
            vol += ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx);
        }
        return vol >= 0 ? 1 : -1;
    }

    /**
     * Den Versatz IN PLACE kürzen. `stoff` sind die LBS-Punkte des Stoffs
     * (vor dem Zuschlag), `koerper` die LBS-Punkte des Körpers und
     * `zuschlag` dessen Zuschlag desselben Bildes (oder null).
     * Gibt die Zahl der gekürzten Punkte zurück.
     */
    kuerzen(stoff, versatz, koerper, zuschlag) {
        this._normalen(koerper, zuschlag);
        const n = this.normalen, soll = this.soll, vz = this.aussen;
        let zahl = 0;
        for (let i = 0; i < this.nS; i++) {
            const s = this.platz[i];
            if (s < 0) continue;
            const j = this.benutzt[s];
            const nx = vz * n[3 * s], ny = vz * n[3 * s + 1], nz = vz * n[3 * s + 2];
            const kx = koerper[3 * j] + (zuschlag ? zuschlag[3 * j] : 0);
            const ky = koerper[3 * j + 1] + (zuschlag ? zuschlag[3 * j + 1] : 0);
            const kz = koerper[3 * j + 2] + (zuschlag ? zuschlag[3 * j + 2] : 0);
            const aussen = (stoff[3 * i] - kx) * nx + (stoff[3 * i + 1] - ky) * ny + (stoff[3 * i + 2] - kz) * nz;
            const nachInnen = -(versatz[3 * i] * nx + versatz[3 * i + 1] * ny + versatz[3 * i + 2] * nz);
            const ist = aussen - nachInnen;
            if (ist < soll[i]) {
                const u = soll[i] - ist;
                versatz[3 * i] += u * nx; versatz[3 * i + 1] += u * ny; versatz[3 * i + 2] += u * nz;
                zahl += 1;
            }
        }
        this.gekuerzt = zahl;
        return zahl;
    }

    /**
     * Anteil der Stoffpunkte IM Körper (Prozent) und die größte Tiefe (mm),
     * mit den Normalen des letzten `kuerzen`-Aufrufs bzw. der Ruhe.
     */
    durchdringung(stoff, koerper, zuschlag) {
        const n = this.normalen, vz = this.aussen;
        let drin = 0, tiefste = 0, gezaehlt = 0;
        for (let i = 0; i < this.nS; i++) {
            const s = this.platz[i];
            if (s < 0) continue;
            const j = this.benutzt[s];
            gezaehlt += 1;
            const kx = koerper[3 * j] + (zuschlag ? zuschlag[3 * j] : 0);
            const ky = koerper[3 * j + 1] + (zuschlag ? zuschlag[3 * j + 1] : 0);
            const kz = koerper[3 * j + 2] + (zuschlag ? zuschlag[3 * j + 2] : 0);
            const aussen = vz * ((stoff[3 * i] - kx) * n[3 * s] + (stoff[3 * i + 1] - ky) * n[3 * s + 1]
                + (stoff[3 * i + 2] - kz) * n[3 * s + 2]);
            if (aussen < -Stoffgrenze.TOLERANZ) { drin += 1; if (-aussen > tiefste) tiefste = -aussen; }
        }
        return { prozent: gezaehlt ? 100 * drin / gezaehlt : 0, tiefe_mm: tiefste * 1000 };
    }
}
