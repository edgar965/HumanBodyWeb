/**
 * Keyframeliste — die Liste der gesetzten Schlüsselbilder.
 *
 * Herausgelöst aus `keyframe-ui.js` (319 Zeilen). Die Zeilen werden bei jedem
 * Zeichnen NEU gebaut, deshalb müssen auch die Lösch-Zuhörer jedes Mal neu
 * angemeldet werden — ein Zuhörer auf dem Behälter wäre sparsamer, aber die
 * Liste ist kurz, und so bleibt die Zuordnung Zeile → Kennung offensichtlich.
 */
export class Keyframeliste {

    static BEHAELTER = 'kf-keyframes';
    static LEER = 'No keyframes yet';

    constructor(beimLoeschen) {
        this.beimLoeschen = beimLoeschen;
    }

    zeichnen(schluesselbilder) {
        const behaelter = document.getElementById(Keyframeliste.BEHAELTER);
        if (!behaelter) return;
        if (schluesselbilder.length === 0) {
            behaelter.innerHTML =
                `<div class="kf-leer">${Keyframeliste.LEER}</div>`;
            return;
        }
        behaelter.innerHTML = schluesselbilder
            .map(bild => Keyframeliste._zeile(bild)).join('');
        behaelter.querySelectorAll('.kf-delete').forEach(knopf => {
            knopf.addEventListener('click', ereignis => {
                this.beimLoeschen(parseInt(ereignis.currentTarget.dataset.id));
            });
        });
    }

    static _zeile(bild) {
        return `
            <div class="kf-item" data-id="${bild.id}">
                <div>
                    <div class="kf-item-name">${bild.objectName}</div>
                    <div class="kf-item-zeit">${bild.time.toFixed(2)}s</div>
                </div>
                <button class="kf-delete" data-id="${bild.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
    }
}
