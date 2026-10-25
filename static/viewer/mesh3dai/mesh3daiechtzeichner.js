/**
 * Mesh3daiechtzeichner — zeichnet eine Zeile mit ECHTEN Daten auf der Seite „Mesh3D-AI“ (15.10.2026; Server `Mesh3daidaten`, `Mesh3daiflaeche`, `Mesh3daidatenteile`).
 * Eingabe = die Außenfläche von Ursula1 in der Pose (`Mesh3daiflaechen`, Teil `aussen`) in der gewählten Ansichtsart; in der Art „Punkte“ (oder solange die Fläche fehlt) die Punktwolke, die das Netz bekommt
 * (4.096 von 16.384 Punkten, `probe.eingabeEcht`). Gewünschte Ausgabe = die ganze gehäutete Figur in der Ansichtsart (auch unter den Kleidern); das Rig legt `Mesh3dairigzeichner.ueberlagern` darüber (Knopf „Rig“).
 * Ausgabe des Netzes = die vorhergesagten Rig-Punkte (Überlagerung, Knopf „Rig“) und die Figur, mit ihnen gehäutet (`Mesh3daiflaechen.ausgabe`, Näherung — das Netz selbst sagt nur die Punkte voraus);
 * darunter auf Wunsch das Soll als Geist (Fläche durchscheinend, Rig grau).
 * Jede Zeile zeigt ihren Teil (`beschreibung.etiketten`: nur Körper, Kleider) und ihre Ausschnitte (`teil.ausschnitte`: Gesicht, Hände/Füße), jeweils um `ziel − mitte` gerückt wie ihr Rig.
 * Aufgerufen von `Mesh3daikapselzeichner` und `Mesh3daigesichtzeichner`, sobald `d.echt` gesetzt ist.
 */
import * as THREE from 'three';
import { Mesh3daiapose } from './mesh3daiapose.js';
import { Mesh3daiechtmaterial } from './mesh3daiechtmaterial.js';
import { Mesh3daiflaechen } from './mesh3daiflaechen.js';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';
import { Mesh3daigenesisfigur } from './mesh3daigenesisfigur.js';
import { Mesh3dairigzeichner } from './mesh3dairigzeichner.js';

export class Mesh3daiechtzeichner {
    /** Punktgröße der Wolke in m (perspektivisch): ganzer Körper rund 1,65 m hoch; in den Ausschnitten (Gesicht, Hände) kleiner. */
    static PUNKTGROESSE = 0.017;
    static PUNKTGROESSE_AUSSCHNITT = 0.006;
    /** Dichte Wolke eines Tripo-Jobs (2 Mio. Punkte, Abstand rund 1 mm): kleine Punkte, sonst verschwimmt die Textur. */
    static PUNKTGROESSE_DICHT = 0.0025;
    static PUNKTGROESSE_DICHT_AUSSCHNITT = 0.0012;
    static GEISTFARBE = 0x8d97ab;
    /** Reihenfolge der Teile in Wolke und Fläche (= `Mesh3daiflaeche.TEILE` auf dem Server). */
    static TEILE = ['koerper', 'anatomie', 'haar', 'slip', 'hose', 'hemd', 'augen'];

    static zeichnen(inhalt, art, d) {
        const z = Mesh3daiechtzeichner;
        const probe = d.probe;
        if (!probe?.rig) return;
        // Das Zwischenbild „Rig → A-Pose“ (17.10.2026) hat eine eigene Fläche (`Mesh3daiapose`), nicht die der Probe.
        if (art === 'apose') {
            Mesh3daiapose.zeichnen(inhalt, d);
            return;
        }
        // Ziel und Ergebnis als Genesis-Figur aus dem Code der Charakter-Seite (19.10.2026, `Mesh3daigenesisfigur`); solange sie baut, steht ein Text im Feld. Ohne Figur (Hände/Füße,
        // Bilder der Animation, Lauf ohne Gelenkwinkel) bleibt der bisherige Weg darunter.
        const genesis = Mesh3daigenesisfigur.fuer(d, art);
        if (genesis) {
            if (genesis.stand === 'fertig') Mesh3daigenesisfigur.einhaengen(inhalt, genesis, d, art);
            else inhalt.userData.hinweis = genesis.text;
            if (art === 'ausgabe') z._geist(inhalt, d);
            return;
        }
        // Teile der Figur, die das Feld zeigt; die Eingabe von „Nur Körper“ ist die ganze Außenfläche mit Kleidern (`eingabe_etiketten` leer).
        const liste = art === 'eingabe' ? (d.beschreibung?.eingabe_etiketten ?? d.beschreibung?.etiketten) : d.beschreibung?.etiketten;
        const etiketten = liste?.length ? liste : null;
        // Punktwolke des Datensatzes in der Ansicht „Punkte“ (in der Animation gibt es sie nicht — dort die Punkte der Fläche) und solange die Fläche fehlt.
        // Trainingspaar (18.10.2026, `probe.start === 'wolke'`): der Start ist das Tripo-Netz, ein ANDERES Netz als das Ziel — immer die Wolke, nie die Außenfläche des Ziels.
        const wolke = art === 'eingabe' && ((d.modus === 'punkte' && probe.eingabeEcht) || !probe.flaeche || probe.start === 'wolke');
        // Ausgabe: die Figur, gehäutet mit dem vorhergesagten Rig — bei einem Lauf mit Daz-Winkeln genau (Drehung je Knochen aus dem Netz, aus der Ruhelage wie das Ziel), sonst die Näherung
        // aus den Rig-Punkten (`Mesh3daihaeutung`); ohne Hautgewichte nur das Rig.
        const genau = probe.rig.dreh && d.haltung?.ruhezentren ? { dreh: probe.rig.dreh, ruhezentren: d.haltung.ruhezentren } : null;
        // Seit 19.10.2026 spätabends (Edgar: „das Ergebnis soll direkt aus der KI kommen“): diese Fläche wäre die Figur des ZIELS in der vorhergesagten Pose — mit `ergebnisOhneZielflaeche` zeigt das Ergebnis
        // hier nur das Rig; eine Fläche gibt es dort, wo die Seite die Figur der KI baut (`Mesh3daigenesisfigur`).
        const flaeche = art === 'ausgabe' ? (d.ergebnisOhneZielflaeche ? null : probe.flaeche?.ausgabe(probe.rig.soll, probe.rig.ausgabe, d.rigBeschreibung.knochen.map(k => k.eltern), genau)) : probe.flaeche;
        const ausschnitte = d.teil?.ausschnitte?.length ? d.teil.ausschnitte : [null];
        for (const a of ausschnitte) {
            const objekte = [];
            if (wolke) {
                if (probe.eingabeEcht) objekte.push(z.punktwolke(probe.eingabeEcht, { etiketten, ausschnitt: a, rig: probe.rig.soll }));
            } else if (flaeche) {
                // „Textur“: die Bilder der Figur (Haut, Kleider in Ursulas Farbe, Haar) in allen drei Feldern — was das Netz an Farbe bekommt, zeigt „Punkte“ im Start.
                const bilder = d.modus === 'textur' ? flaeche.bilder?.() : null;
                objekte.push(Mesh3daiechtmaterial.netz(flaeche.teil({ aussen: art === 'eingabe', etiketten, ausschnitt: a, rig: probe.rig.soll }), d.modus, bilder));
            }
            // Soll als Geist: die Fläche des Soll durchscheinend unter der Ausgabe (das Soll-Rig dazu zeichnet `_geist`, wenn der Knopf „Rig“ an ist).
            if (art === 'ausgabe' && d.geist && probe.flaeche) objekte.push(Mesh3daiechtmaterial.geist(probe.flaeche.teil({ aussen: false, etiketten, ausschnitt: a, rig: probe.rig.soll })));
            for (const objekt of objekte) {
                if (a) objekt.position.set(a.ziel[0] - a.mitte[0], a.ziel[1] - a.mitte[1], a.ziel[2] - a.mitte[2]);
                objekt.traverse(o => { o.frustumCulled = false; });
                inhalt.add(objekt);
            }
        }
        if (art === 'ausgabe') z._geist(inhalt, d);
    }

    /** Ausgabe des Netzes: das Soll-Rig als grauer Geist unter der Vorhersage (Schalter „Soll als Geist“; ein Rig — also nur, wenn der Knopf „Rig“ an ist). */
    static _geist(inhalt, d) {
        if (!d.geist || !d.rig || !d.teil?.rig?.soll || !d.rigBeschreibung || !d.rigIndizes) return;
        const geist = Mesh3dairigzeichner.zeichnen(d.rigBeschreibung, d.rigIndizes, d.teil.rig.soll, { massstab: (d.rigMassstab ?? 1) * 0.7, farbe: Mesh3daiechtzeichner.GEISTFARBE });
        geist.traverse(o => { o.renderOrder = 19; });   // unter der Ausgabe (20), sonst deckt der Geist die Fehlerfarben zu
        inhalt.add(geist);
    }

    /**
     * Die Punktwolke der Eingabe (`{punkte, farbe (0–255, sRGB), etikett}`), auf Teile und einen Ausschnitt beschränkt; die Farben werden in den linearen Raum gerechnet, den three.js erwartet.
     * @param {{etiketten?: string[]|null, ausschnitt?: object|null, rig?: number[][]}} wahl
     */
    static punktwolke(w, { etiketten = null, ausschnitt = null, rig = null } = {}) {
        const z = Mesh3daiechtzeichner;
        if (w.dicht) return z._dichteWolke(w, { etiketten, ausschnitt, rig });
        const erlaubt = etiketten ? new Set(etiketten.map(e => z.TEILE.indexOf(e))) : null;
        let naechster = null, knochen = null, r2 = 0;
        if (ausschnitt) {
            w._naechster ??= Mesh3daiflaechen.naechste(w.punkte.length, i => w.punkte[i], rig);
            naechster = w._naechster;
            knochen = new Set(ausschnitt.knochen);
            r2 = ausschnitt.radius ** 2;
        }
        const lage = [], farben = [];
        const c = new THREE.Color();
        w.punkte.forEach((p, i) => {
            if (erlaubt && !erlaubt.has(w.etikett?.[i])) return;
            if (ausschnitt) {
                if (!knochen.has(naechster[i])) return;
                const m = ausschnitt.mitte;
                if ((p[0] - m[0]) ** 2 + (p[1] - m[1]) ** 2 + (p[2] - m[2]) ** 2 > r2) return;
            }
            lage.push(p[0], p[1], p[2]);
            c.setRGB(w.farbe[i][0] / 255, w.farbe[i][1] / 255, w.farbe[i][2] / 255, THREE.SRGBColorSpace);
            farben.push(c.r, c.g, c.b);
        });
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(lage), 3));
        geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(farben), 3));
        const groesse = ausschnitt ? z.PUNKTGROESSE_AUSSCHNITT : z.PUNKTGROESSE;
        const material = Mesh3daigemeinsam.material(`echtwolke:${groesse}`, () => new THREE.PointsMaterial({ size: groesse, vertexColors: true, sizeAttenuation: true }));
        return new THREE.Points(geo, material);
    }

    /** Dieselbe Wolke aus Typed Arrays (`Mesh3daiseite._dichteWolke`: `lage` Float32, `rgb` Uint8 sRGB, `etikett` Int8) — ohne ein Objekt je Punkt. */
    static _dichteWolke(w, { etiketten, ausschnitt, rig }) {
        const z = Mesh3daiechtzeichner;
        const erlaubt = etiketten ? new Set(etiketten.map(e => z.TEILE.indexOf(e))) : null;
        const lin = new Float32Array(256);
        const c = new THREE.Color();
        for (let k = 0; k < 256; k++) lin[k] = c.setRGB(k / 255, 0, 0, THREE.SRGBColorSpace).r;
        let naechster = null, knochen = null, r2 = 0, m = null;
        if (ausschnitt) {
            w._naechster ??= Mesh3daiflaechen.naechste(w.anzahl, i => [w.lage[3 * i], w.lage[3 * i + 1], w.lage[3 * i + 2]], rig);
            naechster = w._naechster;
            knochen = new Set(ausschnitt.knochen);
            r2 = ausschnitt.radius ** 2;
            m = ausschnitt.mitte;
        }
        const lage = new Float32Array(w.anzahl * 3), farben = new Float32Array(w.anzahl * 3);
        let n = 0;
        for (let i = 0; i < w.anzahl; i++) {
            if (erlaubt && !erlaubt.has(w.etikett[i])) continue;
            const x = w.lage[3 * i], y = w.lage[3 * i + 1], q = w.lage[3 * i + 2];
            if (ausschnitt && (!knochen.has(naechster[i]) || (x - m[0]) ** 2 + (y - m[1]) ** 2 + (q - m[2]) ** 2 > r2)) continue;
            lage[3 * n] = x; lage[3 * n + 1] = y; lage[3 * n + 2] = q;
            farben[3 * n] = lin[w.rgb[3 * i]]; farben[3 * n + 1] = lin[w.rgb[3 * i + 1]]; farben[3 * n + 2] = lin[w.rgb[3 * i + 2]];
            n++;
        }
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(lage.subarray(0, 3 * n), 3));
        geo.setAttribute('color', new THREE.BufferAttribute(farben.subarray(0, 3 * n), 3));
        const groesse = ausschnitt ? z.PUNKTGROESSE_DICHT_AUSSCHNITT : z.PUNKTGROESSE_DICHT;
        const material = Mesh3daigemeinsam.material(`echtwolke:${groesse}`, () => new THREE.PointsMaterial({ size: groesse, vertexColors: true, sizeAttenuation: true }));
        return new THREE.Points(geo, material);
    }
}
