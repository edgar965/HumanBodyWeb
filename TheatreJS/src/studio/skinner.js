import * as THREE from 'three';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js';
import { fetchRetargetedClipFromText } from '../retarget_hybrid.js';
import { Skelettanzeige } from '../../../static/viewer/gemeinsam/skelettanzeige.js';

/**
 * Skinner — Skelett, Hautgewichte und die Umwandlung zu SkinnedMesh.
 *
 * Herausgeloest aus main.js (Umbau 16.08.2026). Die Datei hatte 2.641 Zeilen,
 * davon 2.545 in EINEM DOMContentLoaded-Handler: 181 Funktionen, die sich
 * ueber vierzig Closure-Variablen verstaendigten. Wer dort etwas aendern
 * wollte, musste die ganze Datei im Kopf haben.
 *
 * Dieser Teil laesst sich klar abgrenzen — er dreht sich um genau fuenf Werte
 * (Skelettdaten, Gewichte, gebautes Skelett, Ladeversprechen, Rig-Anzeige), und
 * die sind jetzt Felder einer Klasse statt Variablen in einem 2.500-Zeilen-Block.
 *
 * Nebenbei behoben: Der SkeletonHelper wurde an ZWEI Stellen mit denselben
 * fuenf Materialzeilen aufgebaut (beim Umwandeln und beim Einschalten der
 * Rig-Anzeige). Jetzt gibt es dafuer eine Methode.
 */
export class Skinner {

    /** Kopfknochen in der Reihenfolge, in der gesucht wird. */
    static KOPFKNOCHEN = ['DEF-spine.006', 'DEF-spine.005', 'DEF-head'];
    /** Hoechstens so viele Knochen wirken auf einen Vertex (Three.js-Grenze). */
    static EINFLUESSE = 4;
    /** Koerperhoehe, wenn sie sich nicht messen laesst. */
    static HOEHE_ERSATZ = 1.68;

    /**
     * @param {THREE.Scene} scene
     * @param {Array} charaktere  dieselbe Liste, die main.js fuehrt — beim
     *        Nachladen des Skeletts werden daraus die noch nicht umgewandelten
     *        Figuren nachgezogen.
     */
    constructor(scene, charaktere) {
        this.scene = scene;
        this.charaktere = charaktere;
        this.skelettdaten = null;
        this.gewichte = null;
        this.skelett = null;         // { skeleton, rootBone, bones, boneByName }
        this.anzeige = null;         // THREE.SkeletonHelper
        this.rigSichtbar = false;
        this._laden = null;          // laufendes Versprechen
    }

    get bereit() {
        return Boolean(this.skelettdaten && this.gewichte);
    }

    /** Skelett und Gewichte holen — je Sitzung nur einmal. */
    async laden() {
        if (this._laden) return this._laden;
        this._laden = (async () => {
            try {
                const [skelett, gewichte] = await Promise.all([
                    fetch('/api/character/rigify-skeleton/'),
                    fetch('/api/character/skin-weights/'),
                ]);
                if (skelett.ok) this.skelettdaten = await skelett.json();
                if (gewichte.ok) this.gewichte = await gewichte.json();
                console.log('✓ Skelett und Gewichte geladen:',
                    this.skelettdaten?.bones?.length || 0, 'Knochen');
                if (this.bereit) {
                    this.skelett = buildRigifySkeleton(this.skelettdaten, this.gewichte);
                    console.log('✓ Skelett gebaut:', this.skelett.bones.length, 'Knochen');
                    // Fuer die Browser-Konsole und die UI-Tests.
                    window.rigifySkeletonData = this.skelettdaten;
                    window.rigifySkeleton = this.skelett;
                }
                // Figuren, die vor dem Skelett geladen wurden, nachziehen.
                for (const figur of this.charaktere) {
                    if (!figur.userData.isSkinnedMesh) this.autoUmwandeln(figur);
                }
            } catch (fehler) {
                console.warn('Skelett/Gewichte nicht ladbar:', fehler);
            }
        })();
        return this._laden;
    }

    /** Umwandeln, sobald die Daten da sind — sonst nichts tun. */
    autoUmwandeln(figur) {
        if (!this.bereit || figur.userData.isSkinnedMesh) return;
        // Kurze Verzoegerung: Die Figur muss vollstaendig in der Szene haengen.
        setTimeout(() => {
            try {
                this.umwandeln(figur);
                console.log('✓ zu SkinnedMesh umgewandelt:', figur.userData.presetName);
            } catch (fehler) {
                console.warn('Umwandeln fehlgeschlagen:', fehler);
            }
        }, 100);
    }

    /**
     * Figur in ein SkinnedMesh umwandeln und ans Skelett binden.
     * Gibt das SkinnedMesh zurueck oder null.
     */
    umwandeln(figur) {
        if (!this.bereit) {
            console.warn('Umwandeln nicht moeglich: Skelett/Gewichte fehlen');
            return null;
        }
        if (figur.userData.isSkinnedMesh) return figur.userData.skinnedMesh;

        const koerper = figur.children.find(
            k => k.isMesh && !k.userData.isHair && !k.userData.isGarment);
        if (!koerper) {
            console.warn('Kein Koerpernetz in der Figur gefunden');
            return null;
        }

        // Geometrie klonen: Die urspruengliche haelt WebGL-Zustand aus dem
        // Rendern OHNE Skinning, was nach dem Binden zu Fehlern fuehrt.
        const geo = koerper.geometry.clone();
        this._gewichtefelder(geo);

        // Skelett IMMER neu bauen: Ein bereits animiertes Skelett bringt
        // veraltete Weltmatrizen und boneInverses mit, die nicht zum neuen
        // Bindezustand passen.
        this.skelett = buildRigifySkeleton(this.skelettdaten, this.gewichte);

        const netz = new THREE.SkinnedMesh(geo, koerper.material);
        netz.position.copy(koerper.position);
        netz.rotation.copy(koerper.rotation);
        netz.scale.copy(koerper.scale);
        netz.castShadow = true;
        netz.receiveShadow = true;
        netz.add(this.skelett.rootBone);
        netz.bind(this.skelett.skeleton);

        figur.remove(koerper);
        figur.add(netz);
        figur.userData.isSkinnedMesh = true;
        figur.userData.skinnedMesh = netz;
        figur.userData.skeleton = this.skelett.skeleton;
        figur.userData.rootBone = this.skelett.rootBone;

        // Die Anzeige haengt am rootBone — der ist neu, also neu aufbauen.
        if (this.anzeige) this.rigAufbauen(this.anzeige.visible);

        window.loadedCharacters = window.loadedCharacters || [];
        if (!window.loadedCharacters.includes(figur)) {
            window.loadedCharacters.push(figur);
        }

        this._kleiderBinden(figur, netz);
        this._haareBinden(figur, netz);
        console.log('✓ SkinnedMesh erstellt:', this.skelett.skeleton.bones.length,
            'Knochen, skinIndex:', !!geo.attributes.skinIndex);
        return netz;
    }

    /** Einen BVH-Text als Animation auf ein SkinnedMesh legen. */
    async bvhAufspielen(bvhText, netz) {
        if (!this.skelett?.boneByName) throw new Error('Skelett nicht bereit');
        const clip = await fetchRetargetedClipFromText(
            bvhText, this.skelett, { bodyHeight: this.koerperhoehe(netz) });
        const mixer = new THREE.AnimationMixer(netz);
        const aktion = mixer.clipAction(clip);
        aktion.setLoop(THREE.LoopRepeat);
        aktion.play();
        aktion.paused = true;
        const dauer = clip.duration || 1;
        console.log(`✓ Umgezielter Clip: ${clip.tracks.length} Spuren, ${dauer.toFixed(2)}s`);
        return { mixer, action: aktion, duration: dauer };
    }

    /** Hoehe des Netzes in Metern — fuer die Groessenanpassung der Animation. */
    koerperhoehe(netz) {
        if (!netz) return Skinner.HOEHE_ERSATZ;
        const kasten = new THREE.Box3().setFromObject(netz);
        return kasten.isEmpty() ? Skinner.HOEHE_ERSATZ : kasten.max.y - kasten.min.y;
    }

    // ------------------------------------------------------------ Rig-Anzeige

    /**
     * SkeletonHelper (neu) aufbauen. Ersetzt zwei gleichlautende Bloecke aus
     * main.js — einen beim Umwandeln, einen beim Einschalten. Die fuenf
     * Einstellungen selbst kommen aus gemeinsam/skelettanzeige.js: Dieselben
     * Zeilen standen auch im Rig-Umschalter der Viewer-Seite, also dreimal im
     * Projekt.
     */
    rigAufbauen(sichtbar = true) {
        if (!this.skelett) return null;
        this.anzeige = this.anzeige
            ? Skelettanzeige.erneuern(this.scene, this.anzeige, this.skelett.rootBone)
            : Skelettanzeige.bauen(this.scene, this.skelett.rootBone, sichtbar);
        return this.anzeige;
    }

    /** Rig-Anzeige umschalten; gibt den neuen Zustand zurueck. */
    rigUmschalten() {
        this.rigSichtbar = !this.rigSichtbar;
        if (this.rigSichtbar && !this.anzeige) this.rigAufbauen(true);
        else if (this.anzeige) this.anzeige.visible = this.rigSichtbar;
        return this.rigSichtbar;
    }

    // ------------------------------------------------------------------ intern

    /** skinIndex/skinWeight aus den Servergewichten fuellen. */
    _gewichtefelder(geo) {
        const anzahl = geo.attributes.position.count;
        const k = Skinner.EINFLUESSE;
        const indizes = new Float32Array(anzahl * k);
        const werte = new Float32Array(anzahl * k);
        const vorhanden = this.gewichte.weights ? this.gewichte.weights.length : 0;
        if (anzahl !== vorhanden) {
            console.error(`[SkinnedMesh] Vertexzahl passt nicht: Netz=${anzahl} Gewichte=${vorhanden}`);
        }
        for (let v = 0; v < anzahl; v++) {
            const paare = this.gewichte.weights[v] || [];
            const staerkste = paare.slice().sort((a, b) => b[1] - a[1]).slice(0, k);
            let summe = staerkste.reduce((s, e) => s + e[1], 0);
            if (summe < 1e-6) summe = 1;
            for (let i = 0; i < k; i++) {
                indizes[v * k + i] = i < staerkste.length ? staerkste[i][0] : 0;
                werte[v * k + i] = i < staerkste.length ? staerkste[i][1] / summe : 0;
            }
        }
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(indizes, k));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(werte, k));
    }

    /**
     * Kleidung ans Skelett binden. Der rootBone wird NICHT mitgegeben: Er
     * gehoert ins Koerpernetz. Kleidungsstuecke teilen dasselbe Skelett und
     * benutzen die bindMatrix des Koerpers.
     */
    _kleiderBinden(figur, netz) {
        figur.traverse((kind) => {
            if (kind.isSkinnedMesh && kind !== netz && kind.userData.needsBinding) {
                kind.bind(this.skelett.skeleton, netz.bindMatrix);
                delete kind.userData.needsBinding;
                console.log('✓ Kleidung gebunden:', kind.name || kind.userData.garmentId);
            }
        });
    }

    _haareBinden(figur, netz) {
        const kopf = this.kopfknochenNummer();
        if (kopf < 0) return;
        for (const haare of figur.children.filter(k => k.userData.isHair)) {
            let ungebunden = false;
            haare.traverse((kind) => {
                if (kind.isMesh && !kind.isSkinnedMesh) ungebunden = true;
            });
            if (!ungebunden) continue;
            const gebunden = this.haareUmwandeln(haare, kopf, netz);
            figur.remove(haare);
            figur.add(gebunden);
            console.log('✓ Haare zu SkinnedMesh umgewandelt:', haare.name || 'Haare');
        }
    }

    /** Nummer des Kopfknochens in der Gewichtsliste, sonst -1. */
    kopfknochenNummer() {
        if (!this.gewichte) return -1;
        const namen = this.gewichte.bone_names;
        for (const name of Skinner.KOPFKNOCHEN) {
            const nummer = namen.indexOf(name);
            if (nummer >= 0) return nummer;
        }
        return -1;
    }

    /** Haarnetze vollstaendig an den Kopfknochen binden (Gewicht 1). */
    haareUmwandeln(gltfSzene, kopfnummer, koerpernetz) {
        const netze = [];
        gltfSzene.traverse(kind => {
            if (kind.isMesh) netze.push(kind);
        });
        const gruppe = new THREE.Group();
        gruppe.userData.isHair = true;
        for (const kind of netze) {
            const geo = kind.geometry.clone();
            const anzahl = geo.attributes.position.count;
            const k = Skinner.EINFLUESSE;
            const indizes = new Float32Array(anzahl * k);
            const werte = new Float32Array(anzahl * k);
            for (let v = 0; v < anzahl; v++) {
                indizes[v * k] = kopfnummer;
                werte[v * k] = 1.0;
            }
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(indizes, k));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(werte, k));
            const gebunden = new THREE.SkinnedMesh(geo, kind.material);
            // Weltmatrix uebernehmen, sonst sitzen die Haare falsch.
            kind.updateWorldMatrix(true, false);
            gebunden.applyMatrix4(kind.matrixWorld);
            gebunden.bind(this.skelett.skeleton, koerpernetz.bindMatrix);
            gebunden.userData.isHair = true;
            gruppe.add(gebunden);
        }
        return gruppe;
    }
}
