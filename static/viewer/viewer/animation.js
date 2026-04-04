/**
 * Viewer — Animation UI (tree-based BVH loader, playback controls).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import { detectBVHFormat, fetchRetargetedClipFromUrl } from '../retarget_hybrid.js?v=32';
import { convertToRigifySkinnedMesh } from './skinning.js';

export async function loadAnimations() {
    try {
        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        const tree = document.getElementById('anim-tree');
        if (!tree) return;
        tree.innerHTML = '';

        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();

        if (catNames.length === 0) {
            tree.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden</div>';
            return;
        }

        catNames.forEach(cat => {
            const anims = categories[cat];
            const catDiv = document.createElement('div');
            catDiv.className = 'anim-category';

            const header = document.createElement('div');
            header.className = 'anim-category-header';
            header.innerHTML = `<span class="cat-chevron"><i class="fas fa-chevron-right"></i></span>
                <span>${cat}</span>
                <span class="cat-count">${anims.length}</span>`;
            header.addEventListener('click', () => catDiv.classList.toggle('open'));
            catDiv.appendChild(header);

            const body = document.createElement('div');
            body.className = 'anim-category-body';

            anims.forEach(anim => {
                const item = document.createElement('div');
                item.className = 'anim-item';
                item.dataset.url = anim.url;
                item.innerHTML = `<span>${anim.name}</span><span class="frames">${anim.frames}f</span>`;
                item.addEventListener('click', () => {
                    tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                    loadBVHAnimation(anim.url, anim.name, anim.frames);
                });
                body.appendChild(item);
            });

            catDiv.appendChild(body);
            tree.appendChild(catDiv);
        });

        bindPlaybackControls();
    } catch (e) {
        console.error('Failed to load animations:', e);
    }
}

function bindPlaybackControls() {
    const playBtn = document.getElementById('anim-play');
    const stopBtn = document.getElementById('anim-stop');
    const timeline = document.getElementById('anim-timeline');
    const speedSlider = document.getElementById('anim-speed');
    const speedLabel = document.getElementById('speed-label');

    if (speedSlider && speedLabel) {
        speedSlider.addEventListener('input', () => {
            const speed = parseInt(speedSlider.value) / 100;
            speedLabel.textContent = `Speed: ${speed.toFixed(1)}x`;
            if (state.mixer) state.mixer.timeScale = speed;
        });
    }

    if (playBtn) {
        playBtn.addEventListener('click', () => {
            if (!state.currentAction) return;
            state.playing = !state.playing;
            if (state.playing) {
                if (!state.currentAction.isRunning()) state.currentAction.play();
                state.currentAction.paused = false;
            } else {
                state.currentAction.paused = true;
            }
            playBtn.innerHTML = state.playing
                ? '<i class="fas fa-pause"></i>'
                : '<i class="fas fa-play"></i>';
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            stopAnimation();
            if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>';
            if (timeline) timeline.value = 0;
            state.currentAnimName = '';
            state.currentAnimFrames = 0;
            state.currentAnimDuration = 0;
            const info = document.getElementById('anim-info');
            if (info) info.textContent = '\u2014';
        });
    }

    if (timeline) {
        timeline.addEventListener('input', () => {
            if (state.currentAction && state.mixer) {
                const wasPaused = state.currentAction.paused;
                state.currentAction.paused = false;
                const clip = state.currentAction.getClip();
                const time = (parseInt(timeline.value) / 100) * clip.duration;
                state.mixer.setTime(time);
                state.currentAction.paused = wasPaused;
                if (state.currentAnimDuration > 0) {
                    const curSec = Math.floor(time);
                    const totSec = Math.floor(state.currentAnimDuration);
                    const curFrame = Math.round((time / state.currentAnimDuration) * state.currentAnimFrames);
                    const info = document.getElementById('anim-info');
                    if (info) info.textContent = `${state.currentAnimName} \u2014 ${curSec}/${totSec}s  ${curFrame}/${state.currentAnimFrames}f`;
                }
            }
        });
    }
}

export async function loadBVHAnimation(url, name, fc) {
    stopAnimation(true);

    const info = document.getElementById('anim-info');
    if (info) info.textContent = `Lade ${name || 'Animation'}...`;

    // DEF skeleton path
    if (state.rigifySkeletonData && state.skinWeightData && state.bodyMesh) {
        if (!state.isSkinned) {
            convertToRigifySkinnedMesh(null, state.skinWeightData);
        }
        let bodyH = 1.68;
        const bb = new THREE.Box3().setFromObject(state.bodyMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;

        try {
            const clip = await fetchRetargetedClipFromUrl(url, state.rigifySkeleton, { bodyHeight: bodyH });
            console.log(`Retargeted clip: ${clip.tracks.length} tracks, ${clip.duration.toFixed(2)}s`);

            if (!state.skeletonHelper) {
                state.skeletonHelper = new THREE.SkeletonHelper(state.rigifySkeleton.rootBone);
                state.skeletonHelper.material.depthTest = false;
                state.skeletonHelper.material.depthWrite = false;
                state.skeletonHelper.material.color.set(0x00ffaa);
                state.skeletonHelper.material.linewidth = 2;
                state.skeletonHelper.renderOrder = 999;
                state.skeletonHelper.visible = state.rigVisible;
                state.scene.add(state.skeletonHelper);
            }

            state.mixer = new THREE.AnimationMixer(state.bodyMesh);
            const ss = document.getElementById('anim-speed');
            if (ss) state.mixer.timeScale = parseInt(ss.value) / 100;
            state.currentAction = state.mixer.clipAction(clip);
            state.currentAction.play();
            state.playing = true;

            state.currentAnimName = name || 'Animation';
            state.currentAnimFrames = fc || 0;
            state.currentAnimDuration = state.currentAction ? state.currentAction.getClip().duration : clip.duration;

            const playBtn = document.getElementById('anim-play');
            if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            if (info) info.textContent = `${state.currentAnimName} \u2014 0/${Math.floor(state.currentAnimDuration)}s  0/${state.currentAnimFrames}f`;
            return;
        } catch (e) {
            console.error('Server retarget failed:', e);
        }
    }

    // Fallback: separate BVH skeleton
    state.bvhLoader.load(url, (result) => {
        const bvhBones = result.skeleton.bones;
        if (bvhBones.length === 0) return;

        const rootBone = bvhBones[0];
        rootBone.updateWorldMatrix(true, true);
        const skelBox = new THREE.Box3();
        const tmpVec = new THREE.Vector3();
        bvhBones.forEach(b => {
            b.updateWorldMatrix(true, false);
            b.getWorldPosition(tmpVec);
            skelBox.expandByPoint(tmpVec);
        });
        const skelHeight = skelBox.max.y - skelBox.min.y;
        let bodyHeight = 1.75;
        if (state.bodyMesh) {
            const bodyBox = new THREE.Box3().setFromObject(state.bodyMesh);
            if (!bodyBox.isEmpty()) bodyHeight = bodyBox.max.y - bodyBox.min.y;
        }
        const scale = bodyHeight / Math.max(skelHeight, 0.01);

        state.skelWrapper = new THREE.Group();
        state.skelWrapper.scale.set(scale, scale, scale);
        state.skelWrapper.add(rootBone);
        state.scene.add(state.skelWrapper);

        if (state.skeletonHelper) state.scene.remove(state.skeletonHelper);
        state.skeletonHelper = new THREE.SkeletonHelper(rootBone);
        state.skeletonHelper.material.depthTest = false;
        state.skeletonHelper.material.depthWrite = false;
        state.skeletonHelper.material.color.set(0x00ffaa);
        state.skeletonHelper.material.linewidth = 2;
        state.skeletonHelper.renderOrder = 999;
        state.skeletonHelper.visible = state.rigVisible;
        state.scene.add(state.skeletonHelper);

        state.mixer = new THREE.AnimationMixer(rootBone);
        const ss2 = document.getElementById('anim-speed');
        if (ss2) state.mixer.timeScale = parseInt(ss2.value) / 100;
        state.currentAction = state.mixer.clipAction(result.clip);
        state.currentAction.play();
        state.playing = true;

        state.currentAnimName = name || 'Animation';
        state.currentAnimFrames = fc || 0;
        state.currentAnimDuration = state.currentAction ? state.currentAction.getClip().duration : result.clip.duration;

        const playBtn = document.getElementById('anim-play');
        if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
        if (info) info.textContent = `${state.currentAnimName} \u2014 0/${Math.floor(state.currentAnimDuration)}s  0/${state.currentAnimFrames}f`;
    }, undefined, (err) => {
        console.error('Failed to load BVH:', err);
        if (info) info.textContent = `Fehler: ${name || url}`;
    });
}

export function stopAnimation(destroy = false) {
    if (state.currentAction) {
        state.currentAction.stop();
        state.currentAction.reset();
        if (destroy) state.currentAction = null;
    }
    if (state.mixer && destroy) {
        state.mixer.stopAllAction();
        state.mixer = null;
    }
    if (state.isSkinned && state.bodyMesh && state.bodyMesh.isSkinnedMesh) {
        state.bodyMesh.skeleton.pose();
    }
    if (state.skelWrapper) {
        state.scene.remove(state.skelWrapper);
        state.skelWrapper = null;
    }
    if (state.skeletonHelper) {
        state.scene.remove(state.skeletonHelper);
        state.skeletonHelper = null;
    }
    if (state.rigVisible && state.rigifySkeleton) {
        state.skeletonHelper = new THREE.SkeletonHelper(state.rigifySkeleton.rootBone);
        state.skeletonHelper.material.depthTest = false;
        state.skeletonHelper.material.depthWrite = false;
        state.skeletonHelper.material.color.set(0x00ffaa);
        state.skeletonHelper.material.linewidth = 2;
        state.skeletonHelper.renderOrder = 999;
        state.scene.add(state.skeletonHelper);
    }
    state.playing = false;
}

// Register
fn.loadAnimations = loadAnimations;
fn.loadBVHAnimation = loadBVHAnimation;
fn.stopAnimation = stopAnimation;
