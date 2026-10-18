import { escapeHtml } from '../utils.js';
import { Genesis9seiten } from './genesis9seiten.js';

/**
 * Genesis9reglerliste — die Reglerliste des Genesis-Bedienfelds: Bereiche, darin Gruppen, darüber Suche, „nur geänderte" und „Seiten koppeln"
 * (18.10.2026, Auftrag Edgar „mach die Empfehlung" — Konzept `Docu/konzepte/2026-10-18_genesis9-regler-vereinfachen-konzept.md`).
 *
 * Die Gliederung kommt fertig vom Server (`Genesis9/reglergliederung.py`): je Bereich die Regler in Reihenfolge, jeder mit `gruppe` (leer = direkt im
 * Bereich). Hier wird nur gezeichnet. Bis dahin gab es im Genesis-Feld KEIN Suchfeld (nur in `bildmodell/reglerfeld.js`) — bei 2.406 Reglern.
 *
 * Gefiltert wird über die Zeilen, nicht über neu gebaute Listen: Ein Treffer klappt seinen Bereich und seine Gruppe auf, was die Suche geöffnet hat,
 * klappt sie beim Leeren wieder zu (sonst stünde nach drei Suchen die halbe Liste offen).
 */
export class Genesis9reglerliste {

    static RUHE_MS = 150;

    /**
     * @param behaelter  `#prop-genesis9-regler`
     * @param kopf       Platz für die Werkzeugzeile (`#prop-genesis9-reglerkopf`)
     * @param zeileBauen `regler → .slider-row`
     * @param anhaengen  `(kasten, bereich) → void` — Zusätze je Bereich (Kopf-Eigen-Link, Körpermorph-Formular)
     */
    static fuellen(behaelter, kopf, plan, zeileBauen, anhaengen) {
        behaelter.innerHTML = '';
        const bereiche = plan.bereiche || [];
        if (!bereiche.length) {
            behaelter.innerHTML = `<div class="gedaempft">${escapeHtml(plan.fehler || 'Keine Regler gefunden.')}</div>`;
            return;
        }
        Genesis9seiten.kennen(plan);
        const liste = new Genesis9reglerliste(behaelter, plan);
        for (const bereich of bereiche) {
            const kasten = Genesis9reglerliste._kasten('uma-gruppe', bereich.name, bereich.regler.length);
            let gruppe = null;
            for (const r of bereich.regler) {
                if (!r.gruppe) { kasten.appendChild(zeileBauen(r)); continue; }
                if (gruppe?.dataset.gruppe !== r.gruppe) {
                    const anzahl = bereich.regler.filter(x => x.gruppe === r.gruppe).length;
                    gruppe = Genesis9reglerliste._kasten('uma-gruppe g9-untergruppe', r.gruppe, anzahl);
                    gruppe.dataset.gruppe = r.gruppe;
                    kasten.appendChild(gruppe);
                }
                gruppe.appendChild(zeileBauen(r));
            }
            anhaengen(kasten, bereich);
            behaelter.appendChild(kasten);
        }
        if (kopf) liste.werkzeuge(kopf);
    }

    static _kasten(klasse, titel, anzahl) {
        const kasten = document.createElement('details');
        kasten.className = klasse;
        kasten.innerHTML = `<summary>${escapeHtml(titel)} <span class="gedaempft">(${anzahl})</span></summary>`;
        return kasten;
    }

    constructor(behaelter, plan) {
        this.behaelter = behaelter;
        this.vorgaben = new Map((plan.bereiche || []).flatMap(b => b.regler || []).map(r => [r.name, r.vorgabe ?? 0]));
        this.suche = '';
        this.nurGeaendert = false;
        this.geoeffnet = new Set();
        this._zeit = null;
    }

    /** Die Werkzeugzeile: Suchfeld, „nur geänderte", „Seiten koppeln". */
    werkzeuge(kopf) {
        kopf.innerHTML = `
            <input type="search" class="hb-dehnt g9-reglersuche" placeholder="Regler suchen … (Name, z. B. Nase, HB_, Neck)">
            <label class="g9-reglerschalter" title="Nur Regler zeigen, die nicht auf ihrem Ausgangswert stehen">
                <input type="checkbox" data-schalter="geaendert"> nur geänderte</label>
            <label class="g9-reglerschalter" title="Ein Zug an einem linken Regler stellt den rechten mit (Left/Right im Namen) — und umgekehrt">
                <input type="checkbox" data-schalter="seiten"> Seiten koppeln</label>`;
        const suche = kopf.querySelector('input[type="search"]');
        suche.addEventListener('input', () => {
            clearTimeout(this._zeit);
            this._zeit = setTimeout(() => { this.suche = suche.value.trim().toLowerCase(); this.filtern(); }, Genesis9reglerliste.RUHE_MS);
        });
        const geaendert = kopf.querySelector('[data-schalter="geaendert"]');
        geaendert.addEventListener('change', () => { this.nurGeaendert = geaendert.checked; this.filtern(); });
        const seiten = kopf.querySelector('[data-schalter="seiten"]');
        seiten.checked = Genesis9seiten.an();
        seiten.addEventListener('change', () => Genesis9seiten.schalten(seiten.checked));
    }

    filtern() {
        const aktiv = Boolean(this.suche) || this.nurGeaendert;
        for (const zeile of this.behaelter.querySelectorAll('.slider-row')) {
            const schieber = zeile.querySelector('input[data-regler]');
            zeile.classList.toggle('hb-versteckt', aktiv && !(schieber && this._passt(zeile, schieber)));
        }
        // Von innen nach außen: erst die Gruppen, dann die Bereiche — ein Bereich ist sichtbar, wenn eine seiner Zeilen es ist.
        const kaesten = [...this.behaelter.querySelectorAll('details')].reverse();
        for (const kasten of kaesten) {
            const sichtbar = !aktiv || kasten.querySelector('.slider-row:not(.hb-versteckt)') !== null;
            kasten.classList.toggle('hb-versteckt', !sichtbar);
            if (aktiv && sichtbar && !kasten.open) { kasten.open = true; this.geoeffnet.add(kasten); }
        }
        // Formulare und Links in den Bereichen sind keine Regler — beim Filtern weg.
        for (const rest of this.behaelter.querySelectorAll('details > :not(summary):not(.slider-row):not(details)')) {
            rest.classList.toggle('hb-versteckt', aktiv);
        }
        if (!aktiv) {
            for (const kasten of this.geoeffnet) kasten.open = false;
            this.geoeffnet.clear();
        }
    }

    _passt(zeile, schieber) {
        if (this.suche) {
            const text = `${zeile.querySelector('label')?.textContent || ''} ${schieber.dataset.regler}`.toLowerCase();
            if (!text.includes(this.suche)) return false;
        }
        if (this.nurGeaendert) {
            const vorgabe = this.vorgaben.get(schieber.dataset.regler) ?? 0;
            if (Math.abs(parseFloat(schieber.value) - vorgabe) < 1e-6) return false;
        }
        return true;
    }
}
