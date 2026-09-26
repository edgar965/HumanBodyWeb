import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from './meshoptionenformular.js';
import { Meshbetrachter } from './meshbetrachter.js';
import { Meshfotogewicht } from './meshfotogewicht.js';

/**
 * Meshauftragseite — die Auftragsseite des Reiters „Mesh" (26.09.2026): Lauf verfolgen
 * (wie `Bildmodellauftrag`), Ergebnis im `Meshbetrachter` zeigen, Downloads, Fotos mit
 * Rolle, Optionen erneut stellbar.
 */
export class Meshauftragseite {

    static TAKT_MS = 2000;
    //: Gewicht/Bereich erst 500 ms nach der letzten Reglerbewegung an den Server — die
    //: Live-Vorschau (Baustein `Meshfotogewicht`) reagiert unabhängig davon sofort.
    static GEWICHT_SPEICHERN_MS = 500;

    static starten(jobId) {
        const daten = JSON.parse(document.getElementById('mesh-daten').textContent);
        const seite = new Meshauftragseite(jobId, daten.zustand, daten.katalog);
        seite.aufbauen();
        return seite;
    }

    constructor(jobId, zustand, katalog) {
        this.jobId = jobId;
        this.zustand = zustand;
        this.katalog = katalog;
        this._timer = null;
        this._geladenesGlb = null;
        this._fotogewicht = new Meshfotogewicht((ordner, name) => this.dateiAdresse(ordner, name));
        this._fotogewichtBereit = false;
        this._gewichtSpeicherTimer = {};
    }

    adresse(pfad) { return `/api/mesh/${this.jobId}/${pfad}`; }

    dateiAdresse(ordner, name) {
        return `/api/mesh/${this.jobId}/datei/${ordner}/${encodeURIComponent(name)}`;
    }

    aufbauen() {
        this.betrachter = new Meshbetrachter(document.getElementById('betrachter'));
        Meshoptionenformular.bauen(document.getElementById('mesh-optionen'), this.katalog, this.zustand.optionen);
        document.getElementById('starten').addEventListener('click', () => this.starten());
        document.getElementById('anhalten').addEventListener('click', () => this.anhalten());
        document.getElementById('mesh-weitere-dateien').addEventListener('change', e => this.weitereBilder([...e.target.files]));
        document.getElementById('textur-uebernehmen').addEventListener('click', () => this.retexturieren());
        this.zeigen();
        this.verfolgen();
    }

    // ---------------------------------------------------------------- Lauf

    async starten() {
        const optionen = Meshoptionenformular.lesen(document.getElementById('mesh-optionen'));
        const antwort = await Serverabruf.senden(this.adresse('starten/'), { optionen });
        if (antwort.error) { window.alert(antwort.error); return; }
        this.zustand.status = 'laeuft';
        this.zeigen();
        this.nachfragen();
    }

    async anhalten() {
        await Serverabruf.senden(this.adresse('anhalten/'), {});
        this.nachfragen();
    }

    async weitereBilder(dateien) {
        if (!dateien.length) return;
        const daten = new FormData();
        for (const d of dateien) daten.append('bilder', d, d.name);
        const antwort = await Serverabruf.formular(this.adresse('bilder/'), daten);
        if (antwort.bilder) { this.zustand.bilder = antwort.bilder; this.zeigen(); }
    }

    async rolleSetzen(datei, rolle) {
        const antwort = await Serverabruf.senden(this.adresse(`rolle/${encodeURIComponent(datei)}/`), { rolle });
        if (antwort.bild) {
            const eintrag = this.zustand.bilder.find(b => b.datei === datei);
            if (eintrag) eintrag.rolle = antwort.bild.rolle;
        }
    }

    /** Gewicht (0..100) sofort lokal übernehmen (Live-Vorschau), Server-Ablage debounced —
     *  ein Regler, der bei jedem Pixel eine Anfrage schickt, würde den Server fluten. */
    gewichtLokalSetzen(datei, gewicht) {
        const eintrag = this.zustand.bilder.find(b => b.datei === datei);
        if (eintrag) eintrag.gewicht = gewicht;
        this._texturVorschauAktualisieren();
        clearTimeout(this._gewichtSpeicherTimer[datei]);
        this._gewichtSpeicherTimer[datei] = setTimeout(
            () => Serverabruf.senden(this.adresse(`gewicht/${encodeURIComponent(datei)}/`), { gewicht }),
            Meshauftragseite.GEWICHT_SPEICHERN_MS);
    }

    /** Nur die Textur neu — Form bleibt (Server nutzt `form_cache.npz`, siehe `mesh.md`).
     *  `Serverabruf.senden` WIRFT bei einem Nicht-2xx-Status (z. B. 409 „läuft schon"/„noch
     *  nicht fertig") statt ein `{error}`-JSON zurückzugeben — deshalb try/catch, nicht
     *  `if (antwort.error)` (das bestehende `starten()` verlässt sich darauf, dass der Knopf
     *  in diesem Fall schon disabled ist; hier zusätzlich abgesichert). */
    async retexturieren() {
        const knopf = document.getElementById('textur-uebernehmen');
        const hinweis = document.getElementById('textur-hinweis-live');
        knopf.disabled = true;
        hinweis.textContent = '';
        try {
            await Serverabruf.senden(this.adresse('retexturieren/'), {});
        } catch (fehler) {
            hinweis.textContent = fehler.daten?.error || fehler.message || 'Textur übernehmen fehlgeschlagen';
            knopf.disabled = false;
            return;
        }
        this.zustand.status = 'laeuft';
        this.zeigen();
        this.nachfragen();
    }

    verfolgen() {
        this._stopp();
        if (this.zustand.status !== 'laeuft') return;
        this._timer = setTimeout(() => this.nachfragen(), Meshauftragseite.TAKT_MS);
    }

    _stopp() { if (this._timer) { clearTimeout(this._timer); this._timer = null; } }

    async nachfragen() {
        try {
            const neu = await Serverabruf.json(this.adresse('zustand/'));
            if (neu && neu.id) { this.zustand = neu; this.zeigen(); }
        } catch (fehler) {
            console.warn('Mesh: Nachfrage fehlgeschlagen', fehler);
        }
        this.verfolgen();
    }

    // -------------------------------------------------------------- Zeigen

    zeigen() {
        const z = this.zustand;
        document.getElementById('fortschritt').style.width = `${z.progress || 0}%`;
        document.getElementById('fortschritt-text').textContent =
            z.status === 'laeuft' ? `${z.progress || 0} % — ${z.progress_detail || z.schritt || ''}`
                : (z.status === 'fertig' ? 'Fertig' : z.progress_detail || '');
        const status = document.getElementById('auftrag-status');
        status.textContent = { angelegt: 'Angelegt', laeuft: 'Läuft', fertig: 'Fertig',
                               gescheitert: 'Fehlgeschlagen', angehalten: 'Angehalten' }[z.status] || z.status;
        status.className = `bildmodell-status hb-${z.status === 'fertig' ? 'gut' : z.status === 'gescheitert' ? 'schlecht' : 'laeuft'}`;
        document.getElementById('starten').disabled = z.status === 'laeuft';
        document.getElementById('anhalten').disabled = z.status !== 'laeuft';
        const fehler = document.getElementById('fehler');
        fehler.textContent = z.error || '';
        fehler.classList.toggle('hb-versteckt', !z.error);
        this._kennzahlen();
        this._downloads();
        this._fotoliste();
        this._netzLaden();
    }

    _kennzahlen() {
        const e = this.zustand.ergebnis || {};
        const dl = document.getElementById('kennzahlen');
        dl.innerHTML = '';
        const zeilen = [
            ['Formmodell', ({ trellis2: 'TRELLIS.2', hunyuan3d_2: 'Hunyuan3D-2.0', hunyuan3d_2mv: 'Hunyuan3D-2mv' })[e.formmodell] || e.formmodell || '—'],
            ['Textur', ({ trellis2_pbr: 'gelernt (TRELLIS.2)', hunyuan_paint: 'gemalt (Hunyuan3D)',
                        fotos: 'aus den Fotos', fusion_fotos: 'aus den Fotos (Fusion)', keine: 'keine' })[e.textur_quelle] || '—'],
            ['Punkte', e.punkte != null ? e.punkte.toLocaleString('de-DE') : '—'],
            ['Flächen', e.flaechen != null ? e.flaechen.toLocaleString('de-DE') : '—'],
            ['Dauer', e.dauer_s != null ? `${Math.round(e.dauer_s)} s` : '—'],
        ];
        for (const [k, v] of zeilen) {
            const dt = document.createElement('dt'); dt.textContent = k;
            const dd = document.createElement('dd'); dd.textContent = v;
            dl.append(dt, dd);
        }
    }

    _downloads() {
        const dateien = (this.zustand.ergebnis || {}).dateien || {};
        const behaelter = document.getElementById('downloads');
        behaelter.innerHTML = '';
        const NAMEN = { glb: 'GLB (mit Textur)', obj: 'OBJ + MTL', ply: 'PLY' };
        for (const [art, name] of Object.entries(NAMEN)) {
            if (!dateien[art]) continue;
            const link = document.createElement('a');
            link.href = `${this.dateiAdresse('ergebnis', dateien[art])}?laden=1`;
            link.className = 'btn btn-secondary btn-sm';
            link.innerHTML = `<i class="fas fa-download"></i> ${name}`;
            behaelter.appendChild(link);
        }
    }

    _fotoliste() {
        const behaelter = document.getElementById('fotoliste');
        behaelter.innerHTML = '';
        for (const eintrag of this.zustand.bilder || []) {
            const karte = document.createElement('div');
            karte.className = 'mesh-fotokarte';
            const bild = document.createElement('img');
            bild.className = 'mesh-vorschau';
            bild.src = this.dateiAdresse('eingang', eintrag.datei);
            const rolle = document.createElement('select');
            rolle.className = 'viewer-select mesh-rollenwahl';
            for (const opt of this.katalog.rollen) {
                const option = document.createElement('option');
                option.value = opt.wert; option.textContent = opt.text;
                option.selected = opt.wert === eintrag.rolle;
                rolle.appendChild(option);
            }
            rolle.addEventListener('change', () => this.rolleSetzen(eintrag.datei, rolle.value));
            const gewichtZeile = document.createElement('div');
            gewichtZeile.className = 'mesh-gewichtzeile';
            const gewicht = document.createElement('input');
            gewicht.type = 'range';
            gewicht.min = '0';
            gewicht.max = '100';
            gewicht.value = String(eintrag.gewicht ?? 100);
            gewicht.title = 'Anteil dieses Fotos an der Textur (bei Fusion auch an der Form)';
            const gewichtWert = document.createElement('span');
            gewichtWert.className = 'mesh-gewichtwert';
            gewichtWert.textContent = `${gewicht.value} %`;
            gewicht.addEventListener('input', () => {
                gewichtWert.textContent = `${gewicht.value} %`;
                this.gewichtLokalSetzen(eintrag.datei, Number(gewicht.value));
            });
            gewichtZeile.append(gewicht, gewichtWert);
            karte.append(bild, rolle, gewichtZeile);
            behaelter.appendChild(karte);
        }
    }

    async _netzLaden() {
        const glb = ((this.zustand.ergebnis || {}).dateien || {}).glb;
        const hinweis = document.getElementById('betrachter-hinweis');
        // Kein Netz (nie gelaufen, gescheitert oder gerade am Rechnen) -> „Textur übernehmen"
        // muss gesperrt bleiben, sonst zeigt der Server nur einen 409-Fehler (kein Cache).
        document.getElementById('textur-uebernehmen').disabled = !glb;
        if (!glb) { if (hinweis) hinweis.style.display = ''; return; }
        const url = this.dateiAdresse('ergebnis', glb);
        if (this._geladenesGlb === url) return;
        this._geladenesGlb = url;
        if (hinweis) hinweis.style.display = 'none';
        this._fotogewichtBereit = false;
        try {
            await this.betrachter.laden(url);
        } catch (fehler) {
            console.error('Mesh: GLB konnte nicht geladen werden', fehler);
            if (hinweis) { hinweis.textContent = 'Netz konnte nicht geladen werden.'; hinweis.style.display = ''; }
            return;
        }
        document.getElementById('textur-uebernehmen').disabled = false;
        const live = document.getElementById('textur-hinweis-live');
        if (Meshfotogewicht.aktiv(this.zustand.ergebnis)) {
            try {
                await this._fotogewicht.vorbereiten(this.zustand.bilder);
                this._fotogewichtBereit = true;
                this._texturVorschauAktualisieren();
                live.textContent = '';
            } catch (fehler) {
                console.warn('Mesh: Live-Texturvorschau nicht verfügbar', fehler);
            }
        } else {
            live.textContent = 'Diese Textur kommt vom Formmodell selbst — die Live-Vorschau '
                + 'wirkt erst nach „Textur übernehmen".';
        }
    }

    /** Färbt die geladene Geometrie mit den aktuellen Fotogewichten neu — rein clientseitig,
     *  kein Server-Rundtrip (`Meshfotogewicht`). Ohne Wirkung, solange `_fotogewichtBereit`
     *  falsch ist (Textur kommt vom Formmodell, oder das Netz ist für die Live-Vorschau zu groß). */
    _texturVorschauAktualisieren() {
        if (!this._fotogewichtBereit) return;
        for (const knoten of this.betrachter.meshKnoten()) {
            const anzahl = knoten.geometry.attributes.position.count;
            if (!this._fotogewicht.bereit(anzahl)) continue;
            this._fotogewicht.anwenden(knoten.geometry, this.zustand.bilder);
            if (knoten.material) {
                knoten.material.vertexColors = true;
                knoten.material.needsUpdate = true;
            }
        }
    }
}
