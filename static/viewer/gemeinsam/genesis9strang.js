import * as THREE from 'three';
import { Netzgeometrie } from './netzgeometrie.js';
import { base64ToFloat32 } from './kodierung.js';

/**
 * Genesis9strang — dForce-Stranghaar von Daz als Linien.
 *
 * WAS DER SERVER SCHICKT (`Genesis9/strang.py`, 17.09.2026): die Strangpunkte
 * (236.136 beim Pixie-Schnitt), je Segment ein ENTARTETES Dreieck `[a, b, b]`
 * in `faces`, die Materialgruppen mit ihrer Farbe (`bilder.farbe`, aus dem
 * Preset — Auburn, Black, Blonde …), die Hautgewichte der Haarkappe und
 * `anteil` (0 an der Wurzel, 1 an der Spitze).
 *
 * WARUM DREIECKE UND `wireframe`: Three.js häutet nur ein `SkinnedMesh`
 * (`Eigenhaut.binden` macht aus jedem Mesh eines); `LineSegments` kennt kein
 * Skinning. Ein Drahtgitter-Material zeichnet von jedem Dreieck nur die
 * Kanten — bei `[a, b, b]` ist das genau die Strecke a–b. So bewegen sich die
 * Strähnen mit dem Kopf wie jedes andere Netz. Linien sind ein Pixel breit
 * (WebGL); Daz zeigt Strähnen im Ansichtsfenster ebenso.
 *
 * Die Farbe läuft zur Spitze hin heller (Wurzel 60 %, Spitze 100 % der
 * Presetfarbe) — eine Darstellung, damit die Linien Tiefe bekommen. Bringt
 * das Preset eine Spitzenfarbe mit (`bilder.farbe_spitze`, OmniHair
 * `Hair Root/Tip Color` — HS Viola Hair, `G9haarfarben`, 20.09.2026), wird
 * statt dessen von der Wurzel- zur Spitzenfarbe gemischt, wie Daz' Shader.
 */
export class Genesis9strang {

    static WURZEL = 0.6;

    static bauen(daten, name) {
        const geo = Netzgeometrie.bauen(daten, THREE, null, false);
        geo.deleteAttribute('normal');
        const anteil = daten.anteil ? base64ToFloat32(daten.anteil) : null;
        const gruppen = daten.gruppen || [];
        const materialien = [];
        const farben = new Float32Array(geo.attributes.position.count * 3);
        for (const gruppe of gruppen) {
            const farbe = Genesis9strang.farbe(gruppe.bilder || {});
            const spitze = Genesis9strang.spitze(gruppe.bilder || {});
            geo.addGroup(gruppe.index_ab, gruppe.index_anzahl, materialien.length);
            materialien.push(new THREE.MeshBasicMaterial({
                color: 0xffffff, wireframe: true, vertexColors: true,
            }));
            Genesis9strang._faerben(geo, gruppe, farbe, anteil, farben, spitze);
        }
        geo.setAttribute('color', new THREE.BufferAttribute(farben, 3));
        const netz = new THREE.Mesh(geo, materialien.length ? materialien
            : new THREE.MeshBasicMaterial({ color: 0x3a2a1e, wireframe: true }));
        netz.name = name;
        netz.castShadow = false;
        netz.receiveShadow = false;
        return netz;
    }

    /** Die Presetfarbe (sRGB bei Daz) linear — wie `Genesis9netz.farbe`. */
    /**
     * Die Haarkappe unter den Strähnen (`art: kappe`): unbeleuchtet in der
     * Wurzelfarbe — sie ist die Kopfhaut ohne Bild und stünde beleuchtet
     * (drei Lichter, Summe 7,5) hell unter dunklem Haar.
     */
    static kappe(geo, gruppen) {
        const liste = [];
        for (const gruppe of gruppen) {
            const farbe = Genesis9strang.farbe(gruppe.bilder || {})
                .multiplyScalar(Genesis9strang.WURZEL);
            geo.addGroup(gruppe.index_ab, gruppe.index_anzahl, liste.length);
            liste.push(new THREE.MeshBasicMaterial({ color: farbe }));
        }
        return liste.length ? liste : new THREE.MeshBasicMaterial({ color: 0x231a13 });
    }

    static farbe(bilder) {
        const f = bilder.farbe;
        return (Array.isArray(f) && f.length >= 3)
            ? new THREE.Color().setRGB(f[0], f[1], f[2], THREE.SRGBColorSpace)
            : new THREE.Color(0x3a2a1e);
    }

    /** Die Spitzenfarbe des OmniHair-Shaders (sRGB) — oder null. */
    static spitze(bilder) {
        const f = bilder.farbe_spitze;
        return (Array.isArray(f) && f.length >= 3)
            ? new THREE.Color().setRGB(f[0], f[1], f[2], THREE.SRGBColorSpace)
            : null;
    }

    /**
     * Die Punkte der Gruppe färben — über die Indizes ihres Bereichs. Mit
     * `spitze` Wurzel → Spitze gemischt (Daz' Root-Tip Blend), sonst die
     * Wurzelfarbe zur Spitze hin aufgehellt.
     */
    static _faerben(geo, gruppe, farbe, anteil, farben, spitze = null) {
        const index = geo.index.array;
        const ende = gruppe.index_ab + gruppe.index_anzahl;
        for (let i = gruppe.index_ab; i < ende; i++) {
            const p = index[i];
            const t = anteil ? anteil[p] : 1;
            if (spitze) {
                farben[p * 3] = farbe.r + (spitze.r - farbe.r) * t;
                farben[p * 3 + 1] = farbe.g + (spitze.g - farbe.g) * t;
                farben[p * 3 + 2] = farbe.b + (spitze.b - farbe.b) * t;
                continue;
            }
            const hell = Genesis9strang.WURZEL + (1 - Genesis9strang.WURZEL) * t;
            farben[p * 3] = farbe.r * hell;
            farben[p * 3 + 1] = farbe.g * hell;
            farben[p * 3 + 2] = farbe.b * hell;
        }
    }
}
