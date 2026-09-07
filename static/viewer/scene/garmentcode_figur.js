import { state } from './state.js';

/**
 * GarmentcodeFigur — welche Figur der GarmentCode-Reiter meint, und was er
 * dem Server über sie schickt.
 *
 * Aus `garmentcode.js` herausgelöst (06.09.2026), als die Datei mit dem
 * SMPL-Zweig über 300 Zeilen ging. Die Entscheidung, WAS gesendet wird,
 * hängt an der Quelle der Figur:
 *
 *   HumanBody   Geschlecht, Bauart und die Morphs — der Server misst die
 *               Maße am Netz dieser Figur (`Koerpermasse`).
 *   SMPL        `koerper` und `smpl=1` — der Server nimmt die VORGEGEBENEN
 *               Maße von GarmentCode und drapiert auf diesem Körper; exakt
 *               der Weg des Online-Tools, ohne Messung.
 */
export class GarmentcodeFigur {

    /**
     * Die gewählte Figur aus der Szene, als `{id, inst}`. Ohne sie würde der
     * Grundkörper gemessen — der Schnitt passte dann zu einer Figur, die
     * niemand sieht.
     */
    static gewaehlt() {
        const id = state.selectedCharacterId || state.currentPropsCharId;
        if (!id || !state.characters) return null;
        const inst = state.characters.get(id);
        return inst ? { id, inst } : null;
    }

    /** Die Formulardaten für `/api/garmentcode/…` zu dieser Figur. */
    static formulardaten(figur) {
        const inst = figur.inst;
        const daten = new FormData();
        if (inst.quelle === 'smpl' && inst.koerper) {
            daten.append('koerper', inst.koerper);
            daten.append('geschlecht', inst.geschlecht || 'female');
            daten.append('morphs', '{}');
            return daten;
        }
        const bauart = inst.bodyType || inst.body_type || '';
        daten.append('geschlecht',
            bauart.toLowerCase().startsWith('m') ? 'male'
                : (inst.gender || 'female'));
        if (bauart) daten.append('bauart', bauart);
        daten.append('morphs', JSON.stringify(inst.morphs || {}));
        // Die Metaregler (height, mass, tone, age) gehören zur Figur wie
        // die Morphs — ohne sie wurde eine große Figur in Grundgröße
        // vermessen (06.09.2026).
        daten.append('meta', JSON.stringify(inst.meta || {}));
        return daten;
    }

    /**
     * Ohne Morphs wird der GRUNDKÖRPER vermessen, nicht die Figur auf dem
     * Bildschirm — und das sieht man dem Schnitt nicht an. Am 06.09.2026 hat
     * genau so ein Bau (Figur noch nicht geladen) den Ergebnisordner
     * überschrieben und eine Stunde Messungen verfälscht. Für einen
     * SMPL-Körper gilt das nicht: Er hat nie Morphs.
     */
    static ohneMorphs(figur) {
        const inst = figur?.inst;
        if (!inst || inst.quelle === 'smpl') return false;
        return Object.keys(inst.morphs || {}).length === 0;
    }
}
