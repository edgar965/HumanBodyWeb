/**
 * Simple Three.js BVH Viewer for MocapNET Web UI
 * Displays a skeleton animation from a BVH file
 */

function initBVHViewer(containerId, bvhUrl) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight || 400;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(0, 100, 300);
    camera.lookAt(0, 100, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    // Grid
    const grid = new THREE.GridHelper(400, 20, 0x2a2a4a, 0x1a1a2e);
    scene.add(grid);

    // Lights
    const ambient = new THREE.AmbientLight(0x404040, 2);
    scene.add(ambient);
    const directional = new THREE.DirectionalLight(0xffffff, 1);
    directional.position.set(100, 200, 100);
    scene.add(directional);

    // Placeholder skeleton (will be replaced when BVH loads)
    const skeletonGroup = new THREE.Group();
    scene.add(skeletonGroup);

    // Info text
    const infoDiv = document.createElement('div');
    infoDiv.style.cssText = 'position:absolute;bottom:10px;left:10px;color:#888;font-size:12px;';
    infoDiv.textContent = 'Loading BVH...';
    container.style.position = 'relative';
    container.appendChild(infoDiv);

    // Simple orbit controls
    let isDragging = false;
    let prevMouse = { x: 0, y: 0 };
    let spherical = { theta: 0, phi: Math.PI / 4, radius: 300 };

    function updateCamera() {
        camera.position.x = spherical.radius * Math.sin(spherical.phi) * Math.sin(spherical.theta);
        camera.position.y = spherical.radius * Math.cos(spherical.phi);
        camera.position.z = spherical.radius * Math.sin(spherical.phi) * Math.cos(spherical.theta);
        camera.lookAt(0, 100, 0);
    }

    renderer.domElement.addEventListener('mousedown', (e) => {
        isDragging = true;
        prevMouse = { x: e.clientX, y: e.clientY };
    });

    renderer.domElement.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const dx = e.clientX - prevMouse.x;
        const dy = e.clientY - prevMouse.y;
        spherical.theta += dx * 0.01;
        spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi + dy * 0.01));
        prevMouse = { x: e.clientX, y: e.clientY };
        updateCamera();
    });

    renderer.domElement.addEventListener('mouseup', () => isDragging = false);
    renderer.domElement.addEventListener('mouseleave', () => isDragging = false);

    renderer.domElement.addEventListener('wheel', (e) => {
        spherical.radius = Math.max(50, Math.min(800, spherical.radius + e.deltaY * 0.5));
        updateCamera();
        e.preventDefault();
    });

    // Try to load BVH (simplified - just show info)
    if (bvhUrl) {
        fetch(bvhUrl)
            .then(r => r.ok ? r.text() : Promise.reject('File not accessible'))
            .then(text => {
                const lines = text.split('\n');
                const motionIdx = lines.findIndex(l => l.trim() === 'MOTION');
                if (motionIdx > -1) {
                    const framesLine = lines[motionIdx + 1];
                    const match = framesLine.match(/Frames:\s*(\d+)/);
                    const frames = match ? parseInt(match[1]) : 0;
                    infoDiv.textContent = `BVH loaded: ${frames} frames`;

                    // Draw a simple T-pose skeleton placeholder
                    drawSimpleSkeleton(skeletonGroup);
                }
            })
            .catch(err => {
                infoDiv.textContent = 'BVH file on disk (not served via HTTP)';
                drawSimpleSkeleton(skeletonGroup);
            });
    }

    function drawSimpleSkeleton(group) {
        const material = new THREE.MeshPhongMaterial({ color: 0xe94560 });

        // Simple humanoid shape
        const joints = [
            [0, 100, 0],    // hip
            [0, 140, 0],    // spine
            [0, 170, 0],    // chest
            [0, 185, 0],    // head
            [-20, 170, 0],  // left shoulder
            [-50, 150, 0],  // left elbow
            [-70, 130, 0],  // left hand
            [20, 170, 0],   // right shoulder
            [50, 150, 0],   // right elbow
            [70, 130, 0],   // right hand
            [-10, 100, 0],  // left hip
            [-10, 55, 0],   // left knee
            [-10, 10, 0],   // left foot
            [10, 100, 0],   // right hip
            [10, 55, 0],    // right knee
            [10, 10, 0],    // right foot
        ];

        const bones = [
            [0, 1], [1, 2], [2, 3],     // spine
            [2, 4], [4, 5], [5, 6],     // left arm
            [2, 7], [7, 8], [8, 9],     // right arm
            [0, 10], [10, 11], [11, 12], // left leg
            [0, 13], [13, 14], [14, 15], // right leg
        ];

        // Draw joints
        joints.forEach(pos => {
            const geo = new THREE.SphereGeometry(3, 8, 8);
            const mesh = new THREE.Mesh(geo, material);
            mesh.position.set(pos[0], pos[1], pos[2]);
            group.add(mesh);
        });

        // Draw bones
        const boneMaterial = new THREE.MeshPhongMaterial({ color: 0xff6b81 });
        bones.forEach(([a, b]) => {
            const start = new THREE.Vector3(...joints[a]);
            const end = new THREE.Vector3(...joints[b]);
            const dir = new THREE.Vector3().subVectors(end, start);
            const length = dir.length();
            const geo = new THREE.CylinderGeometry(1.5, 1.5, length, 6);
            const mesh = new THREE.Mesh(geo, boneMaterial);
            mesh.position.copy(start).add(dir.multiplyScalar(0.5));
            mesh.lookAt(end);
            mesh.rotateX(Math.PI / 2);
            group.add(mesh);
        });
    }

    // Animate
    function animate() {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    }
    animate();

    // Handle resize
    window.addEventListener('resize', () => {
        const w = container.clientWidth;
        const h = container.clientHeight || 400;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    });
}
