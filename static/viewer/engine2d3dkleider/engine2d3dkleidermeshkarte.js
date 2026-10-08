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

    /** Die KI des Schritts „Netz" (Option `mesh.modell`) — die Namen der Auswahl in der Liste und im Feld „Modell" dieser Karte. */
    static KI = {
        trellis2: 'TRELLIS.2', pixal3d: 'Pixal3D', pixal3d_mv: 'Pixal3D Mehrbild', hunyuan3d_2: 'Hunyuan3D-2.0', hunyuan3d_2mv: 'Hunyuan3D-2mv',
    };

    static ki(z) {
        return Engine2d3dKleidermeshkarte.KI[z?.optionen?.mesh?.modell] || Engine2d3dKleidermeshkarte.KI.trellis2;
    }

    /** Der Name eines Schritts in der Laufleiste und in „ab"/„bis": „Netz" trägt die gewählte KI (vorher fest „TRELLIS"). `standard` = der feste Name. */
    static schrittname(schritt, z, standard) {
        return schritt === 'netz' ? `Netz (${Engine2d3dKleidermeshkarte.ki(z)})` : standard;
    }

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
        // Überschrift, Knopf und Schrittauswahl nennen die gewählte KI, nicht fest TRELLIS.2.
        const ki = Engine2d3dKleidermeshkarte.ki(z);
        const titel = document.getElementById('engine2d3dkleider-ki');
        if (titel) titel.textContent = ki;
        this.knopf.title = `Rechnet nur den Schritt „Netz" (Fotos → Netz mit ${ki}). Körper, Grundfigur und die übrigen ` +
            'Schritte starten danach einzeln: „ab" und „bis" in der Laufleiste oben.';
        for (const wahl of document.querySelectorAll('#ab-schritt option[value="netz"], #bis-schritt option[value="netz"]')) {
            wahl.textContent = Engine2d3dKleidermeshkarte.schrittname('netz', z);
        }
    }
}
