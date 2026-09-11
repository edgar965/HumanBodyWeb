import * as THREE from 'three';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Garmentstoff } from './garmentcode_stoff.js';
import { GarmentcodeGeometrie } from './garmentcode_geometrie.js';
import { Stueckereignis } from './garmentcode_stueckereignis.js';

/**
 * GarmentcodeAnziehen — das drapierte Kleidungsstück an die Figur hängen.
 *
 * WARUM (Edgar, 06.09.2026: „nach dem Bauen sollte die Kleidung am
 * ausgewählten HumanBody liegen. Was fehlt noch?"): Es fehlte genau dieser
 * Schritt. Der Server rechnete den Schnitt, drapierte ihn und übertrug sogar
 * die Knochengewichte — und dann warf der Browser das Ergebnis weg. Gemessen
 * im laufenden Betrieb: „Fertig in 3D: 5.533 Punkte, 10.854 Dreiecke,
 * angezogen", Netze an der Figur davor 2, danach 2.
 *
 * Die Rig-Datei (`<name>_sim_rig.json`) bringt alles mit: Punkte, Dreiecke,
 * je Punkt bis zu vier Paare aus Knochenindex und Gewicht, dazu die
 * Namensliste der Knochen. Über die Namen werden sie dem Skelett der Figur
 * zugeordnet — Indizes allein taugen nicht, die Reihenfolge muss nicht
 * übereinstimmen.
 *
 * Ohne Skelett oder Gewichte entsteht ein gewöhnliches Netz: sichtbar, aber
 * unbeweglich. Das ist besser als nichts, und die Meldung sagt es.
 */
export class GarmentcodeAnziehen {

    /**
     * Namensstamm des Stücks an der Figur — für den Austausch.
     *
     * Je STÜCK ein eigener Name (06.09.2026): Mit einem festen Namen für
     * alles nahm das zweite Kleidungsstück dem ersten den Platz — wer nach
     * dem T-Shirt eine Hose baute, stand danach ohne T-Shirt da. Derselbe
     * Schnitt zweimal gebaut ersetzt sich weiterhin, und das ist gewollt.
     */
    static STAMM = 'garmentcode_';

    /** Der Name eines Stücks; ohne Angabe der alte Sammelname. */
    static name(stueck) {
        const rein = String(stueck || 'kleidung').replace(/[^a-z0-9_-]/gi, '_');
        return GarmentcodeAnziehen.STAMM + rein;
    }

    /**
     * Der Schlüssel in `inst.clothMeshes` — und warum er dort stehen MUSS.
     *
     * BEFUND (Edgar, 08.09.2026: „Kleid GarmentCode auswählen als Objekt und
     * löschen funktioniert nicht - das ganze Modell wird gelöscht"). Das Stück
     * hing nur über `group.add()` an der Figur. `getSelectableSubMeshes` liest
     * aber `inst.clothMeshes`; was dort fehlt, ist kein Teilnetz. Ein Klick
     * darauf fiel deshalb in `interaction.js` auf `fn.selectCharacter(charId)`
     * durch — ausgewählt war die FIGUR, und Entf löschte sie mitsamt allem.
     *
     * Der Präfix ist eigen: `gar_`, `bld_`, `prim_` und `tpl_` haben in
     * `_removeSubMesh` je eigene Aufräumzweige, die Listen führen, die es
     * hier nicht gibt.
     */
    static schluessel(stueck) {
        const rein = String(stueck || 'kleidung').replace(/[^a-z0-9_-]/gi, '_');
        return `gc_${rein}`;
    }

    /** Three.js erlaubt vier Knochen je Punkt. */
    static KNOCHEN_JE_PUNKT = 4;

    /**
     * Holt die Rig-Datei und hängt das Stück an die Figur.
     *
     * @param figur  Instanz aus `state.characters`
     * @param url    Adresse der `*_sim_rig.json`
     * @returns Objekt mit punkte, dreiecke, angezogen, zugeordnet —
     *          oder wirft
     */
    static async anziehen(figur, url, stueck) {
        const daten = await fetch(url, { cache: 'no-store' }).then(a => {
            if (!a.ok) throw new Error(`Rig nicht ladbar (${a.status})`);
            return a.json();
        });
        return GarmentcodeAnziehen.einhaengen(figur, daten, stueck);
    }

    /** Derselbe Schritt mit schon geladenen Daten — so ist er prüfbar. */
    static einhaengen(figur, daten, stueck) {
        const geometrie = GarmentcodeGeometrie.aus(daten);
        // Das bisherige Aussehen überlebt das Neu-Einhängen — diese Methode
        // läuft auch aus `nachbinden` (`garmentcode_stoff.js`, 09.09.2026).
        const bisher = Garmentstoff.werte(
            figur?.clothMeshes?.[GarmentcodeAnziehen.schluessel(stueck)]);
        // Woraus das Gewebe seine Kachelgröße nimmt (10.09.2026).
        const stoff = { hatUv: !!geometrie.attributes.uv,
                        uvMeter: daten.uv_meter };
        GarmentcodeAnziehen.entfernen(figur, stueck);

        const skelett = GarmentcodeAnziehen._skelett(figur);
        const zuordnung = skelett
            ? GarmentcodeAnziehen.zuordnung(daten.knochen || [], skelett)
            : null;
        const gewichte = daten.gewichte || [];

        let netz;
        if (zuordnung && zuordnung.treffer && gewichte.length) {
            GarmentcodeAnziehen.gewichte(geometrie, gewichte, zuordnung.index);
            netz = new THREE.SkinnedMesh(geometrie,
                                        Garmentstoff.neu(bisher, stoff));
        } else {
            netz = new THREE.Mesh(geometrie, Garmentstoff.neu(bisher, stoff));
            // Ohne Gewichte in der Datei ist das kein Mangel, sondern der
            // Referenzkörper-Weg (06.09.2026) — dort gibt es bewusst kein
            // Rig. Gewarnt wird nur, wenn Gewichte da sind und das Skelett
            // fehlt: Dann ging etwas verloren.
            (gewichte.length ? Protokoll.warnung : Protokoll.debug)('GarmentCode',
                gewichte.length
                    ? 'Kleidung ohne Skinning eingehängt (Gewichte da, aber kein Skelett)'
                    : 'Kleidung als starres Netz eingehängt (Referenzkörper, ohne Rig)');
        }
        netz.name = GarmentcodeAnziehen.name(stueck);
        // Die Rohdaten bleiben AM NETZ. Ein HumanBody-Körper bekommt sein
        // Rigify-Skelett erst beim Animieren (`convertInstToSkinned`); ein
        // Stück, das vorher eingehängt wurde, hängt bis dahin als starres
        // Mesh und muss danach neu gebunden werden. Aus den Attributen der
        // Geometrie geht das nicht — deren Knochennummern gehören zu einem
        // Skelett, das es zu dem Zeitpunkt noch nicht gab (dieselbe Falle
        // wie bei MakeHuman, 07.09.2026).
        netz.userData.gcRig = daten;
        netz.userData.gcStueck = stueck;
        netz.frustumCulled = false;      // das Netz verlässt beim Posieren die Box
        // Die Beschriftung fürs Auswahlmenü — sonst stünde dort `gc_kleid`.
        netz.userData.beschriftung = `${stueck || 'Kleidung'} (GarmentCode)`;
        figur.group.add(netz);
        // Erst DAMIT ist das Stück ein eigenes Objekt: auswählbar,
        // hervorhebbar, einzeln löschbar (siehe `schluessel`).
        if (figur.clothMeshes) {
            figur.clothMeshes[GarmentcodeAnziehen.schluessel(stueck)] = netz;
        }
        // Gebunden wird in der Lage der FIGURGRUPPE, nicht der Welt — so
        // wie der Körper (`Eigenhaut.einhaengen`) und wie die Umkehrmatrizen
        // des Skeletts (`Knochenbau.ruhelagen`). Mit der Weltmatrix wäre
        // ein Stück, das gebunden wird, während die Figur schon 90 cm
        // weiter steht, um genau diese 90 cm doppelt verrechnet.
        if (netz.isSkinnedMesh) {
            netz.updateMatrix();
            netz.bind(skelett, netz.matrix);
        }
        Stueckereignis.melden(figur, stueck, true);
        return {
            punkte: geometrie.attributes.position.count,
            dreiecke: (daten.dreiecke || []).length,
            angezogen: netz.isSkinnedMesh === true,
            zugeordnet: zuordnung ? zuordnung.treffer : 0,
            name: netz.name,
        };
    }

    /**
     * Alle Stücke einer Figur neu binden — nachdem ein Skelett entstanden ist.
     *
     * Edgar, 08.09.2026: „die kleider werden nicht animiert". Der Grund war
     * die Reihenfolge: Ein HumanBody-Körper ist in der Szene ein gewöhnliches
     * `Mesh`; sein Rigify-Skelett baut `convertInstToSkinned` erst, wenn eine
     * Animation geladen wird. Wer vorher ein Stück gebaut hat — der Normalfall
     * —, bekam ein starres Netz, und dabei blieb es: Die Entscheidung
     * SkinnedMesh oder Mesh fällt beim Einhängen und wurde nie revidiert.
     *
     * @returns Anzahl der neu gebundenen Stücke
     */
    static nachbinden(figur) {
        const inst = figur?.inst || figur;
        if (!inst || !GarmentcodeAnziehen._skelett(inst)) return 0;
        const bestand = inst.clothMeshes || {};
        let gebunden = 0;
        for (const schluessel of Object.keys(bestand)) {
            if (!schluessel.startsWith('gc_')) continue;
            const netz = bestand[schluessel];
            // Schon gehäutet: nichts zu tun. Ohne Rohdaten geht es nicht —
            // das ist kein Fehler, sondern ein Stück aus einer Sitzung vor
            // dieser Änderung.
            if (!netz || netz.isSkinnedMesh || !netz.userData?.gcRig) continue;
            const ergebnis = GarmentcodeAnziehen.einhaengen(
                inst, netz.userData.gcRig, netz.userData.gcStueck);
            if (ergebnis.angezogen) gebunden += 1;
        }
        return gebunden;
    }

    /**
     * Ein früher eingehängtes Stück derselben Art wieder abnehmen.
     *
     * Der Eintrag in `clothMeshes` muss MIT weg. Bliebe er stehen, zeigte
     * die Teilnetz-Auswahl ein Stück an, das es nicht mehr gibt — und
     * `dispose()` liefe später über ein bereits freigegebenes Netz.
     */
    static entfernen(figur, stueck) {
        const schluessel = GarmentcodeAnziehen.schluessel(stueck);
        if (figur?.clothMeshes) delete figur.clothMeshes[schluessel];
        const alt = figur?.group?.getObjectByName(
            GarmentcodeAnziehen.name(stueck));
        if (!alt) return false;
        alt.geometry?.dispose();
        alt.material?.dispose();
        alt.removeFromParent();
        Stueckereignis.melden(figur, stueck, false);
        return true;
    }

    // -- Bausteine ------------------------------------------------------------

    /**
     * Knochenindex der Rig-Datei → Index im Skelett der Figur.
     *
     * Namen, die das Skelett nicht kennt, bekommen -1; ihr Gewicht fällt
     * weg. Das ist gewollt: Lieber ein Punkt weniger gebunden als an den
     * falschen Knochen gehängt.
     */
    static zuordnung(namen, skelett) {
        const nachName = new Map();
        skelett.bones.forEach((knochen, i) => {
            nachName.set(knochen.name, i);
            nachName.set(knochen.name.replace(/\./g, '_'), i);
        });
        const index = namen.map(name =>
            nachName.has(name) ? nachName.get(name)
                : (nachName.has(String(name).replace(/\./g, '_'))
                    ? nachName.get(String(name).replace(/\./g, '_')) : -1));
        return { index, treffer: index.filter(i => i >= 0).length };
    }

    /**
     * skinIndex/skinWeight aus den Paaren der Rig-Datei füllen — öffentlich,
     * weil das Theatre dieselben Rig-Dateien an sein eigenes Skelett bindet
     * (`TheatreJS/src/studio/garmentcodebindung.js`, 11.09.2026).
     */
    static gewichte(geometrie, gewichte, zuordnung) {
        const anzahl = geometrie.attributes.position.count;
        const je = GarmentcodeAnziehen.KNOCHEN_JE_PUNKT;
        const indizes = new Uint16Array(anzahl * je);
        const werte = new Float32Array(anzahl * je);
        for (let p = 0; p < anzahl; p++) {
            const paare = (gewichte[p] || [])
                .map(([knochen, wert]) => [zuordnung[knochen] ?? -1, wert])
                .filter(([knochen, wert]) => knochen >= 0 && wert > 0)
                .slice(0, je);
            const summe = paare.reduce((s, [, wert]) => s + wert, 0) || 1;
            paare.forEach(([knochen, wert], k) => {
                indizes[p * je + k] = knochen;
                werte[p * je + k] = wert / summe;    // muss sich zu 1 addieren
            });
        }
        geometrie.setAttribute('skinIndex', new THREE.BufferAttribute(indizes, je));
        geometrie.setAttribute('skinWeight', new THREE.BufferAttribute(werte, je));
    }

    static _skelett(figur) {
        let skelett = null;
        figur?.group?.traverse(o => {
            if (!skelett && o.isSkinnedMesh && o.skeleton) skelett = o.skeleton;
        });
        return skelett;
    }
}
