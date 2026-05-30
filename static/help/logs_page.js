// static/help/logs_page.js
//
// Logs-Page-Interaktion: Tab-Switch, Scroll-zum-Neuesten, Empty-Tab-Auto-
// Switch, bfcache-Reload, Substring-Filter ueber Search-Input.

import { installBfcacheReload, readIntFrom, debounce } from './help_common.js';


/** Verantwortung: Tab-Umschaltung zwischen Exceptions / Alle Logs. */
class TabsController {
    constructor(tabsEl, panes) {
        this.tabsEl = tabsEl;
        this.panes = panes; // { exceptions: HTMLElement, all: HTMLElement }
        this._onChange = null;
    }

    onChange(fn) { this._onChange = fn; }

    activate(which) {
        if (!this.tabsEl) return;
        this.tabsEl.querySelectorAll('.lg-tab').forEach(b => {
            b.classList.toggle('active', b.dataset.pane === which);
        });
        this.panes.exceptions?.classList.toggle('hidden', which !== 'exceptions');
        this.panes.all?.classList.toggle('hidden', which !== 'all');
        this._onChange?.(which);
    }

    bind() {
        if (!this.tabsEl) return;
        this.tabsEl.addEventListener('click', (ev) => {
            const btn = ev.target.closest('.lg-tab');
            if (btn) this.activate(btn.dataset.pane);
        });
    }
}


/** Verantwortung: Scroll auf "neueste Zeile sichtbar". */
class ScrollController {
    constructor(order) {
        this.order = order;
    }

    /** Bei order=desc = neueste oben = scrollTop=0.
     *  Bei order=asc = neueste unten = scrollHeight. Doppelt (sofort + rAF)
     *  damit late CSS/Font-Reflow nicht ueberschreibt. */
    toNewest(pane) {
        if (!pane) return;
        const target = (this.order === 'asc') ? pane.scrollHeight : 0;
        pane.scrollTop = target;
        requestAnimationFrame(() => { pane.scrollTop = target; });
    }
}


/** Verantwortung: Substring-Filter ueber alle .lg-line in einem Pane. */
class SearchFilter {
    constructor(inputEl, panes) {
        this.inputEl = inputEl;
        this.panes = panes; // { exceptions, all }
        this._apply = debounce(this._doApply.bind(this), 80);
    }

    bind() {
        if (!this.inputEl) return;
        this.inputEl.addEventListener('input', () => this._apply());
    }

    _doApply() {
        const q = (this.inputEl.value || '').trim().toLowerCase();
        const has = !!q;
        for (const pane of Object.values(this.panes)) {
            if (!pane) continue;
            pane.querySelectorAll('.lg-line').forEach(span => {
                const hit = !has || span.textContent.toLowerCase().includes(q);
                span.classList.toggle('lg-hidden', !hit);
                span.classList.toggle('lg-match', has && hit);
            });
        }
    }
}


/** Verantwortung: Coordinator -- haengt die Subsysteme zusammen. */
export class LogsPage {
    constructor({ order = 'desc' } = {}) {
        this.order = order;
        this.panes = {
            exceptions: document.getElementById('lgPaneExceptions'),
            all:        document.getElementById('lgPaneAll'),
        };
        this.tabs = new TabsController(document.getElementById('lgTabs'), this.panes);
        this.scroll = new ScrollController(order);
        this.search = new SearchFilter(document.getElementById('lgSearch'), this.panes);
    }

    /** Wenn der Default-Tab (Exceptions) leer ist, gleich auf "Alle Logs"
     * umschalten -- verhindert dass User eine leere Page sieht. */
    _autoSwitchIfEmpty() {
        const exCount  = readIntFrom(document.querySelector('.lg-tab[data-pane="exceptions"] .lg-count'));
        const allCount = readIntFrom(document.querySelector('.lg-tab[data-pane="all"] .lg-count'));
        if (exCount === 0 && allCount > 0) this.tabs.activate('all');
    }

    setup() {
        if (!this.tabs.tabsEl) return;
        this.tabs.onChange((which) => {
            this.scroll.toNewest(which === 'exceptions' ? this.panes.exceptions : this.panes.all);
        });
        this.tabs.bind();
        this.search.bind();
        // Initial: beide Panes auf neuesten Scroll-Punkt, dann ggf. autoswitch.
        Object.values(this.panes).forEach(p => this.scroll.toNewest(p));
        this._autoSwitchIfEmpty();
        installBfcacheReload();
    }
}


export function setupLogsPage(opts = {}) {
    new LogsPage(opts).setup();
}
