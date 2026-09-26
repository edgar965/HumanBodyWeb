import { zahlen, zeilenMajor } from './colladaxml.js';

/**
 * Colladaanimation — den laufenden Clip abtasten und als
 * `<library_animations>` schreiben, EIN `<animation>` je Knochen.
 *
 * ABGETASTET, NICHT AUS DEN ORIGINAL-KEYFRAMES (26.09.2026, wie
 * `_sampleBoneMatrices` in `cloth_export.js`): So ist egal, wie der Clip
 * intern aufgebaut ist (Quaternion-Spuren, Retarget-Zwischenschritte,
 * unterschiedliche Bildraten je Knochen) — es kommt am Ende dasselbe heraus,
 * was gerade auf der Bühne zu sehen ist.
 *
 * `bone.matrix` NACH `wurzel.updateMatrixWorld(true)` ist die LOKALE Lage
 * relativ zum Elternknochen — genau das, was `<node><matrix>` erwartet, ohne
 * eigene Umrechnung.
 */
export class Colladaanimation {

    static FPS = 30;

    /**
     * @param wurzel  `inst.group` — ihr `updateMatrixWorld` zieht Skelett
     *                UND Mixer-Ergebnis nach
     * @param mixer, action  `state.mixer`, `state.currentAction`
     * @param skeleton  `mesh.skeleton`
     * @param sids  wie `Colladaskin.knochenSids(skeleton)`
     */
    static bauen(wurzel, mixer, action, skeleton, sids) {
        const clip = action.getClip();
        const dauer = Math.max(clip.duration, 1 / Colladaanimation.FPS);
        const bilder = Math.max(2, Math.ceil(dauer * Colladaanimation.FPS) + 1);
        const urTime = action.time;
        const urPaused = action.paused;

        const zeiten = [];
        const matrizen = skeleton.bones.map(() => []);
        action.play();
        action.paused = true;
        for (let f = 0; f < bilder; f++) {
            const t = Math.min(f / Colladaanimation.FPS, dauer);
            action.time = t;
            mixer.update(0);
            wurzel.updateMatrixWorld(true);
            zeiten.push(t);
            skeleton.bones.forEach((bone, i) => matrizen[i].push(zeilenMajor(bone.matrix)));
        }
        action.time = urTime;
        action.paused = urPaused;
        mixer.update(0);
        wurzel.updateMatrixWorld(true);

        return sids.map((sid, i) => Colladaanimation._knochenXml(sid, zeiten, matrizen[i])).join('');
    }

    static _knochenXml(sid, zeiten, matrizen) {
        const id = `anim-${sid}`;
        const werte = matrizen.flat();
        const interp = zeiten.map(() => 'LINEAR').join(' ');
        return `<animation id="${id}">`
            + `<source id="${id}-in"><float_array id="${id}-in-array" count="${zeiten.length}">`
            + `${zahlen(zeiten)}</float_array><technique_common><accessor source="#${id}-in-array" `
            + `count="${zeiten.length}" stride="1"><param name="TIME" type="float"/></accessor></technique_common></source>`
            + `<source id="${id}-out"><float_array id="${id}-out-array" count="${werte.length}">`
            + `${zahlen(werte)}</float_array><technique_common><accessor source="#${id}-out-array" `
            + `count="${zeiten.length}" stride="16"><param name="TRANSFORM" type="float4x4"/></accessor></technique_common></source>`
            + `<source id="${id}-interp"><Name_array id="${id}-interp-array" count="${zeiten.length}">`
            + `${interp}</Name_array><technique_common><accessor source="#${id}-interp-array" `
            + `count="${zeiten.length}" stride="1"><param name="INTERPOLATION" type="Name"/></accessor></technique_common></source>`
            + `<sampler id="${id}-sampler"><input semantic="INPUT" source="#${id}-in"/>`
            + `<input semantic="OUTPUT" source="#${id}-out"/><input semantic="INTERPOLATION" source="#${id}-interp"/></sampler>`
            + `<channel source="#${id}-sampler" target="${sid}/matrix"/>`
            + '</animation>';
    }
}
