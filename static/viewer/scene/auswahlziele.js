import { state } from './state.js';
import { Auswahlaura } from '../gemeinsam/auswahlaura.js';

/**
 * Auswahlziele — was die Szene gerade umrandet (`gemeinsam/auswahlaura.js`).
 *
 * Auswahl: das gewählte Teilnetz (Kleidung, Haar), sonst die ganze gewählte Figur
 * (Umriss um Körper und Stoff wie bei Blender). Hover: das Teilnetz unter der Maus, sonst
 * die Figur unter der Maus (`state._hoveredCharId`, `schwebeanzeige.js`).
 */
export class Auswahlziele {

    /** `[auswahl, hover]` als Netzlisten. */
    static jetzt() {
        return [Auswahlziele.auswahl(), Auswahlziele.hover()];
    }

    static auswahl() {
        if (state._selectedSubMesh?.meshObj) return Auswahlaura.netze(state._selectedSubMesh.meshObj);
        const inst = state.selectedCharacterId ? state.characters.get(state.selectedCharacterId) : null;
        return inst ? Auswahlziele.figur(inst) : [];
    }

    static hover() {
        if (state._hoveredSubMesh?.meshObj) return Auswahlaura.netze(state._hoveredSubMesh.meshObj);
        const inst = state._hoveredCharId ? state.characters.get(state._hoveredCharId) : null;
        return inst ? Auswahlziele.figur(inst) : [];
    }

    /** Die ganze Figur: Körper, Anhänge, Kleider, Haar (alles unter `inst.group`). Nur der
     *  Körper hätte seinen Umriss UNTER dem Stoff gezeigt — eine gezackte Linie quer über
     *  das Shirt (Bild im MCP-Tab, 25.09.2026). */
    static figur(inst) {
        return Auswahlaura.netze(inst.group || inst.bodyMesh);
    }
}
