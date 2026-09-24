/**
 * MTL-Dateien finden und in Three.js-Materialien uebersetzen.
 *
 * Aus scene_extras.js herausgeloest (Umbau 16.08.2026): Der eingebaute
 * MTLLoader scheitert an Pfaden, wie sie Blender und 3ds Max schreiben —
 * Rueckstriche, `./`-Vorsatz, absolute Pfade. Darum wird hier von Hand
 * geparst und jede Textur einzeln gesucht: erst unter dem angegebenen
 * (Unter-)Pfad, dann unter dem blossen Dateinamen im selben Ordner.
 */

import * as THREE from 'three';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Mtlwerkstoffe } from './mtl_werkstoffe.js';

const _textureLoader = new THREE.TextureLoader();


// Liest OBJ-Datei-Inhalt und extrahiert die 'mtllib'-Referenz. Versucht die
// referenzierte MTL-Datei erst unter dem im OBJ angegebenen (Sub-)Pfad zu laden,
// fällt dann auf den reinen Dateinamen im OBJ-Verzeichnis zurück.
// Returns: URL zur gefundenen MTL, oder null.
export async function _autoDiscoverMtl(objUrl) {
    try {
        const resp = await fetch(objUrl);
        if (!resp.ok) return null;
        const text = await resp.text();
        // Erster Treffer (OBJ kann mehrere mtllib haben, wir nehmen den ersten)
        const m = text.match(/^\s*mtllib\s+(.+?)\s*$/im);
        if (!m) return null;
        const ref = m[1].trim();
        const cleaned = ref.replace(/\\/g, '/').replace(/^\.\//, '');
        const basePath = objUrl.substring(0, objUrl.lastIndexOf('/') + 1);
        // 1. Versuch: im OBJ angegebener (möglicherweise Sub-)Pfad
        const candidates = [cleaned];
        // 2. Fallback: nur Dateiname (falls User flach ins Bundle geladen hat)
        const fileName = cleaned.split('/').pop();
        if (fileName !== cleaned) candidates.push(fileName);
        for (const c of candidates) {
            const testUrl = basePath + c;
            try {
                const head = await fetch(testUrl, { method: 'HEAD' });
                if (head.ok) {
                    Protokoll.debug('OBJ', `mtllib "${ref}" aufgelöst → ${testUrl}`);
                    return testUrl;
                }
            } catch { Protokoll.debug('OBJ', `mtllib-Kandidat ${testUrl} nicht erreichbar`); }
        }
        Protokoll.warnung('OBJ', `mtllib "${ref}" konnte nicht im Bundle aufgelöst werden`);
        return null;
    } catch (e) {
        Protokoll.warnung('OBJ', 'MTL-Autodiscover fehlgeschlagen:', e);
        return null;
    }
}

/**
 * Eine MTL-Datei laden und in Three.js-Materialien uebersetzen.
 *
 * Die drei Schritte — zerlegen, Texturen laden, Materialien bauen — stehen
 * seit dem 30.08.2026 als `Mtlwerkstoffe` daneben (Befund `jsfunktionen`:
 * diese Funktion war 90 Zeilen lang).
 *
 * @param {string} mtlUrl Adresse der MTL-Datei
 * @returns {Promise<object>} { Materialname: THREE.MeshStandardMaterial }
 */
export async function _parseMtlAndBuildMaterials(mtlUrl) {
    const antwort = await fetch(mtlUrl);
    if (!antwort.ok) throw new Error(`MTL-Fetch HTTP ${antwort.status}`);
    const basisPfad = mtlUrl.substring(0, mtlUrl.lastIndexOf('/') + 1);
    const eintraege = Mtlwerkstoffe.zerlegen(await antwort.text());
    return Mtlwerkstoffe.bauen(eintraege, basisPfad);
}
