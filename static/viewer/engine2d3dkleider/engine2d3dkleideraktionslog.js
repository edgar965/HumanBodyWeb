/**
 * Engine2d3dKleiderAktionslog — was im Browser auf der Seite „2D3D Kleider" geschieht, ins Serverprotokoll (04.10.2026).
 *
 * Edgar: „mach server logs wenn ich einen Tab wechsele, sowie bei allen Aktionen im UI" — nachdem die Reiter „nicht anklickbar" waren und die Seite „hing", das
 * Serverprotokoll aber nur Serveraufrufe kannte (`server_call`) und nichts darüber, was im Browser vorging. Geschrieben wird über `POST /api/log/` →
 * `logs/client.log`, Seite `engine2d3dkleider`; jede Zeile trägt eine Kennung des Tabs (`[a1b2]`), weil mehrere Tabs derselben Seite offen sein können.
 *
 * Standalone (kein `Serverabruf`, kein `fn.serverLog`): Das Modul hängt an nichts, was die Seite laden muss — es soll auch dann schreiben, wenn die Seitenklasse
 * mit ihren dreißig Modulen nicht hochkommt. Gelogt wird:
 *
 *   klick / rechtsklick / aenderung   jede Bedienung eines Knopfes, Links, Reiters, Auswahlfelds; `verzoegert` ist die Zeit zwischen dem Klick und dem Moment, in dem
 *                                      der Hauptfaden ihn bearbeitet (`performance.now() - Ereignis.timeStamp`) — hängt die Seite, steht hier die Zahl
 *   reiter_klick / reiter_wechsel      der Klick auf einen Reiter, dann der Wechsel, den `Seitenreiter` meldet, mit dem Zustand von Knöpfen und Feldern
 *   reiter_druck / reiter_daneben      jeder Druck im Rechteck der Leiste samt Ziel (liegt etwas darüber, steht „NEBEN den Reitern"); ein Klick, der an die Leiste
 *                                      statt an einen Reiter ging (Druck und Loslassen auf verschiedenen Elementen)
 *   reiter_ergebnis                    300 ms nach dem Klick: Welches Feld ist sichtbar? Passt es nicht zum Reiter, steht eine Warnung
 *   reiter_fertig / seite_bereit       die Seite meldet ein Feld bzw. sich selbst fertig, mit der Zeit seit Klick bzw. Start
 *   sichtbarkeit / adresse             Tab verdeckt oder wieder da (Chrome drosselt verdeckte Tabs), `#`-Wechsel
 *   haenger                            Aufgaben im Hauptfaden ab 300 ms (Long-Task-Schnittstelle des Browsers; ab 1 s als Warnung)
 *   reiter_bilder                      15 s nach einem Reiterklick: Zahl und längstes Bild, Bilder ≥ 250 ms, Größe der Zeichenflächen — das Hängen der 3D-Ansicht, das `haenger` nicht sieht
 *   modell_geladen                     das Modell des Stands/der Runde in der 3D-Ansicht: Ladezeit des Browsers (`Engine2d3dKleiderbuehnenmodell._laden`, Ereignis `engine2d3dkleider-modell`)
 *   js_fehler / js_ablehnung / lade_fehler  Fehler im Skript, nicht abgefangene Zusagen, Skript/Stil, die nicht ankamen
 */
export class Engine2d3dKleiderAktionslog {

    static SEITE = 'engine2d3dkleider';
    static ADRESSE = '/api/log/';
    static LANG_MS = 300;
    static HAENGER_MS = 1000;
    static PRUEFUNG_MS = 300;
    static BILDER_S = 15;
    static RUCKLER_MS = 250;
    static INTERAKTIV = 'button, a[href], [role="tab"], summary, select, input, textarea, [data-aktion]';

    /** @param {HTMLElement|null} leiste die Reiterleiste (`#auftrag-reiter`); ohne sie bleibt der Rest in Kraft */
    static starten(leiste) {
        const log = new Engine2d3dKleiderAktionslog(leiste);
        log.anmelden();
        return log;
    }

    constructor(leiste) {
        this.leiste = leiste;
        this.kennung = Math.random().toString(36).slice(2, 6);
        this._start = performance.now();
        this._wechsel = null;            // der laufende Reiterwechsel: { name, start }
        this._bereit = false;
    }

    // ------------------------------------------------------------------ Schreiben

    melden(aktion, detail = '', stufe = 'info') {
        const rumpf = JSON.stringify({ page: Engine2d3dKleiderAktionslog.SEITE, action: aktion, detail: `[${this.kennung}] ${detail}`, level: stufe });
        try {
            fetch(Engine2d3dKleiderAktionslog.ADRESSE, {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: rumpf, keepalive: true,
            // stumm gewollt: Diese Zeile IST der Protokollweg — ein Fehler dabei darf die Bedienung nicht aufhalten und sich nicht selbst melden.
            }).catch(() => {});
        } catch { /* stumm gewollt: siehe oben */ }
    }

    // ------------------------------------------------------------------ Beschreiben

    /** `button#starten reiter=iterationen „Iterationen"` — Name, Datenattribute und Beschriftung (gekürzt). */
    beschreiben(el) {
        const daten = Object.entries(el.dataset || {}).slice(0, 4).map(([k, v]) => `${k}=${String(v).slice(0, 30)}`).join(' ');
        const name = el.id ? `#${el.id}` : (el.getAttribute('name') ? `[name=${el.getAttribute('name')}]` : '');
        const eingabe = el.matches('input, select, textarea');
        const text = (eingabe ? (el.getAttribute('aria-label') || el.title || '') : el.textContent.replace(/\s+/g, ' ').trim()).slice(0, 40);
        return `${el.tagName.toLowerCase()}${name} ${daten} „${text}"`.replace(/\s+/g, ' ').trim();
    }

    wert(el) {
        if (el.type === 'checkbox' || el.type === 'radio') return String(el.checked);
        if (el.type === 'password' || el.type === 'file') return '…';
        return JSON.stringify(String(el.value).slice(0, 60));
    }

    /** Knöpfe und Felder der Reiter, wie sie jetzt stehen — `gewaehlt`/`offen` gegen `-`/`zu`. */
    zustand() {
        const knoepfe = this.leiste ? [...this.leiste.querySelectorAll('[role="tab"][data-reiter]')]
            .map(k => `${k.dataset.reiter}=${k.getAttribute('aria-selected') === 'true' ? 'gewaehlt' : '-'}`) : [];
        const felder = [...document.querySelectorAll('[data-reiterfeld]')].map(f => `${f.dataset.reiterfeld}=${f.hidden ? 'zu' : 'offen'}`);
        return `Knöpfe ${knoepfe.join(' ')} · Felder ${felder.join(' ')}`;
    }

    // ------------------------------------------------------------------ Anmelden

    anmelden() {
        const kenn = navigator.userAgent.match(/(OPR|Edg|Firefox|Chrome)\/[\d.]+/);
        this.melden('seite_offen', `${location.hash || '(ohne #)'} · ${kenn ? kenn[0] : 'Browser unbekannt'} · ${document.visibilityState}`);
        // Erfassungsphase: Der Klick wird gemeldet, auch wenn ein Zuhörer weiter unten ihn schluckt oder wirft.
        document.addEventListener('click', e => this._klick(e), true);
        document.addEventListener('pointerdown', e => this._druck(e), true);
        document.addEventListener('contextmenu', e => this._rechtsklick(e), true);
        document.addEventListener('change', e => this._aenderung(e), true);
        document.addEventListener('visibilitychange', () => this.melden('sichtbarkeit', document.visibilityState));
        window.addEventListener('hashchange', () => this.melden('adresse', location.hash));
        window.addEventListener('engine2d3dkleider-modell', e => this.melden('modell_geladen', e.detail.text, e.detail.stufe));
        if (this.leiste) {
            this.leiste.addEventListener('reiterwechsel', e => this._reiterwechsel(e.detail.name));
            this.leiste.addEventListener('reiterfertig', () => this._reiterfertig());
        }
        this._fehler();
        this._haenger();
    }

    _ziel(e) {
        return e.target instanceof Element ? e.target.closest(Engine2d3dKleiderAktionslog.INTERAKTIV) : null;
    }

    /**
     * Ein Druck innerhalb des Rechtecks der Reiterleiste — auch wenn das Ziel kein Reiterknopf ist (etwas liegt darüber, die Leiste ist unter die
     * Kopfzeile gerutscht) oder die Seite nichts davon bemerkt. `klick` sieht nur Knöpfe; ein Klick, der daneben fällt, bliebe sonst ohne Spur
     * (05.10.2026, Edgar: „Wechsel zum Tab Iterationen funktioniert nicht" — im Protokoll stand von diesem Klick nichts).
     */
    _druck(e) {
        if (!this.leiste) return;
        const r = this.leiste.getBoundingClientRect();
        if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) return;
        const ziel = e.target instanceof Element ? e.target : null;
        const knopf = ziel ? ziel.closest('[role="tab"][data-reiter]') : null;
        const wo = knopf ? `auf ${knopf.dataset.reiter}` : `NEBEN den Reitern: ${ziel ? ziel.tagName.toLowerCase() + (ziel.id ? '#' + ziel.id : '') : '?'}`;
        this.melden('reiter_druck', `${wo} · Fenster ${innerWidth}x${innerHeight} · Scroll ${Math.round(scrollY)} · Leiste y=${Math.round(r.top)}`, knopf ? 'info' : 'warning');
    }

    _klick(e) {
        const ziel = this._ziel(e);
        if (!ziel) {
            // Druck und Loslassen auf verschiedenen Elementen (die Leiste rückte dazwischen): der Klick geht an die Leiste selbst, kein Knopf bekommt ihn.
            if (this.leiste && e.target === this.leiste) this.melden('reiter_daneben', `Klick ging an die Leiste, nicht an einen Reiter · ${this.zustand()}`, 'warning');
            return;
        }
        const verzoegert = Math.round(performance.now() - e.timeStamp);
        const stufe = verzoegert >= Engine2d3dKleiderAktionslog.HAENGER_MS ? 'warning' : 'info';
        const rest = ` · verzoegert=${verzoegert}ms${ziel.disabled ? ' · GESPERRT' : ''}${e.isTrusted ? '' : ' · per Skript'}`;
        const reiter = ziel.matches('[role="tab"][data-reiter]');
        this.melden(reiter ? 'reiter_klick' : 'klick', this.beschreiben(ziel) + rest, stufe);
        if (reiter) {
            this._nachpruefen(ziel.dataset.reiter, performance.now());
            this._bilder(ziel.dataset.reiter);
        }
    }

    _rechtsklick(e) {
        const ziel = this._ziel(e) || (e.target instanceof Element ? e.target : null);
        if (ziel) this.melden('rechtsklick', this.beschreiben(ziel));
    }

    _aenderung(e) {
        const ziel = e.target instanceof Element && e.target.matches('input, select, textarea') ? e.target : null;
        if (ziel) this.melden('aenderung', `${this.beschreiben(ziel)} = ${this.wert(ziel)}`);
    }

    // ------------------------------------------------------------------ Reiter

    /** Kurz nach dem Klick prüfen, ob das Feld des Reiters sichtbar ist — der Klick ist gemeldet, das Ergebnis hier. */
    _nachpruefen(name, start) {
        setTimeout(() => {
            const offen = [...document.querySelectorAll('[data-reiterfeld]')].filter(f => !f.hidden).map(f => f.dataset.reiterfeld);
            const ok = offen.length === 1 && offen[0] === name;
            this.melden('reiter_ergebnis', `${name} → sichtbar: ${offen.join(',') || 'keins'} · ${ok ? 'ok' : 'FALSCH'} · nach ${Math.round(performance.now() - start)}ms`,
                ok ? 'info' : 'warning');
        }, Engine2d3dKleiderAktionslog.PRUEFUNG_MS);
    }

    /**
     * 15 s nach einem Reiterklick die Bildfolge messen (05.10.2026, Edgar: „beim Wechsel auf Iterationen hängt das UI auch"): Der Hänger-Beobachter sieht nur den Hauptfaden — rechnet ein 3D-Bild
     * zu lange (große Fläche, viel Geometrie), bleibt die Seite stehen, ohne dass dort eine lange Aufgabe steht. Die Zeile nennt Zahl und Länge der Bilder und die Größe der Zeichenflächen.
     * Ein verdeckter Tab zeichnet keine Bilder (Chrome) — dann steht `verdeckt` dabei und die Zahl sagt nichts.
     */
    _bilder(name) {
        const s = Engine2d3dKleiderAktionslog;
        const start = performance.now();
        let letzter = start, anzahl = 0, hoechst = 0, ruckler = 0, verdeckt = document.visibilityState !== 'visible';
        let aus = false;
        const takt = jetzt => {
            anzahl += 1;
            hoechst = Math.max(hoechst, jetzt - letzter);
            ruckler += jetzt - letzter >= s.RUCKLER_MS ? 1 : 0;
            letzter = jetzt;
            if (!aus) requestAnimationFrame(takt);
        };
        requestAnimationFrame(takt);
        // Der Abschluss hängt an einem Zeitgeber, nicht am letzten Bild: Ein verdeckter Tab bekommt keine Bilder, und ein hängender liefert den Bericht eben später.
        setTimeout(() => {
            aus = true;
            if (document.visibilityState !== 'visible') verdeckt = true;
            const flaechen = [...document.querySelectorAll('canvas')].map(c => `${c.width}x${c.height}`).join(' ') || 'keine';
            this.melden('reiter_bilder', `${name} · ${anzahl} Bilder in ${s.BILDER_S} s · längstes ${Math.round(hoechst)}ms · ${ruckler}× über ${s.RUCKLER_MS}ms · Flächen ${flaechen} · DPR ${devicePixelRatio}${verdeckt ? ' · verdeckt' : ''}`,
                ruckler ? 'warning' : 'info');
        }, s.BILDER_S * 1000);
    }

    _reiterwechsel(name) {
        this._wechsel = { name, start: performance.now() };
        this.melden('reiter_wechsel', `${name} · ${this.zustand()}`);
    }

    _reiterfertig() {
        if (!this._wechsel) {
            if (this._bereit) return;
            this._bereit = true;
            this.melden('seite_bereit', `${Math.round(performance.now() - this._start)}ms nach dem Laden der Seite`);
            return;
        }
        const { name, start } = this._wechsel;
        this._wechsel = null;
        this.melden('reiter_fertig', `${name} nach ${Math.round(performance.now() - start)}ms`);
    }

    // ------------------------------------------------------------------ Fehler und Hänger

    _fehler() {
        // Erfassungsphase, damit auch Skripte und Stile gemeldet werden, die nicht ankamen (ein Ladefehler steigt nicht auf).
        window.addEventListener('error', e => {
            const quelle = e.target && e.target !== window ? (e.target.src || e.target.href || e.target.tagName) : '';
            if (quelle) this.melden('lade_fehler', String(quelle).slice(-120), 'error');
            else this.melden('js_fehler', `${e.message} @ ${String(e.filename || '').split('/').pop()}:${e.lineno}`, 'error');
        }, true);
        window.addEventListener('unhandledrejection', e => this.melden('js_ablehnung', String((e.reason && e.reason.message) || e.reason).slice(0, 300), 'error'));
    }

    _haenger() {
        if (typeof PerformanceObserver === 'undefined' || !(PerformanceObserver.supportedEntryTypes || []).includes('longtask')) return;
        new PerformanceObserver(liste => {
            for (const t of liste.getEntries()) {
                if (t.duration < Engine2d3dKleiderAktionslog.LANG_MS) continue;
                this.melden('haenger', `Hauptfaden ${Math.round(t.duration)}ms belegt, ab ${(t.startTime / 1000).toFixed(1)} s nach dem Laden`,
                    t.duration >= Engine2d3dKleiderAktionslog.HAENGER_MS ? 'warning' : 'info');
            }
        }).observe({ type: 'longtask', buffered: true });
    }
}
