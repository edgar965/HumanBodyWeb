import { Dazachsen } from '../gemeinsam/dazachsen.js';
import { Meshfighaltungspose } from './meshfighaltungspose.js';

/**
 * Meshfigurgriff — die Hand, die einen Bestandteil des Netzes hält (Stab), bleibt in der Bewegung im Griff (14.10.2026).
 *
 * Edgar (Zauberer im Tanz): „Zauberstab geht durch die Haut oder ist von der Hand entfernt. Ist nicht durchgängig." Der Lauf sucht die Finger so, dass die Faust den Stab umschließt (`Meshfigurgriff` auf dem Server,
 * `ergebnis.griff.seiten.<l|r>.griff`, Daz-Winkel je Fingerknochen) — in der Haltung des Netzes stimmt das. Die Bewegung (BVH) trägt aber eigene Fingerspuren und überschreibt den Griff: die Hand ist flach, der Stab
 * (starr am Handknochen) hängt davor, und die 8 cm, an denen der Stab im Netz fehlt, weil dort die Faust lag (gemessen am Zauberer: Lücke von 8 cm bei 30 % der Länge), liegen offen.
 *
 * Nach jedem Bild der Bewegung (vor den Gelenkkorrekturen, die die Fingerwinkel mitlesen) setzt diese Klasse die Finger der haltenden Hand auf die Winkel des Griffs zurück. Eine leere Hand (`leer`) und jede Hand
 * ohne übernommenen Griff behalten ihre Bewegung.
 */
export class Meshfigurgriff {

    static FINGER = /_(?:index|mid|ring|pinky|thumb)\d$/;
    static ACHSEN = ['rotation/x', 'rotation/y', 'rotation/z'];

    constructor(buehne) {
        this.buehne = buehne;
        this._achsen = null;        // {skelett, knochen: {name: Eintrag von Dazachsen.vorbereiten} | null (lädt)}
    }

    /** Ein Bild: die Finger der haltenden Hände auf den Griff stellen. */
    takt() {
        const inst = this.buehne.modell;
        const winkel = this._winkel();
        if (!winkel || !inst?.skelett?.skeleton) return;
        const knochen = this._knochen(inst);
        if (!knochen) return;
        for (const [name, grad] of Object.entries(winkel)) {
            const k = knochen[name];
            if (k) Dazachsen.quaternion(k, grad, k.bone.quaternion);
        }
    }

    /** `{fingerknochen: [x, y, z]}` aller Hände, die etwas halten und deren Griff der Lauf übernommen hat — null, wenn es keine gibt. */
    _winkel() {
        const seiten = (((this.buehne._letzter || {}).ergebnis || {}).griff || {}).seiten || {};
        const aus = {};
        for (const seite of Object.values(seiten)) {
            if (!seite || !seite.uebernommen || seite.leer) continue;
            for (const [name, w] of Object.entries(seite.griff || {})) {
                if (Meshfigurgriff.FINGER.test(name)) aus[name] = Meshfigurgriff.ACHSEN.map(a => Number(w[a]) || 0);
            }
        }
        return Object.keys(aus).length ? aus : null;
    }

    /** Die Daz-Achsen der Knochen dieses Skeletts (die Felder der Gelenkkorrekturen tragen sie; einmal geholt) — null, solange sie laden. */
    _knochen(inst) {
        const e = this._achsen;
        if (e && e.skelett === inst.skelett) return e.knochen;
        const neu = { skelett: inst.skelett, knochen: null };
        this._achsen = neu;
        Meshfighaltungspose.achsen(inst).then(achsen => {
            if (achsen && this._achsen === neu) neu.knochen = achsen.knochen;
        });
        return null;
    }
}
