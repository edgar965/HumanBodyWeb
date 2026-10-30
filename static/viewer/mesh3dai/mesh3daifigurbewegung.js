/**
 * Mesh3daifigurbewegung — die Standardanimation auf der Ergebnisfigur von Mesh3D-AI (22.10.2026).
 *
 * Edgar: „Mach die Standard Animation auf allen Jobs wieder rein, Testjob und trainings jobs, nur bei der Figur. So wie die Mesh-3D Jobs, mit der Standardanimation, playleiste, stop und pause usw.“
 * Still zeigt das Feld die Figur in der Haltung der KI (vom Server gebacken, `drehung`). Für die Bewegung baut diese Klasse DIESELBE Figur (dieselben Regler, Haut, Anatomie-Stück) in der Ruhelage als
 * `Genesis9Modell` — wie Charakter, Studio und Mesh-3D —, holt die Bewegung über denselben Retarget wie die Charakter-Seite (`fetchRetarget`, Ziel `genesis9`, Regler der Figur; `Eigenanimation`) und spielt
 * sie mit einem Mischer ab; je Bild die Gelenkkorrekturen (`Genesis9gelenke.takt`, wie `Meshfigurgelenke`). Die Stücke aus der KI hängen als `SkinnedMesh` am Skelett der Figur (`Mesh3daibewegungskleid`),
 * die Haut darunter fällt weg wie im stillen Bild (`inst.hautStuecke` → `Hautverdeckung`).
 *
 * Solange `aktiv`, hängt das Feld die bewegte Figur ein statt der stillen (`Mesh3daiansicht._fuellen` → `einhaengen`); Stopp gibt das Feld der stillen Figur zurück. Ohne Bewegung zeichnet das Feld
 * nur auf Anforderung — die Schleife hier läuft nur, solange gespielt wird.
 */
import * as THREE from 'three';
import { Eigenhaut } from '../gemeinsam/eigenhaut.js';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Genesis9gelenke } from '../gemeinsam/genesis9gelenke.js';
import { Hautverdeckung } from '../gemeinsam/hautverdeckung.js';
import { fetchRetarget } from '../retarget_hybrid.js';
import { Mesh3daibewegungsfigur } from './mesh3daibewegungsfigur.js';
import { Mesh3daibewegungskleid } from './mesh3daibewegungskleid.js';
import { Mesh3daigenesisfigur } from './mesh3daigenesisfigur.js';
import { Mesh3daikikleiderfeld } from './mesh3daikikleiderfeld.js';

export class Mesh3daifigurbewegung {
    static _nummer = 0;

    /**
     * @param ansicht das Feld der Ergebnisfigur (`Mesh3daiansicht`)
     * @param quelle `async () => ({schluessel, figur, stuecke: [{id, art, netz}], knochen: [Namen], ruhezentren})` oder null (keine Genesis-Figur für diese Probe)
     */
    constructor(ansicht, quelle) {
        this.ansicht = ansicht;
        this.quelle = quelle;
        ansicht.bewegung = this;
        this.aktiv = false;
        this.spielt = false;
        this.wahl = null;               // 'Kategorie/Name' (Standardanimation, von der Leiste gesetzt)
        this.modell = null;
        this.kleider = [];              // {mesh, art, netz}
        this.clip = null;
        this.mixer = null;
        this.action = null;
        this.dauer = 0;
        this.bilder = 0;
        this.fps = 30;
        this.rahmenMm = null;           // Abstand Ruhegelenke der Kinematik ↔ Knochen der gebauten Figur nach starrer Ausrichtung
        this.text = '';
        this.beiAenderung = null;       // die Leiste zieht ihre Anzeige nach
        this._schluessel = null;
        this._q = null;
        this._clipWahl = null;
        this._wurzel = null;
        this._kleiderWurzel = null;
        this._abbildung = null;
        this._kleiderAn = true;
        this._lauf = 0;
        this._uhr = new THREE.Clock();
    }

    _melden(text) {
        this.text = text;
        this.beiAenderung?.();
    }

    // ------------------------------------------------------------------ Bauen

    /** Figur und Bewegung bereitstellen (einmal je Probe bzw. je Wahl); `true`, wenn abgespielt werden kann. */
    async vorbereiten() {
        // Die Seite verwirft die Figur bei jeder neuen Probe, jedem Weg, jedem Geschlecht (`verwerfen`) — solange sie steht, gilt sie.
        if (!this.modell) {
            const lauf = this._lauf;
            const q = await this.quelle();
            if (lauf !== this._lauf) return false;
            if (!q?.figur) {
                this._melden('Für diese Probe gibt es keine Genesis-Figur im Ergebnis — nichts zu bewegen.');
                return false;
            }
            if (!(await this._figurBauen(q))) return false;
        }
        if (!this.wahl) {
            this._melden('Standardanimation wird gelesen …');
            return false;
        }
        if (this._clipWahl !== this.wahl || !this.clip) {
            const lauf = this._lauf;
            await this._bewegungHolen();
            if (lauf !== this._lauf) return false;
        }
        this._pruefen();
        return Boolean(this.action);
    }

    /** → false, wenn die Seite die Figur verworfen hat, während sie gebaut wurde (neue Probe). */
    async _figurBauen(q) {
        this.verwerfen();
        const lauf = this._lauf;
        this._melden('Figur wird in der Ruhelage gebaut …');
        const modell = new Genesis9Modell(`mesh3dai_bewegung_${++Mesh3daifigurbewegung._nummer}`, { ...q.figur, pose: '', drehung: null });
        await modell.bauen();
        if (lauf !== this._lauf) {
            modell.dispose();
            return false;
        }
        this.modell = modell;
        this._q = q;
        this._schluessel = q.schluessel;
        this._wurzel = null;
        // Rahmen der Stücke (Kinematik der Figur) gegen die gebaute Figur: über die Ruhegelenke gemessen, starr ausgeglichen.
        const rahmen = Mesh3daibewegungsfigur.rahmen(modell, q.knochen, q.ruhezentren);
        this._abbildung = rahmen.abbildung;
        this.rahmenMm = rahmen.rest_mm;
        this._kleiderBinden();
        modell.hautStuecke = Mesh3daikikleiderfeld.hautStuecke({
            stuecke: (q.stuecke || []).map(st => ({ id: st.id, art: st.art, kostuem: st.kostuem, ruhe: Mesh3daibewegungskleid.ruhe(st.netz, this._abbildung), dreiecke: st.netz.dreiecke })),
        });
        this._kleiderAn = true;
        Hautverdeckung.planen(modell);
        this._melden('');
        return true;
    }

    _kleiderBinden() {
        for (const k of this.kleider) {
            k.mesh.parent?.remove(k.mesh);
            k.mesh.geometry.dispose();
        }
        this.kleider = [];
        const q = this._q;
        for (const st of q?.stuecke || []) {
            const mesh = Mesh3daibewegungskleid.binden(st.netz, this.modell.skelett, q.knochen, this._abbildung);
            if (!mesh) continue;
            mesh.userData.art = st.art;
            mesh.visible = this._kleiderAn;
            Eigenhaut.einhaengen(this.modell.group, mesh, this.modell.skelett);
            this.kleider.push({ mesh, art: st.art });
        }
        this._kleiderWurzel = this.modell.skelett?.rootBone || null;
    }

    async _bewegungHolen() {
        const wahl = this.wahl;
        const [kategorie, name] = wahl.split('/');
        this._melden(`Bewegung „${name}“ wird auf die Figur umgesetzt …`);
        const m = this.modell;
        const clip = await fetchRetarget({ category: kategorie, name }, m.skelett, { target: 'genesis9', figur: m.figur, regler: m.regler || {}, bodyHeight: Mesh3daibewegungsfigur.hoehe(m) });
        if (wahl !== this.wahl || m !== this.modell) return;          // inzwischen eine andere Wahl oder Figur
        this.clip = clip;
        this._clipWahl = wahl;
        const zeiten = this.clip.tracks[0]?.times;
        this.bilder = zeiten?.length || 0;
        this.dauer = this.clip.duration;
        this.fps = this.dauer > 0 && this.bilder > 1 ? (this.bilder - 1) / this.dauer : 30;
        this._wurzel = null;                // neuer Mischer beim nächsten `_pruefen`
        this._melden('');
    }

    /**
     * Genesis 9 baut in zwei Zügen (Käfig, dann die gewählte Stufe) und dabei jedes Mal NEUE Knochen (`Engine2d3dKleideranimation._pruefen`): ein Mischer an den alten Knochen bewegt nichts Sichtbares.
     * Wechselt die Wurzel, bekommen Mischer und Stücke das neue Skelett; die Stelle der Bewegung bleibt.
     */
    _pruefen() {
        const wurzel = this.modell?.skelett?.rootBone || null;
        if (!this.clip || !wurzel || wurzel === this._wurzel) return;
        const zeit = this.action ? this.action.time : 0;
        const lief = this.action ? this.action.isScheduled() && !this.action.paused : false;
        this.mixer?.stopAllAction();
        if (this._kleiderWurzel !== wurzel) this._kleiderBinden();
        this._wurzel = wurzel;
        this.mixer = new THREE.AnimationMixer(this.modell.group);
        this.action = this.mixer.clipAction(this.clip);
        this.action.setLoop(THREE.LoopRepeat);
        this.action.play();
        this.action.paused = !lief;
        this.action.time = zeit;
        this.mixer.update(0);
    }

    // ------------------------------------------------------------------ Feld

    /** Vom Feld gerufen (`Mesh3daiansicht._fuellen`), solange `aktiv`: die bewegte Figur statt der stillen, in der Ansichtsart der Zeile. */
    einhaengen(inhalt, d) {
        const gruppe = this.modell?.group;
        if (!gruppe) return;
        gruppe.position.set(0, 0, 0);
        gruppe.quaternion.identity();
        gruppe.traverse(o => { o.frustumCulled = false; o.layers.set(1); });
        gruppe.userData.mesh3daiFremd = true;
        // Ansichtsart wie die stille Figur; ohne Ansichtsart (Testseite) die Materialien der Figur.
        inhalt.userData.genesisErsatz = !d?.modus || d.modus === 'textur' ? null : Mesh3daigenesisfigur._ersatz(d.modus);
        this._kleiderZeigen(d?.kleider !== false);
        inhalt.add(gruppe);
    }

    /** Schalter „Kleider“ der Zeile: alle Stücke samt Haar ein- oder aus (seit 30.10.2026), mit ihnen die Stoffe der Hautverdeckung. */
    _kleiderZeigen(an) {
        if (this._kleiderAn === an) return;
        this._kleiderAn = an;
        for (const k of this.kleider) k.mesh.visible = an;
        for (const netz of Object.values(this.modell.hautStuecke || {})) netz.visible = an;
        Hautverdeckung.planen(this.modell);
    }

    _zeigen() {
        if (!this.aktiv) {
            this.aktiv = true;
            this.ansicht.neuZeigen();
        }
    }

    _bild() {
        Genesis9gelenke.takt(this.modell);
        this.ansicht.zeichnen();
        this.beiAenderung?.();
    }

    // ------------------------------------------------------------------ Bedienung (nach `vorbereiten`)

    umschalten() {
        this._zeigen();
        this.spielt = !(this.action.isScheduled() && !this.action.paused);
        if (!this.action.isScheduled()) { this.action.reset(); this.action.play(); }
        this.action.paused = !this.spielt;
        if (this.spielt) {
            this._uhr.getDelta();
            requestAnimationFrame(() => this._takt());
        }
        this._bild();
    }

    _takt() {
        if (!this.spielt || !this.action) return;
        requestAnimationFrame(() => this._takt());
        this._pruefen();
        this.mixer.update(this._uhr.getDelta());
        this._bild();
    }

    /** Stopp: Bewegung aus, zurück an den Anfang, das Feld zeigt wieder die Figur in der Haltung der KI. */
    stoppen() {
        this.spielt = false;
        this.action?.stop();
        this.modell?.skelett?.skeleton?.pose();
        if (this.aktiv) {
            this.aktiv = false;
            this.ansicht.neuZeigen();
        }
        this.beiAenderung?.();
    }

    /** An eine Stelle (Sekunden), pausiert. */
    stellen(zeit) {
        this._zeigen();
        this.spielt = false;
        if (!this.action.isScheduled()) { this.action.reset(); this.action.play(); }
        this.action.paused = true;
        this.action.time = Math.min(Math.max(zeit, 0), Math.max(this.dauer - 1e-4, 0));
        this.mixer.update(0);
        this._bild();
    }

    springen(ende) { this.stellen(ende ? this.dauer : 0); }

    bild(richtung) { this.stellen((this.action.isScheduled() ? this.action.time : 0) + richtung / this.fps); }

    /** Eine neue Standardanimation: die alte Bewegung fällt weg; lief sie, läuft die neue gleich an (`Mesh3daifigurbewegungsleiste`). */
    wahlSetzen(wahl) {
        if (wahl === this.wahl) return false;
        const lief = this.spielt;
        this.wahl = wahl;
        this.spielt = false;
        this.mixer?.stopAllAction();
        this.clip = null;
        this.mixer = null;
        this.action = null;
        this._wurzel = null;
        return lief;
    }

    /** Neue Probe, neuer Weg, anderes Geschlecht: alles weg, das Feld zeigt die stille Figur. */
    verwerfen() {
        this._lauf++;
        this.spielt = false;
        this.mixer?.stopAllAction();
        for (const k of this.kleider) k.mesh.geometry.dispose();
        this.kleider = [];
        this.modell?.dispose?.();
        this.modell = null;
        this.clip = null;
        this.mixer = null;
        this.action = null;
        this._schluessel = null;
        this._q = null;
        this._clipWahl = null;
        this._wurzel = null;
        this.rahmenMm = null;
        if (this.aktiv) {
            this.aktiv = false;
            this.ansicht.neuZeigen();
        }
        this.beiAenderung?.();
    }
}
