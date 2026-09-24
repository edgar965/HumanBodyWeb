import * as THREE from 'three';
import { base64ToFloat32 } from './kodierung.js';
import { Koerperlage } from './koerperlage.js';
import { OberflaecheGLSL } from './oberflaecheglsl.js';
import { Shaderpatch } from './shaderpatch.js';
import { Koerperzuordnung } from './koerperzuordnung.js';
import { Protokoll } from './protokoll.js';
import { Kleidereinstellungen } from './kleidereinstellungen.js';

/**
 * Oberflaechenbindung — anliegende Kleidung folgt der Körperoberfläche, je
 * Bild, im Vertex-Shader (Konzept Fitting, Schicht 2 + 3, 21.09.2026).
 *
 * Edgar: „Überlege dir ein Konzept, z.B. dass die Kleider dehnbar sind, oder
 * anders an die Oberfläche angepasst werden." Der Server gibt jedem
 * Kleidungsteil seine Ruhe-Zuordnung mit (`G9oberflaechenbindung`: je Punkt
 * drei Körperpunkte, Baryzentrik, Abstand entlang der Körpernormale,
 * `mischung` 1 = anliegend … 0 = frei). Hier wird sie zu Attributen, und die
 * Materialien des Teils bekommen den Eingriff (`OberflaecheGLSL.VERTEX`):
 * gebundene Punkte stehen dort, wo ihr Körperdreieck gerade ist, plus ihrem
 * Ruheabstand — Durchdringen ist für sie konstruktiv unmöglich. Freie und
 * halbfreie Punkte werden aus den Gliedmaßenkapseln gedrückt (Schicht 3).
 *
 * WANN ES GILT: nur, wenn der Körper auf DERSELBEN Stufe steht wie die
 * Bindung (`stufen`) — beim Laden kommt erst der Käfig (Stufe 0), dann die
 * Browserstufe; die Indizes einer Stufe treffen auf der anderen falsche
 * Punkte. `verdrahten` prüft das je Bild über `uOberflaecheAn`.
 *
 * NICHT für Stücke im Stoffschwung (`userData.stoff`): dort setzt der
 * Worker die Lage je Bild; zwei Herren über einem Netz ergäben ein Zittern.
 */
export class Oberflaechenbindung {

    /** Mindestabstand über der Kapsel (Meter) — wie `G9kollision.ABSTAND`. */
    static KAPSELABSTAND = 0.003;
    /** Luft über der Haut, die ein gebundener Punkt höchstens verlangt (Meter);
     *  wer in Ruhe näher lag, darf so nah bleiben. 3 mm (wie `G9kollision.ABSTAND`)
     *  ließen bei `001_ShyrinKurz_smplx` Bild 229 einen Hautstreifen in der Achsel
     *  stehen — die Hautfalte wölbt sich zwischen den gebundenen Punkten vor; mit
     *  1 cm war er weg (Sichtprobe 24.09.2026, Grenzen 12 cm änderten nichts). */
    static LUFT = 0.01;
    /** Tiefer im Körper ist der Punkt nicht über SEINEM Dreieck (Meter). */
    static TIEF_GRENZE = 0.04;
    /** Seitlich weiter weg hat er die Tangentialebene verlassen (Meter). */
    static SEIT_GRENZE = 0.03;
    static SCHLUESSEL = 'oberflaeche';
    /**
     * Schalter fuer Gegenproben (A/B im Tab): Oberflaeche und Kapseln getrennt.
     *
     * BEIDE AUS (23.09.2026, Edgar mit Bild: Loch an der Schulternaht des
     * G9-Base-Shirts UND die Angie Sneakers sichtbar verformt/abgeloest):
     * gemessen an der laufenden Figur (Olesia1, TechnoDance) lag `mischung`
     * ueber FAST DER GANZEN Schuh-Geometrie bei 0,88-1,0 (Server-Formel in
     * `Genesis9/oberflaechenbindung.py`: mischung=1 unter 2,5 cm Abstand zum
     * naechsten Koerperdreieck) — ein Schuh haelt sich aber komplett innerhalb
     * dieses Radius um den Fuss, WIRD ALSO GANZ auf die Fussoberflaeche
     * projiziert, Punkt fuer Punkt UNABHAENGIG voneinander (kein starres
     * Mitschwingen wie bei normalem Skinning). An Stellen mit wechselnder
     * Kruemmung (Ferse, Schuhsohle, Aermelnaht) springt die naechste-Dreieck-
     * Wahl zwischen Nachbarpunkten — das reisst genau die Naht/Sohle auf, die
     * Edgar zeigte. Der eigentliche Kapsel-Fix von heute Nacht (Rumpf-
     * gebundene Punkte nie druecken, siehe `oberflaecheglsl.js`) hat daran
     * nichts geaendert, weil Schicht 2 (diese Projektion) selbst die Ursache
     * ist, nicht Schicht 3 (Kapseln). Bis das Verfahren nur auf wirklich
     * dehnbare, eng anliegende Stoffbereiche begrenzt ist (nicht auf starre
     * Schuhe und Nahtkanten), bleibt SCHICHT 2 aus — reines Skinning wie vor
     * dem 21.09.2026.
     *
     * KAPSELN KURZ AN, DANN WIEDER AUS (23.09.2026): Auf „OK, dann schalte das
     * ein" hin lief Schicht 3 allein (Schicht 2 blieb aus). Am Schuh hat das
     * getragen — Edgar: „Schuhe sind nicht mehr kaputt" —, aber das T-Shirt war
     * danach kaputt, und darauf ging es wieder aus. Was dabei repariert wurde
     * und unabhängig von diesem Schalter gilt:
     *   1. `Koerperzuordnung.gruppenindex` steckte 16 Zehenknochen je Figur in
     *      die ARM-Gruppe (Genesis9 nennt die Zehen wie die Finger:
     *      `l_indextoe1`, `l_midtoe1`, …). Der eigene Fuß galt für die
     *      Schuhspitze damit als FREMDE Gliedmaße und drückte die Kappe heraus
     *      — Edgars Bild mit der aufgerissenen Sneaker-Spitze.
     *   2. `Koerperlage._kapseln` erneuerte die Kapseln nach einem Körper-
     *      Neuaufbau nicht; sie standen dann in der Ruhepose still.
     * OFFEN bleibt das Oberteil: eine Messung über 22 Spagat-Bilder ergab für
     * das Shirt 0 Kapseltreffer — der sichtbare Schaden kommt also NICHT aus
     * dieser Schleife, sondern woanders her. Bis das geklärt ist, bleibt aus.
     *
     * SCHICHT 2 WIEDER AN (24.09.2026, Edgar: Haut durch das Shirt,
     * `001_ShyrinKurz_smplx` Bild 229): nicht mehr als Projektion, sondern NUR
     * HINAUS (`oberflaecheglsl.js`) — der Stoff bleibt beim Skinning und wird
     * nur geschoben, wo er tiefer liegt als in Ruhe. Die Ursache der zerrissenen
     * Schuhe (jeder Punkt für sich auf die Fußoberfläche gesetzt) gibt es damit
     * nicht mehr; ein Punkt über dem Fuß bewegt sich nie. Ob sie läuft, steht
     * seither unter Einstellungen → Kleider (`Kleidereinstellungen`, Vorgabe An).
     *
     * NORMALEN AUS DER FLÄCHE (derselbe Tag): Der helle Fleck in der Achsel bei
     * Bild 229 war KEINE Haut — mit ausgeblendetem Körper blieb er stehen, mit
     * `flatShading` war er weg. In der Achsel mischt jeder Stoffpunkt Arm- und
     * Rumpfknochen; die gemischte Normale passt nicht mehr zur gestauchten
     * Fläche, und das Material (`metalness` 1) spiegelt dort die helle
     * Umgebung. Der Fragment-Eingriff zieht die Normale zur echten Flächen-
     * normale, wo beide auseinanderlaufen (`OberflaecheGLSL.FRAGMENT`).
     */
    static KAPSELN_AKTIV = false;

    /**
     * Die Bindung aus der Serverantwort eines Teils als Attribute ans Netz.
     * `bindgruppe` (welche Gliedmaße der Punkt trägt, für den Kapselfilter
     * in `verdrahten`) steht hier nur als Platzhalter (0) — den Körper
     * gibt es zu diesem Zeitpunkt oft noch nicht (`Genesis9aufbau.alles`:
     * Körper und Kleidung laufen GLEICHZEITIG, ein Stück kann vor dem
     * Körper ankommen). `verdrahten` füllt ihn, sobald `inst.bodyMesh` da
     * ist — bei jedem Einhängen, auch nach `_kleiderBinden`.
     * @returns true, wenn das Netz gebunden ist
     */
    static anlegen(netz, teil) {
        const b = teil?.bindung;
        const geo = netz?.geometry;
        if (!b || !geo?.attributes?.position || teil.stoff) return false;
        const n = geo.attributes.position.count;
        const dreieck = base64ToFloat32(b.dreieck), bary = base64ToFloat32(b.bary);
        const abstand = base64ToFloat32(b.abstand), mischung = base64ToFloat32(b.mischung);
        if (dreieck.length !== 3 * n || mischung.length !== n) {
            Protokoll.warnung('Oberflaechenbindung', `${netz.name}: Bindung passt nicht (${mischung.length} zu ${n})`);
            return false;
        }
        geo.setAttribute('bindung', new THREE.BufferAttribute(dreieck, 3));
        geo.setAttribute('bary', new THREE.BufferAttribute(bary, 3));
        geo.setAttribute('bindabstand', new THREE.BufferAttribute(abstand, 1));
        geo.setAttribute('mischung', new THREE.BufferAttribute(mischung, 1));
        geo.setAttribute('bindgruppe', new THREE.BufferAttribute(new Float32Array(n), 1));
        geo.userData.bindung = { stufen: Number(b.stufen) || 0, gebunden: Oberflaechenbindung._anzahl(mischung) };
        return true;
    }

    /**
     * Gruppen-ID je Stoffpunkt nachtragen — die Gruppe des ERSTEN
     * Körperdreieckpunkts (`Koerperzuordnung`). Ohne Körper oder ohne
     * dessen Skinning-Attribute bleibt 0 (jede Kapsel gilt als fremd —
     * schlechter gefiltert, aber nicht falsch).
     */
    static _bindgruppenNachtragen(inst, netz) {
        const geo = netz?.geometry;
        const dreieck = geo?.attributes?.bindung?.array;
        const bindgruppe = geo?.attributes?.bindgruppe;
        const gruppeJePunkt = inst?.bodyMesh ? Koerperzuordnung.gruppeJePunkt(inst.bodyMesh) : null;
        if (!dreieck || !bindgruppe || !gruppeJePunkt) return;
        const aus = bindgruppe.array;
        for (let i = 0; i < aus.length; i++) {
            const k = dreieck[3 * i];
            aus[i] = k >= 0 && k < gruppeJePunkt.length ? gruppeJePunkt[k] : 0;
        }
        bindgruppe.needsUpdate = true;
    }

    /**
     * Ein Netz (nach dem Einhängen, auch nach dem Neubinden) mit der Figur
     * verdrahten: Eingriff an jedem Material, Körperlage je Bild.
     */
    static verdrahten(inst, netz) {
        const bindung = netz?.geometry?.userData?.bindung;
        if (!bindung) return false;
        Oberflaechenbindung._bindgruppenNachtragen(inst, netz);
        const materialien = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const m of materialien) Oberflaechenbindung._eingriff(m);
        netz.onBeforeRender = (renderer) => Oberflaechenbindung._vorZeichnen(renderer, inst, netz);
        return true;
    }

    static _vorZeichnen(renderer, inst, netz) {
        const lage = Koerperlage.sichern(renderer, inst);
        const passt = Kleidereinstellungen.an('kleider_oberflaechenbindung') && Boolean(lage)
            && (inst.stufen || 0) === netz.geometry.userData.bindung.stufen;
        const flaeche = Kleidereinstellungen.an('kleider_normalen_aus_flaeche');
        const materialien = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const m of materialien) {
            const u = m.userData.oberflaeche;
            if (!u) continue;
            u.uOberflaecheAn.value = passt ? 1 : 0;
            u.uNormaleAusFlaeche.value = flaeche ? 1 : 0;
            u.uKapselAn.value = Oberflaechenbindung.KAPSELN_AKTIV && lage && lage.anzahl ? 1 : 0;
            if (!lage) continue;
            u.uKoerperLage.value = lage.lage;
            u.uKoerperNormale.value = lage.normale;
            u.uLageBreite.value = lage.breite;
            u.uKapselAnzahl.value = lage.anzahl;
            if (lage.kapseln) u.uKapseln.value = lage.kapseln;
        }
    }

    /** Die Uniforms EINMAL je Material anlegen — sie bleiben dieselben Objekte
     *  (Three hält je Programm die Uniforms des zuletzt kompilierten, `genesis9.md`). */
    static _eingriff(material) {
        if (material.userData.oberflaeche) return;
        const platzhalter = new THREE.DataTexture(new Float32Array([0, 0, 0, 1]), 1, 1, THREE.RGBAFormat, THREE.FloatType);
        platzhalter.needsUpdate = true;
        const u = material.userData.oberflaeche = {
            uOberflaecheAn: { value: 0 },
            uKoerperLage: { value: platzhalter },
            uKoerperNormale: { value: platzhalter },
            uLageBreite: { value: 1 },
            uLuft: { value: Oberflaechenbindung.LUFT },
            uTiefGrenze: { value: Oberflaechenbindung.TIEF_GRENZE },
            uSeitGrenze: { value: Oberflaechenbindung.SEIT_GRENZE },
            uNormaleAusFlaeche: { value: 1 },
            uKapselAn: { value: 0 },
            uKapselAbstand: { value: Oberflaechenbindung.KAPSELABSTAND },
            uKapselAnzahl: { value: 0 },
            uKapseln: { value: Array.from({ length: 4 * OberflaecheGLSL.KAPSELN }, () => new THREE.Vector4()) },
        };
        const eingriff = (shader) => {
            Object.assign(shader.uniforms, u);
            shader.vertexShader = shader.vertexShader
                .replace('#include <common>', '#include <common>\n' + OberflaecheGLSL.UNIFORMS)
                .replace('#include <skinning_vertex>', OberflaecheGLSL.VERTEX);
            shader.fragmentShader = shader.fragmentShader
                .replace('#include <common>', '#include <common>\n' + OberflaecheGLSL.FRAGMENT_UNIFORMS)
                .replace('#include <normal_fragment_begin>', OberflaecheGLSL.FRAGMENT);
        };
        eingriff.kennung = () => 'o2';
        Shaderpatch.anhaengen(material, Oberflaechenbindung.SCHLUESSEL, eingriff);
        material.needsUpdate = true;
    }

    static _anzahl(mischung) {
        let n = 0;
        for (let i = 0; i < mischung.length; i++) if (mischung[i] >= 1) n++;
        return n;
    }

    /** Für Proben: Stand einer Figur — gebundene Punkte je Stück. */
    static stand(inst) {
        const aus = {};
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            const b = netz?.geometry?.userData?.bindung;
            if (b) aus[schluessel] = { ...b, an: Boolean(netz.onBeforeRender && netz.onBeforeRender !== THREE.Object3D.prototype.onBeforeRender) };
        }
        return aus;
    }
}
