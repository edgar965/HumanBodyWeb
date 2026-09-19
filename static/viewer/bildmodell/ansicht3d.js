import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Texturauflage } from './texturauflage.js';

/**
 * Ansicht3d — das Ergebnis als Genesis-9-Figur im Browser.
 *
 * Dieselbe Klasse wie Szene und Studio (`Genesis9Modell`, Käfig sofort,
 * feine Stufe nachgeladen), auf einer eigenen kleinen Bühne: Kamera auf die
 * Figurhöhe, Orbit, Lichter an der Kamera. Neu gebaut, sobald sich die Regler des
 * Ergebnisses ändern (`ergebnisStand`). Ohne WebGL bleibt der Hinweistext.
 * Ein Testfall (`Testfallansicht`) hängt die Referenzfigur dazu und schaltet
 * mit `umschalten(an)` zwischen Ergebnis und Referenz um — nur eine ist sichtbar.
 */
export class Ansicht3d {

    constructor(auftrag) {
        this.auftrag = auftrag;
        this.canvas = document.getElementById('ansicht3d');
        this.text = document.getElementById('ansicht3d-text');
        this.modell = null;
        this.referenzModell = null;
        this.referenzAn = false;
        this.auflage = new Texturauflage(auftrag);
        this._stand = null;
        this._laeuft = false;
        if (!this.canvas) return;
        try { this._buehne(); } catch (fehler) { this._melden(`Keine 3D-Ansicht: ${fehler.message}`); return; }
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    _melden(text) { if (this.text) this.text.textContent = text; }

    // ------------------------------------------------------ Referenz (Testfall)

    /** Die Referenzfigur eines Testfalls — sie liegt schon in der Szene. */
    referenz(modell) { this.referenzModell = modell; this._sichtbarkeit(); }

    /** `an`: die Referenz zeigen, sonst das Ergebnis. */
    umschalten(an) { this.referenzAn = !!an; this._sichtbarkeit(); }

    _sichtbarkeit() {
        const referenz = this.referenzAn && !!this.referenzModell;
        if (this.modell) this.modell.group.visible = !referenz;
        if (this.referenzModell) this.referenzModell.group.visible = referenz;
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
        const stand = this.auftrag.ergebnisStand() + '|' + (((z.optionen || {}).person || {}).haar || '');
        const regler = this.auftrag.stellung();
        if (!Object.keys(regler).length) { this._melden('Noch kein Ergebnis.'); return; }
        if (stand === this._stand || this._laeuft) return;
        this._stand = stand;
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
            const hoehe = neu.hoehe || 1.7;
            this.steuerung.target.set(0, hoehe * 0.52, 0);
            this.kamera.position.set(0, hoehe * 0.55, hoehe * 2.4);
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
        }
    }
}
