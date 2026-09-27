import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { OBJExporter } from 'three/addons/exporters/OBJExporter.js';
import { PLYExporter } from 'three/addons/exporters/PLYExporter.js';
import { STLExporter } from 'three/addons/exporters/STLExporter.js';
import { state } from './state.js';
import { Modellexportinhalt } from './modellexport_inhalt.js';
import { Netzpose } from '../gemeinsam/netzpose.js';
import { ObjMtl } from '../gemeinsam/objmtl.js';
import { Gruppennetze } from '../gemeinsam/gruppennetze.js';
import { Klarflaechen } from '../gemeinsam/klarflaechen.js';
import { Vollindex } from '../gemeinsam/vollindex.js';
import { Zusatzdaten } from '../gemeinsam/zusatzdaten.js';
import { Werkstoffvariante } from '../gemeinsam/werkstoffvariante.js';
import { Texturskalierung } from '../gemeinsam/texturskalierung.js';
import { Netzattribute } from '../gemeinsam/netzattribute.js';
import { Genesis9texturen } from '../gemeinsam/genesis9texturen.js';
import { Figuraufbaustand } from '../gemeinsam/figuraufbaustand.js';
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
        // ERST WENN DIE FIGUR GANZ DA IST (26.09.2026, Edgar: „aktiviere
        // export nur wenn die Figur ganz geladen ist"): Genesis 9 kommt in
        // zwei Zügen; zwischen Käfig und voller Stufe steht die Figur
        // vollständig in der Szene und hat ein Sechzehntel ihrer Dreiecke.
        // Ein Export in diesem Fenster ergab 49.552 statt 792.828
        // Körperdreiecken — ohne Meldung (`Figuraufbaustand`).
        await Figuraufbaustand.warten(inst);
        // Bei einer frisch hinzugefügten Figur laufen Texturanfragen noch —
        // `vorladen()` trägt sofort leere Platzhalter ein und füllt sie erst
        // später (siehe `Genesis9texturen.wartenAufAlle`-Doku). Ohne dieses
        // Warten exportiert ein Export direkt nach dem Laden ohne Textur.
        if (optionen.textur) await Genesis9texturen.wartenAufAlle();

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
        // … und derselbe Pfad trägt den GEKÜRZTEN Index der Szene: ohne das
        // hier behielte ein GLB mit Skelett die Löcher unter Kleid und Haaren
        // (`Vollindex`). Nach `Netzattribute.tauschen`, damit die Kopie
        // getauscht wird und nicht die lebende Geometrie.
        const zuruecksetzenVoll = optionen.rig ? Vollindex.tauschen(objekte) : null;
        // Skelett-Wurzeln MIT ins Array — siehe `Modellexportinhalt.skelettWurzeln`.
        const wurzeln = optionen.rig ? Modellexportinhalt.skelettWurzeln(objekte) : [];
        const zuruecksetzenUserData = Zusatzdaten.leeren([...objekte, ...wurzeln]);
        try {
            const clips = animationOk && optionen.rig ? [anim.clip] : [];
            return await new GLTFExporter().parseAsync([...objekte, ...wurzeln], { binary: true, onlyVisible: true, animations: clips });
        } finally {
            zuruecksetzenUserData();
            zuruecksetzenVoll?.();
            zuruecksetzenGeo?.();
            zuruecksetzenTextur?.();
        }
    }

    static async _obj(rohe, optionen) {
        // OBJ kennt keine Materialzonen je Netz — vorher aufteilen, sonst
        // verliert `OBJExporter` die Zuordnung still (siehe `Gruppennetze`).
        const zerlegt = Gruppennetze.zerlegen(rohe);
        // Hornhaut und Tränenfilm raus: OBJ kennt keine Durchsichtigkeit, und
        // MeshLab zeichnet die kartenlose Schale als weiße Kugel über der
        // Iris (siehe `Klarflaechen`).
        const { netze: objekte, weggelassen } = Klarflaechen.entfernen(zerlegt);
        const zuruecksetzen = optionen.textur ? null : Werkstoffvariante.tauschen(objekte);
        try {
            const { mtl, bilder, warnungen } = await ObjMtl.bauen(
                objekte, optionen.textur, `${Modellexport.PLATZHALTER}_`, optionen.aufloesung
            );
            if (weggelassen.length) {
                warnungen.push(
                    `OBJ kennt keine Durchsichtigkeit — ${weggelassen.length} fast durchsichtige `
                    + `Fläche(n) ohne Farbkarte wurden weggelassen (${weggelassen.join(', ')}); `
                    + 'sonst verdecken sie, was dahinter liegt (z. B. die Iris).'
                );
            }
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

// Für Proben und Testfälle: Export ohne Kontextmenü und Dialog auslösen —
// `window.__modellexport.exportieren(inst, optionen)`, Figuren über
// `window.__characters` (dasselbe Muster, `pose_apply.js`).
if (typeof window !== 'undefined') window.__modellexport = Modellexport;
