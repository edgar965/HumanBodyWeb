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

// Die Tabelle stand hier als sechste Kopie — jetzt an EINER Stelle
// (`gemeinsam/koerpermaterialien.js`, Befund `doppelcode` 17.08.2026).
export { BODY_MATERIALS } from '../gemeinsam/koerpermaterialien.js';
