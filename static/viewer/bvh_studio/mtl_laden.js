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
                    console.log(`[OBJ] mtllib "${ref}" aufgelöst → ${testUrl}`);
                    return testUrl;
                }
            } catch {}
        }
        console.warn(`[OBJ] mtllib "${ref}" konnte nicht im Bundle aufgelöst werden`);
        return null;
    } catch (e) {
        console.warn('[OBJ] MTL-Autodiscover fehlgeschlagen:', e);
        return null;
    }
}

// Parst MTL-Text manuell und baut ein { name: MeshStandardMaterial } Dict.
// Robustet Textur-Pfade (entfernt \\-Separators, ./-Prefix, absolute Pfade → nur Dateiname)
// und lädt jede Textur als eigene Request mit Logging. Texturen werden sowohl unter
// dem im MTL angegebenen (Sub-)Pfad als auch unter dem reinen Dateinamen gesucht.
export async function _parseMtlAndBuildMaterials(mtlUrl) {
    const mtlResp = await fetch(mtlUrl);
    if (!mtlResp.ok) throw new Error(`MTL-Fetch HTTP ${mtlResp.status}`);
    const mtlText = await mtlResp.text();
    const basePath = mtlUrl.substring(0, mtlUrl.lastIndexOf('/') + 1);

    // 1) Parse MTL
    const parsed = {};  // name → props
    let current = null;
    for (const raw of mtlText.split(/\r?\n/)) {
        const line = raw.trim();
        if (!line || line.startsWith('#')) continue;
        const parts = line.split(/\s+/);
        const cmd = parts[0];
        if (cmd === 'newmtl') {
            current = { name: parts.slice(1).join(' ') };
            parsed[current.name] = current;
            continue;
        }
        if (!current) continue;
        const val = parts.slice(1).join(' ');
        if (cmd === 'Kd') current.Kd = parts.slice(1, 4).map(parseFloat);
        else if (cmd === 'Ka') current.Ka = parts.slice(1, 4).map(parseFloat);
        else if (cmd === 'Ks') current.Ks = parts.slice(1, 4).map(parseFloat);
        else if (/^map_kd$/i.test(cmd)) current.map_Kd = val;
        else if (/^map_ks$/i.test(cmd)) current.map_Ks = val;
        else if (/^map_ka$/i.test(cmd)) current.map_Ka = val;
        else if (/^(map_bump|bump)$/i.test(cmd)) current.map_Bump = val;
        else if (/^map_ns$/i.test(cmd)) current.map_Ns = val;
        else if (/^(d|tr)$/i.test(cmd)) current.opacity = parseFloat(parts[1]);
        else if (cmd === 'Ns') current.shininess = parseFloat(parts[1]);
    }

    // 2) Textur-Pfad normalisieren und laden
    const texLoader = new THREE.TextureLoader();
    const loadTex = async (rawPath) => {
        // MTL-Optionen ignorieren (z.B. "-s 1 1 -o 0 0 0 filename.png")
        const tokens = rawPath.split(/\s+/).filter(t => t && !t.startsWith('-'));
        const candidate = tokens[tokens.length - 1] || rawPath;
        // Backslashes → Slashes, ./ entfernen
        const cleaned = candidate.replace(/\\/g, '/').replace(/^\.\//, '');
        const fileName = cleaned.split('/').pop();
        if (!fileName) return null;
        // Versuche beide Varianten: subpath (wie im MTL) UND basename (falls flach ins Bundle hochgeladen)
        const candidates = [cleaned];
        if (fileName !== cleaned) candidates.push(fileName);
        for (const c of candidates) {
            const fullUrl = basePath + c;
            try {
                const tex = await texLoader.loadAsync(fullUrl);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                tex.colorSpace = THREE.SRGBColorSpace;
                tex.needsUpdate = true;
                console.log(`[MTL] Textur geladen: ${c}`);
                return tex;
            } catch (e) {
                // stille Retry auf nächsten Kandidaten
            }
        }
        console.warn(`[MTL] Textur NICHT GEFUNDEN: "${rawPath}" — getestet: ${candidates.map(c => basePath + c).join(', ')}`);
        return null;
    };

    // 3) MeshStandardMaterial pro Eintrag bauen
    const materials = {};
    for (const [name, m] of Object.entries(parsed)) {
        const opts = { roughness: 0.85, metalness: 0.02, side: THREE.DoubleSide };
        if (m.Kd && m.Kd.length === 3) opts.color = new THREE.Color(m.Kd[0], m.Kd[1], m.Kd[2]);
        else opts.color = new THREE.Color(0xffffff);
        if (m.map_Kd) {
            const tex = await loadTex(m.map_Kd);
            if (tex) opts.map = tex;
        }
        if (m.map_Ks) {
            const tex = await loadTex(m.map_Ks);
            if (tex) opts.roughnessMap = tex;
        }
        if (m.map_Bump) {
            const tex = await loadTex(m.map_Bump);
            if (tex) opts.normalMap = tex;
        }
        if (m.opacity != null && m.opacity < 1) { opts.transparent = true; opts.opacity = m.opacity; }
        const mat = new THREE.MeshStandardMaterial(opts);
        mat.name = name;
        materials[name] = mat;
    }
    return materials;
}
