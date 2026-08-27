import * as THREE from 'three';
import { _makeDoubleSided, _mergeSimpleGeos } from './formenbauer.js';
/**
 * Band- und Spiralformen: Spiraltutu, Helixband, Rock.
 *
 * Aus formenbauer.js herausgeloest (Umbau 16.08.2026).
 */


/**
 * Build a spiral-tutu: multiple tutu discs spiraling downward.
 * Each disc is a flat ring with drooping outer edge, positioned along a helix.
 */
export function _buildSpiralTutu(part, radius) {
    const winds     = part.spiralWinds ?? 3;
    const startR    = part.spiralStartR ?? radius * 0.5;
    const endR      = part.spiralEndR ?? radius;
    const posTop    = part.spiralPosTop ?? 0.05;
    const posBottom = part.spiralPosBottom ?? -0.15;
    const thickness = part.tutuThickness ?? 0.008;
    const droop     = part.tutuDroop ?? 0.02;
    const droopFrac = part.tutuDroopStart ?? 0.7;
    const radSegs   = 48; // segments around each disc
    const totalHeight = posTop - posBottom;
    // Steps: each wind gets its own disc
    const steps = Math.max(1, Math.round(winds));
    const geos = [];
    for (let i = 0; i < steps; i++) {
        const t = steps === 1 ? 0.5 : i / (steps - 1); // 0..1
        const y = posTop - t * totalHeight;
        const r = startR + t * (endR - startR);
        const angle = t * winds * Math.PI * 2; // spiral rotation
        const innerR = r * 0.08;
        const halfT = thickness * 0.5;
        const droopR = r * droopFrac;
        const pts = [
            new THREE.Vector2(innerR, halfT),
            new THREE.Vector2(droopR, halfT),
            new THREE.Vector2(r, -droop),
            new THREE.Vector2(r - 0.002, -droop - halfT),
            new THREE.Vector2(droopR, -halfT),
            new THREE.Vector2(innerR, -halfT),
        ];
        let disc = _makeDoubleSided(new THREE.LatheGeometry(pts, radSegs));
        // Rotate disc around Y by spiral angle, then translate to height
        const mat = new THREE.Matrix4().makeRotationY(angle);
        mat.setPosition(0, y, 0);
        disc.applyMatrix4(mat);
        geos.push(disc);
    }
    // Merge all discs
    let merged = geos[0];
    for (let i = 1; i < geos.length; i++) {
        merged = _mergeSimpleGeos(merged, geos[i]);
    }

    // Optional inner skirt (hollow cone connecting top to bottom)
    if (part.spiralSkirt) {
        const skirtThick = thickness;
        const topInnerR  = startR * 0.08;  // match tutu inner hole
        const botInnerR  = endR * 0.08;
        const radSegsSkirt = 48;
        const pts = [
            new THREE.Vector2(topInnerR + skirtThick, posTop),
            new THREE.Vector2(botInnerR + skirtThick, posBottom),
            new THREE.Vector2(botInnerR, posBottom),
            new THREE.Vector2(topInnerR, posTop),
        ];
        const skirtGeo = _makeDoubleSided(new THREE.LatheGeometry(pts, radSegsSkirt));
        merged = _mergeSimpleGeos(merged, skirtGeo);
    }

    return merged;
}

/**
 * Build a skirt (Rock): hollow cone/cylinder with configurable top/bottom radii and thickness.
 */
export function _buildSkirt(part, radius) {
    const radiusTop    = part.skirtRadiusTop ?? radius * 0.3;
    const radiusBottom = part.skirtRadiusBottom ?? radius;
    const posTop       = part.skirtPosTop ?? 0.02;
    const posBottom    = part.skirtPosBottom ?? -0.15;
    const thickness    = part.skirtThickness ?? 0.005;
    const radSegs      = 48;
    const height = posTop - posBottom;
    if (height < 0.001) return new THREE.BufferGeometry();
    // Profile: outer top → outer bottom → inner bottom → inner top (closed loop)
    const pts = [
        new THREE.Vector2(radiusTop, posTop),                           // outer top
        new THREE.Vector2(radiusBottom, posBottom),                     // outer bottom
        new THREE.Vector2(radiusBottom - thickness, posBottom),         // inner bottom
        new THREE.Vector2(Math.max(0.001, radiusTop - thickness), posTop), // inner top
    ];
    const geo = new THREE.LatheGeometry(pts, radSegs);
    return _makeDoubleSided(geo);
}
