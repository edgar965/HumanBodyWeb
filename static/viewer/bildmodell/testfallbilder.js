/**
 * Testfallbilder — Fotos der Referenzfigur, im Browser gerendert und in den Auftrag geladen.
 *
 * Edgar (19.09.2026): „als Testcase erstelle ein neues Projekt: Ursula. In dem
 * nimmst du alle Bilder, die du brauchst für alle Maße, Texturen von Ursula."
 * Von P3D Ursula gibt es keine Shopbilder auf diesem Rechner (nur das 114-px-
 * Icon der Bibliothek) — also werden sie aus der Figur selbst gerendert: eine
 * eigene Bühne, `Genesis9Modell` der Referenz (Haut, Augen, Brauen, Wimpern
 * wie in der Szene), feine Stufe und alle Texturen abgewartet, dann je
 * Ansicht eine Kamera (Perspektive 30°, wie ein Porträtobjektiv) auf einen
 * Bereich, den das Skelett vorgibt: ganzer Körper (vorn, Seite, hinten,
 * dreiviertel), Kopf (vorn, Seite), je Hand, Füße, Oberkörper, Rücken. Jedes
 * Bild geht als JPG (`<figur>_<ansicht>.jpg`) über `bilderHochladen` in den
 * Auftrag; die Sichtung ordnet es dann wie ein Foto ein. Der Lauf kennt die
 * Referenz nicht — er sieht nur Bilder.
 */
import * as THREE from 'three';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Genesis9texturen } from '../gemeinsam/genesis9texturen.js';

export class Testfallbilder {

    /** name, Drehung um die Figur (0 = von vorn), Bereich, Bildgröße. */
    static ANSICHTEN = [
        { name: 'vorn', grad: 0, bereich: 'koerper', b: 1200, h: 1600 },
        { name: 'seite', grad: 90, bereich: 'koerper', b: 1200, h: 1600 },
        { name: 'hinten', grad: 180, bereich: 'koerper', b: 1200, h: 1600 },
        { name: 'dreiviertel', grad: 40, bereich: 'koerper', b: 1200, h: 1600 },
        { name: 'kopf_vorn', grad: 0, bereich: 'kopf', b: 1200, h: 1200 },
        { name: 'kopf_seite', grad: 90, bereich: 'kopf', b: 1200, h: 1200 },
        { name: 'hand_l', grad: 0, bereich: 'hand_l', b: 1000, h: 1000 },
        { name: 'hand_r', grad: 0, bereich: 'hand_r', b: 1000, h: 1000 },
        { name: 'fuesse', grad: 0, bereich: 'fuesse', b: 1400, h: 1000 },
        { name: 'oberkoerper', grad: 0, bereich: 'oberkoerper', b: 1200, h: 1200 },
        { name: 'ruecken', grad: 180, bereich: 'oberkoerper', b: 1200, h: 1200 },
    ];
    static FOV = 30;
    static HINTERGRUND = 0xd9d6d0;

    constructor(auftrag) {
        this.auftrag = auftrag;
    }

    // ------------------------------------------------------------ Bühne

    _buehne() {
        this.canvas = document.createElement('canvas');
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, preserveDrawingBuffer: true });
        this.renderer.setPixelRatio(1);
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.szene = new THREE.Scene();
        this.szene.background = new THREE.Color(Testfallbilder.HINTERGRUND);
        this.szene.add(new THREE.HemisphereLight(0xffffff, 0x8a8078, 1.0));
        const licht = new THREE.DirectionalLight(0xffffff, 1.4);
        licht.position.set(1.2, 3, 2.5);
        this.szene.add(licht);
        const fuell = new THREE.DirectionalLight(0xffffff, 0.5);
        fuell.position.set(-2, 1.5, -1.5);
        this.szene.add(fuell);
        this.kamera = new THREE.PerspectiveCamera(Testfallbilder.FOV, 1, 0.02, 50);
    }

    /** Die Figur bauen und warten, bis feine Stufe und alle Bilder da sind. */
    async _figur(figur, melder) {
        melder(`${figur}: Figur wird gebaut …`);
        const modell = new Genesis9Modell('testfallbilder', { figur });
        await modell.bauen();
        this.szene.add(modell.group);
        if (modell.fein) await modell.fein;
        melder('Texturen laden …');
        await Promise.all([...Genesis9texturen._vorrat.values()].map(e => e.fertig));
        await new Promise(r => setTimeout(r, 300));       // Materialien aktualisieren sich im nächsten Bild
        return modell;
    }

    // ---------------------------------------------------------- Bereiche

    /** Weltlage eines Knochens — oder null. */
    static knochen(modell, name) {
        const k = modell.skelett?.boneByName?.[name];
        if (!k) return null;
        return k.getWorldPosition(new THREE.Vector3());
    }

    /** `{mitte, hoehe}` des Bereichs (Meter) aus Skelett und Figurhöhe. */
    bereich(modell, art) {
        const H = modell.hoehe || 1.7;
        const p = name => Testfallbilder.knochen(modell, name);
        const mitte = (...namen) => {
            const punkte = namen.map(p).filter(Boolean);
            if (!punkte.length) return null;
            return punkte.reduce((a, v) => a.add(v), new THREE.Vector3()).multiplyScalar(1 / punkte.length);
        };
        switch (art) {
            case 'kopf': {
                const m = mitte('head') || new THREE.Vector3(0, H * 0.93, 0);
                return { mitte: m.clone().add(new THREE.Vector3(0, H * 0.04, 0)), hoehe: H * 0.24 };
            }
            case 'hand_l':
            case 'hand_r': {
                // Handwurzel plus ein halbes Handmaß nach unten: die Finger hängen in der A-Pose.
                const m = p(`${art.slice(-1)}_hand`) || new THREE.Vector3(art === 'hand_l' ? 0.35 : -0.35, H * 0.45, 0);
                return { mitte: m.clone().add(new THREE.Vector3(0, -H * 0.06, 0)), hoehe: H * 0.24 };
            }
            case 'fuesse': {
                const m = mitte('l_foot', 'r_foot') || new THREE.Vector3(0, H * 0.05, 0);
                return { mitte: new THREE.Vector3(m.x, H * 0.06, m.z), hoehe: H * 0.2 };
            }
            case 'oberkoerper': {
                const m = mitte('spine3', 'spine4') || new THREE.Vector3(0, H * 0.72, 0);
                return { mitte: m, hoehe: H * 0.42 };
            }
            default:
                return { mitte: new THREE.Vector3(0, H * 0.5, 0), hoehe: H * 1.08 };
        }
    }

    _kameraSetzen(ansicht, bereich) {
        const { b, h } = ansicht;
        this.renderer.setSize(b, h, false);
        this.kamera.aspect = b / h;
        this.kamera.updateProjectionMatrix();
        // Der Bereich soll das Bild in der Höhe füllen — oder in der Breite, wenn er breiter ist.
        const tan = Math.tan(THREE.MathUtils.degToRad(Testfallbilder.FOV) / 2);
        let abstand = (bereich.hoehe / 2) / tan;
        if (bereich.breite) abstand = Math.max(abstand, (bereich.breite / 2) / (tan * b / h));
        const w = THREE.MathUtils.degToRad(ansicht.grad);
        const richtung = new THREE.Vector3(Math.sin(w), 0, Math.cos(w));
        this.kamera.position.copy(bereich.mitte).add(richtung.multiplyScalar(abstand));
        this.kamera.lookAt(bereich.mitte);
    }

    _blob(qualitaet = 0.92) {
        return new Promise(r => this.canvas.toBlob(r, 'image/jpeg', qualitaet));
    }

    // ------------------------------------------------------------ Lauf

    /** Alle Ansichten rendern und hochladen; `melder(text)` für die Zeile daneben. */
    async erzeugen(figur, melder = () => {}) {
        this._buehne();
        let modell = null;
        try {
            modell = await this._figur(figur, melder);
            const dateien = [];
            for (const ansicht of Testfallbilder.ANSICHTEN) {
                melder(`Rendern: ${ansicht.name}`);
                this._kameraSetzen(ansicht, this.bereich(modell, ansicht.bereich));
                this.renderer.render(this.szene, this.kamera);
                const blob = await this._blob();
                dateien.push(new File([blob], `${figur}_${ansicht.name}.jpg`, { type: 'image/jpeg' }));
            }
            melder(`${dateien.length} Bilder hochladen …`);
            await this.auftrag.bilderHochladen(dateien);
            melder(`${dateien.length} Bilder aus ${figur} im Auftrag — jetzt „Neue Dateien sichten" oder Starten`);
            return dateien.length;
        } finally {
            if (modell) { this.szene.remove(modell.group); modell.dispose?.(); }
            this.renderer.dispose();
        }
    }
}
