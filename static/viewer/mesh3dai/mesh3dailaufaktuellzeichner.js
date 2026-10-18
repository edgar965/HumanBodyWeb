/**
 * Mesh3dailaufaktuellzeichner — baut die Karten des Reiters „Lauf Aktuell“ auf /mesh-3D-AI/ aus dem Stand von `GET /api/mesh3dai/lauf-aktuell/` (18.10.2026).
 * Rechner gesamt (djangoBase `SystemStats`), laufende Jobs mit CPU, Arbeitsspeicher, GPU und Fortschritt, andere Programme auf der GPU; die Warteschlange (Ketten und ihre Schritte)
 * zeichnet `Mesh3daiwarteschlangezeichner` mit den Bausteinen dieser Klasse, die Reihenfolge der Karten legt `Mesh3dailaufaktuell.holen` fest.
 * Alles über `textContent` — Befehlszeilen und Namen kommen von der Platte, nie als HTML.
 */
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
        const sperre = stand.sperre;
        const belegt = sperre ? `Grafikkarte reserviert für einen Mesh3D-AI-Lauf${sperre.seit ? ` seit ${this.uhr(sperre.seit)} Uhr (${this.spanne(jetzt - sperre.seit)})` : ''}`
            : 'Grafikkarte frei für den nächsten Mesh3D-AI-Lauf';
        const zeile = this.el('p', '', belegt);
        if (sperre) zeile.title = `Sperre gehalten von „${sperre.name}“`;
        karte.append(zeile);
        karte.append(this.el('p', 'hb-hinweis', 'Auslastung des ganzen Rechners. Die Läufe von Mesh3D-AI nutzen die Grafikkarte nacheinander; Browser und andere Programme laufen daneben.'));
        return karte;
    }

    static jobs(stand, jetzt) {
        const jobs = stand.jobs || [];
        const ohne = stand.laeufe_ohne_prozess || [];
        const karte = this.karte(`Laufende Jobs (${jobs.length})`);
        if (!jobs.length && !ohne.length) karte.append(this.el('p', '', 'Gerade rechnet kein Mesh3D-AI-Lauf.'));
        for (const job of jobs) karte.append(this.job(job, stand, jetzt));
        for (const lauf of ohne) {
            const block = this.el('article', 'mesh3dai-la-job');
            block.append(this.el('h3', '', 'Ein Training schreibt noch, aber kein Programm dazu läuft'));
            block.append(this.el('p', 'hb-hinweis', `Das Training ${lauf.kurz} hat sich in der letzten Stunde gemeldet, das Programm dazu ist nicht mehr zu sehen — vermutlich abgebrochen.`));
            block.append(this.fortschritt(lauf.fortschritt), this.link(lauf.adresse, 'Zwischenstand ansehen'));
            karte.append(block);
        }
        karte.append(this.el('p', 'hb-hinweis', 'CPU, Arbeitsspeicher und Grafikkarte: was dieser Lauf gerade belegt (wie im Task-Manager).'));
        return karte;
    }

    static job(job, stand, jetzt) {
        const block = this.el('article', 'mesh3dai-la-job');
        // Edgar, 18.10.2026: „Lass deine blöden Technik infos weg … und sage verständlich was da läuft“ — Titel und ein Satz; Skript, Befehl und PID nur im Tooltip des Titels.
        const kopf = this.el('h3');
        kopf.append(this.el('span', 'mesh3dai-la-art', job.art), document.createTextNode(` ${job.titel}`));
        kopf.title = `${[job.skript, ...(job.argumente || [])].join(' ')}\nPID ${job.pid} · ${job.umgebung} · ${job.prozesse} Prozesse`;
        block.append(kopf);
        if (job.was) block.append(this.el('p', 'mesh3dai-la-was', job.was));
        block.append(this.el('p', 'hb-hinweis', `läuft seit ${this.uhr(job.start)} Uhr (${this.spanne(jetzt - job.start)})`));
        const kerne = stand.kerne || stand.system?.kerne || 1;
        const gesamt = stand.system?.gpu?.mem_total;
        const arten = Object.entries(job.gpu_arten || {}).map(([a, w]) => `${a} ${this.zahl(w)} %`).join(' · ');
        const werte = this.el('div', 'mesh3dai-la-werte');
        werte.append(this.wert('CPU', job.cpu_kerne / kerne, `${this.zahl(job.cpu_kerne)} Kerne (${this.zahl(100 * job.cpu_kerne / kerne)} % des Rechners)`));
        werte.append(this.wert('Arbeitsspeicher', null, `${this.gb(job.ram_mb)} GB`));
        werte.append(this.wert('GPU', job.gpu_prozent / 100, `${this.zahl(job.gpu_prozent)} %`, arten || 'keine Engine aktiv'));
        werte.append(this.wert('GPU-Speicher', gesamt ? job.gpu_mb / gesamt : null, `${this.gb(job.gpu_mb)} GB`, `Prozesse mit GPU-Speicher: ${(job.gpu_pids || []).join(', ') || '—'}`));
        block.append(werte);
        if (job.fortschritt?.length) block.append(this.fortschritt(job.fortschritt));
        else block.append(this.el('p', 'hb-hinweis', 'Wie weit dieser Lauf ist, lässt sich nicht messen.'));
        if (job.lauf) block.append(this.link(job.lauf.adresse, 'Zwischenstand dieses Trainings ansehen'));
        return block;
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

    static fremde(stand) {
        const fremde = stand.fremde_gpu || [];
        if (!fremde.length) return null;
        const karte = this.karte('Weitere Programme auf der GPU');
        const liste = this.el('ul', 'mesh3dai-la-liste');
        for (const f of fremde) liste.append(this.el('li', '', `${f.name} (PID ${f.pid}) · ${this.gb(f.gpu_mb)} GB · ${this.zahl(f.gpu_prozent)} %`));
        karte.append(liste, this.el('p', 'hb-hinweis', 'Programme außerhalb von Mesh3D-AI mit mehr als 200 MB GPU-Speicher oder 1 % Auslastung — sie teilen sich die Karte mit den Läufen.'));
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
