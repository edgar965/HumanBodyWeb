/**
 * Fotogenesisliste — die Tabellen auf `/foto-genesis/` (24.10.2026, wie `Meshgenesisliste`): ein Klick auf eine Zeile öffnet die Seite des Jobs (`/foto-genesis/<job>/`) bzw. im Reiter „Test“ die des Tests
 * (`/foto-genesis/test/<kennung>/`). Der erste Link der Zeile trägt die Adresse; Links, Knöpfe und Kästchen behalten ihr eigenes Verhalten.
 */
export class Fotogenesisliste {
    static aufbauen() {
        const tabellen = [...document.querySelectorAll('table.fotogenesistabelle')];
        for (const tabelle of tabellen) tabelle.addEventListener('click', e => Fotogenesisliste.geklickt(e));
        return tabellen;
    }

    static geklickt(e) {
        if (e.target.closest('a, button, input, select')) return;
        const zeile = e.target.closest('tr[data-id]');
        const ziel = zeile?.querySelector('a[href^="/foto-genesis/"]')?.getAttribute('href');
        if (ziel) window.location.href = ziel;
    }
}
