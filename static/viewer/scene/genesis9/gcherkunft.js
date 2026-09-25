import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Stueckmarkierung } from '../stueckmarkierung.js';
import { GarmentcodeVorbilder } from '../garmentcode_vorbilder.js';
import { GarmentcodeMaterial } from '../garmentcode_material.js';

/**
 * Gcherkunft — „Schnitt in GarmentCode anpassen" an einem gebackenen GC-Stück (Weg 2).
 *
 * Ein Genesis-Stück aus GarmentCode (`gc_*`, `G9gcstuecke`/`G9gceigenes`) kennt
 * seine Herkunft: Vorlage, Vorbild oder Form, alle Reglerwerte, Farbe und Stoff
 * (`GET /api/garmentcode/genesis/<stueck>/`). Der Knopf öffnet den GarmentCode-
 * Reiter (geklickt, nicht `switchTab` — am Klick hängt das Reitergedächtnis),
 * wählt Vorlage und Vorbild, stellt die Regler auf die Werte DES STÜCKS (nicht
 * nur die des Vorbilds — ein im Reiter gespeichertes Stück weicht ab) und das
 * Material. Gebaut wird nichts; „Als Genesis-Stück speichern" ersetzt danach
 * das Stück an der Figur (`GarmentcodeAlsgenesis.ziel`).
 */
export class Gcherkunft {

    static WARTEN_MS = 100;
    static VERSUCHE = 30;

    /** Nur Stücke aus GarmentCode haben eine Herkunft. */
    static gilt(kennung) {
        return /^gc_[a-z0-9_]+$/.test(String(kennung || ''));
    }

    /** Der Knopf für die Eigenschaften — oder null. */
    static knopf(inst, kennung) {
        if (!Gcherkunft.gilt(kennung)) return null;
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn-toggle';
        knopf.innerHTML = '<i class="fas fa-cut"></i> Schnitt in GarmentCode anpassen';
        knopf.title = 'Den GarmentCode-Reiter mit dem Schnitt dieses Stücks öffnen — ' +
                      'danach „Als Genesis-Stück speichern" ersetzt es';
        knopf.addEventListener('click', (e) => {
            e.stopPropagation();
            Gcherkunft.oeffnen(inst, kennung);
        });
        return knopf;
    }

    /** Die gespiegelte Kennung aus der Bilanz (`vorbild_…`, `form_…`) als Reiterquelle. */
    static quelle(schluessel) {
        if (!schluessel || schluessel === 'reiter') return null;
        return { art: String(schluessel).startsWith('form_') ? 'form' : 'vorbild', schluessel };
    }

    static async oeffnen(inst, kennung) {
        const herkunft = await Serverabruf.json(`/api/garmentcode/genesis/${encodeURIComponent(kennung)}/`);
        if (!herkunft || herkunft.fehler || !herkunft.vorlage) return false;
        Stueckmarkierung.reiterKlicken('garmentcode');
        fn.garmentcodeAlsGenesisZiel?.({ instId: inst.id, kennung });
        const quelle = Gcherkunft.quelle(herkunft.quelle);
        if (quelle) fn.garmentcodeQuelleZeigen?.(herkunft.vorlage, quelle);
        else fn.garmentcodeVorlageZeigen?.(herkunft.vorlage);
        // Vorlage und Vorbild laden nach — erst wenn die Vorlage steht und
        // (mit Vorbild) dessen Knopf aktiv ist, die Werte des Stücks darüber.
        const bereit = () => document.getElementById('gc-vorlage')?.value === herkunft.vorlage
            && (quelle?.art !== 'vorbild' || document.querySelector(
                `#gc-vorbilder .vorbild-knopf.active[data-schluessel="${CSS.escape(quelle.schluessel)}"]`));
        for (let i = 0; i < Gcherkunft.VERSUCHE && !bereit(); i += 1) {
            await new Promise((weiter) => setTimeout(weiter, Gcherkunft.WARTEN_MS));
        }
        GarmentcodeVorbilder._reglerStellen(herkunft.werte || {});
        Gcherkunft.material(herkunft);
        return true;
    }

    /** Die Bilanzfarbe (`[r, g, b]` 0–1, wie Daz' `Diffuse Color`) als `#rrggbb` — oder ''. */
    static hex(farbe) {
        if (typeof farbe === 'string') return /^#[0-9a-f]{6}$/i.test(farbe) ? farbe : '';
        if (!Array.isArray(farbe) || farbe.length < 3) return '';
        return '#' + farbe.slice(0, 3).map((w) => Math.round(Math.min(1, Math.max(0, Number(w) || 0)) * 255)
            .toString(16).padStart(2, '0')).join('');
    }

    /** Farbe, Rauheit und Metall in den Stand und die Felder des Reiters (ohne Ereignis). */
    static material(herkunft) {
        const stand = GarmentcodeMaterial.stand;
        const stoff = herkunft.stoff || {};
        const hex = Gcherkunft.hex(herkunft.farbe);
        if (hex) stand.farbe = hex;
        if (typeof stoff.rauheit === 'number') stand.rauheit = stoff.rauheit;
        if (typeof stoff.metall === 'number') stand.metall = stoff.metall;
        if (stoff.gewebe) stand.gewebe = { ...stand.gewebe, ...stoff.gewebe };
        const feld = (id, wert) => { const f = document.getElementById(id); if (f) f.value = String(wert); };
        feld('gc-color', stand.farbe);
        feld('gc-roughness', Math.round(stand.rauheit * 100));
        feld('gc-metalness', Math.round(stand.metall * 100));
    }
}
