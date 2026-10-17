/**
 * Aktionsprotokoll — jede Bedienung im Browser ins Serverprotokoll (`logs/client.log`), auf JEDER Seite (12.10.2026).
 *
 * Edgar: „Ändern des Namens im Job funktioniert nicht (edit button)" — im Protokoll stand von diesem Klick nichts, weil `client.log` nur Serveranfragen kannte (`server_call`). Ob ein Klick ankam, ob die
 * Seite etwas tat und was sie dem Nutzer sagte, ließ sich nicht nachlesen. Dann: „mach sofort Logs für alle Aktionen aus dem Projekt".
 *
 * Eingehängt in `templates/base.html` (erbt jede Seite), in einem eigenen Modul-Skript: Lädt dieses Modul nicht, laufen Combo- und Baumsortierung trotzdem. Geschrieben wird über `Serverprotokoll`
 * (`POST /api/log/`, bei einem Serverausfall aufgehoben und nachgeliefert); die Seite im Protokoll ist das erste Pfadstück (`/mesh-3D/<kennung>/` → `mesh-3D`), jede Zeile trägt die Kennung des Tabs
 * (`[a1b2]`), weil mehrere Tabs derselben Seite offen sein können.
 *
 *   seite_offen / seite_verlassen   Adresse, Browser, ob der Tab sichtbar ist
 *   klick / rechtsklick             Knopf, Link, Reiter, Feld oder Fläche (`tag#id.klasse „Beschriftung“`); `verzoegert` = Zeit zwischen Klick und Bearbeitung, `GESPERRT` bei gesperrtem Knopf
 *   aenderung                       Auswahl, Häkchen, Schieber, Textfeld nach dem Verlassen — mit dem neuen Wert (nie bei Passwort und Datei)
 *   taste                           nur Enter, Escape, Entf, F-Tasten und Strg/Alt-Kürzel; getippter Text wird NIE protokolliert
 *   absenden                        ein Formular wird abgeschickt
 *   alert / confirm / prompt        der Text, den die Seite dem Nutzer zeigt (die Meldung „… konnte nicht gespeichert werden“ stand sonst nirgends), bei confirm/prompt die Antwort
 *   js_fehler / js_ablehnung / lade_fehler   Fehler im Skript, nicht abgefangene Zusagen, Skripte/Stile, die nicht ankamen
 *   sichtbarkeit / adresse          Tab verdeckt oder wieder da, `#`-Wechsel
 *   Seitenlogger (`window.Aktionsprotokoll.melden(aktion, detail)`)   für Entscheidungen im Code, die kein Ereignis sind (z. B. „Name unverändert, nichts gesendet“)
 *
 * Die Seite „2D3D Kleider“ hat einen eigenen, genaueren Logger (`Engine2d3dKleiderAktionslog`); er setzt `data-aktionslog="eigen"` an `<html>`, dann lässt dieses Modul Klick, Änderung und Fehler aus
 * (sonst stünde jede Zeile doppelt) und schreibt nur noch Tasten und Dialoge.
 */
import { Serverprotokoll } from './serverprotokoll.js';

export class Aktionsprotokoll {

    static INTERAKTIV = 'button, a[href], [role="tab"], [role="button"], summary, select, input, textarea, label, [data-aktion]';
    static TEXT_MAX = 40;
    static WERT_MAX = 60;
    static HAENGER_MS = 1000;
    static EINGABE_SPAET_MS = 300;       // ein Druck, der so spät im Hauptfaden ankommt, wird als verzögert gemeldet
    static KLICK_MS = 600;               // so lange wartet ein losgelassener Druck auf seinen Klick
    static BILDER_S = 10;
    static BILD_LANG_MS = 250;
    static BILD_FPS_MIN = 15;
    static _instanz = null;

    /** Einmal je Seite; ein zweiter Aufruf liefert dieselbe Instanz. */
    static einrichten() {
        if (!Aktionsprotokoll._instanz) {
            Aktionsprotokoll._instanz = new Aktionsprotokoll();
            Aktionsprotokoll._instanz.anmelden();
        }
        return Aktionsprotokoll._instanz;
    }

    /**
     * Für Seitencode: eine Entscheidung ins Protokoll. Die Instanz kann in einer ANDEREN Kopie dieser Klasse liegen — die Szenen-Bündel (`mesh3d.js` …) bringen ihre eigene mit,
     * `base.html` lädt die einzelne Datei —, deshalb auch über `window.Aktionsprotokoll` suchen. Fehlt sie ganz (Seite ohne `base.html`), ist das Melden stumm.
     */
    static melden(aktion, detail = '', stufe = 'info') {
        const instanz = Aktionsprotokoll._instanz || (window.Aktionsprotokoll && window.Aktionsprotokoll._instanz);
        if (instanz) instanz.melden(aktion, detail, stufe);
    }

    constructor() {
        this.kennung = Math.random().toString(36).slice(2, 6);
        this.seite = (location.pathname.split('/').filter(Boolean)[0] || 'start');
        this._offen = null;                // der Druck, dessen Klick noch aussteht (`_druck`, `_los`)
    }

    melden(aktion, detail = '', stufe = 'info') {
        try {
            Serverprotokoll.melden(this.seite, aktion, `[${this.kennung}] ${detail}`, stufe);
        // stumm gewollt: Dies IST der Protokollweg — ein Fehler darin darf die Bedienung nicht aufhalten und sich nicht selbst melden.
        } catch { /* stumm gewollt */ }
    }

    /** Wird die Seite von einem eigenen Logger bedient (`data-aktionslog="eigen"`), schreibt dieses Modul nur Tasten und Dialoge. */
    _eigen() {
        return document.documentElement.dataset.aktionslog === 'eigen';
    }

    // ------------------------------------------------------------------ Beschreiben

    /** `button#auftrag-loeschen.btn.btn-secondary „Auftrag löschen“` — Name, Klassen (höchstens drei), Datenattribute und Beschriftung (gekürzt). */
    beschreiben(el) {
        // `btn`-Klassen sagen nichts (jeder Knopf trägt sie); ein Knopf nur mit Symbol bekommt dessen Namen (`fa-pen`) als Beschriftung.
        const klassen = (el.getAttribute('class') || '').split(/\s+/).filter(k => k && !/^btn(-|$)/.test(k)).slice(0, 3).map(k => `.${k}`).join('');
        const symbol = el.querySelector ? el.querySelector('i[class*="fa-"]') : null;
        const symbolname = symbol ? (symbol.getAttribute('class').split(/\s+/).find(k => /^fa-/.test(k) && !/^fa-(solid|regular|brands|fw|lg|sm|xs)$/.test(k)) || '') : '';
        const name = el.id ? `#${el.id}` : (el.getAttribute('name') ? `[name=${el.getAttribute('name')}]` : '');
        const daten = Object.entries(el.dataset || {}).slice(0, 3).map(([k, v]) => `${k}=${String(v).slice(0, 30)}`).join(' ');
        const eingabe = el.matches('input, select, textarea');
        const art = el.tagName.toLowerCase() + (eingabe && el.type ? `:${el.type}` : '');
        const text = (eingabe ? (el.getAttribute('aria-label') || el.title || el.placeholder || '') : (el.textContent || '').replace(/\s+/g, ' ').trim())
            .slice(0, Aktionsprotokoll.TEXT_MAX);
        const vorfahr = el.id ? '' : this._vorfahr(el);
        return `${art}${name}${klassen}${daten ? ' ' + daten : ''}${text ? ` „${text}“` : ''}${symbolname ? ` [${symbolname}]` : ''}${vorfahr}`;
    }

    /** ` in #auftrag-reiter` — das nächste Elternelement mit Kennung, damit ein Klick auf ein Symbol oder eine Zeile zuzuordnen ist. */
    _vorfahr(el) {
        const eltern = el.parentElement ? el.parentElement.closest('[id]') : null;
        return eltern ? ` in #${eltern.id}` : '';
    }

    wert(el) {
        if (el.type === 'checkbox' || el.type === 'radio') return String(el.checked);
        if (el.type === 'password' || el.type === 'file') return '…';
        return JSON.stringify(String(el.value).slice(0, Aktionsprotokoll.WERT_MAX));
    }

    _ziel(e) {
        return e.target instanceof Element ? e.target.closest(Aktionsprotokoll.INTERAKTIV) : null;
    }

    // ------------------------------------------------------------------ Anmelden

    anmelden() {
        const kenn = navigator.userAgent.match(/(OPR|Edg|Firefox|Chrome)\/[\d.]+/);
        this.melden('seite_offen', `${location.pathname}${location.search}${location.hash} · ${kenn ? kenn[0] : 'Browser unbekannt'} · ${document.visibilityState}`);
        // Erfassungsphase: Die Bedienung wird gemeldet, auch wenn ein Zuhörer weiter unten sie schluckt oder wirft.
        document.addEventListener('click', e => this._klick(e), true);
        document.addEventListener('pointerdown', e => this._druck(e), true);
        document.addEventListener('pointerup', e => this._los(e), true);
        document.addEventListener('contextmenu', e => this._rechtsklick(e), true);
        document.addEventListener('change', e => this._aenderung(e), true);
        document.addEventListener('keydown', e => this._taste(e), true);
        document.addEventListener('submit', e => this._absenden(e), true);
        document.addEventListener('visibilitychange', () => { if (!this._eigen()) this.melden('sichtbarkeit', document.visibilityState); });
        window.addEventListener('hashchange', () => { if (!this._eigen()) this.melden('adresse', location.hash); });
        window.addEventListener('pagehide', () => this._verlassen());
        window.addEventListener('error', e => this._fehler(e), true);
        window.addEventListener('unhandledrejection', e => {
            if (!this._eigen()) this.melden('js_ablehnung', String((e.reason && e.reason.message) || e.reason).slice(0, 300), 'error');
        });
        this._dialoge();
        this._bilder();
        window.addEventListener('load', () => this._waechter());
        window.Aktionsprotokoll = Aktionsprotokoll;
    }

    /**
     * Der Wächter im eigenen Faden (`Hauptfadenwaechter`, 05.10.2026) für JEDE Seite: steht der Hauptfaden, schreibt der Worker selbst `haenger_live` / `haenger_ende` ins Protokoll — der Hauptfaden kann es dann
     * nicht (12.10.2026, Edgar: Klicks, die nie ankamen, ohne eine Zeile im Log; ein offener `alert()` und eine blockierte Seite sehen im Protokoll gleich aus: Schweigen). Erst nach `load`, damit eine Seite mit
     * eigenem Logger (`data-aktionslog="eigen"`, startet ihren eigenen Wächter) keinen zweiten bekommt; dynamisch geladen, damit ein Fehler dort die Bedienung nicht aufhält.
     */
    _waechter() {
        if (this._eigen()) return;
        import('./hauptfadenwaechter.js')
            .then(modul => modul.Hauptfadenwaechter.starten({
                adresse: Serverprotokoll.ADRESSE, seite: this.seite, kennung: this.kennung, fehler: text => this.melden('lade_fehler', text, 'error'),
            }))
            .catch(fehler => this.melden('lade_fehler', `hauptfadenwaechter.js: ${fehler && fehler.message ? fehler.message : fehler}`, 'error'));
    }

    // ------------------------------------------------------------------ Verlorene und verspätete Eingaben

    /**
     * Ein Druck der linken Taste. Zwei Fragen, die das Protokoll sonst nicht beantwortet („ich habe zwanzigmal geklickt, und nichts geschah“, Edgar 12.10.2026):
     * (1) Kam der Druck an, aber spät? `verzoegert` = Zeit zwischen dem Druck und seiner Bearbeitung im Hauptfaden — ein belegter Hauptfaden (Bühne, Aufbau) zeigt sich hier.
     * (2) Kam er an, ohne dass ein Klick folgte? Dann steht in `druck_ohne_klick`, wo gedrückt und wo losgelassen wurde. Kommt GAR NICHTS an (weder Druck noch Klick), liegt es nicht an der Seite.
     */
    _druck(e) {
        if (e.button !== 0) return;
        const ziel = e.target instanceof Element ? e.target : null;
        const verzoegert = Math.round(performance.now() - e.timeStamp);
        const eintrag = { ziel: ziel ? this.beschreiben(ziel) : '?', x: Math.round(e.clientX), y: Math.round(e.clientY), t: e.timeStamp };
        this._offen = eintrag;
        if (verzoegert >= Aktionsprotokoll.EINGABE_SPAET_MS) {
            this.melden('eingabe_verzoegert', `Druck auf ${eintrag.ziel} wurde erst ${verzoegert}ms nach der Bewegung bearbeitet (Hauptfaden belegt) · ${document.visibilityState}`, 'warning');
        }
    }

    _los(e) {
        const eintrag = this._offen;
        if (!eintrag || e.button !== 0) return;
        const ziel = e.target instanceof Element ? this.beschreiben(e.target) : '?';
        setTimeout(() => {
            if (this._offen !== eintrag) return;           // ein Klick hat ihn inzwischen abgeholt
            this._offen = null;
            this.melden('druck_ohne_klick', `Druck bei ${eintrag.x},${eintrag.y} auf ${eintrag.ziel}, losgelassen auf ${ziel}, kein Klick nach ${Aktionsprotokoll.KLICK_MS}ms · ${Math.round(e.timeStamp - eintrag.t)}ms gedrückt`, 'warning');
        }, Aktionsprotokoll.KLICK_MS);
    }

    /**
     * Langsame Bilder der Seite: Schreibt nur, wenn ein Zeitraum von `BILDER_S` Sekunden ein Bild ≥ `BILD_LANG_MS` oder unter `BILD_FPS_MIN` Bilder je Sekunde hatte — mit der Größe der Zeichenflächen.
     * Läuft nur, solange der Tab sichtbar ist (ein verdeckter Tab bekommt von Chrome keine Bilder).
     */
    _bilder() {
        let letzter = null, anzahl = 0, laengstes = 0, start = null;
        const takt = jetzt => {
            if (document.visibilityState === 'visible') {
                if (start === null) start = jetzt;
                if (letzter !== null) laengstes = Math.max(laengstes, jetzt - letzter);
                anzahl += 1;
                letzter = jetzt;
                if (jetzt - start >= Aktionsprotokoll.BILDER_S * 1000) {
                    const fps = anzahl / ((jetzt - start) / 1000);
                    if (laengstes >= Aktionsprotokoll.BILD_LANG_MS || fps < Aktionsprotokoll.BILD_FPS_MIN) {
                        const flaechen = [...document.querySelectorAll('canvas')].map(c => `${c.width}x${c.height}`).join(' ') || 'keine';
                        this.melden('bilder_langsam', `${fps.toFixed(1)} Bilder/s, längstes ${Math.round(laengstes)}ms in ${Aktionsprotokoll.BILDER_S} s · Flächen ${flaechen} · DPR ${devicePixelRatio}`, 'warning');
                    }
                    letzter = null; anzahl = 0; laengstes = 0; start = null;
                }
            } else { letzter = null; anzahl = 0; laengstes = 0; start = null; }
            requestAnimationFrame(takt);
        };
        requestAnimationFrame(takt);
    }

    // ------------------------------------------------------------------ Ereignisse

    _klick(e) {
        this._offen = null;                // der Druck davor hat seinen Klick bekommen
        if (this._eigen()) return;
        const ziel = this._ziel(e) || (e.target instanceof Element ? e.target : null);
        if (!ziel) return;
        const verzoegert = Math.round(performance.now() - e.timeStamp);
        const stufe = verzoegert >= Aktionsprotokoll.HAENGER_MS ? 'warning' : 'info';
        const rest = ` · verzoegert=${verzoegert}ms${ziel.disabled ? ' · GESPERRT' : ''}${e.isTrusted ? ` · bei ${Math.round(e.clientX)},${Math.round(e.clientY)}` : ' · per Skript'}`;
        this.melden('klick', this.beschreiben(ziel) + rest, stufe);
    }

    _rechtsklick(e) {
        if (this._eigen()) return;
        const ziel = this._ziel(e) || (e.target instanceof Element ? e.target : null);
        if (ziel) this.melden('rechtsklick', this.beschreiben(ziel));
    }

    _aenderung(e) {
        if (this._eigen()) return;
        const ziel = e.target instanceof Element && e.target.matches('input, select, textarea') ? e.target : null;
        if (ziel) this.melden('aenderung', `${this.beschreiben(ziel)} = ${this.wert(ziel)}`);
    }

    /** Enter, Escape, Entf, F-Tasten, Strg/Alt-Kürzel. Einzelne Zeichen in Feldern gehören dem Nutzer und werden nie geschrieben. */
    _taste(e) {
        if (e.repeat || ['Shift', 'Control', 'Alt', 'Meta', 'CapsLock', 'Tab'].includes(e.key)) return;
        const ziel = e.target instanceof Element ? e.target : null;
        const feld = !!ziel && ziel.matches('input, textarea, select, [contenteditable=""], [contenteditable="true"]');
        const kuerzel = e.ctrlKey || e.altKey || e.metaKey;
        const besonders = ['Enter', 'Escape', 'Delete'].includes(e.key) || /^F\d+$/.test(e.key);
        if (feld && !besonders && !kuerzel) return;
        const tasten = [e.ctrlKey && 'Strg', e.altKey && 'Alt', e.metaKey && 'Meta', e.shiftKey && 'Umschalt', e.key].filter(Boolean).join('+');
        const wo = ziel ? this.beschreiben(ziel) : 'Seite';
        const wert = feld && e.key === 'Enter' && ziel.matches('input, textarea') ? ` = ${this.wert(ziel)}` : '';
        this.melden('taste', `${tasten} auf ${wo}${wert}`);
    }

    _absenden(e) {
        const form = e.target instanceof Element ? e.target : null;
        if (form) this.melden('absenden', `${this.beschreiben(form)} → ${String(form.getAttribute('action') || location.pathname).slice(0, 80)}`);
    }

    _fehler(e) {
        if (this._eigen()) return;
        // Erfassungsphase, damit auch Skripte und Stile gemeldet werden, die nicht ankamen (ein Ladefehler steigt nicht auf).
        const quelle = e.target && e.target !== window ? (e.target.src || e.target.href || e.target.tagName) : '';
        if (quelle) this.melden('lade_fehler', String(quelle).slice(-120), 'error');
        else this.melden('js_fehler', `${e.message} @ ${String(e.filename || '').split('/').pop()}:${e.lineno}`, 'error');
    }

    /** Die Seite wird verlassen oder geschlossen. `sendBeacon`, weil ein `fetch` dabei abgebrochen wird. */
    _verlassen() {
        try {
            const rumpf = JSON.stringify({ page: this.seite, action: 'seite_verlassen', detail: `[${this.kennung}] ${location.pathname}`, level: 'info' });
            navigator.sendBeacon(Serverprotokoll.ADRESSE, new Blob([rumpf], { type: 'application/json' }));
        // stumm gewollt: siehe `melden`.
        } catch { /* stumm gewollt */ }
    }

    // ------------------------------------------------------------------ Meldungen der Seite an den Nutzer

    /** `alert`, `confirm` und `prompt` ersetzen, damit der gezeigte Text und die Antwort im Protokoll stehen. Das Verhalten bleibt unverändert. */
    _dialoge() {
        for (const name of ['alert', 'confirm', 'prompt']) {
            const original = window[name].bind(window);
            window[name] = (...args) => {
                const text = JSON.stringify(String(args[0] === undefined ? '' : args[0]).slice(0, 200));
                if (name === 'alert') this.melden(name, text, 'warning');       // vor dem Anzeigen: Der Dialog hält die Seite an, bis jemand OK klickt
                const antwort = original(...args);
                if (name !== 'alert') this.melden(name, `${text} → ${JSON.stringify(antwort)}`);
                return antwort;
            };
        }
    }
}
