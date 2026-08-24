/**
 * Vorschaufenster — das Popup-Fenster der Animationsvorschau (Taste A).
 *
 * WARUM getrennt (Umbau 16.08.2026): `previewAnimation` in project.js war 231
 * Zeilen lang und machte drei voellig verschiedene Dinge: ein Modal aufbauen,
 * eine Three.js-Szene einrichten und eine retargetete Animation laden. Dazu
 * gehoerten NEUN lose Modulvariablen (`_previewRenderer`, `_previewMixer`, …).
 *
 * Hier liegt das Fenster: DOM, Bedienknoepfe, Renderer, Kamera, Groesse,
 * Freigabe. Was angezeigt wird, entscheidet Vorschau (vorschau.js).
 *
 * Kein Import von vorschau.js — die aktuell gezeigte Animation kommt ueber
 * `fn.getPreviewInfo()` aus der Registry. Ein gegenseitiger Import waere ein
 * Zyklus, und die Registry ist genau fuer diesen Fall da.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _gaussSmooth } from './werkzeug_glaettung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/** Gemerkte Fenstergroesse — ueberlebt den Seitenwechsel. */
const GROESSE_SCHLUESSEL = 'bvhStudio_previewSize';

/** Kopfhoehe des Fensters in Pixeln (fuer die Leinwandhoehe). */
const KOPFHOEHE = 50;

const RUMPF = `
    <div id="preview-box" style="background:var(--bg-secondary,#1a1a2e);border:1px solid var(--border,#334);border-radius:10px;width:1000px;height:700px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 16px 48px rgba(0,0,0,0.5);resize:both;min-width:500px;min-height:400px;max-width:95vw;max-height:90vh;">
        <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 16px;border-bottom:1px solid var(--border,#334);">
            <span id="preview-title" style="font-size:0.9rem;color:#ccc;"></span>
            <div style="display:flex;gap:8px;align-items:center;">
                <button id="preview-play" style="background:none;border:1px solid var(--border,#334);border-radius:4px;color:#ccc;cursor:pointer;padding:4px 10px;font-size:0.8rem;"><i class="fas fa-play" id="preview-play-icon"></i></button>
                <span id="preview-frame" style="font-size:0.75rem;color:#888;">0 / 0</span>
                <button id="preview-save-smooth" style="background:none;border:1px solid var(--border,#334);border-radius:4px;color:#4caf50;cursor:pointer;padding:4px 10px;font-size:0.75rem;" title="Smooth permanent auf BVH speichern"><i class="fas fa-save"></i> Smooth speichern</button>
                <button id="preview-close" style="background:none;border:none;color:#888;cursor:pointer;font-size:1.2rem;">&times;</button>
            </div>
        </div>
        <canvas id="preview-canvas" style="flex:1;width:100%;"></canvas>
    </div>`;

export class Vorschaufenster {
    static modal = null;
    static renderer = null;
    static scene = null;
    static camera = null;
    static controls = null;
    static mixer = null;
    static action = null;
    static clock = null;
    static animId = null;

    /** Fenster und Szene einmalig anlegen; danach wiederverwenden. */
    static sicherstellen() {
        if (Vorschaufenster.modal) return;
        Vorschaufenster._fensterBauen();
        Vorschaufenster._szeneBauen();
    }

    static _fensterBauen() {
        const modal = document.createElement('div');
        modal.id = 'preview-modal';
        modal.style.cssText = 'position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;';
        modal.innerHTML = RUMPF;
        document.body.appendChild(modal);
        Vorschaufenster.modal = modal;

        document.getElementById('preview-close')
            .addEventListener('click', Vorschaufenster.schliessen);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) Vorschaufenster.schliessen();
        });
        document.getElementById('preview-play')
            .addEventListener('click', Vorschaufenster.abspielenUmschalten);
        document.getElementById('preview-save-smooth')
            .addEventListener('click', Vorschaufenster.glaettungSpeichern);
    }

    static _szeneBauen() {
        const canvas = document.getElementById('preview-canvas');
        Vorschaufenster.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
        Vorschaufenster.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);
        const dl = new THREE.DirectionalLight(0xffffff, 2);
        dl.position.set(2, 4, 3);
        scene.add(dl);
        scene.add(new THREE.AmbientLight(0x404060, 1.5));
        scene.add(new THREE.GridHelper(4, 20, 0x333355, 0x222244));
        Vorschaufenster.scene = scene;

        Vorschaufenster.camera = new THREE.PerspectiveCamera(50, 700 / 440, 0.01, 500);
        Vorschaufenster.camera.position.set(0, 1, 3);
        Vorschaufenster.controls = new OrbitControls(Vorschaufenster.camera, canvas);
        Vorschaufenster.controls.target.set(0, 0.8, 0);
        Vorschaufenster.controls.update();
        Vorschaufenster.clock = new THREE.Clock();
    }

    /** Fenster zeigen, Titel setzen, Groesse wiederherstellen und ueberwachen. */
    static zeigen(titel) {
        Vorschaufenster.modal.style.display = 'flex';
        document.getElementById('preview-title').textContent = titel;
        document.getElementById('preview-play-icon').className = 'fas fa-pause';

        const box = document.getElementById('preview-box');
        try {
            const gemerkt = JSON.parse(localStorage.getItem(GROESSE_SCHLUESSEL));
            if (gemerkt?.w && gemerkt?.h) {
                box.style.width = gemerkt.w + 'px';
                box.style.height = gemerkt.h + 'px';
            }
        } catch (e) { Protokoll.debug('vorschau', 'gemerkte Fenstergröße nicht lesbar', e); }

        requestAnimationFrame(Vorschaufenster.groesseAnpassen);
        if (!box._resizeObserver) {
            box._resizeObserver = new ResizeObserver(() => {
                Vorschaufenster.groesseAnpassen();
                try {
                    localStorage.setItem(GROESSE_SCHLUESSEL, JSON.stringify(
                        { w: box.clientWidth, h: box.clientHeight }));
                } catch (e) { Protokoll.debug('vorschau', 'Fenstergröße nicht merkbar', e); }
            });
            box._resizeObserver.observe(box);
        }
    }

    static meldung(text) {
        const el = document.getElementById('preview-title');
        if (el) el.textContent = text;
    }

    static groesseAnpassen() {
        const canvas = document.getElementById('preview-canvas');
        const box = document.getElementById('preview-box');
        if (!canvas || !box || !Vorschaufenster.renderer) return;
        const w = box.clientWidth - 2;
        const h = box.clientHeight - KOPFHOEHE;
        if (w <= 10 || h <= 10) return;
        canvas.width = w;
        canvas.height = h;
        Vorschaufenster.renderer.setSize(w, h, false);
        Vorschaufenster.camera.aspect = w / h;
        Vorschaufenster.camera.updateProjectionMatrix();
    }

    static abspielenUmschalten() {
        const a = Vorschaufenster.action;
        if (!a) return;
        const laeuft = !a.paused && a.isRunning();
        a.paused = laeuft;
        if (!laeuft) a.play();
        document.getElementById('preview-play-icon').className =
            laeuft ? 'fas fa-play' : 'fas fa-pause';
    }

    /** Geglaettete Kurven dauerhaft in die BVH-Datei schreiben. */
    static async glaettungSpeichern() {
        if (!_gaussSmooth.active) {
            alert('Smooth ist nicht aktiv.\nBitte erst Tools > Smooth EINSCHALTEN.');
            return;
        }
        const { category, name } = fn.getPreviewInfo?.() || {};
        if (!category || !name) { alert('Keine Animation geladen.'); return; }
        const sigma = _gaussSmooth.sigma;
        try {
            const ergebnis = await Serverabruf.json('/api/retarget/smooth-bvh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category, name, sigma }),
            });
            if (!ergebnis.ok) {
                alert('Fehler: ' + (ergebnis.error || 'Unbekannt'));
                return;
            }
            fn.serverLog('gauss_saved_preview',
                         `${category}/${name} sigma=${sigma} frames=${ergebnis.frames}`);
            alert(`Smooth (σ=${sigma}) gespeichert: ${category}/${name}\n`
                  + `${ergebnis.frames} Frames geglättet.`);
        } catch (e) {
            alert('Fehler: ' + e.message);
        }
    }

    /**
     * Vorschau-Inhalt vollstaendig freigeben.
     *
     * WARUM so ausfuehrlich (Review 15.08.2026): Vorher stand hier nur
     *     for (const c of toRemove) { scene.remove(c); c.geometry?.dispose(); }
     * Drei Luecken, alle am Code nachgelesen:
     *   1. MATERIALIEN wurden nie entsorgt — sie halten Shader und Texturen.
     *   2. Nur DIREKTE Kinder wurden angefasst. Ein SkinnedMesh haengt unter
     *      einer Gruppe; deren Netze blieben liegen. Deshalb `traverse`.
     *   3. Aufgeraeumt wurde erst beim NAECHSTEN Oeffnen. Wer die Vorschau
     *      schliesst und weiterarbeitet, behielt das Netz im Grafikspeicher.
     * WIDERLEGT wurde die Behauptung, Modal, Renderer, OrbitControls und Zuhoerer
     * sammelten sich an: Sie entstehen einmal in `sicherstellen()`.
     */
    static leeren() {
        if (Vorschaufenster.mixer) {
            Vorschaufenster.mixer.stopAllAction();
            Vorschaufenster.mixer = null;
        }
        Vorschaufenster.action = null;
        if (!Vorschaufenster.scene) return;
        const weg = Vorschaufenster.scene.children.filter(c => c.userData._preview);
        for (const wurzel of weg) {
            Vorschaufenster.scene.remove(wurzel);
            wurzel.traverse(Vorschaufenster._knotenFreigeben);
        }
    }

    static _knotenFreigeben(o) {
        if (o.geometry) o.geometry.dispose();
        const mats = Array.isArray(o.material) ? o.material
                   : (o.material ? [o.material] : []);
        for (const m of mats) {
            for (const k of ['map', 'normalMap', 'roughnessMap', 'metalnessMap',
                             'emissiveMap', 'alphaMap', 'aoMap']) {
                if (m[k]?.dispose) m[k].dispose();
            }
            if (m.dispose) m.dispose();
        }
    }

    static schliessen() {
        if (Vorschaufenster.modal) Vorschaufenster.modal.style.display = 'none';
        if (Vorschaufenster.animId) {
            cancelAnimationFrame(Vorschaufenster.animId);
            Vorschaufenster.animId = null;
        }
        // Beim Schliessen wirklich freigeben, nicht erst beim naechsten Oeffnen.
        Vorschaufenster.leeren();
    }
}

fn.closePreview = Vorschaufenster.schliessen;
