import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Panelbreiten — ziehbare Seitenleisten, deren Breite gemerkt wird.
 *
 * Herausgelöst aus `library.js` (329 Zeilen). Mit der BVH-Bibliothek hat das
 * nichts zu tun: Es sind die zwei Panels links und rechts im Studio. Wer die
 * Bibliothek anfasste, musste das mitlesen.
 *
 * ZWEI KANTEN, ZWEI RECHNUNGEN
 * ============================
 * Ein Panel am linken Bildrand wird an seiner RECHTEN Kante gezogen
 * (`breite = mausX - links`), ein Panel am rechten Rand an seiner LINKEN
 * (`breite = rechts - mausX`). Wer das vertauscht, bekommt ein Panel, das beim
 * Ziehen nach rechts schmaler wird.
 *
 * `resize`-Ereignis am Ende: Der Three.js-Renderer hängt daran und passt sonst
 * seine Leinwand nicht an — sichtbar als verzerrte Szene.
 */
export class Panelbreiten {

    /** Die zwei Panels des Studios. */
    static PANELS = [
        { panelId: 'studio-sidebar', handleId: 'sidebar-resize',
          schluessel: 'bvhStudio_sidebarWidth', kante: 'right', min: 150, max: 600 },
        { panelId: 'props-panel', handleId: 'props-resize',
          schluessel: 'bvhStudio_propsWidth', kante: 'left', min: 260, max: 700 },
    ];

    /** Beide Panels anmelden. */
    static binden() {
        Panelbreiten.PANELS.forEach(angabe => new Panelbreiten(angabe).binden());
    }

    constructor({ panelId, handleId, schluessel, kante, min, max }) {
        this.panel = document.getElementById(panelId);
        this.griff = document.getElementById(handleId);
        this.schluessel = schluessel;
        this.kante = kante;
        this.min = min;
        this.max = max;
        this.zieht = false;
    }

    binden() {
        if (!this.panel || !this.griff) return;
        this.gemerkteBreite();
        this.griff.addEventListener('mousedown', ereignis => {
            this.zieht = true;
            this.griff.classList.add('dragging');
            ereignis.preventDefault();
        });
        document.addEventListener('mousemove', ereignis => this.ziehen(ereignis));
        document.addEventListener('mouseup', () => this.ablegen());
    }

    gemerkteBreite() {
        try {
            const gemerkt = parseInt(localStorage.getItem(this.schluessel) || '');
            if (!isNaN(gemerkt)) this.panel.style.width = this.begrenzt(gemerkt) + 'px';
        } catch (fehler) {
            Protokoll.debug('library', 'gemerkte Panelbreite nicht lesbar', fehler);
        }
    }

    ziehen(ereignis) {
        if (!this.zieht) return;
        const rahmen = this.panel.getBoundingClientRect();
        const breite = this.kante === 'left'
            ? rahmen.right - ereignis.clientX      // Panel rechts, Griff links
            : ereignis.clientX - rahmen.left;      // Panel links, Griff rechts
        this.panel.style.width = this.begrenzt(breite) + 'px';
    }

    ablegen() {
        if (!this.zieht) return;
        this.zieht = false;
        this.griff.classList.remove('dragging');
        try {
            localStorage.setItem(this.schluessel, parseInt(this.panel.style.width));
        } catch (fehler) {
            Protokoll.debug('library', 'Panelbreite nicht merkbar', fehler);
        }
        // Der Three.js-Renderer haengt daran — ohne das bleibt die Szene verzerrt.
        window.dispatchEvent(new Event('resize'));
    }

    begrenzt(breite) {
        return Math.max(this.min, Math.min(this.max, breite));
    }
}
