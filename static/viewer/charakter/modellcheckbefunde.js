import * as THREE from 'three';
import { Gezeichneterpunkt } from '../gemeinsam/gezeichneterpunkt.js';

/**
 * Modellcheckbefunde — die Befunde des Modell Checks als Liste für die Tabelle (02.11.2026 spätabends, Edgar: „Du hast viele Befunde, aber ich sehe die nicht im
 * Bild. mache eine Tabelle mit allen Befunden und wenn ich auf einen Eintrag gehe, dann markiere mir diesen Eintrag rot auf dem View“).
 * Aus dem Ergebnis von `Modellpruefung.pruefen(…, {marken: true})`: Punktmarken (Haut, wo Stoff sein muss; Fuß im Schuh; Stoff auf der Hand; Finger; Körper unter der
 * Kleidung) je Netz in zusammenhängende Stellen geteilt (Rasterzellen von STELLE_M, Nachbarzellen gehören zusammen), Säume je Saum, Gelenke je Knochen, eine
 * durchgefallene Frisur je Netz. Auch Stellen unter der Grenze stehen in der Liste (`fehler: false`) — durchgefallen ist nur, was die Prüfung rot zählt.
 *   Modellcheckbefunde.sammeln(inst, p, gebacken) → [{klasse, pruefung, fehler, stueck, ort, wert, zahl, punkte: Map Netz → [Punkt] | null (ganzes Netz), knochen}]
 */
export class Modellcheckbefunde {

    static STELLE_M = 0.015;
    static STELLEN_MAX = 40;                // je Klasse und Netz; der Rest steht als eine Zeile
    static ORTE = [[/toe|metatarsal/, 'Zehen'], [/foot/, 'Fuß'], [/shin/, 'Unterschenkel'], [/thigh/, 'Oberschenkel'],
        [/thumb|index|mid|ring|pinky|carpal/, 'Finger'], [/hand/, 'Hand'], [/forearm/, 'Unterarm'], [/upperarm/, 'Oberarm'], [/shoulder|collar|clavicle/, 'Schulter'],
        [/pectoral|breast/, 'Brust'], [/neck/, 'Hals'], [/head|jaw|eye|ear|nose|lip|tongue|brow|cheek|teeth/, 'Kopf'], [/pelvis|hip|glute|genital/, 'Becken'],
        [/abdomen|spine1|spine2/, 'Bauch'], [/chest|spine/, 'Rumpf']];
    static RUMPF = new Set(['Brust', 'Becken', 'Bauch', 'Rumpf']);

    /** Kleidung im Sinn des Schalters „Kleider“: Katalogstücke der Art „kleidung“ (ohne das Anatomie-Stück), Eigenkleider, Eigenröcke. */
    static istKleid(o) {
        return (o.userData?.art === 'kleidung' && !/daz_anatomie/.test(o.name || '')) || Boolean(o.userData?.eigenkleid || o.userData?.eigenGebacken)
            || /^eigenrock_/.test(o.name || '');
    }

    static kurz(name) { return String(name || '').replace(/^genesis9_kleid_/, '').replace(/_\d+$/, ''); }

    /** Weltmatrix eines Netzes; gebackene Eigenkleider hängen nicht in der Szene, sie liegen im Raum der Figurgruppe (`Eigenkleidbacken`). */
    static welt(netz, inst) { return netz.parent ? netz.matrixWorld : inst.group.matrixWorld; }

    /** Weltlagen der Punkte `liste` von `netz`, wie gezeichnet (`Gezeichneterpunkt.lage`) → Float32Array. */
    static lagen(netz, liste, inst) {
        const aus = new Float32Array(3 * liste.length), v = new THREE.Vector3(), welt = Modellcheckbefunde.welt(netz, inst);
        liste.forEach((i, j) => { Gezeichneterpunkt.lage(netz, i, v).applyMatrix4(welt); aus[3 * j] = v.x; aus[3 * j + 1] = v.y; aus[3 * j + 2] = v.z; });
        return aus;
    }

    /** Raumkiste eines Befunds (für die Kamera der 3D-Ansicht). */
    static kiste(inst, b) {
        const k = new THREE.Box3(), v = new THREE.Vector3();
        for (const [netz, liste] of b.punkte) {
            if (!liste) { k.union(new THREE.Box3().setFromObject(netz, true)); continue; }
            const l = Modellcheckbefunde.lagen(netz, liste, inst);
            for (let j = 0; j < l.length; j += 3) k.expandByPoint(v.set(l[j], l[j + 1], l[j + 2]));
        }
        for (const kn of b.knochen || []) k.expandByPoint(kn.getWorldPosition(v)).expandByScalar(0.03);
        return k;
    }

    static sammeln(inst, p, gebacken = []) {
        const M = Modellcheckbefunde, aus = [], koerper = inst.bodyMesh, titel = Object.fromEntries(p.pruefungen.map((x) => [x.schluessel, x.titel]));
        const durch = new Set(p.pruefungen.filter((x) => x.ok === false).map((x) => x.schluessel));
        for (const klasse of ['deckung', 'schuhe', 'handstoff', 'finger']) {
            for (const [netz, a] of p.marken?.[klasse] || []) {
                const liste = [];
                for (let i = 0; i < a.length; i++) if (a[i]) liste.push(i);
                M._stellen(aus, inst, netz, liste, { klasse, pruefung: titel[klasse], fehler: durch.has(klasse), stueck: netz === koerper ? 'Körper' : M.kurz(netz.name) });
            }
        }
        for (const s of p.durchstoss?.stuecke || []) {
            M._stellen(aus, inst, koerper, s.punkte, { klasse: 'durchstoss', pruefung: titel.durchstoss, fehler: p.durchstoss.zu.includes(s), stueck: M.kurz(s.name) },
                `Stück bis ${s.tief_mm} mm außen`);
        }
        const netze = [...gebacken];
        inst.group.traverse((o) => { if (o.isMesh && !netze.includes(o)) netze.push(o); });
        for (const s of p.saeume?.saeume || []) {
            const o = netze.find((x) => (x.name || x.uuid) === s.name);
            if (!o) continue;
            aus.push({ klasse: 'saeume', pruefung: titel.saeume, fehler: p.saeume.zu.includes(s), stueck: M.kurz(s.name), ort: M.ort(inst, o, s.punkte),
                wert: `${s.laenge_mm} mm lang · Zacken ${s.zacken_mm} mm · Überlänge ${Math.round(100 * s.ueberlaenge)} %`, zahl: s.punkte.length,
                punkte: new Map([[o, s.punkte]]), knochen: [] });
        }
        if (durch.has('haare')) {
            const text = p.pruefungen.find((x) => x.schluessel === 'haare')?.text || '';
            for (const o of p.marken?.haare || []) aus.push({ klasse: 'haare', pruefung: titel.haare, fehler: true, stueck: M.kurz(o.name), ort: 'Kopf',
                wert: text.replace(/^[^:]*:\s*/, ''), zahl: o.geometry.attributes.position.count, punkte: new Map([[o, null]]), knochen: [] });
        }
        const v = new THREE.Vector3();
        for (const g of p.gelenke?.aussen || []) {
            const k = koerper.skeleton?.bones.find((b) => b.name === g.name);
            aus.push({ klasse: 'gelenke', pruefung: titel.gelenke, fehler: true, stueck: 'Skelett', ort: k ? `${M.ortName(inst, k, k.getWorldPosition(v))} (${g.name})` : g.name,
                wert: `${g.abstand_mm} mm außen`, zahl: 1, punkte: new Map(), knochen: k ? [k] : [] });
        }
        const rang = Object.fromEntries(p.pruefungen.map((x, i) => [x.schluessel, i]));
        return aus.sort((a, b) => (b.fehler - a.fehler) || (rang[a.klasse] - rang[b.klasse]) || (b.zahl - a.zahl));
    }

    /** Punkte eines Netzes als Stellen in die Liste (die größten STELLEN_MAX einzeln, der Rest als eine Zeile). */
    static _stellen(aus, inst, netz, liste, kopf, zusatz = '') {
        if (!liste.length) return;
        const M = Modellcheckbefunde, stellen = M.stellen(inst, netz, liste);
        const zeile = (punkte, ort, groesse) => aus.push({ ...kopf, ort, zahl: punkte.length, punkte: new Map([[netz, punkte]]), knochen: [],
            wert: `${punkte.length} Punkte · ${(100 * groesse).toFixed(1)} cm${zusatz ? ` · ${zusatz}` : ''}` });
        for (const s of stellen.slice(0, M.STELLEN_MAX)) zeile(s.punkte, M.ort(inst, netz, s.punkte, s.mitte), s.groesse);
        const rest = stellen.slice(M.STELLEN_MAX);
        if (rest.length) zeile(rest.flatMap((s) => s.punkte), `${rest.length} weitere Stellen`, Math.max(...rest.map((s) => s.groesse)));
    }

    /** Zusammenhängende Stellen: Punkte in Rasterzellen, benachbarte belegte Zellen gehören zusammen → [{punkte, mitte, groesse}], größte zuerst. */
    static stellen(inst, netz, liste) {
        const r = Modellcheckbefunde.STELLE_M, l = Modellcheckbefunde.lagen(netz, liste, inst), zellen = new Map();
        const schl = (x, y, z) => `${x},${y},${z}`;
        liste.forEach((i, j) => {
            const k = schl(Math.floor(l[3 * j] / r), Math.floor(l[3 * j + 1] / r), Math.floor(l[3 * j + 2] / r));
            if (!zellen.has(k)) zellen.set(k, []);
            zellen.get(k).push(j);
        });
        const namen = [...zellen.keys()], nummer = new Map(namen.map((k, z) => [k, z])), eltern = namen.map((_, z) => z);
        const finde = (x) => { while (eltern[x] !== x) { eltern[x] = eltern[eltern[x]]; x = eltern[x]; } return x; };
        namen.forEach((k, z) => {
            const [x, y, w] = k.split(',').map(Number);
            for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
                const n = nummer.get(schl(x + a, y + b, w + c));
                if (n !== undefined) eltern[finde(n)] = finde(z);
            }
        });
        const gruppen = new Map();
        namen.forEach((k, z) => { const w = finde(z); if (!gruppen.has(w)) gruppen.set(w, []); gruppen.get(w).push(...zellen.get(k)); });
        return [...gruppen.values()].map((js) => {
            const box = new THREE.Box3(), v = new THREE.Vector3();
            for (const j of js) box.expandByPoint(v.set(l[3 * j], l[3 * j + 1], l[3 * j + 2]));
            return { punkte: js.map((j) => liste[j]), mitte: box.getCenter(new THREE.Vector3()), groesse: box.getSize(v).length() };
        }).sort((a, b) => b.punkte.length - a.punkte.length);
    }

    /** Ort einer Stelle: der Knochen mit dem meisten Gewicht an ihren Punkten (ohne Häutung der nächste Knochen des Körpers). */
    static ort(inst, netz, liste, mitte = null) {
        const M = Modellcheckbefunde, g = netz.geometry, si = g.attributes.skinIndex, sw = g.attributes.skinWeight;
        mitte ??= new THREE.Box3().setFromArray(M.lagen(netz, liste, inst)).getCenter(new THREE.Vector3());
        let knochen = null;
        if (netz.isSkinnedMesh && si && sw) {
            const zahl = new Map(), schritt = Math.max(1, Math.floor(liste.length / 500));
            for (let j = 0; j < liste.length; j += schritt) {
                const i = liste[j];
                let best = 0;
                for (let s = 1; s < si.itemSize; s++) if (sw.getComponent(i, s) > sw.getComponent(i, best)) best = s;
                const k = si.getComponent(i, best);
                zahl.set(k, (zahl.get(k) || 0) + 1);
            }
            const k = [...zahl.entries()].sort((a, b) => b[1] - a[1])[0]?.[0];
            knochen = netz.skeleton?.bones[k] || null;
        }
        if (!knochen) {
            const v = new THREE.Vector3();
            let best = Infinity;
            for (const b of inst.bodyMesh.skeleton?.bones || []) { const d = b.getWorldPosition(v).distanceToSquared(mitte); if (d < best) { best = d; knochen = b; } }
        }
        return knochen ? M.ortName(inst, knochen, mitte) : '—';
    }

    /** „Oberschenkel links“, „Rumpf hinten“ — Seite aus dem Knochennamen (Daz: l_ = links der Figur), vorne/hinten am Rumpf aus der Blickrichtung der Figur. */
    static ortName(inst, knochen, mitte) {
        const M = Modellcheckbefunde, name = knochen.name.toLowerCase(), roh = name.replace(/^[lr]_/, '');
        const teil = M.ORTE.find(([re]) => re.test(roh))?.[1] || knochen.name;
        const seite = name.startsWith('l_') ? ' links' : (name.startsWith('r_') ? ' rechts' : '');
        if (!M.RUMPF.has(teil)) return teil + seite;
        const vorn = new THREE.Vector3(0, 0, 1).applyQuaternion(inst.group.getWorldQuaternion(new THREE.Quaternion()));
        return `${teil}${seite} ${mitte.clone().sub(knochen.getWorldPosition(new THREE.Vector3())).dot(vorn) >= 0 ? 'vorne' : 'hinten'}`;
    }
}
