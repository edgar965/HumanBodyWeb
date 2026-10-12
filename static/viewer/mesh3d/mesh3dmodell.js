/**
 * Mesh3dmodell — die Karte „Genesis-Modell“ (Schritt „Modell“) der Jobseite „Mesh-3D“ (11.10.2026): Name des gespeicherten Modells und wo man es findet.
 *
 * Das Modell (`data/models/<Name>.json`: Regler, Stücke, Haut, Augen) steht in der Szene unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle“.
 */
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3dmodell {

    constructor() {
        this.zahlen = document.getElementById('modell-zahlen');
        this._stand = '';
    }

    zeigen(z) {
        if (!Mesh3danzeige.geaendert(this, '_stand', [z.modell, z.status])) return;
        const m = z.modell;
        if (!m) {
            Mesh3danzeige.leer(this.zahlen, z.status === 'fertig' ? 'Kein Modell gespeichert.' : 'Noch kein Modell — der Schritt „Modell“ läuft zuletzt.');
            return;
        }
        Mesh3danzeige.zeilen(this.zahlen, [
            `Gespeichert als „${m.name}“ — in der Szene: Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle.`,
            m.daz ? `Daz-Fassung: ${typeof m.daz === 'object' ? JSON.stringify(m.daz) : m.daz}` : null,
        ]);
        const zeile = document.createElement('div');
        zeile.className = 'hb-hinweis';
        const verweis = document.createElement('a');
        verweis.href = '/Charakter/';
        verweis.target = '_blank';
        verweis.textContent = 'Charakter-Editor öffnen';
        zeile.appendChild(verweis);
        this.zahlen.appendChild(zeile);
    }
}
