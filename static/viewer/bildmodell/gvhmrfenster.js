import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Dialoggroesse } from './dialoggroesse.js';
import { Proportionen3dbuehne } from './proportionen3dbuehne.js';
import { Smplxrig } from './smplxrig.js';
import { Zielkaefig } from './zielkaefig.js';
import { base64ToFloat32 } from '../gemeinsam/kodierung.js';

/**
 * Gvhmrfenster — das Ausgabefenster „SMPL-X mit GVHMR" für EIN Bild.
 *
 * Edgar (20.09.2026): „ich brauch kein ‚Bild neu' sondern eines um eine GVHMR
 * erkennung zu machen, mit ausgabe fenster dazu!" — „mach ein ausgabefenster
 * in 3D mit dem SMPL modell dazu inkl. Rig".
 *
 * Ein `<dialog>` (`bildmodell_gvhmr_dialog.html`, vergrößerbar, Größe gemerkt):
 * links das Foto, rechts das SMPL-X-Netz (bläulich) mit dem Rig (`Smplxrig`,
 * 55 Gelenke und Knochen, orange, durch die Haut sichtbar) auf einer
 * `Proportionen3dbuehne`; darunter der Fortschritt des Laufs (`progress_detail`
 * des Einzelschritts `gvhmr`, solange er für dieses Bild läuft) und die Zahlen
 * des Ergebnisses (Höhe, Bilder, Dauer, Betas, Stand). `oeffnen(datei, rechnen)`
 * zeigt das Fenster; mit `rechnen` oder ohne Ergebnis startet es den Lauf
 * (`Gvhmrknopf.starten`) und lädt Netz und Rig, sobald der Auftrag fertig meldet.
 *
 * `ART` macht das Fenster für einen zweiten Einzelschritt nutzbar: `Flamefenster`
 * (FLAME-Kopf eines Kopfbilds, 20.09.2026 — Edgar: „warum gibt es beim Kopf keine
 * Button zum Lauf und Erzeugung eines 3D-Modells?") tauscht Schritt, Feld, Endpunkt,
 * Dialog und Texte; das Rig gibt es nur bei GVHMR.
 */
export class Gvhmrfenster {

    static MERKER = 'bildmodell.gvhmr.groesse';
    static FARBE = 0xb9c6da;
    static ART = {
        schritt: 'gvhmr', feld: 'gvhmr', endpunkt: 'gvhmr3d', dialog: 'gvhmr-dialog', rig: true,
        name: 'GVHMR', ordner: 'schaetzung/gvhmr/',
        start: 'GVHMR startet — Standvideo, Vorstufe, Modell (30–70 s) …',
        neu: 'GVHMR wird neu gerechnet …', kette: 'Modell aus GVHMR',
    };

    constructor(auftrag, knopf) {
        this.auftrag = auftrag;
        this.knopf = knopf;
        this.art = this.constructor.ART;
        this.dialog = document.getElementById(this.art.dialog);
        this.datei = null;
        this.buehne = null;
        this.rig = null;
        this._stand = null;
        this._kette = null;   // Text, solange nach GVHMR das Modell rechnet
        this._netz = null;    // Text zum geladenen Netz — kommt nach der Kette zurück
        if (!this.dialog) return;
        this.felder = {};
        for (const e of this.dialog.querySelectorAll('[data-feld]')) this.felder[e.dataset.feld] = e;
        for (const k of this.dialog.querySelectorAll('[data-tat="schliessen"]')) k.addEventListener('click', () => this.schliessen());
        this.dialog.querySelector('[data-tat="rechnen"]')?.addEventListener('click', () => this.rechnen());
        this.dialog.querySelector('[data-tat="oben"]')?.addEventListener('click', () => this.knopf.ansehen(this.datei));
        this.dialog.querySelector('[data-tat="gitter"]')?.addEventListener('change', e => this.buehne?.gitterZeigen(e.target.checked));
        this.dialog.querySelector('[data-tat="rig"]')?.addEventListener('change', e => { if (this.rig) this.rig.visible = e.target.checked; });
        this.dialog.querySelector('[data-tat="foto"]')?.addEventListener('click', () => this.buehne?.fotoansicht());
        const zelle = this.felder.canvas?.parentElement;
        if (zelle && typeof ResizeObserver !== 'undefined') new ResizeObserver(() => this._leinwandPassen()).observe(zelle);
        this.dialog.addEventListener('close', () => this.buehne?.anhalten());
        Dialoggroesse.merken(this.dialog, this.constructor.MERKER);
        auftrag.zuhoeren(z => this._zustand(z));
    }

    get offen() { return !!this.dialog && this.dialog.open; }

    _eintrag(datei = this.datei) {
        return ((this.auftrag.zustand || {}).bilder || []).find(b => b.datei === datei) || null;
    }

    /** Fenster für `datei` zeigen; `rechnen` erzwingt einen neuen Lauf, sonst nur ohne Ergebnis. */
    oeffnen(datei, rechnen = false) {
        if (!this.dialog) { window.alert('Kein Ausgabefenster auf dieser Seite.'); return; }
        this.datei = datei;
        this._stand = null;
        this._kette = null;
        this._netz = null;
        this.felder.datei.textContent = datei;
        this.felder.foto.src = this.auftrag.dateiAdresse('zuschnitt', datei);
        if (!this.buehne) {
            try {
                this.buehne = new Proportionen3dbuehne(this.felder.canvas);
                this.rig = this.art.rig ? new Smplxrig(this.buehne.szene) : null;
            } catch (fehler) { this._melden(`Keine 3D-Ansicht: ${fehler.message}`); }
        }
        // Ein neues Bild: Netz und Rig des vorigen weg — `netzSetzen` tauscht sonst nur Punkte.
        if (this.buehne) {
            this.buehne.kaefig.dispose();
            this.buehne.kaefig = new Zielkaefig(this.buehne.szene);
            this.rig?.leeren();
            this.buehne.fotokamera(null);
            this._leinwandPassen();
        }
        if (!this.dialog.open) this.dialog.showModal();
        this.buehne?.starten();
        const e = this._eintrag();
        const g = (e && e[this.art.feld]) || {};
        this._zahlen(g);
        if (rechnen || !(g.netz || g.fehler)) this.rechnen(rechnen);
        else if (g.netz) this._laden();
        else this._melden(`${this.art.name}: ${g.fehler}`);
    }

    schliessen() { if (this.dialog?.open) this.dialog.close(); }

    /** Mittlere Tiefe (−z) des Netzes in Kamerasicht — der Drehpunkt der Orbit-Steuerung. */
    _tiefe(b64) {
        const p = base64ToFloat32(b64);
        let summe = 0, n = 0;
        for (let i = 2; i < p.length; i += 3) { summe += p[i]; n++; }
        return n ? -summe / n : 2.0;
    }

    /** Die Leinwand so groß wie es die Zelle erlaubt, im Seitenverhältnis des Fotos (mit Fotokamera);
     *  ohne füllt sie die Zelle. Läuft bei jeder Größenänderung der Zelle. */
    _leinwandPassen() {
        const leinwand = this.felder.canvas, zelle = leinwand?.parentElement;
        if (!leinwand || !zelle) return;
        const k = this.buehne?.foto;
        if (!k) { leinwand.style.width = '100%'; leinwand.style.height = '100%'; return; }
        const zb = zelle.clientWidth, zh = zelle.clientHeight;
        if (!zb || !zh) return;
        const seitig = k.breite / k.hoehe;
        let b = zb, h = zb / seitig;
        if (h > zh) { h = zh; b = zh * seitig; }
        leinwand.style.width = `${Math.floor(b)}px`;
        leinwand.style.height = `${Math.floor(h)}px`;
    }

    _melden(t) { if (this.felder.text) this.felder.text.textContent = t; }

    /** Den Lauf starten — der Knopf kennt den Rumpf; hier nur Anzeige. */
    async rechnen(neu = true) {
        const e = this._eintrag();
        neu = neu && !!(e && e[this.art.feld] && e[this.art.feld].netz);
        this.felder.balken.hidden = false;
        this.felder.balken.value = 0;
        this._melden(neu ? this.art.neu : this.art.start);
        await this.knopf.starten(this.datei, neu);
    }

    /** Jede Nachfrage des Auftrags: Fortschritt zeigen, fertiges Netz laden. */
    _zustand(z) {
        if (!this.offen || !this.datei) return;
        const bild = (z.optionen || {}).gvhmr_bild;
        const meins = Array.isArray(bild) ? bild.includes(this.datei) : bild === this.datei;
        const laeuft = z.status === 'laeuft' && z.schritt === this.art.schritt && meins;
        if (laeuft) {
            this.felder.balken.hidden = false;
            this.felder.balken.value = z.progress || 0;
            this._melden(`${z.progress || 0} % · ${z.progress_detail || `${this.art.name} läuft …`}`);
            return;
        }
        // Nach GVHMR rechnet derselbe Lauf das Modell neu (`Bildmodelllauf.NACH_GVHMR`: Schätzung,
        // Ziel, Regler, Rest, Vorschau) — Vorher/Nachher-Bilder der Tabelle kommen dann aus GVHMR.
        // Das Netz ist schon da und wird unten geladen; der Balken läuft weiter.
        const kette = z.status === 'laeuft' && meins && (z.optionen || {}).ab === this.art.schritt;
        if (kette) {
            this.felder.balken.hidden = false;
            this.felder.balken.value = z.progress || 0;
            this._kette = `${z.progress || 0} % · ${this.art.kette}: ${z.progress_detail || z.schritt || '…'}`;
            if (this._stand) this._melden(this._kette);
        } else if (this._kette) {
            this._kette = null;
            this.felder.balken.hidden = true;
            if (this._netz) this._melden(this._netz);
        }
        const g = (this._eintrag() || {})[this.art.feld] || null;
        const stand = g ? (g.stand || g.fehler) : null;
        if (!g || stand === this._stand) return;
        this._stand = stand;
        this.felder.balken.hidden = !kette;
        this._zahlen(g);
        if (g.netz) this._laden();
        else this._melden(`${this.art.name}: ${g.fehler || 'kein Ergebnis'}`);
    }

    async _laden() {
        this._melden('Netz wird geladen …');
        try {
            const antwort = await Serverabruf.json(this.auftrag.adresse(`${this.art.endpunkt}/${encodeURIComponent(this.datei)}/`));
            if (!antwort || antwort.error) throw new Error((antwort || {}).error || 'keine Antwort');
            // In der Kamera des Fotos, wenn der Lauf sie ablegte (seit 20.09. spät): dieselbe Pose,
            // derselbe Ausschnitt wie das 2D-Bild — sonst die aufgestellte Weltlage (Blick zur Kamera).
            const k = antwort.kamera || null;
            const sicht = k ? { ...antwort, punkte: k.punkte, gelenke: k.gelenke } : antwort;
            if (this.buehne) {
                this.buehne.netzSetzen(sicht);
                if (this.buehne.netz) this.buehne.netz.material.color.set(this.constructor.FARBE);
                this.buehne.gitterZeigen(!!this.dialog.querySelector('[data-tat="gitter"]')?.checked);
                this.rig?.setzen(sicht);
                if (this.rig) this.rig.visible = this.dialog.querySelector('[data-tat="rig"]')?.checked !== false;
                this.buehne.fotokamera(k, k ? this._tiefe(k.punkte) : 2.0);
                this._leinwandPassen();
            }
            const rig = !this.art.rig ? '' : this.rig && this.rig.da ? `, Rig ${this.rig.anzahl} Gelenke` : ', ohne Rig (Lauf vor dem Rig — „Neu rechnen")';
            const lage = k ? `in der Kamera des Fotos (${k.breite} × ${k.hoehe} px, f = ${Math.round(k.fx)} px)`
                           : this.art.rig ? 'aufrecht, Blick zur Kamera — Lauf vor der Fotokamera, „Neu rechnen" zeigt den Ausschnitt des Fotos'
                           : 'von vorn, Kopf im Ursprung (FLAME kennt keine Fotokamera)';
            this._netz = `${(antwort.anzahl || 0).toLocaleString('de-DE')} Punkte, ${antwort.hoehe_cm} cm${rig} — ${lage}`;
            this._melden(this._kette || this._netz);
        } catch (fehler) {
            this._melden(`Netz nicht geladen: ${fehler.message}`);
        }
    }

    /** Die Zahlen des Ergebnisses als Tabelle. */
    _zahlen(g) {
        const rumpf = this.felder.zahlen?.querySelector('tbody');
        if (!rumpf) return;
        const zeilen = [];
        if (g.hoehe_m) zeilen.push(['Höhe des Netzes', `${g.hoehe_m.toFixed(3)} m`]);
        if (g.frames) zeilen.push(['Bilder im Standvideo', String(g.frames)]);
        if (g.punkte) zeilen.push(['Punkte', g.punkte.toLocaleString('de-DE')]);
        if (g.dauer_s != null) zeilen.push(['Dauer', `${g.dauer_s} s`]);
        if (g.confidence != null) zeilen.push(['Zuversicht (PyMAF-X)', Number(g.confidence).toFixed(2)]);
        if (g.betas) zeilen.push(['Betas (SMPL-X, 10)', g.betas.map(b => b.toFixed(2)).join('  ')]);
        if (g.stand) zeilen.push(['Stand', new Date(g.stand).toLocaleString('de-DE')]);
        if (g.fehler) zeilen.push(['Fehler', g.fehler]);
        rumpf.innerHTML = zeilen.map(([k, v]) => `<tr><th>${k}</th><td>${v}</td></tr>`).join('');
        if (this.felder.dateien) this.felder.dateien.textContent = g.netz ? `${this.art.ordner}${g.netz}` : '';
    }
}
