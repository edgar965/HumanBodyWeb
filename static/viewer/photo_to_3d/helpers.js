/**
 * Photo To 3D — Utility functions: base64 decoding, coordinate conversion, materials.
 */
// Aus gemeinsam/kodierung.js — die Kopien hier sind am 15.08.2026 entfallen (sechsfach vorhanden).
export { base64ToFloat32, base64ToUint16, base64ToUint32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';





/**
 * Align HB face/head profile to match SMPL-X proportions.
 * (Currently a no-op — handled by Z-axis morphs)
 */
export function alignBodyToSMPLX(buf) {
    /* removed: face profile correction now handled by Z-axis morphs
       (Jaw_Prominence, Chin_Prominence, Mouth_PosZ, etc.) which correctly
       move internal geometry (teeth, tongue, gums) along with the surface. */
}

export const BODY_MATERIALS = [
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },
    { color: 0x111111, roughness: 0.8,  metalness: 0.0 },
    { color: 0x0a0a0a, roughness: 0.1,  metalness: 0.0 },
    { color: 0xf4f0e8, roughness: 0.2,  metalness: 0.0 },
    { color: 0xf4f0e8, roughness: 0.05, metalness: 0.0, opacity: 0.3, transparent: true },
    { color: 0x4a7a9b, roughness: 0.15, metalness: 0.0 },
    { color: 0xb55a6a, roughness: 0.7,  metalness: 0.0 },
    { color: 0xf0ece0, roughness: 0.3,  metalness: 0.0 },
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },
];
