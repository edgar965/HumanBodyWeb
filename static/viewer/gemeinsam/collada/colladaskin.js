import { zahlen, reinerName, zeilenMajor } from './colladaxml.js';

/**
 * Colladaskin — die Bind-Pose eines Skeletts, und `<controller><skin>` je
 * SkinnedMesh.
 *
 * DIE BIND-POSE KOMMT AUS `skeleton.boneInverses`, NICHT AUS `bone.matrix`
 * ==========================================================================
 * `bone.matrix`/`bone.matrixWorld` sind die AKTUELLE Pose — bei einer
 * laufenden Animation die des gerade angezeigten Bildes. Three.js berechnet
 * `boneInverses` dagegen EINMAL beim Binden (`Skeleton.calculateInverses`)
 * und rührt sie danach nie wieder an: `boneInverses[i].invert()` ist genau
 * die WELT-Bindepose des Knochens `i`, unabhängig davon, welches Bild gerade
 * läuft. Die Gelenk-Hierarchie in `<library_visual_scenes>`
 * (`Colladaknoten`) baut deshalb auf DIESER Matrix auf, nicht auf der
 * aktuellen Pose — sonst stünde die exportierte Ruhelage schief, wenn zufällig
 * mitten in einer Animation exportiert wird.
 */
export class Colladaskin {

    /** Die Weltlage des Knochens `i` IN DER BINDEPOSE (fest, siehe oben). */
    static bindWeltMatrix(skeleton, i) {
        return skeleton.boneInverses[i].clone().invert();
    }

    /** Dieselbe Lage, relativ zum ELTERNknochen (oder zur Welt, wenn Wurzel). */
    static bindLokalMatrix(skeleton, index) {
        const bone = skeleton.bones[index];
        const welt = Colladaskin.bindWeltMatrix(skeleton, index);
        const elternIndex = bone.parent && bone.parent.isBone ? skeleton.bones.indexOf(bone.parent) : -1;
        if (elternIndex < 0) return welt;
        return Colladaskin.bindWeltMatrix(skeleton, elternIndex).invert().multiply(welt);
    }

    /**
     * Eindeutige `sid`s für alle Knochen — von `Colladaknoten` (Gelenkknoten)
     * UND hier (Joints-Liste des Skins) benutzt, damit beide auf denselben
     * Namen zeigen.
     */
    static knochenSids(skeleton) {
        const vergeben = new Set();
        return skeleton.bones.map((bone, i) => {
            let sid = reinerName(bone.name, `bone${i}`);
            let n = 2;
            while (vergeben.has(sid)) sid = `${reinerName(bone.name, `bone${i}`)}_${n++}`;
            vergeben.add(sid);
            return sid;
        });
    }

    /** `<controller>` mit `<skin>` — `geomId` ist die zugehörige `<geometry>`. */
    static bauen(mesh, geomId, ctrlId) {
        const skel = mesh.skeleton;
        const sids = Colladaskin.knochenSids(skel);
        const geo = mesh.geometry;
        const skinIndex = geo.getAttribute('skinIndex');
        const skinWeight = geo.getAttribute('skinWeight');

        const invBindWerte = [];
        for (let i = 0; i < skel.bones.length; i++) invBindWerte.push(...zeilenMajor(skel.boneInverses[i]));

        const gewichte = [];
        const gewichtIndex = new Map();
        const vcount = [];
        const v = [];
        for (let i = 0; i < skinWeight.count; i++) {
            let n = 0;
            for (let k = 0; k < 4; k++) {
                const w = skinWeight.getComponent(i, k);
                if (!w) continue;
                let wi = gewichtIndex.get(w);
                if (wi === undefined) { wi = gewichte.length; gewichte.push(w); gewichtIndex.set(w, wi); }
                v.push(skinIndex.getComponent(i, k), wi);
                n++;
            }
            vcount.push(n);
        }

        const bindShape = zeilenMajor(mesh.bindMatrix);
        const jointsId = `${ctrlId}-joints`;
        const invId = `${ctrlId}-invbind`;
        const wId = `${ctrlId}-weights`;

        const xml = `<controller id="${ctrlId}"><skin source="#${geomId}">`
            + `<bind_shape_matrix>${zahlen(bindShape)}</bind_shape_matrix>`
            + `<source id="${jointsId}"><Name_array id="${jointsId}-array" count="${sids.length}">`
            + `${sids.join(' ')}</Name_array><technique_common><accessor source="#${jointsId}-array" `
            + `count="${sids.length}" stride="1"><param name="JOINT" type="Name"/></accessor></technique_common></source>`
            + `<source id="${invId}"><float_array id="${invId}-array" count="${invBindWerte.length}">`
            + `${zahlen(invBindWerte)}</float_array><technique_common><accessor source="#${invId}-array" `
            + `count="${sids.length}" stride="16"><param name="TRANSFORM" type="float4x4"/></accessor></technique_common></source>`
            + `<source id="${wId}"><float_array id="${wId}-array" count="${gewichte.length}">`
            + `${zahlen(gewichte)}</float_array><technique_common><accessor source="#${wId}-array" `
            + `count="${gewichte.length}" stride="1"><param name="WEIGHT" type="float"/></accessor></technique_common></source>`
            + `<joints><input semantic="JOINT" source="#${jointsId}"/><input semantic="INV_BIND_MATRIX" source="#${invId}"/></joints>`
            + `<vertex_weights count="${vcount.length}"><input semantic="JOINT" source="#${jointsId}" offset="0"/>`
            + `<input semantic="WEIGHT" source="#${wId}" offset="1"/>`
            + `<vcount>${vcount.join(' ')}</vcount><v>${v.join(' ')}</v></vertex_weights>`
            + '</skin></controller>';
        return { xml, sids };
    }
}
