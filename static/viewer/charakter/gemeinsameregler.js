import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Reglerabbildung } from '../gemeinsam/reglerabbildung.js';
import { Metaregler } from '../gemeinsam/metaregler.js';
import { fn } from '../gemeinsam/registrierung.js';

/**
 * Gemeinsameregler — ein Name, zwei Übersetzungen.
 *
 * WARUM (Edgar, 06.09.2026): „UMA formt über Knochen, dein HumanBody über
 * einzelne Punkte. Wie kann ich beide Welten vereinen ohne Genauigkeit zu
 * verlieren?" Nicht auf der Technik-Ebene, sondern hier: Ein fachlicher
 * Regler („Oberarm Länge") steht für beide Figurarten an derselben Stelle
 * und stellt darunter, was die jeweilige Welt kennt — bei UMA Knochen
 * (`inst.dna`), bei HumanBody Punkte (`inst.morphs`).
 *
 * Die Tabelle ist kein Ersatz: darunter bleiben die UMA-Reglergruppen und die
 * 216 Morphs unverändert stehen. Verloren geht nichts, gewonnen ist ein
 * Bedienfeld, das für beide Figuren gleich aussieht.
 *
 * Die Gruppe „Nur UMA" führt Regler, für die HumanBody keinen Morph hat. Sie
 * erscheint nur bei einer UMA-Figur, dort aber vollständig — von den 62
 * Reglern einer Rasse fällt keiner unter den Tisch (Edgar, 06.09.2026).
 *
 * Tabelle und Umrechnung: `humanbody_core.regler` (Python, eine Quelle) und
 * `gemeinsam/reglerabbildung.js`.
 *
 * KEIN Import von `state.js` oder `undo.js`: Was die Klasse von außen braucht
 * (Morphdefinitionen, die gemessene UMA-Höhe, der Rückruf nach dem Stellen),
 * kommt als Parameter; gemeldet wird über `fn.markDirty`. Nur so lässt sich
 * das Modul in Node prüfen — `state.js` zieht Three.js mit und lädt dort
 * nicht (`test_js_gemeinsameregler`).
 */
export class Gemeinsameregler {

    static BEREICH = 'prop-gemeinsam-section';
    static ADRESSE = '/api/character/regler/gemeinsam/';
    static _tabelle = null;

    /** Die Tabelle einmal je Sitzung holen. */
    static async tabelle() {
        if (!Gemeinsameregler._tabelle) {
            Gemeinsameregler._tabelle = await Serverabruf.json(Gemeinsameregler.ADRESSE);
        }
        return Gemeinsameregler._tabelle;
    }

    /**
     * Den Block für eine Figur bauen.
     *
     * @param inst      Figur (UMA oder HumanBody)
     * @param optionen  `morphDefs` aus /api/character/morphs/, `nachAenderung`
     *                  (nach jedem Stellen, damit die Einzelregler darunter
     *                  nachziehen) und `cm` (misst die Höhe einer UMA-Figur)
     */
    static async fuellen(inst, optionen = {}) {
        const bereich = document.getElementById(Gemeinsameregler.BEREICH);
        if (!bereich) return;
        const behaelter = document.getElementById('prop-gemeinsam-liste');
        behaelter.innerHTML = '';
        bereich.classList.remove('hb-versteckt');
        let tabelle;
        try {
            tabelle = await Gemeinsameregler.tabelle();
        } catch (e) {
            console.error('Gemeinsame Regler nicht geladen:', e);
            bereich.classList.add('hb-versteckt');
            return;
        }
        const umgebung = Gemeinsameregler._umgebung(inst, optionen);
        let gezeigt = 0;
        for (const gruppe of tabelle.gruppen) {
            const zeilen = gruppe.regler
                .filter(e => Reglerabbildung.gilt(e, umgebung))
                .map(e => Gemeinsameregler._zeile(inst, e, umgebung));
            if (!zeilen.length) continue;
            gezeigt += zeilen.length;
            behaelter.appendChild(Gemeinsameregler._gruppe(gruppe.name, zeilen));
        }
        // Nicht mehr „die es in beiden Welten gibt": seit die Gruppe „Nur UMA"
        // dazugehört, stimmt das nur noch für einen Teil (Edgar, 06.09.2026).
        document.getElementById('prop-gemeinsam-kopf').textContent =
            `${gezeigt} Regler · ` + (umgebung.dna ? 'stellt Knochen' : 'stellt Punkte');
    }

    static leeren() {
        document.getElementById(Gemeinsameregler.BEREICH)
            ?.classList.add('hb-versteckt');
    }

    /** Nach einer Änderung an den Einzelreglern die gemeinsamen nachziehen. */
    static angleichen(inst) {
        const umgebung = Gemeinsameregler._umgebung(inst, {});
        for (const schieber of document.querySelectorAll('#prop-gemeinsam-liste input[data-regler]')) {
            const eintrag = schieber._eintrag;
            if (!eintrag || eintrag.einheit) continue;
            const wert = umgebung.dna
                ? Reglerabbildung.ausUma(eintrag, inst.dna)
                : Reglerabbildung.ausHumanbody(eintrag, inst.morphs || {});
            if (wert === null) continue;
            schieber.value = Math.round(wert);
            Gemeinsameregler._anzeigen(schieber, Math.round(wert));
        }
    }

    // -- innen ----------------------------------------------------------------

    /** Was diese Figur ist und wie man sie stellt. */
    static _umgebung(inst, optionen) {
        const uma = inst.quelle === 'uma';
        const defs = optionen.morphDefs || {};
        return {
            dna: uma ? (inst.dna || {}) : null,
            morphnamen: new Set((defs.morphs || []).map(m => m.name)),
            meta: defs.meta_sliders || {},
            nachAenderung: optionen.nachAenderung || null,
            cm: optionen.cm || (() => '?'),
        };
    }

    static _gruppe(name, zeilen) {
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe';
        kasten.open = true;
        const titel = document.createElement('summary');
        titel.textContent = `${name} (${zeilen.length})`;
        kasten.appendChild(titel);
        for (const zeile of zeilen) kasten.appendChild(zeile);
        return kasten;
    }

    static _zeile(inst, eintrag, umgebung) {
        if (eintrag.einheit) return Gemeinsameregler._einheitenzeile(inst, eintrag, umgebung);
        const stand = umgebung.dna
            ? Reglerabbildung.ausUma(eintrag, inst.dna)
            : Reglerabbildung.ausHumanbody(eintrag, inst.morphs || {});
        const wert = Math.round(stand ?? 0);
        const zeile = Gemeinsameregler._bauen(eintrag, -100, 100, wert, wert);
        const schieber = zeile.querySelector('input');
        // UMA rechnet im Browser (sofort), HumanBody holt das Netz vom Server
        // (erst beim Loslassen, sonst ein Aufruf je Pixel).
        schieber.addEventListener('input', () => {
            Gemeinsameregler._anzeigen(schieber, schieber.value);
            if (umgebung.dna) Gemeinsameregler._stellen(inst, eintrag, schieber.value, umgebung);
        });
        schieber.addEventListener('change', () => {
            if (!umgebung.dna) Gemeinsameregler._stellen(inst, eintrag, schieber.value, umgebung);
            fn.markDirty?.(`Regler ${eintrag.anzeige}`);
        });
        return zeile;
    }

    /**
     * Die Größe. Sie trägt eine echte Einheit, und deshalb unterscheiden sich
     * die Skalen: HumanBody führt einen Metaregler in Zentimetern, bei UMA
     * ist `height` ein Knochenmaß 0..1, dessen Wirkung an der Figur GEMESSEN
     * wird (`Umamasse.cm`, als `cm` hereingereicht). Beide zeigen cm an, nur
     * der Schieber ist ein anderer — das ist ehrlicher, als aus 0..1 eine
     * Zentimeterzahl zu rechnen, die nicht stimmt.
     */
    static _einheitenzeile(inst, eintrag, umgebung) {
        if (umgebung.dna) {
            const wert = Math.round((inst.dna[eintrag.uma[0]] ?? 0.5) * 100);
            const zeile = Gemeinsameregler._bauen(eintrag, 0, 100, wert, `${umgebung.cm(inst)} cm`);
            const schieber = zeile.querySelector('input');
            schieber.addEventListener('input', () => {
                inst.dna[eintrag.uma[0]] = parseInt(schieber.value, 10) / 100;
                umgebung.nachAenderung?.();
                inst.anwenden?.();
                Gemeinsameregler._anzeigen(schieber, `${umgebung.cm(inst)} cm`);
            });
            schieber.addEventListener('change', () => fn.markDirty?.(`Regler ${eintrag.anzeige}`));
            return zeile;
        }
        const grenze = umgebung.meta[eintrag.meta] || { min: 150, max: 200 };
        const cm = Math.round(Metaregler.aussen(inst.meta?.[eintrag.meta] || 0,
                                                grenze.min, grenze.max));
        const zeile = Gemeinsameregler._bauen(eintrag, grenze.min, grenze.max, cm, `${cm} cm`);
        const schieber = zeile.querySelector('input');
        schieber.addEventListener('input',
            () => Gemeinsameregler._anzeigen(schieber, `${schieber.value} cm`));
        schieber.addEventListener('change', () => {
            inst.meta[eintrag.meta] = Metaregler.innen(parseFloat(schieber.value),
                                                       grenze.min, grenze.max);
            umgebung.nachAenderung?.();
            fn.markDirty?.(`Regler ${eintrag.anzeige}`);
        });
        return zeile;
    }

    /** Einen gemeinsamen Wert in die Figur schreiben — Knochen oder Punkte. */
    static _stellen(inst, eintrag, roh, umgebung) {
        const wert = parseInt(roh, 10);
        if (umgebung.dna) {
            Object.assign(inst.dna, Reglerabbildung.umaWerte(eintrag, wert));
            inst.anwenden?.();
        } else {
            inst.morphs = inst.morphs || {};
            for (const [name, zahl] of Object.entries(
                    Reglerabbildung.humanbodyWerte(eintrag, wert))) {
                if (Math.abs(zahl) < 0.005) delete inst.morphs[name];
                else inst.morphs[name] = zahl;
            }
        }
        umgebung.nachAenderung?.();
    }

    static _bauen(eintrag, min, max, wert, anzeige) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const beschriftung = document.createElement('label');
        beschriftung.textContent = eintrag.anzeige;
        beschriftung.title = [...(eintrag.uma || []), ...(eintrag.humanbody || [])].join(', ');
        const schieber = document.createElement('input');
        Object.assign(schieber, { type: 'range', min, max, step: 1, value: wert });
        schieber.dataset.regler = eintrag.name;
        schieber._eintrag = eintrag;
        const feld = document.createElement('span');
        feld.className = 'slider-val';
        feld.textContent = anzeige;
        zeile.append(beschriftung, schieber, feld);
        return zeile;
    }

    static _anzeigen(schieber, text) {
        const feld = schieber.parentElement?.querySelector('.slider-val');
        if (feld) feld.textContent = text;
    }
}
