import { Serverabruf } from '/static/djangobase/js/serverabruf.js';

/**
 * Effektverlauf — den Zustand EINES Effektauftrags nachfragen und im
 * Ausgabeschirm zeigen: Abzeichen, Balken, Detailzeile, am Ende das Video.
 *
 * Nachfrage alle TAKT_MS; bei Fehlern wachsender Abstand und Aufgabe nach
 * GRENZE Versuchen — wie `Auftragsstatus` (12.09.2026).
 */
export class Effektverlauf {

    static TAKT_MS = 2000;
    static WARTE_MS = 5000;
    static HOECHSTWARTE_MS = 30000;
    static GRENZE = 60;
    static ENDE = ['complete', 'failed', 'cancelled'];
    static BESCHRIFTUNG = { queued: 'Wartet', running: 'Läuft', complete: 'Fertig',
                            failed: 'Fehlgeschlagen', cancelled: 'Abgebrochen' };

    constructor(schirm, beiEnde = null) {
        this.schirm = schirm;
        this.beiEnde = beiEnde;
        this.fehlversuche = 0;
        this.zeiger = null;
        this.id = null;
    }

    el(kennung) {
        return this.schirm.querySelector('#' + kennung);
    }

    /** Einen laufenden Auftrag verfolgen. */
    verfolgen(id) {
        this.stoppen();
        this.id = id;
        this.fehlversuche = 0;
        this.laufAnzeigen();
        this.zeiger = setTimeout(() => this.nachfragen(), Effektverlauf.TAKT_MS);
    }

    stoppen() {
        if (this.zeiger) clearTimeout(this.zeiger);
        this.zeiger = null;
    }

    async nachfragen() {
        try {
            const daten = await Serverabruf.json(`/api/effekte/${this.id}/status/`);
            this.fehlversuche = 0;
            this.anzeigen(daten);
            if (Effektverlauf.ENDE.includes(daten.status)) {
                this.zeiger = null;
                if (this.beiEnde) this.beiEnde(daten);
                return;
            }
            this.zeiger = setTimeout(() => this.nachfragen(), Effektverlauf.TAKT_MS);
        } catch (fehler) {
            this.fehlversuch(fehler);
        }
    }

    fehlversuch(fehler) {
        this.fehlversuche++;
        if (this.fehlversuche >= Effektverlauf.GRENZE) {
            this.el('effektDetail').textContent = 'Verbindung verloren: ' + fehler.message;
            this.zeiger = null;
            return;
        }
        const warte = Math.min(Effektverlauf.WARTE_MS * this.fehlversuche,
                               Effektverlauf.HOECHSTWARTE_MS);
        this.el('effektDetail').textContent =
            `Keine Antwort (${this.fehlversuche}) — neuer Versuch in ${warte / 1000} s`;
        this.zeiger = setTimeout(() => this.nachfragen(), warte);
    }

    // ------------------------------------------------------------ Anzeige

    laufAnzeigen() {
        const video = this.el('effektVideo');
        video.hidden = true;
        video.removeAttribute('src');
        this.el('effektLeer').hidden = false;
        this.el('effektBalken').hidden = false;
        this.el('effektStopp').hidden = false;
        this.el('effektFehler').hidden = true;
        this.el('effektBericht').hidden = true;
        this.balken(0);
    }

    anzeigen(daten) {
        this.el('effektName').textContent = daten.name || '';
        const abzeichen = this.el('effektAbzeichen');
        abzeichen.textContent = Effektverlauf.BESCHRIFTUNG[daten.status] || daten.status;
        abzeichen.className = 'badge badge-' + daten.status;
        this.el('effektDetail').textContent = daten.progress_detail || '';
        this.balken(daten.progress || 0);
        if (daten.status === 'complete') this.fertig(daten);
        if (daten.status === 'failed' || daten.status === 'cancelled') this.gescheitert(daten);
    }

    balken(prozent) {
        this.el('effektFuellung').style.width = prozent + '%';
        this.el('effektProzent').textContent = prozent + '%';
    }

    fertig(daten) {
        this.el('effektBalken').hidden = true;
        this.el('effektStopp').hidden = true;
        this.el('effektLeer').hidden = true;
        this.el('effektFehler').hidden = true;
        const video = this.el('effektVideo');
        video.src = daten.video_url + '?t=' + Date.now();
        video.hidden = false;
        video.play().catch(() => {});
        this.bericht(daten);
    }

    gescheitert(daten) {
        this.el('effektBalken').hidden = true;
        this.el('effektStopp').hidden = true;
        this.el('effektLeerText').textContent = daten.status === 'cancelled'
            ? 'Abgebrochen.' : 'Fehlgeschlagen — Einzelheiten unten.';
        const fehler = this.el('effektFehler');
        fehler.textContent = daten.error || '';
        fehler.hidden = !daten.error;
    }

    bericht(daten) {
        const liste = this.el('effektBericht');
        liste.replaceChildren();
        for (const [titel, wert] of Effektverlauf.berichtzeilen(daten)) {
            if (!wert) continue;
            const dt = document.createElement('dt');
            dt.textContent = titel;
            const dd = document.createElement('dd');
            dd.textContent = wert;
            liste.append(dt, dd);
        }
        liste.hidden = false;
    }

    /**
     * Die Zeilen des Berichts — je Pipeline andere Kennzahlen, alle aus der
     * `.json` des Unterprozesses (Blender: Stoffpunkte, Simulationszeit;
     * Figur: Teile mit Sitz und Gleichlauf aus der Filmbilanz).
     */
    static berichtzeilen(daten) {
        const b = daten.bericht || {};
        const s = b.sekunden || {};
        const zeilen = [
            ['Pipeline', daten.modell ? `${daten.pipeline} — ${daten.modell}` : daten.pipeline || ''],
            ['Ausgabe', daten.ausgabe || ''],
        ];
        if (b.stoffpunkte) {
            zeilen.push(['Bilder', `${b.bilder} bei ${b.bildrate} fps, Stoff ${b.stoffpunkte} Punkte`]);
            zeilen.push(['Dauer', s.gesamt ? `${s.gesamt} s (Simulation ${s.simulation} s, Rendern ${s.rendern} s)` : '']);
        } else {
            zeilen.push(['Bilder', b.bilder ? `${b.bilder} bei ${b.bildrate} fps`
                + (b.bildrate_bvh ? ` (BVH ${Math.round(b.bildrate_bvh)} fps, Schritt ${b.schritt})` : '') : '']);
            zeilen.push(['Dauer', s.gesamt ? `${s.gesamt} s (Rendern ${s.rendern} s, Kodieren ${s.kodieren} s)` : '']);
            for (const teil of b.teile || []) {
                const sitz = teil.sitz_mm != null ? `Sitz ${teil.sitz_mm} mm` : '';
                const lauf = teil.gleichlauf_mm ? `Gleichlauf ${teil.gleichlauf_mm.join(' / ')} mm` : '';
                zeilen.push([teil.name, [`${teil.punkte} Punkte`, sitz, lauf].filter(Boolean).join(', ')]);
            }
        }
        return zeilen;
    }
}
