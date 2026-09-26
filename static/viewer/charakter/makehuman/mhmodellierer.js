import { escapeHtml } from '../utils.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Zeiten } from '../../gemeinsam/zeiten.js';
import { Mhkoerperregler } from './mhkoerperregler.js';

/**
 * Mhmodellierer — MakeHumans 269 Modellierregler im Eigenschaften-Reiter.
 *
 * WOHER SIE KOMMEN (Edgar, 06.09.2026: „nimm dir den source von makeHuman aus
 * dem web"): aus `MakeHuman/makehuman/data/modifiers/`. Der Server liefert
 * unter `/api/character/mh-figur/regler/` MakeHumans eigene Seiten- und
 * Abschnittsgliederung — „Macro modelling", „Gender", „Torso", „Arms and
 * Legs", „Face", „Measure" — samt Beschriftungen und Grenzen.
 *
 * DIE BESCHRIFTUNGEN SIND ENGLISCH, und zwar mit Absicht: Es sind MakeHumans
 * Namen, unter denen man sie dort und in jeder Anleitung wiederfindet.
 *
 * ERST BEIM AUFKLAPPEN GEBAUT. 269 Regler auf einmal sind 269 Zeilen im DOM,
 * von denen man drei sieht. Jede Seite und jeder Abschnitt ist ein
 * `<details>`; die Zeilen entstehen, wenn er zum ersten Mal geöffnet wird.
 *
 * GERECHNET WIRD BEIM LOSLASSEN, nicht beim Ziehen: Ein Zug ist eine neue
 * Anfrage für Körper UND jedes Kleidungsstück. Wer beim Ziehen rechnete,
 * schickte hundert davon los.
 */
export class Mhmodellierer {

    static ADRESSE = '/api/character/mh-figur/regler/';
    /** Der Plan gilt für alle Figuren — einmal je Seite geholt. */
    static _plan = null;
    /** Läuft gerade ein Neuaufbau? Dann wird der letzte Wunsch nachgezogen. */
    static _laeuft = false;
    static _nachziehen = null;

    static async plan() {
        if (!Mhmodellierer._plan) {
            Mhmodellierer._plan = await Serverabruf.json(Mhmodellierer.ADRESSE);
        }
        return Mhmodellierer._plan;
    }

    // ------------------------------------------------------------------ Aufbau

    /**
     * @param inst      die MakeHuman-Figur
     * @param behaelter Zielelement
     * @param neu       true = auch dann bauen, wenn schon etwas dasteht
     *
     * NUR EINMAL JE FIGUR GEBAUT. `populateProperties` läuft bei jedem
     * Auswählen, jedem Greifen und nach jedem Netzaufbau — wer dabei den
     * Bereich neu aufbaut, klappt dem Benutzer die gerade geöffnete Seite
     * unter der Hand zu. Beim zweiten Mal werden nur die Reglerstellungen
     * nachgezogen; das ist auch das, was nach einem „Zurücksetzen" oder
     * einer geladenen Szene nötig ist.
     */
    static async fuellen(inst, behaelter, neu = false) {
        if (!behaelter) return;
        if (!neu && behaelter.dataset.figur === inst.id
                && behaelter.querySelector('details')) {
            Mhmodellierer.werteAngleichen(inst, behaelter);
            return;
        }
        behaelter.dataset.figur = inst.id;
        behaelter.innerHTML =
            '<div class="hb-hinweis"><i class="fas fa-spinner fa-spin"></i>'
            + ' Lade MakeHuman-Regler …</div>';
        let plan;
        try {
            plan = await Mhmodellierer.plan();
        } catch (fehler) {
            behaelter.innerHTML = '<div class="fehlertext">Regler nicht '
                + `abrufbar: ${escapeHtml(fehler.message)}</div>`;
            return;
        }
        behaelter.innerHTML = '';
        if (plan.fehler || !plan.seiten?.length) {
            behaelter.innerHTML = `<div class="hb-hinweis">${escapeHtml(
                plan.fehler || 'Keine Modellierregler vorhanden.')}</div>`;
            return;
        }
        for (const seite of plan.seiten) {
            behaelter.appendChild(Mhmodellierer._seite(inst, seite));
        }
        behaelter.appendChild(Mhmodellierer._zuruecksetzen(inst, behaelter));
    }

    static _seite(inst, seite) {
        const anzahl = seite.abschnitte.reduce((s, a) => s + a.regler.length, 0);
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe';
        const kopf = document.createElement('summary');
        kopf.textContent = `${seite.name} (${anzahl})`;
        kasten.appendChild(kopf);
        const rumpf = document.createElement('div');
        kasten.appendChild(rumpf);
        Mhmodellierer._beimOeffnen(kasten, () => {
            for (const abschnitt of seite.abschnitte) {
                rumpf.appendChild(Mhmodellierer._abschnitt(inst, abschnitt));
            }
        });
        return kasten;
    }

    static _abschnitt(inst, abschnitt) {
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe';
        const kopf = document.createElement('summary');
        kopf.textContent = `${abschnitt.name} (${abschnitt.regler.length})`;
        kasten.appendChild(kopf);
        const rumpf = document.createElement('div');
        kasten.appendChild(rumpf);
        Mhmodellierer._beimOeffnen(kasten, () => {
            for (const regler of abschnitt.regler) {
                rumpf.appendChild(Mhmodellierer._zeile(inst, regler));
            }
        });
        return kasten;
    }

    /** Den Inhalt genau einmal bauen — beim ersten Aufklappen. */
    static _beimOeffnen(kasten, bauen) {
        kasten.addEventListener('toggle', () => {
            if (!kasten.open || kasten.dataset.gebaut === '1') return;
            kasten.dataset.gebaut = '1';
            bauen();
        });
    }

    // ------------------------------------------------------------------ Zeile

    static _zeile(inst, angabe) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.dataset.kennung = angabe.kennung;
        zeile.dataset.makro = angabe.makro || '';
        zeile.dataset.vorgabe = String(angabe.vorgabe);
        const titel = angabe.hinweis || angabe.kennung;
        zeile.innerHTML = `<label title="${escapeHtml(titel)}">`
            + `${escapeHtml(angabe.name)}</label>`;
        const schieber = document.createElement('input');
        schieber.type = 'range';
        // Der Server rechnet in -1..1 bzw. 0..1; der Schieber läuft in
        // Hundertsteln, weil `step="0.01"` in manchen Browsern rundet.
        schieber.min = String(Math.round(angabe.min * 100));
        schieber.max = String(Math.round(angabe.max * 100));
        schieber.step = '1';
        schieber.value = String(Math.round(
            Mhmodellierer.wert(inst, angabe) * 100));
        schieber.className = 'hb-dehnt-ohne-abstand';
        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        anzeige.textContent = (Number(schieber.value) / 100).toFixed(2);
        schieber.addEventListener('input', () => {
            anzeige.textContent = (Number(schieber.value) / 100).toFixed(2);
        });
        schieber.addEventListener('change', () => {
            Mhmodellierer.setzen(inst, angabe, Number(schieber.value) / 100);
            Mhmodellierer.anwenden(inst);
        });
        zeile.append(schieber, anzeige);
        return zeile;
    }

    /**
     * Die sichtbaren Schieber auf den Stand der Figur bringen.
     *
     * Gebraucht, wo der Bereich stehen bleibt, die Werte sich aber geändert
     * haben: nach dem Zurücksetzen, nach einer geladenen Szene, nach dem
     * Wechsel auf eine andere Figur mit schon gebautem Bereich.
     */
    static werteAngleichen(inst, behaelter) {
        for (const zeile of behaelter.querySelectorAll('.slider-row')) {
            const kennung = zeile.dataset.kennung;
            const schieber = zeile.querySelector('input[type=range]');
            const anzeige = zeile.querySelector('.slider-val');
            if (!kennung || !schieber) continue;
            const makro = zeile.dataset.makro || '';
            const wert = makro
                ? (inst.makro[makro] ?? Number(zeile.dataset.vorgabe))
                : (inst.regler[kennung] ?? Number(zeile.dataset.vorgabe));
            schieber.value = String(Math.round(wert * 100));
            if (anzeige) anzeige.textContent = wert.toFixed(2);
        }
    }

    /** Die aktuelle Stellung eines Reglers an dieser Figur. */
    static wert(inst, angabe) {
        if (angabe.makro) {
            return inst.makro[angabe.makro] ?? angabe.vorgabe;
        }
        return inst.regler[angabe.kennung] ?? angabe.vorgabe;
    }

    static setzen(inst, angabe, wert) {
        if (angabe.makro) inst.makro[angabe.makro] = wert;
        else inst.regler[angabe.kennung] = wert;
    }

    // ----------------------------------------------------------- Zurücksetzen

    static _zuruecksetzen(inst, behaelter) {
        const knopf = document.createElement('button');
        knopf.className = 'btn-toggle hb-volle-breite';
        knopf.innerHTML = '<i class="fas fa-undo"></i> Alle Regler zurücksetzen';
        knopf.addEventListener('click', async () => {
            inst.makro = {};
            inst.regler = {};
            Mhmodellierer.werteAngleichen(inst, behaelter);
            await Mhmodellierer.anwenden(inst);
        });
        return knopf;
    }

    // ------------------------------------------------------------- Anwenden

    /**
     * Körper und Kleidung neu holen — EINE Anfrage zur Zeit.
     *
     * Ein Zug am Regler kostet gemessene 0,07 bis 0,4 s je Netz, und die
     * Kleidung kommt dazu. Wer währenddessen einen zweiten Regler bewegt,
     * bekommt seinen Wunsch nach dem laufenden Bau nachgezogen — „der letzte
     * Stand gewinnt", derselbe Weg wie beim MakeHuman-Proxy
     * (`mhproxy_anpassen.js`, 15.08.2026).
     */
    static async anwenden(inst) {
        if (Mhmodellierer._laeuft) {
            Mhmodellierer._nachziehen = inst;
            return;
        }
        Mhmodellierer._laeuft = true;
        try {
            await inst.neuFormen();
            Mhkoerperregler.nachAufbau(inst, 'MakeHuman-Modellierung');
        } catch (fehler) {
            Protokoll.fehler('MhModell', 'Netz nicht ladbar', fehler);
        } finally {
            Mhmodellierer._laeuft = false;
        }
        const offen = Mhmodellierer._nachziehen;
        if (offen) {
            Mhmodellierer._nachziehen = null;
            setTimeout(() => Mhmodellierer.anwenden(offen), Zeiten.ROLLEN_MS);
        }
    }
}
