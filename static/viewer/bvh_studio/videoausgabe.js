import * as THREE from 'three';
import { state } from './state.js';
import { exportBrowserMediaRecorder, exportServerFfmpeg } from './video_schreiben.js';

/**
 * Videoausgabe — die Szene als MP4 aufnehmen.
 *
 * Herausgelöst aus `export_video.js` (236 Zeilen). Der Ablauf ist kurz, aber
 * jeder Schritt hat einen Grund, den man kennen muss:
 *
 * DIE KAMERA KOMMT AUS DER ZEITLEISTE, NICHT AUS DER ANSICHT
 * ==========================================================
 * Ohne Kamera-Spur mit Keyframes wird ABGEBROCHEN — mit einer Meldung, die sagt,
 * was zu tun ist. Die Alternative wäre, die aktuelle Mausansicht zu backen; das
 * ergibt ein Video, das mit der Zeitleiste nichts zu tun hat, und niemand merkt
 * es vor dem Ansehen.
 *
 * Die Umlaufsteuerung (`OrbitControls`) wird für die Aufnahme ABGESCHALTET: Sie
 * schreibt sonst bei jeder Mausbewegung die Kamera um, die gerade die Zeitleiste
 * setzt. Und die Spur wird auf `cameraActive` gezwungen, auch wenn der Nutzer sie
 * stummgeschaltet hat — sonst nimmt der Export nichts auf.
 *
 * DER ABBRUCH LÄUFT ÜBER `export_video.exportCancelled`
 * =====================================================
 * `video_schreiben.js` liest diesen Namen als lebende Bindung (ES-Module). Ein
 * zweiter Schalter hier wäre eine zweite Wahrheit — und beim ersten Abbruch
 * hätte einer von beiden gefehlt.
 *
 * ALLES WIRD ZURÜCKGESETZT (`finally`)
 * ====================================
 * Standort, Drehung, Bildwinkel, Seitenverhältnis, Steuerung, Wiedergabe. Ein
 * Abbruch mitten im Export darf die Ansicht des Nutzers nicht verändert
 * hinterlassen — und das Seitenverhältnis der Aufnahme (16:9) ist fast nie das
 * des Fensters.
 */
export class Videoausgabe {

    static SEITENVERHAELTNIS = 16 / 9;

    /** Die Kamera-Spur, die den Export treibt — oder `null`. */
    static kameraspur() {
        return state.project.tracks.find(
            spur => spur.type === 'camera' && (spur.clips?.length || 0) > 0) || null;
    }

    /** Ein Renderer in Ausgabegröße, außerhalb des Bildschirms. */
    static renderer(hoehe) {
        const breite = Math.round(hoehe * Videoausgabe.SEITENVERHAELTNIS);
        const leinwand = document.createElement('canvas');
        leinwand.width = breite;
        leinwand.height = hoehe;
        const renderer = new THREE.WebGLRenderer({
            canvas: leinwand, antialias: true, preserveDrawingBuffer: true });
        renderer.setSize(breite, hoehe, false);
        renderer.setPixelRatio(1);
        return { renderer, leinwand, breite, hoehe };
    }

    /** Kamera und Steuerung für die Aufnahme umstellen; liefert den Rückweg. */
    static kameraUebernehmen(spur, breite, hoehe) {
        const zurueck = {
            ort: state.camera.position.clone(),
            drehung: state.camera.quaternion.clone(),
            bildwinkel: state.camera.fov,
            seitenverhaeltnis: state.camera.aspect,
            spurAktiv: spur.cameraActive,
            steuerung: state.controls ? state.controls.enabled : true,
            liefLos: state.playing,
        };
        if (state.controls) state.controls.enabled = false;
        spur.cameraActive = true;
        state.camera.aspect = breite / hoehe;
        state.camera.updateProjectionMatrix();
        state.playing = false;
        return zurueck;
    }

    static kameraZurueck(spur, zurueck) {
        spur.cameraActive = zurueck.spurAktiv;
        state.camera.position.copy(zurueck.ort);
        state.camera.quaternion.copy(zurueck.drehung);
        state.camera.fov = zurueck.bildwinkel;
        state.camera.aspect = zurueck.seitenverhaeltnis;
        state.camera.updateProjectionMatrix();
        if (state.controls) state.controls.enabled = zurueck.steuerung;
        if (zurueck.liefLos) state.playing = true;
    }

    /** Aufnehmen — `motor` ist `server` (ffmpeg) oder `browser`. */
    static async aufnehmen(angaben, felder) {
        const spur = Videoausgabe.kameraspur();
        if (!spur) {
            felder.status.textContent =
                'Fehler: Kein Kamera-Track mit Keyframes. Lege im '
                + 'Timeline-Bereich einen Kamera-Track an und füge mind. einen '
                + 'Keyframe hinzu.';
            felder.balken.style.width = '0%';
            return false;
        }
        const { renderer, leinwand, breite, hoehe } =
            Videoausgabe.renderer(angaben.hoehe);
        const zurueck = Videoausgabe.kameraUebernehmen(spur, breite, hoehe);
        try {
            const schreiben = angaben.motor === 'server'
                ? exportServerFfmpeg : exportBrowserMediaRecorder;
            const werte = angaben.motor === 'server'
                ? [renderer, leinwand, angaben.von, angaben.bis, angaben.bilder,
                   angaben.guete, angaben.dateiname, felder.status, felder.balken]
                : [renderer, leinwand, angaben.von, angaben.bis, angaben.bilder,
                   angaben.dateiname, felder.status, felder.balken];
            await schreiben(...werte);
            return true;
        } finally {
            renderer.dispose();
            Videoausgabe.kameraZurueck(spur, zurueck);
        }
    }
}
