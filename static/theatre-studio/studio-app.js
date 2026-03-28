/**
 * Minimal Theatre.js Studio Test App
 * Uses CDN imports to test Studio UI functionality
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js';
import studio from 'https://cdn.jsdelivr.net/npm/@theatre/studio@0.7.2/dist/studio.esm.js';
import { getProject } from 'https://cdn.jsdelivr.net/npm/@theatre/core@0.7.2/dist/core.esm.js';

console.log('%c=== Theatre.js Studio Debugger ===', 'color: #7c5cbf; font-size: 16px; font-weight: bold');

// Update status display
const updateStatus = (status, color = '#6cf') => {
    const el = document.getElementById('studio-status');
    if (el) {
        el.textContent = status;
        el.style.color = color;
    }
    console.log(`[STATUS] ${status}`);
};

updateStatus('Initializing Studio...', '#ff0');

// 1. Initialize Theatre.js Studio
try {
    studio.initialize();
    window.studio = studio;
    updateStatus('Studio Initialized', '#0f0');
    console.log('✓ studio.initialize() called');
    console.log('  studio object:', studio);
    console.log('  studio.ui:', studio.ui);
} catch (err) {
    updateStatus('Studio Init Failed: ' + err.message, '#f00');
    console.error('✗ Studio initialization failed:', err);
}

// 2. Create Theatre.js Project and Sheet
const project = getProject('Studio Debug Project');
const sheet = project.sheet('Main Scene');
window.project = project;
window.sheet = sheet;

document.getElementById('project-name').textContent = 'Studio Debug Project';
document.getElementById('sheet-name').textContent = 'Main Scene';

console.log('✓ Project created:', project);
console.log('✓ Sheet created:', sheet);

// 3. Setup Three.js scene
const canvas = document.getElementById('studio-canvas');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x222222);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 2, 10);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

// Add grid
const gridHelper = new THREE.GridHelper(20, 20);
scene.add(gridHelper);

// Add axes helper
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper);

// Add simple mesh
const geometry = new THREE.BoxGeometry(2, 2, 2);
const material = new THREE.MeshStandardMaterial({ color: 0x7c5cbf });
const cube = new THREE.Mesh(geometry, material);
cube.position.y = 1;
scene.add(cube);

// Add lights
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const pointLight = new THREE.PointLight(0xffffff, 1, 100);
pointLight.position.set(5, 5, 5);
scene.add(pointLight);

console.log('✓ Three.js scene created');

// 4. Register objects with Theatre.js
const cameraObj = sheet.object('Camera', {
    position: {
        x: camera.position.x,
        y: camera.position.y,
        z: camera.position.z
    },
    fov: camera.fov
});

const lightObj = sheet.object('Point Light', {
    position: {
        x: pointLight.position.x,
        y: pointLight.position.y,
        z: pointLight.position.z
    },
    intensity: pointLight.intensity
});

const cubeObj = sheet.object('Cube', {
    position: {
        x: cube.position.x,
        y: cube.position.y,
        z: cube.position.z
    },
    rotation: {
        x: 0,
        y: 0,
        z: 0
    },
    color: { r: 0.48, g: 0.36, b: 0.75 }
});

// Update object count
document.getElementById('object-count').textContent = '3 (Camera, Light, Cube)';

console.log('✓ Theatre objects registered:', { cameraObj, lightObj, cubeObj });

// Listen to value changes
cameraObj.onValuesChange((values) => {
    camera.position.set(values.position.x, values.position.y, values.position.z);
    camera.fov = values.fov;
    camera.updateProjectionMatrix();
});

lightObj.onValuesChange((values) => {
    pointLight.position.set(values.position.x, values.position.y, values.position.z);
    pointLight.intensity = values.intensity;
});

cubeObj.onValuesChange((values) => {
    cube.position.set(values.position.x, values.position.y, values.position.z);
    cube.rotation.set(values.rotation.x, values.rotation.y, values.rotation.z);
    cube.material.color.setRGB(values.color.r, values.color.g, values.color.b);
});

// 5. Render loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// 6. Debug info after a delay (to check Studio UI rendering)
setTimeout(() => {
    const root = document.getElementById('theatrejs-studio-root');
    console.log('\n=== Studio UI Check (after 2s) ===');
    console.log('  #theatrejs-studio-root exists:', !!root);
    console.log('  Root children count:', root ? root.children.length : 'N/A');
    console.log('  Root innerHTML length:', root ? root.innerHTML.length : 'N/A');

    if (root && root.children.length === 0) {
        updateStatus('Studio UI not rendering (root empty)', '#f80');
        console.warn('⚠ Studio root exists but has no children!');
        console.warn('  This means Studio initialized but UI is not rendering.');
        console.warn('  Check browser console for errors or Theatre.js version compatibility.');
    } else if (root && root.children.length > 0) {
        updateStatus('Studio UI Active!', '#0f0');
        console.log('✓ Studio UI is rendering!');
    } else {
        updateStatus('Studio root not found', '#f00');
        console.error('✗ #theatrejs-studio-root not found in DOM');
    }

    // Try to show Studio UI explicitly
    if (window.studio && window.studio.ui) {
        console.log('\n=== Trying studio.ui.restore() ===');
        try {
            window.studio.ui.restore();
            console.log('✓ studio.ui.restore() called');
        } catch (err) {
            console.error('✗ studio.ui.restore() failed:', err);
        }
    }
}, 2000);

console.log('\n=== Setup Complete ===');
console.log('Check for Theatre.js Studio panel (usually top-right corner)');
console.log('Available globals: window.studio, window.project, window.sheet');
