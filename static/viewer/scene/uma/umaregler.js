import * as THREE from 'three';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/**
 * Umaregler — UMAs Form-Regler auf die Knochen der geladenen GLB rechnen.
 *
 * WARUM (05.09.2026): UMA formt über Knochen (skalieren, verschieben, drehen,
 * Posen). Die Definitionen kommen fertig übersetzt vom Server
 * (`/api/character/uma-regler/`, `humanbody_core.uma.Formregler`); hier steht
 * nur die Rechnung aus `DNAEffect_*.cs` und `UMASkeleton.Morph`.
 *
 * RELATIV ZUR EXPORTIERTEN RUHELAGE: Die GLB enthält das Skelett, wie Unity
 * es mit den Reglerwerten des Exports gebaut hat (Vorgabe: alles 0,5). Ein
 * Regler wirkt deshalb als Unterschied zu seiner Vorgabe — bei 0,5 ändert er
 * nichts, die Figur sieht aus wie in Unity. Vor jeder Anwendung werden die
 * betroffenen Knochen auf die Ruhelage aus der GLB zurückgesetzt, sonst
 * summierte sich jeder Reglerzug auf den vorigen.
 */
export class Umaregler {

    static ADRESSE = '/api/character/uma-regler/';
    static _laufend = new Map();

    /** Die Regler zur Figur — je Geschlecht einmal vom Server geholt. */
    static async laden(datei) {
        const schluessel = datei || '';
        if (!Umaregler._laufend.has(schluessel)) {
            const adresse = Umaregler.ADRESSE + (datei ? `?figur=${encodeURIComponent(datei)}` : '');
            Umaregler._laufend.set(schluessel,
                Serverabruf.json(adresse).then(daten => new Umaregler(daten)));
        }
        return Umaregler._laufend.get(schluessel);
    }

    constructor(daten) {
        this.geschlecht = daten.geschlecht;
        this.gruppen = daten.gruppen || [];
        this.anzahl = daten.anzahl || 0;
        this.uebergangen = daten.uebergangen || [];
        this._fehlend = null;
    }

    alle() {
        return this.gruppen.flatMap(gruppe => gruppe.regler);
    }

    vorgaben() {
        const raus = {};
        for (const regler of this.alle()) raus[regler.name] = regler.vorgabe;
        return raus;
    }

    /**
     * Alle Regler anwenden. `werte`: {name: 0..1}; `knochen`: {name: THREE.Bone};
     * `ruhelage`: Map name → {position, quaternion, scale} aus der GLB.
     */
    anwenden(werte, knochen, ruhelage) {
        const fehlend = new Set();
        for (const [name, lage] of ruhelage) {
            const bone = knochen[name];
            if (!bone) continue;
            bone.position.copy(lage.position);
            bone.quaternion.copy(lage.quaternion);
            bone.scale.copy(lage.scale);
        }
        // Erst die Grundposen, dann alles andere in Dateireihenfolge — wie
        // `DNAInstanceCollection` in UMA.
        const alle = this.alle();
        const reihen = [
            alle.flatMap(r => r.wirkungen.filter(w => w.art === 'pose' && w.grundpose).map(w => [r, w])),
            alle.flatMap(r => r.wirkungen.filter(w => !(w.art === 'pose' && w.grundpose)).map(w => [r, w])),
        ];
        for (const reihe of reihen) {
            for (const [regler, wirkung] of reihe) {
                const wert = werte[regler.name] ?? regler.vorgabe;
                const betrag = Umaregler.abbilden(wirkung, wert) - Umaregler.abbilden(wirkung, regler.vorgabe);
                if (Math.abs(betrag) < 1e-9) continue;
                Umaregler._wirken(wirkung, betrag, knochen, fehlend);
            }
        }
        if (fehlend.size && !this._fehlend) {
            this._fehlend = [...fehlend];
            Protokoll.warnung('Umaregler', 'Knochen aus den Reglern fehlen in der GLB:', this._fehlend);
        }
    }

    /** `minMapping + kurve(wert) * (maxMapping - minMapping)` — `DNAEffect.GetMappedValue`. */
    static abbilden(wirkung, wert) {
        return wirkung.von + Umaregler.kurve(wirkung.kurve, wert) * (wirkung.bis - wirkung.von);
    }

    /** Unity-AnimationCurve: kubisch-hermitesch mit Tangenten, außen geklemmt. */
    static kurve(stuetzen, t) {
        if (!stuetzen || stuetzen.length === 0) return t;
        if (t <= stuetzen[0][0]) return stuetzen[0][1];
        const letzte = stuetzen[stuetzen.length - 1];
        if (t >= letzte[0]) return letzte[1];
        let i = 0;
        while (i < stuetzen.length - 2 && t > stuetzen[i + 1][0]) i++;
        const [t0, v0, , aus0] = stuetzen[i];
        const [t1, v1, ein1] = stuetzen[i + 1];
        const dt = t1 - t0;
        if (dt <= 0) return v1;
        const s = (t - t0) / dt;
        const s2 = s * s, s3 = s2 * s;
        return (2 * s3 - 3 * s2 + 1) * v0 + (s3 - 2 * s2 + s) * dt * aus0
            + (-2 * s3 + 3 * s2) * v1 + (s3 - s2) * dt * ein1;
    }

    static _wirken(wirkung, betrag, knochen, fehlend) {
        if (wirkung.art === 'pose') {
            for (const pose of wirkung.posen) {
                const bone = knochen[pose.knochen];
                if (!bone) { fehlend.add(pose.knochen); continue; }
                Umaregler._morph(bone, pose, betrag);
            }
            return;
        }
        const bone = knochen[wirkung.knochen];
        if (!bone) { fehlend.add(wirkung.knochen); return; }
        if (wirkung.art === 'skalieren') {
            const f = wirkung.faktor;
            bone.scale.set(bone.scale.x * (1 + f[0] * betrag), bone.scale.y * (1 + f[1] * betrag),
                           bone.scale.z * (1 + f[2] * betrag));
        } else if (wirkung.art === 'verschieben') {
            const v = wirkung.versatz;
            bone.position.x += v[0] * betrag;
            bone.position.y += v[1] * betrag;
            bone.position.z += v[2] * betrag;
        } else if (wirkung.art === 'drehen') {
            const achse = new THREE.Vector3().fromArray(wirkung.achse).normalize();
            const delta = new THREE.Quaternion().setFromAxisAngle(
                achse, THREE.MathUtils.degToRad(wirkung.winkel * betrag));
            bone.quaternion.multiply(delta);
        }
    }

    /** `UMASkeleton.Morph(position, scale, rotation, weight)`. */
    static _morph(bone, pose, gewicht) {
        bone.position.x += pose.position[0] * gewicht;
        bone.position.y += pose.position[1] * gewicht;
        bone.position.z += pose.position[2] * gewicht;
        const voll = bone.quaternion.clone().multiply(new THREE.Quaternion().fromArray(pose.drehung));
        bone.quaternion.slerp(voll, gewicht);
        const ziel = new THREE.Vector3(bone.scale.x * pose.skala[0], bone.scale.y * pose.skala[1],
                                       bone.scale.z * pose.skala[2]);
        bone.scale.lerp(ziel, gewicht);
    }
}
