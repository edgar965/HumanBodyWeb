import * as THREE from 'three';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleidermalen — von Hand auf das Modell der Runde malen (01.10.2026; Blenders „Texture Paint").
 *
 * Knopf „Malen" in der Schalterleiste der Bühne: solange er leuchtet, ist das Drehen der Ansicht aus, und jeder Zug mit
 * gedrückter Maus über das Modell der letzten Runde (`Engine2d3dKleiderbuehnenmodell.gruppe`) wird ein Strich. Je Bildpunkt des
 * Zugs ein Raycast: Treffer auf einem Knoten `<art>__<sorte>__<n>_g<k>__<slug>` (GLB je Materialgruppe,
 * `Kleidermodellglb`) liefert `uv` in glTF-Konvention und die Gruppe. Gemalt wird SOFORT in eine Kopie der Textur des
 * Knotens (CanvasTexture — dieselbe Rechnung wie der Server: Kreis mit Radius in Texeln um (u·B, v·H)), beim Loslassen
 * geht der Strich an `POST …/malen/` (`G9kleidpinsel`), der ihn in die Decal-Schicht des Stücks legt und den Regler im
 * Modell stellt; die nächste Runde baut damit. Farbe, Radius und Schichtname stehen neben dem Knopf.
 */
export class Engine2d3dKleidermalen {

    static RADIUS_TEXEL = 12;
    static HOECHSTENS = 4000;

    constructor(seite, buehne, buehnenmodell) {
        this.seite = seite;
        this.buehne = buehne;
        this.buehnenmodell = buehnenmodell;
        this.knopf = document.getElementById('buehne-malen');
        this.felder = document.getElementById('buehne-malen-felder');
        if (!this.knopf || !buehne.canvas) return;
        this.an = false;
        this.strich = null;
        this.raycaster = new THREE.Raycaster();
        this.zeiger = new THREE.Vector2();
        this.leinwaende = new Map();
        this.knopf.addEventListener('click', () => this.umschalten());
        const leinwand = buehne.canvas;
        leinwand.addEventListener('pointerdown', e => this._ab(e));
        leinwand.addEventListener('pointermove', e => this._zug(e));
        window.addEventListener('pointerup', () => this._auf());
    }

    umschalten() {
        if (!this.an && this.seite.formen?.an) this.seite.formen.umschalten();
        this.an = !this.an;
        this.knopf.classList.toggle('active', this.an);
        if (this.felder) this.felder.hidden = !this.an;
        this.buehne.steuerung.enabled = !this.an;
        if (this.an && !this.buehnenmodell.an) this.buehnenmodell.umschalten();
        this.buehne._melden(this.an ? 'Malen: mit gedrückter Maus über das Modell der Runde ziehen' : '');
    }

    _einstellungen() {
        const f = feld => this.felder?.querySelector(`[data-feld="${feld}"]`);
        return {
            farbe: f('farbe')?.value || '#ff2020',
            radius: parseFloat(f('radius')?.value) || Engine2d3dKleidermalen.RADIUS_TEXEL,
            name: (f('name')?.value || 'pinsel').trim().toLowerCase() || 'pinsel',
        };
    }

    _treffer(e) {
        const gruppe = this.buehnenmodell.gruppe;
        if (!gruppe) return null;
        const r = this.buehne.canvas.getBoundingClientRect();
        this.zeiger.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
        this.raycaster.setFromCamera(this.zeiger, this.buehne.kamera);
        const netze = [];
        gruppe.traverse(t => { if (t.isMesh && t.visible && /_g\d+__/.test(t.name)) netze.push(t); });
        const treffer = this.raycaster.intersectObjects(netze, false);
        if (!treffer.length || !treffer[0].uv) return null;
        return treffer[0];
    }

    /** `haar__basic_hair__2_g0__hair01` → {art, sorte, slug}. */
    static zerlegen(name) {
        const m = /^(\w+?)__(.+)__(\d+)_g(\d+)__(.+)$/.exec(name || '');
        return m ? { art: m[1], sorte: m[2], slug: m[5] } : null;
    }

    _ab(e) {
        if (!this.an || e.button !== 0) return;
        const t = this._treffer(e);
        const teil = t && Engine2d3dKleidermalen.zerlegen(t.object.name);
        if (!teil || teil.art === 'koerper') return;
        this.strich = { teil, netz: t.object, punkte: [], ...this._einstellungen() };
        this._malen(t);
    }

    _zug(e) {
        if (!this.strich) return;
        const t = this._treffer(e);
        if (!t || t.object !== this.strich.netz) return;
        this._malen(t);
    }

    /** Ein Punkt des Strichs: sofort auf die Leinwand des Knotens, dazu in die Liste für den Server. */
    _malen(t) {
        const s = this.strich;
        if (s.punkte.length >= Engine2d3dKleidermalen.HOECHSTENS) return;
        s.punkte.push({ gruppe: s.teil.slug, u: t.uv.x, v: t.uv.y });
        const leinwand = this._leinwand(s.netz);
        if (!leinwand) return;
        const ctx = leinwand.canvas.getContext('2d');
        const r = s.radius * leinwand.canvas.width / 1024;
        ctx.fillStyle = s.farbe;
        ctx.beginPath();
        ctx.arc(t.uv.x * leinwand.canvas.width, t.uv.y * leinwand.canvas.height, r, 0, Math.PI * 2);
        ctx.fill();
        leinwand.textur.needsUpdate = true;
    }

    /** Die Textur des Knotens als Leinwand — beim ersten Strich aus der vorhandenen `map` kopiert (oder einfarbig). */
    _leinwand(netz) {
        if (this.leinwaende.has(netz.uuid)) return this.leinwaende.get(netz.uuid);
        const material = [].concat(netz.material)[0];
        if (!material) return null;
        const canvas = document.createElement('canvas');
        const bild = material.map?.image;
        canvas.width = bild?.width || 1024;
        canvas.height = bild?.height || 1024;
        const ctx = canvas.getContext('2d');
        if (bild) {
            ctx.drawImage(bild, 0, 0, canvas.width, canvas.height);
        } else {
            ctx.fillStyle = `#${material.color?.getHexString?.() || '888888'}`;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            material.color?.set?.(0xffffff);
        }
        const textur = new THREE.CanvasTexture(canvas);
        textur.flipY = material.map ? material.map.flipY : false;
        textur.colorSpace = THREE.SRGBColorSpace;
        material.map = textur;
        material.needsUpdate = true;
        const eintrag = { canvas, textur };
        this.leinwaende.set(netz.uuid, eintrag);
        return eintrag;
    }

    async _auf() {
        const s = this.strich;
        this.strich = null;
        if (!s || !s.punkte.length) return;
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('malen/'), {
                kennung: s.teil.sorte, art: s.teil.art, name: s.name, farbe: s.farbe, radius: s.radius,
                striche: s.punkte,
            });
            if (antwort.error) throw new Error(antwort.error);
            this.buehne._melden(`Gemalt: ${s.punkte.length} Punkte auf ${s.teil.sorte} (${antwort.regler}) — wirkt ab der nächsten Runde`);
        } catch (fehler) {
            this.buehne._melden(`Malen nicht gespeichert: ${fehler.daten?.error || fehler.message}`);
        }
    }
}
