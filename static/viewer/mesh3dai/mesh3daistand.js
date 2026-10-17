/**
 * Mesh3daistand — die Statuskarte „Datensatz und Training" auf der Jobseite von Mesh3D-AI (14.10.2026).
 *
 * Edgar: „aktualisierst du alle paar Minuten den Trainingsstand auf der Ursula Seite?" → „mach das, alle paar Minuten, damit es die Trainings nicht beeinträchtigt" und „einstellbar, wie viele Minuten".
 * Holt `GET /api/mesh3dai/<job>/stand/` (`Mesh3daistand` im Server: fertige Proben des Datensatzes und der jüngste Trainingslauf, nur Dateien) im Takt `intervall_minuten` aus der Antwort
 * (Einstellungen → Mesh3D-AI; eine geänderte Einstellung gilt ab der nächsten Abfrage). Ein verdeckter Tab fragt nicht, er holt es beim Zurückkehren nach. „Jetzt" fragt sofort.
 * Anders als der Rest der Seite sind die Zahlen hier ECHT (von der Platte), nicht Attrappe.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Mesh3daistand {
    static VORGABE_MINUTEN = 5;
    static GRUPPEN = { training: 'Training', pruefung: 'Prüfposen (nie trainiert)', spagat: 'Spagat-Bilder (nie trainiert)' };
    static STATUS = { fertig: 'fertig', laeuft: 'läuft', ohne_ergebnis: 'ohne Ergebnis — abgebrochen oder Probelauf' };

    static aufbauen(jobId, wurzel) {
        const karte = new Mesh3daistand(jobId, wurzel);
        karte.starten();
        return karte;
    }

    constructor(jobId, wurzel) {
        this.jobId = jobId;
        this.inhalt = wurzel.querySelector('[data-stand="inhalt"]');
        this.zeit = wurzel.querySelector('[data-stand="zeit"]');
        this.jetzt = wurzel.querySelector('[data-stand="jetzt"]');
        this.minuten = Mesh3daistand.VORGABE_MINUTEN;
        this.timer = null;
        this.faellig = false;
    }

    starten() {
        this.jetzt.addEventListener('click', () => this.abfragen());
        document.addEventListener('visibilitychange', () => { if (!document.hidden && this.faellig) this.abfragen(); });
        this.abfragen();
    }

    async abfragen() {
        clearTimeout(this.timer);
        this.faellig = false;
        this.jetzt.disabled = true;
        try {
            const daten = await Serverabruf.json(`/api/mesh3dai/${encodeURIComponent(this.jobId)}/stand/`);
            this.minuten = daten.intervall_minuten || Mesh3daistand.VORGABE_MINUTEN;
            this.zeigen(daten);
        } catch (fehler) {
            this.inhalt.replaceChildren(this._el('p', `Stand nicht lesbar: ${fehler.message ?? fehler}`, 'fehlertext'));
        } finally {
            this.jetzt.disabled = false;
            this.timer = setTimeout(() => this.takt(), this.minuten * 60000);
        }
    }

    takt() {
        if (document.hidden) {
            this.faellig = true;   // nicht fragen, solange niemand hinsieht; beim Zurückkehren nachholen
            return;
        }
        this.abfragen();
    }

    zeigen(daten) {
        this.zeit.textContent = `Stand ${daten.zeit.slice(11)} · Abfrage alle ${this.minuten} min`;
        const d = daten.datensatz;
        const teile = [this._datensatz(d), this._lauf(daten.lauf)];
        if (daten.lauf && Object.keys(daten.lauf.masse).length) teile.push(this._masse(daten.lauf));
        if (daten.lauf && daten.lauf.zeilen.length) teile.push(this._log(daten.lauf.zeilen));
        this.inhalt.replaceChildren(...teile);
    }

    _datensatz(d) {
        const zeile = this._el('div', '', 'mesh3dai-standzeile');
        const text = d.geplant ? `Datensatz: ${d.vorhanden} von ${d.geplant} Proben gerechnet` : `Datensatz: ${d.vorhanden} Proben gerechnet`;
        zeile.append(this._el('span', text));
        if (d.geplant) {
            const balken = document.createElement('progress');
            balken.max = d.geplant;
            balken.value = d.vorhanden;
            balken.className = 'mesh3dai-standbalken';
            zeile.append(balken);
        }
        zeile.title = 'Fertig heißt: eingabe.npz der Probe liegt unter 3DObjects/mesh3dai/<Modell>/proben/ (das Datenskript schreibt sie zuletzt). Geplant: Einträge in proben.json.';
        return zeile;
    }

    _lauf(lauf) {
        const zeile = this._el('div', '', 'mesh3dai-standzeile');
        if (!lauf) {
            zeile.append(this._el('span', 'Training: noch kein Lauf'));
            return zeile;
        }
        const teile = [`Training ${lauf.name}: ${Mesh3daistand.STATUS[lauf.status] ?? lauf.status}`];
        if (lauf.epoche && lauf.epochen) teile.push(`Epoche ${lauf.epoche} von ${lauf.epochen}`);
        const v = lauf.verlauf;
        if (v.training_mm !== undefined) teile.push(`Verlust der Epoche ${this._mm(v.training_mm)}`);
        if (v.pruefung_mm !== undefined) teile.push(`Prüfposen ${this._mm(v.pruefung_mm)}`);
        if (v.spagat_mm !== undefined) teile.push(`Spagat-Bilder ${this._mm(v.spagat_mm)}`);
        if (lauf.dauer_s) teile.push(`${lauf.dauer_s} s gerechnet`);
        if (lauf.vor_s !== null) teile.push(`Log zuletzt vor ${this._dauer(lauf.vor_s)}`);
        zeile.append(this._el('span', teile.join(' · ')));
        zeile.title = 'Verlust der Epoche: mittlerer Abstand der Rig-Punkte zum Soll im Training (mm). Prüfposen und Spagat-Bilder misst das Skript nur alle 10 Epochen; ' +
            '„läuft“ ist aus der Zeit der Logdatei geschlossen (zehn Minuten), kein Prozess wurde geprüft.';
        return zeile;
    }

    _masse(lauf) {
        const tabelle = document.createElement('table');
        tabelle.className = 'mesh3dai-standtabelle';
        const kopf = ['Gruppe', 'Proben', 'Netz Ø mm', 'Median mm', 'p95 mm', 'mittlere Pose mm', 'A-Pose mm', 'unter 10 mm %'];
        tabelle.createTHead().insertRow().append(...kopf.map(t => this._el('th', t)));
        const koerper = tabelle.createTBody();
        for (const [gruppe, m] of Object.entries(lauf.masse)) {
            const werte = [Mesh3daistand.GRUPPEN[gruppe] ?? gruppe, lauf.proben?.[gruppe] ?? '', m.netz_mm, m.netz_median_mm, m.netz_p95_mm, m.mittlere_pose_mm ?? '—', m.a_pose_mm ?? '—', m.unter_10mm_prozent];
            koerper.insertRow().append(...werte.map((w, i) => this._el('td', String(w), i ? 'num' : '')));
        }
        tabelle.title = 'Abstand der 138 Rig-Punkte zum Soll, gemittelt über Proben und Punkte. „mittlere Pose“: immer die mittlere Soll-Pose des Trainings vorhersagen; „A-Pose“: immer die Ruhelage. Das Netz muss unter beiden liegen.';
        return tabelle;
    }

    _log(zeilen) {
        const huelle = document.createElement('details');
        huelle.append(this._el('summary', 'Letzte Zeilen des Logs'), this._el('pre', zeilen.join('\n')));
        return huelle;
    }

    _mm(wert) {
        return `${Number(wert).toLocaleString('de-DE', { maximumFractionDigits: 1 })} mm`;
    }

    _dauer(sekunden) {
        if (sekunden < 90) return `${sekunden} s`;
        if (sekunden < 5400) return `${Math.round(sekunden / 60)} min`;
        return `${(sekunden / 3600).toLocaleString('de-DE', { maximumFractionDigits: 1 })} h`;
    }

    _el(tag, text, klasse = '') {
        const el = document.createElement(tag);
        el.textContent = text;
        if (klasse) el.className = klasse;
        return el;
    }
}
