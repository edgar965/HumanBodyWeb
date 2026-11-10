/**
 * Meshgenesisliste — die Tabellen auf `/mesh-genesis/` (14.10.2026): ein Klick auf eine Zeile öffnet die Seite des Jobs (`/mesh-genesis/<job>/`) bzw. seit 16.10.2026 im Reiter „Test“ die Seite
 * des Tests (`/mesh-genesis/test/<kennung>/`). Der Link in der Zeile trägt die Adresse; ein Klick auf den Link selbst läuft ohne Zutun des Moduls.
 */
export class Meshgenesisliste {
    static aufbauen() {
        const tabellen = [...document.querySelectorAll('table.meshgenesistabelle')];
        for (const tabelle of tabellen) tabelle.addEventListener('click', e => Meshgenesisliste.geklickt(e));
        return tabellen;
    }

    static geklickt(e) {
        if (e.target.closest('a, button, input, select')) return;
        const zeile = e.target.closest('tr[data-id]');
        if (zeile) window.location.href = zeile.querySelector('a[href^="/mesh-genesis/"]')?.getAttribute('href') || `/mesh-genesis/${zeile.dataset.id}/`;
    }
}
