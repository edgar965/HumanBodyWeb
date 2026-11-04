/**
 * Ai2d3dsteuerung — die Bedienleiste im festen Block der Seite „2d-3d-AI“ (24.10.2026): Perspektive (ein Knopf je Foto), Ansichtsart (dieselben wie Mesh3D-AI, `Mesh3daimaterial.MODI`),
 * Genesis-Modell „Ergebnis“ | „Wahrheit“ (nur Exporte), die Schalter „Kleider“ und „Rig“ (nur Tests), Netz Hunyuan3D-2mv | Tripo3D (nur, wenn es beide gibt). Die Leiste hält den Zustand; Änderungen meldet sie an `geaendert(was)`.
 * Knöpfe und Zustand: `Ai2d3dschalterleiste` (seit 04.11.2026 gemeinsam mit den Leisten der Zeilen, `Ai2d3dzeilenleiste` — eine Zeile mit eigener Leiste folgt dieser hier nicht mehr).
 * Seit 04.11.2026 auch „Normale“ und „Netz farbig“ der Zeilenleisten (Edgar: „mach auch „Normale“ und „Netz farbig“ für genesis“, `Ai2d3dansichtsart`): gewählt wird `ansicht`; die Zeichner
 * bekommen `modus` (ihre Ansichtsart, für die beiden „Textur“), die Felder `art` (`Ai2d3dansicht.seitenart`, sie tauschen dann beim Rendern die Materialien).
 */
import { Mesh3daimaterial } from '../mesh3dai/mesh3daimaterial.js';
import { Ai2d3dansichtsart } from './ai2d3dansichtsart.js';
import { Ai2d3dschalterleiste } from './ai2d3dschalterleiste.js';

export class Ai2d3dsteuerung extends Ai2d3dschalterleiste {
    /** Arten, die für ein Netz als EIN Material keinen Sinn haben, fehlen hier (Punkte, Oberfläche + Drahtnetz — `Ai2d3dnetz.ersatz` würde sie auf „Oberfläche“ setzen). */
    static MODI = Mesh3daimaterial.MODI.filter(m => m.schluessel !== 'punkte' && m.schluessel !== 'oberflaeche_draht');
    static ICONS = { normale: 'fa-compass', netzfarbe: 'fa-fill-drip' };

    /** Die Knöpfe der Ansicht: die von Mesh3D-AI, hinter „Textur“ die beiden getauschten Arten der Zeilenleisten. */
    static ansichten() {
        const zusatz = Ai2d3dansichtsart.ARTEN.filter(a => Ai2d3dansichtsart.getauscht(a.wert))
            .map(a => ({ wert: a.wert, text: a.text, titel: a.titel, icon: Ai2d3dsteuerung.ICONS[a.wert] }));
        const liste = Ai2d3dsteuerung.MODI.map(m => ({ wert: m.schluessel, text: m.name, titel: m.hinweis, icon: m.icon }));
        const nach = liste.findIndex(e => e.wert === 'textur') + 1;
        return [...liste.slice(0, nach), ...zusatz, ...liste.slice(nach)];
    }

    /** @param {HTMLElement} leiste @param {object} daten Seitendaten @param {(was: string) => void} geaendert */
    constructor(leiste, daten, geaendert) {
        super(leiste, geaendert);
        this.foto = Math.max(0, daten.fotos.findIndex(f => f.winkel === 0));
        this.ansicht = 'textur';
        this.quelle = 'ausgabe';
        this.kleider = true;
        this.rig = false;
        this.netz = 0;
        this.ausschnitt = 'koerper';
        this._gruppe('Perspektive', daten.fotos.map(f => ({ wert: f.nr, text: f.winkel === null ? `${f.name} (?)` : f.name, titel: f.winkel === null ? 'Winkel unbekannt' : `${f.winkel}°` })), 'foto');
        this._gruppe('Ausschnitt', [{ wert: 'koerper', text: 'Ganzer Körper', titel: 'Netz und Genesis-Modell ganz' },
            { wert: 'kopf', text: 'Kopf', titel: 'Netz und Genesis-Modell: nur der Kopf (gekoppelt, ziehen dreht beide)' }], 'ausschnitt');
        this._gruppe('Ansicht', Ai2d3dsteuerung.ansichten(), 'ansicht');
        if (daten.genesis && daten.wahrheit) {
            this._gruppe('Genesis-Modell', [{ wert: 'ausgabe', text: 'Ergebnis', titel: 'Was die KI aus den Eingaben macht (heute: Mesh3D-AI aus dem Tripo-Netz)' },
                { wert: 'soll', text: 'Wahrheit', titel: 'Die Figur, aus der die Fotos gerendert sind — Gegenprobe des Vergleichs' }], 'quelle');
        }
        // Ein Schalter statt „an | aus“ (24.10.2026, Edgar: „mach … einen einzigen Kleider Toggle“): gedrückt = Kleider und Haar zu sehen
        this._schalter('Kleider', 'kleider', 'Kleider und Haar zeigen (aus: nur der Körper)', 'fa-shirt');
        // Rig (24.10.2026, Edgar: „Mach einen toggle button für Rig, das möchte ich auch sehen“) — das Skelett der Testfigur in ihrer Haltung, wie der Knopf „Rig“ der Mesh3D-AI-Testseite
        if (daten.test?.adresse && !daten.genesis) this._schalter('Rig', 'rig', 'Das Skelett der Figur in ihrer Haltung über die Ansicht legen (Knochenpunkte, Farbe nach Gruppe)', 'fa-bone');
        if (daten.netze.length > 1) this._gruppe('Netz', daten.netze.map((n, i) => ({ wert: i, text: n.name, titel: `${n.mb} MB` })), 'netz');
    }

    /** Die Ansichtsart der Zeichner („Normale“ und „Netz farbig“ zeichnen sie als „Textur“). */
    get modus() {
        return Ai2d3dansichtsart.getauscht(this.ansicht) ? 'textur' : this.ansicht;
    }

    /** „normale“ / „netzfarbe“, wenn die Felder beim Rendern Materialien tauschen — sonst null. */
    get art() {
        return Ai2d3dansichtsart.getauscht(this.ansicht) ? this.ansicht : null;
    }
}
