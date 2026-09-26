import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Rigauswahl } from '../gemeinsam/rigauswahl.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';

/**
 * Rigsichtbarkeit — die Knochenlinien ALLER sichtbaren Figuren.
 *
 * WARUM (Edgar, 07.09.2026): „es gibt einen Button zum Rig ein und ausblenden.
 * das blendet das aber nur für HumanBody ein/aus. das soll für alle Modelle
 * sein die sichtbar sind."
 *
 * Der alte Umschalter (`menubar.toggleRigVisibility`) nahm `_selectedInst()`
 * und verwaltete genau EINEN `state.skeletonHelper`. Bei vier Figurarten in
 * einer Szene zeigte er das Rig einer Figur; wer eine zweite auswählte,
 * bekam trotzdem die Linien der ersten, weil der Helfer schon stand.
 *
 * Hier hält eine Map je Figur eine eigene Anzeige. Die Entscheidung, WELCHE
 * Figur Linien bekommt, steht in `gemeinsam/rigauswahl.js` — ohne Three.js
 * und deshalb prüfbar.
 *
 * `state.skeletonHelper` BLEIBT
 * =============================
 * Drei Stellen bauen sich selbst einen Helfer, wenn keiner da ist:
 * `animation.js` (zweimal) und `uma/umaanimation.js`. Würde diese Klasse ihn
 * ignorieren, stünden zwei Anzeigen auf demselben Skelett — doppelte Linien,
 * die niemand mehr wegbekommt. Deshalb wird ein vorhandener
 * `state.skeletonHelper` ÜBERNOMMEN, wenn er zur Wurzel einer Figur gehört
 * (`helfer.root`), statt einen zweiten zu bauen; und das Feld zeigt weiter auf
 * die Anzeige der ausgewählten Figur, damit jene drei Stellen unverändert
 * weiterlaufen.
 */
export class Rigsichtbarkeit {

    /** id der Figur -> {anzeige, wurzel}. */
    static _anzeigen = new Map();

    /**
     * Wie oft die Schleife nachsieht, ob Figuren dazugekommen sind.
     *
     * Nicht in jedem Bild: Bei 60 Bildern/s wäre das 60-mal je Sekunde ein
     * Durchgang durch alle Figuren samt Baumsuche. Eine halbe Sekunde ist
     * schnell genug, um beim Hinzufügen einer Figur nicht aufzufallen — der
     * Ladevorgang dauert selbst länger.
     */
    static ABGLEICH_MS = 500;

    static _letzterAbgleich = 0;

    // ------------------------------------------------------------- Umschalter

    /** Den Schalter kippen und anwenden. */
    static umschalten() {
        state.rigVisible = !state.rigVisible;
        Rigsichtbarkeit.anwenden();
        return state.rigVisible;
    }

    /**
     * Linien aufbauen, abräumen und schalten — für alle sichtbaren Figuren.
     *
     * Beim EINSCHALTEN wird für HumanBody-Figuren das Skelett nachgebaut, wenn
     * es noch fehlt (`convertInstToSkinned`). Das kostet, passiert aber nur
     * einmal je Figur und nur auf Knopfdruck.
     */
    static anwenden() {
        if (state.rigVisible) Rigsichtbarkeit._skeletteSicherstellen();
        const traeger = Rigauswahl.traeger(state.characters?.values(),
                                           Rigsichtbarkeit._suchen);
        const bestand = new Map(
            [...Rigsichtbarkeit._anzeigen].map(([id, e]) => [id, e.wurzel]));
        const { neu, ersetzt, weg } = Rigauswahl.abgleich(traeger, bestand);

        for (const id of weg) Rigsichtbarkeit._abraeumen(id);
        for (const t of ersetzt) Rigsichtbarkeit._abraeumen(t.inst.id);
        for (const t of [...neu, ...ersetzt]) Rigsichtbarkeit._bauen(t);

        for (const eintrag of Rigsichtbarkeit._anzeigen.values()) {
            eintrag.anzeige.visible = state.rigVisible;
        }
        Rigsichtbarkeit._ausgewaehlteMerken();
    }

    /**
     * Gedrosselter Abgleich aus der Renderschleife: Eine Figur, die nach dem
     * Einschalten dazukommt, soll ihre Linien von selbst bekommen.
     */
    static abgleichen(jetzt = performance.now()) {
        if (!state.rigVisible) return false;
        if (jetzt - Rigsichtbarkeit._letzterAbgleich < Rigsichtbarkeit.ABGLEICH_MS) {
            return false;
        }
        Rigsichtbarkeit._letzterAbgleich = jetzt;
        Rigsichtbarkeit.anwenden();
        return true;
    }

    /** Alles abräumen — beim Leeren der Szene. */
    static leeren() {
        for (const id of [...Rigsichtbarkeit._anzeigen.keys()]) {
            Rigsichtbarkeit._abraeumen(id);
        }
    }

    // -------------------------------------------------------------- Bausteine

    /**
     * Die Skelettwurzel im Szenenbaum einer Figur suchen.
     *
     * Der Ausweg für Figuren, die ihr Skelett in keinem bekannten Feld führen
     * — etwa ein importiertes GLB mit Rig. Gesucht wird der erste Knochen ohne
     * Knochen-Elternteil; `bones[0]` allein genügt nicht, die Reihenfolge im
     * Skelett ist nicht garantiert die Hierarchie.
     */
    static _suchen(inst) {
        let wurzel = null;
        inst.group?.traverse?.(o => {
            if (wurzel || !o.isSkinnedMesh || !o.skeleton) return;
            const knochen = o.skeleton.bones || [];
            wurzel = knochen.find(k => !k.parent || !k.parent.isBone)
                     || knochen[0] || null;
        });
        return wurzel;
    }

    /**
     * Fehlende Skelette der HumanBody-Figuren nachbauen.
     *
     * `convertInstToSkinned` wandelt das Netz in ein `SkinnedMesh` und hängt
     * das Rigify-Skelett daran. Ohne diesen Schritt hat eine frisch geladene
     * HumanBody-Figur keine Knochen, und der Schalter bliebe für sie wirkungslos
     * — genau das tat der alte Umschalter für alle nicht ausgewählten Figuren.
     */
    static _skeletteSicherstellen() {
        if (!state.rigifySkeletonData || !state.skinWeightData) return;
        if (!fn.convertInstToSkinned) return;
        for (const inst of (state.characters?.values() || [])) {
            if (!Rigauswahl.sichtbar(inst)) continue;
            if (Rigauswahl.wurzel(inst, Rigsichtbarkeit._suchen)) continue;
            // Nur HumanBody-Figuren: Die anderen Arten bringen ihr Skelett
            // mit oder haben keines, und `convertInstToSkinned` erwartet die
            // Netzfelder von `CharacterInstance`.
            if (inst.quelle) continue;
            try {
                fn.convertInstToSkinned(inst);
            } catch (fehler) {
                Protokoll.warnung('Rig', 'Skelett nicht baubar für', inst.id, fehler);
            }
        }
    }

    static _bauen({ inst, wurzel }) {
        // Einen schon stehenden Helfer derselben Wurzel übernehmen, statt
        // einen zweiten zu bauen (siehe Klassenkopf).
        const vorhanden = state.skeletonHelper?.root === wurzel
            ? state.skeletonHelper
            : Skelettanzeige.bauen(state.scene, wurzel, state.rigVisible);
        Rigsichtbarkeit._anzeigen.set(inst.id, { anzeige: vorhanden, wurzel });
    }

    static _abraeumen(id) {
        const eintrag = Rigsichtbarkeit._anzeigen.get(id);
        if (!eintrag) return;
        if (state.skeletonHelper === eintrag.anzeige) state.skeletonHelper = null;
        Skelettanzeige.entfernen(state.scene, eintrag.anzeige);
        Rigsichtbarkeit._anzeigen.delete(id);
    }

    /**
     * `state.skeletonHelper` auf die ausgewählte Figur zeigen lassen — die
     * drei Animationsstellen lesen es und würden sonst einen zweiten Helfer
     * bauen.
     */
    static _ausgewaehlteMerken() {
        const gewaehlt = state.selectedCharacterId;
        const eintrag = gewaehlt ? Rigsichtbarkeit._anzeigen.get(gewaehlt) : null;
        if (eintrag) state.skeletonHelper = eintrag.anzeige;
        else if (Rigsichtbarkeit._anzeigen.size) {
            state.skeletonHelper = [...Rigsichtbarkeit._anzeigen.values()][0].anzeige;
        }
    }
}
