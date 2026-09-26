import { escapeHtml } from '../utils.js';
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { markDirty } from '../undo.js';
import { SmplFigur } from './smplfigur.js';
import { Sanduhr } from '../../gemeinsam/sanduhr.js';

/**
 * Smplformregler — Größe und Fülle eines SMPL-Körpers.
 *
 * WARUM (Edgar, 06.09.2026: „der mann in Fall 2 soll schlank sein, finde den
 * Regler, dass du ihn schlank machst!"): Das Online-Tool hat diesen Regler
 * nicht. Im laufenden Tool gemessen: Mit Bust 70, Waist 55 und Hips 70 bleibt
 * sein 3D-Körper Punkt für Punkt derselbe — 142.500 Punkte, 172 cm, Taille
 * 30,4 cm breit, vor wie nach dem Drapieren. Die Maße wirken dort nur auf den
 * Schnitt.
 *
 * Geformt wird über die SMPL-Blendshapes, serverseitig
 * (`/api/character/smpl-figur/formen/`). Der Regler läuft -100..+100 mit 0 in
 * der Mitte, wie die gemeinsamen Regler. Ein voller Ausschlag sind rund 15 cm
 * Körpergröße bzw. 16-21 cm Taillenumfang — gemessen, nicht geschätzt
 * (`GarmentCode/smplform.py`).
 *
 * Losgelassen wird der Regler, nicht gezogen: Jeder Bau rechnet ein
 * SMPL-X-Netz mit 10.475 Punkten und legt es ab. Bei jedem Pixel neu zu bauen
 * hieße hunderte Läufe für eine Bewegung.
 *
 * ACHT WEITERE REGLER (25.09.2026, „SMPL-X für Vollausstattung"): SMPL-X
 * führt zehn Shape-Betas, nicht nur zwei. Für Beta 2..9 ist — anders als für
 * Größe/Fülle — nicht gemessen, was sie am Körper bewirken; sie laufen roh
 * als „Form 3" … „Form 10" mit (`SMPL/form.py`, `WEITERE_SCHLUESSEL`).
 */
export class Smplformregler {

    static REGLER = [
        { schluessel: 'groesse', name: 'Größe', links: 'klein', rechts: 'groß' },
        { schluessel: 'fuelle', name: 'Fülle', links: 'schlank', rechts: 'kräftig' },
        ...Array.from({ length: 8 }, (_, i) => ({
            schluessel: `form${i + 3}`, name: `Form ${i + 3}`,
            links: 'unbenannt', rechts: 'unbenannt',
        })),
    ];

    static MASSADRESSE = '/api/character/smpl-figur/massregler/';

    /** Maßregler-Liste je Geschlecht, einmal vom Server. */
    static _massVorrat = new Map();

    static fuellen(inst, behaelter) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        for (const angabe of Smplformregler.REGLER) {
            behaelter.appendChild(Smplformregler._zeile(inst, angabe));
        }
        const massbereich = document.createElement('div');
        massbereich.id = 'prop-smpl-massregler';
        behaelter.appendChild(massbereich);
        behaelter.appendChild(Smplformregler._fuss(inst));
        Smplformregler._massFuellen(inst, massbereich);
    }

    /**
     * Benannte Maßregler (25.09.2026, Edgar: „ich kann bei SMPL-X immer noch
     * keine Eigenschaften ändern, z.B. Armlänge, Brustgröße"). Namen und
     * Messpunkte aus SMPL-Anthropometry; je Regler eine kalibrierte Richtung
     * über 300 Betas, die NUR dieses Maß ändert (`SMPL/xmassregler.py`). Der
     * Hinweis am Namen zeigt die gemessene Wirkung bei ±100.
     */
    static async _massFuellen(inst, bereich) {
        const geschlecht = inst.geschlecht === 'male' ? 'male' : 'female';
        let liste = Smplformregler._massVorrat.get(geschlecht);
        if (!liste) {
            try {
                const antwort = await fetch(`${Smplformregler.MASSADRESSE}${geschlecht}/`);
                liste = await antwort.json();
            } catch (fehler) {
                bereich.textContent = `Maßregler nicht ladbar: ${fehler.message}`;
                return;
            }
            Smplformregler._massVorrat.set(geschlecht, liste);
        }
        if (!liste.verfuegbar) {
            bereich.textContent = 'Maßregler fehlen auf dem Server (Smplxmassregler.berechnen).';
            return;
        }
        const titel = document.createElement('div');
        titel.className = 'hb-font-size-0-72rem';
        titel.textContent = 'Körpermaße';
        bereich.appendChild(titel);
        for (const angabe of liste.regler) {
            bereich.appendChild(Smplformregler._zeile(inst, angabe));
        }
    }

    static _hinweis(angabe) {
        const w = angabe.wirkung;
        const grund = `${angabe.links} … ${angabe.rechts}`;
        if (!w) return grund;
        const zahl = (x) => `${x > 0 ? '+' : ''}${String(x).replace('.', ',')}`;
        return `${grund} — gemessen bei ±100: ${zahl(w.minus.ziel_cm)} / ${zahl(w.plus.ziel_cm)} cm`
            + ` (Durchschnitt ${String(w.basis_cm).replace('.', ',')} cm)`;
    }

    static _zeile(inst, angabe) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const wert = Number(inst.form?.[angabe.schluessel]) || 0;
        zeile.innerHTML = `<label title="${escapeHtml(Smplformregler._hinweis(angabe))}">`
            + `${escapeHtml(angabe.name)}</label>`;
        const schieber = document.createElement('input');
        schieber.type = 'range';
        schieber.min = '-100';
        schieber.max = '100';
        schieber.step = '1';
        schieber.value = String(wert);
        schieber.className = 'hb-dehnt-ohne-abstand';
        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        anzeige.textContent = String(wert);
        schieber.addEventListener('input', () => { anzeige.textContent = schieber.value; });
        schieber.addEventListener('change', () => {
            Smplformregler._bauen(inst, angabe.schluessel, Number(schieber.value));
        });
        zeile.appendChild(schieber);
        zeile.appendChild(anzeige);
        return zeile;
    }

    static _fuss(inst) {
        const fuss = document.createElement('div');
        fuss.className = 'hb-font-size-0-72rem';
        fuss.id = 'prop-smpl-formstand';
        const geformt = Object.values(inst.form || {}).some((wert) => Number(wert));
        fuss.textContent = geformt
            ? `Geformt: ${inst.koerper}`
            : 'Durchschnittskörper des Tools (alle Regler in der Mitte).';
        return fuss;
    }

    /** Neuen Körper bauen und die Figur austauschen — Lage bleibt. */
    static async _bauen(inst, schluessel, wert) {
        const stand = document.getElementById('prop-smpl-formstand');
        if (stand) stand.textContent = 'Baue Körper …';
        const form = { ...inst.form, [schluessel]: wert };
        // Haut (Farbe/Rauheit/Glanz) mitnehmen — sonst faellt ein Reglerzug
        // die eigene Hautfarbe wieder auf Grau zurueck (25.09.2026).
        const neu = new SmplFigur(inst.id, {
            koerper: inst.koerper, geschlecht: inst.geschlecht, form, haut: inst.haut,
            details: inst.details,
        });
        try {
            await Sanduhr.um('Körper wird gebaut …', () => neu.bauen());
        } catch (fehler) {
            if (stand) stand.textContent = `Fehler: ${fehler.message}`;
            return;
        }
        neu.group.position.copy(inst.group.position);
        neu.group.rotation.copy(inst.group.rotation);
        neu.group.scale.copy(inst.group.scale);
        state.scene.remove(inst.group);
        inst.dispose();
        state.characters.set(inst.id, neu);
        state.scene.add(neu.group);
        fn.updateCharacterListUI();
        fn.updateVertexCount();
        fn.selectCharacter(inst.id);
        markDirty('SMPL-Form');
    }
}
