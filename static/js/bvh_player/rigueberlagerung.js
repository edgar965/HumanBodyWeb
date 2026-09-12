/**
 * Rigueberlagerung — das HumanBody-Rig (DEF, 176 Knochen) auf dem Video.
 *
 * Das Video kennt nur 2D-Gelenke (`Spielerdaten`), das Rig nur Weltlagen im
 * Skelettfenster. Zwischen beiden liegt keine Kamera, die das Rig exakt ins
 * Bild rechnet — die Wurzel des Retargets steht normiert im Ursprung
 * (`Ruhelage`), und nicht jede Pipeline bringt eine Kamera mit. Deshalb wird
 * je Bild eine ÄHNLICHKEIT (Maßstab + Verschiebung, keine Drehung) zwischen
 * den Körpergelenken des Rigs (x, -y der Weltlage) und den erkannten
 * 2D-Gelenken gerechnet — kleinste Quadrate, geschlossen lösbar — und das
 * ganze Rig damit gezeichnet. Hände, Füße und Gesicht liegen dann dort, wo
 * der Körper sie trägt; was am Körper daneben liegt, liegt auch hier daneben.
 * Weniger als drei erkannte Gelenkpaare: nichts zeichnen, nicht raten.
 */
import * as THREE from 'three';
import { GELENKPAARE } from './humanbodyrig.js';
import { Aehnlichkeit } from './aehnlichkeit.js';

/** Ab welcher Zuverlässigkeit ein 2D-Gelenk in die Rechnung eingeht. */
const MINDESTGUETE = 0.3;

export class Rigueberlagerung {
    static FARBE_KOERPER = '#16c784';
    static FARBE_FEINTEILE = '#f59e0b';

    /**
     * Ähnlichkeit Rig → Bild aus den Gelenkpaaren, oder null.
     * @returns {{s: number, tx: number, ty: number, paare: number}|null}
     */
    static anpassung(rig, bild, bereich) {
        const { rw, rh, ox, oy } = bereich;
        const p = [], q = [];
        const welt = new THREE.Vector3();
        for (const [def, namen] of GELENKPAARE) {
            const name = namen.find(n => bild[n]);
            const kp = name ? bild[name] : null;
            if (!kp || kp[2] <= MINDESTGUETE) continue;
            if (!rig.position(def, welt)) continue;
            p.push([welt.x, -welt.y]);
            q.push([kp[0] * rw + ox, kp[1] * rh + oy]);
        }
        return Aehnlichkeit.anpassen(p, q);
    }

    /** Das Rig mit der Anpassung auf die Leinwand zeichnen. */
    static zeichnen(stift, rig, bild, bereich) {
        const fit = Rigueberlagerung.anpassung(rig, bild, bereich);
        if (!fit) return false;
        stift.lineWidth = 1.5;
        stift.lineCap = 'round';
        for (const [a, b, fein] of rig.weltlinien()) {
            stift.strokeStyle = fein ? Rigueberlagerung.FARBE_FEINTEILE
                                     : Rigueberlagerung.FARBE_KOERPER;
            stift.beginPath();
            stift.moveTo(fit.s * a.x + fit.tx, -fit.s * a.y + fit.ty);
            stift.lineTo(fit.s * b.x + fit.tx, -fit.s * b.y + fit.ty);
            stift.stroke();
        }
        return true;
    }
}
