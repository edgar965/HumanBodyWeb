/**
 * Recherchekategorien — die Kategorien über der Recherche-Tabelle als Schalter (06.10.2026).
 *
 * Edgar: „baue die als toggles um, selektieren zeigt nur die, mit Button ‚Alle Selektieren' / ‚Alle abwählen'". Jede Kategorie ist ein Knopf (`button.rc-chip[data-kategorie]`,
 * `aria-pressed` = gewählt); die Tabelle zeigt nur die Zeilen, deren Kategorie gewählt ist. Zu Beginn sind alle gewählt. Ausgeblendet wird mit einer Klasse an der Zeile
 * (`rc-zeile-aus`), nicht durch Entfernen: Die Sortierung (djangoBase) hängt die Zeilen nur um, die Klasse bleibt dabei an ihnen. Die Kategorie einer Zeile steht in
 * `td.rc-kategoriezelle` (Spalte „Kategorie").
 */
export class Recherchekategorien {

    static AUS = 'rc-zeile-aus';

    constructor(leiste, tabelle) {
        this.leiste = leiste;
        this.tabelle = tabelle;
    }

    /** Bindet die Leiste `#rc-kategorien` an die Tabelle (Ereignisdelegation: ein Horcher für Knöpfe und Schalter). */
    static binden(tabelle) {
        const leiste = document.getElementById('rc-kategorien');
        if (leiste && tabelle) new Recherchekategorien(leiste, tabelle).binden();
    }

    binden() {
        this.leiste.addEventListener('click', (e) => {
            const ziel = e.target instanceof Element ? e.target : null;
            if (!ziel) return;
            const schalter = ziel.closest('button.rc-chip[data-kategorie]');
            if (schalter) {
                schalter.setAttribute('aria-pressed', String(schalter.getAttribute('aria-pressed') !== 'true'));
                this.anwenden();
            } else if (ziel.closest('#rc-kat-alle')) {
                this.alle(true);
            } else if (ziel.closest('#rc-kat-keine')) {
                this.alle(false);
            }
        });
    }

    schalter() {
        return [...this.leiste.querySelectorAll('button.rc-chip[data-kategorie]')];
    }

    alle(gewaehlt) {
        for (const s of this.schalter()) s.setAttribute('aria-pressed', String(gewaehlt));
        this.anwenden();
    }

    /** Blendet jede Zeile ein oder aus, je nachdem, ob ihre Kategorie gewählt ist. */
    anwenden() {
        const gewaehlt = new Set(this.schalter().filter((s) => s.getAttribute('aria-pressed') === 'true').map((s) => s.dataset.kategorie));
        for (const zeile of this.tabelle.tBodies[0].rows) {
            const zelle = zeile.querySelector('td.rc-kategoriezelle');
            if (zelle) zeile.classList.toggle(Recherchekategorien.AUS, !gewaehlt.has(zelle.textContent.trim()));
        }
    }
}
