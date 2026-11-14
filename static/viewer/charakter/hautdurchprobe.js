/**
 * Hautdurchprobe — sieht man Haut, die unter dem Stoff liegen müsste? Gezählt im gezeichneten Bild, je Stück und Ansicht (12.11.2026).
 *
 * Anlass: Edgar, 12.11.2026: „bei olesia1 und spagat animation ist noch immer haut sichtbar bei den Posen, zwischen den Beinen, am T-Shirt, am
 * rechten Bein usw.“ Die `Kleidungsprobe` war grün (Haut p1 −2,7 / −4,8 mm: das Perzentil versteckt örtliche Stellen), der Modell-Check misst
 * die Kleidung ohne den Schub der Hautbindung. Hier zählt das Bild, wie die Seite es zeichnet — Hauteinzug, Hautbindung, Häutung, Maske.
 *
 * DIE REGEL: Zwei Bilder mit dem Renderer der Seite, je Ansicht (vorn, hinten, links, rechts):
 *   A  die ganze Figur; Körperpunkte, die die Hautmaske als verdeckt führt (`geometry.userData.hautVerdeckt`), rot, alle anderen schwarz, jedes Stück
 *      in seiner Farbe;
 *   B  nur die Stücke der Art Kleidung, je Stück eine Farbe, nur Vorderseiten (sonst zählte die Innenseite des Rückens im Kragen).
 * Ein Pixel zählt, wenn A rot ist und B dort ein Stück zeigt: verdeckte Haut steht vor dem Stoff. Freie Haut (Hals, Arme ohne Ärmel) ist schwarz und
 * zählt nicht, auch wenn sie vor einem Stück liegt. Die Materialien der Probe übernehmen die lageverändernden Eingriffe des Netzes
 * (`Gezeichneterpunkt.eingriffe`) und die Art der Häutung (`DQ_MISCH`, `dqhaut.js`).
 *
 *     await __hautdurchprobe.laufen({ bilder: [0, 51, 90] })   // Animation geladen; ohne `bilder` das jetzige Bild
 *     // → { bilder: [{ bild, px: {gesamt, je_stueck: {name: px}, je_ansicht: {vorn: px …}} }], px_max, ok }
 *
 * Grenze `PX_MAX` je Bild und Ansicht bei 512 × 1024: gesetzt, nicht geeicht.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { Gezeichneterpunkt } from '../gemeinsam/gezeichneterpunkt.js';

export class Hautdurchprobe {

    static BREITE = 512;
    static HOEHE = 1024;
    static PX_MAX = 20;
    static ANSICHTEN = { vorn: 0, links: Math.PI / 2, hinten: Math.PI, rechts: -Math.PI / 2 };

    static async laufen({ inst = null, bilder = null, ansichten = null } = {}) {
        const figur = inst || state.characters.get(state.selectedCharacterId) || [...state.characters.values()][0];
        if (!figur?.bodyMesh) throw new Error('keine Figur');
        const renderer = window.__auswahlaura?._composer?.renderer;
        if (!renderer) throw new Error('kein Renderer der Seite');
        const aus = [];
        for (const bild of bilder || [null]) {
            if (bild !== null) {
                window.__animation.stellen(bild);
                for (let k = 0; k < 4; k++) await new Promise((r) => requestAnimationFrame(r));   // Szenenschleife: Gelenkkorrekturen, Körperlage
            }
            aus.push({ bild, px: Hautdurchprobe.zaehlen(renderer, figur, ansichten || Object.keys(Hautdurchprobe.ANSICHTEN)) });
        }
        const px_max = Math.max(0, ...aus.flatMap((b) => Object.values(b.px.je_ansicht)));
        return { bilder: aus, px_max, ok: px_max <= Hautdurchprobe.PX_MAX };
    }

    /** Ein Bild der Figur: je Ansicht die Pixel verdeckter Haut vor einem Stück. */
    static zaehlen(renderer, figur, ansichten) {
        const H = Hautdurchprobe, koerper = figur.bodyMesh;
        const stuecke = Object.entries(figur.clothMeshes || {}).filter(([, n]) => n?.visible !== false && n.userData?.art === 'kleidung' && !n.userData?.ersetzt?.length);
        const farbe = new Map(stuecke.map(([s], i) => [s, i + 1]));
        figur.group.updateMatrixWorld(true);
        const kiste = new THREE.Box3().setFromObject(koerper, true);
        const mitte = kiste.getCenter(new THREE.Vector3()), groesse = kiste.getSize(new THREE.Vector3());
        const halb = 0.525 * Math.max(groesse.y, 2 * Math.max(groesse.x, groesse.z));   // gespreizte Beine passen hinein
        const kamera = new THREE.OrthographicCamera(-halb / 2, halb / 2, halb, -halb, 0.01, 20);
        const ziel = new THREE.WebGLRenderTarget(H.BREITE, H.HOEHE);
        const lesenA = new Uint8Array(4 * H.BREITE * H.HOEHE), lesenB = new Uint8Array(4 * H.BREITE * H.HOEHE);
        const zustand = H._vorbereiten(figur, koerper, stuecke, farbe);
        const je_stueck = {}, je_ansicht = {}, luecke = {};
        let gesamt = 0;
        try {
            for (const name of ansichten) {
                const w = H.ANSICHTEN[name];
                kamera.position.set(mitte.x + 5 * Math.sin(w), mitte.y, mitte.z + 5 * Math.cos(w));
                kamera.lookAt(mitte);
                kamera.updateMatrixWorld(true);
                H._bild(renderer, ziel, kamera, zustand, 'A', lesenA);
                H._bild(renderer, ziel, kamera, zustand, 'B', lesenB);
                let n = 0, frei = 0;
                const treffer = H.ablage ? new Uint8Array(lesenA.length / 4) : null;
                for (let p = 0; p < lesenA.length; p += 4) {
                    if (!(lesenA[p] > 200 && lesenA[p + 1] < 50 && lesenA[p + 2] < 50)) continue;
                    const k = lesenB[p + 1];
                    if (!k) frei++;                                     // verdeckte Haut sichtbar, ohne Stoff dahinter (Lücke zwischen zwei Stücken, Blick in den Ärmel)
                    if (!k) continue;
                    n++;
                    if (treffer) treffer[p / 4] = 1;
                    const s = stuecke[k - 1]?.[0] || '?';
                    je_stueck[s] = (je_stueck[s] || 0) + 1;
                }
                je_ansicht[name] = n;
                luecke[name] = frei;
                gesamt += n;
                if (treffer) H.ablage.push({ name, A: lesenA.slice(), B: lesenB.slice(), treffer });
            }
        } finally {
            H._zurueck(zustand);
            ziel.dispose();
        }
        return { gesamt, je_stueck, je_ansicht, luecke };
    }

    /** Probe-Materialien: Körper mit Farbe je Punkt (rot = verdeckt), Stücke mit ihrer Nummer im Grünkanal; dieselben Eingriffe und dieselbe Häutung wie gezeichnet. */
    static _vorbereiten(figur, koerper, stuecke, farbe) {
        const geo = koerper.geometry, n = geo.attributes.position.count, maske = geo.userData.hautVerdeckt;
        const farben = new Float32Array(3 * n);
        for (let i = 0; i < n; i++) if (maske?.[i]) farben[3 * i] = 1;
        const vorher = geo.getAttribute('color');
        geo.setAttribute('color', new THREE.BufferAttribute(farben, 3));
        const mat = (quelle, eigen) => {
            const m = Gezeichneterpunkt.eingriffe(Array.isArray(quelle) ? quelle[0] : quelle, eigen);
            const dq = (Array.isArray(quelle) ? quelle[0] : quelle)?.defines?.DQ_MISCH;
            if (dq) m.defines = { ...(m.defines || {}), DQ_MISCH: dq };
            return m;
        };
        const koerperMat = mat(koerper.material, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide }));
        const stueckA = new Map(), stueckB = new Map();
        for (const [s, netz] of stuecke) {
            const g = farbe.get(s) / 255;
            stueckA.set(netz, mat(netz.material, new THREE.MeshBasicMaterial({ color: new THREE.Color(0, g, 0.5), side: THREE.DoubleSide })));
            stueckB.set(netz, mat(netz.material, new THREE.MeshBasicMaterial({ color: new THREE.Color(0, g, 0.5), side: THREE.FrontSide })));
        }
        for (const m of [koerperMat, ...stueckA.values(), ...stueckB.values()]) m.toneMapped = false;   // ins Ziel ohne Tonung: die Werte bleiben roh
        const sichtbar = new Map();
        state.scene.traverse((o) => { if (o.isMesh || o.isPoints || o.isLine || o.isSprite) sichtbar.set(o, o.visible); });
        const material = new Map([...sichtbar.keys()].map((o) => [o, o.material]));
        return { figur, koerper, geo, vorher, koerperMat, stueckA, stueckB, sichtbar, material, hintergrund: state.scene.background };
    }

    static _bild(renderer, ziel, kamera, z, art, lesen) {
        for (const o of z.sichtbar.keys()) o.visible = false;
        if (art === 'A') {
            z.koerper.visible = true; z.koerper.material = z.koerperMat;
            for (const [netz, m] of z.stueckA) { netz.visible = true; netz.material = m; }
        } else {
            for (const [netz, m] of z.stueckB) { netz.visible = true; netz.material = m; }
        }
        state.scene.background = null;
        const zielAlt = renderer.getRenderTarget(), farbeAlt = renderer.getClearColor(new THREE.Color()), alphaAlt = renderer.getClearAlpha();
        renderer.setRenderTarget(ziel);
        renderer.setClearColor(0x000000, 1);
        renderer.clear();
        renderer.render(state.scene, kamera);
        renderer.readRenderTargetPixels(ziel, 0, 0, Hautdurchprobe.BREITE, Hautdurchprobe.HOEHE, lesen);
        renderer.setRenderTarget(zielAlt);
        renderer.setClearColor(farbeAlt, alphaAlt);
    }

    /** Zum Ansehen: `Hautdurchprobe.ablage = []` vor `laufen`, danach `zeigen()` — die Bilder A nebeneinander über der Seite, gezählte Pixel gelb, Stücke grün. */
    static ablage = null;

    static zeigen() {
        const H = Hautdurchprobe, liste = H.ablage || [];
        document.getElementById('hautdurchprobe-bild')?.remove();
        const leinwand = document.createElement('canvas');
        leinwand.id = 'hautdurchprobe-bild';
        leinwand.width = H.BREITE * liste.length; leinwand.height = H.HOEHE;
        Object.assign(leinwand.style, { position: 'fixed', left: '0', top: '0', zIndex: 99999, height: '100vh', background: '#000' });
        const c = leinwand.getContext('2d'), bild = c.createImageData(leinwand.width, leinwand.height);
        liste.forEach((e, k) => {
            for (let y = 0; y < H.HOEHE; y++) for (let x = 0; x < H.BREITE; x++) {
                const q = 4 * ((H.HOEHE - 1 - y) * H.BREITE + x), z = 4 * (y * leinwand.width + k * H.BREITE + x);
                const t = e.treffer[q / 4], rot = e.A[q] > 200 && e.A[q + 1] < 50, stoff = e.A[q + 2] > 100;
                bild.data.set(t ? [255, 255, 0, 255] : rot ? [150, 40, 40, 255] : stoff ? [40, 110, 60, 255] : [e.A[q] * 0.6, e.A[q] * 0.6, e.A[q] * 0.6, 255], z);
            }
        });
        c.putImageData(bild, 0, 0);
        document.body.appendChild(leinwand);
        return liste.map((e) => e.name);
    }

    static _zurueck(z) {
        for (const [o, v] of z.sichtbar) o.visible = v;
        for (const [o, m] of z.material) o.material = m;
        state.scene.background = z.hintergrund;
        if (z.vorher) z.geo.setAttribute('color', z.vorher); else z.geo.deleteAttribute('color');
        for (const m of [z.koerperMat, ...z.stueckA.values(), ...z.stueckB.values()]) m.dispose();
    }
}

window.__hautdurchprobe = Hautdurchprobe;
