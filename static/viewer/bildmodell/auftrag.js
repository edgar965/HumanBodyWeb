import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Bildmodellauftrag — der Zustand eines Auftrags und seine Nachfrage.
 *
 * Hält `zustand` (wie `/api/bildmodell/<id>/zustand/` ihn liefert), fragt
 * alle `TAKT_MS` nach, solange der Auftrag läuft, und ruft die Zuhörer
 * (`beiAenderung(zustand)`) nach jeder Antwort. Schreibende Aufrufe
 * (starten, anhalten, Bild stellen, Bilder hochladen, ersetzen, löschen)
 * gehen von hier aus.
 */
export class Bildmodellauftrag {

    static TAKT_MS = 2000;
    static SCHRITTE = ['sichtung', 'schaetzung', 'ziel', 'anpassung', 'rest', 'vorschau', 'textur', 'speichern'];

    constructor(zustand) {
        this.zustand = zustand;
        this.zuhoerer = [];
        this._timer = null;
    }

    get id() { return this.zustand.id; }
    get laeuft() { return this.zustand.status === 'laeuft'; }

    adresse(pfad) { return `/api/bildmodell/${this.id}/${pfad}`; }

    dateiAdresse(ordner, name) {
        return `/api/bildmodell/${this.id}/datei/${ordner}/${encodeURIComponent(name)}`;
    }

    zuhoeren(fn) { this.zuhoerer.push(fn); fn(this.zustand); }

    _melden() { for (const fn of this.zuhoerer) fn(this.zustand); }

    // ---------------------------------------------------------- Nachfrage

    verfolgen() {
        this._stopp();
        if (!this.laeuft) return;
        this._timer = setTimeout(() => this.nachfragen(), Bildmodellauftrag.TAKT_MS);
    }

    _stopp() { if (this._timer) { clearTimeout(this._timer); this._timer = null; } }

    async nachfragen() {
        try {
            const neu = await Serverabruf.json(this.adresse('zustand/'));
            if (neu && neu.id) { this.zustand = neu; this._melden(); }
        } catch (fehler) {
            console.warn('Bildmodell: Nachfrage fehlgeschlagen', fehler);
        }
        this.verfolgen();
    }

    // ------------------------------------------------------------- Aktionen

    /** `bis`: nur bis zu diesem Schritt (die Sichtung neuer Dateien, 19.09.2026);
     *  `schritte`: genau diese Schritte („Textur anpassen" = [sichtung,] textur). */
    async starten(optionen, ab, fest, bis = null, schritte = null) {
        const rumpf = { optionen, ab, fest: fest || {}, bis };
        if (schritte && schritte.length) { rumpf.schritte = schritte; ab = schritte[0]; }
        const antwort = await Serverabruf.senden(this.adresse('starten/'), rumpf);
        if (antwort.error) throw new Error(antwort.error);
        this.zustand.status = 'laeuft';
        this.zustand.schritt = ab;
        this.zustand.progress = 0;
        this.zustand.progress_detail = '';
        this.zustand.lauf = { ab, prozent: 0 };
        this.zustand.error = '';
        this._melden();
        this.verfolgen();
        return antwort;
    }

    async anhalten() {
        const antwort = await Serverabruf.senden(this.adresse('anhalten/'), {});
        if (antwort.error) throw new Error(antwort.error);
        await this.nachfragen();
    }

    async bildStellen(datei, aenderung) {
        const antwort = await Serverabruf.senden(this.adresse(`bild/${encodeURIComponent(datei)}/`), aenderung);
        if (antwort.error) throw new Error(antwort.error);
        const eintrag = (this.zustand.bilder || []).find(b => b.datei === datei);
        if (eintrag) {
            // Ganz ersetzen: ein Feld, das der Server entfernt hat (`teil`), darf nicht stehen bleiben.
            for (const k of Object.keys(eintrag)) delete eintrag[k];
            Object.assign(eintrag, antwort.bild);
        }
        if (antwort.textur) this.zustand.textur = antwort.textur;   // Hautton der gewählten Bilder
        if (antwort.texturbilder) this.zustand.texturbilder = antwort.texturbilder;
        this._melden();
        return antwort.bild;
    }

    /** `typen`: `{dateiname: {haupt, neben, nutzung}}` — die Sichtung übernimmt die Wahl (19.09.2026). */
    async bilderHochladen(dateien, typen = null) {
        const daten = new FormData();
        for (const d of dateien) daten.append('bilder', d, d.name);
        if (typen && Object.keys(typen).length) daten.append('typen', JSON.stringify(typen));
        const antwort = await Serverabruf.formular(this.adresse('bilder/'), daten);
        if (antwort.error) throw new Error(antwort.error);
        this.zustand.originale = antwort.originale;
        // Neu hochgeladene Dateien haben noch keinen Befund — die Seite listet sie zum Sichten.
        const quellen = new Set((this.zustand.bilder || []).map(b => b.quelle || b.datei));
        this.zustand.neue = antwort.originale.filter(n => !quellen.has(n));
        this._melden();
        return antwort;
    }

    // ------------------------------------------- Ersetzen und Löschen (19.09.2026)

    /** Die Antwort der Datei-Endpunkte ist der ganze Zustand. */
    _uebernehmen(antwort) {
        if (antwort.error) throw new Error(antwort.error);
        if (antwort.id) this.zustand = antwort;
        this._melden();
        return antwort;
    }

    async originalErsetzen(name, datei) {
        const daten = new FormData();
        daten.append('bild', datei, datei.name);
        return this._uebernehmen(await Serverabruf.formular(this.adresse(`original/${encodeURIComponent(name)}/ersetzen/`), daten));
    }

    async originalLoeschen(name) {
        return this._uebernehmen(await Serverabruf.senden(this.adresse(`original/${encodeURIComponent(name)}/loeschen/`), {}));
    }

    async bildLoeschen(datei) {
        return this._uebernehmen(await Serverabruf.senden(this.adresse(`bild/${encodeURIComponent(datei)}/loeschen/`), {}));
    }

    // ----------------------------------------------------------- Ergebnis

    /** Die Reglerstellung des Ergebnisses samt Restmorph — für die 3D-Ansicht. */
    stellung() {
        const e = this.zustand.ergebnis || {};
        const regler = { ...((e.anpassung || {}).regler || {}) };
        if (e.rest && e.rest.regler) regler[e.rest.regler] = 1.0;
        return regler;
    }

    ergebnisStand() {
        const e = this.zustand.ergebnis || {};
        return [e.anpassung ? e.anpassung.punkte_rms_mm : null,
                e.rest ? e.rest.rms_mit_morph_mm : null,
                (e.vorschau || {}).icon || ''].join('|');
    }
}
