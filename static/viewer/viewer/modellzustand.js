import { state } from './state.js';
import { Metawerte } from './metawerte.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Modellzustand — den Stand der Modellseite einsammeln und speichern.
 *
 * Herausgelöst aus `presets.js` (352 Zeilen). Was hier NICHT hineinkommt, ist
 * genauso wichtig wie der Inhalt:
 *
 * * **Morphs mit Wert 0** werden weggelassen. Eine Vorgabe hat sonst 400 Nullen,
 *   und beim Anwenden macht es keinen Unterschied — `Modellvorgabe` stellt jeden
 *   nicht genannten Regler ohnehin auf 0.
 * * **Kleidungsstücke ohne Netz** fallen weg: `state.garmentState` behält den
 *   Stand auch von Stücken, die der Nutzer wieder ausgezogen hat.
 *
 * Die Szeneneinstellungen kommen aus dem `localStorage`, weil sie dort auch die
 * Beleuchtungs-Bedienung ablegt — eine zweite Quelle wäre eine zweite Wahrheit.
 */
export class Modellzustand {

    static SZENENSCHLUESSEL = 'humanbody_scene_settings';
    static LETZTER = 'humanbody_current_model';

    /** Die Felder, die zu einem Kleidungsstück gespeichert werden. */
    static KLEIDERFELDER = ['offset', 'stiffness', 'color', 'roughness',
                            'metalness', 'posX', 'posY', 'posZ',
                            'scaleX', 'scaleY', 'scaleZ'];

    /** Der komplette Stand als Vorgabe-Objekt. */
    static einsammeln() {
        const stand = { meta: Metawerte.auslesen(), morphs: Modellzustand._morphs(),
                        cloth: Modellzustand._stoffe(),
                        wardrobe: Modellzustand._garderobe(),
                        garments: Modellzustand._kleider() };
        const koerper = document.getElementById('body-type-select');
        if (koerper) stand.body_type = koerper.value;
        const haare = Modellzustand._haare();
        if (haare) stand.hair_style = haare;
        const szene = Modellzustand._szene();
        if (szene) stand.scene = szene;
        return stand;
    }

    static _morphs() {
        const werte = {};
        document.getElementById('morphs-panel')
            ?.querySelectorAll('input[type="range"][data-morph]')
            .forEach(regler => {
                const wert = parseInt(regler.value);
                if (wert !== 0) werte[regler.dataset.morph] = wert / 100;
            });
        return werte;
    }

    /** Die Stoffsimulationen — je nach Verfahren andere Felder. */
    static _stoffe() {
        const liste = [];
        for (const angabe of Object.values(state.clothParams)) {
            const p = angabe.params;
            const eintrag = {};
            if (p.method === 'template') {
                eintrag.template = p.template;
                eintrag.tightness = p.tightness !== undefined ? p.tightness : 0.5;
                eintrag.segments = p.segments || 32;
                if (p.top_extend) eintrag.top_extend = p.top_extend;
                if (p.bottom_extend) eintrag.bottom_extend = p.bottom_extend;
            } else if (p.method === 'builder') {
                Object.assign(eintrag, { method: 'builder', region: p.region,
                                         looseness: p.looseness });
            } else if (p.method === 'primitive') {
                Object.assign(eintrag, { method: 'primitive', prim_type: p.prim_type,
                                         segments: p.segments, length: p.length });
                if (p.flare) eintrag.flare = p.flare;
            }
            eintrag.color = angabe.color;
            liste.push(eintrag);
        }
        return liste;
    }

    static _haare() {
        const stil = document.getElementById('hair-style-select');
        if (!stil?.value) return null;
        const farbe = document.getElementById('hair-color-select');
        return { url: stil.value,
                 name: stil.options[stil.selectedIndex]?.textContent || '',
                 color: farbe ? farbe.value : '' };
    }

    static _garderobe() {
        const teile = [];
        document.getElementById('wardrobe-panel')
            ?.querySelectorAll('.asset-btn.active')
            .forEach(knopf => teile.push(knopf.dataset.asset));
        return teile;
    }

    static _kleider() {
        const liste = [];
        for (const [kennung, zustand] of Object.entries(state.garmentState)) {
            if (!state.garmentMeshes[kennung]) continue;   // ausgezogen
            const eintrag = { id: kennung };
            for (const feld of Modellzustand.KLEIDERFELDER) {
                eintrag[feld] = zustand[feld];
            }
            liste.push(eintrag);
        }
        return liste;
    }

    static _szene() {
        const gemerkt = localStorage.getItem(Modellzustand.SZENENSCHLUESSEL);
        if (!gemerkt) return null;
        try {
            return JSON.parse(gemerkt);
        } catch (fehler) {
            Protokoll.warnung('presets', 'Szeneneinstellungen unlesbar', fehler);
            return null;
        }
    }

    // ---------------------------------------------------------------- Sichern

    /** Den letzten Stand für den nächsten Seitenaufruf merken. */
    static merken() {
        try {
            localStorage.setItem(Modellzustand.LETZTER,
                                 JSON.stringify(Modellzustand.einsammeln()));
        } catch (fehler) {
            Protokoll.warnung('presets', 'Stand nicht merkbar', fehler);
        }
    }

    /** Unter einem Namen auf dem Server speichern; `true` bei Erfolg. */
    static async speichern(name) {
        const daten = Modellzustand.einsammeln();
        daten.name = name;
        try {
            const antwort = await Serverabruf.senden(
                '/api/character/model/save/', { name, data: daten });
            if (!antwort.ok) {
                alert('Fehler beim Speichern: ' + (antwort.error || 'Unbekannt'));
                return false;
            }
            state.currentPresetName = name;
            Protokoll.info('Viewer', `Modell gespeichert: ${antwort.filename}`);
            return true;
        } catch (fehler) {
            Protokoll.fehler('presets', 'Speichern fehlgeschlagen', fehler);
            alert('Fehler beim Speichern: ' + fehler.message);
            return false;
        }
    }
}
