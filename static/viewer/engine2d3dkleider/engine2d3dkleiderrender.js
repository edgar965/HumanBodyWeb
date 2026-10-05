import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Engine2d3dKleiderrenderlaeufe } from './engine2d3dkleiderrenderlaeufe.js';

/**
 * Engine2d3dKleiderrender — der Render-Schritt rechts neben dem Export (Edgar, 03.10.2026: „füge rechts auch den render schritt hinzu, mit Option, wie
 * lange der sein soll (in s bis zur ganzen bvh in s)", „mit pfadangabe wo der Output gerendert ist").
 *
 * Länge in Sekunden (10 Bilder bis zur ganzen BVH; Knöpfe „10 Bilder", „30 Bilder", „ganze BVH" — Edgar, 04.10.2026: erst 10, dann 30, dann alles), Kamerafahrt und Bildgröße; Audio und BVH gelten wie beim Export (`export-audio`, `export-bvh-pfad`).
 * Der Server rechnet in einem eigenen Prozess (`Engine2d3dKleiderrender`); den Stand liefert der Zustand des Auftrags (`render`: Stufe, Fortschritt,
 * Ausgabepfade). Das fertige Video steht mit seinen Pfaden unter dem Knopf: `ergebnis/render_video.mp4` und die Kopie im Exportordner.
 */
export class Engine2d3dKleiderrender {

    constructor(seite) {
        this.seite = seite;
        const $ = id => document.getElementById(id);
        this.sekunden = $('render-sekunden');
        this.max = $('render-max');
        this.ganz = $('render-ganz');
        this.stufen = [$('render-10'), $('render-30')];
        this.kamera = $('render-kamera');
        this.groesse = $('render-groesse');
        this.spp = $('render-spp');
        this.anmerkung = $('render-anmerkung');
        this.laeufe = new Engine2d3dKleiderrenderlaeufe(seite, nummern => this.neu(nummern));
        this.knopf = $('render-starten');
        this.meldung = $('render-meldung');
        this._dauer = 0;
        this._angefasst = false;
        this._schickt = false;
        this.sekunden.addEventListener('input', () => { this._angefasst = true; });
        this.ganz.addEventListener('click', () => { this.sekunden.value = String(this._dauer); this._angefasst = true; });
        // Die Stufen der Qualitätsprüfung: 10 Bilder, 30 Bilder, dann die ganze BVH.
        for (const [knopf, bilder] of [[this.stufen[0], 10], [this.stufen[1], 30]]) {
            knopf.addEventListener('click', () => { this.sekunden.value = (bilder / 30).toFixed(2); this._angefasst = true; });
        }
        this.knopf.addEventListener('click', () => this.starten());
    }

    /** Die Länge in Sekunden: auf ganze Bilder (1/30 s) gerundet, mindestens 10 Bilder, höchstens die ganze BVH. */
    laenge() {
        const wert = Math.round(Number(this.sekunden.value) * 30) / 30;
        return Math.min(Math.max(wert, 10 / 30), this._dauer || wert);
    }

    zeigen(z) {
        const r = z.render || {};
        this._dauer = Number(r.dauer || 0);
        this.sekunden.max = String(this._dauer || '');
        this.max.textContent = this._dauer ? `bis ${this._dauer.toFixed(1).replace('.', ',')} s (ganze BVH)` : 'keine BVH';
        if (this._dauer && !this._angefasst) this.sekunden.value = '0.33';    // zuerst 10 Bilder
        const laeuft = r.status === 'laeuft' || this._schickt;
        const fehlt = z.laeuft ? 'Der Auftrag rechnet gerade' : !r.moeglich ? 'Für diesen Auftrag gibt es noch kein Render-Rezept'
            : !this._dauer ? 'Es gibt noch keine Bewegung (BVH wählen oder einmal exportieren)' : null;
        this.knopf.disabled = !!fehlt || laeuft;
        this.knopf.title = fehlt || 'Rendert das Modell mit Bewegung und Ton als Video';
        for (const feld of [this.sekunden, this.kamera, this.groesse, this.spp, this.anmerkung, this.ganz, ...this.stufen]) feld.disabled = laeuft;
        this._anzeigen(r, fehlt);
        this.laeufe.zeigen(r.laeufe, r.status === 'laeuft' ? r : null);        // läuft ein Render, trägt seine Zeile die Anzeige „läuft" (Fortschritt, Schritt, Zeit)
        this.laeufe.sperren(laeuft || !!fehlt, laeuft ? 'Es läuft schon ein Render' : fehlt || '');       // „Neu rendern" in der Tabelle: gleiche Bedingungen wie „Rendern"
    }

    _anzeigen(r, fehlt) {
        this.meldung.classList.toggle('hb-schlecht', r.status === 'fehler');
        this.meldung.replaceChildren();
        const zeile = text => { const d = document.createElement('div'); d.textContent = text; this.meldung.appendChild(d); return d; };
        if (r.status === 'laeuft') {
            const vergangen = r.start ? Math.round(Date.now() / 1000 - r.start) : 0;
            const neu = r.neu_nr ? `Lauf #${r.neu_nr} neu · ` : '';
            const warten = r.wartend ? ` · danach noch ${r.wartend} in der Warteschlange` : '';
            zeile(`${neu}${r.schritt || 'Läuft'} — ${Math.round((r.fortschritt || 0) * 100)} % · ${r.bilder} Bilder (${r.sekunden} s) · ${vergangen} s${warten}`);
        } else if (r.status === 'fehler') {
            zeile(`Render fehlgeschlagen: ${r.fehler || 'unbekannt'}`);
        } else if (r.status === 'fertig' && r.ausgabe) {
            zeile(`Fertig in ${r.dauer_s} s: ${r.bilder} Bilder (${r.sekunden} s)${r.ausgabe.ton ? ' mit Ton' : ' ohne Ton'}, ${(r.ausgabe.bytes / 1048576).toFixed(1)} MB`);
            const link = document.createElement('a');
            link.href = r.ausgabe.adresse;
            link.target = '_blank';
            link.textContent = r.ausgabe.pfad;
            const erste = zeile('Video: ');
            erste.appendChild(link);
            zeile(`Kopie im Exportordner: ${r.ausgabe.export}`);
        } else if (fehlt) {
            zeile(fehlt);
        }
    }

    /** „Neu rendern" aus der Tabelle: `nummern` = Liste von Laufnummern oder `'alle'`. Der Server prüft alle Läufe vor dem Start und rechnet sie nacheinander. */
    async neu(nummern) {
        this._schickt = true;
        this.zeigen(this.seite.zustand);
        const audio = document.getElementById('export-audio');
        const tonPfad = document.getElementById('export-audio-pfad');
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('render/neu/'), {
                ...(nummern === 'alle' ? { alle: true } : { nummern }), ton: audio.checked ? tonPfad.value.trim() : '',
            });
            if (antwort.error) throw new Error(antwort.error);
            this.seite.zustand.render = antwort.render;
        } catch (fehler) {
            this.meldung.classList.add('hb-schlecht');
            this.meldung.textContent = `Neu rendern nicht gestartet: ${fehler.daten?.error || fehler.message}`;
        } finally {
            this._schickt = false;
            this.zeigen(this.seite.zustand);
        }
    }

    async starten() {
        this._schickt = true;
        this.zeigen(this.seite.zustand);
        const audio = document.getElementById('export-audio');
        const tonPfad = document.getElementById('export-audio-pfad');
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('render/'), {
                sekunden: this.laenge(), kamera: this.kamera.value, groesse: this.groesse.value, spp: Number(this.spp.value),
                anmerkung: this.anmerkung.value.trim(),
                ton: audio.checked ? tonPfad.value.trim() : '', name: document.getElementById('export-name').value.trim(),
            });
            if (antwort.error) throw new Error(antwort.error);
            this.seite.zustand.render = antwort.render;
        } catch (fehler) {
            this.meldung.classList.add('hb-schlecht');
            this.meldung.textContent = `Render nicht gestartet: ${fehler.daten?.error || fehler.message}`;
        } finally {
            this._schickt = false;
            this.zeigen(this.seite.zustand);
        }
    }
}
