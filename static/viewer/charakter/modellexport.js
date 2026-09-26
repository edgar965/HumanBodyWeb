import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { OBJExporter } from 'three/addons/exporters/OBJExporter.js';
import { PLYExporter } from 'three/addons/exporters/PLYExporter.js';
import { STLExporter } from 'three/addons/exporters/STLExporter.js';
import { state } from './state.js';
import { Modellexportinhalt } from './modellexport_inhalt.js';
import { Netzpose } from '../gemeinsam/netzpose.js';
import { ObjMtl } from '../gemeinsam/objmtl.js';
import { Werkstoffvariante } from '../gemeinsam/werkstoffvariante.js';
import { Texturskalierung } from '../gemeinsam/texturskalierung.js';
import { Netzattribute } from '../gemeinsam/netzattribute.js';
import { Colladaschreiber } from '../gemeinsam/collada/colladaschreiber.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Modellexport — sammelt Objekte, schreibt die gewählten Formate, schickt
 * sie an den Server (`core/api/modellexport.py`).
 *
 * DER BROWSER SCHREIBT DIE FORMATE, DER SERVER LEGT NUR AB — außer bei
 * `.blend`, das läuft durch Blender (`Docu/konzept_modellexport.md`).
 */
export class Modellexport {

    //: Muss mit `core/dienste/modellexportlauf.PLATZHALTER` übereinstimmen —
    //: jede hochgeladene Datei heißt so, der Server ersetzt es durch den
    //: geprüften, eindeutigen Namensstamm.
    static PLATZHALTER = 'MODELL';
    static ENDPUNKT = '/api/character/modellexport/';

    /**
     * @param inst      die Figur (`state.characters.get(...)`)
     * @param optionen  {formate, rig, textur, assets, animation, pose, ordner, name}
     * @returns {ordner, dateien, warnungen} — vom Server
     */
    static async exportieren(inst, optionen) {
        const anim = Modellexportinhalt.animationsstand(inst);
        const animationOk = !!(optionen.animation && anim.aktiv && !anim.fremd);
        const warnungen = Modellexportinhalt.warnungen(inst, optionen);

        const objekteRig = Modellexportinhalt.objekte(inst, { assets: optionen.assets });
        let gebackenCache = null;
        const gebacken = () => {
            if (!gebackenCache) {
                const gruppe = new THREE.Group();
                objekteRig.forEach((obj) => gruppe.add(Netzpose.gebacken(obj, optionen.pose)));
                gruppe.updateMatrixWorld(true);
                // KOPIE, nicht die lebende `children`-Liste: `_obj`/`_ply`/`_stl`
                // haengen dieselben Netze je einmal in eine EIGENE, neue Gruppe
                // um (Three.js' `add()` nimmt dabei automatisch aus der alten
                // Gruppe heraus) — ohne die Kopie wuerde `gebackenCache` dabei
                // leerlaufen, und das naechste Format faende nichts mehr.
                gebackenCache = [...gruppe.children];
            }
            return gebackenCache;
        };

        const dateien = [];
        let glbBytes = null;
        if (optionen.formate.includes('glb') || optionen.formate.includes('blend')) {
            const rigObjekte = optionen.rig ? objekteRig : gebacken();
            glbBytes = await Modellexport._glb(rigObjekte, optionen, animationOk, anim);
            if (optionen.formate.includes('glb')) {
                dateien.push({ name: `${Modellexport.PLATZHALTER}.glb`, blob: new Blob([glbBytes], { type: 'model/gltf-binary' }) });
            }
        }
        if (optionen.formate.includes('obj')) {
            const teilergebnis = await Modellexport._obj(gebacken(), optionen);
            dateien.push(...teilergebnis.dateien);
            warnungen.push(...teilergebnis.warnungen);
        }
        if (optionen.formate.includes('ply')) dateien.push(await Modellexport._ply(gebacken()));
        if (optionen.formate.includes('stl')) dateien.push(Modellexport._stl(gebacken()));
        if (optionen.formate.includes('dae')) {
            const rigObjekte = optionen.rig ? objekteRig : gebacken();
            const teilergebnis = await Modellexport._dae(rigObjekte, optionen, animationOk, inst.group);
            dateien.push(...teilergebnis.dateien);
            warnungen.push(...teilergebnis.warnungen);
        }

        const blendQuelle = optionen.formate.includes('blend')
            ? new Blob([glbBytes], { type: 'model/gltf-binary' }) : null;

        Protokoll.info('Modellexport', `${optionen.formate.join(', ')} nach ${optionen.ordner}`);
        return Modellexport._senden(optionen, dateien, blendQuelle, warnungen);
    }

    // -------------------------------------------------------------- Formate

    static async _glb(objekte, optionen, animationOk, anim) {
        const zuruecksetzenTextur = optionen.textur
            ? Texturskalierung.tauschen(objekte, optionen.aufloesung)
            : Werkstoffvariante.tauschen(objekte);
        // Bei „Rig aus" ist `objekte` schon `Netzpose.gebacken()`-Kopien, die
        // eigene Attribute bereits los sind — beim rigged (LIVE-)Pfad noch nicht.
        const zuruecksetzenGeo = optionen.rig ? Netzattribute.tauschen(objekte) : null;
        // Skelett-Wurzeln MIT ins Array — siehe `Modellexportinhalt.skelettWurzeln`.
        const wurzeln = optionen.rig ? Modellexportinhalt.skelettWurzeln(objekte) : [];
        const zuruecksetzenUserData = Modellexport._userDataLeeren([...objekte, ...wurzeln]);
        try {
            const clips = animationOk && optionen.rig ? [anim.clip] : [];
            return await new GLTFExporter().parseAsync([...objekte, ...wurzeln], { binary: true, onlyVisible: true, animations: clips });
        } finally {
            zuruecksetzenUserData();
            zuruecksetzenGeo?.();
            zuruecksetzenTextur?.();
        }
    }

    /**
     * `GLTFExporter` kopiert `object.userData`/`material.userData` 1:1 nach
     * `extras` — bei Genesis 9 stecken dort App-interne Daten (`gruppe`,
     * `kachel`, `regler`, …), bis über 6 MB JE MESH (Fund 26.09.2026: eine
     * 510-MB-GLB, wovon 425 MB reiner JSON-Text waren). Kein Zielformat
     * braucht das — kurz leeren, nach dem Export zurückstellen.
     */
    static _userDataLeeren(objekte) {
        const eintraege = [];
        const leeren = (obj) => {
            if (obj.userData && Object.keys(obj.userData).length) {
                eintraege.push([obj, 'userData', obj.userData]);
                obj.userData = {};
            }
            const mats = Array.isArray(obj.material) ? obj.material : obj.material ? [obj.material] : [];
            for (const mat of mats) {
                if (mat.userData && Object.keys(mat.userData).length) {
                    eintraege.push([mat, 'userData', mat.userData]);
                    mat.userData = {};
                }
            }
        };
        objekte.forEach((obj) => obj.traverse(leeren));
        return () => eintraege.forEach(([ziel, feld, wert]) => { ziel[feld] = wert; });
    }

    static async _obj(objekte, optionen) {
        const zuruecksetzen = optionen.textur ? null : Werkstoffvariante.tauschen(objekte);
        try {
            const { mtl, bilder, warnungen } = await ObjMtl.bauen(
                objekte, optionen.textur, `${Modellexport.PLATZHALTER}_`, optionen.aufloesung
            );
            const gruppe = new THREE.Group();
            objekte.forEach((o) => gruppe.add(o));
            gruppe.updateMatrixWorld(true);
            const objText = `mtllib ${Modellexport.PLATZHALTER}.mtl\n` + new OBJExporter().parse(gruppe);
            const dateien = [
                { name: `${Modellexport.PLATZHALTER}.obj`, blob: new Blob([objText], { type: 'text/plain' }) },
                { name: `${Modellexport.PLATZHALTER}.mtl`, blob: new Blob([mtl], { type: 'text/plain' }) },
                ...bilder.map((b) => ({ name: b.dateiname, blob: b.blob })),
            ];
            return { dateien, warnungen };
        } finally {
            zuruecksetzen?.();
        }
    }

    static async _ply(objekte) {
        const gruppe = new THREE.Group();
        objekte.forEach((o) => gruppe.add(o));
        gruppe.updateMatrixWorld(true);
        const puffer = await new Promise((resolve) => {
            new PLYExporter().parse(gruppe, resolve, { binary: true });
        });
        return { name: `${Modellexport.PLATZHALTER}.ply`, blob: new Blob([puffer], { type: 'application/octet-stream' }) };
    }

    static _stl(objekte) {
        const gruppe = new THREE.Group();
        objekte.forEach((o) => gruppe.add(o));
        gruppe.updateMatrixWorld(true);
        const daten = new STLExporter().parse(gruppe, { binary: true });
        return { name: `${Modellexport.PLATZHALTER}.stl`, blob: new Blob([daten], { type: 'model/stl' }) };
    }

    static async _dae(objekte, optionen, animationOk, wurzel) {
        const animation = animationOk && optionen.rig
            ? { wurzel, mixer: state.mixer, action: state.currentAction } : null;
        const { xml, bilder, warnungen } = await Colladaschreiber.bauen(objekte, {
            textur: optionen.textur, rig: optionen.rig, animation, praefix: `${Modellexport.PLATZHALTER}_`,
            aufloesung: optionen.aufloesung,
        });
        const dateien = [
            { name: `${Modellexport.PLATZHALTER}.dae`, blob: new Blob([xml], { type: 'model/vnd.collada+xml' }) },
            ...bilder.map((b) => ({ name: b.dateiname, blob: b.blob })),
        ];
        return { dateien, warnungen };
    }

    // -------------------------------------------------------------- Senden

    static async _senden(optionen, dateien, blendQuelle, warnungen) {
        const formular = new FormData();
        formular.append('ordner', optionen.ordner);
        formular.append('name', optionen.name);
        formular.append('warnungen', JSON.stringify(warnungen));
        for (const d of dateien) formular.append('dateien', d.blob, d.name);
        if (blendQuelle) formular.append('blend_quelle', blendQuelle, `${Modellexport.PLATZHALTER}.glb`);
        const antwort = await Serverabruf.formular(Modellexport.ENDPUNKT, formular);
        return { ...antwort, warnungen: [...new Set([...warnungen, ...(antwort.warnungen || [])])] };
    }
}
