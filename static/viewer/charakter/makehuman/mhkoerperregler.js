import { fn } from '../../gemeinsam/registrierung.js';
import { markDirty } from '../undo.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Mhkopfzeile } from './mhkopfzeile.js';

/**
 * Mhkoerperregler — was am MakeHuman-Körper selbst einstellbar ist.
 *
 * DREI DINGE, UND JEDES HAT SEINE ENTSPRECHUNG IN MAKEHUMAN
 * =========================================================
 * * **Netzteile** — MakeHumans Basisnetz besteht aus der Haut (13.378
 *   Vierecke), der Helfergeometrie (4.358) und 125 Gelenkwürfeln (750). Die
 *   Helfer sind unsichtbare Hilfsflächen, an denen die `.mhclo`-Zuordnungen
 *   der Kleidung hängen — wer sehen will, warum ein Rock so sitzt, wie er
 *   sitzt, schaltet sie ein.
 * * **Glätten** — MakeHumans „Smooth": eine Stufe Catmull-Clark. Aus 13.380
 *   Punkten werden 53.514.
 * * **Größe** — eine Skalierung der ganzen Figur, und ausdrücklich NICHT
 *   MakeHumans Höhenregler. Den gibt es seit dem Upstream vom 06.09.2026
 *   auch (Modellieren → „Macro modelling" → Height): Er rechnet mit
 *   `.target`-Dateien, verschiebt die Proportionen mit und reicht von 129 bis
 *   238 cm — gemessen. Der Regler hier zieht das fertige Netz größer, ohne
 *   an der Form zu rühren; das ist zweierlei und steht deshalb getrennt.
 *
 * Netzteile und Glättung holen das Netz neu (gemessen: 0,28 s, beim ersten
 * Glätten 1,15 s, danach aus dem Zwischenspeicher der Unterteilung). Sie
 * hängen deshalb an einem Kästchen, nicht an einem Regler.
 */
export class Mhkoerperregler {

    /** Grenzen des Größenreglers in Zentimetern. */
    static KLEINSTE_CM = 120;
    static GROESSTE_CM = 220;

    /**
     * @param inst     die MakeHuman-Figur
     * @param behaelter Zielelement
     * @param angebot  die Teile aus dem Steckbrief des Servers
     *                 (`[{schluessel, name, erklaerung, flaechen}]`)
     */
    static fuellen(inst, behaelter, angebot) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        for (const teil of angebot || []) {
            behaelter.appendChild(Mhkoerperregler._teilzeile(inst, teil));
        }
        behaelter.appendChild(Mhkoerperregler._glaetten(inst));
        behaelter.appendChild(Mhkoerperregler._groesse(inst));
    }

    // -------------------------------------------------------------- Netzteile

    static _teilzeile(inst, teil) {
        const zeile = document.createElement('div');
        zeile.className = 'prop-row';
        const beschriftung = document.createElement('label');
        beschriftung.title = teil.erklaerung || teil.name;
        const kaestchen = document.createElement('input');
        kaestchen.type = 'checkbox';
        kaestchen.checked = inst.teile.includes(teil.schluessel);
        kaestchen.addEventListener('change', () => {
            const teile = kaestchen.checked
                ? [...inst.teile, teil.schluessel]
                : inst.teile.filter(t => t !== teil.schluessel);
            // Ganz ohne Netz gäbe es nichts zu sehen und nichts zu wählen.
            if (!teile.length) {
                kaestchen.checked = true;
                return;
            }
            inst.teile = teile;
            Mhkoerperregler.neuAufbauen(inst, 'MakeHuman-Netzteile');
        });
        beschriftung.append(kaestchen, document.createTextNode(
            ` ${teil.name}${teil.flaechen ? ` (${teil.flaechen})` : ''}`));
        zeile.appendChild(beschriftung);
        return zeile;
    }

    // --------------------------------------------------------------- Glätten

    static _glaetten(inst) {
        const zeile = document.createElement('div');
        zeile.className = 'prop-row';
        const beschriftung = document.createElement('label');
        beschriftung.title = 'Eine Stufe Catmull-Clark — MakeHumans „Smooth".';
        const kaestchen = document.createElement('input');
        kaestchen.type = 'checkbox';
        kaestchen.checked = inst.glatt;
        kaestchen.addEventListener('change', () => {
            inst.glatt = kaestchen.checked;
            Mhkoerperregler.neuAufbauen(inst, 'MakeHuman-Glättung');
        });
        beschriftung.append(kaestchen,
                            document.createTextNode(' Glätten (Smooth)'));
        zeile.appendChild(beschriftung);
        return zeile;
    }

    // ----------------------------------------------------------------- Größe

    static _groesse(inst) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = '<label title="Skaliert das fertige Netz. MakeHumans'
            + ' eigener Höhenregler steht unter Modellieren → Macro modelling'
            + ' → Height und verformt statt zu strecken.">Größe</label>';
        const schieber = document.createElement('input');
        schieber.type = 'range';
        schieber.min = String(Mhkoerperregler.KLEINSTE_CM);
        schieber.max = String(Mhkoerperregler.GROESSTE_CM);
        schieber.step = '1';
        schieber.className = 'hb-dehnt-ohne-abstand';
        schieber.value = String(Math.min(Mhkoerperregler.GROESSTE_CM,
            Math.max(Mhkoerperregler.KLEINSTE_CM,
                     Math.round(inst.sichtbareHoehe() * 100))));
        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        anzeige.textContent = `${schieber.value} cm`;
        schieber.addEventListener('input', () => {
            anzeige.textContent = `${schieber.value} cm`;
            inst.aufHoehe(Number(schieber.value) / 100);
            Mhkopfzeile.angleichen(inst);
        });
        schieber.addEventListener('change', () => {
            fn.updateCharacterListUI();
            markDirty('MakeHuman-Größe');
        });
        zeile.append(schieber, anzeige);
        return zeile;
    }

    // ------------------------------------------------------------ Neuaufbau

    /**
     * Den Körper neu holen — die Kleidung bleibt hängen.
     *
     * Sie sitzt auf dem BASISNETZ, nicht auf dem angezeigten: Ob die
     * Helfergeometrie sichtbar ist oder das Netz geglättet, ändert an der
     * `.mhclo`-Rechnung nichts.
     */
    static async neuAufbauen(inst, grund) {
        try {
            await inst.koerperAufbauen();
        } catch (fehler) {
            Protokoll.fehler('MhFigur', 'Netz nicht ladbar', fehler);
            alert(`MakeHuman-Netz nicht ladbar: ${fehler.message}`);
            return;
        }
        Mhkoerperregler.nachAufbau(inst, grund);
    }

    /**
     * Was nach JEDEM Neuaufbau zu tun ist — auch nach einem, den der
     * Modellierer angestoßen hat (`mhmodellierer.js`). Stand vorher nur in
     * `neuAufbauen`; von dort war es nicht erreichbar, ohne den Körper ein
     * zweites Mal zu holen.
     */
    static nachAufbau(inst, grund) {
        Mhkopfzeile.angleichen(inst);
        fn.updateVertexCount();
        fn.updateCharacterListUI();
        markDirty(grund);
    }
}
