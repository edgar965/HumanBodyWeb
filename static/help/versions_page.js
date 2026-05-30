// static/help/versions_page.js
//
// Versionen-Page-Interaktion: Refresh mit Spinner-Indicator (statt synchrones
// Full-Page-Reload das 5-10s leer aussieht), Collapsible-Repos (Klick auf
// Repo-Head klappt Commit-Tabelle ein/aus), bfcache-Reload.

import { installBfcacheReload } from './help_common.js';


/** Verantwortung: Refresh-Button -- visuelles Spinner-Feedback waehrend
 *  der Reload laeuft. Anders als ein nakter <a href> der erst nach
 *  Vollendung der 5-10s gh-API-Calls visuell etwas tut, zeigen wir sofort
 *  einen Spinner.
 */
class RefreshController {
    constructor(btnEl, refreshUrl) {
        this.btnEl = btnEl;
        this.refreshUrl = refreshUrl;
    }

    bind() {
        if (!this.btnEl) return;
        this.btnEl.addEventListener('click', (ev) => {
            ev.preventDefault();
            this._showSpinner();
            window.location.href = this.refreshUrl;
        });
    }

    _showSpinner() {
        this.btnEl.classList.add('vw-loading');
        const icon = this.btnEl.querySelector('i');
        if (icon) icon.className = 'fas fa-circle-notch fa-spin';
        const span = this.btnEl.querySelector('.hv-btn-label');
        if (span) span.textContent = 'Lade...';
        this.btnEl.setAttribute('aria-busy', 'true');
        this.btnEl.style.pointerEvents = 'none';
    }
}


/** Verantwortung: Collapse-Toggle pro Repo-Block. Klick auf den Header
 *  schaltet `.vw-collapsed` auf dem Container -- CSS macht den Rest. */
class CollapseController {
    constructor(repoBlocks) {
        this.repoBlocks = repoBlocks;
    }

    bind() {
        for (const block of this.repoBlocks) {
            const head = block.querySelector('.vw-repo-head');
            if (!head) continue;
            head.style.cursor = 'pointer';
            head.title = 'Klick: Repo ein-/ausklappen';
            head.addEventListener('click', (ev) => {
                // Klicks auf den GitHub-Link/Tag-Link selbst durchlassen.
                if (ev.target.closest('a')) return;
                block.classList.toggle('vw-collapsed');
            });
        }
    }
}


export class VersionsPage {
    constructor({ refreshUrl = '?refresh=1' } = {}) {
        this.refresh = new RefreshController(
            document.getElementById('hvRefreshBtn'),
            refreshUrl,
        );
        this.collapse = new CollapseController(document.querySelectorAll('.vw-repo'));
    }

    setup() {
        this.refresh.bind();
        this.collapse.bind();
        installBfcacheReload();
    }
}


export function setupVersionsPage(opts = {}) {
    new VersionsPage(opts).setup();
}
