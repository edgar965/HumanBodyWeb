/**
 * Engine2d3dKleidermeshkarte — der Abschnitt „Mesh" direkt unter den Bildern, wie das Interface des Hugging-Face-Space
 * „microsoft/TRELLIS.2" (02.10.2026).
 *
 * Edgar: „mesh generierung möchte ich optional getrennt machen vom nächsten Schritt … das UI für Mesh bitte direkt unter den
 * Bildern so wie das UI von der Hugging face seite". Die Regler baut `Meshoptionenformular` aus der Gruppe `mesh` des Katalogs
 * (Resolution, Seed, Randomize Seed, Decimation Target, Texture Size, darunter zugeklappt „Advanced Settings" mit den drei
 * Stufen); diese Klasse setzt den Knopf dazwischen, an dieselbe Stelle wie der Space („Generate" steht über den Advanced
 * Settings). „Mesh erzeugen" rechnet NUR den Schritt „Netz" (`ab = bis = netz`); die übrigen Schritte starten danach einzeln
 * über „ab"/„bis" in der Laufleiste.
 */
export class Engine2d3dKleidermeshkarte {

    constructor(seite) {
        this.seite = seite;
        const behaelter = document.getElementById('engine2d3dkleider-optionen-mesh');
        const zeile = document.createElement('div');
        zeile.className = 'engine2d3dkleider-mesh-erzeugen';
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.id = 'mesh-erzeugen';
        this.knopf.className = 'btn btn-primary';
        this.knopf.title = 'Rechnet nur den Schritt „Netz" (Fotos → Netz mit TRELLIS.2). Körper, Grundfigur und die übrigen ' +
            'Schritte starten danach einzeln: „ab" und „bis" in der Laufleiste oben.';
        this.knopf.innerHTML = '<i class="fas fa-cube"></i> <span>Mesh erzeugen</span>';
        const hinweis = document.createElement('span');
        hinweis.className = 'hb-hinweis';
        hinweis.textContent = 'Nur der Schritt „Netz" — die nächsten Schritte starten getrennt.';
        zeile.append(this.knopf, hinweis);
        // Vor „Advanced Settings", wie im Space; ohne zugeklappten Bereich ans Ende.
        behaelter.insertBefore(zeile, behaelter.querySelector('details'));
        this.knopf.addEventListener('click', () => seite.starten('netz', 'netz', this.knopf));
    }

    zeigen(z) {
        this.knopf.disabled = !!z.laeuft;
        this.knopf.querySelector('span').textContent = z.laeuft ? 'Berechnet …' : 'Mesh erzeugen';
    }
}
