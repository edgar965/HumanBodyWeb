import { state, API } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { wsSend, sendMorphThrottled } from './websocket.js';
import { getSkinMat, syncSkinUI, applySkinColor } from './scene_settings.js';
import { Hautfarbe } from '../gemeinsam/hautfarbe.js';
import { Morphliste } from '../gemeinsam/morphliste.js';
import { Metaregler } from '../gemeinsam/metaregler.js';
import { Hautbedienung } from './hautbedienung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Morphbedienung — das Morph-Feld der Viewer-Seite: Körperart, Metaregler,
 * Hautmaterial, Morph-Kategorien und der Reset-Knopf.
 *
 * Aus viewer/morphs.js herausgeloest (Umbau 16.08.2026): `loadMorphs()` hatte
 * 193 Zeilen. Vier Dinge daran lagen mehrfach im Projekt und sind jetzt
 * gemeinsam: die Gamma-Korrektur der Hautfarbe (`Hautfarbe`, war 8×), die
 * Morph-Kategorienliste (`Morphliste`, war 5×), die Meta-Umrechnung
 * (`Metaregler`, war 5×) und die zwei Materialregler (`Hautbedienung`).
 */
export class Morphbedienung {

    /** Vorgaben der Haut beim Zurücksetzen. */
    static HAUT_RAUHEIT = 0.55;
    static HAUT_METALL = 0.0;

    constructor(daten) {
        this.daten = daten;
        this.artwahl = document.getElementById('body-type-select');
        this.feld = document.getElementById('morphs-panel');
        this.liste = new Morphliste({
            geaendert: (name, wert) => sendMorphThrottled(name, wert),
        });
    }

    /** Morphdaten holen und die Bedienung aufbauen. */
    static async laden() {
        try {
            const daten = await Serverabruf.json(`${API}/morphs/`);
            state.skinColors = daten.skin_colors || {};
            return new Morphbedienung(daten).bauen();
        } catch (fehler) {
            console.error('Morphs nicht ladbar:', fehler);
            return null;
        }
    }

    bauen() {
        this.koerperart();
        Metaregler.verdrahten(this.daten.meta_sliders,
                              (name, wert) => wsSend({ type: 'meta', name, value: wert }));
        Hautbedienung.verdrahten();
        this.morphliste();
        this.zuruecksetzenKnopf();
        applySkinColor();
        return this;
    }

    koerperart() {
        if (!this.artwahl) return;
        for (const art of this.daten.body_types) {
            this.artwahl.appendChild(new Option(art.replace('_', ' '), art));
        }
        this.artwahl.addEventListener('change', () => {
            wsSend({ type: 'body_type', value: this.artwahl.value });
            this.hautNachziehen();
            // Männliche Körper haben andere Maße; anliegende Kleidung würde
            // sonst im Körper stecken.
            if (this.artwahl.value.startsWith('Male_')) fn.removeAllCloth();
        });
    }

    hautNachziehen() {
        const material = getSkinMat();
        if (Hautfarbe.ausKoerperart(material, this.artwahl.value,
                                    this.daten.skin_colors)) {
            syncSkinUI(material);
        }
    }

    morphliste() {
        // `state.morphCategories` wurde hier früher gefüllt und nirgends
        // gelesen — das Feld ist mit dem Umbau entfallen.
        if (!this.feld) return;
        this.liste.bauen(this.feld, this.daten.morphs, this.daten.categories);
    }

    // ------------------------------------------------------------ Zurücksetzen

    zuruecksetzenKnopf() {
        document.getElementById('reset-morphs')
            ?.addEventListener('click', () => this.zuruecksetzen());
    }

    zuruecksetzen() {
        if (this.feld) Morphliste.zuruecksetzen(this.feld);
        Metaregler.zuruecksetzen(this.daten.meta_sliders);
        this.hautZuruecksetzen();
        wsSend({ type: 'reset', body_type: this.artwahl?.value });
    }

    hautZuruecksetzen() {
        const material = getSkinMat();
        if (!material) return;
        if (!Hautfarbe.ausKoerperart(material, this.artwahl?.value,
                                     this.daten.skin_colors)) {
            material.color.setHex(Hautfarbe.ERSATZ_FARBE);
        }
        material.roughness = Morphbedienung.HAUT_RAUHEIT;
        material.metalness = Morphbedienung.HAUT_METALL;
        Hautbedienung.zuruecksetzen(material);
    }
}
