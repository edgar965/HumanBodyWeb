import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { wsSend } from './websocket.js';
import { removeAllCloth, loadCloth } from './cloth.js';
import { loadHair, haarfarbeSetzen } from './hair.js';
import { loadGarment, removeAllGarments } from './garment.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Metawerte } from './metawerte.js';
import { Modellzustand } from './modellzustand.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Modellvorgabe — eine gespeicherte Vorgabe auf die Modellseite legen.
 *
 * Herausgelöst aus `presets.js` (352 Zeilen). Die Reihenfolge und die
 * Verzögerungen sind nicht Zierde:
 *
 * * **Nicht genannte Morphs werden auf 0 gestellt.** Sonst bleibt stehen, was
 *   der Nutzer vorher verstellt hatte, und die Vorgabe sieht jedes Mal anders aus.
 * * **Stoffe laden versetzt** (`STOFFPAUSE_MS` je Stück): Jede Simulation belegt
 *   den Server für ein bis zwei Sekunden; gleichzeitig gestartet verdrängen sie
 *   sich gegenseitig.
 * * **Die Haarfarbe kommt später** — sie wirkt erst, wenn das Haarnetz da ist.
 * * **Männliche Figuren bekommen keine Stoffsimulation.** Die Vorlagen sind auf
 *   die weibliche Silhouette geschnitten und liegen am Männerkörper daneben.
 */
export class Modellvorgabe {

    /** Region -> Stoffvorlage, wenn die Vorgabe keine Vorlage nennt. */
    static VORLAGEN = { TOP: 'TPL_TSHIRT', PANTS: 'TPL_PANTS',
                        SKIRT: 'TPL_SKIRT', DRESS: 'TPL_DRESS' };
    static ERSATZVORLAGE = 'TPL_TSHIRT';
    static ERSTE_STOFFPAUSE_MS = 500;
    static STOFFPAUSE_MS = 300;
    static MERKPAUSE_MS = 2000;

    /**
     * Kleiderregler: Kennung, Feld, Faktor, Vorgabewert, Null-zählt-mit.
     *
     * Die letzte Spalte hält die alte Eigenheit fest: Bei den vier
     * Millimeter-Reglern zählte eine gespeicherte 0 als Wert, bei den übrigen
     * schlug sie auf den Vorgabewert durch (`g.offset || 0.006`). Ein Stück mit
     * Abstand 0 bekommt also weiterhin 6 mm — geändert wird das hier nicht,
     * sonst sehen gespeicherte Modelle nach dem Umbau anders aus.
     */
    static KLEIDERREGLER = [
        ['garment-offset', 'offset', 1000, 0.006, false],
        ['garment-stiffness', 'stiffness', 100, 0.8, false],
        ['garment-min-dist', 'minDist', 1, 3, true],
        ['garment-crotch-floor', 'crotchFloor', 1, 0, true],
        ['garment-lift', 'lift', 1, 0, true],
        ['garment-crotch-depth', 'crotchDepth', 1, 0, true],
        ['garment-roughness', 'roughness', 100, 0.8, false],
        ['garment-metalness', 'metalness', 100, 0, false],
        ['garment-pos-x', 'posX', 100, 0, false],
        ['garment-pos-y', 'posY', 100, 0, false],
        ['garment-pos-z', 'posZ', 100, 0, false],
        ['garment-scale-x', 'scaleX', 100, 1, false],
        ['garment-scale-y', 'scaleY', 100, 1, false],
        ['garment-scale-z', 'scaleZ', 100, 1, false],
    ];

    static anwenden(vorgabe) {
        Modellvorgabe._koerpertyp(vorgabe.body_type);
        Modellvorgabe._meta(vorgabe.meta);
        Modellvorgabe._morphs(vorgabe.morphs);
        Modellvorgabe._garderobe(vorgabe.wardrobe);
        Modellvorgabe._stoffe(vorgabe);
        Modellvorgabe._haare(vorgabe.hair_style);
        Modellvorgabe._kleider(vorgabe.garments);
        state.currentPresetName = vorgabe.name || '';
        setTimeout(() => Modellzustand.merken(), Modellvorgabe.MERKPAUSE_MS);
        Protokoll.debug('Viewer',
                        `Preset "${vorgabe.name || 'unknown'}" applied`);
    }

    static _koerpertyp(typ) {
        const wahl = document.getElementById('body-type-select');
        if (!wahl || !typ) return;
        wahl.value = typ;
        wahl.dispatchEvent(new Event('change'));
    }

    static _meta(werte) {
        if (!werte) return;
        for (const [name, wert] of Metawerte.setzen(werte)) {
            wsSend({ type: 'meta', name, value: wert });
        }
    }

    static _morphs(werte) {
        if (!werte) return;
        const stapel = {};
        document.getElementById('morphs-panel')
            ?.querySelectorAll('input[type="range"][data-morph]')
            .forEach(regler => {
                const wert = werte[regler.dataset.morph];
                const anzeige = wert !== undefined ? Math.round(wert * 100) : 0;
                regler.value = anzeige;
                regler.nextElementSibling.textContent = anzeige;
                if (wert !== undefined) stapel[regler.dataset.morph] = wert;
            });
        if (Object.keys(stapel).length > 0) {
            wsSend({ type: 'morph_batch', morphs: stapel });
        }
    }

    /** Zubehör an- und abwählen — der Knopf schaltet beim Klick um. */
    static _garderobe(teile) {
        const feld = document.getElementById('wardrobe-panel');
        if (!feld || !teile || teile.length === 0) return;
        feld.querySelectorAll('.asset-btn.active').forEach(knopf => {
            if (!teile.includes(knopf.dataset.asset)) knopf.click();
        });
        for (const name of teile) {
            const knopf = feld.querySelector(`.asset-btn[data-asset="${name}"]`);
            if (knopf && !knopf.classList.contains('active')
                    && !knopf.classList.contains('disabled')) {
                knopf.click();
            }
        }
    }

    // ------------------------------------------------------------------ Stoffe

    static vorlage(angabe) {
        if (!angabe) return Modellvorgabe.ERSATZVORLAGE;
        return angabe.template
            || (angabe.region ? Modellvorgabe.VORLAGEN[angabe.region]
                              : Modellvorgabe.ERSATZVORLAGE);
    }

    static _stoffe(vorgabe) {
        if (!vorgabe.cloth || vorgabe.body_type?.startsWith('Male_')) return;
        removeAllCloth();
        const liste = (Array.isArray(vorgabe.cloth) ? vorgabe.cloth
                                                    : [vorgabe.cloth]).filter(Boolean);
        liste.forEach((angabe, i) => setTimeout(
            () => Modellvorgabe._stoff(angabe),
            Modellvorgabe.ERSTE_STOFFPAUSE_MS + i * Modellvorgabe.STOFFPAUSE_MS));
        Modellvorgabe._stoffregler(liste[liste.length - 1]);
    }

    static _stoff(angabe) {
        const vorlage = Modellvorgabe.vorlage(angabe);
        loadCloth(`tpl_${vorlage}`, {
            method: 'template', template: vorlage,
            tightness: angabe.tightness !== undefined ? angabe.tightness : 0.5,
            segments: angabe.segments || 32,
            top_extend: angabe.top_extend || 0,
            bottom_extend: angabe.bottom_extend || 0,
        }, angabe.color || null);
    }

    /** Die Regler auf das ZULETZT geladene Stück stellen — es ist ausgewählt. */
    static _stoffregler(letzter) {
        const wahl = document.getElementById('cloth-tpl-type');
        if (wahl) {
            wahl.value = Modellvorgabe.vorlage(letzter);
            wahl.dispatchEvent(new Event('change'));
        }
        const enge = (letzter && letzter.tightness !== undefined)
            ? letzter.tightness : 0.5;
        const regler = document.getElementById('cloth-tpl-tightness');
        if (regler) regler.value = Math.round(enge * 100);
        const anzeige = document.getElementById('cloth-tpl-tightness-val');
        if (anzeige) anzeige.textContent = enge.toFixed(2);
        const farbe = document.getElementById('cloth-color');
        if (farbe && letzter?.color) farbe.value = letzter.color;
    }

    // ------------------------------------------------------------- Haare/Kleider

    static _haare(angabe) {
        if (!angabe) return;
        const stil = document.getElementById('hair-style-select');
        if (stil && angabe.url) {
            for (const eintrag of stil.options) {
                if (eintrag.value === angabe.url) {
                    stil.value = eintrag.value;
                    break;
                }
            }
            loadHair(angabe.url);
        }
        const farbe = document.getElementById('hair-color-select');
        if (!farbe || !angabe.color) return;
        farbe.value = angabe.color;
        // Die Farbe wirkt erst, wenn das Haarnetz geladen ist.
        setTimeout(() => haarfarbeSetzen(angabe.color), Zeiten.SEKUNDE_MS);
    }

    static _kleider(liste) {
        if (!liste || liste.length === 0) return;
        removeAllGarments();
        setTimeout(async () => {
            for (const angabe of liste) {
                Modellvorgabe._kleiderregler(angabe);
                state.selectedGarmentId = angabe.id;
                await loadGarment(angabe.id);
            }
            fn.updateEquippedList?.();
        }, Zeiten.NACHLADEN_MS);
    }

    /** Die Regler VOR dem Laden stellen — der Server liest sie mit. */
    static _kleiderregler(angabe) {
        for (const [kennung, feld, faktor, vorgabe, nullZaehlt]
                of Modellvorgabe.KLEIDERREGLER) {
            const regler = document.getElementById(kennung);
            if (!regler) continue;
            const wert = nullZaehlt
                ? (angabe[feld] !== undefined ? angabe[feld] : vorgabe)
                : (angabe[feld] || vorgabe);
            regler.value = faktor === 1 ? wert : Math.round(wert * faktor);
        }
        const farbe = document.getElementById('garment-color');
        if (farbe) farbe.value = angabe.color || '#4d5980';
    }
}
