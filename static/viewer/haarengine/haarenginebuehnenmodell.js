import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Meshfigurbuehne } from '../meshfigur/meshfigurbuehne.js';
import { Haarengineposenkopie } from './haarengineposenkopie.js';

/**
 * Haarenginebuehnenmodell — das Modell der letzten Iteration auf der Hauptbühne.
 *
 * Der Knopf `#buehne-iterationsmodell` lädt die GLB `dateien.modell` der jüngsten Runde (`Begutachtungsrunde`: Körper, Kleider,
 * Haar als je ein Knoten `<art>__<sorte>__<n>`, in der gestellten Haltung, so, wie die Runde benotet wurde). Dabei geht
 * „Grundfigur" aus; schaltet man sie wieder ein, steht sie zum Vergleich um `Meshfigurbuehne.ABSTAND` (1,5 m) nach rechts
 * versetzt neben dem Modell (Edgar, 30.09.2026). „Haare" und „Kleider" blenden die Knoten des Modells ein und aus (`_teile`;
 * ältere GLBs ohne Präfix: `hair` im Namen = Haar, `koerper` = Körper, sonst Kleidung). Der Stand des Knopfs bleibt je
 * Browser gemerkt.
 *
 * Die Bewegung (`Haarengineanimation`) läuft weiter auf der Genesis-Figur; hat das Modell ein Rig, übernimmt es deren
 * Haltung je Bild (`Haarengineposenkopie`) — die GLB der Runden hat keins, sie steht.
 */
export class Haarenginebuehnenmodell {

    static ARTEN = {
        modell: {
            knopf: 'buehne-iterationsmodell',
            speicher: 'haarengine.buehne.iterationsmodell',
            name: 'Modell',
            leer: 'Modell (letzte Iteration)',
            titel: r => `Modell der Runde ${r}: Grundfigur mit Haar, am Rig (spielt auch die Bewegung)`,
            keine: 'Noch keine Runde mit Modell — erst „Weiter iterieren“ im Reiter „Iterationen“',
        },
    };

    constructor(seite, buehne, art = 'modell') {
        this.seite = seite;
        this.buehne = buehne;
        this.art = art;
        this.eigen = Haarenginebuehnenmodell.ARTEN[art];
        this.knopf = document.getElementById(this.eigen.knopf);
        this.beschriftung = this.knopf.querySelector('span');
        this.an = this._gemerkt();
        this.gruppe = null;
        this.skelett = null;
        this.geschwister = null;
        this._adresse = null;
        this._laedt = null;
        this.knopf.classList.toggle('active', this.an);
        if (this.an) this.buehne.schalter?.setzen('modell', false);
        this.knopf.addEventListener('click', () => this.umschalten());
        this.kopie = null;
        this._quelle = null;
        const schalter = this.buehne.schalter;
        if (schalter) {
            const vorher = schalter.geaendert;
            schalter.geaendert = () => { vorher(); this._teile(); };
        }
        this._takt();
    }

    /** Zu welchem Schalter ein Knoten der Runden-GLB gehört: haar | kleidung | koerper. */
    static art(name) {
        const n = String(name || '');
        if (n.startsWith('haar__')) return 'haar';
        if (n.startsWith('kleidung__')) return 'kleidung';
        if (n.startsWith('koerper')) return 'koerper';
        return /hair|haar/i.test(n) ? 'haar' : 'kleidung';
    }

    /** „Haare" und „Kleider" auf die Knoten des Modells übertragen, die Grundfigur daneben rücken. */
    _teile() {
        this._versetzen();
        if (!this.gruppe) return;
        const an = this.buehne.schalter?.stand || {};
        this.gruppe.traverse(teil => {
            if (!teil.isMesh) return;
            const art = Haarenginebuehnenmodell.art(teil.name);
            if (art === 'haar') teil.visible = an.haare !== false;
            else if (art === 'kleidung') teil.visible = an.kleider !== false;
        });
    }

    /** Die Grundfigur um `Meshfigurbuehne.ABSTAND` nach rechts, solange Modell UND Grundfigur zu sehen sind. */
    _versetzen() {
        const figur = this.buehne.modell?.group;
        if (!figur) return;
        const versetzt = this.an && !!this.gruppe && !!this.buehne.schalter?.stand.modell;
        figur.position.x = versetzt ? Meshfigurbuehne.ABSTAND : 0;
    }

    _gemerkt() {
        try { return localStorage.getItem(this.eigen.speicher) === '1'; } catch { return false; }
    }

    _merken() {
        try { localStorage.setItem(this.eigen.speicher, this.an ? '1' : '0'); } catch { /* stumm gewollt: nur Bequemlichkeit */ }
    }

    /** Die jüngste Runde mit Datei `schluessel` in `dateien` → {adresse, runde} oder null. */
    static quelle(z, seite, schluessel = 'modell') {
        const runden = ((z.ergebnis || {}).iterationen || []).filter(r => (r.dateien || {})[schluessel]);
        if (!runden.length) return null;
        const r = runden.reduce((a, b) => (Number(b.runde) > Number(a.runde) ? b : a));
        return { adresse: seite.dateiAdresse('iterationen', r.dateien[schluessel]), runde: r.runde };
    }

    umschalten() {
        if (!this.an && this.geschwister?.an) this.geschwister.ausschalten();
        this.an = !this.an;
        this._merken();
        this.knopf.classList.toggle('active', this.an);
        this.buehne.schalter?.setzen('modell', !this.an);
        this.buehne._sichtbarkeit?.();
        this._teile();
        this.zeigen(this.seite.zustand);
    }

    /** Vom anderen Knopf aufgerufen: nur dieses Modell wegnehmen, die Grundfigur bleibt Sache des Aufrufers. */
    ausschalten() {
        this.an = false;
        this._merken();
        this.knopf.classList.remove('active');
        if (this.gruppe) this.gruppe.visible = false;
    }

    /**
     * Jedes Bild: die Grundfigur neben das Modell rücken, solange beide zu sehen sind (die Bühne baut die Figur neu, wenn
     * sich ihr Stand ändert — deshalb je Bild, nicht einmal); dann der Haltung der Genesis-Figur folgen, solange eine
     * Bewegung auf ihr liegt.
     */
    _takt() {
        requestAnimationFrame(() => this._takt());
        this._versetzen();
        if (!this.an || !this.skelett) return;
        const quelle = this.buehne.modell?.skelett;
        // Genesis 9 baut die feine Stufe mit NEUEN Knochen nach (siehe `Haarengineanimation._pruefen`).
        if (quelle && quelle.rootBone?.uuid !== this._quelle) {
            this._quelle = quelle.rootBone?.uuid;
            this.kopie = new Haarengineposenkopie(this.skelett, quelle);
        }
        this.kopie?.folgen(!!this.seite.animation?.action);
    }

    zeigen(z) {
        if (!this.buehne.szene) return;
        const quelle = Haarenginebuehnenmodell.quelle(z || {}, this.seite, this.art);
        this.knopf.title = quelle ? this.eigen.titel(quelle.runde) : this.eigen.keine;
        this.beschriftung.textContent = quelle ? `${this.eigen.name} (Runde ${quelle.runde})` : this.eigen.leer;
        if (this.gruppe) this.gruppe.visible = this.an;
        if (!this.an || !quelle || quelle.adresse === this._adresse || this._laedt) return;
        this._laden(quelle);
    }

    async _laden(quelle) {
        this._laedt = quelle.adresse;
        this.buehne._melden(`${this.eigen.name} der Runde ${quelle.runde} wird geladen …`);
        try {
            const gltf = await new GLTFLoader().loadAsync(quelle.adresse);
            this._entfernen();
            this.gruppe = gltf.scene;
            this.gruppe.name = 'Iterationsmodell_' + this.art;
            this.skelett = Haarenginebuehnenmodell._skelett(this.gruppe);
            this.gruppe.visible = this.an;
            this._teile();
            this.buehne.szene.add(this.gruppe);
            this._adresse = quelle.adresse;
            this.buehne._melden('');
        } catch (fehler) {
            this.buehne._melden(`${this.eigen.name} der Runde ${quelle.runde} nicht geladen: ${fehler.message}`);
        } finally {
            this._laedt = null;
        }
    }

    _entfernen() {
        if (!this.gruppe) return;
        this.buehne.szene.remove(this.gruppe);
        this.gruppe.traverse(teil => {
            teil.geometry?.dispose();
            for (const stoff of [].concat(teil.material || [])) stoff.dispose();
        });
        this.gruppe = null;
        this.skelett = null;
        this.kopie = null;
        this._quelle = null;
    }

    static _skelett(gruppe) {
        let skeleton = null;
        gruppe.traverse(teil => { if (!skeleton && teil.isSkinnedMesh) skeleton = teil.skeleton; });
        if (!skeleton) return null;
        const boneByName = Object.fromEntries(skeleton.bones.map(knochen => [knochen.name, knochen]));
        const rootBone = skeleton.bones.find(knochen => !knochen.parent?.isBone) || skeleton.bones[0];
        return { skeleton, boneByName, rootBone };
    }
}
