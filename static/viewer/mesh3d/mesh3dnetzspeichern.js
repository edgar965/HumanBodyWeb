import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3dnetzteileliste } from './mesh3dnetzteileliste.js';

/**
 * Mesh3dnetzspeichern — der Teil von „Netz bearbeiten“, der schreibt (13.10.2026, `Mesh3dnetzwerkzeug`): die entfernten Flächen als neue GLB speichern (`POST …/netzschnitt/`), die Datei zur Quelle des Auftrags machen
 * (`POST …/netzuebernahme/`, oder gleich beim Speichern) und danach von vorn rechnen (`Mesh3dlauf.neu`).
 *
 * Wird die Datei zur Quelle, sind die Ergebnisse des Auftrags verworfen und der Auftrag „Mesh to 3D“ entfernt (`Mesh3dquellwechsel`); die 3D-Ansicht darüber zeigt dann eine Figur, die es nicht mehr gibt. Darum lädt
 * die Seite danach NEU — alle Karten stehen dann auf dem Stand des Servers — und die Meldung („Gespeichert: …“) überlebt den Neustart über `sessionStorage` (eine Zeile, nach dem Zeigen gelöscht).
 */
export class Mesh3dnetzspeichern {
    static MERKEN = 'mesh3d.netzergebnis';
    static FRAGE = 'Das Netz ohne die entfernten Flächen speichern, zur Quelle dieses Auftrags machen und von vorn neu rechnen?\n\nDie bisherigen Ergebnisse dieses Auftrags werden verworfen. Die alte Datei bleibt unverändert.';
    static FRAGE_ZURUECK = 'Den gespeicherten Schnitt zurücknehmen?\n\nDie Datei VOR dem Schnitt wird wieder die Quelle dieses Auftrags, die bisherigen Ergebnisse werden verworfen (danach „Neu berechnen“). Die bearbeitete Datei bleibt auf der Platte.';
    static FRAGE_WIEDER = 'Den zurückgenommenen gespeicherten Schnitt wiederholen?\n\nDie Datei NACH dem Schnitt (ohne die entfernten Flächen) wird wieder die Quelle dieses Auftrags, die bisherigen Ergebnisse werden verworfen (danach „Neu berechnen“).';

    /**
     * @param {object} seite die Jobseite (`kennung`, `lauf`, `zustand`, `aktualisieren`, `fehlerband`)
     * @param {HTMLElement} feld Zeile für das Ergebnis („Gespeichert: …“)
     * @param {Function} melden `(text)` — die Meldungszeile der Leiste
     * @param {Function} arbeiten `(ja, text)` — sperrt die Knöpfe, solange etwas geschrieben wird
     */
    constructor(seite, feld, melden, arbeiten) {
        this.seite = seite;
        this.feld = feld;
        this.melden = melden;
        this.arbeiten = arbeiten;
    }

    /** `wahl.schnitte` speichern; `uebernehmen`: zur Quelle machen und von vorn rechnen (mit Rückfrage). */
    async speichern(wahl, uebernehmen) {
        if (uebernehmen && !window.confirm(Mesh3dnetzspeichern.FRAGE)) return;
        this.arbeiten(true, uebernehmen ? 'Speichert und übernimmt …' : 'Speichert …');
        try {
            const a = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/netzschnitt/`, { schnitte: wahl.schnitte, uebernehmen });
            if (a.uebernommen) return await this._neuStarten(wahl, `${this._zusammenfassung(a)} Übernommen: die Datei ist jetzt die Quelle dieses Auftrags, die bisherigen Ergebnisse sind verworfen.`, uebernehmen);
            this._zeigen(a, wahl);
        } catch (fehler) {
            this.melden(`Speichern fehlgeschlagen: ${fehler.message}`);
            this.seite.fehlerband.meldung(`Netz speichern fehlgeschlagen: ${fehler.message}`);
        } finally {
            this.arbeiten(false);
        }
    }

    /** Eine gespeicherte Datei zur Quelle machen (Knopf „Als Quelle übernehmen“). */
    async uebernehmen(datei, wahl) {
        this.arbeiten(true, 'Übernimmt …');
        try {
            const a = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/netzuebernahme/`, { datei });
            if (!a.uebernommen) throw new Error(a.grund || 'nicht übernommen');
            await this._neuStarten(wahl, `Übernommen: ${datei} — die bisherigen Ergebnisse sind verworfen. Oben „Neu berechnen“ rechnet das neue Netz.`, false);
        } catch (fehler) {
            this.melden(`Übernehmen fehlgeschlagen: ${fehler.message}`);
        } finally {
            this.arbeiten(false);
        }
    }

    /** Den gespeicherten und übernommenen Schnitt zurücknehmen (Knopf „Gespeicherten Schnitt zurücknehmen“, `POST …/netzzurueck/`): die Datei vor dem Schnitt wird wieder die Quelle des Auftrags. */
    async zuruecknehmen(wahl) {
        if (!window.confirm(Mesh3dnetzspeichern.FRAGE_ZURUECK)) return;
        this.arbeiten(true, 'Nimmt den gespeicherten Schnitt zurück …');
        try {
            const a = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/netzzurueck/`, {});
            if (!a.uebernommen) throw new Error(a.grund || 'nicht zurückgenommen');
            await this._neuStarten(wahl, `Zurückgenommen: ${a.datei} ist wieder die Quelle dieses Auftrags — die bisherigen Ergebnisse sind verworfen. Oben „Neu berechnen“ rechnet das Netz davor.`, false);
        } catch (fehler) {
            this.melden(`Zurücknehmen fehlgeschlagen: ${fehler.message}`);
        } finally {
            this.arbeiten(false);
        }
    }

    /** Den zurückgenommenen gespeicherten Schnitt wiederholen (Knopf „Gespeicherten Schnitt wiederholen“, `POST …/netzwieder/`): die jüngste Datei, die aus der jetzigen Quelle entstand, wird wieder die Quelle. */
    async wiederholen(wahl) {
        if (!window.confirm(Mesh3dnetzspeichern.FRAGE_WIEDER)) return;
        this.arbeiten(true, 'Wiederholt den gespeicherten Schnitt …');
        try {
            const a = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/netzwieder/`, {});
            if (!a.uebernommen) throw new Error(a.grund || 'nicht wiederholt');
            await this._neuStarten(wahl, `Wiederholt: ${a.datei} ist wieder die Quelle dieses Auftrags — die bisherigen Ergebnisse sind verworfen. Oben „Neu berechnen“ rechnet das Netz ohne die entfernten Flächen.`, false);
        } catch (fehler) {
            this.melden(`Wiederholen fehlgeschlagen: ${fehler.message}`);
        } finally {
            this.arbeiten(false);
        }
    }

    /** Das Ergebnis des letzten Speicherns vor dem Neuladen der Seite, einmal (`netzGeladen` ruft es). */
    gemerktes() {
        try {
            const roh = window.sessionStorage.getItem(Mesh3dnetzspeichern.MERKEN);
            if (!roh) return;
            window.sessionStorage.removeItem(Mesh3dnetzspeichern.MERKEN);
            const gemerkt = JSON.parse(roh);
            if (gemerkt.kennung !== this.seite.kennung) return;
            this.feld.textContent = gemerkt.text;
            this.feld.hidden = false;
        } catch { /* ohne Speicher keine Meldung nach dem Neuladen — die Datei ist trotzdem gespeichert */ }
    }

    // ------------------------------------------------------------------ Innenleben

    _zahlen(a) {
        const z = Mesh3dnetzteileliste.zahl, p = Mesh3dnetzteileliste.prozent;
        return `${z(a.entfernt)} Flächen (${p(a.anteil)}) entfernt, ${z(a.flaechen_nachher)} bleiben, ${a.groesse_mb} MB.`;
    }

    _zusammenfassung(a) { return `Gespeichert: ${a.datei} — ${this._zahlen(a)}`; }

    /** Die Datei ist Quelle: Auswahl zurück, bei „… und rechnen“ den Lauf von vorn starten, Meldung merken, Seite neu laden. */
    async _neuStarten(wahl, text, rechnen) {
        wahl.zuruecksetzen();
        let angehaengt = text;
        if (rechnen) {
            await this.seite.lauf.neu(null);
            if (this.seite.zustand?.status !== 'laeuft') angehaengt += ' Der Lauf ließ sich nicht starten — oben „Neu berechnen“.';
        }
        try {
            window.sessionStorage.setItem(Mesh3dnetzspeichern.MERKEN, JSON.stringify({ kennung: this.seite.kennung, text: angehaengt }));
        } catch { /* siehe `gemerktes` */ }
        this.melden('Die Seite lädt neu …');
        window.setTimeout(() => window.location.reload(), 300);
    }

    /** Gespeichert, aber (noch) nicht Quelle: Pfad, Zahlen und der Knopf „Als Quelle übernehmen“. */
    _zeigen(a, wahl) {
        const pfad = document.createElement('code');
        pfad.textContent = a.datei;
        const zeile = ['Gespeichert: ', pfad, ` — ${this._zahlen(a)} `];
        if (a.grund) zeile.push(`Nicht übernommen: ${a.grund}. `);
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-secondary btn-sm';
        knopf.textContent = 'Als Quelle übernehmen';
        knopf.title = 'Diese Datei zur Quelle des Auftrags machen — die bisherigen Ergebnisse werden verworfen, gerechnet wird erst mit „Neu berechnen“';
        knopf.addEventListener('click', () => this.uebernehmen(a.datei, wahl));
        zeile.push(knopf);
        this.feld.replaceChildren(...zeile);
        this.feld.hidden = false;
    }
}
