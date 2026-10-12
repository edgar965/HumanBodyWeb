/**
 * Mesh3diterationen — der Reiter „Iterationen“ der Jobseite „Mesh-3D“: ein Vorschlag, noch nicht angeschlossen (11.10.2026).
 *
 * Edgar (11.10.2026): „Iterationen mit Renderbildern des Meshes als Vorlagen.“ Gemeint ist der Kreislauf von „2D3D Kleider“ — jede Runde rendert das Modell (Figur mit
 * Kleidern und Haar) aus den Blickwinkeln der Vorlagen und misst die Abweichung — mit dem Unterschied, dass die Vorlagen hier keine Fotos sind, sondern Renderings
 * des Meshes aus exakt bekannten Kameras (vorn 0°, links 90°, rechts −90°, hinten 180°, dazu die vier Schrägen). Der Reiter zeigt, wie er aussehen soll; der Schritt
 * fehlt im Lauf (Konzept `Docu/konzepte/2026-10-11_mesh-3d-konzept.md`, Stufe 3).
 */
export class Mesh3diterationen {

    static TEXT = [
        ['Vorlagen', 'Renderings des Meshes aus bekannten Kameras (Schritt „Ansichten“), mit Alpha aus der Tiefenkarte — eine Reihe von vier bis acht Bildern, je mit Blickwinkel und Gewicht. Sie ersetzen die Fotos von „2D3D Kleider“; eine Blickwinkelschätzung entfällt.'],
        ['Runden', 'Tabelle wie bei „2D3D Kleider“: Nummer, Abweichung (Umriss und Farbe gegen die Vorlage), Rezept, Kommentar, Vergleichstafel Vorlage ↔ Render; Runden lassen sich wählen, ausdünnen und löschen.'],
        ['Begutachtung', 'Rezept (Aufrufe an das Modell: Kleider, Haar, Passform, Farben) und Kommentar je Runde; „Runde rechnen“ und „Automatisch“ wie dort.'],
        ['Was sie messen', 'Die Treue zum MESH, nicht zur Person: wo das Mesh die Person falsch zeigt, wird das Modell dem Fehler treu. Beim Weg mit getrennten Teilen sind Kleider und Haar schon das Original — die Iterationen stellen nur noch nach.'],
    ];

    constructor() {
        const ziel = document.getElementById('iterationen-karte');
        const titel = document.createElement('h2');
        titel.textContent = 'Iterationen — Vorschlag';
        const hinweis = document.createElement('p');
        hinweis.className = 'hb-hinweis mesh3d-warnung';
        hinweis.textContent = 'Noch nicht angeschlossen: Der Lauf hat diesen Schritt nicht. So soll der Reiter aussehen, sobald er gebaut ist.';
        const liste = document.createElement('dl');
        for (const [kopf, text] of Mesh3diterationen.TEXT) {
            const dt = document.createElement('dt');
            dt.textContent = kopf;
            const dd = document.createElement('dd');
            dd.className = 'hb-hinweis';
            dd.textContent = text;
            liste.append(dt, dd);
        }
        ziel.append(titel, hinweis, liste);
    }

    zeigen() { /* nichts zu zeigen: der Reiter ist ein Vorschlag */ }
}
