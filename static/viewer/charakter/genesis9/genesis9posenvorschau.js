import { THREE } from '../state.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Genesis9materialabruf } from '../../gemeinsam/genesis9materialabruf.js';

/**
 * Genesis9posenvorschau — eine Daz-Pose SOFORT zeigen: das vorhandene Skelett drehen, bevor der Server die Figur neu backt.
 *
 * Edgar, 17.10.2026: „posen dauern irrsinnig lange, das sollte doch in 1 s gehen" — dann „mach erst … Sofortschau". Gemessen
 * (fünf Stücke an Ursula, Chrome): Der neue Körper stand nach 1,4–4,4 s, die genaue Kleidung nach rund 10 s; der Körper-
 * NEUBAU im Browser (Netz, Materialien, Umbinden aller Stücke) kostet allein Sekunden, und das Haar schwebte so lange an der
 * alten Stelle.
 *
 * Hier fragt der Klick nur die Knochenwege (`/knochenwege/`, `G9knochenwegeapi`: je Knochen `neu · alt⁻¹` der Daz-Matrizen)
 * und stellt jeden Knochen auf `Weg · Bindelage`. Körper, Anhänge, Kleidung und Haar hängen an diesen Knochen und folgen
 * über ihre Haut — exakt wie der Server backt (am Käfig gemessen: 0,00000 mm, `ProjektTemp/_wegwerf/knochenwege_probe.py`;
 * Gelenkkorrekturen und Stoff kommen erst mit dem Neubau). Der Neubau läuft unverändert dahinter (`Genesis9lauf`); die
 * Wege bleiben an der Figur (`_posenwege`), damit die Kleidervorschau nach dem neuen Körper dieselben nimmt.
 */
export class Genesis9posenvorschau {

    /** Je Skelett der Rumpf der Stellung, in der es gebaut wurde — beim ersten Klick auf dieses Skelett gemerkt. */
    static _gebaut = new WeakMap();

    /**
     * @param feld     `pose` oder `ausdruck`
     * @param kennung  die neue Pose ('' = Ruhelage)
     * @returns true, wenn die Knochen stehen
     */
    static async zeigen(inst, feld, kennung) {
        const skelett = inst?.skelett;
        if (!skelett?.bones?.length || skelett.skeleton?.boneInverses?.length !== skelett.bones.length) return false;
        // Gemerkt beim ersten Blick: Ein zweiter Klick, während der erste Neubau schon läuft (die Figur trägt dann schon die
        // erste Pose), rechnet weiter von der Stellung, in der DIESES Skelett gebunden ist.
        if (!Genesis9posenvorschau._gebaut.has(skelett)) {
            Genesis9posenvorschau._gebaut.set(skelett, Genesis9materialabruf.nutzlast(inst));
        }
        const alt = Genesis9posenvorschau._gebaut.get(skelett);
        const neu = { ...Genesis9materialabruf.nutzlast(inst), [feld === 'ausdruck' ? 'ausdruck' : 'pose']: kennung || '' };
        const auftrag = inst._posenvorschau = (inst._posenvorschau || 0) + 1;
        let antwort;
        try {
            antwort = await Serverabruf.senden(
                `${inst.constructor.ADRESSE}${encodeURIComponent(inst.figur)}/knochenwege/`, { alt, neu });
        } catch (fehler) {
            Protokoll.warnung('Posenvorschau', `Knochenwege nicht geholt: ${fehler.message}`);
            return false;
        }
        // Ein neuerer Klick, oder der neue Körper ist schon da (anderes Skelett): nichts mehr zu zeigen.
        if (inst._posenvorschau !== auftrag || inst.skelett !== skelett || !antwort?.wege) return false;
        Genesis9posenvorschau.stellen(skelett, antwort.wege);
        const ziel = Genesis9posenvorschau._stellung(neu);
        inst._posenwege = {
            wege: antwort.wege,
            // Gilt für den Zug, der genau diese Stellung auf DIESES Skelett folgen lässt (`Kleidervorschau.merken`).
            gilt: (figur) => figur.skelett === skelett
                && Genesis9posenvorschau._stellung(Genesis9materialabruf.nutzlast(figur)) === ziel,
        };
        return true;
    }

    /**
     * Jeden Knochen auf `Weg · Bindelage` stellen (Raum der Figurgruppe); ein Knochen ohne eigenen Weg (Zunge, Zöpfe,
     * Endknochen) nimmt den seines nächsten Vorfahren. Lokal = Elternlage⁻¹ · Lage; die Wurzel hängt an der Gruppe.
     */
    static stellen(skelett, wege) {
        const { bones, skeleton } = skelett;
        const ziel = new Map();
        bones.forEach((k, i) => ziel.set(k, new THREE.Matrix4().copy(skeleton.boneInverses[i]).invert()));
        for (const k of bones) {
            let weg = null;
            for (let b = k; b?.isBone && !weg; b = b.parent) weg = wege[b.name] || null;
            if (weg) ziel.get(k).premultiply(new THREE.Matrix4().fromArray(weg));
        }
        const lokal = new THREE.Matrix4();
        for (const k of bones) {
            const eltern = ziel.get(k.parent);
            if (eltern) lokal.copy(eltern).invert().multiply(ziel.get(k));
            else lokal.copy(ziel.get(k));
            lokal.decompose(k.position, k.quaternion, k.scale);
        }
        skelett.rootBone?.updateMatrixWorld(true);
    }

    /** Was die Geometrie bestimmt: der Rumpf ohne die Materialfelder, als Text. */
    static _stellung(nutzlast) {
        const rest = { ...nutzlast };
        for (const feld of Genesis9materialabruf.MATERIAL) delete rest[feld];
        return JSON.stringify(rest);
    }
}
