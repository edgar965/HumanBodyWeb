// static/help/help_common.js
//
// Geteilte Helper fuer die Hilfe-Seiten (Logs, Versionen). Module-Level
// Side-Effects sind idempotent (Modul wird vom Browser nur einmal evaluiert).

let _bfcacheInstalled = false;

/**
 * Erzwingt einen Reload wenn der Browser die Seite aus dem bfcache
 * wiederherstellt (z.B. Back-Button). Sonst sieht der User stale Logs/
 * Versionen ohne dass es einen Refetch gegeben hat.
 *
 * Idempotent -- registriert den Listener nur beim ersten Aufruf. Verhindert
 * Memory-Leak wenn `setup*Page()` mehrfach gerufen wird.
 */
export function installBfcacheReload() {
    if (_bfcacheInstalled) return;
    _bfcacheInstalled = true;
    window.addEventListener('pageshow', (ev) => {
        if (ev.persisted) window.location.reload();
    });
}

/**
 * parseInt der Zahl in einem Element, robust gegen Whitespace +
 * Tausender-Trenner. Default 0.
 */
export function readIntFrom(el, fallback = 0) {
    if (!el) return fallback;
    const digits = (el.textContent || '').replace(/\D/g, '');
    return digits ? parseInt(digits, 10) : fallback;
}

/**
 * Debounce: ruft fn erst nach `delay` ms ohne weitere Aufrufe.
 * Fuer Search-Input-Filter.
 */
export function debounce(fn, delay = 120) {
    let timer = null;
    return function debounced(...args) {
        if (timer !== null) clearTimeout(timer);
        timer = setTimeout(() => { timer = null; fn.apply(this, args); }, delay);
    };
}
