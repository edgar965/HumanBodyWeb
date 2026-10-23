/**
 * Mesh3dailaufaktuellzeichner — baut die Karten des Reiters „Lauf Aktuell“ auf /mesh-3D-AI/ aus dem Stand von `GET /api/mesh3dai/lauf-aktuell/` (18.10.2026).
 * Rechner gesamt (djangoBase `SystemStats`), laufende Jobs mit CPU, Arbeitsspeicher, GPU und Fortschritt, andere Programme auf der GPU; die Warteschlange (Ketten und ihre Schritte)
 * zeichnet `Mesh3daiwarteschlangezeichner` mit den Bausteinen dieser Klasse, die Reihenfolge der Karten legt `Mesh3dailaufaktuell.holen` fest.
 * Alles über `textContent` — Befehlszeilen und Namen kommen von der Platte, nie als HTML.
 */
import { Mesh3dailaufaktuellfremde } from './mesh3dailaufaktuellfremde.js';

export class Mesh3dailaufaktuellzeichner {
    static WARN = 75;
    static GEFAHR = 90;

    static rechner(stand, jetzt) {
        const s = stand.system || {};
        const gpu = s.gpu;
        const karte = this.karte('Rechner');
        const werte = this.el('div', 'mesh3dai-la-werte');
        if (gpu) {
            werte.append(this.wert('GPU', gpu.util / 100, `${this.zahl(gpu.util)} %`, `${gpu.name} · ${gpu.temp} °C · Mittel der letzten 5 Messungen (Momentwert ${gpu.util_roh} %)`));
            werte.append(this.wert('GPU-Speicher', gpu.mem_used / gpu.mem_total, `${this.gb(gpu.mem_used)} von ${this.gb(gpu.mem_total)} GB`));
        } else {
            werte.append(this.el('p', 'hb-hinweis', 'Keine GPU-Werte (nvidia-smi antwortet nicht).'));
        }
        if (s.cpu_percent != null) werte.append(this.wert('CPU', s.cpu_percent / 100, `${this.zahl(s.cpu_percent)} % von ${s.kerne} Kernen`));
        if (s.ram_percent != null) werte.append(this.wert('Arbeitsspeicher', s.ram_percent / 100, `${this.zahl(s.ram_percent)} %`));
        karte.append(werte);
        // Zwei Plätze der GPU-Sperre (seit 20.10.2026): je Platz belegt seit … oder frei; der Name der Sperre nur im Tooltip.
        const plaetze = stand.plaetze || [];
        const zeile = this.el('p', '', `Grafikkarte: ${plaetze.map((p) => (p.name ? `Platz ${p.platz} belegt${p.seit ? ` seit ${this.uhr(p.seit)} Uhr (${this.spanne(jetzt - p.seit)})` : ''}` : `Platz ${p.platz} frei`)).join(' · ') || '—'}`);
        zeile.title = plaetze.filter((p) => p.name).map((p) => `Platz ${p.platz}: Sperre „${p.name}“`).join('\n');
        karte.append(zeile);
        return karte;
    }

    /** Laufende Jobs als Tabelle — Job · Schritt · Ablauf · seit · CPU · GPU · Fortschritt (20.10.2026, Edgar: „Mach eine klare Liste der Jobs, ohne gaga Texte, … welcher Job, welcher Schritt“). */
    static jobs(stand, jetzt) {
        const jobs = stand.jobs || [];
        const ohne = stand.laeufe_ohne_prozess || [];
        const karte = this.karte(`Laufende Jobs (${jobs.length})`);
        if (!jobs.length) karte.append(this.el('p', '', 'Gerade rechnet kein Mesh3D-AI-Lauf.'));
        else karte.append(this.jobtabelle(jobs, stand, jetzt));
        for (const lauf of ohne) {
            const p = this.el('p', 'mesh3dai-la-fehler', `Training ${lauf.kurz}: schreibt noch, aber kein Programm dazu läuft — vermutlich abgebrochen. `);
            p.append(this.link(lauf.adresse, 'Zwischenstand'));
            karte.append(p);
        }
        return karte;
    }

    static jobtabelle(jobs, stand, jetzt) {
        const rahmen = this.el('div', 'mesh3dai-ws-rahmen');
        const tabelle = this.el('table', 'doku mesh3dai-ws-tabelle mesh3dai-la-jobs');
        const kopf = this.el('tr');
        for (const t of ['Job', 'Schritt', 'Ablauf', 'Seit', 'CPU', 'GPU', 'Fortschritt']) kopf.append(this.el('th', '', t));
        const thead = this.el('thead');
        thead.append(kopf);
        const tbody = this.el('tbody');
        for (const job of jobs) tbody.append(this.jobzeile(job, stand, jetzt));
        tabelle.append(thead, tbody);
        rahmen.append(tabelle);
        return rahmen;
    }

    static jobzeile(job, stand, jetzt) {
        const tr = this.el('tr', job.wartet_gpu ? 'mesh3dai-la-wartet' : 'mesh3dai-ws-laeuft');
        const jobzelle = this.el('td');
        if (job.job_adresse) {
            const a = this.el('a', '', job.job_text);
            a.href = job.job_adresse;
            jobzelle.append(a);
        } else {
            jobzelle.textContent = job.job_text;
        }
        if (job.job_titel) jobzelle.title = job.job_titel;
        // Skript, Befehl und PID nur im Tooltip (Edgar, 18.10.2026: „Lass deine blöden Technik infos weg“).
        const schritt = this.el('td', '', job.titel);
        schritt.title = `${job.art} · ${[job.skript, ...(job.argumente || [])].join(' ')}\nPID ${job.pid} · ${job.umgebung} · ${job.prozesse} Prozesse`;
        const a = job.ablauf;
        const ablauf = this.el('td', '', a ? `${a.titel}${a.schritt ? ` · Schritt ${a.schritt} von ${a.von}` : ''}` : 'einzeln gestartet');
        if (a) ablauf.title = a.schritt_titel;
        const kerne = stand.kerne || stand.system?.kerne || 1;
        const cpu = this.el('td', 'num', `${this.zahl(job.cpu_kerne)} Kerne · ${this.gb(job.ram_mb)} GB`);
        cpu.title = `${this.zahl(100 * job.cpu_kerne / kerne)} % des Rechners · Arbeitsspeicher ${this.gb(job.ram_mb)} GB`;
        const gpu = this.el('td', 'num', job.wartet_gpu ? 'wartet auf die Grafikkarte' : `${this.zahl(job.gpu_prozent)} % · ${this.gb(job.gpu_mb)} GB`);
        gpu.title = Object.entries(job.gpu_arten || {}).map(([art, w]) => `${art} ${this.zahl(w)} %`).join(' · ') || 'keine Engine aktiv';
        const fortschritt = this.el('td', 'mesh3dai-ws-fortschritt');
        if (job.fortschritt?.length) fortschritt.append(this.fortschritt(job.fortschritt));
        else fortschritt.textContent = '—';
        if (job.lauf) fortschritt.append(this.link(job.lauf.adresse, 'Zwischenstand'));
        tr.append(jobzelle, schritt, ablauf, this.el('td', 'num', `${this.uhr(job.start)} · ${this.spanne(jetzt - job.start)}`), cpu, gpu, fortschritt);
        return tr;
    }

    static fortschritt(liste) {
        const rahmen = this.el('div', 'mesh3dai-la-fortschritt');
        for (const f of liste) {
            const anteil = f.gesamt ? f.fertig / f.gesamt : null;
            const rest = f.rest_s != null ? ` · noch etwa ${this.spanne(f.rest_s)}` : '';
            const zeile = this.wert(f.name, anteil, `${f.text}${anteil != null ? ` · ${this.zahl(100 * anteil)} %` : ''}${rest}`, f.hinweis, true);
            rahmen.append(zeile);
        }
        return rahmen;
    }

    /** Ruhig gehalten (`Mesh3dailaufaktuellfremde`): Programme bleiben eine Minute stehen, feste Reihenfolge, Karte immer da. */
    static fremde(stand) {
        const eintraege = Mesh3dailaufaktuellfremde.liste(stand.fremde_gpu, stand.zeit);
        const karte = this.karte('Weitere Programme auf der GPU');
        if (!eintraege.length) karte.append(this.el('p', '', 'Gerade keine.'));
        const liste = this.el('ul', 'mesh3dai-la-liste');
        for (const f of eintraege) {
            const li = this.el('li', f.aktiv ? '' : 'mesh3dai-la-ruhend',
                `${f.name} (PID ${f.pid}) · ${f.aktiv ? `${this.gb(f.gpu_mb)} GB · ${this.zahl(f.gpu_prozent)} %` : 'unter der Schwelle'}`);
            if (!f.aktiv) li.title = `Zuletzt ${this.uhr(f.zuletzt, true)} Uhr: ${this.gb(f.gpu_mb)} GB · ${this.zahl(f.gpu_prozent)} % — bleibt eine Minute stehen, damit die Liste nicht springt.`;
            liste.append(li);
        }
        karte.append(liste, this.el('p', 'hb-hinweis', 'Programme außerhalb von Mesh3D-AI mit mehr als 200 MB GPU-Speicher oder 1 % Auslastung — sie teilen sich die Karte mit den Läufen. Wer darunter fällt, bleibt eine Minute blass stehen.'));
        return karte;
    }

    static fuss(stand) {
        return this.el('p', 'hb-hinweis mesh3dai-la-fuss', `Stand ${this.uhr(stand.zeit, true)} · alle ${stand.takt_s} s, nur solange dieser Reiter offen ist.`);
    }

    // ---- Bausteine
    static karte(titel) {
        const karte = this.el('div', 'card mesh3dai-joblist mesh3dai-la-karte');
        karte.append(this.el('h2', '', titel));
        return karte;
    }

    /** Name, Balken (Anteil 0–1, ohne Anteil kein Balken bzw. bei `fortschritt` ein laufender) und Text. */
    static wert(name, anteil, text, titel = '', fortschritt = false) {
        const zeile = this.el('div', 'mesh3dai-la-wert');
        if (titel) zeile.title = titel;
        zeile.append(this.el('span', 'mesh3dai-la-name', name));
        const balken = this.el('div', 'mesh3dai-la-balken');
        if (anteil != null && Number.isFinite(anteil)) {
            const fuellung = this.el('div', 'mesh3dai-la-fuellung');
            const prozent = Math.max(0, Math.min(100, 100 * anteil));
            fuellung.style.width = `${prozent}%`;
            if (fortschritt) fuellung.classList.add('mesh3dai-la-fortschrittsfuellung');
            else if (prozent >= this.GEFAHR) fuellung.classList.add('mesh3dai-la-gefahr');
            else if (prozent >= this.WARN) fuellung.classList.add('mesh3dai-la-warn');
            balken.append(fuellung);
        } else if (fortschritt) {
            balken.classList.add('mesh3dai-la-unbestimmt');
        } else {
            balken.classList.add('mesh3dai-la-leer');
        }
        zeile.append(balken, this.el('span', 'mesh3dai-la-text', text));
        return zeile;
    }

    static link(adresse, text) {
        const a = this.el('a', 'btn btn-secondary btn-sm mesh3dai-la-link', text);
        a.href = adresse;
        return a;
    }

    static el(tag, klasse = '', text = '') {
        const e = document.createElement(tag);
        if (klasse) e.className = klasse;
        if (text) e.textContent = text;
        return e;
    }

    static zahl(w, stellen = 1) {
        return Number(w || 0).toLocaleString('de-DE', { maximumFractionDigits: stellen });
    }

    static gb(mb) {
        return (Number(mb || 0) / 1000).toLocaleString('de-DE', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    }

    static uhr(sekunden, mitSekunden = false) {
        return new Date(sekunden * 1000).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', ...(mitSekunden ? { second: '2-digit' } : {}) });
    }

    static spanne(sekunden) {
        const minuten = Math.round(Math.max(0, sekunden) / 60);
        if (minuten < 1) return 'unter 1 min';
        return minuten >= 60 ? `${Math.floor(minuten / 60)} h ${minuten % 60} min` : `${minuten} min`;
    }
}
