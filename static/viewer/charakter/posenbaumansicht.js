import { Kategoriekasten } from '../gemeinsam/kategoriekasten.js';

/**
 * Posenbaumansicht — der Ordnerbaum im Reiter „Posen": ein Kasten je Bestand
 * (HumanBody, Genesis 9), darunter die Ordner verschachtelt, in jedem die Posen.
 *
 * Edgar, 17.10.2026: „Mache Ordner damit sie strukturiert sind." Die Daten
 * kommen fertig als Baum (`/api/character/posenbaum/`, `Posenbaum`); hier wird
 * nur gezeichnet, geklappt und gemerkt. Was ein Klick oder Rechtsklick TUT,
 * steht beim Aufrufer (`pose_apply.js`, `Posenbaummenue`).
 *
 * OFFENE ORDNER BLEIBEN OFFEN: über einen Neubau (nach Verschieben, Löschen,
 * Speichern) und über ein Neuladen der Seite (`localStorage`, nur eine
 * Bequemlichkeit je Browser — fehlt er, sind die Vorgaben offen).
 */
export class Posenbaumansicht {

    static SPEICHER = 'hb-posenbaum-offen';
    /** Ohne Gemerktes offen: die Bestände und die Grundposen (T-/A-Pose) und eigenen. */
    static VORGABE_OFFEN = ['humanbody:', 'genesis9:', 'humanbody:rest_poses', 'humanbody:eigene'];

    /**
     * @param liste    das Element `#pose-list`
     * @param umfeld   `{klick(pose, bestand, zeile), menuePose(ereignis, pose, bestand, zeile),
     *                   menueOrdner(ereignis, knoten, bestand)}`
     */
    constructor(liste, umfeld) {
        this.liste = liste;
        this.umfeld = umfeld;
        this.offen = Posenbaumansicht._gemerkt();
        this.bestaende = [];
        this._angaben = new WeakMap();
    }

    /** Die Pose einer Zeile (`{id, name, art?, ordner}`). */
    angabe(zeile) {
        return this._angaben.get(zeile) || null;
    }

    /** Den Baum zeichnen. `waehle` (`{bestand, id}`) öffnet den Weg zu dieser Pose. */
    zeichnen(daten, waehle = null) {
        this.bestaende = daten.bestaende || [];
        if (waehle) this._wegOeffnen(waehle);
        this.liste.innerHTML = '';
        this.liste.classList.add('posenbaum');
        for (const bestand of this.bestaende) {
            this.liste.appendChild(this._ordner(bestand.baum, bestand, bestand.titel));
        }
        return waehle ? this.zeileVon(waehle.bestand, waehle.id) : null;
    }

    zeileVon(bestand, id) {
        return [...this.liste.querySelectorAll('.pose-zeile')]
            .find((z) => z.dataset.bestand === bestand && z.dataset.poseId === id) || null;
    }

    bestand(kennung) {
        return this.bestaende.find((b) => b.kennung === kennung) || null;
    }

    /** Alle Ordnerpfade eines Bestands, in Baumreihenfolge (für „Verschieben nach …"). */
    ordnerpfade(kennung) {
        const aus = [];
        const sammeln = (knoten) => {
            for (const k of knoten.ordner || []) { aus.push(k.pfad); sammeln(k); }
        };
        const bestand = this.bestand(kennung);
        if (bestand) sammeln(bestand.baum);
        return aus;
    }

    static anzahl(knoten) {
        return (knoten.posen || []).length
            + (knoten.ordner || []).reduce((s, k) => s + Posenbaumansicht.anzahl(k), 0);
    }

    // ------------------------------------------------------------ Bausteine

    _ordner(knoten, bestand, titel) {
        const schluessel = `${bestand.kennung}:${knoten.pfad}`;
        const { kasten, kopf, koerper } = Kategoriekasten.bauen(
            titel || knoten.name, Posenbaumansicht.anzahl(knoten), { offen: this.offen.has(schluessel) });
        kasten.dataset.bestand = bestand.kennung;
        kasten.dataset.pfad = knoten.pfad;
        if (!knoten.pfad) {
            kasten.classList.add('posenbestand');
            kopf.title = bestand.hinweis || '';
        }
        // Nach dem Umschalten von `Kategoriekasten` (der Hörer davor) merken.
        kopf.addEventListener('click', () => this._merken(schluessel, kasten.classList.contains('open')));
        kopf.addEventListener('contextmenu', (ereignis) => {
            ereignis.preventDefault();
            ereignis.stopPropagation();
            this.umfeld.menueOrdner(ereignis, knoten, bestand);
        });
        for (const unter of knoten.ordner || []) koerper.appendChild(this._ordner(unter, bestand));
        for (const pose of knoten.posen || []) koerper.appendChild(this._zeile(pose, bestand, knoten));
        return kasten;
    }

    _zeile(pose, bestand, knoten) {
        const zeile = document.createElement('div');
        zeile.className = 'anim-item pose-zeile';
        // Name als TEXT: er kommt aus einem Dateinamen.
        zeile.textContent = pose.name;
        if (pose.art === 'ausdruck') {
            zeile.classList.add('pose-ausdruck');
            zeile.title = 'Ausdruck (Gesicht)';
        }
        zeile.dataset.poseId = pose.id;
        zeile.dataset.bestand = bestand.kennung;
        zeile.dataset.ordner = knoten.pfad;
        const angabe = { ...pose, ordner: knoten.pfad };
        this._angaben.set(zeile, angabe);
        zeile.addEventListener('click', () => this.umfeld.klick(angabe, bestand, zeile));
        zeile.addEventListener('contextmenu', (ereignis) => {
            ereignis.preventDefault();
            ereignis.stopPropagation();
            this.umfeld.menuePose(ereignis, angabe, bestand, zeile);
        });
        return zeile;
    }

    /** Den Bestand und jeden Ordner über der Pose öffnen (die gerade gespeicherte, die verschobene). */
    _wegOeffnen({ bestand, id }) {
        const teile = String(id).split('/').slice(0, -1);
        const knoten = this.bestand(bestand)?.baum;
        this.offen.add(`${bestand}:`);
        // Genesis-9-Kennungen tragen keinen Ordner — den Weg im Baum suchen.
        const weg = teile.length ? teile.map((_, i) => teile.slice(0, i + 1).join('/'))
                                 : Posenbaumansicht._wegZu(knoten, id) || [];
        for (const pfad of weg) this.offen.add(`${bestand}:${pfad}`);
    }

    static _wegZu(knoten, id) {
        if (!knoten) return null;
        if ((knoten.posen || []).some((p) => p.id === id)) return knoten.pfad ? [knoten.pfad] : [];
        for (const unter of knoten.ordner || []) {
            const weg = Posenbaumansicht._wegZu(unter, id);
            if (weg) return knoten.pfad ? [knoten.pfad, ...weg] : weg;
        }
        return null;
    }

    _merken(schluessel, offen) {
        if (offen) this.offen.add(schluessel); else this.offen.delete(schluessel);
        try {
            localStorage.setItem(Posenbaumansicht.SPEICHER, JSON.stringify([...this.offen]));
        } catch (fehler) { /* privates Fenster, gesperrter Speicher: dann nur bis zum Neuladen */ }
    }

    static _gemerkt() {
        try {
            const roh = JSON.parse(localStorage.getItem(Posenbaumansicht.SPEICHER) || 'null');
            if (Array.isArray(roh)) return new Set(roh.map(String));
        } catch (fehler) { /* siehe `_merken` */ }
        return new Set(Posenbaumansicht.VORGABE_OFFEN);
    }
}
