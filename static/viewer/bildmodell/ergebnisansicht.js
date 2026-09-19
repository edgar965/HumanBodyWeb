/**
 * Ergebnisansicht — Vorschauen, Zahlen und die gefundenen Regler.
 *
 * Zahlen kommen aus `ergebnis` (Schätzung, Zielnetz, Anpassung je Teil,
 * Restmorph) — gemessen im Arbeitsprozess, hier nur gezeigt. Die Regler
 * stehen als Liste mit Wert; ein Haken „festhalten" nimmt den Regler beim
 * nächsten Start ab „anpassung" als Vorgabe (`fest`), das Feld daneben den
 * Wert. `festgehalten()` liefert das Wörterbuch für den Start.
 */
import { Massetabelle } from './massetabelle.js';

export class Ergebnisansicht {

    static TEILE = { kopf: 'Kopf', hals: 'Hals', rumpf: 'Rumpf', becken: 'Becken',
                     l_schulter: 'Schulter l', r_schulter: 'Schulter r', l_oberarm: 'Oberarm l',
                     r_oberarm: 'Oberarm r', l_unterarm: 'Unterarm l', r_unterarm: 'Unterarm r',
                     l_hand: 'Hand l', r_hand: 'Hand r', l_oberschenkel: 'Oberschenkel l',
                     r_oberschenkel: 'Oberschenkel r', l_unterschenkel: 'Unterschenkel l',
                     r_unterschenkel: 'Unterschenkel r', l_fuss: 'Fuß l', r_fuss: 'Fuß r' };

    constructor(auftrag) {
        this.auftrag = auftrag;
        this._stand = '';
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    zeigen(z) {
        const stand = JSON.stringify(z.ergebnis || {}) + (z.modell || '');
        if (stand === this._stand) return;
        this._stand = stand;
        this.vorschauen(z);
        this.zahlen(z);
        this.regler(z);
    }

    vorschauen(z) {
        const feld = document.getElementById('vorschauen');
        if (!feld) return;
        feld.innerHTML = '';
        // Mit Proportionszeilen (Vorher/Nachher je Ansicht) sind die kleinen Vorschauen doppelt.
        if ((z.ergebnis || {}).proportionen) return;
        const v = (z.ergebnis || {}).vorschau || {};
        for (const name of ['vorn', 'seite', 'hinten', 'kopf']) {
            if (!v[name]) continue;
            const bild = document.createElement('img');
            bild.className = 'bildmodell-ansichtbild';
            bild.src = this.auftrag.dateiAdresse('ergebnis', v[name]) + `?t=${Date.now()}`;
            bild.title = name;
            feld.appendChild(bild);
        }
    }

    zahlen(z) {
        const feld = document.getElementById('zahlen');
        if (!feld) return;
        const e = z.ergebnis || {};
        const zeilen = [];
        const s = e.schaetzung;
        if (s) zeilen.push(['Schätzung', `${s.anzahl} Hauptbild(er), ${s.mischung}; Grundfigur ${s.geschlecht}${s.kopf ? '; FLAME-Kopf' : ''}`]);
        const t = e.ziel;
        if (t) zeilen.push(['Zielnetz', `${t.hoehe_ziel_cm ?? t.hoehe_cm} cm, ${t.paarung ? t.paarung.zugeordnet + ' von ' + t.paarung.punkte + ' Punkten zugeordnet' : ''}${t.ohne_betas ? ' — ohne Schätzung (Grundfigur)' : ''}`]);
        const a = e.anpassung;
        if (a) {
            zeilen.push(['Anpassung', `${a.punkte_rms_mm} mm RMS, Gelenke ${a.gelenke_mm ?? '–'} mm, ${Object.keys(a.regler || {}).length} Regler aktiv von ${a.variablen} (${a.reglersatz}, ${a.basis})`]);
            const teile = Object.entries(a.teile || {}).map(([k, v]) => `${Ergebnisansicht.TEILE[k] || k} ${v}`).join(' · ');
            if (teile) zeilen.push(['je Teil (mm)', teile]);
            if (a.verlauf) zeilen.push(['Verlauf', a.verlauf.map(v => `${v.durchgang}: ${v.rms_mm} mm`).join(' → ')]);
        }
        if (a && a.haende && a.haende.haende) {
            const h = a.haende;
            zeilen.push(['Hände', `${h.haende} sichere Hände, Mittelfinger/Handfläche ${h.finger} ± ${h.finger_streuung} → Fingers Length ${Object.values(h.regler || {})[0] ?? '–'}${a.festgehalten && Object.keys(a.festgehalten).length ? ' (festgehalten)' : ' (nur gemessen)'}`]);
        }
        const r = e.rest;
        if (r && !r.aus) zeilen.push(['Restmorph', `${r.regler}: ${r.punkte} Punkte, bis ${r.max_mm} mm; Rest ${r.rest_vorher_mm} → ${r.rms_mit_morph_mm ?? r.rest_nachher_mm} mm`]);
        if (z.modell) zeilen.push(['Modell', `gespeichert als „${z.modell}" — in Szene, Studio und Theatre unter Genesis 9 · gespeichert`]);
        feld.innerHTML = zeilen.map(([k, v]) => `<div class="bildmodell-zahl"><b>${k}</b><span>${v}</span></div>`).join('')
            + Massetabelle.html(e.masse);
    }

    regler(z) {
        const feld = document.getElementById('reglerliste');
        if (!feld) return;
        const a = (z.ergebnis || {}).anpassung;
        feld.innerHTML = '';
        if (!a || !a.regler) return;
        const fest = a.festgehalten || {};
        const kopf = document.createElement('div');
        kopf.className = 'bildmodell-reglerkopf';
        kopf.innerHTML = '<b>Regler</b><span class="hb-hinweis">Haken = beim nächsten Start ab „Anpassung" festhalten</span>';
        feld.appendChild(kopf);
        const eintraege = Object.entries(a.regler).sort((x, y) => Math.abs(y[1]) - Math.abs(x[1]));
        for (const [name, wert] of eintraege) {
            const zeile = document.createElement('label');
            zeile.className = 'bildmodell-reglerzeile';
            const haken = document.createElement('input');
            haken.type = 'checkbox'; haken.dataset.regler = name; haken.checked = name in fest;
            const text = document.createElement('span');
            text.textContent = name.replace('_figure_ctrl_Character', '').replace('_bs_', ' ').replace('_ctrl_', ' ');
            text.title = name;
            const zahl = document.createElement('input');
            zahl.type = 'number'; zahl.step = '0.01'; zahl.value = String(wert); zahl.dataset.regler = name;
            zeile.append(haken, text, zahl);
            feld.appendChild(zeile);
        }
    }

    festgehalten() {
        const aus = {};
        for (const haken of document.querySelectorAll('#reglerliste input[type="checkbox"]:checked')) {
            const zahl = document.querySelector(`#reglerliste input[type="number"][data-regler="${CSS.escape(haken.dataset.regler)}"]`);
            aus[haken.dataset.regler] = zahl ? Number(zahl.value) : 0;
        }
        return aus;
    }
}
