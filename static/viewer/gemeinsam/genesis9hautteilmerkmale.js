import * as THREE from 'three';
import { Genesis9hautebenenwerte } from './genesis9hautebenenwerte.js';

/**
 * Genesis9hautteilmerkmale — die Hautebenen JE KÖRPERTEIL (26.10.2026, Edgar: „mach 1 und 2: Die Hautebenen je Körperteil ausbauen und auch neue Hautmerkmale (Narben,
 * Muttermale usw.), die gibt es schon an anderen Stellen im Projekt“). Die Merkmale sind die der ganzen Figur (`Genesis9hautebenenwerte.FELDER`: Hautton … Muttermale, Pickel,
 * Cellulite, Aknenarben); hier bekommt jedes Ziel von `Genesis9hautteile.ZIELE` einen ZUSCHLAG auf den Wert der ganzen Figur.
 *
 * WERTE in `inst.hautebenen` wie Hautfarbe und Tattoo (`Genesis9hautteile.schluessel`): `eigen_merkmal_<ziel>` = Stärke % (Vorgabe 100, wirkt auf alle Merkmale des Ziels),
 * `eigen_merkmal_<ziel>_<merkmal>` = Zuschlag in Prozentpunkten wie der Regler der ganzen Figur. „beide“ und die Seite addieren sich; „gesamt“ fehlt (das sind die Hautregler).
 * SHADER: je Kanal der Teilkarte 20 Werte (`uHtTeilE`, 24 × 5 vec4), gewichtet mit den Anteilen des Texels zu `htTe[5]` (`Genesis9hautteileGLSL.LESEN`); die Uniforms der
 * Hautebenen werden im Farbblock damit ÜBERDECKT (`SCHATTEN`), der Code der Ebenen bleibt. Was sonst an ein Gebiet gebunden ist (Sommersprossen und Altersflecken an die
 * Gebietskarte, Pickel an Gesicht und oberen Rücken, Cellulite an Hüfte/Oberschenkel, Aknenarben an den Kopf), wirkt mit dem Zuschlag auf dem GANZEN Teil.
 */
export class Genesis9hautteilmerkmale {

    /** Reihenfolge = Platz im Shader (`htTe[i >> 2][i & 3]`). */
    static MERKMALE = ['ton', 'roetung', 'farbton', 'oliv', 'saettigung', 'helligkeit', 'struktur', 'teint', 'adern', 'sommer', 'altersflecken', 'pigment',
                       'vitiligo', 'muttermale', 'pickel', 'cellulite', 'narben'];
    static JE_KANAL = 5;           // vec4 je Kanal (20 Plätze, 17 belegt)
    static KANAELE = 24;
    static ART = 'merkmal';

    /** Die Felder des Fensters: Stärke, dann je Merkmal Titel und Bereich wie der Regler der ganzen Figur. */
    static felder() {
        const quelle = Object.fromEntries(Genesis9hautebenenwerte.FELDER.map(f => [f.name, f]));
        return [{ feld: '', titel: 'Stärke (alle Merkmale)', typ: 'bereich', min: 0, max: 100, einheit: '%' },
            ...Genesis9hautteilmerkmale.MERKMALE.map(n => ({ feld: n, titel: quelle[n]?.titel || n, typ: 'bereich', min: quelle[n]?.min < 0 ? -100 : 0, max: 100, einheit: '%',
                                                            hilfe: quelle[n]?.hilfe || '' }))];
    }

    static vorgabe() {
        return { '': 100, ...Object.fromEntries(Genesis9hautteilmerkmale.MERKMALE.map(n => [n, 0])) };
    }

    static uniforms() {
        const n = Genesis9hautteilmerkmale.KANAELE * Genesis9hautteilmerkmale.JE_KANAL;
        return { uHtTeilE: { value: Array.from({ length: n }, () => new THREE.Vector4()) }, uHtTeilEAn: { value: 0 } };
    }

    /**
     * → `{an, werte: Float32Array(24 × 20)}`: je Kanal die Summe der Zuschläge aller Ziele, die ihn enthalten (Anteil 0…1 bzw. −1…1 wie `Genesis9hautebenenwerte.wirksam`).
     * `wert(art, ziel, feld)` und `teile` kommen aus `Genesis9hautteile` (kein Ring der Module).
     */
    static rechnen(ziele, teile, wert) {
        const breit = 4 * Genesis9hautteilmerkmale.JE_KANAL;
        const werte = new Float32Array(Genesis9hautteilmerkmale.KANAELE * breit);
        let an = false;
        for (const z of ziele) {
            if (z.ganz) continue;
            const staerke = wert(Genesis9hautteilmerkmale.ART, z.ziel, '') / 100;
            if (!(staerke > 0)) continue;
            Genesis9hautteilmerkmale.MERKMALE.forEach((n, i) => {
                const v = staerke * wert(Genesis9hautteilmerkmale.ART, z.ziel, n) / 100;
                if (!v) return;
                an = true;
                for (const teil of z.teile) werte[teile.indexOf(teil) * breit + i] += v;
            });
        }
        return { an, werte };
    }

    static eintragen(u, rechnung) {
        if (!u.uHtTeilE) return;
        u.uHtTeilEAn.value = rechnung.an ? 1 : 0;
        const w = rechnung.werte;
        u.uHtTeilE.value.forEach((v, k) => v.set(w[4 * k], w[4 * k + 1], w[4 * k + 2], w[4 * k + 3]));
    }
}
