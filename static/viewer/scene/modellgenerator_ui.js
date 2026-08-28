/**
 * Modellgenerator — der Modell-Reiter der Szenenseite.
 *
 * WARUM diese Datei jetzt klein ist (Umbau 16.08.2026): Sie hatte 887 Zeilen,
 * darunter eine Bedienfunktion mit 276 Zeilen und eine Auswahlfunktion mit 144.
 * Beide bestanden fast nur aus derselben Zeile in Varianten: Element holen,
 * Wert lesen, in `bone_parts[gewaehlt]` schreiben, neu aufbauen. Das steht jetzt
 * als Tabelle in zwei Modulen:
 *
 *   modellgenerator/zustand.js         was gerade bearbeitet wird
 *   modellgenerator/formregler.js      formabhaengige Parameter (31 Regler)
 *   modellgenerator/knochenregler.js   Radius, Farbe, Versatz, Drehung, Textur
 *   modellgenerator/knochenbaum.js     die Liste links
 *   modellgenerator/knochenauswahl.js  Knochen waehlen
 *   modellgenerator/erzeugung.js       Netz bauen, Charakter setzen
 *   modellgenerator/speicher.js        Datei und Server
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _selectedInst } from './utils.js';
import { getDefaultModelConfig, getDefaultRigConfig } from './state.js';
import { Modellbauzustand } from './modellgenerator/zustand.js';
import { Formregler } from './modellgenerator/formregler.js';
import { Knochenregler } from './modellgenerator/knochenregler.js';
import { Knochenbaum } from './modellgenerator/knochenbaum.js';
import { Knochenauswahl } from './modellgenerator/knochenauswahl.js';
import { Modellerzeugung } from './modellgenerator/erzeugung.js';
import { Modellspeicher } from './modellgenerator/speicher.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Modellgenerator {
    static async starten() {
        if (!state.rigifySkeletonData || !state.skinWeightData) {
            Protokoll.warnung('modellgenerator_ui', 'Model Generator: skeleton data not loaded yet');
            return;
        }
        if (!Modellbauzustand.konfig) await Modellgenerator._konfigBeschaffen();
        Modellgenerator._anlaufen();
        document.querySelectorAll('#tab-modell .panel-section')
            .forEach(p => p.classList.remove('collapsed'));
    }

    /** Konfiguration aus einem geladenen Charakter oder als Vorgabe. */
    static async _konfigBeschaffen() {
        const gewaehlt = _selectedInst();
        const inst = (gewaehlt?.generatedConfig) ? gewaehlt
            : [...state.characters.values()].find(c => c.generatedConfig) || null;
        if (inst?.generatedConfig) {
            Modellbauzustand.ausCharakter(inst);
            if (Modellbauzustand.skelettart === 'rig') {
                await Modellbauzustand.rigKnochenLaden();
            }
            Protokoll.debug('MG', 'Konfiguration vom geladenen Charakter '
                            + 'uebernommen:', inst.presetName);
            return;
        }
        await Modellgenerator._vorgabeKonfig();
    }

    /** Vorgabekonfiguration passend zur eingestellten Skelettart. */
    static async _vorgabeKonfig() {
        if (Modellbauzustand.skelettart === 'rig') {
            await Modellbauzustand.rigKnochenLaden();
            if (Modellbauzustand.rigBrauchbar()) {
                Modellbauzustand.konfig = getDefaultRigConfig(Modellbauzustand.rigKnochen);
                return true;
            }
            Modellbauzustand.skelettart = 'def';   // ohne Rig-Daten auf DEF zurueck
        }
        Modellbauzustand.konfig = getDefaultModelConfig(state.rigifySkeletonData,
                                                        state.skinWeightData);
        return true;
    }

    /**
     * Einmal binden, Skelettart nachziehen, Baum und Regler aufbauen.
     *
     * WARUM ALS EIGENER SCHRITT (28.08.2026, Befund `doppelcode`): Diese acht
     * Zeilen standen zweimal in DIESER Datei — in `starten()` und in
     * `knochenklick()`. Sie hängen zusammen und müssen in dieser Reihenfolge
     * laufen: `binden()` zuerst, sonst hängen die Ereignisse an Elementen,
     * die der Baumaufbau gleich wieder ersetzt.
     *
     * `gebunden` ist die Sperre dagegen, zweimal zu binden. Ohne sie feuert
     * jeder Regler doppelt — und das sieht man nicht, man merkt es nur daran,
     * dass das Modell zweimal neu gebaut wird.
     */
    static _anlaufen() {
        if (!Modellbauzustand.gebunden) {
            Modellgenerator.binden();
            Modellbauzustand.gebunden = true;
        }
        const art = document.getElementById('mg-skeleton-type');
        if (art) art.value = Modellbauzustand.skelettart;
        Modellgenerator.baumAufbauen();
        Modellgenerator.globalreglerNachziehen();
    }

    static baumAufbauen() {
        Knochenbaum.aufbauen(Knochenauswahl.waehlen, Modellerzeugung.anfordern);
    }

    static binden() {
        Modellgenerator._skelettartBinden();
        Modellgenerator._globalreglerBinden();
        Formregler.binden(Modellerzeugung.anfordern);
        Knochenregler.binden(Modellerzeugung.anfordern,
                             Modellgenerator._formGewechselt,
                             Knochenbaum.eintragAuffrischen);
        document.getElementById('mg-generate')
            ?.addEventListener('click', () => Modellerzeugung.charakterBauen());
        document.getElementById('mg-save-server')
            ?.addEventListener('click', () => Modellspeicher.speichern());
    }

    static _formGewechselt(form) {
        Formregler.gruppeZeigen(form);
        Modellerzeugung.anfordern();
    }

    static _skelettartBinden() {
        const auswahl = document.getElementById('mg-skeleton-type');
        if (!auswahl) return;
        auswahl.addEventListener('change', async () => {
            const neu = auswahl.value;
            if (neu === Modellbauzustand.skelettart) return;
            Modellbauzustand.skelettart = neu;
            await Modellgenerator._vorgabeKonfig();
            // Faellt _vorgabeKonfig auf DEF zurueck, muss die Auswahl mitziehen.
            auswahl.value = Modellbauzustand.skelettart;

            Modellbauzustand.gewaehlterKnochen = null;
            fn._clearBoneHighlightCache();
            const abschnitt = document.getElementById('mg-bone-props-section');
            if (abschnitt) abschnitt.style.display = 'none';
            Modellgenerator.baumAufbauen();
            Modellgenerator.globalreglerNachziehen();
        });
    }

    static _globalreglerBinden() {
        const text = (id, feld, marke) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.addEventListener('input', () => { Modellbauzustand.konfig[feld] = el.value; });
            el.addEventListener('change', () => fn.markDirty?.(marke));
        };
        text('mg-model-name', 'name', 'Modellname');
        text('mg-default-color', 'default_color', 'Standardfarbe');

        const zahl = (id, feld, wandeln, stellen) => {
            const el = document.getElementById(id);
            if (!el) return;
            const anzeige = document.getElementById(id + '-val');
            el.addEventListener('input', () => {
                const v = wandeln(el.value);
                Modellbauzustand.konfig[feld] = v;
                if (anzeige) anzeige.textContent = stellen ? v.toFixed(stellen) : v;
            });
        };
        zahl('mg-default-radius', 'default_radius', parseFloat, 3);
        zahl('mg-segments', 'segments', parseInt, 0);
    }

    static globalreglerNachziehen() {
        const k = Modellbauzustand.konfig;
        if (!k) return;
        const setzen = (id, wert, text) => {
            const el = document.getElementById(id);
            if (el) el.value = wert;
            const anzeige = document.getElementById(id + '-val');
            if (anzeige && text !== undefined) anzeige.textContent = text;
        };
        setzen('mg-model-name', k.name || 'Neues Modell');
        setzen('mg-default-color', k.default_color || '#4488cc');
        setzen('mg-default-radius', k.default_radius || 0.03,
               (k.default_radius || 0.03).toFixed(3));
        setzen('mg-segments', k.segments || 8, k.segments || 8);
    }

    /**
     * Strg+Klick auf einen Knochen des erzeugten Modells.
     *
     * Zweimal denselben Knochen anklicken hebt die Auswahl wieder auf.
     */
    static knochenklick(name, inst) {
        if (!Modellbauzustand.konfig && inst.generatedConfig) {
            Modellbauzustand.ausCharakter(inst);
            Modellgenerator._anlaufen();
        }
        if (!Modellbauzustand.charakterId && inst.generatedConfig) {
            Modellbauzustand.ausCharakter(inst);
            Modellgenerator.baumAufbauen();
        }
        if (state._selectedBoneName === name) {
            fn._clearBoneSelection();
            Knochenauswahl.aufheben();
            return;
        }
        fn._clearBoneSelection();
        state._selectedBoneName = name;
        if (inst.bodyMesh) {
            state._boneSelectOverlay = fn._createBoneOverlay(
                inst.bodyMesh, name, state._BONE_SELECT_MAT);
        }
        Knochenauswahl.waehlen(name);
        fn.switchTab('modell');
        document.getElementById('mg-bone-props-section')
            ?.classList.remove('collapsed');
        Knochenbaum.insBildRuecken(name);
    }
}

fn.initModelGenerator = Modellgenerator.starten;
fn._doBoneClick = Modellgenerator.knochenklick;
fn._mgSelectBone = Knochenauswahl.waehlen;
fn._mgGenerateCharacter = Modellerzeugung.charakterBauen;
fn._mgGeneratePreview = Modellerzeugung.netzBauen;
fn._mgAutoRegenerate = Modellerzeugung.anfordern;
fn._mgSaveModelToServer = Modellspeicher.speichern;
