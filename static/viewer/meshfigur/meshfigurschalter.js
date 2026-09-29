/**
 * Meshfigurschalter — die Kästchen über der 3D-Ansicht (29.09.2026, Edgar: „mach toggle Boxen oben in
 * der 3D View: Mesh, Haare, Kleider, Nebeneinander, 3DModell. Default: 3DModell, Haar, Kleider aktiviert").
 *
 * Bis dahin waren es drei Auswahlknöpfe (Figur | Netz | Nebeneinander) — also sich ausschließende Zustände.
 * Jetzt ist jeder Teil der Bühne einzeln schaltbar; welche beim Öffnen leuchten, steht im Template
 * (Klasse `active`), nicht hier, damit die Vorgabe an EINER Stelle liegt.
 *
 * Die Knöpfe stehen im HTML und tragen `data-schalter="<schluessel>"`; diese Klasse bindet sie nur.
 * Stil: `css/schaltknoepfe.css` (Edgars Vorlage war die Werkzeugleiste im Theatre).
 *
 * KEIN Knopf wird gesperrt (Edgar, 29.09.2026: „MACH NEBENEINANDER!"). Eine erste Fassung sperrte, was
 * gerade nichts zu schalten hatte — das stand dem Bedienen im Weg, statt zu helfen: „Nebeneinander"
 * verlangte, dass man vorher selbst „Mesh" einschaltet, statt es einfach zu tun.
 */
export class Meshfigurschalter {

    static SCHLUESSEL = ['mesh', 'haare', 'kleider', 'nebeneinander', 'modell'];

    constructor(geaendert) {
        this.geaendert = geaendert;
        this.felder = {};
        for (const schluessel of Meshfigurschalter.SCHLUESSEL) {
            const knopf = document.querySelector(`button[data-schalter="${schluessel}"]`);
            if (!knopf) continue;
            this.felder[schluessel] = knopf;
            knopf.addEventListener('click', () => {
                knopf.classList.toggle('active');
                this.geaendert();
            });
        }
    }

    /** Was JETZT leuchtet. */
    get stand() {
        const stand = {};
        for (const schluessel of Meshfigurschalter.SCHLUESSEL) {
            stand[schluessel] = Boolean(this.felder[schluessel]?.classList.contains('active'));
        }
        return stand;
    }

    /** Einen Knopf von der Bühne aus setzen — „Nebeneinander" schaltet so „Mesh" mit an. */
    setzen(schluessel, an) {
        this.felder[schluessel]?.classList.toggle('active', an);
    }
}
