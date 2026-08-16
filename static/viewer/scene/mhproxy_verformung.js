import { base64ToFloat32, blenderToThreeCoords, _selectedInst, _selectedMHMesh,
         _charQueryParams, _sliderVal } from './utils.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Mhverformung — Geometrie der MakeHuman-Kleidung: Größe, Abstand, Höhe und
 * das Herausdrücken aus dem Körper.
 *
 * Aus `loadMHProxyUI()` herausgeloest (Umbau 16.08.2026). Getrennt von der
 * Verdrahtung, weil hier nichts mit Bedienelementen passiert, sondern mit
 * Vertices — und weil der Schwerpunkt gemerkt werden muss, was einen Zustand
 * braucht.
 */
export class Mhverformung {

    /**
     * @param vorsilbe  Kennungs-Vorsilbe der Regler: 'mh' im Assets-Reiter,
     *                  'prop-mh' im Eigenschaften-Reiter. Beide Reiter hatten
     *                  bis zum Umbau am 16.08.2026 je eine eigene, Zeile für
     *                  Zeile gleiche Fassung des Herausdrückens — 60 Zeilen
     *                  doppelt, inklusive der Koordinatenumrechnung und des
     *                  Sicherns für das Zurücknehmen.
     */
    constructor(vorsilbe = 'mh') {
        this.vorsilbe = vorsilbe;
        // Schwerpunkt je Kleidungsschlüssel. Vorher wurde er bei JEDER
        // Reglerbewegung neu über alle Vertices gerechnet, obwohl die
        // Ausgangspunkte sich dabei nicht ändern.
        this._schwerpunkte = new Map();
    }

    // -------------------------------------------------------------- Verformen

    /**
     * Größe, Abstand und Höhe direkt auf den Vertices — ohne Serverfrage.
     * Skaliert wird um den Schwerpunkt der Ausgangspunkte, der Abstand drückt
     * radial nach außen.
     */
    anwenden() {
        const auswahl = _selectedMHMesh();
        if (!auswahl) return;
        const ausgang = auswahl.inst.garmentOrigPositions?.[auswahl.key];
        if (!ausgang) return;

        const abstand = _sliderVal(`${this.vorsilbe}-offset`) / 1000;
        const groesse = _sliderVal(`${this.vorsilbe}-scale`) / 100;
        const hoehe = _sliderVal(`${this.vorsilbe}-y-offset`) / 1000;
        const [sx, sy, sz] = this.schwerpunkt(auswahl.key, ausgang);

        const punkte = auswahl.mesh.geometry.getAttribute('position');
        const feld = punkte.array;
        for (let i = 0; i < ausgang.length; i += 3) {
            let x = (ausgang[i] - sx) * groesse + sx;
            let y = (ausgang[i + 1] - sy) * groesse + sy;
            let z = (ausgang[i + 2] - sz) * groesse + sz;
            if (abstand > 0) {
                const dx = x - sx, dy = y - sy, dz = z - sz;
                const laenge = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;
                x += (dx / laenge) * abstand;
                y += (dy / laenge) * abstand;
                z += (dz / laenge) * abstand;
            }
            feld[i] = x;
            feld[i + 1] = y + hoehe;   // in Three.js zeigt Y nach oben
            feld[i + 2] = z;
        }
        punkte.needsUpdate = true;
        auswahl.mesh.geometry.computeBoundingSphere();
    }

    /** Schwerpunkt der Ausgangspunkte — gemerkt, solange sie gleich bleiben. */
    schwerpunkt(schluessel, ausgang) {
        const gemerkt = this._schwerpunkte.get(schluessel);
        if (gemerkt && gemerkt.laenge === ausgang.length) return gemerkt.wert;
        let x = 0, y = 0, z = 0;
        for (let i = 0; i < ausgang.length; i += 3) {
            x += ausgang[i];
            y += ausgang[i + 1];
            z += ausgang[i + 2];
        }
        const anzahl = ausgang.length / 3;
        const wert = [x / anzahl, y / anzahl, z / anzahl];
        this._schwerpunkte.set(schluessel, { laenge: ausgang.length, wert });
        return wert;
    }

    /** Nach einer Neuanpassung sind die Ausgangspunkte andere. */
    vergessen(schluessel) {
        this._schwerpunkte.delete(schluessel);
    }

    // --------------------------------------------------------- Aus dem Körper

    /**
     * Kleidung, die im Körper steckt, nach außen drücken. Der Server rechnet
     * das; er arbeitet in Blender-Koordinaten, deshalb die Umrechnung hin und
     * zurück.
     */
    async herausdruecken() {
        const figur = _selectedInst();
        if (!figur) return;
        const schluessel = Object.keys(figur.clothMeshes || {})
            .find(name => name.startsWith('mh_'));
        const netz = schluessel && figur.clothMeshes[schluessel];
        if (!netz) return;

        const punkte = netz.geometry.getAttribute('position');
        this._standSichern(figur, schluessel, punkte);
        try {
            const neue = await this._serverDruecken(figur, punkte.array);
            if (!neue) return;
            punkte.array.set(neue);
            punkte.needsUpdate = true;
            netz.geometry.computeBoundingSphere();
            // Die Regler rechnen ab jetzt von hier aus weiter.
            figur.garmentOrigPositions[schluessel] = new Float32Array(neue);
            this.vergessen(schluessel);
            Protokoll.debug('Szene', 'Aus dem Körper gedrückt');
        } catch (fehler) {
            console.error('Herausdrücken fehlgeschlagen:', fehler);
        }
    }

    /** Stand vor dem Drücken behalten — einmal, für das Zurücknehmen. */
    _standSichern(figur, schluessel, punkte) {
        if (!figur._mhPrePush) figur._mhPrePush = {};
        if (!figur._mhPrePush[schluessel]) {
            figur._mhPrePush[schluessel] = new Float32Array(punkte.array);
        }
    }

    async _serverDruecken(figur, threePunkte) {
        // Three.js -> Blender: (x, y, z) -> (x, -z, y)
        const blender = new Float32Array(threePunkte.length);
        for (let i = 0; i < threePunkte.length; i += 3) {
            blender[i] = threePunkte[i];
            blender[i + 1] = -threePunkte[i + 2];
            blender[i + 2] = threePunkte[i + 1];
        }
        const frage = _charQueryParams(figur);
        frage.set('push_dist', _sliderVal(`${this.vorsilbe}-push-dist`));
        frage.set('use_mh_body', '0');
        const b64 = btoa(String.fromCharCode(...new Uint8Array(blender.buffer)));
        const daten = await Serverabruf.json(`/api/character/mh-push-outside/?${frage}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vertices: b64 }),
        });
        if (daten.error) {
            console.warn('Herausdrücken fehlgeschlagen:', daten.error);
            return null;
        }
        const neue = base64ToFloat32(daten.vertices);
        blenderToThreeCoords(neue);
        return neue;
    }

    zuruecknehmen() {
        const auswahl = _selectedMHMesh();
        if (!auswahl) return;
        const stand = auswahl.inst._mhPrePush?.[auswahl.key];
        if (!stand) return;
        const punkte = auswahl.mesh.geometry.getAttribute('position');
        punkte.array.set(stand);
        punkte.needsUpdate = true;
        auswahl.mesh.geometry.computeBoundingSphere();
        auswahl.inst.garmentOrigPositions[auswahl.key] = new Float32Array(stand);
        delete auswahl.inst._mhPrePush[auswahl.key];
        this.vergessen(auswahl.key);
        Protokoll.debug('Szene', 'Herausdrücken zurückgenommen');
    }
}
