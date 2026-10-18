import { Mesh3dailaufaktuellzeichner as Z } from './mesh3dailaufaktuellzeichner.js';

/**
 * Mesh3daiwarteschlangezeichner — die Karte „Warteschlange“ im Reiter „Lauf Aktuell“ auf /mesh-3D-AI/ (18.10.2026; ersetzt „Ketten im Hintergrund“).
 * Edgar: „soll die aktuelle Job queue enthalten, mit der Jobliste, und Spalte mit Fortschrittsbalken bei aktuellem Job“ → „statt Jobliste: Warteschlange“.
 * Je Kette eine Kopfzeile (Zustand, worauf sie wartet, PID), darunter ihre Schritte mit Nummer, Zustand, Beginn, Dauer; der laufende Schritt trägt den Balken.
 * Daten: `stand.warteschlange` (`Mesh3daiwarteschlange`). Alles über `textContent`.
 */
export class Mesh3daiwarteschlangezeichner {
    static ZUSTAND = {
        'fertig': '✓ fertig', 'läuft': '▶ läuft', 'wartet': 'wartet', 'übersprungen': 'übersprungen', 'abgebrochen': 'abgebrochen', 'nicht gestartet': 'nicht gestartet',
    };

    static karte(stand, jetzt) {
        const w = stand.warteschlange;
        if (!w) return null;
        const schritte = (w.ketten || []).flatMap((k) => k.schritte);
        const offen = schritte.filter((s) => s.zustand === 'wartet').length;
        const karte = Z.karte(`Warteschlange (${schritte.length} Schritte, ${offen} offen)`);
        if (w.fehler) karte.append(Z.el('p', 'mesh3dai-la-fehler', `${w.fehler} (${w.datei})`));
        const laeuft = schritte.filter((s) => s.zustand === 'läuft');
        karte.append(Z.el('p', '', laeuft.length ? `Gerade: ${laeuft.map((s) => `Schritt ${s.nr} · ${s.titel}`).join(' · ')}` : 'Gerade läuft kein Schritt einer Kette.'));
        if (schritte.length) karte.append(this.tabelle(w, jetzt));
        if (w.unbeschrieben?.length) karte.append(this.unbeschrieben(w.unbeschrieben, jetzt));
        const hinweis = Z.el('p', 'hb-hinweis', 'Die Schritte laufen von selbst nacheinander: jeder Block wartet, bis der vorige fertig ist. Wo sich der Fortschritt nicht messen lässt, läuft der Balken durch.');
        hinweis.title = `Beschreibung der Ketten: ${w.datei}`;
        karte.append(hinweis);
        return karte;
    }

    static tabelle(w, jetzt) {
        const rahmen = Z.el('div', 'mesh3dai-ws-rahmen');
        const tabelle = Z.el('table', 'doku mesh3dai-ws-tabelle');
        const kopf = Z.el('tr');
        for (const t of ['Nr', 'Schritt', 'Zustand', 'Beginn', 'Dauer', 'Fortschritt']) kopf.append(Z.el('th', '', t));
        const thead = Z.el('thead');
        thead.append(kopf);
        const tbody = Z.el('tbody');
        for (const k of w.ketten) {
            tbody.append(this.kettenzeile(k, jetzt));
            for (const s of k.schritte) tbody.append(this.schrittzeile(s, jetzt));
        }
        tabelle.append(thead, tbody);
        rahmen.append(tabelle);
        return rahmen;
    }

    static kettenzeile(k, jetzt) {
        const tr = Z.el('tr', 'mesh3dai-ws-kette');
        const td = Z.el('td');
        td.colSpan = 6;
        td.title = `${k.skript} · Log ${k.log}${k.prozesse?.length ? ` · PID ${k.prozesse.map((p) => p.pid).join(', ')}` : ''}`;
        td.append(Z.el('strong', '', k.titel), document.createTextNode(' '), this.marke(k.zustand), document.createTextNode(` ${this.kettentext(k, jetzt)}`));
        if (k.doppelt) td.append(Z.el('strong', 'mesh3dai-la-doppelt', ' · läuft doppelt — rechnet dieselben Schritte zweimal'));
        tr.append(td);
        return tr;
    }

    static kettentext(k, jetzt) {
        // Läuft: seit dem ersten begonnenen Schritt — der Prozess der Kette lebt schon, während sie wartet (Formkette: Prozess 19:04, erster Schritt 22:35).
        const beginn = k.schritte.find((s) => s.start)?.start;
        const seit = beginn ? `seit ${Z.uhr(beginn)} Uhr` : '';
        if (k.zustand === 'fertig') return k.ende ? `um ${Z.uhr(k.ende)} Uhr` : '';
        if (k.zustand === 'abgebrochen') return '— ist stehen geblieben, bevor alle Schritte fertig waren';
        if (k.zustand === 'nicht gestartet') return '— ist nicht eingeplant';
        if (k.zustand === 'wartet' && k.wartet_auf) {
            return k.wartet_auf.erreicht ? '— beginnt gleich' : `bis „${k.wartet_auf.titel}“ fertig ist`;
        }
        return seit;
    }

    static schrittzeile(s, jetzt) {
        const tr = Z.el('tr', `mesh3dai-ws-schritt mesh3dai-ws-${this.klasse(s.zustand)}`);
        tr.append(Z.el('td', 'num', String(s.nr)), Z.el('td', '', s.titel));
        const zustand = Z.el('td');
        zustand.append(this.marke(s.zustand));
        tr.append(zustand, Z.el('td', 'num', s.start ? Z.uhr(s.start) : ''));
        let dauer = '';
        if (s.dauer_s != null) dauer = Z.spanne(s.dauer_s);
        else if (s.zustand === 'läuft' && s.seit_s != null) dauer = `seit ${Z.spanne(s.seit_s)}`;
        tr.append(Z.el('td', 'num', dauer));
        const zelle = Z.el('td', 'mesh3dai-ws-fortschritt');
        if (s.zustand === 'läuft') this.fortschritt(zelle, s);
        tr.append(zelle);
        return tr;
    }

    /** Balken (oder laufender Balken), Text, Abschnitt und letzte Zeile des Logs, Link zum Lauf. */
    static fortschritt(zelle, s) {
        const f = s.fortschritt;
        const anteil = f?.gesamt ? f.fertig / f.gesamt : null;
        const balken = Z.el('div', 'mesh3dai-la-balken');
        if (anteil != null && Number.isFinite(anteil)) {
            const fuellung = Z.el('div', 'mesh3dai-la-fuellung mesh3dai-la-fortschrittsfuellung');
            fuellung.style.width = `${Math.max(0, Math.min(100, 100 * anteil))}%`;
            balken.append(fuellung);
        } else {
            balken.classList.add('mesh3dai-la-unbestimmt');
        }
        zelle.append(balken);
        const rest = f?.rest_s != null ? ` · noch etwa ${Z.spanne(f.rest_s)}` : '';
        const text = f ? `${f.text}${anteil != null ? ` · ${Z.zahl(100 * anteil)} %` : ''}${rest}` : 'läuft — wie weit, lässt sich nicht messen';
        const zeile = Z.el('div', 'mesh3dai-ws-text', text);
        // Abschnitt und letzte Logzeile nur im Tooltip (Edgar: „Lass deine blöden Technik infos weg“).
        zeile.title = [f?.hinweis, s.abschnitt && `Abschnitt: ${s.abschnitt}`, s.letzte_zeile && `Log zuletzt: ${s.letzte_zeile}`].filter(Boolean).join('\n');
        zelle.append(zeile);
        if (s.lauf) zelle.append(Z.link(s.lauf.adresse, 'Zwischenstand ansehen'));
    }

    static unbeschrieben(liste, jetzt) {
        const block = Z.el('div');
        block.append(Z.el('p', '', 'Außerdem laufen diese Abläufe, deren Schritte hier nicht beschrieben sind:'));
        const ul = Z.el('ul', 'mesh3dai-la-liste');
        for (const k of liste) {
            const li = Z.el('li', '', `${k.name} · seit ${Z.uhr(k.start)} Uhr (${Z.spanne(jetzt - k.start)})`);
            li.title = `PID ${k.pid}`;
            if (k.doppelt) li.append(Z.el('strong', 'mesh3dai-la-doppelt', ' · läuft doppelt'));
            ul.append(li);
        }
        block.append(ul);
        return block;
    }

    static marke(zustand) {
        const span = Z.el('span', 'mesh3dai-ws-zustand', this.ZUSTAND[zustand] || zustand);
        span.dataset.zustand = this.klasse(zustand);
        return span;
    }

    static klasse(zustand) {
        return { 'läuft': 'laeuft', 'übersprungen': 'uebersprungen', 'nicht gestartet': 'nichtgestartet' }[zustand] || zustand;
    }
}
