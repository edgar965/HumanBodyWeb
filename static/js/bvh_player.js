import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function initBVHPlayer({ videoId, canvasId, bvhUrl, fps = 30, overlayId = null, detectionUrl = null }) {
    const video = document.getElementById(videoId);
    const container = document.getElementById(canvasId);
    if (!video || !container) return;

    // --- Three.js setup ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    const width = container.clientWidth;
    const height = container.clientHeight || 400;

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(0, 100, 300);
    camera.layers.enable(0);
    camera.layers.enable(1);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.target.set(0, 80, 0);
    controls.update();

    // Grid on layer 1 so overlay camera doesn't see it
    const grid = new THREE.GridHelper(400, 20, 0x2a2a4a, 0x1f1f3a);
    grid.layers.set(1);
    scene.add(grid);
    scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(50, 200, 100);
    scene.add(dirLight);

    // --- Overlay setup (skeleton on top of video) ---
    let overlayRenderer = null;
    let overlayCamera = null;
    const overlayContainer = overlayId ? document.getElementById(overlayId) : null;

    if (overlayContainer) {
        overlayRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        overlayRenderer.setClearColor(0x000000, 0);
        const ow = overlayContainer.clientWidth || 640;
        const oh = overlayContainer.clientHeight || 360;
        overlayRenderer.setSize(ow, oh);
        overlayRenderer.setPixelRatio(window.devicePixelRatio);
        overlayContainer.appendChild(overlayRenderer.domElement);

        // Orthographic front-facing camera (only layer 0 = skeleton)
        overlayCamera = new THREE.OrthographicCamera(-100, 100, 100, -100, 0.1, 2000);
        overlayCamera.layers.set(0);
    }

    // State
    let mixer = null;
    let action = null;
    let skeletonHelper = null;
    let rootBone = null;
    let clipDuration = 0;
    let currentSpeed = 1;
    let isPlaying = false;

    // Detection flags (per-frame: true = person detected, false = not)
    let detectionFlags = null;
    if (detectionUrl) {
        fetch(detectionUrl)
            .then(r => r.json())
            .then(d => { if (d && d.length > 0) detectionFlags = d; })
            .catch(() => {});
    }

    // --- UI elements ---
    const btnPlayPause = document.getElementById('btnPlayPause');
    const playIcon = document.getElementById('playIcon');
    const timelineSlider = document.getElementById('timelineSlider');
    const timeCurrent = document.getElementById('timeCurrent');
    const timeDuration = document.getElementById('timeDuration');
    const speedBtns = document.querySelectorAll('.speed-btn');

    // --- Load BVH ---
    const loader = new BVHLoader();
    loader.load(bvhUrl, (result) => {
        rootBone = result.skeleton.bones[0];
        scene.add(rootBone);

        skeletonHelper = new THREE.SkeletonHelper(rootBone);
        skeletonHelper.material.linewidth = 2;
        scene.add(skeletonHelper);

        // Joint spheres
        const jointMat = new THREE.MeshBasicMaterial({ color: 0xe94560 });
        result.skeleton.bones.forEach((bone) => {
            const sphere = new THREE.Mesh(
                new THREE.SphereGeometry(1.5, 8, 8),
                jointMat,
            );
            bone.add(sphere);
        });

        // Animation mixer - LoopRepeat so action never auto-pauses
        mixer = new THREE.AnimationMixer(rootBone);
        action = mixer.clipAction(result.clip);
        action.play();
        clipDuration = result.clip.duration;

        // Auto-center main camera
        centerCamera(rootBone);

        // Fit overlay camera to skeleton bounds
        if (overlayCamera && overlayContainer) {
            fitOverlayCamera(rootBone);
        }

        // Timeline
        video.addEventListener('loadedmetadata', () => {
            timelineSlider.max = video.duration;
            timeDuration.textContent = formatTime(video.duration);
        });
        if (video.duration) {
            timelineSlider.max = video.duration;
            timeDuration.textContent = formatTime(video.duration);
        }
    }, undefined, (err) => {
        console.error('BVH load error:', err);
        container.innerHTML = '<div style="color:#e94560;padding:2rem;text-align:center;">Failed to load BVH file</div>';
    });

    function centerCamera(rootBone) {
        const box = new THREE.Box3();
        rootBone.traverse((child) => {
            if (child.isBone) {
                const pos = new THREE.Vector3();
                child.getWorldPosition(pos);
                box.expandByPoint(pos);
            }
        });
        const center = new THREE.Vector3();
        box.getCenter(center);
        const size = new THREE.Vector3();
        box.getSize(size);

        controls.target.copy(center);
        const maxDim = Math.max(size.x, size.y, size.z);
        camera.position.set(center.x, center.y, center.z + maxDim * 2);
        controls.update();
    }

    function fitOverlayCamera(rootBone) {
        const box = new THREE.Box3();
        rootBone.traverse((child) => {
            if (child.isBone) {
                const pos = new THREE.Vector3();
                child.getWorldPosition(pos);
                box.expandByPoint(pos);
            }
        });
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        const padding = 1.5;
        let halfH = (size.y * padding) / 2;
        let halfW = (size.x * padding) / 2;

        // Match container aspect ratio
        const cw = overlayContainer.clientWidth || 1;
        const ch = overlayContainer.clientHeight || 1;
        const containerAspect = cw / ch;
        const skeletonAspect = halfW / Math.max(halfH, 0.001);

        if (containerAspect > skeletonAspect) {
            halfW = halfH * containerAspect;
        } else {
            halfH = halfW / containerAspect;
        }

        overlayCamera.left = center.x - halfW;
        overlayCamera.right = center.x + halfW;
        overlayCamera.top = center.y + halfH;
        overlayCamera.bottom = center.y - halfH;
        overlayCamera.position.set(center.x, center.y, 500);
        overlayCamera.lookAt(center.x, center.y, 0);
        overlayCamera.updateProjectionMatrix();
    }

    // --- Sync loop ---
    function animate() {
        requestAnimationFrame(animate);

        if (mixer && video.duration) {
            // Map video time to BVH clip time (clamp to avoid LoopRepeat wrap)
            const t = Math.min(
                (video.currentTime / video.duration) * clipDuration,
                clipDuration - 0.0001
            );
            mixer.setTime(t);

            // Hide skeleton on frames where no person was detected
            if (detectionFlags) {
                const frameIdx = Math.min(
                    Math.floor((video.currentTime / video.duration) * detectionFlags.length),
                    detectionFlags.length - 1
                );
                const visible = detectionFlags[frameIdx];
                if (skeletonHelper) skeletonHelper.visible = visible;
                if (rootBone) rootBone.visible = visible;
            }
        }

        controls.update();
        renderer.render(scene, camera);

        // Overlay: render skeleton with transparent background
        if (overlayRenderer && overlayCamera) {
            const savedBg = scene.background;
            scene.background = null;
            overlayRenderer.render(scene, overlayCamera);
            scene.background = savedBg;
        }

        // Update timeline
        if (video.duration) {
            timelineSlider.value = video.currentTime;
            timeCurrent.textContent = formatTime(video.currentTime);
        }
    }
    animate();

    // --- Controls ---
    function togglePlayPause() {
        if (video.paused) {
            video.play();
            isPlaying = true;
            playIcon.className = 'fas fa-pause';
        } else {
            video.pause();
            isPlaying = false;
            playIcon.className = 'fas fa-play';
        }
    }

    function skip(delta) {
        video.currentTime = Math.max(0, Math.min(video.duration || 0, video.currentTime + delta));
    }

    function frameStep(direction) {
        video.pause();
        isPlaying = false;
        playIcon.className = 'fas fa-play';
        const frameDuration = 1 / fps;
        video.currentTime = Math.max(0, Math.min(video.duration || 0, video.currentTime + direction * frameDuration));
    }

    function setSpeed(speed) {
        currentSpeed = speed;
        video.playbackRate = speed;
        if (action) action.timeScale = speed;
        speedBtns.forEach(btn => {
            btn.classList.toggle('active', parseFloat(btn.dataset.speed) === speed);
        });
    }

    // Button handlers
    btnPlayPause.addEventListener('click', togglePlayPause);
    document.getElementById('btnSkipBack10').addEventListener('click', () => skip(-10));
    document.getElementById('btnSkipBack1').addEventListener('click', () => skip(-1));
    document.getElementById('btnSkipFwd1').addEventListener('click', () => skip(1));
    document.getElementById('btnSkipFwd10').addEventListener('click', () => skip(10));
    document.getElementById('btnFrameBack').addEventListener('click', () => frameStep(-1));
    document.getElementById('btnFrameFwd').addEventListener('click', () => frameStep(1));

    // Timeline slider
    timelineSlider.addEventListener('input', () => {
        video.currentTime = parseFloat(timelineSlider.value);
    });

    // Speed buttons
    speedBtns.forEach(btn => {
        btn.addEventListener('click', () => setSpeed(parseFloat(btn.dataset.speed)));
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT') return;
        switch (e.key) {
            case ' ':
                e.preventDefault();
                togglePlayPause();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                if (e.shiftKey) skip(-10);
                else if (e.ctrlKey) frameStep(-1);
                else skip(-1);
                break;
            case 'ArrowRight':
                e.preventDefault();
                if (e.shiftKey) skip(10);
                else if (e.ctrlKey) frameStep(1);
                else skip(1);
                break;
        }
    });

    // Video events
    video.addEventListener('play', () => {
        isPlaying = true;
        playIcon.className = 'fas fa-pause';
    });
    video.addEventListener('pause', () => {
        isPlaying = false;
        playIcon.className = 'fas fa-play';
    });
    video.addEventListener('ended', () => {
        isPlaying = false;
        playIcon.className = 'fas fa-play';
    });

    // Resize handling
    function onResize() {
        const w = container.clientWidth;
        const h = container.clientHeight || 400;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);

        // Resize overlay to match video element
        if (overlayRenderer && overlayContainer) {
            const ow = overlayContainer.clientWidth;
            const oh = overlayContainer.clientHeight;
            if (ow > 0 && oh > 0) {
                overlayRenderer.setSize(ow, oh);
            }
        }
    }
    window.addEventListener('resize', onResize);

    if (typeof ResizeObserver !== 'undefined') {
        new ResizeObserver(onResize).observe(container);
        if (overlayContainer) {
            new ResizeObserver(onResize).observe(overlayContainer);
        }
    }
}

function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '00:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}
