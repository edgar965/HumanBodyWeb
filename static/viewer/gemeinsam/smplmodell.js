import * as THREE from 'three';
import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { Eigenhaut } from './eigenhaut.js';
import { Modell } from './modell.js';

/**
 * SmplModell — ein Referenzkörper von GarmentCode oder ein SMPL-X-Körper,
 * als `Modell` für jede Seite.
 *
 * WARUM (Edgar, 06.09.2026: „keine experimente, baue erstmal das Online tool
 * nach!"): Das Online-Tool drapiert auf `mean_all` mit dessen vorgegebenen
 * Maßen. Für diese Körper (mean_all, mean_female, mean_male, die zwei
 * SMPL-X-Durchschnitte) kennt GarmentCode Maße und Segmentierung — der
 * GarmentCode-Reiter läuft auf ihnen exakt wie das Tool. Das ist die
 * Messlatte für die HumanBody-Figur.
 *
 * SEIT 15.09.2026 SMPL-X (Edgar: „die SMPL Modelle auf SMPL-X umstellen (also
 * inkl. Gesichtsknochen)"): Netz 10.475 Punkte, Skelett 55 Gelenke — Körper,
 * Kiefer (`Jaw`), Augen (`Left_eye`/`Right_eye`), 30 Finger — und die
 * Hautgewichte des Modells; alles vom Server (`core/dienste/smplxrig.py`).
 * GarmentCodes eigene Körper bekommen dasselbe Skelett übertragen.
 *
 * Das Netz kommt vom Server in Metern mit Y oben — so rechnet GarmentCode,
 * und so rechnet Three.js; nichts wird gedreht. Keine Morphs.
 *
 * Dieselben Felder wie `CharacterInstance` und `UmaFigur`, damit Liste,
 * Auswahl, Zählung und Speichern nicht je Quelle unterscheiden müssen.
 *
 * Seit 13.09.2026 in `gemeinsam/`; die Szene erbt als `SmplModell` nur das Speichern.
 */
export class SmplModell extends Modell {

    static QUELLE = 'smpl';
    static ADRESSE = '/api/character/smpl-figur/';
    static FORMADRESSE = '/api/character/smpl-figur/formen/';

    /** Hautfarbe des Referenzkörpers — bewusst grau, kein Mensch. */
    static FARBE = 0x9a9a9a;

    constructor(id, daten) {
        super(id, SmplModell.QUELLE);
        this.koerper = daten.koerper || 'mean_all';
        this.presetName = daten.presetName || `GarmentCode · ${this.koerper}`;
        this.bodyType = 'GarmentCode';
        this.geschlecht = daten.geschlecht || null;
        this.masse = daten.masse || {};
        this.hoehe = 0;
        // Form der Figur: zwei Regler, -100..+100, 0 = Durchschnittskörper
        // des Tools. Das Online-Tool hat diese Regler nicht — gemessen
        // bleibt sein 3D-Körper bei jedem Maß derselbe (siehe smplform.py).
        this.form = {
            groesse: Number(daten.form?.groesse) || 0,
            fuelle: Number(daten.form?.fuelle) || 0,
        };
        this.betas = daten.betas || [];
    }

    async bauen() {
        const geformt = this.form.groesse || this.form.fuelle;
        const daten = geformt
            ? await Serverabruf.senden(SmplModell.FORMADRESSE, {
                geschlecht: this.geschlecht || 'female',
                groesse: this.form.groesse, fuelle: this.form.fuelle,
            })
            : await Serverabruf.json(
                `${SmplModell.ADRESSE}${encodeURIComponent(this.koerper)}/netz/`);
        if (daten.fehler) throw new Error(daten.fehler);
        if (daten.name) this.koerper = daten.name;
        this.betas = daten.betas || this.betas;
        const punkte = daten.punkte || [];
        const dreiecke = daten.dreiecke || [];
        if (!punkte.length || !dreiecke.length) {
            throw new Error(`Referenzkörper ${this.koerper} ohne Netz`);
        }
        this.bodyMesh = SmplModell._netz(punkte, dreiecke);
        this.bodyMesh.name = `garmentcode_koerper_${this.koerper}`;
        // ERST das Skelett, DANN das Netz einhängen: Die Bindung braucht
        // die Knochen in ihrer Ruhelage (`Eigenhaut.einhaengen`).
        this.skelettBauen(daten.skelett);
        this._hautBinden(daten.hautgewichte);
        this.geschlecht = daten.geschlecht || this.geschlecht;
        this.masse = daten.masse || {};
        this.hoehe = daten.hoehe || 0;
        this.bodyType = `GarmentCode · ${this.koerper}`;
        Protokoll.debug('SmplModell',
            `${this.koerper}: ${punkte.length} Punkte, ${dreiecke.length} Dreiecke, ${this.hoehe.toFixed(2)} m`);
        return this;
    }

    /**
     * Das Netz an das eigene Skelett binden — sonst bleibt es beim Abspielen
     * starr, während die Knochen sich bewegen.
     *
     * Die Gewichte stammen aus dem SMPL-X-Modell selbst (`weights`, 10475 × 55,
     * je Punkt die vier größten); für GarmentCodes eigene Körper (23.752
     * Punkte) sind sie über den nächstgelegenen SMPL-X-Punkt übertragen.
     * Ohne Skelett oder ohne Gewichte
     * hängt hier ein gewöhnliches `Mesh` — die Figur ist dann sichtbar, aber
     * nicht animierbar.
     */
    _hautBinden(haut) {
        if (this.skelett && haut) {
            this.bodyMesh = Eigenhaut.binden(this.bodyMesh, this.skelett, haut);
        }
        Eigenhaut.einhaengen(this.group, this.bodyMesh, this.skelett);
        this.isSkinned = !!this.bodyMesh.isSkinnedMesh;
    }

    static _netz(punkte, dreiecke) {
        const lage = new Float32Array(punkte.length * 3);
        for (let i = 0; i < punkte.length; i++) {
            lage[i * 3] = punkte[i][0];
            lage[i * 3 + 1] = punkte[i][1];
            lage[i * 3 + 2] = punkte[i][2];
        }
        const index = new Uint32Array(dreiecke.length * 3);
        for (let i = 0; i < dreiecke.length; i++) {
            index[i * 3] = dreiecke[i][0];
            index[i * 3 + 1] = dreiecke[i][1];
            index[i * 3 + 2] = dreiecke[i][2];
        }
        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        geometrie.setIndex(new THREE.BufferAttribute(index, 1));
        geometrie.computeVertexNormals();
        return new THREE.Mesh(geometrie, new THREE.MeshStandardMaterial({
            color: SmplModell.FARBE, roughness: 0.7, metalness: 0.0,
        }));
    }


}
