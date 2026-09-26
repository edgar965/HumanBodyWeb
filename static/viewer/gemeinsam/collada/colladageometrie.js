import { xmlEsc, zahlen, reinerName } from './colladaxml.js';

/**
 * Colladageometrie — EIN `<geometry>`-Block je Netz.
 *
 * Position, Normale und UV liegen in Three.js' `BufferGeometry` bereits
 * PARALLEL (ein Eintrag je Punkt, `geometry.index` zeigt für alle drei
 * gleichermaßen) — deshalb genügt in den `<triangles>` EIN gemeinsamer
 * Index für POSITION/NORMAL/TEXCOORD (`offset="0"` überall). Eine eigene
 * Neuindizierung je Attribut, wie sie andere Collada-Schreiber brauchen, ist
 * hier nicht nötig.
 *
 * MEHRERE WERKSTOFFE (`geometry.groups`): anders als OBJ (nur ein `usemtl`
 * je Teil) kennt Collada mehrere `<triangles>`-Blöcke mit je eigenem
 * `material`-Symbol — eine Materialgruppe geht hier NICHT verloren.
 */
export class Colladageometrie {

    /** @returns {xml, geomId, symbole: [{symbol, materialIndex}]} */
    static bauen(mesh, geomId) {
        const geo = mesh.geometry;
        const pos = geo.getAttribute('position');
        const normal = geo.getAttribute('normal');
        const uv = geo.getAttribute('uv');
        const index = geo.getIndex();

        let xml = `<geometry id="${geomId}" name="${xmlEsc(mesh.name || geomId)}"><mesh>`;
        xml += Colladageometrie._quelle(geomId, 'positions', pos, 3, ['X', 'Y', 'Z']);
        if (normal) xml += Colladageometrie._quelle(geomId, 'normals', normal, 3, ['X', 'Y', 'Z']);
        if (uv) xml += Colladageometrie._quelle(geomId, 'uv', uv, 2, ['S', 'T']);
        xml += `<vertices id="${geomId}-vertices"><input semantic="POSITION" source="#${geomId}-positions"/></vertices>`;

        const dreiecke = index ? index.count / 3 : pos.count / 3;
        const gruppen = geo.groups && geo.groups.length ? geo.groups : [{ start: 0, count: dreiecke * 3, materialIndex: 0 }];
        const symbole = [];
        for (const gruppe of gruppen) {
            const symbol = `sym${gruppe.materialIndex}`;
            symbole.push({ symbol, materialIndex: gruppe.materialIndex });
            xml += Colladageometrie._dreiecke(geomId, symbol, index, gruppe, !!normal, !!uv);
        }
        xml += '</mesh></geometry>';
        return { xml, geomId, symbole };
    }

    static _quelle(geomId, art, attribut, komponenten, achsen) {
        const werte = [];
        for (let i = 0; i < attribut.count; i++) {
            for (let k = 0; k < komponenten; k++) werte.push(attribut.getComponent(i, k));
        }
        const arrId = `${geomId}-${art}-array`;
        const params = achsen.map(a => `<param name="${a}" type="float"/>`).join('');
        return `<source id="${geomId}-${art}">`
            + `<float_array id="${arrId}" count="${werte.length}">${zahlen(werte)}</float_array>`
            + `<technique_common><accessor source="#${arrId}" count="${attribut.count}" stride="${komponenten}">`
            + `${params}</accessor></technique_common></source>`;
    }

    static _dreiecke(geomId, symbol, index, gruppe, hatNormale, hatUv) {
        const eingaenge = [`<input semantic="VERTEX" source="#${geomId}-vertices" offset="0"/>`];
        if (hatNormale) eingaenge.push(`<input semantic="NORMAL" source="#${geomId}-normals" offset="0"/>`);
        if (hatUv) eingaenge.push(`<input semantic="TEXCOORD" source="#${geomId}-uv" offset="0" set="0"/>`);
        const p = [];
        const anzahl = gruppe.count;
        for (let i = gruppe.start; i < gruppe.start + anzahl; i++) {
            p.push(index ? index.getX(i) : i);
        }
        return `<triangles material="${symbol}" count="${anzahl / 3}">${eingaenge.join('')}`
            + `<p>${p.join(' ')}</p></triangles>`;
    }

    static reinerId(name, ersatz) {
        return reinerName(name, ersatz);
    }
}
