/**
 * Knopfleiste der Ergebnisseite — Umschalter fuer Haare, Rig, Kleidung,
 * Ansicht und Aufnahme.
 *
 * Aus ui_panel.js herausgeloest (Umbau 16.08.2026): `buildControlPanel` war
 * 393 Zeilen — Knopfleiste, Reiter, vier Reiterinhalte und die Umschaltlogik
 * in einer Funktion. Die Knopfleiste allein sind 185 davon.
 */

import * as THREE from 'three';
import { state } from './state.js';
import '../gemeinsam/registrierung.js';
import { el } from './ui_panel.js';

export class Knopfleiste {
    /** Baut die Leiste in den Behaelter. */
    static bauen(container, data) {
    // --- Toggle buttons bar ---
    const toggleBar = el('div', 'rc-toggle-bar');
    
    const modelBtn = el('button', 'rc-toggle-btn active');
    modelBtn.innerHTML = '<i class="fas fa-user"></i> Model';
    modelBtn.addEventListener('click', () => {
        if (state.bodyMesh) state.bodyMesh.visible = !state.bodyMesh.visible;
        modelBtn.classList.toggle('active', state.bodyMesh && state.bodyMesh.visible);
    });
    toggleBar.appendChild(modelBtn);
    
    const rigBtn = el('button', 'rc-toggle-btn');
    rigBtn.innerHTML = '<i class="fas fa-bone"></i> Rig';
    rigBtn.addEventListener('click', () => {
        state.rigVisible = !state.rigVisible;
        if (state.rigVisible) {
            if (!state.skeletonHelper && state.rigifySkeleton) {
                state.skeletonHelper = new THREE.SkeletonHelper(state.rigifySkeleton.rootBone);
                state.skeletonHelper.material.depthTest = false;
                state.skeletonHelper.material.depthWrite = false;
                state.skeletonHelper.material.color.set(0x00ffaa);
                state.skeletonHelper.material.linewidth = 2;
                state.skeletonHelper.renderOrder = 999;
                state.scene.add(state.skeletonHelper);
            }
            if (state.skeletonHelper) state.skeletonHelper.visible = true;
        } else {
            if (state.skeletonHelper) state.skeletonHelper.visible = false;
        }
        rigBtn.classList.toggle('active', state.rigVisible);
        if (typeof window.setBvhOverlayVisible === 'function') {
            window.setBvhOverlayVisible(state.rigVisible);
        }
    });
    toggleBar.appendChild(rigBtn);
    
    const clothBtn = el('button', 'rc-toggle-btn active');
    clothBtn.innerHTML = '<i class="fas fa-tshirt"></i> Kleider';
    clothBtn.addEventListener('click', () => {
        state.clothesVisible = !state.clothesVisible;
        for (const m of Object.values(state.clothMeshes)) {
            if (m) m.visible = state.clothesVisible;
        }
        for (const m of Object.values(state.garmentMeshes)) {
            if (m) m.visible = state.clothesVisible;
        }
        clothBtn.classList.toggle('active', state.clothesVisible);
    });
    toggleBar.appendChild(clothBtn);
    
    const hairBtn = el('button', 'rc-toggle-btn active');
    hairBtn.innerHTML = '<i class="fas fa-hat-wizard"></i> Haar';
    hairBtn.addEventListener('click', () => {
        if (state.hairMesh) {
            state.hairMesh.visible = !state.hairMesh.visible;
            hairBtn.classList.toggle('active', state.hairMesh.visible);
        }
    });
    toggleBar.appendChild(hairBtn);
    
    // Video floating window toggle
    const floatingEl = document.getElementById('floatingVideo');
    if (floatingEl) {
        const videoBtn = el('button', 'rc-toggle-btn active');
        videoBtn.innerHTML = '<i class="fas fa-video"></i> Original';
        videoBtn.addEventListener('click', () => {
            floatingEl.classList.toggle('hidden');
            videoBtn.classList.toggle('active', !floatingEl.classList.contains('hidden'));
        });
        toggleBar.appendChild(videoBtn);
    
        const closeBtn = document.getElementById('floatingVideoClose');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                floatingEl.classList.add('hidden');
                videoBtn.classList.remove('active');
            });
        }
    
        // Drag by titlebar
        const titlebar = document.getElementById('floatingVideoTitlebar');
        if (titlebar) {
            let dragX = 0, dragY = 0, startX = 0, startY = 0;
            titlebar.addEventListener('mousedown', (e) => {
                if (e.target.closest('.floating-video-close')) return;
                e.preventDefault();
                startX = e.clientX; startY = e.clientY;
                const onMove = (ev) => {
                    dragX = ev.clientX - startX; dragY = ev.clientY - startY;
                    startX = ev.clientX; startY = ev.clientY;
                    const rect = floatingEl.getBoundingClientRect();
                    floatingEl.style.left = rect.left + dragX + 'px';
                    floatingEl.style.top = rect.top + dragY + 'px';
                    floatingEl.style.bottom = 'auto';
                };
                const onUp = () => {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                };
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });
        }
    
        // Resize handle
        const resizeHandle = document.getElementById('floatingVideoResize');
        if (resizeHandle) {
            resizeHandle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const startW = floatingEl.offsetWidth;
                const startH = floatingEl.offsetHeight;
                const startMX = e.clientX;
                const startMY = e.clientY;
                const onMove = (ev) => {
                    const newW = Math.max(200, startW + (ev.clientX - startMX));
                    const newH = Math.max(120, startH + (ev.clientY - startMY));
                    floatingEl.style.width = newW + 'px';
                    floatingEl.style.height = newH + 'px';
                };
                const onUp = () => {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                };
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });
        }
    }
    
    // 3D viewport fullscreen toggle + resize
    const charContainer = document.getElementById('resultCharacter');
    const charViewport = document.getElementById('characterViewport');
    const fsBtn = document.getElementById('btnViewportFullscreen');
    const resizeHandle = document.getElementById('viewportResizeHandle');
    
    if (fsBtn && charContainer && charViewport) {
        let isFullscreen = true;
        let customHeight = null;
    
        fsBtn.addEventListener('click', () => {
            isFullscreen = !isFullscreen;
            if (isFullscreen) {
                charContainer.classList.add('result-character-fullscreen');
                charViewport.style.height = '';
                customHeight = null;
                fsBtn.innerHTML = '<i class="fas fa-expand"></i>';
            } else {
                charContainer.classList.remove('result-character-fullscreen');
                charViewport.style.height = (customHeight || 500) + 'px';
                fsBtn.innerHTML = '<i class="fas fa-compress"></i>';
            }
            window.dispatchEvent(new Event('resize'));
        });
    
        if (resizeHandle) {
            resizeHandle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const startY = e.clientY;
                const startH = charViewport.offsetHeight;
                if (isFullscreen) {
                    isFullscreen = false;
                    charContainer.classList.remove('result-character-fullscreen');
                    fsBtn.innerHTML = '<i class="fas fa-compress"></i>';
                }
                const onMove = (ev) => {
                    const newH = Math.max(250, startH + (ev.clientY - startY));
                    charViewport.style.height = newH + 'px';
                    customHeight = newH;
                    window.dispatchEvent(new Event('resize'));
                };
                const onUp = () => {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                };
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });
        }
    }
    
    container.appendChild(toggleBar);
    
    }
}
