import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Texturauflage } from './texturauflage.js';
import { Zielkaefig } from './zielkaefig.js';

/**
 * Ansicht3d — das Ergebnis als Genesis-9-Figur im Browser.
 *
 * Dieselbe Klasse wie Szene und Studio (`Genesis9Modell`, Käfig sofort,
 * feine Stufe nachgeladen), auf einer eigenen kleinen Bühne: Kamera auf die
 * Figurhöhe, Orbit, Lichter an der Kamera. Neu gebaut, sobald sich die Regler des
 * Ergebnisses ändern (`ergebnisStand`). Ohne WebGL bleibt der Hinweistext.
 * Ein Testfall (`Testfallansicht`) hängt die Referenzfigur dazu und schaltet
 * mit `umschalten(an)` zwischen Ergebnis und Referenz um — nur eine ist sichtbar.
 *
 * ZIEL LIVE (20.09.2026, abends — Edgar: „3D links, 2D rechts … Wenn ich die
 * Regler ändere, dann ändert sich gleich das 3D Modell links"): in derselben
 * Szene liegt das Zielnetz als `Zielkaefig`; `zielSetzen(antwort, netz)` kommt
 * von der `Zielnetzlive` der Modellsicht nach jedem Pfeil und Schieber. Die
 * Wahl „Ziel (folgt den Pfeilen)" / „Modell (Ergebnis)" (`wasZeigen`) ist
 * beim Öffnen auf dem Ziel, sobald es eines gibt — das ist die Anzeige, die
 * den Reglern folgt; das Ergebnis mit Haut und Haar ist einen Klick entfernt.
 *
 * SMPL-X (GVHMR) je Bild (20.09.2026, Edgar: „ein SMPL mit GVHMR erzeuge und
 * ansehen kann, für jedes Bild"): ein zweiter `Zielkaefig` (`smplx`, bläulich)
 * mit dem Netz aus `gvhmr3d/<datei>/` (`gvhmrSetzen`, vom `Gvhmrknopf`); die
 * dritte Wahl „SMPL-X (GVHMR)" erscheint mit dem ersten Netz.
 */
export class Ansicht3d {

    /** localStorage-Schlüssel der Wahl Ziel/Modell. */
    static MERKER = 'bildmodell.ansicht3d.was';
    //: Kamera-Position/-Blick, job-übergreifend gemerkt (23.09.2026, Edgar: „im Ergebnis Modell
    //: rechts solltest du dir die Position des Modells merken") — wie bei `Kopfpipelineansicht`.
    static KAMERA_MERKER = 'bildmodell.ansicht3d.kamera';

    constructor(auftrag) {
        this.auftrag = auftrag;
        this.canvas = document.getElementById('ansicht3d');
        this.text = document.getElementById('ansicht3d-text');
        this.modell = null;
        this.referenzModell = null;
        this.referenzAn = false;
        this.kaefig = null;
        this.was = 'ziel';
        this.auflage = new Texturauflage(auftrag);
        this._stand = null;
        this._laeuft = false;
        this._kameraSteht = false;
        if (!this.canvas) return;
        try { this._buehne(); } catch (fehler) { this._melden(`Keine 3D-Ansicht: ${fehler.message}`); return; }
        this.kaefig = new Zielkaefig(this.szene);
        this.smplx = new Zielkaefig(this.szene);
        this.smplxDatei = null;
        this._schalter();
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    _melden(text) { if (this.text) this.text.textContent = text; }

    // -------------------------------------------------------- Ziel (live)

    /** Die Knöpfe über der Ansicht: Ziel/Modell, Gitter. */
    _schalter() {
        for (const r of document.querySelectorAll('input[name="ansicht3d-was"]')) {
            r.addEventListener('change', () => { if (r.checked) this.wasZeigen(r.value); });
        }
        document.getElementById('ansicht3d-gitter')?.addEventListener('change', e => {
            this.kaefig?.gitterZeigen(e.target.checked);
            this.smplx?.gitterZeigen(e.target.checked);
        });
    }

    /** `was`: `ziel` (folgt den Pfeilen), `modell` (Ergebnis mit Haut) oder `gvhmr` (SMPL-X eines Bildes).
     *  `merken`: die Wahl überlebt ein Neuladen (`MERKER`) — `gvhmr` nicht, das Netz ist dann weg. */
    wasZeigen(was, merken = true) {
        this.was = ['modell', 'gvhmr'].includes(was) ? was : 'ziel';
        for (const r of document.querySelectorAll('input[name="ansicht3d-was"]')) r.checked = r.value === this.was;
        this._sichtbarkeit();
        if (merken && this.was !== 'gvhmr') { try { localStorage.setItem(Ansicht3d.MERKER, this.was); } catch (e) { /* privat */ } }
    }

    /** Was beim Laden gezeigt wird: die gemerkte Wahl — sonst das Modell, sobald eine Fototextur
     *  da ist (Edgar, 21.09.2026: „keine neue Textur auf dem 3D Modell ganz oben" — die Seite stand
     *  auf „Ziel", dem Käfig ohne Haut), und der Käfig, wenn es noch keine gibt. */
    _anfangswahl(z) {
        let gemerkt = null;
        try { gemerkt = localStorage.getItem(Ansicht3d.MERKER); } catch (e) { /* privat */ }
        if (gemerkt === 'ziel' || gemerkt === 'modell') return gemerkt;
        return ((z.ergebnis || {}).fototextur || {}).kacheln ? 'modell' : 'ziel';
    }

    /** Das SMPL-X-Netz eines Bildes (`gvhmr3d/`): immer neu gebaut, bläulich, dann gezeigt. */
    gvhmrSetzen(antwort) {
        if (!this.smplx || !antwort || !antwort.punkte) return;
        this.smplx.netzSetzen(antwort);
        if (this.smplx.netz) this.smplx.netz.material.color.set(0xb9c6da);
        this.smplxDatei = antwort.datei || null;
        const wahl = document.getElementById('ansicht3d-gvhmr-wahl');
        if (wahl) { wahl.hidden = false; wahl.title = `SMPL-X aus GVHMR: ${this.smplxDatei || ''}`; }
        if (!this._kameraSteht && this.smplx.da) this._kameraAuf(this.smplx.hoehe);
        this._melden(`SMPL-X (GVHMR) aus ${this.smplxDatei || '?'}: ${(antwort.anzahl || 0).toLocaleString('de-DE')} Punkte, ${antwort.hoehe_cm || '?'} cm`);
        this.wasZeigen('gvhmr');
    }

    /** Eine Antwort von `Zielnetzlive`: Netz bauen oder Punkte tauschen; die erste stellt die Kamera. */
    zielSetzen(antwort, netz) {
        if (!this.kaefig || !antwort) return;
        this.kaefig.setzen(antwort, netz);
        if (!this._kameraSteht && this.kaefig.da) this._kameraAuf(this.kaefig.hoehe);
        this._sichtbarkeit();
    }

    _kameraAuf(hoehe) {
        hoehe = hoehe || 1.7;
        const gemerkt = this._kameraGemerkt();
        if (gemerkt) {
            this.kamera.position.set(gemerkt.px, gemerkt.py, gemerkt.pz);
            this.steuerung.target.set(gemerkt.tx, gemerkt.ty, gemerkt.tz);
        } else {
            this.steuerung.target.set(0, hoehe * 0.52, 0);
            this.kamera.position.set(0, hoehe * 0.55, hoehe * 2.4);
        }
        this._kameraSteht = true;
    }

    _kameraGemerkt() {
        try { return JSON.parse(localStorage.getItem(Ansicht3d.KAMERA_MERKER) || 'null'); }
        catch (fehler) { return null; }
    }

    _kameraSpeichern() {
        const p = this.kamera.position, t = this.steuerung.target;
        try {
            localStorage.setItem(Ansicht3d.KAMERA_MERKER, JSON.stringify(
                { px: p.x, py: p.y, pz: p.z, tx: t.x, ty: t.y, tz: t.z }));
        } catch (fehler) { /* privat */ }
    }

    /** Jede Änderung (Ziehen, Zoomen) 400 ms entprellt gemerkt, zusätzlich sofort bei
     *  `pointerup`/`wheel` auf der Leinwand (23.09.2026, wie `Kopfpipelineansicht` — direkt am
     *  DOM-Ereignis, falls OrbitControls' eigene Änderungserkennung einen Zug mal nicht zählt). */
    _kameraMerkenEinrichten() {
        this.canvas.addEventListener('pointerup', () => this._kameraSpeichern());
        this.canvas.addEventListener('wheel', () => {
            clearTimeout(this._kameraZeitstempel);
            this._kameraZeitstempel = setTimeout(() => this._kameraSpeichern(), 400);
        }, { passive: true });
        let zeitstempel = null;
        this.steuerung.addEventListener('change', () => {
            clearTimeout(zeitstempel);
            zeitstempel = setTimeout(() => this._kameraSpeichern(), 400);
        });
    }

    // ------------------------------------------------------ Referenz (Testfall)

    /** Die Referenzfigur eines Testfalls — sie liegt schon in der Szene. */
    referenz(modell) { this.referenzModell = modell; this._sichtbarkeit(); }

    /** `an`: die Referenz zeigen, sonst das Ergebnis. */
    umschalten(an) { this.referenzAn = !!an; this._sichtbarkeit(); }

    /** Genau eine Figur ist zu sehen: Referenz vor SMPL-X vor Ziel vor Modell — die Wahl nur, wenn da. */
    _sichtbarkeit() {
        const referenz = this.referenzAn && !!this.referenzModell;
        const gvhmr = !referenz && this.was === 'gvhmr' && !!(this.smplx && this.smplx.da);
        const ziel = !referenz && !gvhmr && this.was === 'ziel' && !!(this.kaefig && this.kaefig.da);
        if (this.modell) this.modell.group.visible = !referenz && !ziel && !gvhmr;
        if (this.referenzModell) this.referenzModell.group.visible = referenz;
        if (this.kaefig) this.kaefig.visible = ziel;
        if (this.smplx) this.smplx.visible = gvhmr;
    }

    _buehne() {
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.szene = new THREE.Scene();
        this.kamera = new THREE.PerspectiveCamera(30, 1, 0.05, 50);
        this.kamera.position.set(0, 1.0, 4.2);
        this.steuerung = new OrbitControls(this.kamera, this.canvas);
        this.steuerung.target.set(0, 0.9, 0);
        this.steuerung.enableDamping = true;
        this._kameraMerkenEinrichten();
        this._lichter();
        const boden = new THREE.GridHelper(2, 10, 0x445566, 0x2a3340);
        this.szene.add(boden);
        this._groesse();
        window.addEventListener('resize', () => this._groesse());
        const lauf = () => { this.steuerung.update(); this.renderer.render(this.szene, this.kamera); requestAnimationFrame(lauf); };
        requestAnimationFrame(lauf);
    }

    /**
     * Gleichmäßig von allen Seiten: das Hauptlicht hängt an der KAMERA und
     * dreht mit ihr, die dem Betrachter zugewandte Seite ist immer beleuchtet
     * (ein festes Licht von vorn rechts ließ die linke Rückseite im Dunkeln,
     * und die Fototextur trägt den Schatten der Fotos schon in sich). Dazu ein
     * neutraler Himmel/Boden statt des blauen Bodens, der die Haut kühl färbte.
     */
    _lichter() {
        this.szene.add(new THREE.HemisphereLight(0xffffff, 0xc8c2ba, 1.3));
        const haupt = new THREE.DirectionalLight(0xffffff, 1.0);
        haupt.position.set(1, 1.5, 2);
        const fuell = new THREE.DirectionalLight(0xffffff, 0.35);
        fuell.position.set(-2, -0.5, 1.5);
        this.kamera.add(haupt, fuell);
        this.szene.add(this.kamera);
    }

    _groesse() {
        const b = this.canvas.clientWidth || 480, h = this.canvas.clientHeight || 560;
        this.renderer.setSize(b, h, false);
        this.kamera.aspect = b / h;
        this.kamera.updateProjectionMatrix();
    }

    /**
     * Die Daz-Haut auf den gemessenen Hautton tönen: je Material mit Albedo der
     * Faktor Fototon / mittlerer Albedoton (beide linear), geklemmt 0,25..2,5.
     * Ohne gewählte Bilder bleibt die Haut, wie Daz sie liefert.
     */
    hauttonAnwenden(textur, versuch = 0) {
        const ton = textur && textur.hautton ? textur.hautton.join(',') : '';
        if (!this.modell || !this.modell.bodyMesh || ton === this._hautton) return;
        // Mit gebackener Fototextur trägt die Kachel den Ton schon (`G9texturbacken.getoent`).
        if (this.auflage && this.auflage.aktiv) { this._hautton = ton; return; }
        const lin = v => { const c = v / 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
        const materialien = Array.isArray(this.modell.bodyMesh.material)
            ? this.modell.bodyMesh.material : [this.modell.bodyMesh.material];
        let getoent = 0;
        for (const m of materialien) {
            if (!m || !m.map) continue;
            if (!ton) { m.color.setRGB(1, 1, 1); m.needsUpdate = true; getoent += 1; continue; }
            const ref = Ansicht3d.mittelton(m.map);
            if (!ref) continue;
            const f = textur.hautton.map((v, i) => Math.min(2.5, Math.max(0.25, lin(v) / Math.max(1e-3, lin(ref[i])))));
            m.color.setRGB(f[0], f[1], f[2]);
            m.needsUpdate = true;
            getoent += 1;
        }
        // Die Albedo kommt aus dem Texturvorrat erst nach dem Netz (8K-Kacheln: Sekunden) — bis 30 s nachfassen.
        if (getoent) this._hautton = ton;
        else if (versuch < 20) setTimeout(() => this.hauttonAnwenden(textur, versuch + 1), 1500);
    }

    /** Mittlerer sRGB-Ton eines Texturbildes (16 × 16 verkleinert), einmal je Textur gemerkt. */
    static mittelton(textur) {
        if (textur.userData && textur.userData.mittelton) return textur.userData.mittelton;
        const bild = textur.image;
        if (!bild || !bild.width) return null;
        try {
            const c = document.createElement('canvas');
            c.width = 16; c.height = 16;
            const ctx = c.getContext('2d');
            ctx.drawImage(bild, 0, 0, 16, 16);
            const d = ctx.getImageData(0, 0, 16, 16).data;
            const summe = [0, 0, 0];
            let n = 0;
            for (let i = 0; i < d.length; i += 4) {
                if (d[i + 3] < 128) continue;
                summe[0] += d[i]; summe[1] += d[i + 1]; summe[2] += d[i + 2]; n += 1;
            }
            if (!n) return null;
            textur.userData = textur.userData || {};
            textur.userData.mittelton = summe.map(v => v / n);
            return textur.userData.mittelton;
        } catch (fehler) {
            return null;
        }
    }

    async zeigen(z) {
        this.hauttonAnwenden(z.textur);
        // Die Fotokacheln (Stufe 2) bei jedem Stand — auch wenn das Netz schon steht.
        if (this.modell) this.auflage.anwenden(this.modell, (z.ergebnis || {}).fototextur);
        // Erste Wahl beim Laden; eine NEU gebackene Textur schaltet auf „Modell" — sonst sieht
        // man sie nicht (Käfig „Ziel" hat keine Haut).
        const texturstand = ((z.ergebnis || {}).fototextur || {}).stand || null;
        if (this._texturstand === undefined) this.wasZeigen(this._anfangswahl(z), false);
        else if (texturstand && texturstand !== this._texturstand && this.was !== 'gvhmr') this.wasZeigen('modell');
        this._texturstand = texturstand;
        const stand = this.auftrag.ergebnisStand() + '|' + (((z.optionen || {}).person || {}).haar || '');
        const regler = this.stellungGeber ? this.stellungGeber() : this.auftrag.stellung();
        if (!Object.keys(regler).length) { this._melden('Noch kein Ergebnis.'); return; }
        if (stand === this._stand || this._laeuft) return;
        this._stand = stand;
        await this._bauen(regler, z);
    }

    /**
     * Die Figur mit dieser Reglerstellung neu bauen — vom `Reglerfeld` je Schieberzug
     * (Ebene 3, 21.09.2026). Entprellt; läuft gerade ein Bau, wird der Wunsch gemerkt und
     * danach EINMAL gebaut (kein Stau, keine überholten Antworten).
     */
    reglerSetzen(regler) {
        this._eigen = regler;
        if (this._reglerWarte) clearTimeout(this._reglerWarte);
        this._reglerWarte = setTimeout(async () => {
            this._reglerWarte = null;
            if (this._laeuft) { this._nochmal = true; return; }
            await this._bauen(this._stellung(regler), this.auftrag.zustand);
        }, 150);
    }

    /** Die Stellung für einen Bau: vom `Reglerfeld` (`stellungGeber`), sonst die übergebene/Fit. */
    _stellung(sonst) {
        return this.stellungGeber ? this.stellungGeber() : (sonst || this.auftrag.stellung());
    }

    async _bauen(regler, z) {
        this._laeuft = true;
        this._melden('Figur wird gebaut …');
        try {
            const haar = ((z.optionen || {}).person || {}).haar;
            const kleidung = haar ? { [haar]: {} } : {};
            const neu = new Genesis9Modell('bildmodell', { figur: 'basis', regler, presetName: z.name, kleidung });
            await neu.bauen();
            if (this.modell) { this.szene.remove(this.modell.group); this.modell.dispose?.(); }
            this.modell = neu;
            this.szene.add(neu.group);
            if (!this._kameraSteht) this._kameraAuf(neu.hoehe);
            this._melden(`${z.name}: ${Object.keys(regler).length} Regler, ${(neu.browserpunkte || 0).toLocaleString('de-DE')} Punkte`);
            this._hautton = null;
            this.hauttonAnwenden(z.textur);
            this.auflage.anwenden(neu, (z.ergebnis || {}).fototextur);
            this._sichtbarkeit();
        } catch (fehler) {
            this._melden(`Figur nicht gebaut: ${fehler.message}`);
            this._stand = null;
        } finally {
            this._laeuft = false;
            if (this._nochmal) { this._nochmal = false; await this._bauen(this._stellung(this._eigen || regler), this.auftrag.zustand); }
        }
    }
}
