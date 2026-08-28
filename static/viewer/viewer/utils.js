/**
 * Viewer — Utility functions (base64, coordinate transforms, slider helpers).
 */
import { fn } from '../gemeinsam/registrierung.js';
// Aus gemeinsam/kodierung.js — die Kopien hier sind am 15.08.2026 entfallen (sechsfach vorhanden).
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords,
         float32ToBase64, uint32ToBase64 } from '../gemeinsam/kodierung.js';
export { base64ToFloat32, base64ToUint32, blenderToThreeCoords,
         float32ToBase64, uint32ToBase64 };

// =========================================================================
// Base64 decode
// =========================================================================


// =========================================================================
// Base64 encode (for sending buffers to server)
// =========================================================================

// =========================================================================
// Coordinate transforms
// =========================================================================


// Three.js -> Blender: (x, y, z) -> (x, -z, y)
export function threeToBlenderCoords(buf) {
    const out = new Float32Array(buf.length);
    for (let i = 0; i < buf.length; i += 3) {
        out[i]     = buf[i];
        out[i + 1] = -buf[i + 2];
        out[i + 2] = buf[i + 1];
    }
    return out;
}

// =========================================================================
// Slider helpers
// =========================================================================
export function bindSlider(sliderId, valId, fmt) {
    const slider = document.getElementById(sliderId);
    const val = document.getElementById(valId);
    if (slider && val) {
        slider.addEventListener('input', () => {
            val.textContent = fmt(parseInt(slider.value));
        });
    }
}

export function sliderVal(sliderId) {
    const el = document.getElementById(sliderId);
    return el ? parseInt(el.value) : 0;
}

export function setSlider(sliderId, value, fmt) {
    const el = document.getElementById(sliderId);
    if (!el) return;
    if (el.type === 'color') {
        el.value = value;
        return;
    }
    el.value = value;
    const valEl = document.getElementById(sliderId + '-val');
    if (valEl && fmt) valEl.textContent = fmt(parseInt(value));
}

// =========================================================================
// Body query string builder
// =========================================================================
export function buildBodyQueryString() {
    const bodySelect = document.getElementById('body-type-select');
    const bodyType = bodySelect ? bodySelect.value : 'Female_Caucasian';
    let qs = `body_type=${encodeURIComponent(bodyType)}`;
    // Morph sliders
    document.querySelectorAll('#morphs-panel input[type="range"]').forEach(slider => {
        const mName = slider.dataset.morph || slider.dataset.morphName || slider.id.replace('morph-', '');
        if (mName && slider.value !== undefined) {
            qs += `&morph_${mName}=${slider.value / 100}`;
        }
    });
    // Meta sliders (display -> internal)
    ['age', 'mass', 'tone', 'height'].forEach(m => {
        const el = document.getElementById(`meta-${m}`);
        if (el) {
            const dv = parseInt(el.value);
            const mn = parseInt(el.min), mx = parseInt(el.max);
            const neutral = (mn + mx) / 2;
            const half = (mx - mn) / 2;
            const internal = half ? (dv - neutral) / half : 0;
            qs += `&meta_${m}=${internal}`;
        }
    });
    return qs;
}

// Register in fn
fn.base64ToFloat32 = base64ToFloat32;
fn.base64ToUint32 = base64ToUint32;
fn.float32ToBase64 = float32ToBase64;
fn.uint32ToBase64 = uint32ToBase64;
fn.blenderToThreeCoords = blenderToThreeCoords;
fn.threeToBlenderCoords = threeToBlenderCoords;
fn.bindSlider = bindSlider;
fn.sliderVal = sliderVal;
fn.setSlider = setSlider;
fn.buildBodyQueryString = buildBodyQueryString;
