import * as THREE from 'three';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Clipanimation } from '../studio/clipanimation.js';

/**
 * Haarengineanimation — die retargetete BVH-Bewegung LIVE auf dem Genesis-9-Modell der Bühne abspielen.
 *
 * Kein eigenes Video-Fenster: Play, Bild vor/zurück und der Schieber wirken auf der Figur der Hauptbühne (Edgar, 29.09.2026: „ich
 * brauche kein extra Animationsfenster, Play soll im Hauptausgabefenster funktionieren" — Quelle: BlenderModel).
 *
 * KEIN NEUER RETARGET-WEG: `Clipanimation.bauen` ist dieselbe Klasse, die das BVH-Studio für jeden Genesis-9-Clip benutzt
 * (`static/viewer/studio/clipanimation.js`) — sie macht aus den Spuren der `film_bewegung.json` (`tracks`, `position_track`) einen
 * `THREE.AnimationClip` gegen genau die Form `{skeleton, boneByName}`, die `Knochenbau.bauen` liefert und die `Meshfigurbuehne`s
 * `Genesis9Modell` schon als `modell.skelett` mitbringt. Die Bewegung ist zu sehen, sobald der Schritt „film" sie gerechnet hat —
 * auch ohne den Film der Engine.
 *
 * EIGENE RENDERSCHLEIFE: `Meshfigurbuehne` läuft schon per `requestAnimationFrame`; statt sie anzufassen (geteilt mit „Mesh to 3D"),
 * aktualisiert diese Klasse den Mixer in einer eigenen Schleife. Three.js liest die Knochen-Weltmatrizen erst beim Rendern — eine
 * Reihenfolge zwischen den zwei Schleifen ist nicht nötig, im schlechtesten Fall ein Bild (16 ms) Verzug.
 */
export class Haarengineanimation {

    constructor(seite, buehne) {
        this.seite = seite;
        this.buehne = buehne;
        this._z = {};
        this._stand = null;
        this._ziehen = false;
        this.mixer = null;
        this.action = null;
        this.dauer = 0;
        this.fps = 30;
        this.karte = document.getElementById('animations-leiste');
        this.scrubber = document.getElementById('anim-scrubber');
        this.zeit = document.getElementById('anim-zeit');
        this.bildfeld = document.getElementById('anim-bild');
        this.bilder = 0;
        this._uhr = new THREE.Clock();
        this.binden();
        this._takt();
    }

    binden() {
        document.getElementById('anim-play').addEventListener('click', () => this.umschalten());
        document.getElementById('anim-zurueck').addEventListener('click', () => this.bild(-1));
        document.getElementById('anim-vor').addEventListener('click', () => this.bild(1));
        this.scrubber.addEventListener('input', () => this.gezogen());
        this.scrubber.addEventListener('mousedown', () => { this._ziehen = true; });
        this.scrubber.addEventListener('touchstart', () => { this._ziehen = true; }, { passive: true });
        const loslassen = () => { this._ziehen = false; };
        this.scrubber.addEventListener('mouseup', loslassen);
        this.scrubber.addEventListener('touchend', loslassen);
    }

    /** Vom Seitentakt (alle 2 s) gerufen — merkt sich nur den Zustand, das eigentliche Prüfen macht
     *  `_pruefen` in JEDEM Bild (`_takt`). Nötig, weil `Meshfigurbuehne` die Figur ASYNCHRON baut
     *  (gemessen 10–12 s für ein Genesis-9-Modell): Ein bereits „fertiger" Auftrag pollt nach
     *  `verfolgen()` nur EIN einziges Mal nach — ohne den eigenen Takt bliebe die Leiste für immer
     *  versteckt, weil die Figur beim einzigen Nachpoll noch nicht fertig gebaut war. */
    zeigen(z) {
        this._z = z || {};
        this._pruefen();
    }

    /**
     * Neu laden, sobald die Bewegung ODER das Skelett der Bühnenfigur wechselt.
     *
     * NICHT `modell.group.uuid` nehmen (Befund 29.09.2026, „Animation funktioniert nicht" — geprüft
     * mit echten Bone-UUIDs, keine Vermutung): Genesis 9 baut in zwei Zügen (Käfig sofort, die feine
     * Stufe im Hintergrund nach, `Figuraufbaustand`/`modell.fein`) — `skelettBauen` räumt dabei das
     * ALTE Skelett ab und erzeugt KOMPLETT NEUE `THREE.Bone`-Objekte, aber dieselbe `group`. Der
     * Mixer blieb also unsichtbar an den Käfig-Knochen hängen, während die sichtbare Figur längst
     * die neuen der feinen Stufe trägt — `action.time` lief normal, nur an nichts Sichtbarem.
     * `skelett.rootBone.uuid` ändert sich bei jedem `skelettBauen`, auch ohne dass `group` wechselt.
     */
    _pruefen() {
        const film = (this._z.ergebnis || {}).film || {};
        const modell = this.buehne.modell;
        const stand = JSON.stringify([film.bewegung, modell?.skelett?.rootBone?.uuid || null]);
        if (stand === this._stand) return;
        this._stand = stand;
        this._loeschen();
        this.karte.hidden = !(film.bewegung && modell?.skelett);
        if (!film.bewegung || !modell?.skelett) return;
        Serverabruf.json(this.seite.dateiAdresse('ergebnis', film.bewegung))
            .then(daten => this._aufbauen(modell, daten))
            .catch(() => { this.karte.hidden = true; this._stand = null; });
    }

    _aufbauen(modell, daten) {
        if (!daten.tracks || !daten.frame_count) { this.karte.hidden = true; return; }
        Clipanimation.namenEntschaerfen(modell.skelett);
        const clip = Clipanimation.bauen(daten, modell.skelett);
        this.mixer = new THREE.AnimationMixer(modell.group);
        this.action = this.mixer.clipAction(clip);
        this.action.setLoop(THREE.LoopRepeat);
        this.action.play();
        this.action.paused = true;
        this.dauer = clip.duration;
        this.fps = daten.duration ? daten.frame_count / daten.duration : 30;
        this.bilder = daten.frame_count;
        this.mixer.update(0);
        this.knopf(false);
        this.fortschritt();
    }

    _loeschen() {
        if (this.mixer) this.mixer.stopAllAction();
        this.mixer = null;
        this.action = null;
        this.dauer = 0;
    }

    _takt() {
        requestAnimationFrame(() => this._takt());
        this._pruefen();
        const delta = this._uhr.getDelta();
        if (this.mixer && this.action && !this.action.paused) {
            this.mixer.update(delta);
            this.fortschritt();
        }
    }

    // -------------------------------------------------------------- Bedienung

    umschalten() {
        if (!this.action) return;
        this.action.paused = !this.action.paused;
        this.knopf(!this.action.paused);
    }

    knopf(spielt) {
        const icon = document.querySelector('#anim-play i');
        if (icon) icon.className = spielt ? 'fas fa-pause' : 'fas fa-play';
    }

    /** Ein Bild vor (`richtung` 1) oder zurück (-1) — pausiert, aus der Bildrate der Bewegung. */
    bild(richtung) {
        if (!this.action) return;
        this.action.paused = true;
        this.knopf(false);
        const ziel = this.action.time + richtung / this.fps;
        this.action.time = Math.min(Math.max(ziel, 0), this.dauer || ziel);
        this.mixer.update(0);
        this.fortschritt();
    }

    gezogen() {
        if (!this.action || !this.dauer) return;
        this.action.time = (Number(this.scrubber.value) / 1000) * this.dauer;
        this.mixer.update(0);
        this.fortschritt();
    }

    fortschritt() {
        if (!this.action) return;
        if (!this._ziehen && this.dauer) {
            this.scrubber.value = String(Math.round((this.action.time / this.dauer) * 1000));
        }
        this.zeit.textContent =
            `${Haarengineanimation._mmss(this.action.time)} / ${Haarengineanimation._mmss(this.dauer)}`;
        // Edgar, 30.09.2026: aktuelles Bild neben der Sekundenanzeige — Bild 1 … frame_count der Bewegung.
        const bild = Math.min(this.bilder, Math.floor(this.action.time * this.fps + 1e-6) + 1);
        this.bildfeld.textContent = `Bild ${bild} / ${this.bilder}`;
    }

    static _mmss(sekunden) {
        if (!Number.isFinite(sekunden)) return '0:00';
        const s = Math.floor(sekunden % 60).toString().padStart(2, '0');
        return `${Math.floor(sekunden / 60)}:${s}`;
    }
}
