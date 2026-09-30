import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Blendermodellposenkopie } from './blendermodellposenkopie.js';

/**
 * Blendermodellbuehnenmodell — ein Modell der letzten Iteration auf der Hauptbühne (Edgar, 29.09.2026: „mach auch im
 * Hauptfenster das 3D Modell sichtbar, meinetwegen auf Knopfdruck, für die letzte Iteration" und „es geht um das
 * ganze Modell, inkl. Kostüm").
 *
 * Zwei Arten, je ein Knopf (`ARTEN`), einander ausschließend:
 *   modell — die GLB `dateien.modell` (`Kostuemrunde.modell`): Grundfigur + Kostüm aus TEILEN am Rig, in der gestellten Haltung,
 *            so, wie die Runde benotet wurde. Knopf `#buehne-iterationsmodell`.
 *   sicht  — die GLB `dateien.sicht` (`Sichtmodell`): der Sichtkörper der Vorlage mit Fototextur und der Stab, am selben Rig.
 *            Knopf `#buehne-sichtmodell`. Er hat den Umriss der Fotos in jeder Ansicht (30.09.2026 nachts gebaut).
 * Ein Knopf schaltet sein Modell ein; dabei geht „Grundfigur" aus (sichtbar am Knopf, zum Vergleich wieder einschaltbar) und
 * das andere Modell aus. Der Stand jedes Knopfs bleibt je Browser gemerkt.
 *
 * Die Bewegung (`Blendermodellanimation`) läuft weiter auf der — dann ausgeblendeten — Genesis-Figur; das Modell
 * übernimmt deren Haltung je Bild (`Blendermodellposenkopie`: andere Knochenachsen, gleiche Knochen) — aber erst, wenn die
 * Bewegung angefasst ist (`Blendermodellanimation.bewegt`: läuft oder nicht auf Bild 1). Davor steht das Modell in der Haltung
 * der Runde, so wie das Bild „Render" sie zeigt; sonst stünde es von Anfang an in der ersten Tanzpose.
 */
export class Blendermodellbuehnenmodell {

    static ARTEN = {
        modell: {
            knopf: 'buehne-iterationsmodell',
            speicher: 'blendermodell.buehne.iterationsmodell',
            name: 'Modell',
            leer: 'Modell (letzte Iteration)',
            titel: r => `Modell der Runde ${r}: Grundfigur mit Kostüm aus Teilen, am Rig (spielt auch die Bewegung)`,
            keine: 'Noch keine Runde mit Modell — erst „Weiter iterieren“ im Reiter „Iterationen“',
        },
        sicht: {
            knopf: 'buehne-sichtmodell',
            speicher: 'blendermodell.buehne.sichtmodell',
            name: 'Sichtmodell',
            leer: 'Sichtmodell',
            titel: r => `Sichtmodell der Runde ${r}: der Umriss der Fotos mit Fototextur, am Rig`,
            keine: 'Noch kein Sichtmodell — es entsteht alle fünf Minuten mit dem Modell einer Runde (Option „Sichtmodell“)',
        },
    };

    constructor(seite, buehne, art = 'modell') {
        this.seite = seite;
        this.buehne = buehne;
        this.art = art;
        this.eigen = Blendermodellbuehnenmodell.ARTEN[art];
        this.knopf = document.getElementById(this.eigen.knopf);
        this.beschriftung = this.knopf.querySelector('span');
        this.an = this._gemerkt();
        this.gruppe = null;
        this.skelett = null;
        this.wahl = null;
        this.feld = document.getElementById('buehne');
        this.geschwister = null;
        this._adresse = null;
        this._laedt = null;
        this.knopf.classList.toggle('active', this.an);
        if (this.an) this.buehne.schalter?.setzen('modell', false);
        this.knopf.addEventListener('click', () => this.umschalten());
        this.kopie = null;
        this._quelle = null;
        this._takt();
    }

    _gemerkt() {
        try { return localStorage.getItem(this.eigen.speicher) === '1'; } catch { return false; }
    }

    _merken() {
        try { localStorage.setItem(this.eigen.speicher, this.an ? '1' : '0'); } catch { /* stumm gewollt: nur Bequemlichkeit */ }
    }

    /** Die Runde `wahl` — sonst die jüngste — mit Datei `schluessel` in `dateien` → {adresse, runde} oder null. */
    static quelle(z, seite, schluessel = 'modell', wahl = null) {
        const runden = ((z.ergebnis || {}).iterationen || []).filter(r => (r.dateien || {})[schluessel]);
        if (!runden.length) return null;
        const r = wahl === null ? runden.reduce((a, b) => (Number(b.runde) > Number(a.runde) ? b : a))
            : runden.find(x => Number(x.runde) === Number(wahl));
        if (!r) return null;
        return { adresse: seite.dateiAdresse('iterationen', r.dateien[schluessel]), runde: r.runde };
    }

    /** Das Modell EINER Runde zeigen (Knopf „In 3D" in der Bilderzeile der Iterationen) statt des jüngsten: Bild und Bühne
     *  gehören dann zur selben Runde (Edgar, 30.09.2026: „3924 zeigt was anderes als im 3D View"). */
    waehlen(runde) {
        if (!this.an && this.geschwister?.an) this.geschwister.ausschalten();
        this.wahl = runde;
        this.an = true;
        this._merken();
        this.knopf.classList.add('active');
        this.buehne.schalter?.setzen('modell', false);
        this.buehne._sichtbarkeit?.();
        this.zeigen(this.seite.zustand);
        this.feld?.scrollIntoView({ block: 'nearest' });
    }

    umschalten() {
        if (!this.an && this.geschwister?.an) this.geschwister.ausschalten();
        this.an = !this.an;
        if (this.an) this.wahl = null;
        this._merken();
        this.knopf.classList.toggle('active', this.an);
        this.buehne.schalter?.setzen('modell', !this.an);
        this.buehne._sichtbarkeit?.();
        this.zeigen(this.seite.zustand);
    }

    /** Vom anderen Knopf aufgerufen: nur dieses Modell wegnehmen, die Grundfigur bleibt Sache des Aufrufers. */
    ausschalten() {
        this.an = false;
        this._merken();
        this.knopf.classList.remove('active');
        if (this.gruppe) this.gruppe.visible = false;
    }

    /** Jedes Bild: der Haltung der Genesis-Figur folgen, solange eine Bewegung auf ihr liegt. */
    _takt() {
        requestAnimationFrame(() => this._takt());
        if (!this.an || !this.skelett) return;
        const quelle = this.buehne.modell?.skelett;
        // Genesis 9 baut die feine Stufe mit NEUEN Knochen nach (siehe `Blendermodellanimation._pruefen`).
        if (quelle && quelle.rootBone?.uuid !== this._quelle) {
            this._quelle = quelle.rootBone?.uuid;
            this.kopie = new Blendermodellposenkopie(this.skelett, quelle);
        }
        this.kopie?.folgen(!!this.seite.animation?.bewegt());
    }

    zeigen(z) {
        if (!this.buehne.szene) return;
        const quelle = Blendermodellbuehnenmodell.quelle(z || {}, this.seite, this.art, this.wahl);
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
            this.skelett = Blendermodellbuehnenmodell._skelett(this.gruppe);
            this.gruppe.visible = this.an;
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
