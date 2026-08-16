/**
 * HumanBody Animations — Three.js viewer with BVH animation tree + playback.
 * Loads the character mesh statically, plays BVH skeletons overlaid.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import './retarget_hybrid.js?v=32';
import './gemeinsam/kodierung.js';
import { Seitenzustand } from './animation/seitenzustand.js';
import { loadSkinColors, applySceneSettings } from './animation/material.js';
import { loadAnimationTree, setupAnimManagement } from './animation/baum.js';
import { loadMesh, loadRigifySkeleton, loadSkinWeights } from './animation/netz.js';
import { loadBVHAnimation, bindPlaybackControls, animate } from './animation/wiedergabe.js';
import { initSaveButtons } from './animation/speichern.js';



// Rigify Skeleton + Skinning
// Rig
// Skin colors per ethnicity (from API)
// =========================================================================
// Initialization
// =========================================================================
async function init() {
    const canvas = document.getElementById('viewer-canvas');
    const container = canvas.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;

    // Renderer
    Seitenzustand.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    Seitenzustand.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    Seitenzustand.renderer.setSize(w, h);
    Seitenzustand.renderer.outputColorSpace = THREE.SRGBColorSpace;
    Seitenzustand.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    Seitenzustand.renderer.toneMappingExposure = 1.6;

    // Scene
    Seitenzustand.scene = new THREE.Scene();
    Seitenzustand.scene.background = new THREE.Color(0x1a1a2e);

    // Camera
    Seitenzustand.camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    Seitenzustand.camera.position.set(0, 1.0, 3.5);

    // Controls
    Seitenzustand.controls = new OrbitControls(Seitenzustand.camera, canvas);
    Seitenzustand.controls.target.set(0, 0.9, 0);
    Seitenzustand.controls.enableDamping = true;
    Seitenzustand.controls.dampingFactor = 0.08;
    Seitenzustand.controls.minDistance = 0.5;
    Seitenzustand.controls.maxDistance = 15;
    Seitenzustand.controls.update();

    // Lighting
    const keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
    keyLight.position.set(2, 4, -5);
    Seitenzustand.scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
    fillLight.position.set(-3, 3, -4);
    Seitenzustand.scene.add(fillLight);

    const backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
    backLight.position.set(0, 4, 5);
    Seitenzustand.scene.add(backLight);

    const ambient = new THREE.AmbientLight(0xffffff, 0.8);
    Seitenzustand.scene.add(ambient);

    // Apply Seitenzustand.scene settings from localStorage
    applySceneSettings(keyLight, fillLight, backLight, ambient);

    // Ground grid
    const grid = new THREE.GridHelper(4, 20, 0x333355, 0x222244);
    Seitenzustand.scene.add(grid);

    // Resize
    window.addEventListener('resize', Seitenzustand.groesseAnpassen);

    // Panel toggle
    document.querySelectorAll('.panel-section h3').forEach(h3 => {
        h3.addEventListener('click', () => {
            h3.closest('.panel-section').classList.toggle('collapsed');
        });
    });

    // Animation Seitenzustand.controls
    bindPlaybackControls();

    // Demo animation button — Play/Pause toggle
    const demoBtn = document.getElementById('play-demo-anim');
    if (demoBtn) {
        demoBtn.addEventListener('click', () => {
            if (!Seitenzustand.currentAction) {
                loadBVHAnimation('/api/character/bvh/Mixamo/Catwalk_Idle_02/', 'Catwalk Idle 02', 0);
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
            } else if (Seitenzustand.playing) {
                Seitenzustand.currentAction.paused = true;
                Seitenzustand.playing = false;
                demoBtn.innerHTML = '<i class="fas fa-play"></i>';
                demoBtn.classList.remove('active');
                const playBtn = document.getElementById('anim-play');
                if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>';
            } else {
                if (!Seitenzustand.currentAction.isRunning()) Seitenzustand.currentAction.play();
                Seitenzustand.currentAction.paused = false;
                Seitenzustand.playing = true;
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
                const playBtn = document.getElementById('anim-play');
                if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            }
        });
    }

    // Rig toggle — single SkeletonHelper from Seitenzustand.rigifySkeleton
    const rigToggle = document.getElementById('rig-toggle');
    if (rigToggle) {
        rigToggle.addEventListener('click', () => {
            Seitenzustand.rigVisible = !Seitenzustand.rigVisible;
            if (Seitenzustand.rigVisible) {
                if (!Seitenzustand.skeletonHelper && Seitenzustand.rigifySkeleton) {
                    Seitenzustand.skeletonHelper = new THREE.SkeletonHelper(Seitenzustand.rigifySkeleton.rootBone);
                    Seitenzustand.skeletonHelper.material.depthTest = false;
                    Seitenzustand.skeletonHelper.material.depthWrite = false;
                    Seitenzustand.skeletonHelper.material.color.set(0x00ffaa);
                    Seitenzustand.skeletonHelper.material.linewidth = 2;
                    Seitenzustand.skeletonHelper.renderOrder = 999;
                    Seitenzustand.scene.add(Seitenzustand.skeletonHelper);
                }
                if (Seitenzustand.skeletonHelper) Seitenzustand.skeletonHelper.visible = true;
            } else {
                if (Seitenzustand.skeletonHelper) Seitenzustand.skeletonHelper.visible = false;
            }
            rigToggle.classList.toggle('active', Seitenzustand.rigVisible);
        });
    }

    // Model toggle
    const modelToggle = document.getElementById('model-toggle');
    if (modelToggle) {
        modelToggle.addEventListener('click', () => {
            if (Seitenzustand.bodyMesh) Seitenzustand.bodyMesh.visible = !Seitenzustand.bodyMesh.visible;
            modelToggle.classList.toggle('active', Seitenzustand.bodyMesh && Seitenzustand.bodyMesh.visible);
        });
    }

    // Save buttons
    initSaveButtons();

    // Start render loop
    animate();

    // Load data
    loadMesh();
    loadRigifySkeleton();
    loadSkinWeights();
    loadSkinColors();
    loadAnimationTree();
    setupAnimManagement();
}















// =========================================================================
// DEF Skeleton + Skin Weights
// =========================================================================



// buildRigifySkeleton() imported from rigify_skeleton_builder.js


// Retarget via server-side API (retarget_hybrid.js)





// (Rig visualization now uses SkeletonHelper from Seitenzustand.rigifySkeleton — no separate rigGroup)

// =========================================================================
// Utility
// =========================================================================









// =========================================================================
// Boot
// =========================================================================
init();
