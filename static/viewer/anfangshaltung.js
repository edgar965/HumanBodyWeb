/**
 * Anfangshaltung — das Skelett in die Haltung von Bild 0 bringen.
 *
 * WARUM ÜBERHAUPT (stand schon vorher so im Code): Für die Zentrierung muss
 * das Skelett stehen, wie es im ersten Bild steht. Bandai braucht dafür die
 * Drehungen (sonst hängt die Figur in der Rest-Pose), MocapNET und SMPL die
 * Positionen (sonst sitzt sie um die Z/Y-Verschiebung daneben).
 *
 * WARUM EIGENE KLASSE (31.08.2026): `placeBvhSkeleton()` war mit 92 Zeilen
 * über die Faustregel gewachsen und tat drei Dinge — Haltung setzen, Höhe
 * messen, Anzeige bauen. Das erste ist der grösste und verwickeltste Teil;
 * er steht jetzt für sich.
 *
 * KEINE THREE-ABHÄNGIGKEIT: Die Klasse ruft nur `quaternion.set`,
 * `position.set` und `position.copy` — dieselben Aufrufe wie vorher. Damit
 * lässt sie sich mit Attrappen prüfen, ohne eine Szene aufzubauen.
 */

export class Anfangshaltung {
    /**
     * @param {Array} knochen Knochenliste des Skeletts
     * @param {object} klip   Die Animation (`{tracks: […]}`) oder null
     */
    constructor(knochen, klip) {
        this.knochen = knochen || [];
        this.klip = klip;
        this.spuren = null;
    }

    /**
     * Setzt Bild 0 auf die Knochen und backt den Bandai-Sonderfall ein.
     *
     * @param {string} art       Kennung des Formats (`bandai`, `cmu`, …)
     * @param {object} wurzel    Der Wurzelknochen
     * @returns {boolean} Wurde etwas gesetzt?
     */
    anwenden(art, wurzel) {
        if (!this.klip || !this.klip.tracks || this.klip.tracks.length === 0) {
            return false;
        }
        this.spuren = Anfangshaltung.spurenJeKnochen(this.klip.tracks);
        this._bildNullSetzen();
        if (art === 'bandai') this._bandaiEinbacken(wurzel);
        return true;
    }

    /**
     * `{Knochenname: {quaternion: Spur, position: Spur}}`.
     *
     * Der Spurname ist `<Knochen>.<Eigenschaft>`; getrennt wird am ERSTEN
     * Punkt, weil Knochennamen selbst keinen enthalten (DEF-Namen schon —
     * die kommen hier aber nicht vor).
     *
     * @param {Array} spuren Die Spuren der Animation
     */
    static spurenJeKnochen(spuren) {
        const raus = {};
        for (const spur of spuren) {
            const punkt = spur.name.indexOf('.');
            if (punkt < 0) continue;
            const knochen = spur.name.substring(0, punkt);
            const eigenschaft = spur.name.substring(punkt + 1);
            if (!raus[knochen]) raus[knochen] = {};
            raus[knochen][eigenschaft] = spur;
        }
        return raus;
    }

    /** `{Name: Knochen}` — für den Zugriff aus den Spurnamen. */
    _nachNamen() {
        const raus = {};
        for (const k of this.knochen) raus[k.name] = k;
        return raus;
    }

    /** Die ersten vier bzw. drei Werte jeder Spur auf ihren Knochen. */
    _bildNullSetzen() {
        const nachNamen = this._nachNamen();
        for (const [name, spuren] of Object.entries(this.spuren)) {
            const knochen = nachNamen[name];
            if (!knochen) continue;
            const dreh = spuren.quaternion;
            if (dreh && dreh.values.length >= 4) {
                const v = dreh.values;
                knochen.quaternion.set(v[0], v[1], v[2], v[3]);
            }
            const ort = spuren.position;
            if (ort && ort.values.length >= 3) {
                const v = ort.values;
                knochen.position.set(v[0], v[1], v[2]);
            }
        }
    }

    /**
     * Bandai: `joint_Root` → `Hips` zusammenlegen.
     *
     * Bandai führt die Wurzelbewegung an `Hips` statt an `joint_Root`. Ohne
     * diesen Schritt bewegt sich die Figur doppelt — einmal über die Wurzel,
     * einmal über die Hüfte.
     *
     * ES WIRD IN DEN SPURWERTEN GESCHRIEBEN, nicht nur an den Knochen: Die
     * Bewegung muss über die ganze Animation umziehen, nicht nur im ersten
     * Bild.
     *
     * @param {object} wurzel Der Wurzelknochen
     */
    _bandaiEinbacken(wurzel) {
        const hueften = this._nachNamen()['Hips'];
        if (!hueften || hueften.parent !== wurzel) return;
        const wurzelOrt = this.spuren['joint_Root']?.position;
        const hueftOrt = this.spuren['Hips']?.position;
        if (wurzelOrt && hueftOrt) {
            const anzahl = Math.min(wurzelOrt.values.length,
                                    hueftOrt.values.length);
            for (let i = 0; i < anzahl; i++) {
                wurzelOrt.values[i] = hueftOrt.values[i];
            }
            for (let i = 0; i < hueftOrt.values.length; i++) {
                hueftOrt.values[i] = 0;
            }
        }
        wurzel.position.copy(hueften.position);
        hueften.position.set(0, 0, 0);
    }
}
