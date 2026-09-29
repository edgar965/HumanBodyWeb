import { Meshfigurhaarobjekt } from './meshfigurhaarobjekt.js';

/**
 * Meshfigurkleider — die Kleidung der Figur ein- und ausblenden (Kästchen „Kleider", 29.09.2026).
 *
 * ZWEI Quellen, ein Schalter:
 *   * Das Kleidungsobjekt aus dem Netz (`ergebnis/kleidung.glb`, Schritt „kleidung"): Shirt, Hose, Socken der
 *     Person, in die Ruhelage der Figur zurückgerechnet — wie das Haar aus dem Netz ein eigenes Objekt in der
 *     Gruppe der Figur (dieselbe Klasse, `Meshfigurhaarobjekt`; sie ist nicht auf Haar beschränkt).
 *   * Getragene Stücke der Garderobe (`Genesis9Modell.clothMeshes`, Kennung → Netz). Die FRISUR ist dort ebenfalls
 *     ein Stück der Garderobe — sie gehört aber zum Kästchen „Haare" (`Meshfigurhaarwahl`), also lässt diese Klasse
 *     alle Schlüssel der Frisurkennung liegen und fasst nur den Rest an.
 *
 * SICHTBAR JE NETZ, NICHT JE GRUPPE — aus demselben Grund wie beim Haar (`meshfigurhaarobjekt.js`):
 * `Modellexportinhalt.objekte` fragt `mesh.visible`, eine bloß ausgeblendete Gruppe ginge mit in die GLB.
 * Damit gilt das Kästchen auch für den Export.
 */
export class Meshfigurkleider {

    constructor(seite, melden) {
        this.modell = null;
        this.kennung = null;
        this.an = true;
        this.netz = new Meshfigurhaarobjekt(seite, melden,
                                            { name: 'Kleidung aus dem Netz', datei: e => (e.kleidung || {}).objekt });
    }

    /** Das Objekt laden, wenn sich die Datei geändert hat; `gruppe` = die Gruppe der Figur (oder null). */
    zeigen(z, gruppe) {
        this.netz.zeigen(z, gruppe);
        this.anwenden();
    }

    /** Nach jedem Neubau der Figur: das Objekt hängt sich in ihre neue Gruppe. */
    anhaengen(modell) {
        this.netz.anhaengen(modell.group);
        this.anwenden();
    }

    /** Modell und Kennung der Frisur nachziehen — die Netze der Stücke kommen nach dem Bau nach. */
    setzen(modell, frisurkennung) {
        this.modell = modell;
        this.kennung = frisurkennung || null;
        this.anwenden();
    }

    /** Die Schlüssel aller getragenen Stücke AUSSER der Frisur. */
    get stuecke() {
        const alle = Object.keys(this.modell?.clothMeshes || {});
        if (!this.kennung) return alle;
        return alle.filter(schluessel => !schluessel.startsWith(`${this.kennung}/`));
    }

    get vorhanden() { return this.stuecke.length > 0 || this.netz.vorhanden; }

    sichtbar(an) {
        this.an = an;
        this.anwenden();
    }

    anwenden() {
        const netze = this.modell?.clothMeshes || {};
        for (const schluessel of this.stuecke) {
            netze[schluessel]?.traverse(o => { if (o.isMesh) o.visible = this.an; });
        }
        this.netz.sichtbar(this.an);
    }
}
