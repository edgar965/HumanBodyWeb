import { Koerperdetails } from '../gemeinsam/koerperdetails.js';
import { Morphliste } from '../gemeinsam/morphliste.js';
import { Brauenvorlagen } from '../gemeinsam/brauenvorlagen.js';
import { Charakterkoerper } from './charakter_koerper.js';
import { Detailbereiche } from './detailbereiche.js';
import { markDirty } from './undo.js';

/**
 * Detailbedienung — die Bereiche Haut, Augen, Augenbrauen, Mund und Nägel im
 * Reiter „Modell" (Edgar, 12.09.2026: „bei klick auf das Model … muss ich
 * doch einen Bereich haben wo ich die Farbe der Fingernägel, die
 * Augenwimpern, die Farbe der Augen usw einstellen kann?" — abends: „fehlen
 * die Augenbrauen. Auch augenlider fehlen" — und: „es fehlen noch die
 * Lippen (farbe usw.) … schön nach Bereich geordnet").
 *
 * Was welcher Bereich enthält, steht in `Detailbereiche`. Farben, Glanz und
 * die Längen von Wimpern und Fußnägeln wirken sofort im Browser
 * (`Koerperdetails.anwenden`, Feld `inst.details` des Modells); die Brauen
 * sind eine Zeichnung im Hautshader (`Brauenhaut`, 16.09.2026: jeder Regler zeichnet neu).
 * Fingernägel, Lider und Brauenform gehen über MORPHS (`Hands_NailsLength`,
 * `Eyelids_*`, `Eyebrows_*`) — wie jeder Morph über den Server (`neuLaden`),
 * und der Regler im Bereich „Morphs" zieht mit (`Morphliste.angleichen`).
 * Die Haut ohne eigene Farbe zeigt die der Körperart (Feld leer).
 */
export class Detailbedienung {

    static _figur = null;
    static _neuLaden = null;
    static _verdrahtet = false;

    /** Die Bereiche mit den Werten der Figur füllen. */
    static fuellen(inst, neuLaden) {
        Detailbedienung._figur = inst;
        Detailbedienung._neuLaden = neuLaden;
        if (!inst.details) inst.details = Koerperdetails.aus(null);
        for (const [kennung, feld] of Detailbereiche.farben()) {
            const eingabe = document.getElementById(kennung);
            if (eingabe) eingabe.value = inst.details[feld] || Detailbedienung._koerperfarbe(inst);
        }
        for (const [kennung, feld] of Detailbereiche.prozent()) {
            Detailbedienung._reglerSetzen(kennung, Math.round(inst.details[feld] * 100), '%');
        }
        for (const [kennung, feld] of Detailbereiche.millimeter()) {
            Detailbedienung._reglerSetzen(kennung, Math.round(inst.details[feld] * 1000), 'mm');
        }
        for (const [kennung, feld] of Detailbereiche.auswahl()) {
            const wahl = document.getElementById(kennung);
            if (wahl) wahl.value = inst.details[feld] || '';
        }
        Detailbedienung._vorlageZeigen(inst.details);
        for (const name of Detailbereiche.morphe()) {
            Detailbedienung._reglerSetzen(Detailbereiche.morphKennung(name),
                                          Math.round((inst.morphs?.[name] || 0) * 100), '');
        }
        Detailbedienung._verdrahten();
    }

    /** Die Hautfarbe, die die Figur gerade trägt (Körperart) — fürs leere Feld. */
    static _koerperfarbe(inst) {
        const farbe = Charakterkoerper.materialien(inst)[0]?.color;
        return farbe?.getHexString ? `#${farbe.getHexString()}` : '#d4a574';
    }

    static _reglerSetzen(kennung, wert, einheit) {
        const regler = document.getElementById(kennung);
        // stumm gewollt: nicht jedes Detailfeld hat einen Regler auf der Seite
        if (!regler) return;
        regler.value = wert;
        const anzeige = document.getElementById(kennung + '-val');
        if (anzeige) anzeige.textContent = einheit ? `${wert} ${einheit}` : String(wert);
    }

    static _verdrahten() {
        if (Detailbedienung._verdrahtet) return;
        Detailbedienung._verdrahtet = true;
        for (const [kennung, feld] of Detailbereiche.farben()) {
            document.getElementById(kennung)?.addEventListener('input', (e) => {
                Detailbedienung._aendern(feld, e.target.value);
            });
        }
        for (const [kennung, feld] of Detailbereiche.prozent()) {
            const regler = document.getElementById(kennung);
            regler?.addEventListener('input', () => {
                Detailbedienung._reglerSetzen(kennung, regler.value, '%');
                Detailbedienung._aendern(feld, Number(regler.value) / 100);
            });
        }
        for (const [kennung, feld] of Detailbereiche.millimeter()) {
            const regler = document.getElementById(kennung);
            regler?.addEventListener('input', () => {
                Detailbedienung._reglerSetzen(kennung, regler.value, 'mm');
                Detailbedienung._aendern(feld, Number(regler.value) / 1000);
            });
        }
        for (const [kennung, feld] of Detailbereiche.auswahl()) {
            document.getElementById(kennung)?.addEventListener('change', (e) => {
                Detailbedienung._aendern(feld, e.target.value);
            });
        }
        Detailbedienung._vorlagenVerdrahten();
        for (const name of Detailbereiche.morphe()) {
            Detailbedienung._morphregler(Detailbereiche.morphKennung(name), name);
        }
        for (const knopf of document.querySelectorAll('.prop-detail-reset')) {
            knopf.addEventListener('click', () => Detailbedienung.zuruecksetzen(knopf.dataset.bereich || null));
        }
    }

    static VORLAGE = 'prop-detail-brauen-vorlage';

    /** Die Brauenvorlagen ins Auswahlfeld; eine Wahl setzt die Brauenfelder. */
    static _vorlagenVerdrahten() {
        const wahl = document.getElementById(Detailbedienung.VORLAGE);
        if (!wahl) return;
        wahl.innerHTML = Brauenvorlagen.ALLE.map(([k, name]) => `<option value="${k}">${name}</option>`).join('')
            + '<option value="eigene">Eigene Werte</option>';
        wahl.addEventListener('change', () => {
            const inst = Detailbedienung._figur;
            if (!inst || wahl.value === 'eigene') return;
            const neu = Brauenvorlagen.anwenden(inst.details, wahl.value, Koerperdetails.VORGABE);
            inst.details = Koerperdetails.aus({ [Koerperdetails.FELD]: neu });
            Detailbedienung.fuellen(inst, Detailbedienung._neuLaden);
            Detailbedienung.anwenden(inst, 'brauen');
            markDirty();
        });
    }

    static _vorlageZeigen(details) {
        const wahl = document.getElementById(Detailbedienung.VORLAGE);
        if (wahl) wahl.value = Brauenvorlagen.erkennen(details, Koerperdetails.VORGABE) ?? 'eigene';
    }

    /** Ein Morph-Regler: Anzeige beim Ziehen, Serverlauf beim Loslassen. */
    static _morphregler(kennung, name) {
        const regler = document.getElementById(kennung);
        if (!regler) return;
        regler.addEventListener('input', () => Detailbedienung._reglerSetzen(kennung, regler.value, ''));
        regler.addEventListener('change', () => Detailbedienung._morph(name, Number(regler.value) / 100));
    }

    /** Farbe, Glanz oder Länge ändern: in die Figur, aufs Netz, Szene als geändert merken. */
    static _aendern(feld, wert) {
        const inst = Detailbedienung._figur;
        if (!inst) return;
        inst.details = Koerperdetails.aus({ [Koerperdetails.FELD]: { ...inst.details, [feld]: wert } });
        Detailbedienung.anwenden(inst, feld);
        markDirty();
    }

    /**
     * Sofort aufs Netz — ohne Serverlauf (`Koerperdetails` merkt die Basis).
     * Brauen (`brauen*`): der Server zeichnet die Karte neu (`Brauenhaut`,
     * 0,2 s); alles (`null`) = Neubau.
     */
    static anwenden(inst, feld = null) {
        if (!inst.bodyMesh) return;
        // Eine Figurart mit eigener Umsetzung derselben Felder (SMPL-X, 25.09.2026:
        // Shader + Wimpern-/Mundnetze, `gemeinsam/smpldetails.js`).
        // Eigener Name: `HumanbodyModell.detailsAnwenden(neue)` gibt es auch — mit Punkten, nicht Feldern.
        if (typeof inst.detailfeldAnwenden === 'function') { inst.detailfeldAnwenden(feld); return; }
        if (Detailbereiche.neubau(feld)) { Charakterkoerper.details(inst); return; }
        if (!inst.details.haut) Charakterkoerper.hautfarbe(inst, Charakterkoerper.materialien(inst));
        Koerperdetails.anwenden(inst.bodyMesh, inst.details);
    }

    /** Einen Morph der Figur setzen (0 = weg) und den Körper neu holen. */
    static _morph(name, wert) {
        const inst = Detailbedienung._figur;
        if (!inst) return;
        if (!inst.morphs) inst.morphs = {};
        if (Math.abs(wert) < 0.005) delete inst.morphs[name];
        else inst.morphs[name] = wert;
        Morphliste.angleichen(document.getElementById('prop-morphs-panel'), inst.morphs || {});
        Detailbedienung._neuLaden?.(inst);
    }

    /** Einen Bereich (oder alle) auf die Vorgabe: Details und seine Morphs. */
    static zuruecksetzen(bereich = null) {
        const inst = Detailbedienung._figur;
        if (!inst) return;
        const neu = { ...inst.details };
        for (const feld of Detailbereiche.felder(bereich)) neu[feld] = Koerperdetails.VORGABE[feld];
        inst.details = Koerperdetails.aus({ [Koerperdetails.FELD]: neu });
        let morphsWeg = 0;
        for (const name of Detailbereiche.morphe(bereich)) {
            if (inst.morphs && name in inst.morphs) { delete inst.morphs[name]; morphsWeg += 1; }
        }
        Detailbedienung.fuellen(inst, Detailbedienung._neuLaden);
        Detailbedienung.anwenden(inst);
        markDirty();
        if (morphsWeg) {
            Morphliste.angleichen(document.getElementById('prop-morphs-panel'), inst.morphs || {});
            Detailbedienung._neuLaden?.(inst);
        }
    }
}
