import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Dazkleidung } from './dazkleidung.js';

/**
 * Genesis9morphformular — das freie Morph-Formular unter den Reglern eines Daz-Stücks (01.10.2026; bis dahin „nicht
 * gebaut: die festen Regler decken die Operationen").
 *
 * Ein Ortsmorph mit eigenem Namen: Ort (Höhenband, Sektor um die senkrechte Achse, Landmarke mit Radius, Welle),
 * Richtung (Hautnormale, radial, oben …), Weg in cm, Seite, Auslauf — dieselben Felder wie `morph_ort` im Rezept.
 * `POST garderobe/<kennung>/morph/` baut ihn (`G9kleidmorphe.bauen`), die Antwort nennt den Regler; er wird sofort als
 * Zeile in die Gruppe „Eigene Morphe" gehängt und auf 1 gestellt (der Bau läuft über `Dazkleidung.anziehenAuf`, wenn
 * das Stück getragen ist — sonst bleibt der Wert gemerkt bis zum Anziehen).
 *
 * Immer zu beim Laden (kein Gedächtnis — `engine2d3dkleider.md`).
 */
export class Genesis9morphformular {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/';
    static LANDMARKEN = '/api/character/genesis9-figur/landmarken/';
    static RICHTUNGEN = [['haut', 'Hautnormale'], ['aussen', 'nach außen'], ['innen', 'nach innen'], ['oben', 'nach oben'],
                         ['unten', 'nach unten'], ['vorn', 'nach vorn'], ['hinten', 'nach hinten']];
    static _landmarken = null;
    /** Das LAUFENDE Versprechen der Namensliste — alle Formulare warten auf dasselbe (sonst holt jedes seine eigene). */
    static _landmarkenLauf = null;

    static bauen(inst, stueck, werteLesen, zeileBauen) {
        const kasten = document.createElement('details');
        kasten.className = 'g9-kategorie genesis9-morphformular';
        kasten.open = false;
        kasten.innerHTML = `<summary class="aufklappkopf">Neuer Morph … <span class="gedaempft">(Ort, Richtung, Weg)</span></summary>`;
        const formular = document.createElement('div');
        formular.className = 'genesis9-morphfelder';
        formular.innerHTML = Genesis9morphformular._html(stueck);
        kasten.appendChild(formular);
        Genesis9morphformular._landmarkenFuellen(formular);
        formular.querySelector('[data-tat="bauen"]').addEventListener('click', async () => {
            await Genesis9morphformular._bauen(inst, stueck, formular, kasten, werteLesen, zeileBauen);
        });
        return kasten;
    }

    static _html(stueck) {
        const richtungen = Genesis9morphformular.RICHTUNGEN
            .map(([w, t]) => `<option value="${w}">${escapeHtml(t)}</option>`).join('');
        return `
            <div class="slider-row"><label>Name</label>
                <input type="text" class="hb-dehnt" data-feld="name" placeholder="z. B. bauch_beule" maxlength="40"></div>
            <div class="slider-row"><label>Band (0 unten … 1 oben)</label>
                <input type="number" data-feld="band_von" value="0" min="0" max="1" step="0.05" class="genesis9-morphzahl">
                <input type="number" data-feld="band_bis" value="1" min="0" max="1" step="0.05" class="genesis9-morphzahl"></div>
            <div class="slider-row"><label>Sektor (° um die Achse, 0 vorn, + links)</label>
                <input type="number" data-feld="sektor_a" value="-180" min="-180" max="180" step="5" class="genesis9-morphzahl">
                <input type="number" data-feld="sektor_b" value="180" min="-180" max="180" step="5" class="genesis9-morphzahl"></div>
            <div class="slider-row"><label>Landmarke</label>
                <select data-feld="landmarke" class="hb-dehnt"><option value="">— keine —</option></select>
                <input type="number" data-feld="radius_cm" value="8" min="0.5" max="60" step="0.5" class="genesis9-morphzahl" title="Radius cm"></div>
            <div class="slider-row"><label>Welle (cm, 0 = keine)</label>
                <input type="number" data-feld="welle_cm" value="0" min="0" max="60" step="1" class="genesis9-morphzahl">
                <select data-feld="welle_richtung" class="hb-dehnt"><option value="laengs">längs</option><option value="quer">quer</option></select></div>
            <div class="slider-row"><label>Richtung</label>
                <select data-feld="richtung" class="hb-dehnt">${richtungen}</select></div>
            <div class="slider-row"><label>Weg (cm)</label>
                <input type="number" data-feld="weg_cm" value="2" min="-20" max="20" step="0.5" class="genesis9-morphzahl">
                <select data-feld="seite" class="hb-dehnt"><option value="">beide Seiten</option><option value="links">links</option><option value="rechts">rechts</option></select></div>
            <div class="slider-row"><label>Auslauf (Anteil der Höhe)</label>
                <input type="number" data-feld="weich" value="0.15" min="0.01" max="0.5" step="0.01" class="genesis9-morphzahl"></div>
            <div class="slider-row"><button type="button" class="btn" data-tat="bauen"><span>Morph bauen und stellen</span></button>
                <span class="gedaempft genesis9-morphmeldung"></span></div>`;
    }

    static async _landmarkenFuellen(formular) {
        try {
            // Erst nach der Antwort gemerkt, hieß: Alle Formulare, die VOR ihr entstanden, holten sie noch einmal
            // (568 Abrufe je Aufbau der Garderobe, gemessen 09.10.2026). Ein Fehlschlag brennt sich nicht ein.
            if (!Genesis9morphformular._landmarken) {
                Genesis9morphformular._landmarkenLauf ??= Serverabruf.json(Genesis9morphformular.LANDMARKEN)
                    .then(antwort => Object.keys(antwort.landmarken || {}).sort())
                    .catch(fehler => { Genesis9morphformular._landmarkenLauf = null; throw fehler; });
                Genesis9morphformular._landmarken = await Genesis9morphformular._landmarkenLauf;
            }
        } catch { return; }
        const feld = formular.querySelector('[data-feld="landmarke"]');
        for (const name of Genesis9morphformular._landmarken) {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            feld.appendChild(option);
        }
    }

    /** Die Felder → der Rumpf für `POST …/morph/` (auch vom Körperformular genutzt). */
    static rumpf(formular) {
        const f = feld => formular.querySelector(`[data-feld="${feld}"]`)?.value;
        const zahl = feld => parseFloat(f(feld));
        const ort = {};
        const [von, bis] = [zahl('band_von'), zahl('band_bis')];
        if (!(von === 0 && bis === 1)) ort.band = [von, bis];
        const [a, b] = [zahl('sektor_a'), zahl('sektor_b')];
        if (!(a === -180 && b === 180)) ort.sektor = [a, b];
        if (f('landmarke')) { ort.landmarke = f('landmarke'); ort.radius_cm = zahl('radius_cm'); }
        if (zahl('welle_cm') > 0) ort.welle = { laenge_cm: zahl('welle_cm'), richtung: f('welle_richtung') };
        return { name: (f('name') || '').trim(), ort, richtung: f('richtung') || 'haut', weg_cm: zahl('weg_cm'),
                 seite: f('seite') || null, weich: zahl('weich') };
    }

    static async _bauen(inst, stueck, formular, kasten, werteLesen, zeileBauen) {
        const meldung = formular.querySelector('.genesis9-morphmeldung');
        const knopf = formular.querySelector('[data-tat="bauen"]');
        const rumpf = Genesis9morphformular.rumpf(formular);
        if (!/^[a-z][a-z0-9_]{0,40}$/.test(rumpf.name)) { meldung.textContent = 'Name: a-z, 0-9, _ (mit Buchstabe beginnen)'; return; }
        if (!Object.keys(rumpf.ort).length && rumpf.richtung === 'haut') { meldung.textContent = 'Einen Ort wählen (Band, Sektor, Landmarke)'; return; }
        knopf.disabled = true;
        meldung.textContent = 'Baut …';
        try {
            const antwort = await Serverabruf.senden(`${Genesis9morphformular.ADRESSE}${encodeURIComponent(stueck.id)}/morph/`, rumpf);
            if (antwort.fehler) throw new Error(antwort.fehler);
            const regler = antwort.regler;
            meldung.textContent = `${antwort.brief?.bewegt ?? '?'} Punkte, bis ${antwort.brief?.weg_max_mm ?? '?'} mm`;
            // In die Reglerliste des Stücks: Gruppe „Eigene Morphe" (oder neu), Zeile davor einhängen, Wert 1.
            if (!stueck.regler.some(r => r.name === regler.name)) stueck.regler.push(regler);
            const zeile = zeileBauen(regler);
            Genesis9morphformular._einhaengen(kasten, regler, zeile);
            const getragen = Dazkleidung.kleidung(inst)[stueck.id];
            const werte = werteLesen();
            werte.regler = { ...((getragen || {}).regler || {}), [regler.name]: 1 };
            const schieber = zeile.querySelector('input[type="range"]');
            if (schieber) { schieber.value = '1'; zeile.querySelector('.slider-value').textContent = '100 %'; }
            if (getragen) {
                getragen.regler = werte.regler;
                Genesis9lauf.planen(inst, () => Dazkleidung.anziehenAuf(inst, stueck.id, werte), () => {}, `stueck:${stueck.id}`);
            }
            markDirty();
        } catch (fehler) {
            meldung.textContent = `Fehler: ${fehler.daten?.fehler || fehler.message}`;
        } finally {
            knopf.disabled = false;
        }
    }

    /** Die neue Zeile in die Gruppe „Eigene Morphe" des Stückkastens — vor dem Formular, damit man sie gleich sieht. */
    static _einhaengen(kasten, regler, zeile) {
        const stueckkasten = kasten.parentElement;
        let gruppe = [...stueckkasten.querySelectorAll('details.genesis9-reglergruppe')]
            .find(g => g.querySelector('summary')?.textContent.trim().startsWith(regler.gruppe));
        if (!gruppe) {
            gruppe = document.createElement('details');
            gruppe.className = 'g9-kategorie genesis9-reglergruppe';
            gruppe.innerHTML = `<summary class="aufklappkopf">${escapeHtml(regler.gruppe)} <span class="gedaempft">(0)</span></summary>`;
            stueckkasten.insertBefore(gruppe, kasten);
        }
        gruppe.appendChild(zeile);
        gruppe.open = true;
        const zaehler = gruppe.querySelector('summary .gedaempft');
        if (zaehler) zaehler.textContent = `(${gruppe.querySelectorAll('.slider-row').length})`;
    }
}
