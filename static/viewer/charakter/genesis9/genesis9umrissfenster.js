import { escapeHtml } from '../utils.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9groessehalten } from './genesis9groessehalten.js';
import { Genesis9lauf } from './genesis9lauf.js';

/**
 * Genesis9umrissfenster — das Fenster „… formen" eines Eigenreglers (Abschnitt „Eigen" unter Genesis 9; 25.10.2026, Edgar: „ein UI dazu, wie ich den bedienen kann").
 * Für jede Art dasselbe Fenster (`Genesis9/eigenregler.py`): Profil von der Seite, Kopf vorne, Mund, Nase, Augen, Brauen von vorn, Ohren von der Seite; seit dem Abend
 * auch die Körperteile (`Genesis9/streifenmorph.py`: Hals, Rumpf, Arme, Hände, Beine, Füße — zwei Kanten entlang des Teils, Glieder senkrecht gestellt).
 *
 * Grau gestrichelt der Umriss der Figur OHNE diesen Regler, orange der geformte. Anfasser ziehen (Maus) oder wählen und mit den Pfeiltasten schieben (0,5 mm, Umschalt 2 mm).
 * Bei Merkmalen über die Mitte (Mund, Nase, Kopf vorne) koppelt „Seiten gleich" den Anfasser der anderen Seite gespiegelt; Anfasser auf der Mitte bleiben dann waagrecht stehen.
 * Die Vorschau rechnet dieselbe Überblendung wie der Server (Gewichte je Umrisspunkt). „Übernehmen" schreibt den Versatz als Anfasserwerte in die Regler DIESER Figur
 * (`eigenform:<kennung>:<Anfasser>:a|b`, `Genesis9/eigenform.py`; 25.10.2026 abends, Edgar: „Körperregler … nur für die aktuelle Figur“) und baut sie neu — nichts wird auf dem
 * Server abgelegt, gespeichert wird mit der Figur. Alles auf null nimmt die Werte heraus. Der Hauptregler (Grundform für alle Figuren) bleibt, wie er steht.
 */
export class Genesis9umrissfenster {

    static adresse(kennung, tat) { return `/api/character/genesis9-figur/eigenregler/${encodeURIComponent(kennung)}/${tat}/`; }
    static PFEIL_MM = 0.5;
    static _offen = null;

    /** @param o.inst Figur, o.regler Reglerzeile (mit `eigenregler.kennung`), o.zeile die `.slider-row` (Schieber und Hinweis werden nachgezogen) */
    static async oeffnen({ inst, regler, zeile }) {
        Genesis9umrissfenster.schliessen();
        const huelle = document.createElement('div');
        huelle.className = 'scene-modal-overlay visible g9-profil-huelle';
        huelle.innerHTML = `
            <div class="scene-modal g9-profil-dialog" role="dialog" aria-label="${escapeHtml(regler.anzeige)} formen">
                <div class="scene-modal-header"><h4>${escapeHtml(regler.anzeige)} formen</h4>
                    <button type="button" class="scene-modal-close" title="Schließen">×</button></div>
                <div class="scene-modal-body">
                    <div class="g9-profil-hinweis gedaempft">Lädt …</div>
                    <svg class="g9-profil-svg" tabindex="0"></svg>
                    <label class="g9-profil-koppeln hb-versteckt"><input type="checkbox" checked> Seiten gleich (gespiegelt)</label>
                    <div class="g9-profil-wahl"></div>
                </div>
                <div class="scene-modal-footer">
                    <button type="button" class="btn-toggle" data-tat="anfasser-null">Anfasser zurück</button>
                    <button type="button" class="btn-toggle" data-tat="alles-null">Alles zurücksetzen</button>
                    <button type="button" class="primary" data-tat="uebernehmen">Übernehmen</button>
                </div>
            </div>`;
        document.body.appendChild(huelle);
        const z = { inst, regler, zeile, huelle, svg: huelle.querySelector('svg'), wahl: huelle.querySelector('.g9-profil-wahl'), daten: null, gewaehlt: 0,
                    koppeln: huelle.querySelector('.g9-profil-koppeln input') };
        const zu = () => Genesis9umrissfenster.schliessen(huelle);
        huelle._taste = (e) => Genesis9umrissfenster._taste(z, e, zu);
        huelle.querySelector('.scene-modal-close').addEventListener('click', zu);
        document.addEventListener('keydown', huelle._taste);
        huelle.querySelector('[data-tat="anfasser-null"]').addEventListener('click', () => Genesis9umrissfenster._setzen(z, z.gewaehlt, [0, 0]));
        huelle.querySelector('[data-tat="alles-null"]').addEventListener('click', () => {
            z.daten?.anfasser.forEach(a => { a.versatz = [0, 0]; });
            if (z.daten) Genesis9umrissfenster._zeichnen(z);
        });
        huelle.querySelector('[data-tat="uebernehmen"]').addEventListener('click', () => Genesis9umrissfenster._uebernehmen(z));
        Genesis9umrissfenster._offen = huelle;
        try {
            const daten = await Serverabruf.senden(Genesis9umrissfenster.adresse(regler.eigenregler.kennung, 'ansicht'), { regler: inst.regler || {} });
            if (daten.fehler) throw new Error(daten.fehler);
            z.daten = daten;
            huelle.querySelector('.g9-profil-hinweis').textContent = `Ansicht ${daten.text}. Anfasser ziehen oder anklicken und mit den Pfeiltasten schieben `
                + '(Umschalt: 2 mm). Grau gestrichelt: ohne diesen Regler.';
            huelle.querySelector('.g9-profil-koppeln').classList.toggle('hb-versteckt', !daten.partner?.length);
            Genesis9umrissfenster._ziehen(z);
            Genesis9umrissfenster._zeichnen(z);
            z.svg.focus();
        } catch (fehler) {
            z.wahl.textContent = `Nicht geladen: ${fehler.message}`;
        }
        return huelle;
    }

    static schliessen(huelle = null) {
        const ziel = huelle || Genesis9umrissfenster._offen;
        if (!ziel) return;
        document.removeEventListener('keydown', ziel._taste);
        ziel.remove();
        if (Genesis9umrissfenster._offen === ziel) Genesis9umrissfenster._offen = null;
    }

    /** Der geformte Umriss: Umriss + Σ Gewicht × Versatz je Anfasser (m, Ebene der Ansicht). */
    static geformt(daten) {
        return daten.umriss.map((p, i) => {
            let da = 0;
            let db = 0;
            daten.gewichte[i].forEach((w, a) => { da += w * daten.anfasser[a].versatz[0]; db += w * daten.anfasser[a].versatz[1]; });
            return [p[0] + da, p[1] + db];
        });
    }

    /** m → SVG (mm, y nach unten). */
    static _p(q) { return [q[0] * 1000, -q[1] * 1000]; }

    static _zeichnen(z) {
        const d = z.daten;
        const alle = d.umriss.map(Genesis9umrissfenster._p);
        const xs = alle.map(p => p[0]);
        const ys = alle.map(p => p[1]);
        const groesse = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
        const rand = 0.18 * groesse + 3;
        z.svg.setAttribute('viewBox', `${Math.min(...xs) - rand} ${Math.min(...ys) - rand} ${Math.max(...xs) - Math.min(...xs) + 2 * rand} ${Math.max(...ys) - Math.min(...ys) + 2 * rand}`);
        const punkte = (liste) => liste.map(Genesis9umrissfenster._p).map(p => `${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ');
        const form = d.geschlossen ? 'polygon' : 'polyline';
        const r = (0.022 * groesse + 0.4).toFixed(2);
        const kreise = d.anfasser.map((a, i) => {
            const [x, y] = Genesis9umrissfenster._p([a.punkt[0] + a.versatz[0], a.punkt[1] + a.versatz[1]]);
            const bewegt = Math.hypot(a.versatz[0], a.versatz[1]) > 1e-6 ? ' bewegt' : '';
            return `<circle class="g9-profil-anfasser${i === z.gewaehlt ? ' gewaehlt' : ''}${bewegt}" data-i="${i}" cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="${r}"
                    vector-effect="non-scaling-stroke"><title>${escapeHtml(a.anzeige)}</title></circle>`;
        }).join('');
        z.svg.innerHTML = `<${form} class="g9-profil-vorher" vector-effect="non-scaling-stroke" points="${punkte(d.umriss)}"/>
            <${form} class="g9-profil-nachher" vector-effect="non-scaling-stroke" points="${punkte(Genesis9umrissfenster.geformt(d))}"/>${kreise}`;
        const a = d.anfasser[z.gewaehlt];
        const mm = (v) => (v * 1000).toFixed(1).replace('.', ',');
        const bewegt = d.anfasser.filter(x => Math.hypot(...x.versatz) > 1e-6).length;
        z.wahl.innerHTML = `<b>${escapeHtml(a.anzeige)}</b>: im Bild nach rechts ${mm(a.versatz[0])} mm, nach oben ${mm(a.versatz[1])} mm
            <span class="gedaempft">· ${bewegt} von ${d.anfasser.length} Anfassern bewegt</span>`;
    }

    /** Versatz setzen; mit „Seiten gleich" auch den gespiegelten Anfasser (Anfasser auf der Mitte nur senkrecht). */
    static _setzen(z, i, versatz) {
        if (!z.daten) return;
        const partner = z.daten.partner?.[i];
        const gekoppelt = z.daten.partner?.length && z.koppeln.checked;
        if (gekoppelt && partner === i) versatz = [0, versatz[1]];
        z.daten.anfasser[i].versatz = versatz;
        if (gekoppelt && partner !== undefined && partner !== i) z.daten.anfasser[partner].versatz = [-versatz[0], versatz[1]];
        Genesis9umrissfenster._zeichnen(z);
    }

    /** Ziehen mit der Maus: Zeigerlage → SVG-Koordinaten (mm) → Versatz des Anfassers in m. */
    static _ziehen(z) {
        let zug = null;
        const lage = (e) => {
            const pt = new DOMPoint(e.clientX, e.clientY).matrixTransform(z.svg.getScreenCTM().inverse());
            return [pt.x / 1000, -pt.y / 1000];
        };
        z.svg.addEventListener('pointerdown', (e) => {
            const kreis = e.target.closest('.g9-profil-anfasser');
            if (!kreis) return;
            z.gewaehlt = Number(kreis.dataset.i);
            zug = { start: lage(e), versatz: [...z.daten.anfasser[z.gewaehlt].versatz] };
            z.svg.setPointerCapture(e.pointerId);
            Genesis9umrissfenster._zeichnen(z);
        });
        z.svg.addEventListener('pointermove', (e) => {
            if (!zug) return;
            const [x, y] = lage(e);
            Genesis9umrissfenster._setzen(z, z.gewaehlt, [zug.versatz[0] + x - zug.start[0], zug.versatz[1] + y - zug.start[1]]);
        });
        const ende = () => { zug = null; };
        z.svg.addEventListener('pointerup', ende);
        z.svg.addEventListener('pointercancel', ende);
    }

    static _taste(z, e, zu) {
        if (e.key === 'Escape') { zu(); return; }
        const schritt = { ArrowRight: [1, 0], ArrowLeft: [-1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
        if (!schritt || !z.daten || !z.huelle.contains(document.activeElement)) return;
        e.preventDefault();
        const m = (e.shiftKey ? 2 : Genesis9umrissfenster.PFEIL_MM) / 1000;
        const v = z.daten.anfasser[z.gewaehlt].versatz;
        Genesis9umrissfenster._setzen(z, z.gewaehlt, [v[0] + schritt[0] * m, v[1] + schritt[1] * m]);
    }

    /** Anfasserwerte in die Regler der Figur (m, auf ±`versatz_max_m` begrenzt, 0 = herausnehmen), dann neu bauen. */
    static _uebernehmen(z) {
        if (!z.daten) return;
        const regler = z.inst.regler = z.inst.regler || {};
        const grenze = z.daten.versatz_max_m || 0.15;
        let bewegt = 0;
        z.daten.anfasser.forEach(a => {
            a.regler.forEach((name, k) => {
                const v = Math.max(-grenze, Math.min(grenze, a.versatz[k]));
                if (Math.abs(v) < 1e-6) delete regler[name];
                else regler[name] = Math.round(v * 1e5) / 1e5;
            });
            if (Math.hypot(...a.versatz) > 1e-6) bewegt += 1;
        });
        const grund = `eigenform:${z.regler.eigenregler.kennung}`;
        Genesis9lauf.planen(z.inst, () => Genesis9groessehalten.umbauen(z.inst, grund, () => z.inst.neuFormen()), () => {}, grund);
        z.wahl.textContent = bewegt ? `Übernommen für diese Figur — ${bewegt} von ${z.daten.anfasser.length} Anfassern bewegt. Die Figur wird neu gebaut.`
            : 'Übernommen — keine Anfasser bewegt, die Form dieser Figur ist herausgenommen.';
    }
}
