import { Knopfsanduhr } from '../gemeinsam/knopfsanduhr.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Exportleisteaufloesung } from './exportleisteaufloesung.js';
import { Exportleisteexport } from './exportleisteexport.js';
import { Exportleistefigur } from './exportleistefigur.js';
import { Exportleistelaeufe } from './exportleistelaeufe.js';

/**
 * Exportleisterender — der Block „Rendern" der Exportleiste (31.10.2026): die Figur der Seite mit der BVH-Bewegung (Feld im Block „Exportieren") und dem Ton als Video.
 *
 * Länge in Sekunden (10 Bilder bis zur ganzen BVH; „10 Bilder", „30 Bilder", „ganze BVH" — erst die Qualität prüfen, dann länger), Kamera, Größe (frei, `Exportleisteaufloesung`),
 * Physik an/aus, Proben je Pixel, Anmerkung, die Regler (`Exportleisteregler`, vor dem Start gespeichert). Der Browser schickt die Figur als GLB, der Server rechnet in einem eigenen
 * Prozess (`Exportleisterender`, unter der Gpusperre); den Stand zeigt der Zustand im Takt der Leiste, die fertigen Läufe `Exportleistelaeufe`. `mp4` ist der MP4-Export des Blocks
 * „Exportieren": derselbe Weg über die ganze BVH, mit Auflösung, Physik, Ordner und Namen von dort.
 */
export class Exportleisterender {

    constructor(leiste) {
        this.leiste = leiste;
        const $ = id => leiste.wurzel.querySelector(`#${id}`);
        this.sekunden = $('exportleiste-sekunden');
        this.max = $('exportleiste-max');
        this.kamera = $('exportleiste-kamera');
        this.groesse = new Exportleisteaufloesung($('exportleiste-groesse'), $('exportleiste-breite'), $('exportleiste-hoehe'));
        this.physik = $('exportleiste-physik');
        this.spp = $('exportleiste-spp');
        this.anmerkung = $('exportleiste-anmerkung');
        this.knopf = $('exportleiste-rendern');
        this.meldung = $('exportleiste-render-meldung');
        // Ziel des Videos (31.10.2026, Edgar: „wo wird die gerenderte Datei gespeichert?“): eigene Felder, einmal vorbelegt (Exportordner, `<Name>_render`), danach gehören sie dem Nutzer
        this.ordner = $('exportleiste-render-ordner');
        this.datei = $('exportleiste-render-datei');
        this.suchen = $('exportleiste-render-suchen');
        this.suchen.addEventListener('click', () => Exportleisteexport.ordnerSuchen(this.ordner, this.suchen, text => { this.meldung.textContent = text; }));
        this.stufen = [...leiste.wurzel.querySelectorAll('[data-bilder]')];
        this.laeufe = new Exportleistelaeufe($('exportleiste-laeufe'), teil => leiste.adresse(teil), nummern => this.neu(nummern), nummern => this.loeschen(nummern));
        this._dauer = 0;
        this._schickt = false;
        for (const knopf of this.stufen) {
            knopf.addEventListener('click', () => {
                this.sekunden.value = knopf.dataset.bilder === 'ganz' ? String(this._dauer) : (Number(knopf.dataset.bilder) / 30).toFixed(2);
            });
        }
        this.knopf.addEventListener('click', () => this.starten());
    }

    /** Die Länge auf ganze Bilder (1/30 s), mindestens 10 Bilder, höchstens die ganze BVH. */
    laenge() {
        const wert = Math.round(Number(this.sekunden.value) * 30) / 30;
        return Math.min(Math.max(wert, 10 / 30), this._dauer || wert);
    }

    zeigen(z) {
        const r = z.render || {};
        if (!this.ordner.value) this.ordner.value = z.exportordner || '';
        if (!this.datei.value) this.datei.value = z.name ? `${z.name}_render` : '';
        this._dauer = Number(z.bvh?.sekunden || 0);
        this.sekunden.max = String(this._dauer || '');
        this.max.textContent = this._dauer ? `bis ${this._dauer.toFixed(1).replace('.', ',')} s (ganze BVH)` : (z.bvh?.fehler || 'keine BVH');
        const laeuft = r.status === 'laeuft' || this._schickt;
        const fehlt = !r.moeglich ? 'Die Programme des Render-Rezepts fehlen (Figurfilm/standfilm)' : !this._dauer ? 'Erst eine BVH wählen (Block „Exportieren“)' : z.sperre || null;
        Knopfsanduhr.setzen(this.knopf, laeuft, 'Rendert …', !!fehlt);
        this.knopf.title = laeuft ? 'Ein Render läuft — der Stand steht darunter' : fehlt || 'Rendert die Figur mit Bewegung und Ton als Video';
        for (const feld of [this.sekunden, this.kamera, this.physik, this.spp, this.anmerkung, this.ordner, this.datei, this.suchen, ...this.stufen]) feld.disabled = laeuft;
        this.groesse.sperren(laeuft);
        this.leiste.regler.sperren(laeuft);
        this._anzeigen(r, fehlt);
        this.laeufe.zeigen(r.laeufe);
        this.laeufe.sperren(laeuft || !!z.sperre);
    }

    _anzeigen(r, fehlt) {
        this.meldung.classList.toggle('hb-schlecht', r.status === 'fehler');
        this.meldung.replaceChildren();
        const zeile = text => { const d = document.createElement('div'); d.textContent = text; this.meldung.appendChild(d); return d; };
        if (r.status === 'laeuft') {
            const vergangen = r.start ? Math.round(Date.now() / 1000 - r.start) : 0;
            const neu = r.neu_nr ? ` · Lauf #${r.neu_nr} neu${r.wartend ? `, ${r.wartend} warten` : ''}` : '';
            zeile(`${r.schritt || 'Läuft'} — ${Math.round((r.fortschritt || 0) * 100)} % · ${r.bilder} Bilder (${Number(r.sekunden).toFixed(2)} s) · ${vergangen} s${neu}`);
        } else if (r.status === 'fehler') {
            zeile(`Render fehlgeschlagen: ${r.fehler || 'unbekannt'}`);
        } else if (r.status === 'fertig' && r.ausgabe) {
            zeile(`Fertig in ${r.dauer_s} s: ${r.bilder} Bilder (${Number(r.sekunden).toFixed(2)} s)${r.ausgabe.ton ? ' mit Ton' : ' ohne Ton'}, ${(r.ausgabe.bytes / 1048576).toFixed(1)} MB`);
            const link = document.createElement('a');
            link.href = r.ausgabe.adresse;
            link.target = '_blank';
            link.textContent = r.ausgabe.export;
            zeile('Gespeichert unter: ').appendChild(link);
        } else if (fehlt) {
            zeile(fehlt);
        }
    }

    starten() {
        return this._senden('render/', {
            sekunden: this.laenge(), kamera: this.kamera.value, ...this.groesse.wert(), physik: this.physik.checked, spp: Number(this.spp.value), anmerkung: this.anmerkung.value.trim(),
        });
    }

    /** MP4-Export (Block „Exportieren"): die ganze BVH, `{breite, hoehe, physik, ordner, datei}` von dort, Kamera und Qualität von hier. */
    mp4(angaben) {
        return this._senden('render/', {
            sekunden: this._dauer, kamera: this.kamera.value, spp: Number(this.spp.value), anmerkung: `MP4-Export ${angaben.physik ? 'mit' : 'ohne'} Physik`, ...angaben,
        });
    }

    /** „Neu rendern" (`Exportleistelaeufe`): `[nr]` oder 'alle' — Einstellungen je Lauf, BVH, Ton und Ordner der Leiste für Läufe, die keine eigenen mitbringen. */
    neu(nummern) {
        return this._senden('render/neu/', nummern === 'alle' ? { alle: true } : { nummern });
    }

    /** Löschen (`Exportleistelaeufe`): die Läufe samt Video und Bogen; die Antwort trägt den neuen Stand der Tabelle. */
    async loeschen(nummern) {
        try {
            const antwort = await Serverabruf.senden(this.leiste.adresse('render/loeschen/'), { nummern });
            if (antwort.error) throw new Error(antwort.error);
            if (this.leiste.zustand) this.leiste.zustand.render = antwort.render;
            this.zeigen(this.leiste.zustand || {});
            return true;
        } catch (fehler) {
            this.meldung.classList.add('hb-schlecht');
            this.meldung.textContent = `Löschen fehlgeschlagen: ${fehler.daten?.error || fehler.message}`;
            return false;
        }
    }

    async _senden(teil, eigen) {
        this._schickt = true;
        this.zeigen(this.leiste.zustand || {});
        const exp = this.leiste.export;
        try {
            await this.leiste.regler.speichern();
            this.meldung.textContent = this.leiste.zustand?.eigenes_modell ? 'Der Render wird gestartet …' : 'Die Figur wird ganz gebaut und als GLB an den Server geschickt …';
            const { blob, stellung } = await this.leiste.figur.fuerServer();
            const daten = Exportleistefigur.formular(blob, {
                ton: exp.audio.checked ? exp.audioPfad.value.trim() : '', bvh: exp.bvh.value.trim(), stellung,
                name: exp.name.value.trim(), ordner: this.ordner.value.trim(), datei: this.datei.value.trim(), ...eigen,
            });
            const antwort = await Serverabruf.formular(this.leiste.adresse(teil), daten);
            if (antwort.error) throw new Error(antwort.error);
            if (this.leiste.zustand) this.leiste.zustand.render = antwort.render;
        } catch (fehler) {
            this._schickt = false;
            this.zeigen(this.leiste.zustand || {});
            this.meldung.classList.add('hb-schlecht');
            this.meldung.textContent = `Render nicht gestartet: ${fehler.daten?.error || fehler.message}`;
            return false;
        }
        this._schickt = false;
        this.zeigen(this.leiste.zustand || {});
        return true;
    }
}
