/**
 * Stueckfeder — der weiche Rand eines Ersatzstücks (die Scham aus einer .blend) in Three.js.
 *
 * Die Rechnung steht in `stueckrand.js` (ohne Three.js). Hier nur: die Deckkraft als Attribut `randalpha` an die
 * Geometrie legen und die Materialien des Netzes so patchen, dass sie sie auf die Deckkraft anwenden. Das Material wird
 * dazu `transparent` (sonst bliebe jeder Alpha-Wert 1: Three.js setzt bei undurchsichtigen Materialien `OPAQUE`).
 *
 * Der Eingriff läuft über `Shaderpatch`, damit er neben dem Hautshader (`genesis9haut`) und dem Einzug besteht.
 */
import * as THREE from 'three';
import { Shaderpatch } from './shaderpatch.js';
import { Stueckrand } from './stueckrand.js';
import { Figurhaut } from './figurhaut.js';
import { Hautmaske } from './hautmaske.js';

export class Stueckfeder {

    static SCHLUESSEL = 'randfeder';

    /**
     * Die Fahnen am Rand abtragen (`Stueckrand.fahnen`), die Deckkraft des verbleibenden Rands an das Netz legen und die
     * Materialien patchen. Der volle Index bleibt in `geometry.userData.indexVoll` (wie bei der Haut).
     * @returns {number|false} Anzahl abgetragener Dreiecke, `false` ohne Netz
     */
    static setzen(netz) {
        const geo = netz?.geometry;
        if (!geo?.attributes?.position || !geo.index) return false;
        const voll = Figurhaut.merken(geo);
        const weg = Stueckrand.fahnen(geo.attributes.position.array, voll.index);
        const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, new Uint8Array(geo.attributes.position.count), weg);
        Figurhaut.indexSetzen(geo, neu.index, neu.gruppen);
        const a = Stueckrand.deckkraft(geo.attributes.position.array, neu.index);
        geo.setAttribute('randalpha', new THREE.BufferAttribute(a, 1));
        for (const mat of Array.isArray(netz.material) ? netz.material : [netz.material]) Stueckfeder.patchen(mat);
        return neu.entfernt;
    }

    /**
     * Den Eingriff von `setzen` rückgängig machen: voller Index (die Fahnen sind wieder da), Deckkraft 1 überall. Für ein Stück, das
     * auf der groben Stufe noch als Ersatzstück gerechnet wurde und auf der feinen verschweißt ist (`hautloch.js`) — dort endet der
     * Rand genau auf der Haut und braucht weder Feder noch Abtrag.
     */
    static zuruecknehmen(netz) {
        const geo = netz?.geometry;
        const voll = geo?.userData?.indexVoll;
        if (voll && geo.index && geo.index.count !== voll.index.length) Figurhaut.indexSetzen(geo, voll.index, voll.gruppen);
        const alpha = geo?.getAttribute('randalpha');
        if (!alpha) return false;
        alpha.array.fill(1);
        alpha.needsUpdate = true;
        for (const mat of Array.isArray(netz.material) ? netz.material : [netz.material]) {
            if (mat && mat.transparent && !mat.alphaMap) { mat.transparent = false; mat.needsUpdate = true; }
        }
        return true;
    }

    /** Den Eingriff an ein Material hängen (einmal). */
    static patchen(mat) {
        if (!mat || Shaderpatch.hat(mat, Stueckfeder.SCHLUESSEL)) return;
        mat.transparent = true;
        mat.depthWrite = true;
        Shaderpatch.anhaengen(mat, Stueckfeder.SCHLUESSEL, (shader) => {
            Shaderpatch.hinterInclude(shader, 'common', 'attribute float randalpha;\nvarying float vRandalpha;');
            Shaderpatch.hinterInclude(shader, 'begin_vertex', 'vRandalpha = randalpha;');
            shader.fragmentShader = shader.fragmentShader
                .replace('#include <common>', '#include <common>\nvarying float vRandalpha;')
                .replace('#include <color_fragment>', '#include <color_fragment>\ndiffuseColor.a *= vRandalpha;');
        });
    }
}
