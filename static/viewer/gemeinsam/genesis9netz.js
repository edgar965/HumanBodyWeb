import * as THREE from 'three';
import { Netzgeometrie } from './netzgeometrie.js';
import { Genesis9strang } from './genesis9strang.js';
import { Genesis9haut } from './genesis9haut.js';
import { base64ToFloat32 } from './kodierung.js';

/**
 * Genesis9netz — ein Daz-Netz (Körper, Augen, Mund, Wimpern, Kleidung)
 * mit Materialgruppen und Texturen bauen.
 *
 * WARUM MATERIALGRUPPEN (17.09.2026): Genesis 9 trägt seine Haut in fünf
 * UDIM-Kacheln — Kopf, Körper, Beine, Arme, Nägel je ein 4K-Bild. Der
 * Server liefert die Dreiecke nach Material sortiert und je Gruppe den
 * Indexbereich (`index_ab`/`index_anzahl` zählen EINTRÄGE, nicht Dreiecke —
 * `BufferGeometry.addGroup`) samt den Bildern (`bilder.albedo`, `normalen`,
 * `alpha`, `rauheit`) als Bibliothekspfad. Die UV sind je Gruppe schon in
 * 0..1 (Kachel abgezogen).
 *
 * NACHLADEN, NICHT WARTEN: Die Figur steht sofort im Hautton da und wird
 * scharf, sobald die Bilder kommen (4K-JPGs, 1–3 MB je Kachel). Albedo
 * bekommt `SRGBColorSpace` — ohne ihn kommt die Haut flau und zu hell.
 * `flipY` bleibt beim Standard: Daz' UV laufen wie in OBJ (v nach oben),
 * dieselbe Erfahrung wie bei UMA (`umapythonnetz.js`).
 *
 * Gruppen OHNE Bilder (Augenfeuchte, Träne) werden als Glanzschicht
 * gezeichnet: durchsichtig, glatt. Gruppen mit `alpha` (Wimpern, Haare)
 * bekommen `alphaTest`, damit die Reihenfolge der Dreiecke nicht zählt.
 * Stranghaar (`art: strang`, 17.09.2026) baut `Genesis9strang`. Gruppen
 * mit `schminke` (18.09.2026: Farbe, Gewicht, Rauheit vom Server
 * komponiert) bekommen die Mischung im Shader (`Genesis9haut.schminke`);
 * `detailnormalen` (die 8K, nur mit Strg+Alt+H) mischt `Genesis9haut.detail`.
 */
export class Genesis9netz {

    static ADRESSE = '/api/character/genesis9-figur/textur/';
    /** Hautton, bis die Bilder da sind. */
    static HAUT = 0xd9b39c;
    /** Was ohne Bild eine Glanzschicht ist. */
    static GLANZ = ['EyeMoisture', 'Tear'];

    /**
     * @param daten  Serverantwort mit vertices/faces/normals/uvs (base64) und `gruppen`
     * @param name   Name des Netzes in der Szene
     * @returns {THREE.Mesh}
     */
    static bauen(daten, name) {
        if (daten.art === 'strang') return Genesis9strang.bauen(daten, name);
        // `drehen = false`: Daz rechnet schon in Three-Achsen (Y oben, Meter).
        const geo = Netzgeometrie.bauen(daten, THREE, null, false);
        // Duenne je Punkt (0..1) fuer das Durchlicht der Haut (`Genesis9haut`).
        if (daten.dicke) {
            geo.setAttribute('dicke', new THREE.BufferAttribute(base64ToFloat32(daten.dicke), 1));
        }
        const material = daten.art === 'kappe'
            ? Genesis9strang.kappe(geo, daten.gruppen || [])
            : Genesis9netz.materialien(geo, daten.gruppen || []);
        const netz = new THREE.Mesh(geo, material);
        netz.name = name;
        netz.castShadow = true;
        netz.receiveShadow = true;
        // dForce-Kleidung: Freiheit und Lage des Käfigs für den Stoffschwung (`genesis9stoffschwung.js`).
        if (daten.stoff) {
            netz.userData.stoff = { frei: base64ToFloat32(daten.stoff.frei),
                                    kaefig: base64ToFloat32(daten.stoff.kaefig), stufen: daten.stufen || 0 };
        }
        return netz;
    }

    /** Je Gruppe ein Material — oder eines für alles, wenn Gruppen fehlen. */
    static materialien(geo, gruppen) {
        if (!gruppen.length) return Genesis9netz.haut();
        const liste = [];
        for (const gruppe of gruppen) {
            const material = Genesis9netz.material(gruppe);
            geo.addGroup(gruppe.index_ab, gruppe.index_anzahl, liste.length);
            liste.push(material);
            Genesis9netz.texturen(material, gruppe.bilder || {});
        }
        return liste;
    }

    static material(gruppe) {
        const bilder = gruppe.bilder || {};
        if (!bilder.albedo && Genesis9netz.GLANZ.some(g => gruppe.name.startsWith(g))) {
            return new THREE.MeshPhysicalMaterial({
                color: 0xffffff, roughness: 0.05, metalness: 0,
                transparent: true, opacity: 0.12, depthWrite: false,
            });
        }
        // Klarlack/Metall der Schminke (`Genesis9/glanz.py`) brauchen Threes Physical-Material.
        const material = Genesis9netz.haut(Boolean(bilder.schminke?.glanz));
        if (Genesis9netz.farbe(bilder)) material.color.copy(Genesis9netz.farbe(bilder));
        if (bilder.durchlicht) Genesis9haut.durchlicht(material, bilder.durchlicht);
        if (bilder.schminke) Genesis9haut.schminke(material);
        // 8K-Detailnormalen (nur mit Strg+Alt+H, `Genesis9/browserbilder.py`) über den Grundnormalen.
        if (bilder.detailnormalen && bilder.normalen) Genesis9haut.detail(material, bilder.detailgewicht);
        if (bilder.alpha) {
            material.transparent = true;
            material.alphaTest = 0.3;
            material.side = THREE.DoubleSide;
        }
        return material;
    }

    /**
     * Die Diffusfarbe des Presets als `THREE.Color` — oder null.
     *
     * Daz' Farbkanäle sind sRGB (die Werte des Farbwählers, 0..1); Three
     * rechnet linear. Ohne die Umrechnung stand das Pixie-Haar (`diffuse`
     * 0,31/0,24/0,20 = Dunkelbraun) hellgrau auf dem Kopf (17.09.2026).
     */
    static farbe(bilder) {
        const f = bilder.farbe;
        if (!Array.isArray(f) || f.length < 3) return null;
        return new THREE.Color().setRGB(f[0], f[1], f[2], THREE.SRGBColorSpace);
    }

    static haut(physisch = false) {
        const Art = physisch ? THREE.MeshPhysicalMaterial : THREE.MeshStandardMaterial;
        return new Art({ color: Genesis9netz.HAUT, roughness: 0.6, metalness: 0 });
    }

    /** Die Bilder einer Gruppe nachladen und einhängen. */
    static texturen(material, bilder) {
        const lader = new THREE.TextureLoader();
        const laden = (pfad, danach) => lader.load(
            Genesis9netz.ADRESSE + pfad.split('/').map(encodeURIComponent).join('/'),
            bild => { danach(bild); material.needsUpdate = true; },
            undefined, () => {});
        if (bilder.albedo) {
            laden(bilder.albedo, bild => {
                bild.colorSpace = THREE.SRGBColorSpace;
                material.map = bild;
                // Daz rechnet Farbe × Bild: die Haut ist weiß, die braunen Brauen
                // sind ein helles Bild mal Braun. Ohne Angabe wäre der Hautton
                // ein Ton zu viel — dann weiß.
                const farbe = Genesis9netz.farbe(bilder);
                if (farbe) material.color.copy(farbe); else material.color.setHex(0xffffff);
            });
        }
        if (bilder.normalen) {
            laden(bilder.normalen, bild => {
                material.normalMap = bild;
                // DirectX-Normalen (Y nach unten, `Genesis9/browserbilder.py`): Y umkehren.
                if (bilder.normalenachse === -1) material.normalScale.set(1, -1);
                Genesis9haut.klarlackNormalen(material);
            });
        } else if (bilder.schminke?.normalen) {
            // Glitzer-Normalen brauchen eine Grundnormale (Amala hat keine): flach.
            material.normalMap = Genesis9haut.platzhalter(128, 128, 255);
        }
        if (bilder.detailnormalen && bilder.normalen) {
            laden(bilder.detailnormalen, bild => Genesis9haut.detailBild(material, bild));
        }
        if (bilder.alpha) {
            laden(bilder.alpha, bild => { material.alphaMap = bild; });
        }
        if (bilder.rauheit) {
            laden(bilder.rauheit, bild => {
                material.roughnessMap = bild;
                material.roughness = 1.0;
            });
        }
        for (const art of ['farbe', 'gewicht', 'rauheit', 'glanz', 'normalen']) {
            if (!bilder.schminke?.[art]) continue;
            laden(bilder.schminke[art], bild => Genesis9haut.schminkeBilder(material, { [art]: bild }));
        }
        // Zahlen der Schminke: Top Coat Color/Bump, Modus der Glitzer-Normalen.
        if (bilder.schminke?.werte) Genesis9haut.glanzWerte(material, bilder.schminke.werte);
    }
}
