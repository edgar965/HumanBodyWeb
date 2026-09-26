import { markDirty } from '../undo.js';

/**
 * Smplhautregler — Farbe, Rauheit und Glanz eines SMPL-X-Körpers.
 *
 * WARUM (Edgar, 25.09.2026: „warum hat SMPLX kein Skin … SMPL-X für
 * Vollausstattung"): Der Körper trug bis dahin fest Grau (`SmplModell.FARBE`)
 * — passend für den Referenzkörper von GarmentCode, aber unbrauchbar für eine
 * Figur, die wie ein Mensch aussehen soll. Die Werte liegen in `inst.haut`
 * (`{farbe, rauheit, glanz, textur}`, `farbe` 0 = „nicht gesetzt", dann bleibt es
 * grau) und werden mit der Figur gespeichert (`SmplFigur.toJSON`); gerechnet
 * wird direkt am Material (`SmplModell.hautAnwenden`), ohne Serveranfrage
 * und ohne Neubau des Netzes.
 */
export class Smplhautregler {

    static fuellen(inst, behaelter) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        const farbe = Smplhautregler._farbe(inst);
        if (inst._fototextur) behaelter.appendChild(Smplhautregler._textur(inst, farbe));
        behaelter.appendChild(farbe);
        behaelter.appendChild(Smplhautregler._regler(inst, 'rauheit', 'Rauheit', 0, 1, 0.01));
        behaelter.appendChild(Smplhautregler._regler(inst, 'glanz', 'Glanz', 0, 1, 0.01));
    }

    //: BEDLAM-Texturlisten je Geschlecht, einmal geholt (`Promise`, wie ein Vorrat).
    static _bedlamListen = new Map();

    static _bedlamListe(geschlecht) {
        const g = geschlecht === 'male' ? 'male' : 'female';
        if (!Smplhautregler._bedlamListen.has(g)) {
            Smplhautregler._bedlamListen.set(g, fetch(`/api/character/smpl-figur/bedlam/${g}/`)
                .then((r) => r.json()).then((d) => d.texturen || []).catch(() => []));
        }
        return Smplhautregler._bedlamListen.get(g);
    }

    /**
     * Textur: das eigene Meshcapade-Hautfoto, keine, oder eine der 100
     * BEDLAM-Hauttexturen (26.09.2026, „du hast doch eine Textur
     * heruntergeladen, wende sie an" / „baue das ein" —
     * `core/dienste/smplxbedlamdienst.py`, leer ohne heruntergeladenen
     * Ordner). Mit Foto ist die Hautfarbe aus — sie würde das Foto nur
     * umtönen (`SmplModell.hautAnwenden`).
     */
    static _textur(inst, farbzeile) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = '<label>Textur</label>';
        const wahl = document.createElement('select');
        wahl.className = 'viewer-select';
        wahl.innerHTML = '<option value="foto">Hautfoto (Meshcapade)</option>'
            + '<option value="keine">Keine (nur Hautfarbe)</option>';
        if (['foto', 'keine'].includes(inst.haut.textur)) wahl.value = inst.haut.textur;
        const sperren = () => {
            for (const e of farbzeile.querySelectorAll('input, button')) e.disabled = inst.haut.textur !== 'keine';
            farbzeile.title = inst.haut.textur === 'keine' ? '' : 'Das Hautfoto bestimmt die Farbe';
        };
        wahl.addEventListener('change', () => {
            inst.haut.textur = wahl.value;
            inst.hautAnwenden();
            sperren();
            markDirty();
        });
        Smplhautregler._bedlamListe(inst.geschlecht).then((liste) => {
            if (!liste.length || !wahl.isConnected) return;
            const gruppe = document.createElement('optgroup');
            gruppe.label = 'BEDLAM (Meshcapade, weitere Hauttöne)';
            for (const eintrag of liste) {
                const option = document.createElement('option');
                option.value = `bedlam:${eintrag.schluessel}`;
                option.textContent = eintrag.name;
                gruppe.appendChild(option);
            }
            wahl.appendChild(gruppe);
            if (inst.haut.textur.startsWith('bedlam:')) wahl.value = inst.haut.textur;
        });
        zeile.appendChild(wahl);
        sperren();
        return zeile;
    }

    static _hexVonFarbe(farbe) {
        return farbe ? `#${farbe.toString(16).padStart(6, '0')}` : '#9a9a9a';
    }

    static _farbe(inst) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = '<label>Hautfarbe</label>';
        const feld = document.createElement('input');
        feld.type = 'color';
        feld.value = Smplhautregler._hexVonFarbe(inst.haut.farbe);
        feld.addEventListener('input', () => {
            inst.haut.farbe = parseInt(feld.value.slice(1), 16);
            inst.hautAnwenden();
            markDirty();
        });
        const weg = document.createElement('button');
        weg.type = 'button';
        weg.textContent = '×';
        weg.title = 'Eigene Farbe entfernen — wieder das Grau des Referenzkörpers';
        weg.addEventListener('click', () => {
            inst.haut.farbe = 0;
            feld.value = Smplhautregler._hexVonFarbe(0);
            inst.hautAnwenden();
            markDirty();
        });
        zeile.append(feld, weg);
        return zeile;
    }

    static _regler(inst, schluessel, titel, min, max, schritt) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const name = document.createElement('label');
        name.textContent = titel;
        const regler = document.createElement('input');
        regler.type = 'range';
        regler.min = String(min);
        regler.max = String(max);
        regler.step = String(schritt);
        regler.value = String(inst.haut[schluessel]);
        regler.className = 'hb-dehnt-ohne-abstand';
        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        anzeige.textContent = Number(inst.haut[schluessel]).toFixed(2);
        regler.addEventListener('input', () => {
            const wert = Number(regler.value);
            anzeige.textContent = wert.toFixed(2);
            inst.haut[schluessel] = wert;
            inst.hautAnwenden();
        });
        regler.addEventListener('change', () => markDirty());
        zeile.append(name, regler, anzeige);
        return zeile;
    }
}
