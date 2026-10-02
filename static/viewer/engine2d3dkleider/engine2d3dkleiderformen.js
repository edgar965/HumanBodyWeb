import * as THREE from 'three';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderformen — von Hand auf der FORM des Modells modellieren (01.10.2026; Blenders Sculpt-Pinsel).
 *
 * Knopf „Formen" neben „Malen": solange er leuchtet, ist das Drehen der Ansicht aus, und jeder Zug mit gedrückter Maus
 * über ein Stück, eine Frisur oder den Körper wird ein Strich. Je Bildpunkt des Zugs ein Raycast; ein neuer Strichpunkt
 * erst nach einem Viertel des Radius (wie Blenders Abstand der Tupfer). Die Bühne zeigt den Zug SOFORT (die Punkte des
 * getroffenen Teils werden verschoben — Ziehen, Drücken, Aufblasen, Greifen; Glätten und Flach erst nach der Runde),
 * beim Loslassen gehen die Strichpunkte in den Koordinaten der GLB an `POST …/formen/` (`G9formpinsel`): ein eigener
 * Morph am Käfig des Stücks bzw. des Körpers, der Regler steht danach im Modell — die nächste Runde baut damit, und
 * weil es ein Morph ist, läuft die Fotoprojektion auf der geformten Fläche.
 *
 * Knotennamen (Runden-GLB `Kleidermodellglb`, Standmodell `Standmodellglb`): `kleidung__<sorte>__<n>[_g<k>__<slug>|_flach]`,
 * `haar__…`, Körper `koerper__koerper__0…`; die Anhänge (`koerper_<x>__…`: Augen, Mund) formt der Pinsel nicht.
 */
export class Engine2d3dKleiderformen {

    static SCHRITT_M = 0.001;
    static HOECHSTENS = 4000;

    constructor(seite, buehne, buehnenmodell) {
        this.seite = seite;
        this.buehne = buehne;
        this.buehnenmodell = buehnenmodell;
        this.knopf = document.getElementById('buehne-formen');
        this.felder = document.getElementById('buehne-formen-felder');
        if (!this.knopf || !buehne.canvas) return;
        this.an = false;
        this.strich = null;
        this.raycaster = new THREE.Raycaster();
        this.zeiger = new THREE.Vector2();
        this.knopf.addEventListener('click', () => this.umschalten());
        const leinwand = buehne.canvas;
        leinwand.addEventListener('pointerdown', e => this._ab(e));
        leinwand.addEventListener('pointermove', e => this._zug(e));
        window.addEventListener('pointerup', () => this._auf());
    }

    umschalten() {
        if (!this.an && this.seite.malen?.an) this.seite.malen.umschalten();
        this.an = !this.an;
        this.knopf.classList.toggle('active', this.an);
        if (this.felder) this.felder.hidden = !this.an;
        this.buehne.steuerung.enabled = !this.an;
        if (this.an && !this.buehnenmodell.an) this.buehnenmodell.umschalten();
        this.buehne._melden(this.an ? 'Formen: mit gedrückter Maus über Stück, Haar oder Körper ziehen' : '');
    }

    _einstellungen() {
        const f = feld => this.felder?.querySelector(`[data-feld="${feld}"]`);
        return {
            modus: f('modus')?.value || 'ziehen',
            radius_cm: parseFloat(f('radius')?.value) || 4,
            staerke: parseFloat(f('staerke')?.value) || 1,
            name: (f('name')?.value || 'form').trim().toLowerCase() || 'form',
        };
    }

    /** Knotenname → {art, sorte, praefix} — null für Anhänge und Unbekanntes. */
    static zerlegen(name) {
        if (/^koerper__koerper__0/.test(name || '')) return { art: 'koerper', sorte: '', praefix: 'koerper__koerper__0' };
        const m = /^(kleidung|haar)__(.+?)__(\d+)(?:_g\d+__.+|_flach)?$/.exec(name || '');
        return m ? { art: m[1], sorte: m[2], praefix: `${m[1]}__${m[2]}__${m[3]}` } : null;
    }

    _treffer(e) {
        const gruppe = this.buehnenmodell.gruppe;
        if (!gruppe) return null;
        const r = this.buehne.canvas.getBoundingClientRect();
        this.zeiger.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
        this.raycaster.setFromCamera(this.zeiger, this.buehne.kamera);
        const netze = [];
        gruppe.traverse(t => { if (t.isMesh && t.visible && Engine2d3dKleiderformen.zerlegen(t.name)) netze.push(t); });
        const treffer = this.raycaster.intersectObjects(netze, false);
        return treffer.length && treffer[0].face ? treffer[0] : null;
    }

    /** Punkt und Normale eines Treffers in den Koordinaten der GLB (Wurzel `gruppe`). */
    _lokal(t) {
        const gruppe = this.buehnenmodell.gruppe;
        gruppe.updateMatrixWorld(true);
        const p = gruppe.worldToLocal(t.point.clone());
        const n = t.face.normal.clone().transformDirection(t.object.matrixWorld);
        const umkehr = new THREE.Matrix4().copy(gruppe.matrixWorld).invert();
        n.transformDirection(umkehr);
        if (n.dot(this.raycaster.ray.direction.clone().transformDirection(umkehr)) > 0) n.negate();
        return { p, n };
    }

    _ab(e) {
        if (!this.an || e.button !== 0) return;
        const t = this._treffer(e);
        const teil = t && Engine2d3dKleiderformen.zerlegen(t.object.name);
        if (!teil) return;
        const netze = [];
        this.buehnenmodell.gruppe.traverse(o => { if (o.isMesh && o.name.startsWith(teil.praefix)) netze.push(o); });
        const { p, n } = this._lokal(t);
        const ebene = new THREE.Plane().setFromNormalAndCoplanarPoint(
            this.buehne.kamera.getWorldDirection(new THREE.Vector3()).negate(), t.point);
        this.strich = { teil, netze, punkte: [], start: { p, n, welt: t.point.clone() }, ebene, zug: new THREE.Vector3(),
                        ...this._einstellungen() };
        this.strich.basis = new Map(netze.map(o => [o.uuid, o.geometry.attributes.position.array.slice()]));
        this._tupfer(p, n);
    }

    _zug(e) {
        const s = this.strich;
        if (!s) return;
        if (s.modus === 'greifen') {
            const r = this.buehne.canvas.getBoundingClientRect();
            this.zeiger.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
            this.raycaster.setFromCamera(this.zeiger, this.buehne.kamera);
            const q = this.raycaster.ray.intersectPlane(s.ebene, new THREE.Vector3());
            if (!q) return;
            s.zug = this.buehnenmodell.gruppe.worldToLocal(q).sub(s.start.p);
            this._greifen();
            return;
        }
        const t = this._treffer(e);
        if (!t || !s.netze.includes(t.object)) return;
        const { p, n } = this._lokal(t);
        const letzter = s.punkte[s.punkte.length - 1];
        if (letzter && p.distanceTo(new THREE.Vector3(...letzter.p)) < s.radius_cm / 400) return;
        this._tupfer(p, n);
    }

    _tupfer(p, n) {
        const s = this.strich;
        if (s.punkte.length >= Engine2d3dKleiderformen.HOECHSTENS) return;
        const t = { p: [p.x, p.y, p.z], n: [n.x, n.y, n.z] };
        s.punkte.push(t);
        if (['ziehen', 'druecken', 'aufblasen'].includes(s.modus)) this._tupfen(t);
    }

    /** Einen Tupfer in die Anzeige: die Punkte der getroffenen Netze um ihn verschieben (die Rechnung macht der Server,
     *  die Bühne zeigt nur, wohin es geht). Die Netzpunkte liegen in den Koordinaten der GLB wie die Tupfer. */
    _tupfen(t) {
        const s = this.strich;
        const radius = s.radius_cm / 100;
        const weg = s.staerke * Engine2d3dKleiderformen.SCHRITT_M * (s.modus === 'druecken' ? -1 : 1);
        for (const netz of s.netze) {
            const lage = netz.geometry.attributes.position;
            const a = lage.array;
            const normalen = netz.geometry.attributes.normal?.array;
            for (let i = 0; i < lage.count; i++) {
                const w = Engine2d3dKleiderformen.abfall(Math.hypot(a[3 * i] - t.p[0], a[3 * i + 1] - t.p[1], a[3 * i + 2] - t.p[2]), radius);
                if (w <= 0) continue;
                const r = s.modus === 'aufblasen' && normalen ? [normalen[3 * i], normalen[3 * i + 1], normalen[3 * i + 2]] : t.n;
                a[3 * i] += w * weg * r[0]; a[3 * i + 1] += w * weg * r[1]; a[3 * i + 2] += w * weg * r[2];
            }
            lage.needsUpdate = true;
        }
    }

    /** Greifen: der Bereich um den Startpunkt folgt dem Zug (von der Ausgangslage aus, nicht aufaddiert). */
    _greifen() {
        const s = this.strich;
        const radius = s.radius_cm / 100;
        for (const netz of s.netze) {
            const lage = netz.geometry.attributes.position;
            const basis = s.basis.get(netz.uuid);
            const a = lage.array;
            for (let i = 0; i < lage.count; i++) {
                const w = s.staerke * Engine2d3dKleiderformen.abfall(
                    Math.hypot(basis[3 * i] - s.start.p.x, basis[3 * i + 1] - s.start.p.y, basis[3 * i + 2] - s.start.p.z), radius);
                a[3 * i] = basis[3 * i] + w * s.zug.x;
                a[3 * i + 1] = basis[3 * i + 1] + w * s.zug.y;
                a[3 * i + 2] = basis[3 * i + 2] + w * s.zug.z;
            }
            lage.needsUpdate = true;
        }
    }

    static abfall(abstand, radius) {
        const t = Math.min(Math.max(1 - abstand / Math.max(radius, 1e-6), 0), 1);
        return t * t * (3 - 2 * t);
    }

    async _auf() {
        const s = this.strich;
        this.strich = null;
        if (!s) return;
        for (const netz of s.netze) { netz.geometry.computeVertexNormals(); netz.geometry.computeBoundingSphere(); }
        const striche = s.modus === 'greifen'
            ? [{ p: [s.start.p.x, s.start.p.y, s.start.p.z], n: [s.start.n.x, s.start.n.y, s.start.n.z],
                 d: [s.zug.x, s.zug.y, s.zug.z] }]
            : s.punkte;
        if (!striche.length) return;
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('formen/'), {
                kennung: s.teil.sorte, art: s.teil.art, name: s.name, modus: s.modus, radius_cm: s.radius_cm,
                staerke: s.staerke, striche,
            });
            if (antwort.error) throw new Error(antwort.error);
            const ziel = s.teil.art === 'koerper' ? 'Körper' : s.teil.sorte;
            this.buehne._melden(`Geformt (${s.modus}): ${striche.length} Strichpunkte auf ${ziel} — ${antwort.regler}, wirkt ab der nächsten Runde`
                + (antwort.anker ? '' : ' (ohne Anker der Runde: Lage der Grundfigur angenommen)'));
        } catch (fehler) {
            this.buehne._melden(`Formen nicht gespeichert: ${fehler.daten?.error || fehler.message}`);
        }
    }
}
