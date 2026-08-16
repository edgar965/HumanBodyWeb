/**
 * Objektdateien — Textur, MTL und Mesh eines importierten 3D-Objekts ersetzen.
 *
 * Aus properties.js herausgeloest (Umbau 16.08.2026): drei Hochlade-Vorgaenge,
 * die dort mitten in der Ereignisbindung standen.
 *
 * Alle drei laden in denselben Buendel-Ordner wie das urspruengliche Objekt
 * (`bundleId` aus der bestehenden URL) — sonst finden die MTL-Dateien ihre
 * Texturen nicht mehr.
 */
import * as THREE from 'three';
import { fn } from '../../gemeinsam/registrierung.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';

export class Objektdateien {
    /** Buendel-Kennung aus der vorhandenen Objekt-URL ziehen. */
    static _buendel(track) {
        const m = (track.objectUrl || '').match(/\/scene_objects\/(obj_[^/]+)\//);
        return m ? m[1] : null;
    }

    static async _hochladen(track, datei) {
        const daten = new FormData();
        daten.append('object', datei);
        const buendel = Objektdateien._buendel(track);
        if (buendel) daten.append('bundleId', buendel);
        const ergebnis = await Serverabruf.formular(
            '/api/studio/scene-object-upload/', daten);
        if (!ergebnis.ok) throw new Error(ergebnis.error || 'Upload fehlgeschlagen');
        return ergebnis;
    }

    static _dateiWaehlen(erlaubt) {
        return new Promise(fertig => {
            const eingabe = document.createElement('input');
            eingabe.type = 'file';
            eingabe.accept = erlaubt;
            eingabe.addEventListener('change', () => fertig(eingabe.files[0] || null));
            eingabe.click();
        });
    }

    static async texturErsetzen(track) {
        try {
            const datei = await Objektdateien._dateiWaehlen(
                'image/png,image/jpeg,image/jpg,image/webp');
            if (!datei) return;
            const hoch = await Objektdateien._hochladen(track, datei);
            const textur = await new THREE.TextureLoader().loadAsync(hoch.url);
            textur.wrapS = textur.wrapT = THREE.RepeatWrapping;
            textur.colorSpace = THREE.SRGBColorSpace;
            Objektdateien._jedesMaterial(track, (m) => {
                if (m.map) m.map.dispose();
                m.map = textur;
                m.needsUpdate = true;
            });
            track.objectTextureUrl = hoch.url;
            fn.serverLog?.('obj_texture_replaced', `track=${track.name} file=${datei.name}`);
            fn.updateProperties();
        } catch (e) {
            alert('Textur-Upload fehlgeschlagen: ' + e.message);
        }
    }

    static texturEntfernen(track) {
        Objektdateien._jedesMaterial(track, (m) => {
            if (!m.map) return;
            m.map.dispose();
            m.map = null;
            m.needsUpdate = true;
        });
        track.objectTextureUrl = null;
        fn.updateProperties();
    }

    static async mtlErsetzen(track) {
        try {
            const datei = await Objektdateien._dateiWaehlen('.mtl');
            if (!datei) return;
            const hoch = await Objektdateien._hochladen(track, datei);
            const { MTLLoader } = await import('three/addons/loaders/MTLLoader.js');
            const lader = new MTLLoader();
            lader.setPath(hoch.url.substring(0, hoch.url.lastIndexOf('/') + 1));
            const materialien = await lader.loadAsync(
                hoch.url.substring(hoch.url.lastIndexOf('/') + 1));
            materialien.preload();
            const eintraege = Object.entries(materialien.materials || {});
            if (eintraege.length === 0) { alert('MTL enthält keine Materialien'); return; }
            const erstes = eintraege[0][1];
            track.mesh.traverse(o => {
                if (!o.isMesh) return;
                // Bei mehreren Materialien ueber den Namen zuordnen, sonst das erste.
                const passend = materialien.materials[o.material?.name];
                if (o.material) {
                    const alte = Array.isArray(o.material) ? o.material : [o.material];
                    alte.forEach(m => m.dispose?.());
                }
                o.material = passend || erstes;
            });
            track.objectMtlUrl = hoch.url;
            // Auch im Clip merken, damit Speichern/Laden die neue Datei nimmt.
            const clip = track.clips.find(c => c.type === 'object_clip');
            if (clip) clip.data = { ...clip.data, mtlUrl: hoch.url };
            fn.serverLog?.('obj_mtl_replaced', `track=${track.name} file=${datei.name}`);
        } catch (e) {
            alert('MTL-Upload fehlgeschlagen: ' + e.message);
        }
    }

    /** Mesh tauschen und Lage, Drehung und Groesse des alten uebernehmen. */
    static async meshErsetzen(track) {
        try {
            const datei = await Objektdateien._dateiWaehlen('.obj,.glb,.gltf,.fbx');
            if (!datei) return;
            const hoch = await Objektdateien._hochladen(track, datei);
            const lage = track.mesh.position.clone();
            const drehung = track.mesh.rotation.clone();
            const groesse = track.mesh.scale.x;

            const clip = track.clips.find(c => c.type === 'object_clip');
            if (clip) {
                clip.data = { ...clip.data, url: hoch.url,
                              fileName: datei.name, ext: hoch.ext };
            }
            const se = await import('../objektimport.js');
            await se._loadSceneObjectIntoTrack(track, hoch.url, datei.name, hoch.ext,
                                               clip?.startFrame || 0, null);
            if (track.mesh) {
                track.mesh.position.copy(lage);
                track.mesh.rotation.copy(drehung);
                track.mesh.scale.setScalar(groesse);
            }
            // _loadSceneObjectIntoTrack legt einen neuen Clip an — der urspruengliche
            // hat oben schon die neue URL bekommen, also das Duplikat entfernen.
            const objektclips = track.clips.filter(c => c.type === 'object_clip');
            if (objektclips.length > 1) {
                const idx = track.clips.lastIndexOf(objektclips[objektclips.length - 1]);
                if (idx >= 0) track.clips.splice(idx, 1);
            }
            fn.serverLog?.('obj_mesh_replaced', `track=${track.name} file=${datei.name}`);
            fn.updateProperties();
        } catch (e) {
            alert('Mesh-Upload fehlgeschlagen: ' + e.message);
        }
    }

    static _jedesMaterial(track, tun) {
        track.mesh?.traverse(o => {
            if (!o.isMesh || !o.material) return;
            const mats = Array.isArray(o.material) ? o.material : [o.material];
            for (const m of mats) tun(m);
        });
    }
}
