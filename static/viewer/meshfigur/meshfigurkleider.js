import { Hautverdeckung } from '../gemeinsam/hautverdeckung.js';
import { Meshfighaut } from './meshfighaut.js';
import { Meshfighautstueck } from './meshfighautstueck.js';
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

    /** Schlüssel, unter dem das Kleidungsobjekt der Haut-Verdeckung gemeldet wird (`Figurhaut.stuecke`). */
    static HAUTSTUECK = 'mesh3d_kleidung';

    constructor(seite, melden) {
        this.modell = null;
        this.kennung = null;
        this.an = true;
        this._hautStand = null;
        this._hautGeometrie = null;
        this._hautStueck = null;
        this.netz = new Meshfigurhaarobjekt(seite, melden,
                                            { name: 'Kleidung aus dem Netz', datei: e => (e.kleidung || {}).objekt });
        // An die Haltung gebunden (`Meshfigurhaarobjekt`): das Netz wird erst später (Haltung gerechnet) zum `SkinnedMesh` — dann muss die Haut-Verdeckung es neu melden.
        this.netz.gebunden = () => { this._hautStand = null; this.anwenden(); };
    }

    /** Das Objekt laden, wenn sich die Datei geändert hat; `gruppe` = die Gruppe der Figur (oder null); `haltung`: die Figur steht in der Haltung des Netzes (`Meshfigurhaarobjekt`). */
    zeigen(z, gruppe, haltung = false) {
        this.netz.zeigen(z, gruppe, haltung);
        this.anwenden();
    }

    /** Nach jedem Neubau der Figur: das Objekt hängt sich in ihre neue Gruppe. */
    anhaengen(modell) {
        this.netz.anhaengen(modell.group, modell.skelett, modell);
        this.anwenden();
    }

    /** Modell und Kennung der Frisur nachziehen — die Netze der Stücke kommen nach dem Bau nach. */
    setzen(modell, frisurkennung) {
        if (modell !== this.modell) this._hautStand = null;         // eine neue Figur kennt das gemeldete Stück noch nicht
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
        this._hautMelden();
    }

    /**
     * Das Kleidungsobjekt der Haut-Verdeckung melden (14.10.2026): wie in Charakter und Studio fehlt die Haut dort, wo ein Stück sie verdeckt — sonst
     * kommt sie bei Bewegung und Gelenkkorrekturen durch den anliegenden Stoff (Ballerina: Hüftansatz). Das Netz wechselt, wenn die Hautdatei gebunden
     * ist (`Meshfighaut._umwandeln`), und die Sichtbarkeit mit dem Kästchen „Kleider“ — beides ändert den Stand und stößt die Maske neu an; ein
     * ausgeblendetes Stück verdeckt nichts (`Hautverdeckung.zaehlt`).
     */
    _hautMelden() {
        const modell = this.modell;
        if (!modell) return;
        const netz = this._netz();
        const geometrie = netz?.geometry?.index ? netz.geometry : null;
        // Ein Netz in der Haltung (Mesh-3D, `Meshfighaut._an_die_haltung`) liegt im Raum der Haltung, die Maske vergleicht in der Ruhelage: ohne die Bindung gibt es noch keine brauchbaren Punkte.
        const haltung = Boolean(netz?.userData?.haltungsbindung);
        const unfertig = this.netz._drehung && !haltung;
        const stand = geometrie && !unfertig ? `${netz.uuid}|${netz.visible}|${netz.userData?.bindung || 0}` : null;
        if (stand === this._hautStand) return;
        this._hautStand = stand;
        if (geometrie && !unfertig && (this._hautGeometrie !== geometrie || haltung)) {          // dieselbe Geometrie nach dem Binden: nicht noch einmal verschweißen
            this._hautGeometrie = geometrie;
            this._hautStueck = new Meshfighautstueck(geometrie, () => this._netz(), haltung ? Meshfighaut.ruheposition(netz, modell.skelett) : null);
        }
        if (unfertig) { modell.hautStuecke = {}; Hautverdeckung.planen(modell); return; }
        modell.hautStuecke = geometrie ? { [Meshfigurkleider.HAUTSTUECK]: this._hautStueck } : {};
        Hautverdeckung.planen(modell);
    }

    /** Das Netz des Kleidungsobjekts, wie es gerade in der Szene steht (vor dem Binden ein `Mesh`, danach ein `SkinnedMesh`). */
    _netz() {
        return this.netz.objekt ? Meshfighaut.netze(this.netz.objekt)[0] || null : null;
    }
}
