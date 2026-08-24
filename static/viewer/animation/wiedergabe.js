/**
 * Wiedergabe: BVH laden, abspielen, anhalten, Bedienknoepfe.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026).
 */

import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { fetchRetargetedClipFromUrl } from '../retarget_hybrid.js?v=32';
import { Seitenzustand } from './seitenzustand.js';
import { convertToRigifySkinnedMesh } from './netz.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';
import { Animationslader } from '../gemeinsam/animationslader.js';


// =========================================================================
// Global state
// =========================================================================
// Animation
export const bvhLoader = new BVHLoader();

export function animate() {
    requestAnimationFrame(animate);
    const dt = Seitenzustand.clock.getDelta();
    Seitenzustand.controls.update();

    if (Seitenzustand.mixer && Seitenzustand.playing) Seitenzustand.mixer.update(dt);

    Seitenzustand.renderer.render(Seitenzustand.scene, Seitenzustand.camera);

    // FPS counter
    Seitenzustand.frameCount++;
    Seitenzustand.fpsAccum += dt;
    if (Seitenzustand.fpsAccum >= 1.0) {
        document.getElementById('fps-display').textContent = Seitenzustand.frameCount;
        Seitenzustand.frameCount = 0;
        Seitenzustand.fpsAccum = 0;
    }
}

/**
 * BVH laden und abspielen — über `Animationslader`, den auch die Viewer-Seite
 * nutzt. Vorher standen hier 91 Zeilen, die Zeile für Zeile denen in
 * viewer/animation.js entsprachen.
 */
export async function loadBVHAnimation(url, name, fc) {
    return new Animationslader(Seitenzustand, {
        bvhLader: bvhLoader,
        anhalten: zerstoeren => stopAnimation(zerstoeren),
        skinnen: gewichte => convertToRigifySkinnedMesh(null, gewichte),
        umzielen: (adresse, skelett, wahl) =>
            fetchRetargetedClipFromUrl(adresse, skelett, wahl),
        beschriften: (name2, bilder, dauer) =>
            `${name2} — ${bilder}f — ${dauer.toFixed(1)}s`,
    }).laden(url, name, fc);
}

export function stopAnimation(destroy = false) {
    if (Seitenzustand.currentAction) {
        Seitenzustand.currentAction.stop();
        Seitenzustand.currentAction.reset();
        if (destroy) Seitenzustand.currentAction = null;
    }
    if (Seitenzustand.mixer && destroy) {
        Seitenzustand.mixer.stopAllAction();
        Seitenzustand.mixer = null;
    }
    // Reset DEF skeleton to rest pose so mesh returns to T-pose
    if (Seitenzustand.isSkinned && Seitenzustand.rigifySkeleton) {
        Seitenzustand.rigifySkeleton.skeleton.pose();
    }
    // Clean up animation skeleton; recreate from DEF skeleton if rig visible
    // FEHLER bis 16.08.2026: `skelWrapper` war aus netz.js IMPORTIERT und
    // wurde hier zugewiesen — auf eine importierte Bindung darf man nicht
    // schreiben ("TypeError: Assignment to constant variable"). Der
    // Rueckfallweg ohne Skinning brach deshalb ab. Jetzt im Seitenzustand.
    if (Seitenzustand.skelWrapper) {
        Seitenzustand.scene.remove(Seitenzustand.skelWrapper);
        Seitenzustand.skelWrapper = null;
    }
    if (Seitenzustand.skeletonHelper) {
        Seitenzustand.scene.remove(Seitenzustand.skeletonHelper);
        Seitenzustand.skeletonHelper = null;
    }
    if (Seitenzustand.rigVisible && Seitenzustand.rigifySkeleton) {
        Seitenzustand.skeletonHelper = Skelettanzeige.bauen(Seitenzustand.scene, Seitenzustand.rigifySkeleton.rootBone);
    }
    Seitenzustand.playing = false;
}

export function bindPlaybackControls() {
    const playBtn = document.getElementById('anim-play');
    const stopBtn = document.getElementById('anim-stop');
    const timeline = document.getElementById('anim-timeline');
    const speedSlider = document.getElementById('anim-speed');
    const speedLabel = document.getElementById('speed-label');

    if (speedSlider) {
        speedSlider.addEventListener('input', () => {
            const speed = parseInt(speedSlider.value) / 100;
            speedLabel.textContent = `Speed: ${speed.toFixed(1)}x`;
            if (Seitenzustand.mixer) Seitenzustand.mixer.timeScale = speed;
        });
    }

    playBtn.addEventListener('click', () => {
        if (!Seitenzustand.currentAction) return;
        Seitenzustand.playing = !Seitenzustand.playing;
        if (Seitenzustand.playing) {
            if (!Seitenzustand.currentAction.isRunning()) Seitenzustand.currentAction.play();
            Seitenzustand.currentAction.paused = false;
        } else {
            Seitenzustand.currentAction.paused = true;
        }
        playBtn.innerHTML = Seitenzustand.playing
            ? '<i class="fas fa-pause"></i>'
            : '<i class="fas fa-play"></i>';
    });

    stopBtn.addEventListener('click', () => {
        stopAnimation();
        playBtn.innerHTML = '<i class="fas fa-play"></i>';
        timeline.value = 0;
    });

    timeline.addEventListener('input', () => {
        if (Seitenzustand.currentAction && Seitenzustand.mixer) {
            const wasPaused = Seitenzustand.currentAction.paused;
            Seitenzustand.currentAction.paused = false;
            const clip = Seitenzustand.currentAction.getClip();
            const time = (parseInt(timeline.value) / 100) * clip.duration;
            Seitenzustand.mixer.setTime(time);
            Seitenzustand.currentAction.paused = wasPaused;
        }
    });
}
