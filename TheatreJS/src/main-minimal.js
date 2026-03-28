/**
 * MINIMAL Theatre.js Studio Setup
 * Following official docs exactly: https://www.theatrejs.com/docs/latest/getting-started
 */

import studio from '@theatre/studio';
import { getProject } from '@theatre/core';
import * as THREE from 'three';

console.log('=== Theatre.js Minimal Setup ===');

// Step 1: Initialize Studio (must be first!)
studio.initialize();
console.log('✓ Studio initialized');

// Step 2: Create project
const project = getProject('My Project');
console.log('✓ Project created');

// Step 3: Create sheet
const sheet = project.sheet('Scene');
console.log('✓ Sheet created');

// Step 4: Create Three.js scene
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 5;

const renderer = new THREE.WebGLRenderer({
    canvas: document.getElementById('theatre-canvas'),
    antialias: true
});
renderer.setSize(window.innerWidth, window.innerHeight);

// Simple cube
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshNormalMaterial();
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

console.log('✓ Three.js scene created');

// Step 5: Create Theatre object for cube
const cubeObj = sheet.object('Cube', {
    position: {
        x: 0,
        y: 0,
        z: 0,
    },
});

cubeObj.onValuesChange((values) => {
    cube.position.set(values.position.x, values.position.y, values.position.z);
});

console.log('✓ Theatre object created');

// Render loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();

console.log('✓ Setup complete');
console.log('Theatre.js Studio should appear in top-right corner');

// Expose for debugging
window.studio = studio;
window.project = project;
window.sheet = sheet;
