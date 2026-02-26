import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

console.log('[bvh_player] v0.75 loaded');

export function initBVHPlayer({ videoId, canvasId, bvhUrl, fps = 30, overlayId = null, detectionUrl = null, keypointsUrl = null }) {
    console.log('[bvh_player] initBVHPlayer called');
    const video = document.getElementById(videoId);
    const container = document.getElementById(canvasId);
    if (!video || !container) return;

    // --- Three.js setup (3D panel) ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    const width = container.clientWidth;
    const height = container.clientHeight || 400;

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(0, 100, 300);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.target.set(0, 80, 0);
    controls.update();

    const grid = new THREE.GridHelper(400, 20, 0x2a2a4a, 0x1f1f3a);
    scene.add(grid);
    scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(50, 200, 100);
    scene.add(dirLight);

    // --- 2D Canvas overlay (skeleton on top of video) ---
    let overlayCanvas = null;
    let overlayCtx = null;
    const overlayContainer = overlayId ? document.getElementById(overlayId) : null;

    if (overlayContainer) {
        overlayCanvas = document.createElement('canvas');
        overlayCanvas.style.width = '100%';
        overlayCanvas.style.height = '100%';
        overlayCanvas.style.position = 'absolute';
        overlayCanvas.style.top = '0';
        overlayCanvas.style.left = '0';
        overlayContainer.appendChild(overlayCanvas);
        overlayCtx = overlayCanvas.getContext('2d');
        _resizeOverlayCanvas();
    }

    function _resizeOverlayCanvas() {
        if (!overlayCanvas || !overlayContainer) return;
        const ow = overlayContainer.clientWidth;
        const oh = overlayContainer.clientHeight;
        if (ow > 0 && oh > 0) {
            overlayCanvas.width = ow * window.devicePixelRatio;
            overlayCanvas.height = oh * window.devicePixelRatio;
            overlayCtx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
        }
    }

    // State
    let mixer = null;
    let action = null;
    let skeletonHelper = null;
    let rootBone = null;
    let clipDuration = 0;
    let currentSpeed = 1;
    let isPlaying = false;

    // Detection flags (per-frame boolean)
    let detectionFlags = null;
    if (detectionUrl) {
        fetch(detectionUrl)
            .then(r => r.json())
            .then(d => { if (d && d.length > 0) detectionFlags = d; })
            .catch(() => {});
    }

    // 2D keypoints for overlay
    let keypointsData = null;
    if (keypointsUrl) {
        fetch(keypointsUrl)
            .then(r => r.json())
            .then(d => { if (d && d.frames && d.frames.length > 0) keypointsData = d; })
            .catch(() => {});
    }

    // --- UI elements ---
    const btnPlayPause = document.getElementById('btnPlayPause');
    const playIcon = document.getElementById('playIcon');
    const timelineSlider = document.getElementById('timelineSlider');
    const timeCurrent = document.getElementById('timeCurrent');
    const timeDuration = document.getElementById('timeDuration');
    const speedBtns = document.querySelectorAll('.speed-btn');

    // --- Load BVH (3D panel only) ---
    const loader = new BVHLoader();
    const BODY_BONE_NAMES = new Set([
        'hip', 'abdomen', 'chest', 'neck', 'neck1', 'head',
        'rCollar', 'rShldr', 'rForeArm', 'rHand',
        'lCollar', 'lShldr', 'lForeArm', 'lHand',
        'rButtock', 'rThigh', 'rShin', 'rFoot',
        'lButtock', 'lThigh', 'lShin', 'lFoot',
    ]);

    loader.load(bvhUrl, (result) => {
        rootBone = result.skeleton.bones[0];
        scene.add(rootBone);

        skeletonHelper = new THREE.SkeletonHelper(rootBone);
        skeletonHelper.material.linewidth = 2;
        scene.add(skeletonHelper);

        // Joint spheres — only on body bones
        const jointMat = new THREE.MeshBasicMaterial({ color: 0xe94560 });
        result.skeleton.bones.forEach((bone) => {
            if (!BODY_BONE_NAMES.has(bone.name)) return;
            const sphere = new THREE.Mesh(
                new THREE.SphereGeometry(1.5, 8, 8),
                jointMat,
            );
            bone.add(sphere);
        });

        // Animation mixer
        mixer = new THREE.AnimationMixer(rootBone);
        action = mixer.clipAction(result.clip);
        action.play();
        clipDuration = result.clip.duration;

        // Auto-center camera — fit skeleton to fill viewport
        centerCamera(rootBone);

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

    function centerCamera(root) {
        const box = new THREE.Box3();
        root.traverse((child) => {
            if (child.isBone && BODY_BONE_NAMES.has(child.name)) {
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
        // Position camera so skeleton fills ~70% of viewport
        const maxDim = Math.max(size.x, size.y, size.z);
        const fovRad = camera.fov * Math.PI / 180;
        const dist = maxDim / (2 * Math.tan(fovRad / 2)) * 1.3;
        camera.position.set(center.x, center.y, center.z + dist);
        controls.update();
    }

    // --- Draw 2D skeleton on canvas overlay ---
    function drawOverlay() {
        if (!overlayCtx || !overlayCanvas) return;
        const cw = overlayContainer.clientWidth;
        const ch = overlayContainer.clientHeight;
        overlayCtx.clearRect(0, 0, cw, ch);

        if (!keypointsData || !video.duration) return;

        // Map video time to keypoints frame
        const nFrames = keypointsData.frames.length;
        const frameIdx = Math.min(
            Math.floor((video.currentTime / video.duration) * nFrames),
            nFrames - 1
        );

        // Check detection flags — hide if no person detected
        if (detectionFlags) {
            const detIdx = Math.min(
                Math.floor((video.currentTime / video.duration) * detectionFlags.length),
                detectionFlags.length - 1
            );
            if (!detectionFlags[detIdx]) return;
        }

        const kp = keypointsData.frames[frameIdx];
        if (!kp) return;

        const minConf = 0.3;

        // Draw connections
        overlayCtx.strokeStyle = '#00ff00';
        overlayCtx.lineWidth = 2.5;
        overlayCtx.lineCap = 'round';
        for (const [j1, j2] of keypointsData.connections) {
            const p1 = kp[j1], p2 = kp[j2];
            if (p1 && p2 && p1[2] > minConf && p2[2] > minConf) {
                overlayCtx.beginPath();
                overlayCtx.moveTo(p1[0] * cw, p1[1] * ch);
                overlayCtx.lineTo(p2[0] * cw, p2[1] * ch);
                overlayCtx.stroke();
            }
        }

        // Draw joints
        overlayCtx.fillStyle = '#e94560';
        for (const name of keypointsData.joints) {
            const p = kp[name];
            if (p && p[2] > minConf) {
                overlayCtx.beginPath();
                overlayCtx.arc(p[0] * cw, p[1] * ch, 4, 0, Math.PI * 2);
                overlayCtx.fill();
            }
        }
    }

    // --- Sync loop ---
    function animate() {
        requestAnimationFrame(animate);

        if (mixer && video.duration) {
            // Map video time to BVH clip time
            const t = Math.min(
                (video.currentTime / video.duration) * clipDuration,
                clipDuration - 0.0001
            );
            mixer.setTime(t);

            // Hide 3D skeleton on frames where no person was detected
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

        // Draw 2D overlay
        drawOverlay();

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
        if (e.target.tagName === 'TEXTAREA') return;
        if (e.key === ' ') {
            e.preventDefault();
            togglePlayPause();
        } else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            if (e.ctrlKey) frameStep(-10);
            else frameStep(-1);
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            if (e.ctrlKey) frameStep(10);
            else frameStep(1);
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

        _resizeOverlayCanvas();
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
