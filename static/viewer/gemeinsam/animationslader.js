import * as THREE from 'three';
import { Skelettanzeige } from './skelettanzeige.js';
import { Protokoll } from './protokoll.js';

/**
 * Animationslader — eine BVH laden, am Server auf das DEF-Skelett umzielen und
 * auf der Figur abspielen. Geht das nicht, wird das BVH-Skelett selbst als
 * Strichfigur gezeigt.
 *
 * Umbau 16.08.2026: Diese Funktion gab es ZWEIMAL, als `loadBVHAnimation` in
 * `viewer/animation.js` (105 Zeilen) und in `animation/wiedergabe.js`
 * (91 Zeilen) — Zeile für Zeile dasselbe, nur mit verschiedenen
 * Zustandsträgern (`state` gegen `Seitenzustand`) und verschieden formatierter
 * Info-Zeile. Beide Fassungen hatten denselben Rückfallweg mit derselben
 * Höhenskalierung, dieselbe 404-Behandlung, dasselbe Tempo aus `#anim-speed`.
 *
 * Der Zustandsträger und die Beschriftung sind jetzt Parameter.
 */
export class Animationslader {

    /** Körperhöhe, wenn sie nicht zu messen ist. */
    static ERSATZ_KOERPERHOEHE = 1.68;
    /** Körperhöhe im Rückfallweg (Strichfigur). */
    static ERSATZ_HOEHE_STRICH = 1.75;
    /** Kleinste Skelettgröße, damit nicht durch 0 geteilt wird. */
    static MIN_SKELETTHOEHE = 0.01;

    /**
     * @param zustand      state bzw. Seitenzustand
     * @param wahl.beschriften (name, bilder, dauer) => Text der Info-Zeile
     * @param wahl.anhalten    (zerstoeren) => laufende Animation beenden
     * @param wahl.skinnen     (gewichte) => Netz in ein SkinnedMesh wandeln
     * @param wahl.umzielen    (url, skelett, wahl) => Clip vom Server
     * @param wahl.merken      (name, bilder, dauer) => Zusatzfelder pflegen
     */
    constructor(zustand, wahl) {
        this.zustand = zustand;
        this.beschriften = wahl.beschriften;
        this.anhalten = wahl.anhalten;
        this.skinnen = wahl.skinnen;
        this.umzielen = wahl.umzielen;
        this.merken = wahl.merken || (() => {});
        // Die Animationsseite hält ihren BVH-Lader im Modul, die Viewer-Seite
        // im Zustand.
        this.bvhLader = wahl.bvhLader || zustand.bvhLoader;
    }

    async laden(url, name, bilder) {
        this.anhalten(true);
        this.name = name || 'Animation';
        this.bilder = bilder || 0;
        this._info(`Lade ${this.name}...`);
        if (await this._umgezielt(url)) return true;
        return this._strichfigur(url);
    }

    _info(text) {
        const feld = document.getElementById('anim-info');
        if (feld) feld.textContent = text;
    }

    /** Tempo aus dem Regler der Seite, in Prozent. */
    _tempo() {
        const regler = document.getElementById('anim-speed');
        if (regler) this.zustand.mixer.timeScale = parseInt(regler.value, 10) / 100;
    }

    _abspielen(wurzel, clip) {
        this.zustand.mixer = new THREE.AnimationMixer(wurzel);
        this._tempo();
        this.zustand.currentAction = this.zustand.mixer.clipAction(clip);
        this.zustand.currentAction.play();
        this.zustand.playing = true;
        const dauer = this.zustand.currentAction.getClip().duration;
        this.merken(this.name, this.bilder, dauer);
        const knopf = document.getElementById('anim-play');
        if (knopf) knopf.innerHTML = '<i class="fas fa-pause"></i>';
        this._info(this.beschriften(this.name, this.bilder, dauer));
    }

    // ---------------------------------------------------------- Weg 1: Umzielen

    /** true, wenn die Animation umgezielt läuft. */
    async _umgezielt(url) {
        const z = this.zustand;
        if (!z.rigifySkeletonData || !z.skinWeightData || !z.bodyMesh) return false;
        if (!z.isSkinned) this.skinnen(z.skinWeightData);
        try {
            const clip = await this.umzielen(url, z.rigifySkeleton,
                                             { bodyHeight: this.koerperhoehe() });
            // Die Strichanzeige des DEF-Skeletts muss stehen, bevor der Clip läuft.
            if (!z.skeletonHelper) {
                z.skeletonHelper = Skelettanzeige.bauen(z.scene,
                                                        z.rigifySkeleton.rootBone,
                                                        z.rigVisible);
            }
            this._abspielen(z.bodyMesh, clip);
            return true;
        } catch (fehler) {
            return this._umzielfehler(fehler, url);
        }
    }

    /**
     * Fehlt die Datei, ist der Rückfallweg zwecklos: Er holt dieselbe Adresse
     * noch einmal und scheitert genauso. Vorher standen deshalb ZWEI rote
     * Meldungen in der Konsole, wenn eine gespeicherte Animation umbenannt oder
     * gelöscht worden war — ohne Hinweis darauf, was fehlt.
     */
    _umzielfehler(fehler, url) {
        if (String(fehler?.message).includes('404')) {
            Protokoll.warnung('animationslader', 'Animation nicht vorhanden:', url);
            this._info(`Datei fehlt: ${this.name}`);
            return true;   // als behandelt gelten lassen
        }
        console.error('Umzielen am Server fehlgeschlagen:', fehler);
        return false;
    }

    koerperhoehe() {
        const kasten = new THREE.Box3().setFromObject(this.zustand.bodyMesh);
        return kasten.isEmpty() ? Animationslader.ERSATZ_KOERPERHOEHE
                                : kasten.max.y - kasten.min.y;
    }

    // -------------------------------------------------------- Weg 2: Strichfigur

    /** BVH-Skelett als eigene Strichfigur, auf Körperhöhe skaliert. */
    _strichfigur(url) {
        return new Promise(fertig => {
            const lader = this.bvhLader;
            if (!lader) {
                console.error('Kein BVH-Lader vorhanden');
                fertig(false);
                return;
            }
            lader.load(url, ergebnis => {
                fertig(this._strichfigurAufbauen(ergebnis));
            }, undefined, fehler => {
                console.error('BVH nicht ladbar:', fehler);
                this._info(`Fehler: ${this.name}`);
                fertig(false);
            });
        });
    }

    _strichfigurAufbauen(ergebnis) {
        const knochen = ergebnis.skeleton.bones;
        if (!knochen.length) return false;
        const z = this.zustand;
        const wurzel = knochen[0];
        wurzel.updateWorldMatrix(true, true);

        const gruppe = new THREE.Group();
        const maszstab = this._maszstab(knochen);
        gruppe.scale.set(maszstab, maszstab, maszstab);
        gruppe.add(wurzel);
        z.scene.add(gruppe);
        z.skelWrapper = gruppe;

        if (z.skeletonHelper) z.scene.remove(z.skeletonHelper);
        z.skeletonHelper = Skelettanzeige.bauen(z.scene, wurzel, z.rigVisible);
        this._abspielen(wurzel, ergebnis.clip);
        return true;
    }

    /** Die Strichfigur wird auf die Höhe des Körpers gebracht. */
    _maszstab(knochen) {
        const kasten = new THREE.Box3();
        const punkt = new THREE.Vector3();
        for (const knoten of knochen) {
            knoten.updateWorldMatrix(true, false);
            knoten.getWorldPosition(punkt);
            kasten.expandByPoint(punkt);
        }
        const skeletthoehe = kasten.max.y - kasten.min.y;
        let koerper = Animationslader.ERSATZ_HOEHE_STRICH;
        if (this.zustand.bodyMesh) {
            const koerperkasten = new THREE.Box3()
                .setFromObject(this.zustand.bodyMesh);
            if (!koerperkasten.isEmpty()) {
                koerper = koerperkasten.max.y - koerperkasten.min.y;
            }
        }
        return koerper / Math.max(skeletthoehe, Animationslader.MIN_SKELETTHOEHE);
    }
}
