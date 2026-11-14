/**
 * Fusshaltung — die Fußdeltas einer Figur (Absatz der Pose, Fußhaltung der Schuhe) nach dem Mixer auf die Knochen mischen.
 *
 * Aus `charakter/posenabsatz.js` herausgelöst (12.11.2026), weil das BVH Studio dieselbe Mischung braucht: Die Stiefel des Fallout Rangers
 * bringen eine Fußhaltung mit (`griff`, Fuß 60° gedreht); der Mixer stellt die Füße je Bild neu, ohne sie kippt der Stiefel gegen das Bein
 * (Tagebuch `Docu/tagebuch/2026-11-12_fallout-ranger-stiefel.md`). Die Charakter-Seite mischt seit dem 12.11.2026 (`Posenabsatz.nachMixer`),
 * das Studio stellte die Spur ohne (`studio/bvhspur.js`). Das Theatre zeigt keine Genesis-9-Figuren.
 *
 * `figur.absatzDeltas` = `{knochenname: [x, y, z, w]}` (Genesis: `griffdeltas` der Körperantwort, `Genesis9Modell`); gemischt wird nur ein
 * Knochen, den der Mixer seit dem letzten Mischen neu gesetzt hat (`figur._absatzGemischt`) — sonst summierte sich die Drehung Bild für Bild.
 */
export class Fusshaltung {

    /** Fußdeltas auf die Knochen multiplizieren, die der Mixer neu gesetzt hat; gibt die Zahl der gemischten Knochen zurück. */
    static mischen(figur) {
        if (!figur?.absatzDeltas || !figur.group) return 0;
        let skelett = null;
        figur.group.traverse((teil) => {
            if (!skelett && teil.isSkinnedMesh && teil.skeleton) skelett = teil.skeleton;
        });
        if (!skelett) return 0;
        const gemischt = figur._absatzGemischt || (figur._absatzGemischt = {});
        let n = 0;
        for (const [name, wert] of Object.entries(figur.absatzDeltas)) {
            const knochen = skelett.getBoneByName(name.replace(/\./g, '_'));
            if (!knochen) continue;
            const vorher = gemischt[name];
            if (vorher && knochen.quaternion.equals(vorher)) continue;
            const Quat = knochen.quaternion.constructor;
            knochen.quaternion.multiply(new Quat(wert[0], wert[1], wert[2], wert[3]));
            gemischt[name] = knochen.quaternion.clone();
            n++;
        }
        return n;
    }
}
