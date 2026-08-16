/**
 * Seitenzustand — der gemeinsame Zustand der Animationsseite.
 *
 * WARUM (Umbau 15.08.2026): animations.js hatte 1033 Zeilen und 18 lose
 * `let`-Variablen auf Modulebene — Szene, Kamera, Netz, Mischer, Abspielzustand,
 * Skelettdaten. Jede Funktion griff direkt darauf zu, weshalb sich die Datei
 * nicht aufteilen liess: Wohin man auch schneidet, die Haelfte der Variablen
 * bleibt auf der falschen Seite (in timeline.js ist genau das passiert und hat
 * einen ReferenceError beim Seitenaufbau erzeugt).
 *
 * Als Klasse mit statischen Feldern gibt es EINEN Ort dafuer, und jedes Modul
 * schreibt `Seitenzustand.bodyMesh = …` statt auf eine Variable zu hoffen, die
 * es zufaellig noch sieht.
 */
import * as THREE from 'three';

export class Seitenzustand {
    // ----- Darstellung
    static scene = null;
    static camera = null;
    static renderer = null;
    static controls = null;

    // ----- Koerper
    static bodyMesh = null;
    static bodyGeometry = null;
    static isSkinned = false;

    // ----- Zeit und Messung
    static clock = new THREE.Clock();
    static frameCount = 0;
    static fpsAccum = 0;

    // ----- Animation
    static mixer = null;
    static currentAction = null;
    static skeletonHelper = null;
    static playing = false;

    // ----- Skelett und Gewichte
    static rigifySkeletonData = null;
    static skinWeightData = null;
    static rigifySkeleton = null;
    static rigVisible = false;

    // ----- Hautfarben je Herkunft (vom Server)
    static skinColors = {};

    /** Ist die Szene aufgebaut? */
    static get bereit() {
        return !!(this.scene && this.renderer && this.camera);
    }

    /**
     * Renderer und Kamera an die Behaeltergroesse anpassen.
     *
     * Lag als lose Funktion `onResize` in animations.js. Beim Aufteilen rief
     * animation/netz.js sie weiter auf, ohne sie zu sehen — ein
     * ReferenceError, sobald ein Netz geladen wird. Da die Funktion
     * ausschliesslich auf diesen Feldern arbeitet, gehoert sie hierher.
     */
    static groesseAnpassen() {
        if (!Seitenzustand.renderer || !Seitenzustand.camera) return;
        const behaelter = Seitenzustand.renderer.domElement.parentElement;
        const w = behaelter.clientWidth;
        const h = behaelter.clientHeight || window.innerHeight;
        Seitenzustand.renderer.setSize(w, h);
        Seitenzustand.camera.aspect = w / h;
        Seitenzustand.camera.updateProjectionMatrix();
    }
}
