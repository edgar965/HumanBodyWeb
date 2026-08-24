import { state, DEFAULT_BODY } from './state.js';
import { applySceneSkinSettings } from './scene_settings.js';
import { loadBVHAnimation } from './animation.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Modellvorgabe } from './modellvorgabe.js';

/**
 * Startvorgabe — was beim Öffnen der Modellseite von selbst geladen wird.
 *
 * Herausgelöst aus `presets.js` (352 Zeilen). Drei Eigenheiten:
 *
 * 1. **Es wird auf das Körpernetz gewartet** (bis zu 15 s). Eine Vorgabe, die
 *    Regler stellt, bevor die Figur existiert, verpufft ohne Fehlermeldung.
 * 2. **Ein fest eingestellter Körpertyp gewinnt** (`DEFAULT_BODY`): Dann wird die
 *    Auswahl gesetzt und SONST NICHTS geladen — die Testseiten wollen genau
 *    diesen Körper sehen, nicht eine komplette Vorgabe darüber.
 * 3. **Die SMPL-Seite hat ihre eigene Einstellung** (`humanbody_preset`), die
 *    Modellseite die ihre (`config`) — dieselbe Frage, zwei Endpunkte.
 */
export class Startvorgabe {

    static WARTEN_MS = 15000;
    static ERSATZVORGABE = 'femaleWithClothes';
    static ANIMATIONSPAUSE_MS = 1500;

    /** Auf das Körpernetz warten; `false`, wenn es nicht kommt. */
    static async warten() {
        const start = Date.now();
        while (!state.bodyMesh && Date.now() - start < Startvorgabe.WARTEN_MS) {
            await new Promise(weiter => setTimeout(weiter, Zeiten.WARTESCHRITT_MS));
        }
        return !!state.bodyMesh;
    }

    async laden() {
        if (!await Startvorgabe.warten()) {
            Protokoll.warnung('presets', 'Default preset: mesh not ready, skipping');
            return;
        }
        await new Promise(weiter => setTimeout(weiter, Zeiten.BILDPAUSE_MS));
        if (DEFAULT_BODY) {
            Startvorgabe._koerpertyp(DEFAULT_BODY);
            return;
        }
        const einstellung = await Startvorgabe._einstellung();
        if (einstellung.rigZeigen) Startvorgabe._rigZeigen();
        await this._vorgabeLaden(einstellung.name);
        if (einstellung.animation) {
            setTimeout(() => Startvorgabe._animation(einstellung.animation),
                       Startvorgabe.ANIMATIONSPAUSE_MS);
        }
    }

    static _koerpertyp(typ) {
        const wahl = document.getElementById('body-type-select');
        if (!wahl) return;
        wahl.value = typ;
        wahl.dispatchEvent(new Event('change'));
        Protokoll.debug('Viewer', `Default body type applied: ${typ}`);
    }

    /** Welche Vorgabe die Seite laden soll — je nach Seite ein anderer Weg. */
    static async _einstellung() {
        const stand = { name: Startvorgabe.ERSATZVORGABE, rigZeigen: false,
                        animation: '' };
        const smplSeite = !!document.getElementById('smpl-body-panel');
        const adresse = smplSeite ? '/api/settings/smpl/'
                                  : '/api/settings/humanbody/';
        let daten;
        try {
            daten = await Serverabruf.json(adresse);
        } catch (fehler) {
            Protokoll.debug('vorgaben', `${adresse} nicht abrufbar`, fehler);
            return stand;
        }
        if (smplSeite) {
            if (daten.humanbody_preset) stand.name = daten.humanbody_preset;
            return stand;
        }
        if (daten.config) stand.name = daten.config;
        stand.rigZeigen = !!daten.show_rig_config;
        stand.animation = daten.default_anim_config || '';
        return stand;
    }

    static _rigZeigen() {
        state.rigVisible = true;
        document.getElementById('rig-toggle')?.classList.add('active');
    }

    async _vorgabeLaden(name) {
        let vorgabe;
        try {
            vorgabe = await Serverabruf.json(
                `/api/character/model/${encodeURIComponent(name)}/`);
        } catch (fehler) {
            Protokoll.warnung('vorgaben', `Vorgabe "${name}" nicht abrufbar`,
                              fehler);
            return;
        }
        Modellvorgabe.anwenden(vorgabe);
        // Die Hauteinstellungen kommen aus der Szene und würden sonst von den
        // Materialien der Vorgabe überschrieben.
        setTimeout(() => applySceneSkinSettings(), Zeiten.NACHZIEHEN_MS);
        Protokoll.debug('Viewer', `Default preset loaded: ${name}`);
    }

    static _animation(adresse) {
        loadBVHAnimation(adresse, 'Default', 0);
        const knopf = document.getElementById('play-demo-anim');
        if (!knopf) return;
        knopf.innerHTML = '<i class="fas fa-pause"></i>';
        knopf.classList.add('active');
    }
}
