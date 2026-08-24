import * as THREE from 'three';

/**
 * Buehnenschleife — die Bildschleife des Theatre-Studios.
 *
 * Herausgelöst aus `main.js` (788 Zeilen). Sie tut je Bild vier Dinge, und
 * zwei davon sind nicht offensichtlich:
 *
 * 1. **Die Animation weiterdrehen** — mit dem Tempo des Abspielers, und am
 *    Ende zurück auf 0 (die Bühne läuft in Schleife).
 * 2. **Das Licht seinem Symbol nachziehen.** Gezogen wird das SYMBOL (nur das
 *    ist anklickbar); die Lichtquelle selbst muss hinterher.
 * 3. `controls.update()`.
 * 4. **`SkinnedMesh` ohne Skelett kurz ausblenden.** Three.js wirft beim
 *    Zeichnen, wenn die Bindung fehlt — das passiert im Moment zwischen
 *    „Netz da" und „Skelett gebunden". Nach dem Zeichnen werden sie sofort
 *    wieder sichtbar gemacht, sonst blieben sie für immer unsichtbar.
 */
export class Buehnenschleife {

    /**
     * @param {Object} bild   { scene, camera, renderer, controls }
     * @param {Object} teile  { animationslauf, abspieler, auswahl }
     */
    constructor(bild, teile) {
        Object.assign(this, bild, teile);
        this.uhr = new THREE.Clock();
    }

    starten() {
        const schritt = () => {
            requestAnimationFrame(schritt);
            this.bild();
        };
        schritt();
        return this;
    }

    bild() {
        this._animation(this.uhr.getDelta());
        this._lichtNachziehen();
        this.controls.update();
        this.zeichnen();
    }

    _animation(dauer) {
        const lauf = this.animationslauf;
        if (!lauf.mixer || !this.abspieler.laeuft) return;
        lauf.mixer.update(dauer * this.abspieler.tempo);
        if (lauf.aktion && lauf.aktion.time >= this.abspieler.dauer) {
            lauf.aktion.time = 0;
        }
        this.abspieler.zeitVerfolgen();
    }

    _lichtNachziehen() {
        const licht = this.auswahl.licht();
        if (!licht) return;
        licht.position.copy(this.auswahl.lichtsymbol.position);
        this.auswahl.lichtsymbol.lookAt(licht.target.position);
    }

    /** Ein Bild zeichnen — auch von außen aufrufbar (Server-Rendering). */
    zeichnen() {
        const versteckt = [];
        this.scene.traverse(teil => {
            if (teil.isSkinnedMesh && !teil.skeleton) {
                teil.visible = false;
                versteckt.push(teil);
            }
        });
        this.renderer.render(this.scene, this.camera);
        for (const teil of versteckt) teil.visible = true;
    }
}
