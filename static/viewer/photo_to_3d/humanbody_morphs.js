/**
 * Photo To 3D — Morph-Bedienung: Körperart, Metaregler, Morph-Liste.
 *
 * Umbau 16.08.2026: `buildMorphPanel()` baute die Kategorienliste Zeile für
 * Zeile genauso wie viewer/morphs.js, scene/properties.js,
 * vergleich/vergleichsregler.js und result_character — fünf Kopien derselben
 * Liste. Sie kommt jetzt aus `Morphliste`, die Meta-Umrechnung aus
 * `Metaregler`.
 */
import { state, API } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Morphliste } from '../gemeinsam/morphliste.js';
import { Metaregler } from '../gemeinsam/metaregler.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/** Die Liste dieser Seite: Startwert aus `morphValues`, Änderung neu rechnen. */
const liste = new Morphliste({
    startwert: name => state.morphValues[name],
    geaendert: (name, wert) => {
        state.morphValues[name] = wert;
        fn.requestMeshUpdate();
    },
});

export async function loadMorphs() {
    try {
        state.morphsData = await Serverabruf.json(`${API}/morphs/`);
    } catch (fehler) {
        Protokoll.fehler('Morphs', 'Liste nicht ladbar:', fehler);
        return;
    }
    const daten = state.morphsData;
    state.skinColors = daten.skin_colors || {};

    koerperartwahl(daten);
    Metaregler.verdrahten(daten.meta_sliders, (name, wert) => {
        state.metaValues[name] = wert;
        fn.requestMeshUpdate();
    });
    hautfarbwahl();
    buildMorphPanel(daten);
    zuruecksetzenKnopf();
}

function koerperartwahl(daten) {
    const feld = document.getElementById('body-type-select');
    if (!feld) return;
    for (const art of daten.body_types) {
        feld.appendChild(new Option(art.replace('_', ' '), art));
    }
    feld.value = state.currentBodyType;
    feld.addEventListener('change', () => koerperartWechseln(feld.value));
}

/**
 * Beim Wechsel des Geschlechts müssen die Hautgewichte neu geholt werden —
 * männliche und weibliche Netze haben verschiedene Vertexzahlen.
 */
async function koerperartWechseln(neueArt) {
    const vorher = geschlecht(state.currentBodyType);
    state.currentBodyType = neueArt;
    if (vorher !== geschlecht(neueArt)) {
        try {
            const adresse = `${API}/skin-weights/?body_type=`
                + encodeURIComponent(neueArt);
            state.skinWeightData = await Serverabruf.json(adresse);
        } catch (fehler) {
            Protokoll.warnung('Morphs', 'Hautgewichte nicht ladbar:', fehler);
        }
    }
    await fn.loadMesh(neueArt);
    const adresse = `${API}/morphs/?body_type=` + encodeURIComponent(neueArt);
    try {
        state.morphsData = await Serverabruf.json(adresse);
    } catch (fehler) {
        // Ohne diesen Fänger endet der Wechsel in einer stillen
        // "Unhandled promise rejection": Die Reglerliste bliebe die der alten
        // Körperart, ohne dass jemand etwas merkt.
        Protokoll.fehler('Morphs', 'Körperart nicht ladbar:', fehler);
        alert('Die Morph-Liste für ' + neueArt + ' ist nicht ladbar: '
              + fehler.message);
        return;
    }
    state.skinColors = state.morphsData.skin_colors || {};
    buildMorphPanel(state.morphsData);
}

function geschlecht(koerperart) {
    return koerperart.startsWith('Male_') ? 'male' : 'female';
}

function hautfarbwahl() {
    document.getElementById('skin-color-viewer')
        ?.addEventListener('input', ereignis => {
            const material = state.bodyMesh?.material;
            const haut = Array.isArray(material) ? material[0] : material;
            if (haut) haut.color.set(ereignis.target.value);
        });
}

function zuruecksetzenKnopf() {
    const feld = document.getElementById('morphs-panel');
    document.getElementById('reset-morphs')?.addEventListener('click', () => {
        state.morphValues = {};
        if (feld) Morphliste.zuruecksetzen(feld);
        fn.requestMeshUpdate();
    });
}

export function buildMorphPanel(daten) {
    const feld = document.getElementById('morphs-panel');
    if (feld) liste.bauen(feld, daten.morphs, daten.categories);
}

fn.loadMorphs = loadMorphs;
fn.buildMorphPanel = buildMorphPanel;
