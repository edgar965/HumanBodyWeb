/**
 * Animationsbaum und Wiedergabe der Vergleichsseite.
 *
 * Aus skeleton_test.js herausgeloest (Umbau 16.08.2026).
 */

import * as THREE from 'three';
import '../animation/wiedergabe.js';
import { Testzustand } from './testzustand.js';
import { removeBoneViz } from './knochenbild.js';
import { detectBVHFormat, fetchRetargetedClipFromUrl } from '../retarget_hybrid.js?v=32';
import { placeBvhSkeleton } from '../skeleton_test.js';


// =========================================================================
// Animation Tree
// =========================================================================
export async function loadAnimationTree() {
    try {
        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        Testzustand.allAnimations = data.categories || {};

        const tree = document.getElementById('anim-tree');
        tree.innerHTML = '';

        const catNames = Object.keys(Testzustand.allAnimations).sort();

        if (catNames.length === 0) {
            tree.innerHTML = '<div style="padding:16px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden</div>';
            return;
        }

        catNames.forEach(cat => {
            const anims = Testzustand.allAnimations[cat];
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
                item.dataset.category = cat;
                item.innerHTML = `<span>${anim.name}</span><span class="frames">${anim.frames}f</span>`;
                item.addEventListener('click', () => {
                    tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                    loadAndPlayAnimation(anim.url, anim.name, anim.frames, cat);
                });
                body.appendChild(item);
            });

            catDiv.appendChild(body);
            tree.appendChild(catDiv);
        });

        // Auto-load first CMU and MocapNET animations for rest-pose display
        autoLoadRestPoseSkeletons();
    } catch (e) {
        console.error('Failed to load animations:', e);
    }
}

// =========================================================================
// Auto-load first BVH of each type for rest-pose display
// =========================================================================
export function autoLoadRestPoseSkeletons() {
    const FORMAT_TO_SKEL = { CMU: 'cmu', MIXAMO: 'mixamo', MOCAPNET: 'mocapnet', OPENPOSE: 'openpose', BANDAI: 'bandai', SMPL: 'smpl' };
    const loaded = new Set();

    // Load first animation from each category, detect format, place skeleton
    for (const cat of Object.keys(Testzustand.allAnimations).sort()) {
        const anims = Testzustand.allAnimations[cat];
        if (!anims || anims.length === 0) continue;

        Testzustand.bvhLoader.load(anims[0].url, (result) => {
            const format = detectBVHFormat(result.skeleton.bones);
            const skelKey = FORMAT_TO_SKEL[format];
            if (skelKey && !loaded.has(skelKey) && !Testzustand.skeletons[skelKey].bvhResult) {
                loaded.add(skelKey);
                placeBvhSkeleton(result, skelKey);
                Testzustand.skeletons[skelKey].bvhResult = result;
            }
        });
    }
}

// =========================================================================
// Load & Play Animation on all 3 Testzustand.skeletons
// =========================================================================
export function loadAndPlayAnimation(url, name, fc, category) {
    stopAnimation();
    document.getElementById('anim-info').textContent = `Lade ${name}...`;

    Testzustand.bvhLoader.load(url, async (result) => {
        const bones = result.skeleton.bones;
        if (bones.length === 0) return;

        const format = detectBVHFormat(bones);
        Testzustand.currentBvhResult = result;
        Testzustand.currentFormat = format;

        // Create a multi-target Testzustand.mixer using a common root
        // We use separate mixers for each skeleton

        const mixers = [];

        // --- BVH skeleton (position depends on format) ---
        const bvhKey = format === 'CMU' ? 'cmu'
                     : format === 'MIXAMO' ? 'mixamo'
                     : format === 'BANDAI' ? 'bandai'
                     : format === 'AIST' ? 'smpl'
                     : format === 'OPENPOSE' ? 'openpose'
                     : 'mocapnet';
        const bvhSkel = Testzustand.skeletons[bvhKey];

        // Remove old BVH skeleton
        if (bvhSkel.wrapper) {
            bvhSkel.group.remove(bvhSkel.wrapper);
            bvhSkel.wrapper = null;
        }
        removeBoneViz(bvhKey);
        bvhSkel.labels.forEach(lbl => lbl.parent && lbl.parent.remove(lbl));
        bvhSkel.labels = [];

        // Place the new BVH skeleton
        placeBvhSkeleton(result, bvhKey);

        // Play animation on BVH skeleton
        const bvhMixer = new THREE.AnimationMixer(bvhSkel.rootBone);
        const bvhAction = bvhMixer.clipAction(result.clip);
        bvhAction.play();
        mixers.push(bvhMixer);
        window._cmuMixer = bvhMixer;
        window._cmuRootBone = bvhSkel.rootBone;

        // --- DEF skeleton (left, red) — retargeted ---
        if (Testzustand.skeletons.def.skeleton && Testzustand.rigifySkeletonData && Testzustand.skinWeightData) {
            try {
                Testzustand.skeletons.def.skeleton.skeleton.pose();
                const clip = await fetchRetargetedClipFromUrl(url, Testzustand.skeletons.def.skeleton, {});
                const defMixer = new THREE.AnimationMixer(Testzustand.skeletons.def.rootBone);
                const defAction = defMixer.clipAction(clip);
                defAction.play();
                mixers.push(defMixer);
                window._defMixer = defMixer;
                window._defRootBone = Testzustand.skeletons.def.rootBone;
                window._defClip = clip;
            } catch (e) {
                console.error('DEF retarget failed:', e.message);
            }
        }

        // Store combined Testzustand.mixer
        Testzustand.mixer = {
            _mixers: mixers,
            update(dt) { for (const m of this._mixers) m.update(dt); },
            stopAllAction() { for (const m of this._mixers) m.stopAllAction(); },
            setTime(t) { for (const m of this._mixers) m.setTime(t); },
        };
        Testzustand.currentAction = { clip: result.clip, paused: false };
        Testzustand.playing = true;

        document.getElementById('anim-play').innerHTML = '<i class="fas fa-pause"></i>';
        document.getElementById('anim-info').textContent =
            `${name} — ${fc}f — ${result.clip.duration.toFixed(1)}s — ${format}`;
    }, undefined, (err) => {
        console.error('Failed to load BVH:', err);
        document.getElementById('anim-info').textContent = `Fehler: ${name}`;
    });
}

export function stopAnimation() {
    if (Testzustand.mixer) {
        Testzustand.mixer.stopAllAction();
        Testzustand.mixer = null;
    }
    Testzustand.currentAction = null;
    Testzustand.currentBvhResult = null;

    // Reset DEF skeleton to rest pose
    if (Testzustand.skeletons.def.skeleton) {
        Testzustand.skeletons.def.skeleton.skeleton.pose();
    }

    Testzustand.playing = false;
}

// =========================================================================
// Playback Testzustand.controls
// =========================================================================
export function bindPlaybackControls() {
    const playBtn = document.getElementById('anim-play');
    const stopBtn = document.getElementById('anim-stop');
    const timeline = document.getElementById('anim-timeline');

    playBtn.addEventListener('click', () => {
        if (!Testzustand.currentAction) return;
        Testzustand.playing = !Testzustand.playing;
        Testzustand.currentAction.paused = !Testzustand.playing;
        playBtn.innerHTML = Testzustand.playing
            ? '<i class="fas fa-pause"></i>'
            : '<i class="fas fa-play"></i>';
    });

    stopBtn.addEventListener('click', () => {
        stopAnimation();
        playBtn.innerHTML = '<i class="fas fa-play"></i>';
        timeline.value = 0;
        document.getElementById('anim-info').textContent = '—';
        document.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
    });

    timeline.addEventListener('input', () => {
        if (Testzustand.currentAction && Testzustand.mixer) {
            const clip = Testzustand.currentAction.clip;
            const time = (parseInt(timeline.value) / 100) * clip.duration;
            Testzustand.mixer.setTime(time);
        }
    });
}
