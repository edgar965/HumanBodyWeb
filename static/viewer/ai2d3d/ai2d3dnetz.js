/**
 * Ai2d3dnetz — Feld 2 „Netz“ der Seite „2d-3d-AI“ (24.10.2026): das Netz aus den Fotos (Hunyuan3D-2mv oder Tripo3D) als GLB, Zeichner für `Mesh3daiansicht`.
 *
 * Die Ansichtsarten wie bei Mesh3D-AI (`Mesh3daimaterial.MODI`, Materialien `Mesh3daiechtmaterial`): „Textur“ zeigt die Materialien der Datei, alle anderen Arten zeichnet das Feld mit EINEM Ersatzmaterial
 * über Ebene 1 (`inhalt.userData.genesisErsatz`, derselbe Weg wie die Genesis-Figur in `Mesh3daigenesisfigur`). Ein Netz wird je Adresse einmal geladen; die Tripo-Dateien haben 61–69 MB
 * und ~1,9 Mio. Dreiecke (gelesen 24.10.2026, `_wegwerf/ai2d3d/glb_kopf.py`) — der Ladestand steht im Feld.
 */
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Mesh3daiechtmaterial } from '../mesh3dai/mesh3daiechtmaterial.js';

export class Ai2d3dnetz {
    /** @param {(text: string) => void} melden Ladestand ins Feld @param {() => void} fertig das Feld neu zeigen */
    constructor(melden, fertig) {
        this.melden = melden;
        this.fertig = fertig;
        this._netze = new Map();
    }

    /** Ersatzmaterial der Ansichtsart; `null` = die eigenen Materialien („Textur“). */
    static ersatz(modus) {
        if (modus === 'textur') return null;
        const art = modus === 'punkte' || modus === 'oberflaeche_draht' ? 'oberflaeche' : modus;
        const netz = Mesh3daiechtmaterial.netz(undefined, art);
        return netz.material ?? netz.children?.[0]?.material ?? null;
    }

    _laden(netz) {
        const e = { stand: 'laedt', szene: null, text: `${netz.name} wird geladen … (${netz.mb} MB)` };
        this._netze.set(netz.adresse, e);
        const anfang = performance.now();
        new GLTFLoader().load(netz.adresse, gltf => {
            e.szene = gltf.scene;
            e.stand = 'fertig';
            e.text = '';
            e.dauer = Math.round(performance.now() - anfang);
            this.fertig();
        }, fortschritt => {
            if (fortschritt.total) this.melden(`${netz.name} wird geladen … ${Math.round(100 * fortschritt.loaded / fortschritt.total)} % von ${netz.mb} MB`);
        }, fehler => {
            e.stand = 'fehler';
            e.text = `${netz.name} nicht geladen: ${fehler?.message ?? fehler}`;
            console.warn(`Ai2d3dnetz: ${e.text}`);
            this.fertig();
        });
        return e;
    }

    /** Zeichner von `Mesh3daiansicht`: `d = {netz: {name, mb, adresse}, modus}`. */
    zeichnen(inhalt, _art, d) {
        if (!d.netz) {
            inhalt.userData.hinweis = 'Für diesen Job liegt kein Netz aus den Fotos vor.';
            return;
        }
        const e = this._netze.get(d.netz.adresse) ?? this._laden(d.netz);
        if (e.stand !== 'fertig') {
            inhalt.userData.hinweis = e.text;
            return;
        }
        e.szene.traverse(o => { o.layers.set(1); o.frustumCulled = false; });
        // Gehört nicht dem Feld (`Mesh3daiansicht._leeren` gibt es dann nicht frei) — beim nächsten Zeigen hängt es wieder ein.
        e.szene.userData.mesh3daiFremd = true;
        inhalt.add(e.szene);
        inhalt.userData.genesisErsatz = Ai2d3dnetz.ersatz(d.modus);
        this.dauer = e.dauer;
    }
}
