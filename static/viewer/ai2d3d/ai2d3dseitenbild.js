/**
 * Ai2d3dseitenbild — die Figur, wie DIESE SEITE sie zeichnet, aus der Kamera jedes Fotos rendern und an den Server geben (24.10.2026; Edgar: „unverändert schlecht. Passe deine
 * testmethoden an, das musst du Doch selber herausfinden, dass die nicht übereinstimmen“).
 *
 * Die Abnahme (`koerperpruefung_lauf.py --seite`) misst diese Bilder mit Sapiens2 und ViTPose gegen die Fotos. Bis dahin maß sie einen eigenen Python-Renderer, der weder das
 * Anatomie-Stück noch die Hautverdeckung der Seite kannte — dort Shorts bis zum Saum, hier ein Genital unter zu kurzen Shorts.
 *
 * Kamera = die Lochkamera der Einpassung (`Koerperprojektion`): x′ = R (X − mitte), Bild = f · (x′, −y′) / (Z − z′) + t mit Z = f / s. Die Figur der Seite steht im selben Rahmen wie die
 * gehäutete Figur der Einpassung (gemessen 24.10.2026 an EdgarTrip: Hülle −0,396…0,396 / −0,094…1,739 / −0,166…0,185 m auf beiden Seiten). Die Kamera steht also bei
 * mitte + Rᵀ (0, 0, Z), ihre Achsen sind die Zeilen von R, die Projektion trägt Brennweite und Bildmitte des Fotos.
 * Zwei Durchgänge wie `Ai2d3dvergleich`: auf Weiß (das Bild) und auf Grün (die Maske) → ein RGBA-PNG, Alpha = Figur.
 *
 *     await window.__ai2d3d.seitenbilder()      // → [{nr, bytes}], legt <Job>/abnahme/seite_<nr>.png ab
 */
import * as THREE from 'three';
import { Mesh3daizeichenflaeche } from '../mesh3dai/mesh3daizeichenflaeche.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Ai2d3dseitenbild {
    /** Höhe des Renderings in Pixeln (die Abnahme skaliert auf die Fotogröße hoch; 1.600 px ≈ 1,2 mm je Pixel bei 1,85 m Körpergröße) */
    static HOEHE = 1600;
    static SCHLUESSEL = [0, 255, 0];
    static SCHWELLE_SCHLUESSEL = 60;
    static NAH = 0.05;
    static FERN = 50;

    /** Die Kamera eines Fotos (Eintrag aus `kameras.json`). */
    static kamera(k) {
        const r = k.R, z = k.f / k.s;
        const achse = i => new THREE.Vector3(r[i][0], r[i][1], r[i][2]);
        const ort = new THREE.Vector3(...k.mitte).addScaledVector(achse(2), z);
        const kamera = new THREE.PerspectiveCamera();
        kamera.matrixAutoUpdate = false;
        kamera.matrix.makeBasis(achse(0), achse(1), achse(2)).setPosition(ort);
        kamera.matrixWorld.copy(kamera.matrix);
        kamera.matrixWorldInverse.copy(kamera.matrixWorld).invert();
        const w = k.breite, h = k.hoehe, n = Ai2d3dseitenbild.NAH, f = Ai2d3dseitenbild.FERN;
        kamera.projectionMatrix.set(2 * k.f / w, 0, (w - 2 * k.t[0]) / w, 0,
                                    0, 2 * k.f / h, (2 * k.t[1] - h) / h, 0,
                                    0, 0, -(f + n) / (f - n), -2 * f * n / (f - n),
                                    0, 0, -1, 0);
        kamera.projectionMatrixInverse.copy(kamera.projectionMatrix).invert();
        kamera.layers.enableAll();
        return kamera;
    }

    /** Ein Durchgang der Szene auf `grund` (RGB 0–255) in eine 2D-Leinwand — echte Materialien, ohne was nur zur Ansicht gehört (das Rig). */
    static _durchgang(ansicht, kamera, breite, hoehe, grund) {
        const leinwand = document.createElement('canvas');
        const farbe = new THREE.Color().setRGB(...grund.map(v => v / 255), THREE.SRGBColorSpace).getHex();
        const versteckt = [];
        ansicht.szene.traverseVisible(o => { if (o.userData.nurAnsicht) versteckt.push(o); });
        Mesh3daizeichenflaeche.zeichnen(leinwand, breite, hoehe, farbe, r => {
            const ersatz = ansicht.szene.overrideMaterial;
            ansicht.szene.overrideMaterial = null;
            ansicht.licht?.(true);              // echte Materialien unter dem Fotolicht (`Ai2d3dansicht.FOTOLICHT`)
            for (const o of versteckt) o.visible = false;
            r.render(ansicht.szene, kamera);
            for (const o of versteckt) o.visible = true;
            ansicht.szene.overrideMaterial = ersatz;
            ansicht.licht?.(!ersatz);
        });
        return leinwand.getContext('2d').getImageData(0, 0, leinwand.width, leinwand.height);
    }

    /** RGBA-PNG (data-URL) eines Fotos: Bild vom weißen Durchgang, Alpha aus dem grünen. */
    static bild(ansicht, k) {
        const z = Ai2d3dseitenbild, hoehe = z.HOEHE, breite = Math.round(k.breite * hoehe / k.hoehe);
        const kamera = z.kamera(k);
        const weiss = z._durchgang(ansicht, kamera, breite, hoehe, [255, 255, 255]);
        const gruen = z._durchgang(ansicht, kamera, breite, hoehe, z.SCHLUESSEL);
        const g = gruen.data, aus = weiss.data, s = z.SCHLUESSEL;
        let figur = 0;
        for (let o = 0; o < aus.length; o += 4) {
            const drin = Math.abs(g[o] - s[0]) + Math.abs(g[o + 1] - s[1]) + Math.abs(g[o + 2] - s[2]) > z.SCHWELLE_SCHLUESSEL;
            aus[o + 3] = drin ? 255 : 0;
            figur += drin;
        }
        const leinwand = Object.assign(document.createElement('canvas'), { width: weiss.width, height: weiss.height });
        leinwand.getContext('2d').putImageData(weiss, 0, 0);
        return { url: leinwand.toDataURL('image/png'), figur, breite: weiss.width, hoehe: weiss.height };
    }

    /** Alle Fotos: Kameras holen, rendern, ablegen. @param seite `Ai2d3dseite` @param {string} job Kennung (sonst aus der Adresse des ersten Fotos) */
    static async aufnehmen(seite, job = undefined) {
        job = job ?? /\/api\/2d3dai\/([^/]+)\/foto\//.exec(seite.daten.fotos?.[0]?.adresse || '')?.[1];
        if (!job) throw new Error('Ai2d3dseitenbild: keine Kennung des Tests');
        const daten = await Serverabruf.json(`/api/2d3dai/${job}/abnahme/kameras/`);
        // Haltung je Foto (Auftrag EdgarTrip, 24.10.2026): jedes Foto in SEINER Haltung rendern; ohne Ablage (eine Haltung für alle) die Figur, wie sie dasteht
        const haltungen = (await Serverabruf.json(`/api/2d3dai/${job}/abnahme/haltungen/`).catch(() => ({ fotos: {} }))).fotos || {};
        const figur = seite.genesis?.inHaltung ? seite.genesis : null;
        const aus = [];
        for (const k of Object.values(daten.kameras)) {
            const h = haltungen[String(k.datei).split('.')[0]];
            const ersatz = h && figur?.figur?.parent ? await figur.inHaltung(h.dreh, h.ausgabe) : null;
            if (ersatz) {
                ersatz.position.copy(figur.figur.position);
                ersatz.quaternion.copy(figur.figur.quaternion);
                ersatz.scale.copy(figur.figur.scale);
                figur.figur.parent.add(ersatz);
                figur.figur.visible = false;
            }
            let b;
            try {
                b = Ai2d3dseitenbild.bild(seite.genesisfeld, k);
            } finally {
                if (ersatz) {
                    ersatz.removeFromParent();
                    ersatz.traverse(o => o.geometry?.dispose());      // nur die Geometrie dieser Haltung; Materialien und Texturen teilt sie mit der Figur
                    figur.figur.visible = true;
                }
            }
            if (!b.figur) throw new Error(`Ai2d3dseitenbild: Foto ${k.nr} (${k.datei}) zeigt keine Figur — Kamera oder Rahmen falsch`);
            const antwort = await Serverabruf.senden(`/api/2d3dai/${job}/abnahme/seite/${k.nr}/`, { bild: b.url });
            aus.push({ nr: k.nr, datei: k.datei, figur_px: b.figur, groesse: [b.breite, b.hoehe], bytes: antwort.bytes, haltung: ersatz ? 'je Foto' : 'gemeinsam' });
        }
        console.info('Ai2d3dseitenbild:', JSON.stringify(aus));
        return aus;
    }
}
