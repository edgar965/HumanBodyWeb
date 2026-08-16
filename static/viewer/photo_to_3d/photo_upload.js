/**
 * Photo To 3D — Photo upload and analyze functionality.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Fotoanalyse } from './fotoanalyse.js';

// =========================================================================
// Photo Upload
// =========================================================================
export function initPhotoUpload() {
    const zone = document.getElementById('upload-zone');
    const input = document.getElementById('photo-input');
    const preview = document.getElementById('photo-preview');
    const img = document.getElementById('photo-img');
    const removeBtn = document.getElementById('photo-remove');
    const actions = document.getElementById('photo-actions');
    const analyzeBtn = document.getElementById('btn-analyze');

    zone.addEventListener('click', () => input.click());
    input.addEventListener('change', () => {
        if (input.files.length > 0) showPhoto(input.files[0]);
    });
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', e => {
        e.preventDefault(); zone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) showPhoto(file);
    });
    removeBtn.addEventListener('click', () => {
        preview.style.display = 'none'; actions.style.display = 'none';
        zone.style.display = ''; input.value = '';
        document.getElementById('detection-results').style.display = 'none';
        state.detectedSkinColor = null;
    });
    analyzeBtn.addEventListener('click', () => analyzePhoto());

    function showPhoto(file) {
        const reader = new FileReader();
        reader.onload = e => {
            img.src = e.target.result;
            preview.style.display = 'block'; actions.style.display = 'block';
            zone.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}

/**
 * Foto analysieren. Der Ablauf steckt in fotoanalyse.js — vorher 272 Zeilen
 * hier, die laengste JavaScript-Funktion des Projekts.
 */
export async function analyzePhoto() {
    return new Fotoanalyse().ausfuehren();
}


fn.initPhotoUpload = initPhotoUpload;
fn.analyzePhoto = analyzePhoto;
