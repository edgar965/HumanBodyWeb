import { Panel } from './panels/panel.js';
import { Theatreanmeldung } from '../laden/theatreanmeldung.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Figurentfernen — das Gewählte aus der Bühne nehmen, und wieder zurück.
 *
 * ANLASS (Edgar, 11.09.2026): „wenn ich auf ein Modell klicke, möchte ich das
 * entfernen können, z.B. mit dem Entf button. Undo soll auch verfügbar sein."
 *
 * Gewählt ist, was `Auswahl` hält: eine Figur ODER ein Kleidungsstück. Entf
 * nimmt genau das — ein gewähltes Stück lässt die Figur stehen. (In der
 * Szene-Seite löschte Entf am 08.09.2026 die ganze Figur, weil das Stück
 * dort kein eigenes Objekt war; hier ist es von Anfang an eines.)
 *
 * RÜCKGÄNGIG IST EIN BEFEHLSSTAPEL, KEIN SCHNAPPSCHUSS. Die Szene-Seite
 * spielt für Undo den ganzen Bühnenstand neu ein (`scene/undo.js`) — das
 * lädt Figuren vom Server, Sekunden je Figur. Hier wird das entfernte Objekt
 * nur AUSGEHÄNGT und aufgehoben: Netze, Skelett, Material bleiben, Rückgängig
 * hängt es an derselben Stelle wieder ein. Nichts wird freigegeben, solange
 * es auf einem Stapel liegt; mehr als `TIEFE` Einträge fallen hinten heraus.
 *
 * TASTEN UND DAS THEATRE-STUDIO: Theatre.js hört selbst auf Strg+Z für seine
 * Schlüsselbilder. Zwei Rückgängig-Systeme auf einer Taste brauchen eine
 * Regel, und die ist: **Rückgängig wirkt dort, wo zuletzt geklickt wurde.**
 * Kam der letzte Klick aus dem Studio-Overlay (`#theatrejs-studio-root`),
 * bleibt die Taste dem Studio; sonst — Bühne, Leiste, Menü — gilt sie hier
 * und wird dem Studio vorenthalten. Über das Menü „Bearbeiten" geht es immer,
 * ohne Taste.
 *
 * AUSTAUSCH (11.09.2026, `studio/figurtausch.js`): „Modell austauschen" ist
 * EIN Schritt auf dem Stapel — alte Figur raus, neue rein. Rückgängig dreht
 * beides um, statt die alte neben die neue zu stellen. `danach(figur)` läuft
 * nach jedem Wechsel und holt Eigenschaften-Feld und Animation nach.
 */
export class Figurentfernen {

    /** So viele Schritte lassen sich zurücknehmen. */
    static TIEFE = 20;

    /** Wurzel des Theatre.js-Studio-Overlays. */
    static STUDIO = 'theatrejs-studio-root';

    /** Felder, in denen Entf und Strg+Z dem Text gehören. */
    static EINGABE = /^(INPUT|TEXTAREA|SELECT)$/;

    /**
     * @param {Object} teile { scene, figuren, auswahl }
     *        figuren = dieselbe Liste, die Raycaster und Skinner führen
     */
    constructor({ scene, figuren, auswahl }) {
        this.scene = scene;
        this.figuren = figuren;
        this.auswahl = auswahl;
        this.rueck = [];
        this.wieder = [];
        this.klickImStudio = false;
    }

    verdrahten() {
        document.getElementById('menu-auswahl-entfernen')
            ?.addEventListener('click', () => this.entfernen());
        document.getElementById('menu-rueckgaengig')
            ?.addEventListener('click', () => this.rueckgaengig());
        document.getElementById('menu-wiederholen')
            ?.addEventListener('click', () => this.wiederholen());
        document.addEventListener('pointerdown', (e) => {
            this.klickImStudio = Boolean(
                e.target?.closest?.(`#${Figurentfernen.STUDIO}`));
        }, true);
        // Capture-Phase, damit die Entscheidung VOR dem Studio fällt.
        window.addEventListener('keydown', (e) => this._taste(e), true);
        return this;
    }

    // -- Befehle --------------------------------------------------------------

    /** Das Gewählte entfernen. Liefert den Eintrag oder `null`. */
    entfernen() {
        const eintrag = this.auswahl.kleidung
            ? this._stueckAushaengen(this.auswahl.kleidung)
            : (this.auswahl.figur ? this._figurAushaengen(this.auswahl.figur) : null);
        if (!eintrag) return null;
        this._ablegen(this.rueck, eintrag);
        this.wieder.length = 0;
        this._abgewaehlt();
        Protokoll.debug('figurentfernen', 'entfernt:', eintrag.name);
        return eintrag;
    }

    rueckgaengig() {
        const eintrag = this.rueck.pop();
        if (!eintrag) return null;
        this._einhaengen(eintrag);
        this._ablegen(this.wieder, eintrag);
        Protokoll.debug('figurentfernen', 'zurück:', eintrag.name);
        return eintrag;
    }

    wiederholen() {
        const eintrag = this.wieder.pop();
        if (!eintrag) return null;
        if (eintrag.art === 'tausch') {
            this._tauschen(eintrag, true);
            this._ablegen(this.rueck, eintrag);
            return eintrag;
        }
        const erneut = eintrag.art === 'figur'
            ? this._figurAushaengen(eintrag.objekt)
            : this._stueckAushaengen(eintrag.objekt);
        if (!erneut) return null;
        this._ablegen(this.rueck, erneut);
        this._abgewaehlt();
        return erneut;
    }

    /**
     * `alt` gegen die schon eingehängte `neu` tauschen — ein Schritt.
     * @param {Function} danach  (figur) => …, nach jedem Wechsel
     */
    ersetzen(alt, neu, danach = null) {
        const altEintrag = this._figurAushaengen(alt);
        if (!altEintrag) return null;
        const eintrag = {
            art: 'tausch', alt: altEintrag, danach,
            neu: { art: 'figur', objekt: neu, index: this.figuren.indexOf(neu),
                   schluessel: neu.userData.theatreSchluessel,
                   name: neu.userData.presetName || neu.name || 'Figur' },
            name: `${altEintrag.name} → ${neu.userData.presetName || 'Figur'}`,
        };
        this._ablegen(this.rueck, eintrag);
        this.wieder.length = 0;
        this.auswahl.figurVormerken(neu);
        danach?.(neu);
        Protokoll.debug('figurentfernen', 'getauscht:', eintrag.name);
        return eintrag;
    }

    // -- Aus- und Einhängen ---------------------------------------------------

    _figurAushaengen(figur) {
        const index = this.figuren.indexOf(figur);
        if (index < 0) return null;
        this.figuren.splice(index, 1);
        this.scene.remove(figur);
        Figurentfernen._ausListe(window.loadedCharacters, figur);
        const schluessel = figur.userData.theatreSchluessel;
        try {
            Theatreanmeldung.abmelden(schluessel);
        } catch (fehler) {
            Protokoll.warnung('figurentfernen', 'Theatre-Objekt bleibt:', fehler.message);
        }
        return { art: 'figur', objekt: figur, index, schluessel,
                 name: figur.userData.presetName || figur.name || 'Figur' };
    }

    _stueckAushaengen(netz) {
        const figur = netz.parent;
        if (!figur) return null;
        const index = figur.children.indexOf(netz);
        figur.remove(netz);
        return { art: 'stueck', objekt: netz, figur, index,
                 name: netz.userData.beschriftung || netz.name || 'Kleidung' };
    }

    /** Tausch ausführen (`vor`: alt → neu) oder zurücknehmen (neu → alt). */
    _tauschen(eintrag, vor) {
        const [weg, hin] = vor ? ['alt', 'neu'] : ['neu', 'alt'];
        const ausgehaengt = this._figurAushaengen(eintrag[weg].objekt);
        if (ausgehaengt) eintrag[weg] = ausgehaengt;   // frischer Index und Schlüssel
        this._einhaengen(eintrag[hin]);
        eintrag.danach?.(eintrag[hin].objekt);
    }

    _einhaengen(eintrag) {
        if (eintrag.art === 'tausch') {
            this._tauschen(eintrag, false);
            return;
        }
        if (eintrag.art === 'figur') {
            const figur = eintrag.objekt;
            this.scene.add(figur);
            this.figuren.splice(Math.min(eintrag.index, this.figuren.length), 0, figur);
            if (window.loadedCharacters && !window.loadedCharacters.includes(figur)) {
                window.loadedCharacters.push(figur);
            }
            if (eintrag.schluessel) {
                figur.userData.theatreObjekt = Theatreanmeldung.anmelden(
                    figur, eintrag.schluessel, 'Character');
            }
            this.auswahl.figurVormerken(figur);
            return;
        }
        const { figur, objekt, index } = eintrag;
        figur.add(objekt);
        // `add` hängt hinten an; die alte Stelle stellt die Reihenfolge der
        // Kinder wieder her — sie bestimmt, was der Raycaster zuerst trifft.
        figur.children.splice(figur.children.indexOf(objekt), 1);
        figur.children.splice(Math.min(index, figur.children.length), 0, objekt);
    }

    // -- Tasten ---------------------------------------------------------------

    _taste(e) {
        if (Figurentfernen.EINGABE.test(e.target?.tagName || '')
            || e.target?.isContentEditable || this.klickImStudio) return;
        const strg = e.ctrlKey || e.metaKey;
        let getan = false;
        if (e.key === 'Delete' && !strg) {
            getan = Boolean(this.entfernen());
        } else if (strg && e.key.toLowerCase() === 'z' && !e.shiftKey) {
            getan = Boolean(this.rueckgaengig());
        } else if (strg && (e.key.toLowerCase() === 'y'
                            || (e.key.toLowerCase() === 'z' && e.shiftKey))) {
            getan = Boolean(this.wiederholen());
        }
        if (getan) {
            e.preventDefault();
            e.stopImmediatePropagation();   // das Studio bekommt die Taste nicht
        }
    }

    // -- Helfer ---------------------------------------------------------------

    _ablegen(stapel, eintrag) {
        stapel.push(eintrag);
        if (stapel.length > Figurentfernen.TIEFE) stapel.shift();
    }

    _abgewaehlt() {
        this.auswahl.leeren();
        Panel.leeren();
    }

    static _ausListe(liste, objekt) {
        const i = Array.isArray(liste) ? liste.indexOf(objekt) : -1;
        if (i >= 0) liste.splice(i, 1);
    }
}
