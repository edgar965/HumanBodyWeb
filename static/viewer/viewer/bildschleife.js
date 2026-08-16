/**
 * Bildschleife — die Renderschleife der Viewer-Seite samt Anzeigen.
 *
 * Aus viewer/index.js herausgeloest (Umbau 16.08.2026): 40 Zeilen, in denen
 * drei Dinge zusammenlagen — Animation weiterdrehen, Zeitleiste und
 * Beschriftung nachziehen, Bildrate zaehlen. Das mittlere Stueck rechnete
 * Prozent, Sekunden und Bildnummern in derselben Zeile aus.
 */
export class Bildschleife {

    /** Nach dieser Zeit wird die Bildrate neu angezeigt. */
    static FPS_FENSTER_S = 1.0;

    constructor(state) {
        this.state = state;
        this.bilder = 0;
        this.zeitkonto = 0;
    }

    /** Schleife starten — laeuft bis zum Seitenwechsel. */
    starten() {
        const takt = () => {
            requestAnimationFrame(takt);
            this.schritt();
        };
        requestAnimationFrame(takt);
        return this;
    }

    schritt() {
        const dt = this.state.clock.getDelta();
        this.state.controls.update();
        if (this.state.mixer && this.state.playing) {
            this.state.mixer.update(dt);
            this.zeitanzeige();
        }
        this.state.renderer.render(this.state.scene, this.state.camera);
        this.bildrate(dt);
    }

    /** Zeitleiste und Beschriftung der laufenden Animation. */
    zeitanzeige() {
        const aktion = this.state.currentAction;
        const dauer = this.state.currentAnimDuration;
        if (!aktion || dauer <= 0) return;
        const zeit = aktion.time;

        const leiste = document.getElementById('anim-timeline');
        if (leiste) {
            leiste.value = Math.round(Math.min(100, (zeit / dauer) * 100));
        }
        const beschriftung = document.getElementById('anim-info');
        if (!beschriftung) return;
        const bilder = this.state.currentAnimFrames;
        beschriftung.textContent =
            `${this.state.currentAnimName} — ${Math.floor(zeit)}/`
            + `${Math.floor(dauer)}s  ${Math.round((zeit / dauer) * bilder)}/${bilder}f`;
    }

    /** Bildrate über ein Sekundenfenster mitteln und anzeigen. */
    bildrate(dt) {
        this.bilder++;
        this.zeitkonto += dt;
        if (this.zeitkonto < Bildschleife.FPS_FENSTER_S) return;
        const anzeige = document.getElementById('fps-display');
        if (anzeige) anzeige.textContent = this.bilder;
        this.bilder = 0;
        this.zeitkonto = 0;
    }
}
