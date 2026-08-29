/**
 * Viewer — Animation UI (tree-based BVH loader, playback controls).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { fetchRetargetedClipFromUrl } from '../retarget_hybrid.js';
import { convertToRigifySkinnedMesh } from './skinning.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';
import { Animationslader } from '../gemeinsam/animationslader.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Kategoriekasten } from '../gemeinsam/kategoriekasten.js';

export async function loadAnimations() {
    try {
        const data = await Serverabruf.json('/api/character/animations/');
        const tree = document.getElementById('anim-tree');
        if (!tree) return;
        tree.innerHTML = '';

        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();

        if (catNames.length === 0) {
            tree.innerHTML = '<div class="leer-hinweis">Keine Animationen gefunden</div>';
            return;
        }

        catNames.forEach(cat => {
            const anims = categories[cat];
            const {kasten: catDiv, koerper: body} =
                Kategoriekasten.bauen(cat, anims.length);

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

/**
 * BVH laden und abspielen. Der Ablauf steckt in `Animationslader` — er stand
 * bis zum Umbau am 16.08.2026 zweimal im Projekt, hier mit 105 und in
 * animation/wiedergabe.js mit 91 Zeilen.
 */
export async function loadBVHAnimation(url, name, fc) {
    return new Animationslader(state, {
        anhalten: zerstoeren => stopAnimation(zerstoeren),
        skinnen: gewichte => convertToRigifySkinnedMesh(null, gewichte),
        umzielen: (adresse, skelett, wahl) =>
            fetchRetargetedClipFromUrl(adresse, skelett, wahl),
        // Die Viewer-Seite zeigt Fortschritt in Sekunden und Bildern, ihre
        // Zeitleiste braucht dafür Name, Bildzahl und Dauer im Zustand.
        merken: (name2, bilder, dauer) => {
            state.currentAnimName = name2;
            state.currentAnimFrames = bilder;
            state.currentAnimDuration = dauer;
        },
        beschriften: (name2, bilder, dauer) =>
            `${name2} — 0/${Math.floor(dauer)}s  0/${bilder}f`,
    }).laden(url, name, fc);
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
        state.skeletonHelper = Skelettanzeige.bauen(state.scene, state.rigifySkeleton.rootBone);
    }
    state.playing = false;
}

// Register
fn.loadBVHAnimation = loadBVHAnimation;
