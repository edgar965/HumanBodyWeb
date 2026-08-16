/**
 * BvhSpieler — Video und BVH nebeneinander abspielen (Ergebnisseite).
 *
 * WARUM diese Datei jetzt klein ist (Umbau 16.08.2026): `initBVHPlayer` war
 * EINE Funktion mit 907 Zeilen. Alles darin haing an Closure-Variablen — Szene,
 * Kamera, Mischer, zwei Leinwaende, Abspielzustand, geladene Daten —, weshalb
 * sich kein Stueck herausloesen liess, ohne die Haelfte der Variablen zu
 * verlieren. Als Klasse mit Feldern verteilt sich das auf sieben Module:
 *
 *   bvh_player/skelettformate.js     MocapNET- und SMPL-Tabellen, Erkennung
 *   bvh_player/abspielzustand.js     Zeit, Tempo, Ersatzuhr, Sichtbarkeit
 *   bvh_player/szene.js              Three.js-Ansicht und Knochennummern
 *   bvh_player/skelett.js            BVH laden, Linien, Bewegung
 *   bvh_player/spielerdaten.js       2D-Keypoints und Erkennungsmarken
 *   bvh_player/videoueberlagerung.js 2D-Skelett auf dem Video
 *   bvh_player/vergleichstafel.js    dritte Spalte: 2D gegen 3D
 *   bvh_player/bedienung.js          Knoepfe, Tastatur, Zeitleiste
 */
import { Abspielzustand } from './bvh_player/abspielzustand.js';
import { Spielerszene } from './bvh_player/szene.js';
import { Spielerskelett } from './bvh_player/skelett.js';
import { Spielerdaten } from './bvh_player/spielerdaten.js';
import { Videoueberlagerung } from './bvh_player/videoueberlagerung.js';
import { Vergleichstafel } from './bvh_player/vergleichstafel.js';
import { Spielerbedienung } from './bvh_player/bedienung.js';

console.log('[bvh_player] v0.89 loaded (Klassen, 3-Spalten-Ansicht)');

export class BvhSpieler {
    constructor(video, behaelter, fps) {
        this.video = video;
        this.fps = fps;
        this.zustand = new Abspielzustand(video);
        this.szene = new Spielerszene(behaelter);
        this.skelett = new Spielerskelett(this.szene);
        this.daten = new Spielerdaten();
        this.tafel = new Vergleichstafel();
        this.ueberlagerung = null;
        this.bedienung = new Spielerbedienung(this);
    }

    /** Knochennummern ein- oder ausschalten. Gibt den neuen Stand zurueck. */
    nummernUmschalten() {
        this.szene.nummernZeigen = !this.szene.nummernZeigen;
        console.log('[bvh_player] Bone labels:',
                    this.szene.nummernZeigen ? 'ON' : 'OFF');
        return this.szene.nummernZeigen;
    }

    async starten({ bvhUrl, overlayId, detectionUrl, keypointsUrl }) {
        this.bedienung.anbinden();
        this.daten = await Spielerdaten.laden(keypointsUrl, detectionUrl);
        this.ueberlagerung = new Videoueberlagerung(
            overlayId ? document.getElementById(overlayId) : null,
            this.video, this.daten);
        this._groesseUeberwachen();
        this._schleife();

        try {
            this.zustand.klipdauer = await this.skelett.laden(bvhUrl);
            this.bedienung.dauerUebernehmen();
            console.log('[bvh_player] Ready, clip duration:',
                        this.zustand.klipdauer.toFixed(1) + 's');
        } catch (e) {
            console.error('[bvh_player] BVH load error:', e);
            this.szene.fehler('Failed to load BVH file');
        }
    }

    _schleife() {
        const bild = (stempel) => {
            requestAnimationFrame(bild);
            this.zustand.takt(stempel);
            // Die Ergebnisseite liest den Stand mit.
            window.bvhPlayerProgress = this.zustand.fortschritt;
            window.bvhPlayerDuration = this.zustand.dauer;

            this._skelettStellen();
            this.szene.zeichnen();
            this.szene.nummernZeichnen(this.skelett);
            this.ueberlagerung?.zeichnen(this.zustand, this.skelett.format,
                                         this.szene.nummernZeigen);
            if (this.tafel.aktiv) {
                this.tafel.auffrischen(this.zustand, this.skelett,
                                       this.daten, this.fps);
            }
            this.bedienung.standAnzeigen(this.skelett, this.daten, this.fps);
        };
        bild(0);
    }

    /**
     * Skelett auf den aktuellen Zeitpunkt stellen und entscheiden, ob es zu
     * sehen ist: nicht vor dem ersten Abspielen, nicht hinter dem Klipende und
     * nicht in Abschnitten ohne erkannte Person.
     */
    _skelettStellen() {
        if (!this.skelett.mischer || this.skelett.klipdauer <= 0) return;
        const imKlip = this.skelett.zeitSetzen(
            this.zustand.fortschritt * this.skelett.klipdauer);
        const sichtbar = this.zustand.sichtbar && imKlip
            && (!this.zustand.videoBrauchbar
                || this.daten.erkanntBei(this.zustand.fortschritt));
        this.skelett.sichtbarkeit(sichtbar);
    }

    _groesseUeberwachen() {
        const anpassen = () => {
            this.szene.groesseAnpassen();
            this.ueberlagerung?.groesseAnpassen();
        };
        window.addEventListener('resize', anpassen);
        if (typeof ResizeObserver === 'undefined') return;
        new ResizeObserver(anpassen).observe(this.szene.behaelter);
        if (this.ueberlagerung?.behaelter) {
            new ResizeObserver(anpassen).observe(this.ueberlagerung.behaelter);
        }
    }
}

export function initBVHPlayer({ videoId, canvasId, bvhUrl, fps = 30,
                                overlayId = null, detectionUrl = null,
                                keypointsUrl = null }) {
    console.log('[bvh_player] initBVHPlayer called', { videoId, canvasId });
    const video = document.getElementById(videoId);
    const behaelter = document.getElementById(canvasId);
    if (!video || !behaelter) {
        console.error('[bvh_player] Missing elements:',
                      { video: !!video, container: !!behaelter });
        return null;
    }
    const spieler = new BvhSpieler(video, behaelter, fps);
    // Die Ergebnisseite schaltet die Ueberlagerung ueber diesen Haken.
    window.setBvhOverlayVisible = (sichtbar) => {
        spieler.zustand.erzwungen = sichtbar;
        if (sichtbar) spieler.zustand.zeigen = true;
    };
    spieler.starten({ bvhUrl, overlayId, detectionUrl, keypointsUrl });
    return spieler;
}
