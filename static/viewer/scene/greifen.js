import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Greifrechnung } from '../gemeinsam/greifrechnung.js';
import { Greifgeometrie } from './greifgeometrie.js';

/**
 * Greifen — G, R und S so, wie die Zeile unter der Figur es verspricht.
 *
 * WARUM (Edgar, 06.09.2026): „ich verstehe nicht G zum Translate, bei Klick
 * auf G und dann Maus tut sich nichts." Zu Recht: G schaltete nur den MODUS
 * des Gizmos um. Wer danach die Maus bewegte, bewegte nichts — man musste
 * einen der Pfeile greifen, und die sitzen am Ursprung der Figur, also
 * zwischen den Füßen, klein und halb verdeckt.
 *
 * Seither heißt G, was es in Blender heißt: Taste drücken, Figur folgt der
 * Maus, Linksklick oder Enter setzt sie ab, Escape oder Rechtsklick stellt
 * den alten Stand wieder her. X, Y oder Z beschränken auf eine Achse.
 *
 * Das Gizmo bleibt daneben bestehen — wer lieber zieht, zieht.
 */
export class Greifen {

    /** Der laufende Vorgang, oder null. */
    static aktiv = null;

    /** Die letzte bekannte Zeigerposition — beim Tastendruck gibt es kein Event. */
    static _zeiger = { x: 0, y: 0 };

    static laeuft() {
        return Greifen.aktiv !== null;
    }

    /**
     * Einmal beim Seitenaufbau: den Zeiger mitverfolgen.
     *
     * Auf `window`, nicht auf der Leinwand: Wer die Maus zuletzt über dem
     * Bedienfeld hatte und dann G drückt, hätte sonst einen veralteten
     * Startpunkt — und die Figur spränge beim ersten Wackeln meterweit
     * (gemessen am 06.09.2026: 2,7 m).
     */
    static beobachten() {
        window.addEventListener('pointermove', (e) => {
            Greifen._zeiger = { x: e.clientX, y: e.clientY };
        }, { passive: true, capture: true });
    }

    /**
     * Greifen starten. Ohne ausgewählte Figur passiert nichts.
     * @param modus 'translate' | 'rotate' | 'scale'
     */
    static starten(modus) {
        const inst = state.characters.get(state.selectedCharacterId);
        if (!inst?.group) return false;
        if (Greifen.aktiv) Greifen.aktiv.abbrechen();
        Greifen.aktiv = new Greifen(inst, modus);
        return true;
    }

    constructor(inst, modus) {
        this.inst = inst;
        this.objekt = inst.group;
        this.modus = modus;
        this.achse = null;
        // Der Startpunkt wird erst bei der ERSTEN Bewegung gesetzt. So kann
        // kein veralteter Zeigerstand die Figur springen lassen, egal woher
        // die Maus kommt.
        this.start = null;
        this.wert = modus === 'scale' ? 1 : (modus === 'rotate' ? 0 : { x: 0, y: 0, z: 0 });

        // Ausgangsstand, damit Escape ihn zurückholen kann.
        this.position = this.objekt.position.clone();
        this.drehung = this.objekt.quaternion.clone();
        this.groesse = this.objekt.scale.clone();

        this.mitte = Greifgeometrie.mitteImBild(this.objekt);
        // Die Bezugsebene liegt fest, wo die Figur BEIM START stand. Wandert
        // sie mit der schon verschobenen Figur mit, misst man gegen sich
        // selbst und die Bewegung geht auf null zurück (06.09.2026 gemessen).
        this.weltStart = this.objekt.getWorldPosition(new THREE.Vector3());
        this.ebene = Greifgeometrie.ebene(this.weltStart, this.achse);
        this.startpunkt = null;

        this.kameraFrei = state.controls.enabled;
        state.controls.enabled = false;
        if (state.transformControls) state.transformControls.enabled = false;
        state.greiftGerade = true;

        this._anzeigen();
        this._binden();
    }

    // -- Ablauf ---------------------------------------------------------------

    bewegen(punkt) {
        if (!this.start) {
            this.start = { x: punkt.x, y: punkt.y };
            this.startpunkt = Greifgeometrie.aufDerEbene(this.ebene, this.start);
            return;                       // die erste Bewegung ist der Bezug
        }
        if (this.modus === 'translate') this._verschieben(punkt);
        else if (this.modus === 'rotate') this._drehen(punkt);
        else this._skalieren(punkt);
        this.zeile.textContent = Greifrechnung.anzeige(this.modus, this.wert, this.achse);
        fn.updateCharacterListUI?.();
    }

    /** Auf eine Achse beschränken — oder die Beschränkung wieder aufheben. */
    beschraenken(achse) {
        this.achse = (this.achse === achse) ? null : achse;
        if (this.start) this.bewegen(Greifen._zeiger);
    }

    bestaetigen() {
        this._loesen();
        fn.markDirty?.();
        fn.updateCharacterListUI?.();
        fn.populateProperties?.(state.selectedCharacterId);
    }

    abbrechen() {
        this.objekt.position.copy(this.position);
        this.objekt.quaternion.copy(this.drehung);
        this.objekt.scale.copy(this.groesse);
        this.objekt.updateMatrixWorld(true);
        this._loesen();
        fn.updateCharacterListUI?.();
    }

    // -- Die drei Bewegungen --------------------------------------------------

    _verschieben(punkt) {
        const jetzt = Greifgeometrie.aufDerEbene(this.ebene, punkt);
        if (!jetzt || !this.startpunkt) return;
        const roh = jetzt.clone().sub(this.startpunkt);
        // Y meint ausdrücklich die Höhe, alles andere den Boden.
        const d = (this.achse === 'y')
            ? Greifrechnung.maskieren({ x: roh.x, y: roh.y, z: roh.z }, 'y')
            : Greifrechnung.maskieren(Greifgeometrie.aufDenBoden(roh), this.achse);
        this.wert = d;
        this.objekt.position.set(this.position.x + d.x, this.position.y + d.y,
                                 this.position.z + d.z);
        this.objekt.updateMatrixWorld(true);
    }

    _drehen(punkt) {
        const w = Greifrechnung.winkel(this.mitte, this.start, punkt);
        this.wert = w;
        // Ohne Achsenwahl wird um die SENKRECHTE gedreht, nicht um die
        // Blickachse: Figuren stehen, und eine fast waagrechte Kamera ließe
        // sie sonst nach hinten kippen. Wer kippen will, drückt X oder Z.
        const achse = new THREE.Vector3(0, 1, 0);
        if (this.achse === 'x') achse.set(1, 0, 0);
        else if (this.achse === 'z') achse.set(0, 0, 1);
        const dreh = new THREE.Quaternion().setFromAxisAngle(achse.normalize(), w);
        this.objekt.quaternion.copy(dreh.multiply(this.drehung));
        this.objekt.updateMatrixWorld(true);
    }

    _skalieren(punkt) {
        const f = Greifrechnung.faktor(this.start, punkt);
        this.wert = f;
        if (this.achse) {
            this.objekt.scale.copy(this.groesse);
            this.objekt.scale[this.achse] = this.groesse[this.achse] * f;
        } else {
            this.objekt.scale.copy(this.groesse).multiplyScalar(f);
        }
        this.objekt.updateMatrixWorld(true);
    }

    // -- Bedienung ------------------------------------------------------------

    _binden() {
        this._hoerer = [
            [window, 'pointermove', (e) => {
                Greifen._zeiger = { x: e.clientX, y: e.clientY };
                this.bewegen(Greifen._zeiger);
            }, true],
            // Der bestätigende Klick darf nicht als Auswahlklick durchgehen:
            // sonst fiele die Figur ab, sobald man daneben absetzt.
            [window, 'pointerdown', (e) => {
                e.preventDefault(); e.stopImmediatePropagation();
                if (e.button === 2) this.abbrechen(); else this.bestaetigen();
            }, true],
            [window, 'pointerup', (e) => { e.stopImmediatePropagation(); }, true],
            [window, 'contextmenu', (e) => { e.preventDefault(); }, true],
            // `stopImmediatePropagation`, nicht `stopPropagation`: Escape hängt
            // auch an `window` (dort wählt es die Figur ab). Ein Hörer am
            // SELBEN Ziel läuft trotz `stopPropagation` weiter — die Figur
            // fiel beim Abbrechen aus der Auswahl.
            [window, 'keydown', (e) => {
                const achse = Greifrechnung.achse(e.key);
                if (achse) { e.stopImmediatePropagation(); this.beschraenken(achse); return; }
                if (e.key === 'Escape') { e.stopImmediatePropagation(); this.abbrechen(); }
                else if (e.key === 'Enter') { e.stopImmediatePropagation(); this.bestaetigen(); }
            }, true],
        ];
        this._hoerer.forEach(([ziel, typ, ruf, fangen]) =>
            ziel.addEventListener(typ, ruf, fangen));
    }

    _loesen() {
        this._hoerer.forEach(([ziel, typ, ruf, fangen]) =>
            ziel.removeEventListener(typ, ruf, fangen));
        this.balken?.remove();
        state.controls.enabled = this.kameraFrei;
        if (state.transformControls) state.transformControls.enabled = true;
        state.greiftGerade = false;
        Greifen.aktiv = null;
    }

    /** Der Hinweis im Bild — ohne ihn sieht man nicht, dass etwas läuft. */
    _anzeigen() {
        const balken = document.createElement('div');
        balken.className = 'greif-hinweis';
        const zeile = document.createElement('span');
        zeile.className = 'greif-wert';
        zeile.textContent = Greifrechnung.anzeige(this.modus, this.wert, this.achse);
        const hilfe = document.createElement('span');
        hilfe.className = 'greif-hilfe';
        hilfe.textContent = 'Maus bewegen · X/Y/Z Achse · Klick oder Enter setzt ab · Esc bricht ab';
        balken.append(zeile, hilfe);
        (state.canvas.parentElement || document.body).appendChild(balken);
        this.balken = balken;
        this.zeile = zeile;
    }
}

fn.greifenStarten = (modus) => Greifen.starten(modus);
fn.greifenBeobachten = () => Greifen.beobachten();
