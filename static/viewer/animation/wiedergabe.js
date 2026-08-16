/**
 * Wiedergabe: BVH laden, abspielen, anhalten, Bedienknoepfe.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026).
 */

import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { fetchRetargetedClipFromUrl } from '../retarget_hybrid.js?v=32';
import { Seitenzustand } from './seitenzustand.js';
import { convertToRigifySkinnedMesh, skelWrapper } from './netz.js';


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

export async function loadBVHAnimation(url, name, fc) {
    stopAnimation(true);

    document.getElementById('anim-info').textContent = `Lade ${name}...`;

    if (Seitenzustand.rigifySkeletonData && Seitenzustand.skinWeightData && Seitenzustand.bodyMesh) {
        // Server-side retarget path: skin mesh + retarget BVH via API
        if (!Seitenzustand.isSkinned) convertToRigifySkinnedMesh(null, Seitenzustand.skinWeightData);

        let bodyH = 1.68;
        const bb = new THREE.Box3().setFromObject(Seitenzustand.bodyMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;

        try {
            const clip = await fetchRetargetedClipFromUrl(url, Seitenzustand.rigifySkeleton, { bodyHeight: bodyH });

            // Ensure SkeletonHelper exists for DEF skeleton
            if (!Seitenzustand.skeletonHelper) {
                Seitenzustand.skeletonHelper = new THREE.SkeletonHelper(Seitenzustand.rigifySkeleton.rootBone);
                Seitenzustand.skeletonHelper.material.depthTest = false;
                Seitenzustand.skeletonHelper.material.depthWrite = false;
                Seitenzustand.skeletonHelper.material.color.set(0x00ffaa);
                Seitenzustand.skeletonHelper.material.linewidth = 2;
                Seitenzustand.skeletonHelper.renderOrder = 999;
                Seitenzustand.skeletonHelper.visible = Seitenzustand.rigVisible;
                Seitenzustand.scene.add(Seitenzustand.skeletonHelper);
            }

            // Play retargeted clip on the SkinnedMesh
            Seitenzustand.mixer = new THREE.AnimationMixer(Seitenzustand.bodyMesh);
            const ss = document.getElementById('anim-speed');
            if (ss) Seitenzustand.mixer.timeScale = parseInt(ss.value) / 100;
            Seitenzustand.currentAction = Seitenzustand.mixer.clipAction(clip);
            Seitenzustand.currentAction.play();
            Seitenzustand.playing = true;

            document.getElementById('anim-play').innerHTML = '<i class="fas fa-pause"></i>';
            document.getElementById('anim-info').textContent =
                `${name} — ${fc}f — ${clip.duration.toFixed(1)}s`;
        } catch (e) {
            console.error('Server retarget failed:', e);
            document.getElementById('anim-info').textContent = `Fehler: ${name}`;
        }
    } else {
        // Fallback: BVH skeleton overlay (no skinning data available)
        bvhLoader.load(url, (result) => {
            const bones = result.skeleton.bones;
            if (bones.length === 0) return;

            const rootBone = bones[0];
            rootBone.updateWorldMatrix(true, true);
            const skelBox = new THREE.Box3();
            const tmpVec = new THREE.Vector3();
            bones.forEach(b => {
                b.updateWorldMatrix(true, false);
                b.getWorldPosition(tmpVec);
                skelBox.expandByPoint(tmpVec);
            });
            const skelHeight = skelBox.max.y - skelBox.min.y;

            let bodyHeight = 1.75;
            if (Seitenzustand.bodyMesh) {
                const bodyBox = new THREE.Box3().setFromObject(Seitenzustand.bodyMesh);
                if (!bodyBox.isEmpty()) bodyHeight = bodyBox.max.y - bodyBox.min.y;
            }

            skelWrapper = new THREE.Group();
            const scale = bodyHeight / Math.max(skelHeight, 0.01);
            skelWrapper.scale.set(scale, scale, scale);
            skelWrapper.add(rootBone);
            Seitenzustand.scene.add(skelWrapper);

            if (Seitenzustand.skeletonHelper) Seitenzustand.scene.remove(Seitenzustand.skeletonHelper);
            Seitenzustand.skeletonHelper = new THREE.SkeletonHelper(rootBone);
            Seitenzustand.skeletonHelper.material.depthTest = false;
            Seitenzustand.skeletonHelper.material.depthWrite = false;
            Seitenzustand.skeletonHelper.material.color.set(0x00ffaa);
            Seitenzustand.skeletonHelper.material.linewidth = 2;
            Seitenzustand.skeletonHelper.renderOrder = 999;
            Seitenzustand.skeletonHelper.visible = Seitenzustand.rigVisible;
            Seitenzustand.scene.add(Seitenzustand.skeletonHelper);

            Seitenzustand.mixer = new THREE.AnimationMixer(rootBone);
            const ss2 = document.getElementById('anim-speed');
            if (ss2) Seitenzustand.mixer.timeScale = parseInt(ss2.value) / 100;
            Seitenzustand.currentAction = Seitenzustand.mixer.clipAction(result.clip);
            Seitenzustand.currentAction.play();
            Seitenzustand.playing = true;

            document.getElementById('anim-play').innerHTML = '<i class="fas fa-pause"></i>';
            document.getElementById('anim-info').textContent =
                `${name} — ${fc}f — ${result.clip.duration.toFixed(1)}s`;
        }, undefined, (err) => {
            console.error('Failed to load BVH:', err);
            document.getElementById('anim-info').textContent = `Fehler: ${name}`;
        });
    }
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
    if (skelWrapper) { Seitenzustand.scene.remove(skelWrapper); skelWrapper = null; }
    if (Seitenzustand.skeletonHelper) { Seitenzustand.scene.remove(Seitenzustand.skeletonHelper); Seitenzustand.skeletonHelper = null; }
    if (Seitenzustand.rigVisible && Seitenzustand.rigifySkeleton) {
        Seitenzustand.skeletonHelper = new THREE.SkeletonHelper(Seitenzustand.rigifySkeleton.rootBone);
        Seitenzustand.skeletonHelper.material.depthTest = false;
        Seitenzustand.skeletonHelper.material.depthWrite = false;
        Seitenzustand.skeletonHelper.material.color.set(0x00ffaa);
        Seitenzustand.skeletonHelper.material.linewidth = 2;
        Seitenzustand.skeletonHelper.renderOrder = 999;
        Seitenzustand.scene.add(Seitenzustand.skeletonHelper);
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
