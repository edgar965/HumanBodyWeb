/**
 * Vergleichsregler — Morph- und Grundregler einer Vergleichsspalte fuellen
 * und anbinden.
 *
 * Aus `loadMorphs` in viewer_compare.js herausgeloest (Umbau 16.08.2026): eine
 * Funktion mit 150 Zeilen, die Auswahlliste, vier Grundregler, drei Hautregler
 * und die gesamte Morph-Liste in einem Stueck aufbaute.
 */
import { Vergleichsnetz } from './vergleichsnetz.js';
import { GRUNDREGLER } from './vergleichspanel.js';
import { Hautfarbe } from '../gemeinsam/hautfarbe.js';
import { Metaregler } from '../gemeinsam/metaregler.js';
import { Morphliste } from '../gemeinsam/morphliste.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/** Vorgabe-Hautfarbe, wenn die Herkunft keine kennt. */
const HAUTVORGABE = Hautfarbe.ERSATZ_FARBE;

export class Vergleichsregler {
    static async laden(ansicht) {
        try {
            const daten = await Serverabruf.json(ansicht.apiPrefix + '/morphs/');
            ansicht.morphData = daten;
            ansicht.skinColorMap = daten.skin_colors || {};
            Vergleichsregler._koerperarten(ansicht, daten);
            Vergleichsregler._grundregler(ansicht, daten);
            Vergleichsregler._hautregler(ansicht);
            Vergleichsregler._morphliste(ansicht, daten);
            // Das Netz kann schon geladen sein — Farbe jetzt setzen.
            Vergleichsnetz.hautfarbeAnwenden(ansicht);
        } catch (e) {
            console.error(`[${ansicht.label}] Failed to load morphs:`, e);
        }
    }

    static _koerperarten(ansicht, daten) {
        const auswahl = ansicht.felder.koerperart;
        for (const art of daten.body_types) {
            const eintrag = document.createElement('option');
            eintrag.value = art;
            eintrag.textContent = art.replace(/_/g, ' ');
            auswahl.appendChild(eintrag);
        }
        if (ansicht.defaultBodyType
            && daten.body_types.includes(ansicht.defaultBodyType)) {
            auswahl.value = ansicht.defaultBodyType;
        }
        auswahl.addEventListener('change', () => {
            ansicht.funk.senden({ type: 'body_type', value: auswahl.value });
            Vergleichsnetz.hautfarbeAnwenden(ansicht);
        });
    }

    static _grundregler(ansicht, daten) {
        for (const [name] of GRUNDREGLER) {
            const els = ansicht.felder.grundregler[name];
            if (!els) continue;
            // Die Vergleichsseite hat ihre Regler in `felder.grundregler`,
            // nicht unter `meta-<name>` — deshalb hier `grenzenSetzen` von Hand.
            Metaregler.grenzenSetzen({ regler: els.slider, anzeige: els.val },
                                     daten.meta_sliders?.[name]);
            els.slider.addEventListener('input', () => {
                els.val.textContent = els.slider.value;
                ansicht.funk.senden({
                    type: 'meta', name,
                    value: Metaregler.ausRegler(els.slider),
                });
            });
        }
    }

    static _hautregler(ansicht) {
        const f = ansicht.felder;
        f.hautfarbe?.addEventListener('input', (e) => {
            const material = Vergleichsnetz.hautmaterial(ansicht);
            if (material) material.color.set(e.target.value);
        });
        const anteil = (regler, anzeige, feld) => {
            regler?.addEventListener('input', () => {
                const wert = parseFloat(regler.value) / 100;
                anzeige.textContent = wert.toFixed(2);
                const material = Vergleichsnetz.hautmaterial(ansicht);
                if (material) material[feld] = wert;
            });
        };
        anteil(f.rauheit, f.rauheitWert, 'roughness');
        anteil(f.metall, f.metallWert, 'metalness');
    }

    /**
     * Die Morph-Liste kommt aus `Morphliste` — dieselbe Liste wie auf der
     * Viewer-, Foto- und Ergebnisseite. Vorher stand sie hier als eigene
     * `_kategorie`/`_morphzeile`-Kopie.
     */
    static _morphliste(ansicht, daten) {
        const liste = new Morphliste({
            geaendert: (name, wert) => ansicht.funk.morphGebremst(name, wert),
        });
        liste.bauen(ansicht.felder.morphliste, daten.morphs, daten.categories);
    }

    /** Alle Regler auf ihre Vorgaben zuruecksetzen. */
    static zuruecksetzen(ansicht) {
        const f = ansicht.felder;
        if (f.morphliste) Morphliste.zuruecksetzen(f.morphliste);
        for (const [name] of GRUNDREGLER) {
            const els = f.grundregler[name];
            if (!els) continue;
            Metaregler.grenzenSetzen({ regler: els.slider, anzeige: els.val },
                                     ansicht.morphData?.meta_sliders?.[name]);
        }
        Vergleichsregler._hautZuruecksetzen(ansicht);
        ansicht.funk.senden({
            type: 'reset',
            body_type: f.koerperart?.value || ansicht.defaultBodyType,
        });
    }

    static _hautZuruecksetzen(ansicht) {
        const material = Vergleichsnetz.hautmaterial(ansicht);
        if (!material) return;
        const art = ansicht.felder.koerperart?.value || '';
        if (!Hautfarbe.ausKoerperart(material, art, ansicht.skinColorMap)) {
            material.color.setHex(HAUTVORGABE);
        }
        material.roughness = 0.55;
        material.metalness = 0.0;
        Vergleichsnetz.reglerNachziehen(ansicht, material);
    }
}
