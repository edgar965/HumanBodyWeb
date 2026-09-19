import { Rigzeichnung } from './rigzeichnung.js';
import { Texturwahl } from './texturwahl.js';

/**
 * Bilderansicht — die Ausschnitte des Auftrags, nach Kategorie getrennt.
 *
 * Je Bereich (`#bereich-<kategorie>`, Reihenfolge aus der Vorlage) eine
 * Kachel je Ausschnitt: Bild mit Rig (SVG, `Rigzeichnung`), Quelle,
 * Ansicht/Haltung, Kategorie als Auswahl, Gewicht als Schieber — Änderungen
 * gehen sofort an den Server (`bildStellen`) und ordnen die Kachel um.
 * Vor der Sichtung stehen die Originale in `#originale`.
 */
export class Bilderansicht {

    static KATEGORIEN = { koerper: 'Hauptbild Körper', kopf: 'Hauptbild Kopf', video: 'Drehvideo',
                          neben: 'Nebenbild', gruppe: 'Gruppenbild', leer: 'Ohne Befund' };
    static ANSICHT = { vorne: 'von vorn', seite: 'von der Seite', hinten: 'von hinten',
                       dreiviertel: 'dreiviertel', drehung: 'Drehvideo' };

    constructor(auftrag) {
        this.auftrag = auftrag;
        this.rig = true;
        this._stand = '';
        document.getElementById('rig-schalter')?.addEventListener('change', e => {
            this.rig = e.target.checked;
            document.getElementById('bilder-karte').classList.toggle('ohne-rig', !this.rig);
        });
        // Welches Rig über den Bildern liegt (19.09.2026): die Sichtung liefert bis zu drei.
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
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    zeigen(zustand) {
        this._zustand = zustand;
        Texturwahl.zusammenfassung(zustand);
        const bilder = zustand.bilder || [];
        const stand = JSON.stringify(bilder.map(b => [b.datei, b.kategorie, b.gewicht, b.manuell]))
            + '|' + (zustand.originale || []).join(',') + '|' + this.rigWahl;
        if (stand === this._stand) return;
        this._stand = stand;
        this._originale(zustand, bilder.length > 0);
        const anzahl = document.getElementById('bilder-anzahl');
        if (anzahl) anzahl.textContent = bilder.length ? `${bilder.length} Ausschnitte aus ${(zustand.originale || []).length} Dateien` : `${(zustand.originale || []).length} Dateien`;
        for (const bereich of document.querySelectorAll('.bildmodell-bereich')) {
            const kategorie = bereich.dataset.kategorie;
            const eigene = bilder.filter(b => (b.kategorie || 'neben') === kategorie);
            bereich.classList.toggle('hb-versteckt', eigene.length === 0);
            bereich.querySelector('.bildmodell-zaehler').textContent = eigene.length ? `(${eigene.length})` : '';
            const feld = bereich.querySelector('.bildmodell-kacheln');
            feld.innerHTML = '';
            for (const b of eigene) feld.appendChild(this.kachel(b));
        }
    }

    _originale(zustand, versteckt) {
        const feld = document.getElementById('originale');
        if (!feld) return;
        feld.classList.toggle('hb-versteckt', versteckt);
        if (versteckt) return;
        feld.innerHTML = '';
        for (const name of zustand.originale || []) {
            const bild = document.createElement('img');
            bild.className = 'bildmodell-original';
            bild.src = this.auftrag.dateiAdresse('original', name);
            bild.title = name;
            feld.appendChild(bild);
        }
    }

    kachel(b) {
        const k = document.createElement('figure');
        k.className = 'bildmodell-kachel';
        k.dataset.datei = b.datei;
        const rahmen = document.createElement('div');
        rahmen.className = 'bildmodell-bildrahmen';
        // Der Rahmen bekommt das Seitenverhältnis des Bildes: so füllt das Bild
        // ihn ganz, und das Rig-SVG (viewBox 0 0 1 1) liegt Punkt für Punkt darauf.
        if (b.breite && b.hoehe) rahmen.style.aspectRatio = `${b.breite} / ${b.hoehe}`;
        const bild = document.createElement('img');
        bild.src = this.auftrag.dateiAdresse('zuschnitt', b.datei);
        bild.alt = b.datei;
        bild.loading = 'lazy';
        rahmen.appendChild(bild);
        const rig = this.rigFuer(b);
        if (rig.art === 'mediapipe') {
            rahmen.appendChild(Rigzeichnung.svg(b.landmarken, b.gesicht, (b.breite || 3) / (b.hoehe || 4), b.haende_punkte));
        } else if (rig.punkte) {
            rahmen.appendChild(Rigzeichnung.cocoSvg(rig.punkte, (b.breite || 3) / (b.hoehe || 4)));
        }
        k.appendChild(rahmen);
        const text = document.createElement('figcaption');
        const teile = [];
        if (b.ansicht) teile.push(Bilderansicht.ANSICHT[b.ansicht] || b.ansicht);
        if (b.video) teile.push(`${b.bilder || '?'} Bilder` + (b.fps ? ` bei ${b.fps} fps` : ''));
        else if (b.haltung) teile.push(b.haltung === 'neutral' ? 'neutrale Haltung' : 'posiert');
        if (b.koerper_sichtbar) teile.push(`${Math.round(b.koerper_sichtbar * 100)} % Körper`);
        if (b.gesicht && b.gesicht.hoehe) teile.push(`Gesicht ${Math.round(b.gesicht.hoehe * 100)} %`);
        if (b.punkte) teile.push(`${b.punkte} YOLO-Punkte`);
        if (rig.art && rig.art !== 'mediapipe' && rig.teile.length) teile.push(`${rig.art}: ${rig.teile.join(', ')}`);
        if (b.haende_punkte && b.haende_punkte.length) {
            teile.push(b.haende_punkte.map(h => `${h.seite === 'Left' ? 'linke' : 'rechte'} Hand ${Math.round(h.guete * 100)} %`).join(', '));
        }
        const s = b.schaetzung;
        if (s && s.fehler) teile.push(`Schätzer: ${s.fehler}`);
        else if (s && s.frames) teile.push(`${s.backend}: eine Form aus ${s.frames} Bildern`);
        else if (s) teile.push(`${s.backend}: ${Math.round((s.confidence || 0) * 100)} %`);
        if (s && s.silhouette && s.silhouette.iou_nachher != null) {
            teile.push(`Silhouette ${Math.round(s.silhouette.iou_vorher * 100)} → ${Math.round(s.silhouette.iou_nachher * 100)} %`);
        } else if (s && s.silhouette && s.silhouette.fehler) teile.push(`Silhouette: ${s.silhouette.fehler}`);
        if (b.fehler) teile.push(b.fehler);
        text.innerHTML = `<span class="bildmodell-quelle" title="${b.quelle || ''}">${(b.quelle || b.datei)}</span>`
            + `<span class="bildmodell-befund">${teile.join(' · ')}</span>`;
        k.appendChild(text);
        k.appendChild(this.steller(b));
        const textur = Texturwahl.feld(b, (datei, aenderung) => this.stellen(datei, aenderung));
        if (textur) k.appendChild(textur);
        return k;
    }

    /** Das Rig, das die Wahl für dieses Bild ergibt: `{art, punkte, teile}`. */
    rigFuer(b) {
        const rigs = b.rigs || {};
        const hatMp = !!(b.landmarken || b.gesicht || (b.haende_punkte && b.haende_punkte.length));
        const wahl = this.rigWahl || 'auto';
        const reihe = wahl === 'auto' ? ['mediapipe', 'yolo', 'openpifpaf'] : [wahl];
        for (const art of reihe) {
            if (art === 'mediapipe' && hatMp) return { art, punkte: b.landmarken, teile: [] };
            const r = rigs[art];
            if (art !== 'mediapipe' && r && r.punkte) return { art, punkte: r.punkte, teile: r.teile || [] };
        }
        return { art: null, punkte: null, teile: [] };
    }

    steller(b) {
        const zeile = document.createElement('div');
        zeile.className = 'bildmodell-steller';
        const wahl = document.createElement('select');
        for (const [wert, anzeige] of Object.entries(Bilderansicht.KATEGORIEN)) {
            const o = document.createElement('option');
            o.value = wert; o.textContent = anzeige; o.selected = (b.kategorie || 'neben') === wert;
            wahl.appendChild(o);
        }
        wahl.title = 'Kategorie — die Anpassung nimmt Hauptbilder Körper und Kopf';
        wahl.addEventListener('change', () => this.stellen(b.datei, { kategorie: wahl.value }));
        const gewicht = document.createElement('input');
        gewicht.type = 'range'; gewicht.min = '0'; gewicht.max = '1'; gewicht.step = '0.1';
        gewicht.value = String(b.gewicht ?? 0);
        gewicht.title = 'Gewicht in der Mischung (0 = nicht verwendet)';
        const wert = document.createElement('span');
        wert.className = 'bildmodell-gewicht';
        wert.textContent = Number(gewicht.value).toFixed(1);
        gewicht.addEventListener('input', () => { wert.textContent = Number(gewicht.value).toFixed(1); });
        gewicht.addEventListener('change', () => this.stellen(b.datei, { gewicht: Number(gewicht.value) }));
        zeile.append(wahl, gewicht, wert);
        if (b.manuell) {
            const m = document.createElement('span');
            m.className = 'bildmodell-manuell'; m.title = 'von Hand gestellt'; m.textContent = '✎';
            zeile.appendChild(m);
        }
        return zeile;
    }

    async stellen(datei, aenderung) {
        try { await this.auftrag.bildStellen(datei, aenderung); }
        catch (fehler) { window.alert(fehler.message); }
    }
}
