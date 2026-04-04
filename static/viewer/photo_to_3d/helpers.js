/**
 * Photo To 3D — Utility functions: base64 decoding, coordinate conversion, materials.
 */
import * as THREE from 'three';

export function base64ToFloat32(b64) {
    const bin = atob(b64);
    const u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    return new Float32Array(u8.buffer);
}

export function base64ToUint32(b64) {
    const bin = atob(b64);
    const u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    return new Uint32Array(u8.buffer);
}

export function base64ToUint16(b64) {
    const bin = atob(b64);
    const u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    return new Uint16Array(u8.buffer);
}

export function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1], z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

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
