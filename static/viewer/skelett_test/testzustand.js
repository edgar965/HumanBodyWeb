/**
 * Testzustand — der gemeinsame Zustand der Skelett-Vergleichsseite.
 *
 * WARUM eine Klasse (Umbau 16.08.2026): skeleton_test.js hatte 663 Zeilen und
 * vierzehn lose Modulvariablen — Szene, Kamera, Mischer, Abspielzustand, das
 * Skelettverzeichnis. Beim Aufteilen liegt sonst die Haelfte davon auf der
 * falschen Seite; wer aus einem herausgeloesten Modul `playing = true` schreibt,
 * bekommt beim ES-Modul-Import ausserdem einen Fehler, weil importierte
 * Bindungen nicht beschreibbar sind.
 *
 * `skeletons` bleibt ein Woerterbuch: Es beschreibt sieben gleichartige
 * Eintraege und wird durchlaufen, nicht durchgereicht.
 */
import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';

/** Eine Skelettspalte der Vergleichsansicht. */
function spalte(farbe, xVersatz, zVersatz = 0) {
    return { group: null, bones: null, labels: [], vizMeshes: [], color: farbe,
             xOffset: xVersatz, zOffset: zVersatz, rootBone: null,
             boneByName: null, skeleton: null, bvhResult: null, wrapper: null };
}

export class Testzustand {
    // ----- Darstellung
    static scene = null;
    static camera = null;
    static renderer = null;
    static controls = null;
    static labelRenderer = null;

    // ----- Zeit und Messung
    static clock = new THREE.Clock();
    static frameCount = 0;
    static fpsAccum = 0;

    // ----- Wiedergabe
    static bvhLoader = new BVHLoader();
    static mixer = null;
    static currentAction = null;
    static playing = false;
    static currentBvhResult = null;
    static currentFormat = null;

    // ----- Daten
    static rigifySkeletonData = null;
    static skinWeightData = null;
    static allAnimations = {};

    /** Die sieben Skelettspalten: DEF vorn, SMPL dahinter. */
    static skeletons = {
        def:      spalte(0xff4444, -3.0),
        cmu:      spalte(0x44ff44, -1.5),
        mixamo:   spalte(0xffaa44, 0.0),
        mocapnet: spalte(0x4488ff, 1.5),
        bandai:   spalte(0xbb44ff, 3.0),
        smpl:     spalte(0xffff00, -3.0, -2.0),
        openpose: spalte(0x44dddd, 4.5),
    };
}
