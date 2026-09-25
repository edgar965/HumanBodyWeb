import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { Randleuchten } from './randleuchten.js';

/**
 * Auswahlaura — wie Auswahl und Hover in der 3D-Ansicht zu sehen sind (Szene, BVH Studio).
 *
 * WARUM (Edgar, 25.09.2026): „ich brauche eine deutlich bessere Anzeige im UI bei
 * einer Selektion … kaum erkennen wann etwas selektiert ist. Auch hover soll sowas wie
 * eine Aura haben, nur heller." Bis dahin hob die Szene nur das Eigenleuchten an
 * (`emissive` 0x12123a, Hover 0x08081a) — auf hellem Stoff unter drei Lichtern
 * unsichtbar; das Studio zeichnete einen Kasten um die Knochen.
 *
 * DREI STILE (Einstellungen → Studio, `ui_prefs.auswahl_stil`), wie andere es machen:
 *   `aura`   Three.js `OutlinePass` (Beispiel `webgl_postprocessing_outline`): Kontur mit
 *            weichem Glühen — VORGABE (verdeckte Kanten aus: der Körperumriss unter
 *            dem Shirt lag sonst als gezackte Linie auf dem Stoff);
 *   `kontur` Blender/Unity/Unreal: scharfe Linie ohne Glühen;
 *   `rand`   Spiele: Fresnel-Randleuchten auf dem Objekt selbst (`Randleuchten`).
 * Auswahl dunkles Orange, Hover helles Orange — dieselbe Aura, dunkel und hell (Edgar).
 *
 * KOSTEN NUR MIT ZIEL: ohne Auswahl und Hover rendert die Seite direkt
 * (`renderer.render`). `aura`/`kontur` laufen über den Composer: Szene in ein Ziel mit
 * 4-fach-MSAA, je Pass Maske + Tiefe, dann `OutputPass` (Tonwert, sRGB wie der
 * Renderer). Die Videoaufnahmen rendern selbst — die Anzeige kommt nie ins Video.
 */
export class Auswahlaura {

    static STILE = ['aura', 'kontur', 'rand'];
    static VORGABE = 'aura';
    /** Je Stil: Auswahl und Hover (Farbe, verdeckte Kante, Stärke, Glühen, Dicke). */
    static PAESSE = {
        aura: {
            auswahl: { farbe: 0xb84400, verdeckt: 0x000000, staerke: 6.0, glow: 0.8, dicke: 2.0 },
            hover: { farbe: 0xffe8c8, verdeckt: 0x000000, staerke: 3.0, glow: 1.4, dicke: 1.2 },
        },
        kontur: {
            auswahl: { farbe: 0xb84400, verdeckt: 0x000000, staerke: 10.0, glow: 0.0, dicke: 1.0 },
            hover: { farbe: 0xffe8c8, verdeckt: 0x000000, staerke: 5.0, glow: 0.0, dicke: 1.0 },
        },
    };
    /** Die Einstellung „Deckkraft der Auswahl" (0..1) mit dieser Vorgabe ist Faktor 1. */
    static VORGABE_DECKKRAFT = 0.3;

    static stil = Auswahlaura.VORGABE;
    static faktor = 1.0;
    static _composer = null;
    static _auswahl = null;
    static _hover = null;
    static _groesse = new THREE.Vector2();
    static _geladen = null;

    /** Den Stil aus `ui_prefs` holen (einmal je Seite). */
    static laden() {
        if (!Auswahlaura._geladen) {
            Auswahlaura._geladen = fetch('/api/ui-prefs/', { credentials: 'same-origin' })
                .then((a) => (a.ok ? a.json() : {}))
                .then((v) => Auswahlaura.stilSetzen(v?.auswahl_stil))
                .catch(() => Auswahlaura.stilSetzen(null));
        }
        return Auswahlaura._geladen;
    }

    static stilSetzen(stil) {
        Auswahlaura.stil = Auswahlaura.STILE.includes(stil) ? stil : Auswahlaura.VORGABE;
        Auswahlaura._einstellen();
        return Auswahlaura.stil;
    }

    /** Aus der Szenen-Einstellung „Deckkraft der Auswahl" — 0 schaltet die Anzeige ab. */
    static deckkraft(wert) {
        if (typeof wert !== 'number') return;
        Auswahlaura.faktor = Math.max(0, wert) / Auswahlaura.VORGABE_DECKKRAFT;
        Auswahlaura._einstellen();
    }

    /**
     * Ein Bild: `auswahl`/`hover` sind Netze (Mesh/SkinnedMesh). Liefert true, wenn
     * über den Composer gerendert wurde.
     */
    static rendern(renderer, szene, kamera, auswahl = [], hover = []) {
        // Hover auch INNERHALB der Auswahl (die Jeans einer gewählten Figur) — der
        // helle Hover liegt als späterer Pass über der dunklen Auswahl.
        const nurHover = hover;
        const aus = Auswahlaura.faktor <= 0;
        if (Auswahlaura.stil === 'rand' || aus) {
            Randleuchten.setzen(aus ? [] : auswahl, aus ? [] : nurHover, Auswahlaura.faktor);
            renderer.render(szene, kamera);
            return false;
        }
        Randleuchten.setzen([], [], 0);
        if (!auswahl.length && !nurHover.length) {
            renderer.render(szene, kamera);
            return false;
        }
        const composer = Auswahlaura._bereit(renderer, szene, kamera);
        Auswahlaura._auswahl.selectedObjects = auswahl;
        Auswahlaura._hover.selectedObjects = nurHover;
        Auswahlaura._auswahl.enabled = auswahl.length > 0;
        Auswahlaura._hover.enabled = nurHover.length > 0;
        composer.render();
        return true;
    }

    /** Sichtbare Netze unter Wurzeln (die unsichtbare Stoffkopie zählt nicht). */
    static netze(...wurzeln) {
        const aus = [];
        for (const w of wurzeln) Auswahlaura._sammeln(w, aus);
        return aus;
    }

    /**
     * Rekursiv, damit ganze Teilbäume wegfallen: die Pfeile der Transform-Steuerung
     * (Edgar, 25.09.2026, Bild: „die Pfeile haben auch eine Aura und blinken") hängen
     * an der Figur — sie zeichnen ohne Tiefentest, ihre Maske flackerte. Dazu Hüllen des
     * Randleuchtens und alles andere, was ohne Tiefentest über der Szene liegt.
     */
    static _sammeln(o, aus) {
        if (!o || Auswahlaura._hilfe(o)) return;
        if ((o.isMesh || o.isSkinnedMesh) && o.visible && !Auswahlaura._ohneTiefe(o)) aus.push(o);
        for (const k of o.children || []) Auswahlaura._sammeln(k, aus);
    }

    /**
     * Die Pfeile der Transform-Steuerung aus den Masken des Passes heraushalten (Edgar,
     * 25.09.2026, Bild: „die Pfeile haben auch eine Aura und blinken"). `OutlinePass`
     * blendet Nicht-Gewähltes für die Maske aus, die Steuerung schaltet ihre Griffe aber in
     * JEDEM `updateMatrixWorld` wieder sichtbar — mal in der Maske, mal nicht: Aura und
     * Flackern. Während des Passes ist ihr ganzer Teilbaum aus; im Bild (`RenderPass`)
     * bleibt er.
     */
    static _ohneHelfer(pass) {
        const original = pass.render.bind(pass);
        pass.render = (...argumente) => {
            const aus = (pass.renderScene?.children || [])
                .filter((o) => o.visible && Auswahlaura._hilfe(o));
            for (const o of aus) o.visible = false;
            try { original(...argumente); } finally { for (const o of aus) o.visible = true; }
        };
        return pass;
    }

    static _hilfe(o) {
        return Boolean(o.isTransformControlsGizmo || o.isTransformControlsPlane
            || o.isTransformControlsRoot || String(o.type || '').startsWith('TransformControls')
            || o.userData?.randleuchten || o.userData?.isSelectionFrame);
    }

    static _ohneTiefe(o) {
        const m = Array.isArray(o.material) ? o.material[0] : o.material;
        return m?.depthTest === false;
    }

    static _bereit(renderer, szene, kamera) {
        renderer.getDrawingBufferSize(Auswahlaura._groesse);
        const { x: breite, y: hoehe } = Auswahlaura._groesse;
        let composer = Auswahlaura._composer;
        if (!composer || composer.renderer !== renderer) {
            const ziel = new THREE.WebGLRenderTarget(breite, hoehe,
                                                     { type: THREE.HalfFloatType, samples: 4 });
            composer = new EffectComposer(renderer, ziel);
            composer.addPass(new RenderPass(szene, kamera));
            Auswahlaura._hover = Auswahlaura._ohneHelfer(
                new OutlinePass(new THREE.Vector2(breite, hoehe), szene, kamera));
            Auswahlaura._auswahl = Auswahlaura._ohneHelfer(
                new OutlinePass(new THREE.Vector2(breite, hoehe), szene, kamera));
            // Erst die dunkle Auswahl, dann der helle Hover darüber — sonst verschluckt die
            // dunkle Kante den Hover auf einem Stück der gewählten Figur.
            composer.addPass(Auswahlaura._auswahl);
            composer.addPass(Auswahlaura._hover);
            composer.addPass(new OutputPass());
            Auswahlaura._composer = composer;
            Auswahlaura._einstellen();
        }
        // Fenstergröße, Kamera und Szene können wechseln (Projekt laden, Kamerawahl).
        const pixel = renderer.getPixelRatio();
        const soll = [Math.round(breite / pixel), Math.round(hoehe / pixel)];
        if (composer._breite !== soll[0] || composer._hoehe !== soll[1]) {
            composer.setPixelRatio(pixel);
            composer.setSize(soll[0], soll[1]);
            composer._breite = soll[0];
            composer._hoehe = soll[1];
        }
        const [grund] = composer.passes;
        grund.scene = szene;
        grund.camera = kamera;
        for (const pass of [Auswahlaura._auswahl, Auswahlaura._hover]) {
            pass.renderScene = szene;
            pass.renderCamera = kamera;
        }
        return composer;
    }

    static _einstellen() {
        const satz = Auswahlaura.PAESSE[Auswahlaura.stil] || Auswahlaura.PAESSE.aura;
        for (const [pass, art] of [[Auswahlaura._auswahl, satz.auswahl], [Auswahlaura._hover, satz.hover]]) {
            if (!pass) continue;
            pass.visibleEdgeColor.set(art.farbe);
            pass.hiddenEdgeColor.set(art.verdeckt);
            pass.edgeGlow = art.glow;
            pass.edgeThickness = art.dicke;
            pass.edgeStrength = art.staerke * Auswahlaura.faktor;
            pass.pulsePeriod = 0;
        }
    }
}

// Für Proben im Tab (wie `__characters`).
if (typeof window !== 'undefined') window.__auswahlaura = Auswahlaura;
