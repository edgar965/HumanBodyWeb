import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshpfadliste } from '../mesh/meshpfadliste.js';
import { Exportleisteexport } from './exportleisteexport.js';
import { Exportleistefigur } from './exportleistefigur.js';
import { Exportleisteregler } from './exportleisteregler.js';
import { Exportleisterender } from './exportleisterender.js';

/**
 * Exportleiste — Modell speichern, Export (GLB, OBJ, Blender, mit oder ohne Animation und Audio), Render mit den Reglern für Rendering und Physik, Pfade (31.10.2026).
 *
 * Edgar: „baue die ganze Exportleiste auf mit Physik usw." (Vorbild: die rechte Spalte von „2D3D Kleider"), „mach das als wiederverwendbares Modul". Markup `_exportleiste.html`,
 * Server `core/api/exportleiste.py`. Die Seite gibt eine Quelle:
 *
 *     Exportleiste.starten(document.getElementById('exportleiste'), {
 *         modell: async ({ bvh }) => ({ inst, figur, regler, hoehe_m }),   // die Figur der Seite (Genesis9Modell, voll gebaut, mit ihren Stücken); `bvh` = Vorgabe des Bereichs
 *         bvh: () => 'Kategorie/Name',                                      // Vorschlag für die Animation (optional; z. B. die Standardanimation der Seite)
 *     });
 *
 * Der Zustand kommt vom Server (Exportordner, Ton-Vorgabe, Regler, Render, Pfade); solange ein Render läuft, alle `TAKT_MS` neu. Ändert die Seite ihren BVH-Vorschlag, holt die
 * Leiste Pfad und Länge dieser BVH (der Render braucht die Länge als Obergrenze).
 */
export class Exportleiste {

    static TAKT_MS = 2000;
    static RUHE_TAKTE = 5;

    static starten(wurzel, quelle) {
        if (!wurzel) throw new Error('Exportleiste: kein Behälter #exportleiste auf der Seite');
        const leiste = new Exportleiste(wurzel, quelle);
        window.__exportleiste = leiste;
        leiste.laden();
        setInterval(() => leiste._takt(), Exportleiste.TAKT_MS);
        return leiste;
    }

    constructor(wurzel, quelle) {
        this.wurzel = wurzel;
        this.quelle = quelle;
        this.basis = wurzel.dataset.adresse;
        this.zustand = null;
        this.figur = new Exportleistefigur(quelle, () => this.zustand?.bvh_vorgabe || '', () => !!this.zustand?.eigenes_modell);
        this.export = new Exportleisteexport(this);
        this.render = new Exportleisterender(this);
        this.regler = new Exportleisteregler(this);
        this.pfade = wurzel.querySelector('#exportleiste-pfade');
        this._vorschlag = null;
        this._laedt = false;
    }

    adresse(teil = '') {
        return this.basis + teil;
    }

    /** Die BVH, nach der der Zustand fragt: was im Feld steht, sonst der Vorschlag der Seite. */
    bvh() {
        return this.export.bvhWert() || this._vorschlag || '';
    }

    async laden() {
        if (this._laedt) return;
        this._laedt = true;
        try {
            const bvh = this.bvh();
            this.zustand = await Serverabruf.json(this.adresse(bvh ? `?bvh=${encodeURIComponent(bvh)}` : ''));
            this.export.zeigen(this.zustand);
            this.regler.zeigen(this.zustand);
            this.render.zeigen(this.zustand);
            Meshpfadliste.zeichnen(this.pfade, this.zustand.pfade);
        } catch (fehler) {
            this.export.melden(`Exportleiste nicht geladen: ${fehler.daten?.error || fehler.message}`, true);
        } finally {
            this._laedt = false;
        }
    }

    /** Neuer BVH-Vorschlag der Seite → neu laden; läuft ein Render → neu laden (Fortschritt). */
    _takt() {
        if (document.visibilityState === 'hidden') return;
        let vorschlag = null;
        try { vorschlag = this.quelle.bvh?.() || null; } catch (fehler) { console.warn('Exportleiste: Vorschlag der BVH nicht lesbar', fehler); }
        if (vorschlag !== this._vorschlag) {
            this._vorschlag = vorschlag;
            this.export.vorschlagGeaendert();
            this.laden();
            return;
        }
        // Läuft ein Render: jeden Takt; sonst alle `RUHE_TAKTE` — so sieht die Seite auch einen Render, den ein anderer Tab gestartet hat (31.10.2026, Venus: „läuft schon“ ohne Anzeige)
        this._ruhe = (this._ruhe || 0) + 1;
        if (this.zustand?.render?.status === 'laeuft' || this._ruhe >= Exportleiste.RUHE_TAKTE) {
            this._ruhe = 0;
            this.laden();
        }
    }
}
