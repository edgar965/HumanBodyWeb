import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

console.log('[bvh_player] v0.88 loaded (3-column layout)');

export function initBVHPlayer({ videoId, canvasId, bvhUrl, fps = 30, overlayId = null, detectionUrl = null, keypointsUrl = null }) {
    console.log('[bvh_player] initBVHPlayer called', { videoId, canvasId });
    const video = document.getElementById(videoId);
    const container = document.getElementById(canvasId);
    if (!video || !container) {
        console.error('[bvh_player] Missing elements:', { video: !!video, container: !!container });
        return;
    }

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

    // --- Bone label overlay (2D canvas on top of 3D) ---
    let labelCanvas = null;
    let labelCtx = null;
    let labelsVisible = true;
    labelCanvas = document.createElement('canvas');
    labelCanvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:10';
    container.style.position = 'relative';
    container.appendChild(labelCanvas);
    labelCtx = labelCanvas.getContext('2d');

    function drawBoneLabels() {
        if (!labelCtx || !labelCanvas) return;
        const cw = container.clientWidth;
        const ch = container.clientHeight || 400;
        labelCanvas.width = cw;
        labelCanvas.height = ch;
        labelCtx.clearRect(0, 0, cw, ch);
        if (!labelsVisible || !rootBone || !rootBone.visible) return;

        labelCtx.font = 'bold 12px monospace';
        labelCtx.textAlign = 'center';
        labelCtx.textBaseline = 'bottom';

        let idx = 0;
        for (const name of BODY_BONE_NAMES) {
            const bone = bodyBoneMap[name];
            if (!bone) { idx++; continue; }
            const pos = new THREE.Vector3();
            bone.getWorldPosition(pos);
            // Project to screen
            pos.project(camera);
            const sx = (pos.x * 0.5 + 0.5) * cw;
            const sy = (-pos.y * 0.5 + 0.5) * ch;
            // Only draw if in front of camera
            if (pos.z >= -1 && pos.z <= 1) {
                // Background pill
                const label = `${idx}`;
                const tw = labelCtx.measureText(label).width + 6;
                labelCtx.fillStyle = 'rgba(0,0,0,0.7)';
                labelCtx.fillRect(sx - tw/2, sy - 16, tw, 16);
                // Text
                labelCtx.fillStyle = '#fbbf24';
                labelCtx.fillText(label, sx, sy - 2);
            }
            idx++;
        }
    }

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
    let rootBone = null;
    let clipDuration = 0;
    let currentSpeed = 1;
    let isPlaying = false;

    // Fallback clock when video is missing/broken (duration NaN or Infinity)
    let manualTime = 0;
    let lastTimestamp = 0;
    function videoOK() {
        return video.duration > 0 && isFinite(video.duration) && !isNaN(video.duration);
    }

    // --- Debug comparison panel (3rd column in result-layout) ---
    let debugDiv = document.getElementById('debugBonePanel');
    if (debugDiv) debugDiv.innerHTML = '<div style="padding:8px;color:#fbbf24">Warte auf BVH-Daten...</div>';

    const DEBUG_BONES = [
        'Pelvis','Spine1','Spine2','Spine3','Neck','Head',
        'Left_collar','Left_shoulder','Left_elbow','Left_wrist','Left_palm',
        'Right_collar','Right_shoulder','Right_elbow','Right_wrist','Right_palm',
        'Left_hip','Left_knee','Left_ankle','Left_foot',
        'Right_hip','Right_knee','Right_ankle','Right_foot'];

    function updateDebugOverlay() {
        if (!debugDiv) return;
        if (!rootBone) {
            debugDiv.innerHTML = '<div style="color:#fbbf24">Warte auf BVH-Daten...</div>';
            return;
        }

        const totalDur = videoOK() ? video.duration : clipDuration;
        const curTime = videoOK() ? video.currentTime : manualTime;
        const progress = totalDur > 0 ? curTime / totalDur : 0;
        const frametime = action ? action.getClip().tracks[0]?.times?.[1] || (1/fps) : (1/fps);
        const bvhFrame = clipDuration > 0 ? Math.floor((progress * clipDuration) / frametime) : 0;

        // 2D keypoints for current frame
        let kp2d = null;
        let frame2dIdx = 0;
        if (keypointsData) {
            const n = keypointsData.frames.length;
            frame2dIdx = Math.min(Math.floor(progress * n), n - 1);
            kp2d = keypointsData.frames[frame2dIdx];
        }

        // Collect 3D positions
        const pos3d = {};
        for (const name of DEBUG_BONES) {
            const bone = bodyBoneMap[name];
            if (bone) {
                const p = new THREE.Vector3();
                bone.getWorldPosition(p);
                pos3d[name] = p;
            }
        }

        // Normalize both to pelvis-relative, scaled by pelvis→neck distance
        // 2D: Y-down (screen), 3D: Y-up → flip 3D Y for comparison
        let norm2d = null, norm3d = null;
        if (kp2d && kp2d['Pelvis'] && kp2d['Neck']) {
            const px = kp2d['Pelvis'][0], py = kp2d['Pelvis'][1];
            const nx = kp2d['Neck'][0],   ny = kp2d['Neck'][1];
            const refLen = Math.sqrt((nx-px)**2 + (ny-py)**2);
            if (refLen > 0.001) {
                norm2d = {};
                for (const name of DEBUG_BONES) {
                    const p = kp2d[name];
                    if (p) norm2d[name] = [(p[0]-px)/refLen, (p[1]-py)/refLen];
                }
            }
        }
        if (pos3d['Pelvis'] && pos3d['Neck']) {
            const pp = pos3d['Pelvis'], np = pos3d['Neck'];
            const dx = np.x-pp.x, dy = np.y-pp.y, dz = np.z-pp.z;
            const refLen = Math.sqrt(dx*dx + dy*dy + dz*dz);
            if (refLen > 0.1) {
                norm3d = {};
                for (const name of DEBUG_BONES) {
                    const p = pos3d[name];
                    if (p) {
                        // Project to XY plane, flip Y to match 2D (Y-down)
                        norm3d[name] = [(p.x-pp.x)/refLen, -(p.y-pp.y)/refLen];
                    }
                }
            }
        }

        // Compute raw 2D pixel distances from Pelvis (for Video column)
        let raw2d = null;
        if (kp2d && kp2d['Pelvis']) {
            const px = kp2d['Pelvis'][0], py = kp2d['Pelvis'][1];
            raw2d = {};
            for (const name of DEBUG_BONES) {
                const p = kp2d[name];
                if (p) raw2d[name] = Math.sqrt((p[0]-px)**2 + (p[1]-py)**2);
            }
        }

        // Build HTML table: # | Bone | Video (dist) | 2D (dist) | 3D (dist) | Diff
        let h = `<div style="padding:8px;border-bottom:1px solid #334155;margin-bottom:4px">` +
            `<div style="color:#16c784;font-size:13px;font-weight:bold">Bone-Vergleich</div>` +
            `<div style="color:#ccc;font-size:10px">Frame ${Math.floor(curTime * fps)} | 2D:${frame2dIdx} 3D:${bvhFrame} (${curTime.toFixed(2)}s)</div></div>`;
        h += '<table style="width:100%;border-collapse:collapse;font-size:11px;padding:0 6px">';
        h += '<tr style="color:#f472b6;border-bottom:2px solid #475569">' +
            '<th style="text-align:center;padding:3px 2px;width:16px">#</th>' +
            '<th style="text-align:left;padding:3px 4px">Bone</th>' +
            '<th style="text-align:center;padding:3px 4px;background:#1a0f2e">Video</th>' +
            '<th style="text-align:center;padding:3px 4px;background:#0f2a1e">2D</th>' +
            '<th style="text-align:center;padding:3px 4px;background:#1e1a2e">3D</th>' +
            '<th style="text-align:center;padding:3px 4px">Diff</th></tr>';
        h += '<tr style="color:#999;font-size:9px;border-bottom:1px solid #334155">' +
            '<td></td><td></td>' +
            '<td style="text-align:right;padding:1px 4px;background:#1a0f2e">dist</td>' +
            '<td style="text-align:right;padding:1px 4px;background:#0f2a1e">dist</td>' +
            '<td style="text-align:right;padding:1px 4px;background:#1e1a2e">dist</td>' +
            '<td style="text-align:right;padding:1px 4px">Δ</td></tr>';

        for (let bi = 0; bi < DEBUG_BONES.length; bi++) {
            const name = DEBUG_BONES[bi];
            const n2 = norm2d ? norm2d[name] : null;
            const n3 = norm3d ? norm3d[name] : null;

            // Video: raw pixel distance from Pelvis (normalized 0-1 coords)
            const vDist = raw2d && raw2d[name] !== undefined ? raw2d[name].toFixed(3) : '—';

            // 2D normalized: distance from Pelvis
            const d2 = n2 ? Math.sqrt(n2[0]**2 + n2[1]**2) : null;
            const c2 = d2 !== null ? d2.toFixed(3) : '—';

            // 3D normalized: distance from Pelvis
            const d3 = n3 ? Math.sqrt(n3[0]**2 + n3[1]**2) : null;
            const c3 = d3 !== null ? d3.toFixed(3) : '—';

            // Diff between 2D and 3D distances
            let diff = '—', diffColor = '#64748b';
            if (d2 !== null && d3 !== null) {
                const dd = d3 - d2;
                diff = (dd >= 0 ? '+' : '') + dd.toFixed(3);
                const absDiff = Math.abs(dd);
                diffColor = absDiff < 0.15 ? '#16c784' : absDiff < 0.4 ? '#fbbf24' : '#ef4444';
            }
            h += `<tr style="border-top:1px solid #1e293b">` +
                `<td style="text-align:center;padding:2px 2px;color:#64748b;font-size:10px">${bi}</td>` +
                `<td style="padding:2px 4px;color:#8cb4ff;white-space:nowrap;font-size:10px">${name}</td>` +
                `<td style="text-align:right;padding:2px 4px;background:#1a0f2e;color:#c084fc">${vDist}</td>` +
                `<td style="text-align:right;padding:2px 4px;background:#0f2a1e">${c2}</td>` +
                `<td style="text-align:right;padding:2px 4px;background:#1e1a2e">${c3}</td>` +
                `<td style="text-align:right;padding:2px 4px;color:${diffColor}">${diff}</td></tr>`;
        }
        h += '</table>';

        // Summary: arm & leg angles
        h += '<div style="margin-top:6px;border-top:1px solid #475569;padding-top:4px;color:#fbbf24;font-size:12px">';
        const pairs = [
            ['L arm', 'Left_shoulder', 'Left_wrist'],
            ['R arm', 'Right_shoulder', 'Right_wrist'],
            ['L leg', 'Left_hip', 'Left_ankle'],
            ['R leg', 'Right_hip', 'Right_ankle']];
        for (const [label, top, bot] of pairs) {
            let s2 = '—', s3 = '—';
            if (norm2d && norm2d[top] && norm2d[bot]) {
                const dy = norm2d[bot][1] - norm2d[top][1];
                s2 = dy > 0 ? `↓${dy.toFixed(2)}` : `↑${(-dy).toFixed(2)}`;
            }
            if (norm3d && norm3d[top] && norm3d[bot]) {
                const dy = norm3d[bot][1] - norm3d[top][1];
                s3 = dy > 0 ? `↓${dy.toFixed(2)}` : `↑${(-dy).toFixed(2)}`;
            }
            h += `${label}: 2D=${s2} 3D=${s3} &nbsp;|&nbsp; `;
        }
        h += '</div>';

        // Raw 3D world positions for reference
        h += '<div style="margin-top:4px;color:#64748b;font-size:10px">';
        h += 'Raw 3D (cm): ';
        for (const name of ['Pelvis','Left_shoulder','Left_wrist','Right_shoulder','Right_wrist']) {
            const p = pos3d[name];
            if (p) h += `${name}=[${p.x.toFixed(0)},${p.y.toFixed(0)},${p.z.toFixed(0)}] `;
        }
        h += '</div>';

        debugDiv.innerHTML = h;
    }

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

    // --- Video metadata (must be registered BEFORE BVH load, not inside callback) ---
    function onVideoMetadata() {
        console.log('[bvh_player] Video metadata loaded, duration:', video.duration);
        if (videoOK()) {
            if (timelineSlider) timelineSlider.max = video.duration;
            if (timeDuration) timeDuration.textContent = formatTime(video.duration);
        }
    }
    video.addEventListener('loadedmetadata', onVideoMetadata);
    // If already loaded (cached), apply immediately
    if (video.duration && !isNaN(video.duration)) {
        onVideoMetadata();
    }
    // Detect broken video (404, no source, etc.)
    video.addEventListener('error', () => {
        console.warn('[bvh_player] Video error — using BVH clock fallback');
    });

    // --- Load BVH (3D panel only) ---
    const loader = new BVHLoader();

    // MocapNET body bones + connections
    const MOCAPNET_BONES = new Set([
        'hip', 'abdomen', 'chest', 'neck', 'neck1', 'head',
        'rCollar', 'rShldr', 'rForeArm', 'rHand',
        'lCollar', 'lShldr', 'lForeArm', 'lHand',
        'rButtock', 'rThigh', 'rShin', 'rFoot',
        'lButtock', 'lThigh', 'lShin', 'lFoot',
    ]);
    const MOCAPNET_CONNECTIONS = [
        ['hip', 'abdomen'], ['abdomen', 'chest'], ['chest', 'neck'], ['neck', 'neck1'], ['neck1', 'head'],
        ['chest', 'rCollar'], ['rCollar', 'rShldr'], ['rShldr', 'rForeArm'], ['rForeArm', 'rHand'],
        ['chest', 'lCollar'], ['lCollar', 'lShldr'], ['lShldr', 'lForeArm'], ['lForeArm', 'lHand'],
        ['hip', 'rButtock'], ['rButtock', 'rThigh'], ['rThigh', 'rShin'], ['rShin', 'rFoot'],
        ['hip', 'lButtock'], ['lButtock', 'lThigh'], ['lThigh', 'lShin'], ['lShin', 'lFoot'],
    ];

    // SMPL body bones + connections
    const SMPL_BONES = new Set([
        'Pelvis', 'Spine1', 'Spine2', 'Spine3', 'Neck', 'Head',
        'Left_hip', 'Left_knee', 'Left_ankle', 'Left_foot',
        'Right_hip', 'Right_knee', 'Right_ankle', 'Right_foot',
        'Left_collar', 'Left_shoulder', 'Left_elbow', 'Left_wrist',
        'Right_collar', 'Right_shoulder', 'Right_elbow', 'Right_wrist',
    ]);
    const SMPL_CONNECTIONS = [
        ['Pelvis', 'Spine1'], ['Spine1', 'Spine2'], ['Spine2', 'Spine3'], ['Spine3', 'Neck'], ['Neck', 'Head'],
        ['Spine3', 'Left_collar'], ['Left_collar', 'Left_shoulder'], ['Left_shoulder', 'Left_elbow'], ['Left_elbow', 'Left_wrist'],
        ['Spine3', 'Right_collar'], ['Right_collar', 'Right_shoulder'], ['Right_shoulder', 'Right_elbow'], ['Right_elbow', 'Right_wrist'],
        ['Pelvis', 'Left_hip'], ['Left_hip', 'Left_knee'], ['Left_knee', 'Left_ankle'], ['Left_ankle', 'Left_foot'],
        ['Pelvis', 'Right_hip'], ['Right_hip', 'Right_knee'], ['Right_knee', 'Right_ankle'], ['Right_ankle', 'Right_foot'],
    ];

    // Active set — chosen at BVH load time
    let BODY_BONE_NAMES = MOCAPNET_BONES;
    let BODY_CONNECTIONS = MOCAPNET_CONNECTIONS;

    // Custom body-only skeleton lines (replaces SkeletonHelper which draws ALL 164+ bones)
    let bodyLineSegments = null;
    let bodyBoneMap = {};  // name → bone

    function updateBodyLines() {
        if (!bodyLineSegments || !rootBone) return;
        const positions = bodyLineSegments.geometry.attributes.position;
        let idx = 0;
        for (const [parentName, childName] of BODY_CONNECTIONS) {
            const pBone = bodyBoneMap[parentName];
            const cBone = bodyBoneMap[childName];
            if (pBone && cBone) {
                const p1 = new THREE.Vector3();
                const p2 = new THREE.Vector3();
                pBone.getWorldPosition(p1);
                cBone.getWorldPosition(p2);
                positions.setXYZ(idx, p1.x, p1.y, p1.z);
                positions.setXYZ(idx + 1, p2.x, p2.y, p2.z);
            }
            idx += 2;
        }
        positions.needsUpdate = true;
    }

    loader.load(bvhUrl, (result) => {
        console.log('[bvh_player] BVH loaded, bones:', result.skeleton.bones.length);
        rootBone = result.skeleton.bones[0];
        scene.add(rootBone);

        // Build bone name → bone lookup
        result.skeleton.bones.forEach((bone) => {
            bodyBoneMap[bone.name] = bone;
        });

        // Detect BVH format: SMPL vs MocapNET
        const boneNames = new Set(Object.keys(bodyBoneMap));
        if (boneNames.has('Pelvis') && boneNames.has('Left_hip')) {
            BODY_BONE_NAMES = SMPL_BONES;
            BODY_CONNECTIONS = SMPL_CONNECTIONS;
            console.log('[bvh_player] Detected SMPL format');
        } else {
            BODY_BONE_NAMES = MOCAPNET_BONES;
            BODY_CONNECTIONS = MOCAPNET_CONNECTIONS;
            console.log('[bvh_player] Detected MocapNET format');
        }

        // Debug: show which bones are matched vs missing
        const matched = [], missing = [];
        for (const name of BODY_BONE_NAMES) {
            if (boneNames.has(name)) matched.push(name);
            else missing.push(name);
        }
        console.log(`[bvh_player] Bones matched: ${matched.length}/${BODY_BONE_NAMES.size}`, matched);
        if (missing.length) console.warn('[bvh_player] Bones MISSING:', missing);
        console.log('[bvh_player] All BVH bone names:', [...boneNames]);
        // Expose for debugging via console
        window.__bvhDebug = { matched, missing, allBones: [...boneNames], bodyBoneMap };

        // Custom body-only line segments (instead of SkeletonHelper)
        const lineGeo = new THREE.BufferGeometry();
        const linePositions = new Float32Array(BODY_CONNECTIONS.length * 2 * 3);
        lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
        const lineMat = new THREE.LineBasicMaterial({ color: 0x16c784, linewidth: 2 });
        bodyLineSegments = new THREE.LineSegments(lineGeo, lineMat);
        scene.add(bodyLineSegments);

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

        // Animation mixer — LoopOnce + clamp to prevent wrapping artifacts
        mixer = new THREE.AnimationMixer(rootBone);
        action = mixer.clipAction(result.clip);
        action.setLoop(THREE.LoopOnce);
        action.clampWhenFinished = true;
        action.play();
        clipDuration = result.clip.duration;

        // Apply frame 0 so bones have their actual animated positions
        // (without this, bones are at BVH OFFSET positions which differ from frame data)
        mixer.setTime(0);
        rootBone.updateWorldMatrix(true, true);

        // Initial line positions
        updateBodyLines();

        // Auto-center camera — fit skeleton to fill viewport
        centerCamera(rootBone);

        // If video is broken, use BVH clip duration for timeline
        if (!videoOK() && clipDuration > 0) {
            console.log('[bvh_player] Video broken — using BVH clock, duration:', clipDuration.toFixed(1) + 's');
            if (timelineSlider) timelineSlider.max = clipDuration;
            if (timeDuration) timeDuration.textContent = formatTime(clipDuration);
        }

        // Hide until user starts playback
        rootBone.visible = false;
        bodyLineSegments.visible = false;
    }, undefined, (err) => {
        console.error('[bvh_player] BVH load error:', err);
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
    let overlayActive = false;  // true after first play or user seek
    let overlayForced = false;  // true when externally forced via setBvhOverlayVisible()

    // Expose overlay control for result_character.js "Rig" button
    window.setBvhOverlayVisible = function(visible) {
        overlayForced = visible;
        if (visible) overlayActive = true;
    };

    function drawOverlay() {
        if (!overlayCtx || !overlayCanvas) return;
        const cw = overlayContainer.clientWidth;
        const ch = overlayContainer.clientHeight;
        // Ensure canvas backing store matches container (fixes stale init sizing)
        const dpr = window.devicePixelRatio;
        const needW = Math.round(cw * dpr);
        const needH = Math.round(ch * dpr);
        if (overlayCanvas.width !== needW || overlayCanvas.height !== needH) {
            overlayCanvas.width = needW;
            overlayCanvas.height = needH;
            overlayCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }
        overlayCtx.clearRect(0, 0, cw, ch);

        if ((!overlayActive && !overlayForced) || !keypointsData || !video.duration) return;

        // Map video time to keypoints frame
        const nFrames = keypointsData.frames.length;
        const rawFrameIdx = Math.floor((video.currentTime / video.duration) * nFrames);
        if (rawFrameIdx >= nFrames) return;
        const frameIdx = rawFrameIdx;

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

        // Account for letterboxing: video uses object-fit:contain
        let rw = cw, rh = ch, ox = 0, oy = 0;
        if (video.videoWidth && video.videoHeight) {
            const vAsp = video.videoWidth / video.videoHeight;
            const cAsp = cw / ch;
            if (cAsp > vAsp) {
                rw = ch * vAsp; rh = ch; ox = (cw - rw) / 2;
            } else {
                rw = cw; rh = cw / vAsp; oy = (ch - rh) / 2;
            }
        }

        // Draw connections
        overlayCtx.strokeStyle = '#00ff00';
        overlayCtx.lineWidth = 2.5;
        overlayCtx.lineCap = 'round';
        for (const [j1, j2] of keypointsData.connections) {
            const p1 = kp[j1], p2 = kp[j2];
            if (p1 && p2 && p1[2] > minConf && p2[2] > minConf) {
                overlayCtx.beginPath();
                overlayCtx.moveTo(p1[0] * rw + ox, p1[1] * rh + oy);
                overlayCtx.lineTo(p2[0] * rw + ox, p2[1] * rh + oy);
                overlayCtx.stroke();
            }
        }

        // Build name→index map from BODY_BONE_NAMES so 2D labels match 3D labels
        const boneIdx = {};
        let bi2 = 0;
        for (const n of BODY_BONE_NAMES) boneIdx[n] = bi2++;

        // Draw joints + index labels (same numbering as 3D skeleton)
        overlayCtx.fillStyle = '#e94560';
        overlayCtx.font = 'bold 11px monospace';
        overlayCtx.textAlign = 'center';
        overlayCtx.textBaseline = 'bottom';
        for (const name of keypointsData.joints) {
            const p = kp[name];
            if (p && p[2] > minConf) {
                const sx = p[0] * rw + ox;
                const sy = p[1] * rh + oy;
                // Joint dot
                overlayCtx.fillStyle = '#e94560';
                overlayCtx.beginPath();
                overlayCtx.arc(sx, sy, 4, 0, Math.PI * 2);
                overlayCtx.fill();
                // Index label (same numbering as 3D bone labels)
                if (labelsVisible && boneIdx[name] !== undefined) {
                    const label = `${boneIdx[name]}`;
                    const tw = overlayCtx.measureText(label).width + 6;
                    overlayCtx.fillStyle = 'rgba(0,0,0,0.7)';
                    overlayCtx.fillRect(sx - tw / 2, sy - 18, tw, 14);
                    overlayCtx.fillStyle = '#fbbf24';
                    overlayCtx.fillText(label, sx, sy - 5);
                }
            }
        }
    }

    // --- Sync loop ---
    function animate(timestamp) {
        requestAnimationFrame(animate);

        // Advance manual clock when video is broken and playing
        if (!videoOK() && isPlaying && clipDuration > 0) {
            const dt = lastTimestamp ? (timestamp - lastTimestamp) / 1000 : 0;
            manualTime = Math.min(manualTime + dt * currentSpeed, clipDuration);
            if (manualTime >= clipDuration) {
                manualTime = 0; // loop
            }
        }
        lastTimestamp = timestamp;

        // Expose progress for result_character.js
        const totalDur = videoOK() ? video.duration : clipDuration;
        const curTime = videoOK() ? video.currentTime : manualTime;
        const progress = totalDur > 0 ? curTime / totalDur : 0;
        window.bvhPlayerProgress = progress;
        window.bvhPlayerDuration = totalDur;

        if (mixer && clipDuration > 0) {
            const rawT = progress * clipDuration;

            // Hide 3D skeleton when beyond data
            const beyondBVH = rawT >= clipDuration;
            if (!beyondBVH) {
                // Reset action if clamped/paused (e.g. video replayed after ending)
                if (action && action.paused) {
                    action.reset();
                    action.play();
                }
                mixer.setTime(rawT);
            }

            // Determine visibility: hidden before first play, beyond data, or no person
            let visible = (overlayActive || overlayForced) && !beyondBVH;
            if (visible && detectionFlags && videoOK()) {
                const frameIdx = Math.min(
                    Math.floor(progress * detectionFlags.length),
                    detectionFlags.length - 1
                );
                visible = detectionFlags[frameIdx];
            }
            if (bodyLineSegments) bodyLineSegments.visible = visible;
            if (rootBone) rootBone.visible = visible;

            // Update custom body line positions after animation
            if (visible) updateBodyLines();
        }

        controls.update();
        renderer.render(scene, camera);

        // Draw bone index labels on 3D canvas
        drawBoneLabels();

        // Draw 2D overlay
        drawOverlay();

        // Update debug comparison overlay (if visible)
        updateDebugOverlay();

        // Update timeline
        if (totalDur > 0) {
            if (timelineSlider) timelineSlider.value = curTime;
            // Show time + frame numbers for debugging
            const nFrames2d = keypointsData ? keypointsData.frames.length : 0;
            const frame2d = nFrames2d > 0 ? Math.min(Math.floor(progress * nFrames2d), nFrames2d - 1) : 0;
            const frametime = action ? action.getClip().tracks[0]?.times?.[1] || (1/fps) : (1/fps);
            const rawT2 = progress * clipDuration;
            const bvhFrame = clipDuration > 0 ? Math.floor(rawT2 / frametime) : 0;
            const nFramesBvh = clipDuration > 0 ? Math.round(clipDuration / frametime) : 0;
            const frameInfo = `  2D:${frame2d}/${nFrames2d} 3D:${bvhFrame}/${nFramesBvh}`;
            if (timeCurrent) timeCurrent.textContent = formatTime(curTime) + frameInfo;
        }
    }
    animate();

    // --- Controls ---
    function togglePlayPause() {
        console.log('[bvh_player] togglePlayPause, paused=', video.paused, 'videoOK=', videoOK());
        if (videoOK()) {
            if (video.paused) {
                video.play().catch(err => console.warn('[bvh_player] play() rejected:', err.message));
            } else {
                video.pause();
            }
            // State is updated by video 'play'/'pause' event listeners below
        } else {
            // Fallback: toggle internal clock
            isPlaying = !isPlaying;
            overlayActive = true;
            lastTimestamp = 0; // reset delta timer
            if (playIcon) playIcon.className = isPlaying ? 'fas fa-pause' : 'fas fa-play';
        }
    }

    function skip(delta) {
        if (videoOK()) {
            video.currentTime = Math.max(0, Math.min(video.duration, video.currentTime + delta));
        } else if (clipDuration > 0) {
            manualTime = Math.max(0, Math.min(clipDuration, manualTime + delta));
            overlayActive = true;
        }
    }

    function frameStep(direction) {
        const frameDuration = 1 / fps;
        if (videoOK()) {
            video.pause();
            video.currentTime = Math.max(0, Math.min(video.duration, video.currentTime + direction * frameDuration));
        } else {
            isPlaying = false;
            if (playIcon) playIcon.className = 'fas fa-play';
            manualTime = Math.max(0, Math.min(clipDuration, manualTime + direction * frameDuration));
            overlayActive = true;
        }
    }

    function setSpeed(speed) {
        currentSpeed = speed;
        if (videoOK()) video.playbackRate = speed;
        if (action) action.timeScale = speed;
        speedBtns.forEach(btn => {
            btn.classList.toggle('active', parseFloat(btn.dataset.speed) === speed);
        });
    }

    function stopPlayback() {
        if (videoOK()) {
            video.pause();
            video.currentTime = 0;
        }
        isPlaying = false;
        manualTime = 0;
        overlayActive = false;
        if (playIcon) playIcon.className = 'fas fa-play';
    }

    // Button handlers
    console.log('[bvh_player] Attaching button handlers...');
    if (btnPlayPause) btnPlayPause.addEventListener('click', togglePlayPause);
    const _btn = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener('click', fn); else console.warn('[bvh_player] Missing button:', id); };
    _btn('btnStop', stopPlayback);
    _btn('btnSkipBack10', () => skip(-10));
    _btn('btnSkipBack1', () => skip(-1));
    _btn('btnSkipFwd1', () => skip(1));
    _btn('btnSkipFwd10', () => skip(10));
    _btn('btnFrameBack', () => frameStep(-1));
    _btn('btnFrameFwd', () => frameStep(1));

    // Timeline slider
    if (timelineSlider) {
        timelineSlider.addEventListener('input', () => {
            const t = parseFloat(timelineSlider.value);
            if (videoOK()) {
                video.currentTime = t;
            } else {
                manualTime = t;
                overlayActive = true;
            }
        });
    }

    // Speed buttons
    speedBtns.forEach(btn => {
        btn.addEventListener('click', () => setSpeed(parseFloat(btn.dataset.speed)));
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        const tag = e.target.tagName;
        if (tag === 'TEXTAREA' || tag === 'INPUT') return;
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
        } else if (e.key === 'n' || e.key === 'N') {
            // Toggle bone index numbers on 3D skeleton
            labelsVisible = !labelsVisible;
            console.log('[bvh_player] Bone labels:', labelsVisible ? 'ON' : 'OFF');
        }
    });

    // Toggle buttons
    const btnIdx = document.getElementById('btnToggleIdx');
    if (btnIdx) {
        btnIdx.classList.add('active'); // labels visible by default
        btnIdx.addEventListener('click', () => {
            labelsVisible = !labelsVisible;
            btnIdx.classList.toggle('active', labelsVisible);
        });
    }

    console.log('[bvh_player] All handlers attached. Video duration:', video.duration);

    // Video events
    video.addEventListener('play', () => {
        isPlaying = true;
        overlayActive = true;
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
    video.addEventListener('seeked', () => {
        overlayActive = true;
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
