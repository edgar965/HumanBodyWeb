import * as THREE from 'three';
import { Bindungsrechner } from './bindungsrechner.js';
import { Oberflaechenbindung } from './oberflaechenbindung.js';
import { Protokoll } from './protokoll.js';

/**
 * Humanbodybindung — die Oberflächenbindung für HumanBody-Figuren
 * (Auftrag Edgar, 24.09.2026: „Implementiere das auch für HumanBody").
 *
 * WARUM IM BROWSER: Bei Genesis 9 liefert der Server die Zuordnung mit dem
 * Kleidungsnetz. HumanBody-Kleidung kommt auf sechs Wegen an die Figur
 * (Assets `gar_`, Kleider `kld_`, MakeHuman `mh_`, GarmentCode `gc_`, Daz
 * `daz_`, Vorlagen `tpl_`), keiner geht über eine gemeinsame Stelle, und der
 * Körper wird erst beim Animieren gehäutet (`haeuten` ersetzt das Netz). Statt
 * sechs Wege anzufassen, sieht `takt` je Bild nach, welches GEHÄUTETE Stück am
 * Skelett des Körpers noch keine Bindung zu DIESEM Körpernetz hat, und rechnet
 * sie (`Bindungsrechner`, einmal je Stück und Körper, ~50 ms).
 *
 * ZWEI UNTERSCHIEDE ZU GENESIS 9, beide in der Bindung vermerkt:
 *   - `vorzeichen`: HumanBodys `normal`-Attribut zeigt nach INNEN; der Shader
 *     dreht die Normale aus der Körperlage damit um.
 *   - Die Stücke sind teils mit ihrer eigenen Matrix gebunden (`bind(skelett,
 *     netz.matrix)`). Die Ruhelage des Stoffs wird deshalb über beide
 *     `bindMatrix` in den Raum des Körpers gebracht; je Bild rechnet der Shader
 *     über `uZuKoerper`/`uVonKoerper` zwischen den lokalen Räumen um.
 *
 * `punkte` (Punktzahl des Körpers) statt `stufen`: Die Indizes gelten nur für
 * das Körpernetz, gegen das gerechnet wurde; ein anderes (Körpertyp gewechselt)
 * schaltet die Bindung ab, bis `takt` neu gerechnet hat.
 */
export class Humanbodybindung {

    static QUELLE = 'modell';
    /** Körpergeometrie → Bindungsrechner. */
    static _rechner = new WeakMap();
    /** Stoffnetz → Körpergeometrie, gegen die gerechnet wurde (auch ohne Ergebnis). Am NETZ,
     *  nicht an der Geometrie: `nachbinden` baut ein neues Netz um dieselbe Geometrie, und
     *  das braucht seinen eigenen Eingriff (`onBeforeRender`). */
    static _gerechnet = new WeakMap();

    static takt(figuren) {
        for (const inst of figuren) {
            if (inst?.quelle !== Humanbodybindung.QUELLE && inst?.quelle !== 'genesis9') continue;
            const koerper = inst.bodyMesh;
            if (!koerper?.isSkinnedMesh || !koerper.skeleton) continue;
            for (const [schluessel, netz] of Object.entries(inst.clothMeshes || {})) {
                if (!Humanbodybindung.zustaendig(inst, schluessel)) continue;
                if (!netz?.isSkinnedMesh || netz.skeleton !== koerper.skeleton) continue;
                if (Humanbodybindung._gerechnet.get(netz) === koerper.geometry) continue;
                Humanbodybindung.binden(inst, koerper, netz);
            }
        }
    }

    /**
     * Welche Stücke hier gebunden werden: auf HumanBody alle; auf Genesis 9 nur
     * GarmentCode (`gc_`, 24.09.2026, Edgar: „ob wir von dem Genesis Fitting
     * lernen könnten bei Garment Code") — Daz-Stücke bringen ihre Bindung
     * vom Server mit (`G9oberflaechenbindung`), GarmentCode-Stücke hatten keine.
     */
    static zustaendig(inst, schluessel) {
        if (inst?.quelle === Humanbodybindung.QUELLE) return true;
        return inst?.quelle === 'genesis9' && String(schluessel).startsWith('gc_');
    }

    static binden(inst, koerper, netz) {
        const t0 = performance.now();
        Humanbodybindung._gerechnet.set(netz, koerper.geometry);
        try {
            const rechner = Humanbodybindung._rechnerFuer(koerper.geometry);
            if (!rechner) return false;
            const stoff = Humanbodybindung._stoffImKoerperraum(koerper, netz);
            const b = rechner.fuer(stoff);
            if (!Oberflaechenbindung.anlegenAusFeldern(netz, b, {
                stufen: inst.stufen || 0, punkte: rechner.punkte.length / 3, vorzeichen: rechner.vorzeichen,
            })) return false;
            Oberflaechenbindung.verdrahten(inst, netz);
            Protokoll.debug('Humanbodybindung', `${netz.name}: ${netz.geometry.userData.bindung.gebunden} `
                + `von ${stoff.length / 3} Punkten gebunden, ${(performance.now() - t0).toFixed(0)} ms`);
            return true;
        } catch (fehler) {
            Protokoll.warnung('Humanbodybindung', `${netz.name}: Bindung nicht gerechnet`, fehler);
            return false;
        }
    }

    static _rechnerFuer(geo) {
        let r = Humanbodybindung._rechner.get(geo);
        if (r) return r;
        const lage = geo.attributes.position, normale = geo.attributes.normal;
        const feld = Humanbodybindung.vollerIndex(geo);
        if (!lage || !normale || !feld?.length) return null;
        const punkte = Float32Array.from(lage.array);
        const roh = Float32Array.from(normale.array);
        const vorzeichen = Bindungsrechner.vorzeichen(punkte, roh);
        if (vorzeichen < 0) for (let i = 0; i < roh.length; i++) roh[i] = -roh[i];
        r = new Bindungsrechner(punkte, feld, roh);
        r.vorzeichen = vorzeichen;
        Humanbodybindung._rechner.set(geo, r);
        return r;
    }

    /**
     * Der unmaskierte Index des Körpers als Zahlenfeld. Die Hautverdeckung legt
     * ihn ab, bevor sie maskiert — auf HumanBody als Index, auf Genesis 9 als
     * `{index, gruppen}` (24.09.2026: dort las die Bindung 0 Dreiecke und band
     * 0 von 9.966 Punkten der Harem Pants).
     */
    static vollerIndex(geo) {
        const voll = geo?.userData?.indexVoll;
        const index = voll?.index ?? voll ?? geo?.index;
        return index?.array || (ArrayBuffer.isView(index) || Array.isArray(index) ? index : null);
    }

    /** Stoff in Ruhe (Bindpose) im Raum des Körpers: inv(B_körper) · B_stoff · p. */
    static _stoffImKoerperraum(koerper, netz) {
        const m = new THREE.Matrix4().copy(koerper.bindMatrix).invert().multiply(netz.bindMatrix);
        const a = netz.geometry.attributes.position;
        const aus = new Float32Array(3 * a.count);
        const v = new THREE.Vector3();
        for (let i = 0; i < a.count; i++) {
            v.fromBufferAttribute(a, i).applyMatrix4(m);
            aus[3 * i] = v.x; aus[3 * i + 1] = v.y; aus[3 * i + 2] = v.z;
        }
        return aus;
    }

    /** Für Proben: je Stück, ob gebunden und wie viele Punkte. */
    static stand(inst) {
        const aus = {};
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            aus[schluessel] = { gehaeutet: Boolean(netz?.isSkinnedMesh),
                                bindung: netz?.geometry?.userData?.bindung || null };
        }
        return aus;
    }
}

window.__humanbodybindung = Humanbodybindung;
