import * as THREE from 'three';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Netzgeometrie } from '../gemeinsam/netzgeometrie.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * GarmentcodePanels — das Schnittmuster als flache Flächen am Körper.
 *
 * WARUM (Edgar, 07.09.2026: „der 2D button könnte das Schnittmuster gleich
 * aufs Modell tun, so wie die Online version, und der 3D Button das 2D
 * Schnittmuster dann entfernen, ist das machbar?").
 *
 * Machbar, weil GarmentCode die Antwort selbst mitliefert: Jedes Panel
 * trägt in der Spezifikation eine `translation` und eine `rotation` — genau
 * daraus baut der Upstream sein `boxmesh`, das dann simuliert wird. Was das
 * Online-Werkzeug vor der Simulation zeigt, ist diese Anordnung.
 *
 * Die Rechnung steht auf dem Server (`GarmentCode/schnittvorschau.py`) und
 * ist dort gegen dieses `boxmesh.obj` geprüft: fünf der sechs Hüllgrenzen
 * auf 0,0 cm. Hier hängt nur noch ein Netz an der Figur.
 *
 * ZWEI SEITEN SICHTBAR, HALB DURCHSCHEINEND: Ein Panel ist eine Fläche
 * ohne Dicke; mit `FrontSide` verschwindet das Rückenteil, sobald man um
 * die Figur herumgeht, und das sieht aus, als fehle es. Die Durchsicht ist
 * kein Schmuck — die Panels stehen 2 bis 5 cm vom Körper ab, und ohne sie
 * ist nicht zu sehen, wo der Saum am Bein sitzt.
 */
export class GarmentcodePanels {

    static ADRESSE = '/api/garmentcode/schnittnetz/';

    /** Ein Name je Vorlage — zwei Schnitte hängen sich sonst gegenseitig ab. */
    static name(vorlage) {
        return `garmentcode2d_${vorlage || 'schnitt'}`;
    }

    /**
     * Die Panels an die Figur hängen. Gibt die Anzahl zurück, oder 0.
     *
     * @param figur        `{id, inst}` aus `GarmentcodeFigur.gewaehlt()`
     *                     ODER die Szeneninstanz selbst
     * @param spezifikation Pfad der `*_specification.json` (vom Server)
     * @param vorlage      Name des Kleidungsstücks (für den Netznamen)
     */
    static async zeigen(figur, spezifikation, vorlage) {
        const gruppe = GarmentcodePanels.gruppe(figur);
        if (!gruppe || !spezifikation) return 0;
        const daten = new FormData();
        daten.append('spezifikation', spezifikation);
        const antwort = await Serverabruf.formular(
            GarmentcodePanels.ADRESSE, daten);
        if (antwort.fehler) throw new Error(antwort.fehler);

        GarmentcodePanels.entfernen(figur, vorlage);
        // `drehen = false`: Der Server liefert schon Three-Achsen (Meter,
        // Y oben). Ohne Normalen — `Netzgeometrie` rechnet sie selbst, und
        // eine flache Fläche braucht keine gespeicherten.
        const geometrie = Netzgeometrie.bauen(antwort, THREE, null, false);
        geometrie.computeVertexNormals();
        const netz = new THREE.Mesh(geometrie, GarmentcodePanels.werkstoff());
        netz.name = GarmentcodePanels.name(vorlage);
        netz.userData.panels = antwort.panels || [];
        gruppe.add(netz);
        Protokoll.debug('GC-Panels',
            `${vorlage}: ${antwort.panels?.length || 0} Panels, `
            + `${antwort.vertex_count} Punkte`);
        return antwort.panels?.length || 0;
    }

    /**
     * Das Vorschaunetz wieder abräumen.
     *
     * Der 3D-Knopf ruft das, bevor er drapiert: Sonst stünde der flache
     * Schnitt im simulierten Stoff, und beide sähen falsch aus. Ohne
     * `vorlage` fliegt JEDE Schnittvorschau an dieser Figur — das ist der
     * Fall „Figur gewechselt" und „Vorlage gewechselt" in einem.
     */
    static entfernen(figur, vorlage = null) {
        const gruppe = GarmentcodePanels.gruppe(figur);
        if (!gruppe) return 0;
        const treffer = gruppe.children.filter(
            k => vorlage ? k.name === GarmentcodePanels.name(vorlage)
                         : k.name?.startsWith('garmentcode2d_'));
        for (const netz of treffer) Netzentsorgung.entfernen(gruppe, netz);
        return treffer.length;
    }

    /**
     * Die Three.js-Gruppe der Figur — egal, in welcher Form sie kommt.
     *
     * `GarmentcodeFigur.gewaehlt()` liefert `{id, inst}`, und die
     * Szeneninstanz steckt in `.inst`; `GarmentcodeDrapierung.anziehen`
     * reicht deshalb `figur.inst` weiter. Wer hier `figur.group` nimmt,
     * bekommt `undefined` — und `zeigen()` meldete „die Panels liessen
     * sich nicht anlegen", obwohl der Server 8 Panels geschickt hatte
     * (gemessen 07.09.2026). Kein Fehler, keine Ausnahme, nur eine
     * Meldung, die in die falsche Richtung zeigt.
     */
    static gruppe(figur) {
        return figur?.group || figur?.inst?.group || null;
    }

    static werkstoff() {
        return new THREE.MeshStandardMaterial({
            color: 0xd8a0b4,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.72,
            roughness: 0.85,
            metalness: 0.0,
            // Ohne das flimmert die Fläche gegen den Körper, wo sie ihn
            // streift — zwei Flächen im selben Tiefenwert.
            polygonOffset: true,
            polygonOffsetFactor: -1,
            polygonOffsetUnits: -1,
        });
    }
}
