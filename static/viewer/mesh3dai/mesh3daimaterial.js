/**
 * Mesh3daimaterial — die Ansichtsarten der Zeilen auf der Seite „Mesh3D-AI“ (14.10.2026, Edgar: „mach in jeder Zeile des Vergleichs Ansichtsoptionen: Drahtnetz, Oberfläche, Textur — oder nimm dir noch andere Vorlagen von Blender“).
 * Die Namen in Klammern sind die Blender-Ansichten, an die sich die Art anlehnt. `netz` macht aus einer Geometrie das Objekt für die gewählte Art (bei „Oberfläche + Drahtnetz“ zwei übereinanderliegende Netze);
 * die Zeichner (`Mesh3daikapseln`, `Mesh3daigesichtzeichner`) reichen ihre Geometrie und den Stil nur durch. „Punkte / Gerüst“ ist keine Fläche und wird von den Zeichnern selbst behandelt.
 */
import * as THREE from 'three';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';
import { Mesh3daitextur } from './mesh3daitextur.js';

export class Mesh3daimaterial {
    static MODI = [
        { schluessel: 'oberflaeche', name: 'Oberfläche', icon: 'fa-cube', hinweis: 'Geschlossene Fläche mit Licht, in allen drei Feldern in derselben Farbe (Blender: Solid). Farben zeigen „Textur“ und „Punkte“.' },
        { schluessel: 'drahtnetz', name: 'Drahtnetz', icon: 'fa-border-all', hinweis: 'Nur die Kanten der Dreiecke (Blender: Wireframe).' },
        { schluessel: 'oberflaeche_draht', name: 'Oberfläche + Drahtnetz', icon: 'fa-layer-group', hinweis: 'Fläche mit den Kanten darüber (Blender: Solid mit Wireframe-Überlagerung).' },
        { schluessel: 'textur', name: 'Textur', icon: 'fa-image', hinweis: 'Fläche mit Karte (Blender: Material Preview). Attrappe: ein erfundenes Muster. Echte Daten: Ziel und Ergebnis mit den Bildern der Figur (Haut, Kleider); Start in den Farben, die das Netz bekommt (flache Teilfarben).' },
        { schluessel: 'matcap', name: 'Matcap', icon: 'fa-circle', hinweis: 'Beleuchtung aus einer Kugelkarte, unabhängig vom Licht der Szene (Blender: Solid mit MatCap).' },
        { schluessel: 'normalen', name: 'Normalen', icon: 'fa-palette', hinweis: 'Die Richtung der Fläche als Farbe — zeigt Knicke und umgedrehte Dreiecke.' },
        { schluessel: 'roentgen', name: 'Röntgen', icon: 'fa-eye', hinweis: 'Durchscheinend, Überlagerungen werden heller (Blender: X-Ray).' },
        { schluessel: 'punkte', name: 'Punkte', icon: 'fa-braille', hinweis: 'Start: die Punktwolke, die das Netz bekommt. Ziel und Ergebnis: die Punkte der Fläche (Attrappe: Punkte und Linien der Dummy-Flächen). Das Genesis-Skelett schaltet der Knopf „Rig“.' },
    ];
    static VORGABE = 'oberflaeche';
    static GEISTFARBE = 0xcfd6e4;

    /** Die Farbe aufgehellt, damit Linien und Gerüst auch bei dunklen Stücken (Hose, Schuhe) auf dem dunklen Grund zu sehen sind. */
    static heller(farbe, anteil = 0.55) {
        return new THREE.Color(farbe).lerp(new THREE.Color(1, 1, 1), anteil);
    }

    /** Hex einer Farbe (Zahl oder `THREE.Color`) — der Schlüssel der geteilten Materialien (`Mesh3daigemeinsam`). */
    static _hex(farbe) {
        return new THREE.Color(farbe).getHex();
    }

    static _draht(geo, farbe, deckkraft) {
        const material = Mesh3daigemeinsam.material(`draht:${Mesh3daimaterial._hex(farbe)}:${deckkraft}`,
            () => new THREE.MeshBasicMaterial({ color: farbe, wireframe: true, transparent: deckkraft < 1, opacity: deckkraft }));
        return new THREE.Mesh(geo, material);
    }

    /**
     * @param {THREE.BufferGeometry} geo
     * @param {{modus?: string, wand?: boolean, sollfarbe: number, gruppe?: string, tint?: number, deckkraft?: number}} stil
     *   `sollfarbe` die Farbe des Modells an dieser Stelle; `tint` ersetzt sie (Ausgabe des Netzes: orange); `wand` = Geist, immer als Drahtnetz; `gruppe` wählt das Muster der Textur.
     * @returns {THREE.Object3D} ein Netz oder eine Gruppe aus zwei Netzen — Lage und Drehung setzt der Aufrufer
     */
    static netz(geo, stil) {
        const z = Mesh3daimaterial;
        if (stil.wand) return z._draht(geo, z.GEISTFARBE, 0.45);
        const farbe = stil.tint ?? stil.sollfarbe;
        const deckkraft = stil.deckkraft ?? 1;
        const durchsichtig = deckkraft < 1;
        const modus = stil.modus ?? z.VORGABE;
        const mat = (schluessel, fabrik) => Mesh3daigemeinsam.material(`${modus}:${schluessel}`, fabrik);
        switch (modus) {
            case 'drahtnetz':
                return z._draht(geo, z.heller(farbe), 1);
            case 'oberflaeche_draht': {
                const gruppe = new THREE.Group();
                const flaeche = mat(`${z._hex(farbe)}:${deckkraft}`, () => new THREE.MeshStandardMaterial({ color: farbe, roughness: 0.75, transparent: durchsichtig, opacity: deckkraft, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 }));
                gruppe.add(new THREE.Mesh(geo, flaeche));
                gruppe.add(z._draht(geo, 0xffffff, 0.35));
                return gruppe;
            }
            case 'textur': {
                const tint = stil.tint ?? 0xffffff;
                return new THREE.Mesh(geo, mat(`${stil.gruppe}:${z._hex(stil.sollfarbe)}:${z._hex(tint)}:${deckkraft}`,
                    () => new THREE.MeshStandardMaterial({ map: Mesh3daitextur.fuer(stil.gruppe, stil.sollfarbe), color: tint, roughness: 0.8, transparent: durchsichtig, opacity: deckkraft })));
            }
            case 'matcap':
                return new THREE.Mesh(geo, mat(`${z._hex(farbe)}:${deckkraft}`, () => new THREE.MeshMatcapMaterial({ matcap: Mesh3daitextur.matcap(), color: farbe, transparent: durchsichtig, opacity: deckkraft })));
            case 'normalen':
                return new THREE.Mesh(geo, mat(`${deckkraft}`, () => new THREE.MeshNormalMaterial({ transparent: durchsichtig, opacity: deckkraft })));
            case 'roentgen':
                return new THREE.Mesh(geo, mat(`${z._hex(farbe)}`, () => new THREE.MeshBasicMaterial({ color: z.heller(farbe, 0.3), transparent: true, opacity: 0.28, depthWrite: false, blending: THREE.AdditiveBlending })));
            default:
                return new THREE.Mesh(geo, mat(`${z._hex(farbe)}:${deckkraft}`, () => new THREE.MeshStandardMaterial({ color: farbe, roughness: 0.75, transparent: durchsichtig, opacity: deckkraft })));
        }
    }
}
