import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Meshfigurbuehne } from '../meshfigur/meshfigurbuehne.js';
import { Engine2d3dKleiderposenkopie } from './engine2d3dkleiderposenkopie.js';
import { Engine2d3dKleiderstandbestellung } from './engine2d3dkleiderstandbestellung.js';

/**
 * Engine2d3dKleiderbuehnenmodell — das 3D-Modell des LETZTEN Stands auf der Hauptbühne.
 *
 * Edgar, 01.10.2026: „das laden des 3d modells dauert immer lange, meldung: es wird gebaut. Baue beim letzten stand ein 3d
 * modell (Genesis mit assets) und lades es gleich, das muss schnell gehen." Quelle ist deshalb zuerst die fertige GLB des
 * Stands (`z.standmodell`, `Engine2d3dKleiderstandmodell` auf dem Server: Körper mit gebackenen Kacheln, Augen, Mund, Wimpern,
 * Brauen, Kleider und Haar am Rig — gemessen 1,1 s für 46 MB), sonst die GLB der jüngsten Runde. Fehlt die Datei oder ist
 * sie veraltet, bestellt `Engine2d3dKleiderstandbestellung` sie; bis dahin steht die alte Fassung da.
 *
 * Der Knopf ist von selbst an (nur ein ausdrückliches Aus bleibt je Browser gemerkt). Solange er ein Modell zeigt, ist
 * „3DModell" (die im Browser gebaute Genesis-Figur) aus — und wird gar nicht erst gebaut (`Meshfigurbuehne.zeigen`). Gibt
 * es noch kein Modell, bleibt „3DModell" an: Bis 01.10.2026 schaltete ein gemerktes „an" die Figur auch dann aus, wenn
 * der Auftrag kein Modell hatte, und die Bühne blieb leer (Auftrag `.52`, Befund Edgar „es wird kein 3d modell angezeigt").
 *
 * „Haare" und „Kleider" blenden die Knoten des Modells ein und aus (`_teile`, Präfix `<art>__`). Die Bewegung spielt
 * `Engine2d3dKleideranimation` direkt auf dem Skelett dieser GLB (`figur()`); nur wenn sie auf der Genesis-Figur liegt, überträgt
 * `Engine2d3dKleiderposenkopie` deren Haltung.
 */
export class Engine2d3dKleiderbuehnenmodell {

    static ARTEN = {
        modell: {
            knopf: 'buehne-iterationsmodell',
            speicher: 'engine2d3dkleider.buehne.iterationsmodell',
            name: 'Modell',
            leer: 'Modell',
            titel: q => (!q.stand ? `Modell der Runde ${q.runde}: Grundfigur mit Haar`
                : q.runde ? `Das Modell des letzten Stands (Runde ${q.runde}): Genesis mit Augen, Kleidern und Haar, am Rig`
                    : q.kleidung ? 'Noch keine Iteration: die Grundfigur aus dem Schritt „Körper“ mit Augen, Brauen, Wimpern und den Kleiderstücken aus dem Netz '
                                   + '(Schritt „Kleiderstücke“), am Rig — Haar setzen erst die Iterationen'
                        : 'Noch keine Iteration: die Grundfigur aus dem Schritt „Körper“ mit Augen, Brauen und Wimpern, am Rig — '
                          + 'Kleider (Schritt „Kleiderstücke“) und Haar setzen erst die Iterationen'),
            keine: 'Noch kein Modell — erst nach dem Schritt „Körper“',
        },
    };

    constructor(seite, buehne, art = 'modell') {
        this.seite = seite;
        this.buehne = buehne;
        this.art = art;
        this.eigen = Engine2d3dKleiderbuehnenmodell.ARTEN[art];
        this.knopf = document.getElementById(this.eigen.knopf);
        this.beschriftung = this.knopf.querySelector('span');
        this.an = this._gemerkt();
        this.gruppe = null;
        this.skelett = null;
        this.geschwister = null;
        this._adresse = null;
        this._laedt = null;
        this.bestellung = new Engine2d3dKleiderstandbestellung(seite, text => this.buehne._melden(text));
        this.knopf.classList.toggle('active', this.an);
        // Schon hier, aus dem Zustand im Kopf der Seite: `Engine2d3dKleiderseite.zeigen` ruft die Bühne VOR diesem Modell — stünde
        // „3DModell" beim ersten Takt noch an, finge der Bau im Browser an, den das Modell ersetzen soll.
        this._hatQuelle = this._ersetzt(seite.zustand || {});
        this.buehne.schalter?.setzen('modell', !(this.an && this._hatQuelle));
        this.knopf.addEventListener('click', () => this.umschalten());
        this.kopie = null;
        this._quelle = null;
        const schalter = this.buehne.schalter;
        if (schalter) {
            const vorher = schalter.geaendert;
            schalter.geaendert = () => { vorher(); this._teile(); };
        }
        // „Haare"/„Kleider" ohne Inhalt sagen beim Klick, warum nichts passiert (Befund Edgar, 01.10.2026: „Buttons Kleider,
        // haare ohne effekt" — `.52` hat keine Iteration, sein Modell trägt weder Kleider noch Haar).
        for (const knopf of document.querySelectorAll('button[data-schalter="haare"], button[data-schalter="kleider"]')) {
            knopf.addEventListener('click', () => {
                if (this.an && this.gruppe && knopf.classList.contains('ohne-inhalt')) this.buehne._melden(knopf.title);
            });
        }
        this._takt();
    }

    /** Zu welchem Schalter ein Knoten der GLB gehört: haar | kleidung | koerper. */
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
        this._inhalt();
        if (!this.gruppe) return;
        const an = this.buehne.schalter?.stand || {};
        this.gruppe.traverse(teil => {
            if (!teil.isMesh) return;
            const art = Engine2d3dKleiderbuehnenmodell.art(teil.name);
            if (art === 'haar') teil.visible = an.haare !== false;
            else if (art === 'kleidung') teil.visible = an.kleider !== false;
        });
    }

    /** „Haare" und „Kleider" blass, wenn das gezeigte Modell nichts davon trägt — gesperrt wird nicht (`Meshfigurschalter`). */
    _inhalt() {
        const arten = new Set();
        if (this.an && this.gruppe) this.gruppe.traverse(t => { if (t.isMesh) arten.add(Engine2d3dKleiderbuehnenmodell.art(t.name)); });
        for (const [schluessel, art, was, wer] of [
            ['haare', 'haar', 'kein Haar', 'das setzen erst die Iterationen'],
            ['kleider', 'kleidung', 'keine Kleider', 'der Schritt „Kleiderstücke“ und die Iterationen setzen sie'],
        ]) {
            const knopf = document.querySelector(`button[data-schalter="${schluessel}"]`);
            if (!knopf) continue;
            knopf.dataset.titel ??= knopf.title;
            const leer = !!(this.an && this.gruppe) && !arten.has(art);
            knopf.classList.toggle('ohne-inhalt', leer);
            knopf.title = leer ? `Das Modell trägt ${was} — ${wer} (Reiter „Iterationen“)`
                : knopf.dataset.titel;
        }
    }

    /** Die Grundfigur um `Meshfigurbuehne.ABSTAND` nach rechts, solange Modell UND Grundfigur zu sehen sind. */
    _versetzen() {
        const figur = this.buehne.modell?.group;
        if (!figur) return;
        const versetzt = this.an && !!this.gruppe && !!this.buehne.schalter?.stand.modell;
        figur.position.x = versetzt ? Meshfigurbuehne.ABSTAND : 0;
    }

    /** Von selbst an — nur ein ausdrückliches Aus (`'0'`) bleibt gemerkt. */
    _gemerkt() {
        try { return localStorage.getItem(this.eigen.speicher) !== '0'; } catch { return true; }
    }

    _merken() {
        try { localStorage.setItem(this.eigen.speicher, this.an ? '1' : '0'); } catch { /* stumm gewollt: nur Bequemlichkeit */ }
    }

    /**
     * Das Modell des Stands, sonst die BESTE Runde mit GLB (`kreislauf.runde_bester`, sonst die jüngste) → {adresse,
     * runde, stand} oder null. Ist der Stand veraltet (ein Lauf rechnet gerade), geht die beste Runde vor.
     */
    static quelle(z, seite, schluessel = 'modell') {
        const s = z.standmodell, beste = Number(((z.ergebnis || {}).kreislauf || {}).runde_bester || 0);
        const runden = ((z.ergebnis || {}).iterationen || []).filter(r => (r.dateien || {})[schluessel]);
        const r = runden.find(x => Number(x.runde) === beste) || runden.at(-1) || null;   // Runden in Rundenfolge
        if (s?.datei && (s.aktuell || !r || Number(r.runde) <= Number(s.runde || 0))) {
            const adresse = `${seite.dateiAdresse('ergebnis', s.datei)}?v=${encodeURIComponent(s.fassung || '')}`;
            // `teile` steht im Bericht des Stands (`stand.json`): trägt er Kleidung (Fotostücke vor den Iterationen, `Standvorabkleider`)?
            return { adresse, runde: s.runde, stand: true, kleidung: (s.teile || []).some(t => String(t).startsWith('kleidung:')) };
        }
        if (!r) return null;
        return { adresse: seite.dateiAdresse('iterationen', r.dateien[schluessel]), runde: r.runde, stand: false };
    }

    /** Gibt es ein Modell, das die Genesis-Figur ersetzt — die GLB einer Runde, oder die des Stands (da oder bestellt)? */
    _ersetzt(z) {
        return !!Engine2d3dKleiderbuehnenmodell.quelle(z, this.seite, this.art) || Engine2d3dKleiderstandbestellung.kommt(z);
    }

    umschalten() {
        if (!this.an && this.geschwister?.an) this.geschwister.ausschalten();
        this.an = !this.an;
        this._merken();
        this.knopf.classList.toggle('active', this.an);
        this.buehne.schalter?.setzen('modell', !(this.an && this._hatQuelle));
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

    /** Für `Engine2d3dKleideranimation`: `{group, skelett}` dieser GLB, solange sie zu sehen ist und ein Rig hat — sonst null. */
    figur() {
        return this.an && this.gruppe && this.skelett ? { group: this.gruppe, skelett: this.skelett } : null;
    }

    /**
     * Jedes Bild: die Grundfigur neben das Modell rücken, solange beide zu sehen sind; dann — nur wenn die Bewegung auf der
     * Genesis-Figur liegt, nicht auf dieser GLB — deren Haltung übernehmen.
     */
    _takt() {
        requestAnimationFrame(() => this._takt());
        this._versetzen();
        if (!this.an || !this.skelett || this.seite.animation?.ziel === this.gruppe) return;
        const quelle = this.buehne.modell?.skelett;
        if (!quelle) return;
        // Genesis 9 baut die feine Stufe mit NEUEN Knochen nach (siehe `Engine2d3dKleideranimation._pruefen`).
        if (quelle.rootBone?.uuid !== this._quelle) {
            this._quelle = quelle.rootBone?.uuid;
            this.kopie = new Engine2d3dKleiderposenkopie(this.skelett, quelle);
        }
        this.kopie?.folgen(!!this.seite.animation?.action);
    }

    zeigen(z) {
        if (!this.buehne.szene) return;
        const quelle = Engine2d3dKleiderbuehnenmodell.quelle(z || {}, this.seite, this.art);
        this.bestellung.pruefen(z || {});
        this.knopf.title = quelle ? this.eigen.titel(quelle) : this.eigen.keine;
        this.beschriftung.textContent = quelle?.runde ? `${this.eigen.name} (Runde ${quelle.runde})`
            : quelle ? `${this.eigen.name} (ohne Iteration)` : this.eigen.leer;
        // Die Genesis-Figur nur dann ausschalten, wenn es ein Modell gibt (oder gleich gibt), das sie ersetzt — und nur,
        // wenn sich das ändert: sonst nähme der Takt der Seite (alle 2 s) jedem Klick auf „3DModell" die Wirkung.
        const hat = this._ersetzt(z || {});
        if (hat !== this._hatQuelle) {
            this._hatQuelle = hat;
            this.buehne.schalter?.setzen('modell', !(this.an && hat));
            this.buehne._sichtbarkeit?.();
        }
        if (this.gruppe) this.gruppe.visible = this.an;
        if (!this.an || !quelle || quelle.adresse === this._adresse || this._laedt) return;
        this._laden(quelle);
    }

    async _laden(quelle) {
        this._laedt = quelle.adresse;
        const t0 = performance.now();
        this.buehne._melden(`${this.eigen.name} wird geladen …`);
        try {
            const gltf = await new GLTFLoader().loadAsync(quelle.adresse);
            this._entfernen();
            this.gruppe = gltf.scene;
            this.gruppe.name = 'Iterationsmodell_' + this.art;
            this.skelett = Engine2d3dKleiderbuehnenmodell._skelett(this.gruppe);
            this.gruppe.visible = this.an;
            this._teile();
            this.buehne.szene.add(this.gruppe);
            this._adresse = quelle.adresse;
            this.buehne._melden('');
            console.info(`[2D3D Kleider] ${this.eigen.name} geladen in ${Math.round(performance.now() - t0)} ms: ${quelle.adresse}`);
        } catch (fehler) {
            this.buehne._melden(`${this.eigen.name} nicht geladen: ${fehler.message}`);
        } finally {
            this._laedt = null;
        }
    }

    _entfernen() {
        if (!this.gruppe) return;
        this.buehne.szene.remove(this.gruppe);
        this.gruppe.traverse(teil => {
            teil.geometry?.dispose();
            for (const stoff of [].concat(teil.material || [])) {
                stoff.map?.dispose();
                stoff.dispose();
            }
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
