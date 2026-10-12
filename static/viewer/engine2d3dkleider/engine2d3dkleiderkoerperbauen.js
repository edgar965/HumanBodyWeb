/**
 * Engine2d3dKleiderkoerperbauen — die Karte „Genesis-Modell" auf der Auftragsseite von „2D3D Kleider" (11.10.2026).
 *
 * Edgar: „bei den jobs … brauche ich einen Button um den letzten Schritt einzeln zu bauen — also das Genesis Modell aus dem Mesh"
 * und danach: „da sollte der Button sein" — nach der Karte „Kleiderstücke", wie die Knöpfe der anderen Schritte. Der Knopf rechnet NUR
 * die Schritte `koerper` und `grundfigur` (`ab = koerper`, `bis = grundfigur`); gesperrt ist er wie die anderen Schrittknöpfe, solange
 * ein Lauf rechnet (`Knopfsperre` in `Engine2d3dKleiderseite.starten`).
 */
export class Engine2d3dKleiderkoerperbauen {

    static SCHRITTE = ['koerper', 'grundfigur'];

    constructor(seite) {
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.id = 'koerper-bauen';
        this.knopf.className = 'btn btn-primary btn-sm';
        this.knopf.title = 'Rechnet nur die Schritte „Körper“ und „Grundfigur“: das Genesis-Modell aus dem Netz der Fotos. Kleiderstücke und Iterationen laufen nicht mit.';
        this.knopf.innerHTML = '<i class="fas fa-cube"></i> <span>Genesis-Modell bauen</span>';
        this.knopf.addEventListener('click', () => seite.starten('koerper', 'grundfigur', this.knopf));
        document.getElementById('koerper-bauen-zeile').append(this.knopf);
    }

    zeigen(z) {
        this.knopf.disabled = !!z.laeuft;
        const baut = z.laeuft && Engine2d3dKleiderkoerperbauen.SCHRITTE.includes(z.schritt);
        this.knopf.querySelector('span').textContent = baut ? 'Berechnet …' : 'Genesis-Modell bauen';
    }
}
