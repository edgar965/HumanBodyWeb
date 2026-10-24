/**
 * Ai2d3dliste — die Tabellen auf `/2d-3d-AI/` (24.10.2026, wie `Mesh3dailiste`): ein Klick auf eine Zeile öffnet die Seite des Jobs (`/2d-3d-AI/<job>/`) bzw. im Reiter „Test“ die des Tests
 * (`/2d-3d-AI/test/<kennung>/`). Der erste Link der Zeile trägt die Adresse; Links, Knöpfe und Kästchen behalten ihr eigenes Verhalten.
 */
export class Ai2d3dliste {
    static aufbauen() {
        const tabellen = [...document.querySelectorAll('table.ai2d3dtabelle')];
        for (const tabelle of tabellen) tabelle.addEventListener('click', e => Ai2d3dliste.geklickt(e));
        return tabellen;
    }

    static geklickt(e) {
        if (e.target.closest('a, button, input, select')) return;
        const zeile = e.target.closest('tr[data-id]');
        const ziel = zeile?.querySelector('a[href^="/2d-3d-AI/"]')?.getAttribute('href');
        if (ziel) window.location.href = ziel;
    }
}
