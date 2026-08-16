import { el, Ziehgriff } from './bauteile.js';

/**
 * Videofenster — das schwebende Fenster mit dem Originalvideo: ein- und
 * ausschalten, verschieben, in der Größe ziehen, schließen.
 *
 * Aus knopfleiste.js herausgeloest (Umbau 16.08.2026). Verschieben und Größe
 * waren zwei ausgeschriebene Maus-Ziehschleifen; beide gehen jetzt über
 * `Ziehgriff`. Das Verschieben rechnete dabei Schritt für Schritt weiter
 * (`startX = ev.clientX` in jedem Zug) — das läuft bei schnellen Bewegungen
 * vom Zeiger weg. Jetzt Ausgangslage plus Abstand zum Druckpunkt.
 */
export class Videofenster {

    /** Kleinste Maße beim Ziehen. */
    static MIN_BREITE = 200;
    static MIN_HOEHE = 120;

    /**
     * Baut den Umschaltknopf in die Leiste und verdrahtet das Fenster.
     * Gibt null zurück, wenn die Seite kein Videofenster hat.
     */
    static bauen(leiste) {
        const fenster = document.getElementById('floatingVideo');
        if (!fenster) return null;
        const werk = new Videofenster(fenster);
        leiste.appendChild(werk.knopf());
        werk.verschieben();
        werk.groesse();
        return werk;
    }

    constructor(fenster) {
        this.fenster = fenster;
        this.schalter = null;
    }

    knopf() {
        this.schalter = el('button', 'rc-toggle-btn active');
        this.schalter.innerHTML = '<i class="fas fa-video"></i> Original';
        this.schalter.addEventListener('click', () => {
            this.fenster.classList.toggle('hidden');
            this.schalter.classList.toggle('active', !this.versteckt());
        });
        document.getElementById('floatingVideoClose')
            ?.addEventListener('click', () => this.schliessen());
        return this.schalter;
    }

    versteckt() {
        return this.fenster.classList.contains('hidden');
    }

    schliessen() {
        this.fenster.classList.add('hidden');
        this.schalter?.classList.remove('active');
    }

    verschieben() {
        let start = null;
        Ziehgriff.an(document.getElementById('floatingVideoTitlebar'),
            (dx, dy) => {
                this.fenster.style.left = start.left + dx + 'px';
                this.fenster.style.top = start.top + dy + 'px';
                // Unten losgelassen, sonst zieht die CSS-Vorgabe zurück.
                this.fenster.style.bottom = 'auto';
            },
            { beginn: () => { start = this.fenster.getBoundingClientRect(); },
              ausser: '.floating-video-close' });
    }

    groesse() {
        let start = null;
        Ziehgriff.an(document.getElementById('floatingVideoResize'),
            (dx, dy) => {
                this.fenster.style.width =
                    Math.max(Videofenster.MIN_BREITE, start.breite + dx) + 'px';
                this.fenster.style.height =
                    Math.max(Videofenster.MIN_HOEHE, start.hoehe + dy) + 'px';
            },
            { beginn: () => {
                start = { breite: this.fenster.offsetWidth,
                          hoehe: this.fenster.offsetHeight };
              },
              stoppen: true });
    }
}
