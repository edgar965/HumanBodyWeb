import { Texturwahl } from './texturwahl.js';
import { Bildkachel } from './bildkachel.js';
import { Bildsteller } from './bildsteller.js';

/**
 * Bilderansicht — die Ausschnitte des Auftrags, nach Kategorie getrennt.
 *
 * Je Bereich (`#bereich-<kategorie>`, Reihenfolge aus der Vorlage) eine
 * Kachel je Ausschnitt (`Bildkachel`: Bild mit Rig, Befund, `Bildsteller`
 * mit drei Boxen, Gewicht, Textur, Ersetzen, Löschen). Änderungen gehen
 * sofort an den Server und ordnen die Kachel um.
 *
 * Oben: „Bilder oder Videos hinzufügen" (Edgar, 19.09.2026: „einen Button
 * oben zum Hinzufügen eines neuen Bildes") und „Neue Dateien sichten" —
 * startet den Lauf ab Sichtung, nur bis Sichtung, Umfang „nur neue Dateien".
 * Dateien ohne Befund (`zustand.neue`: hochgeladen oder ersetzt) stehen in
 * `#originale` mit Ersetzen/Löschen, bis die Sichtung sie einordnet.
 */
export class Bilderansicht {

    constructor(auftrag, katalog, formular) {
        this.auftrag = auftrag;
        this.formular = formular;
        this.steller = new Bildsteller(auftrag, katalog);
        this.kachel = new Bildkachel(auftrag, this.steller);
        this.rig = true;
        this._stand = '';
        document.getElementById('rig-schalter')?.addEventListener('change', e => {
            this.rig = e.target.checked;
            document.getElementById('bilder-karte').classList.toggle('ohne-rig', !this.rig);
        });
        // Welches Rig über den Bildern liegt (19.09.2026): die Sichtung liefert bis zu vier.
        this.rigWahl = 'auto';
        document.getElementById('rig-wahl')?.addEventListener('change', e => {
            this.rigWahl = e.target.value;
            this._stand = '';
            if (this._zustand) this.zeigen(this._zustand);
        });
        const dazu = document.getElementById('bilder-dazu');
        dazu?.addEventListener('change', async () => {
            if (!dazu.files.length) return;
            try { await this.auftrag.bilderHochladen([...dazu.files]); }
            catch (fehler) { window.alert(fehler.message); }
            dazu.value = '';
        });
        document.getElementById('neue-sichten')?.addEventListener('click', () => this.neueSichten());
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    zeigen(zustand) {
        this._zustand = zustand;
        Texturwahl.zusammenfassung(zustand);
        const bilder = zustand.bilder || [];
        const neue = zustand.neue || [];
        const stand = JSON.stringify(bilder.map(b => [b.datei, b.kategorie, b.ansicht, b.teil, b.nutzung, b.gewicht, b.manuell, b.textur_an,
            b.gvhmr ? (b.gvhmr.stand || b.gvhmr.fehler) : '']))
            + '|' + (zustand.originale || []).join(',') + '|' + neue.join(',') + '|' + this.rigWahl + '|' + zustand.status
            + '|' + zustand.schritt + '|' + ((zustand.optionen || {}).gvhmr_bild || '');
        if (stand === this._stand) return;
        this._stand = stand;
        this._neue(zustand, neue);
        const anzahl = document.getElementById('bilder-anzahl');
        if (anzahl) anzahl.textContent = bilder.length ? `${bilder.length} Ausschnitte aus ${(zustand.originale || []).length} Dateien` : `${(zustand.originale || []).length} Dateien`;
        for (const bereich of document.querySelectorAll('.bildmodell-bereich')) {
            const kategorie = bereich.dataset.kategorie;
            const eigene = bilder.filter(b => (b.kategorie || 'neben') === kategorie);
            bereich.classList.toggle('hb-versteckt', eigene.length === 0);
            bereich.querySelector('.bildmodell-zaehler').textContent = eigene.length ? `(${eigene.length})` : '';
            const feld = bereich.querySelector('.bildmodell-kacheln');
            feld.innerHTML = '';
            for (const b of eigene) feld.appendChild(this.kachel.element(b, this.rigWahl));
        }
    }

    /** Dateien ohne Befund — mit Ersetzen und Löschen, und dem Hinweis auf die Sichtung. */
    _neue(zustand, neue) {
        const feld = document.getElementById('originale');
        const knopf = document.getElementById('neue-sichten');
        if (!feld) return;
        feld.classList.toggle('hb-versteckt', neue.length === 0);
        if (knopf) {
            knopf.classList.toggle('hb-versteckt', neue.length === 0);
            knopf.disabled = zustand.status === 'laeuft';
            knopf.querySelector('span').textContent = `${neue.length} neue ${neue.length === 1 ? 'Datei' : 'Dateien'} sichten`;
        }
        feld.innerHTML = '';
        if (!neue.length) return;
        const kopf = document.createElement('h3');
        kopf.textContent = 'Noch nicht gesichtet';
        kopf.title = 'Hochgeladen oder ersetzt — „Neue Dateien sichten" ordnet sie ein';
        feld.appendChild(kopf);
        const kacheln = document.createElement('div');
        kacheln.className = 'bildmodell-kacheln';
        for (const name of neue) {
            const k = document.createElement('figure');
            k.className = 'bildmodell-kachel';
            const video = /\.(mp4|mov|webm|mkv|avi|m4v)$/i.test(name);
            const bild = document.createElement(video ? 'video' : 'img');
            bild.className = 'bildmodell-original';
            bild.src = this.auftrag.dateiAdresse('original', name) + `?t=${Date.now()}`;
            bild.title = name;
            if (video) bild.muted = true;
            const text = document.createElement('figcaption');
            text.innerHTML = `<span class="bildmodell-quelle" title="${name}">${name}</span><span class="bildmodell-befund">noch kein Befund</span>`;
            const knoepfe = document.createElement('div');
            knoepfe.className = 'bildmodell-steller';
            const zeile = document.createElement('div');
            zeile.className = 'bildmodell-stellerzeile bildmodell-stellerknoepfe';
            zeile.append(this.steller.ersetzenKnopf(name),
                this.steller.loeschenKnopf(`Datei ${name} löschen?`, () => this.auftrag.originalLoeschen(name)));
            knoepfe.appendChild(zeile);
            k.append(bild, text, knoepfe);
            kacheln.appendChild(k);
        }
        feld.appendChild(kacheln);
    }

    /** Nur die Sichtung, nur für die Dateien ohne Befund (Umfang „neue"). */
    async neueSichten() {
        try {
            const person = window.__bildmodell?.person?.werte?.() || {};
            const proportionen = window.__bildmodell?.proportionen?.werte?.() || {};
            const optionen = { ...(this.formular ? this.formular.werte() : {}), person, proportionen, umfang: 'neue' };
            await this.auftrag.starten(optionen, 'sichtung', {}, 'sichtung');
        } catch (fehler) {
            window.alert(`Sichtung nicht gestartet: ${fehler.message}`);
        }
    }
}
