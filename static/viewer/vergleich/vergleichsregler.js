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

/** Vorgabe-Hautfarbe, wenn die Herkunft keine kennt. */
const HAUTVORGABE = 0xd4a574;

export class Vergleichsregler {
    static async laden(ansicht) {
        try {
            const daten = await (await fetch(ansicht.apiPrefix + '/morphs/')).json();
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
            const grenzen = daten.meta_sliders?.[name];
            if (grenzen) {
                els.slider.min = grenzen.min;
                els.slider.max = grenzen.max;
                els.slider.value = grenzen.default;
                els.val.textContent = grenzen.default;
            }
            els.slider.addEventListener('input', () => {
                const angezeigt = parseInt(els.slider.value);
                els.val.textContent = angezeigt;
                ansicht.funk.senden({
                    type: 'meta', name,
                    value: Vergleichsregler._innenwert(els.slider, angezeigt),
                });
            });
        }
    }

    /**
     * Reglerstellung in den Bereich [-1, 1] umrechnen.
     * Die Mitte des Reglers ist der neutrale Wert 0.
     */
    static _innenwert(slider, angezeigt) {
        const min = parseInt(slider.min), max = parseInt(slider.max);
        const halb = (max - min) / 2;
        return halb ? (angezeigt - (min + max) / 2) / halb : 0;
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

    static _morphliste(ansicht, daten) {
        const nachKategorie = {};
        for (const m of daten.morphs) {
            (nachKategorie[m.category] ||= []).push(m);
        }
        const liste = ansicht.felder.morphliste;
        liste.innerHTML = '';
        for (const kategorie of daten.categories.sort()) {
            const morphs = nachKategorie[kategorie];
            if (!morphs?.length) continue;
            liste.appendChild(
                Vergleichsregler._kategorie(ansicht, kategorie, morphs));
        }
    }

    static _kategorie(ansicht, name, morphs) {
        const kasten = document.createElement('div');
        kasten.className = 'morph-category';
        const kopf = document.createElement('div');
        kopf.className = 'morph-category-header';
        kopf.textContent = `${name} (${morphs.length})`;
        kopf.addEventListener('click', () => kasten.classList.toggle('open'));
        kasten.appendChild(kopf);

        const rumpf = document.createElement('div');
        rumpf.className = 'morph-category-body';
        for (const m of morphs) {
            rumpf.appendChild(Vergleichsregler._morphzeile(ansicht, m));
        }
        kasten.appendChild(rumpf);
        return kasten;
    }

    static _morphzeile(ansicht, morph) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const beschriftung = document.createElement('label');
        beschriftung.textContent = morph.name.split('_').slice(1).join(' ')
                                   || morph.name;
        beschriftung.title = morph.name;

        const regler = document.createElement('input');
        regler.type = 'range';
        regler.min = -100;
        regler.max = 100;
        regler.value = 0;
        regler.step = 1;
        regler.dataset.morph = morph.name;

        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        anzeige.textContent = '0';

        regler.addEventListener('input', () => {
            anzeige.textContent = regler.value;
            ansicht.funk.morphGebremst(morph.name, parseInt(regler.value) / 100.0);
        });
        zeile.append(beschriftung, regler, anzeige);
        return zeile;
    }

    /** Alle Regler auf ihre Vorgaben zuruecksetzen. */
    static zuruecksetzen(ansicht) {
        const f = ansicht.felder;
        f.morphliste?.querySelectorAll('input[type="range"]').forEach(r => {
            r.value = 0;
            r.nextElementSibling.textContent = '0';
        });
        for (const [name] of GRUNDREGLER) {
            const els = f.grundregler[name];
            const grenzen = ansicht.morphData?.meta_sliders?.[name];
            if (els && grenzen) {
                els.slider.value = grenzen.default;
                els.val.textContent = grenzen.default;
            }
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
        const teile = art.split('_');
        const farben = ansicht.skinColorMap[teile[1] || teile[0]];
        if (farben) {
            material.color.setRGB(Math.pow(farben[0], 1 / 2.2),
                                  Math.pow(farben[1], 1 / 2.2),
                                  Math.pow(farben[2], 1 / 2.2));
        } else {
            material.color.setHex(HAUTVORGABE);
        }
        material.roughness = 0.55;
        material.metalness = 0.0;
        Vergleichsnetz.reglerNachziehen(ansicht, material);
    }
}
