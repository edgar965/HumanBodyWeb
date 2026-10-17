/**
 * Mesh3dailiste — die Tabellen auf `/mesh-3D-AI/` (14.10.2026): ein Klick auf eine Zeile öffnet die Seite des Jobs (`/mesh-3D-AI/<job>/`) bzw. seit 16.10.2026 im Reiter „Test“ die Seite
 * des Tests (`/mesh-3D-AI/test/<kennung>/`). Der Link in der Zeile trägt die Adresse; ein Klick auf den Link selbst läuft ohne Zutun des Moduls.
 */
export class Mesh3dailiste {
    static aufbauen() {
        const tabellen = [...document.querySelectorAll('table.mesh3daitabelle')];
        for (const tabelle of tabellen) tabelle.addEventListener('click', e => Mesh3dailiste.geklickt(e));
        return tabellen;
    }

    static geklickt(e) {
        if (e.target.closest('a, button, input, select')) return;
        const zeile = e.target.closest('tr[data-id]');
        if (zeile) window.location.href = zeile.querySelector('a[href^="/mesh-3D-AI/"]')?.getAttribute('href') || `/mesh-3D-AI/${zeile.dataset.id}/`;
    }
}
