/**
 * Modellbauzustand — was der Modellgenerator gerade bearbeitet.
 *
 * WARUM eine Klasse (Umbau 16.08.2026): Diese sechs Felder lagen als
 * `_mgConfig`, `_mgSelectedBone`, `_mgInitialized`, `_mgSkeletonType`,
 * `_mgRigBonesData`, `_mgCharacterId` im grossen `state`-Objekt der Szenenseite —
 * zwischen zweihundert anderen. Sie gehoeren zusammen, werden nur von drei
 * Modulen benutzt und beschreiben genau einen Vorgang.
 *
 * `konfig` bleibt bewusst ein Dictionary: Es IST das Dateiformat der
 * Modell-JSON und geht unveraendert an den Server. Eine Klasse dazwischen waere
 * eine zweite Beschreibung desselben Formats.
 */

export class Modellbauzustand {
    /** Modellbeschreibung (Dateiformat, Dictionary). */
    static konfig = null;
    /** Name des im Baum gewaehlten Knochens. */
    static gewaehlterKnochen = null;
    /** Sind die Bedienelemente schon angebunden? */
    static gebunden = false;
    /** 'rig' oder 'def'. */
    static skelettart = 'rig';
    /** Knochenliste des Rigify-Rigs, einmal geholt. */
    static rigKnochen = null;
    /** Charakter in der Szene, der dieses Modell zeigt. */
    static charakterId = null;

    /** Das gerade gewaehlte Knochenteil oder null. */
    static teil() {
        const k = Modellbauzustand.konfig;
        const name = Modellbauzustand.gewaehlterKnochen;
        if (!k || !name) return null;
        return k.bone_parts[name] || null;
    }

    /**
     * Rig-Knochen holen und merken.
     *
     * Diese Stelle stand viermal fast gleich im Code (dreimal in
     * modellgenerator_ui.js, einmal in character.js) — jedes Mal mit eigenem
     * try/catch und eigener Warnung.
     */
    static async rigKnochenLaden() {
        if (Modellbauzustand.rigKnochen) return Modellbauzustand.rigKnochen;
        try {
            const resp = await fetch('/api/character/rig/');
            if (resp.ok) Modellbauzustand.rigKnochen = await resp.json();
        } catch (e) {
            console.warn('Failed to load rig bones:', e);
        }
        return Modellbauzustand.rigKnochen;
    }

    /** Hat das Rig brauchbare Knochendaten? */
    static rigBrauchbar() {
        return !!Modellbauzustand.rigKnochen?.bones?.length;
    }

    /** Zustand aus einem geladenen Charakter uebernehmen. */
    static ausCharakter(inst) {
        Modellbauzustand.konfig = JSON.parse(JSON.stringify(inst.generatedConfig));
        Modellbauzustand.skelettart = inst.generatedConfig.skeleton_type || 'rig';
        Modellbauzustand.charakterId = inst.id;
    }
}
