/**
 * Auftragname — den Namen eines Auftrags auf seiner Seite ändern (29.09.2026).
 *
 * Edgar: „die namen sollen in allen Jobs angegeben werden können … geänderte namen dann
 * auch in der Übersicht". Der Name stand in der Überschrift und war nur beim Anlegen
 * setzbar. Jetzt ist die Überschrift selbst das Eingabefeld: klicken (oder auf den Stift),
 * schreiben, Enter — Escape nimmt zurück.
 *
 * Wie `Auftragloeschen` kennt diese Klasse keinen Bereich; alles Bereichsspezifische steht
 * als `data-`Attribut am Namensfeld:
 *   data-adresse  Endpunkt `POST /api/modell-aus-dateien/<bereich>/<id>/name/` (Pflicht)
 *
 * Die Übersicht zeigt denselben Wert aus der Datenbank — sie braucht deshalb nichts
 * nachgezogen zu bekommen, sondern nur den nächsten Aufruf (`auftragsseiten.md`).
 */
import { Serverabruf } from './serverabruf.js';

export class Auftragname {

    static FELD = 'auftrag-name';

    /** Bindet das Namensfeld, falls die Seite eines hat. */
    static binden(id = Auftragname.FELD) {
        const feld = document.getElementById(id);
        if (!feld || !feld.dataset.adresse) return null;
        return new Auftragname(feld).aufbauen();
    }

    constructor(feld) {
        this.feld = feld;
        this.adresse = feld.dataset.adresse;
        this.laeuft = false;
    }

    aufbauen() {
        this.feld.classList.add('auftrag-name-editierbar');
        this.feld.title = 'Namen ändern';
        this.feld.addEventListener('click', () => this.bearbeiten());
        const stift = document.createElement('button');
        stift.type = 'button';
        stift.className = 'btn btn-secondary btn-sm auftrag-name-stift';
        stift.title = 'Namen ändern';
        stift.innerHTML = '<i class="fas fa-pen"></i>';
        stift.addEventListener('click', (ereignis) => { ereignis.stopPropagation(); this.bearbeiten(); });
        this.feld.after(' ', stift);
        this.stift = stift;
        return this;
    }

    /** Überschrift gegen ein Eingabefeld tauschen. */
    bearbeiten() {
        if (this.eingabe) { this.eingabe.focus(); return; }
        const alt = this.feld.textContent.trim();
        const eingabe = document.createElement('input');
        eingabe.type = 'text';
        eingabe.className = 'viewer-eingabe auftrag-name-eingabe';
        eingabe.maxLength = 200;
        eingabe.value = alt;
        eingabe.addEventListener('keydown', (ereignis) => {
            if (ereignis.key === 'Enter') { ereignis.preventDefault(); this.speichern(eingabe.value, alt); }
            if (ereignis.key === 'Escape') { ereignis.preventDefault(); this.beenden(alt); }
        });
        // Blur speichert ebenfalls — ein Klick daneben soll die Eingabe nicht verwerfen.
        eingabe.addEventListener('blur', () => { if (this.eingabe) this.speichern(eingabe.value, alt); });
        this.feld.style.display = 'none';
        if (this.stift) this.stift.style.display = 'none';
        this.feld.after(eingabe);
        this.eingabe = eingabe;
        eingabe.focus();
        eingabe.select();
    }

    async speichern(neu, alt) {
        const name = (neu || '').trim();
        if (this.laeuft) return;
        if (!name || name === alt) { this.beenden(alt); return; }
        this.laeuft = true;
        try {
            const antwort = await Serverabruf.senden(this.adresse, { name });
            if (antwort && antwort.error) throw new Error(antwort.error);
            this.beenden(antwort.name || name);
            document.title = document.title.replace(alt, antwort.name || name);
        } catch (fehler) {
            this.beenden(alt);
            window.alert(`Name konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
        } finally {
            this.laeuft = false;
        }
    }

    beenden(text) {
        if (this.eingabe) { this.eingabe.remove(); this.eingabe = null; }
        this.feld.textContent = text;
        this.feld.style.display = '';
        if (this.stift) this.stift.style.display = '';
    }
}
