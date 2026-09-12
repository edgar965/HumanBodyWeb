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
 *   bvh_player/humanbodyrig.js       das umgezielte DEF-Rig (Haende, Fuesse, Gesicht)
 *   bvh_player/rigueberlagerung.js   dasselbe Rig auf dem Video
 *   bvh_player/rigstart.js           das Rig beim Seitenstart, Clip von der Figur
 */
import { Abspielzustand } from './bvh_player/abspielzustand.js';
import { Spielerszene } from './bvh_player/szene.js';
import { Spielerskelett } from './bvh_player/skelett.js';
import { Spielerdaten } from './bvh_player/spielerdaten.js';
import { Videoueberlagerung } from './bvh_player/videoueberlagerung.js';
import { Vergleichstafel } from './bvh_player/vergleichstafel.js';
import { Spielerbedienung } from './bvh_player/bedienung.js';
import { Rigstart } from './bvh_player/rigstart.js';
import { Protokoll } from '../viewer/gemeinsam/protokoll.js';

Protokoll.debug('bvh_player', 'v0.89 loaded (Klassen, 3-Spalten-Ansicht)');

export class BvhSpieler {
    constructor(video, behaelter, fps, jobId = null) {
        this.video = video;
        this.fps = fps;
        this.jobId = jobId;
        /** Das HumanBody-Rig — gebaut beim ersten Einschalten. */
        this.rig = null;
        this.rigGewuenscht = false;
        this.zustand = new Abspielzustand(video);
        this.szene = new Spielerszene(behaelter);
        this.skelett = new Spielerskelett(this.szene);
        this.daten = new Spielerdaten();
        this.tafel = new Vergleichstafel();
        this.ueberlagerung = null;
        this.bedienung = new Spielerbedienung(this);
        this.rigstart = new Rigstart(this);
    }

    /** Knochennummern ein- oder ausschalten. Gibt den neuen Stand zurueck. */
    nummernUmschalten() {
        this.szene.nummernZeigen = !this.szene.nummernZeigen;
        Protokoll.debug('bvh_player', 'Bone labels:',
                    this.szene.nummernZeigen ? 'ON' : 'OFF');
        return this.szene.nummernZeigen;
    }

    /**
     * HumanBody-Rig ein- oder ausschalten (12.09.2026, Edgar: „kannst du das
     * HumanBody Rig anzeigen auf allen views?"). Beim ersten Einschalten wird
     * es gebaut und der Clip geholt; solange bleibt der Knopf ohne Wirkung.
     * Gibt den neuen Stand zurueck.
     */
    async rigUmschalten() {
        this.rigGewuenscht = !this.rigGewuenscht;
        if (this.rigGewuenscht && !this.rig && this.jobId && this.skelett.wurzel) {
            // Gebaut wird es seit dem Seitenstart (`Rigstart`); hier nur abholen.
            const rig = await this.rigstart.rig();
            this.rig = rig;
            if (this.ueberlagerung) this.ueberlagerung.rig = rig;
            if (!rig) this.rigGewuenscht = false;
        }
        // Die 3D-Figur schaltet ihr Rig mit — dieselbe Ansicht, derselbe Knopfstand.
        if (typeof window.setCharacterRigVisible === 'function') {
            window.setCharacterRigVisible(this.rigGewuenscht);
        }
        return this.rigGewuenscht;
    }

    /**
     * Das HumanBody-Rig ist die VORGABE, nicht der Knopf (Edgar, 12.09.2026,
     * zum dritten Mal: „oben ist ein anderes Rig zu sehen als unten"). Bis
     * der Clip da ist, zeigt das Fenster das BVH-Skelett; der Knopf steht
     * danach auf an und schaltet zurueck auf das rohe BVH.
     */
    async rigVorgeben() {
        if (this.rigGewuenscht || !this.jobId) return false;
        await this.rigUmschalten();
        this.bedienung.rigStandZeigen(this.rigGewuenscht);
        return this.rigGewuenscht;
    }

    async starten({ bvhUrl, overlayId, detectionUrl, keypointsUrl }) {
        this.bedienung.anbinden();
        this.rigstart.beginnen();               // sofort, parallel zur BVH-Datei
        this.daten = await Spielerdaten.laden(keypointsUrl, detectionUrl);
        this.ueberlagerung = new Videoueberlagerung(
            overlayId ? document.getElementById(overlayId) : null,
            this.video, this.daten);
        this._groesseUeberwachen();
        this._schleife();

        try {
            this.zustand.klipdauer = await this.skelett.laden(bvhUrl);
            this.bedienung.dauerUebernehmen();
            Protokoll.debug('bvh_player', 'Ready, clip duration:',
                        this.zustand.klipdauer.toFixed(1) + 's');
            await this.rigVorgeben();
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
        // Mit dem HumanBody-Rig weichen die Koerperlinien des BVH — zwei
        // Skelette uebereinander waeren nicht zu lesen.
        // Und solange das Rig noch kommt, gar kein Skelett — sonst startet
        // Play mit dem „anderen Rig" (Edgar, 12.09.2026).
        const rigAn = this.rigGewuenscht && !!this.rig;
        this.skelett.sichtbarkeit(sichtbar && !rigAn && !this.rigstart.ausstehend);
        if (this.rig) {
            const imRig = this.rig.zeitSetzen(
                this.zustand.fortschritt * this.rig.klipdauer);
            this.rig.sichtbarkeit(sichtbar && rigAn && imRig);
        }
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
                                keypointsUrl = null, jobId = null }) {
    Protokoll.debug('bvh_player', 'initBVHPlayer called', { videoId, canvasId });
    const video = document.getElementById(videoId);
    const behaelter = document.getElementById(canvasId);
    if (!video || !behaelter) {
        console.error('[bvh_player] Missing elements:',
                      { video: !!video, container: !!behaelter });
        return null;
    }
    const spieler = new BvhSpieler(video, behaelter, fps, jobId);
    // Fuer Pruefungen von aussen (Konsole, Testlauf): der laufende Spieler.
    window.__bvhSpieler = spieler;
    // Die Ergebnisseite schaltet die Ueberlagerung ueber diesen Haken.
    window.setBvhOverlayVisible = (sichtbar) => {
        spieler.zustand.erzwungen = sichtbar;
        if (sichtbar) spieler.zustand.zeigen = true;
    };
    spieler.starten({ bvhUrl, overlayId, detectionUrl, keypointsUrl });
    return spieler;
}
