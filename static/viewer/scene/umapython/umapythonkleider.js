import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';

/**
 * Umapythonkleider — die Kleidung einer UMA-Python-Figur wählen; der Port zieht an.
 *
 * WARUM (Edgar, 25.09.2026: „baue das zwischendurch für UMA: Der Unity-Bau
 * zieht die Kleidung wirklich an. Der Python-Port kann das auch"): `Figur.bauen`
 * nahm längst `kleidung=…`, aber der Browser schickte nur Rasse und DNA — die
 * Port-Figur war immer nackt. Das Angebot ist dasselbe wie beim Unity-Bau
 * (`GET uma-garderobe/?rasse=`, `Umakleider`): je Platz ein Rezept.
 *
 * ANDERS ALS BEIM UNITY-BAU OHNE KNOPF: Eine Wahl baut sofort. Edgar hatte
 * beim Unity-Weg gefragt „Warum ändern sich die Kleider nicht, wenn ich die
 * ändere?" (06.09.2026); dort kostet ein Bau Unity, hier 6–14 s im Server
 * beim ersten Mal, danach kommt er aus der Ablage (Rasse + Kleidung). Während
 * ein Bau läuft, sind die Listen gesperrt — zwei Bauten gleichzeitig würden
 * sich überholen.
 */
export class Umapythonkleider {

    static ADRESSE = '/api/character/uma-garderobe/';
    static FELD = 'prop-umapython-kleidung';

    static async fuellen(inst) {
        const feld = document.getElementById(Umapythonkleider.FELD);
        if (!feld) return;
        feld.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        let angebot;
        try {
            angebot = await Serverabruf.json(
                `${Umapythonkleider.ADRESSE}?rasse=${encodeURIComponent(inst.rasse)}`);
        } catch (fehler) {
            feld.innerHTML = `<div class="gedaempft">Angebot nicht ladbar: ${escapeHtml(fehler.message)}</div>`;
            return;
        }
        feld.innerHTML = '';
        if (!angebot?.plaetze?.length) {
            feld.innerHTML = '<div class="gedaempft">Für diese Rasse führt UMA keine Kleidung.</div>';
            return;
        }
        feld.appendChild(Umapythonkleider._kasten(inst, angebot));
    }

    static _kasten(inst, angebot) {
        const getragen = new Set(inst.kleidung || []);
        const kasten = document.createElement('div');
        kasten.className = 'uma-garderobe';
        kasten.innerHTML = `<div>${angebot.anzahl} Rezepte für diese Rasse, je Platz eines:</div>`;
        for (const platz of angebot.plaetze) {
            const zeile = document.createElement('div');
            zeile.className = 'slider-row';
            const label = document.createElement('label');
            label.textContent = platz.platz;
            label.title = platz.platz;
            const auswahl = document.createElement('select');
            auswahl.className = 'viewer-select hb-dehnt-ohne-abstand';
            auswahl.dataset.platz = platz.platz;
            auswahl.appendChild(new Option('— nichts —', ''));
            for (const rezept of platz.rezepte) {
                const eintrag = new Option(rezept.name, rezept.name);
                if (getragen.has(rezept.name)) eintrag.selected = true;
                auswahl.appendChild(eintrag);
            }
            auswahl.addEventListener('change', () => Umapythonkleider._anziehen(inst, kasten, stand));
            zeile.append(label, auswahl);
            kasten.appendChild(zeile);
        }
        const stand = document.createElement('div');
        stand.className = 'uma-garderobe-fuss';
        stand.textContent = Umapythonkleider._text(inst);
        kasten.appendChild(stand);
        return kasten;
    }

    static _text(inst) {
        const n = (inst.kleidungGetragen || inst.kleidung || []).length;
        const fehlend = (inst.kleidung || []).filter(k => inst.kleidungGetragen && !inst.kleidungGetragen.includes(k));
        return (n ? `${n} Stück(e) angezogen` : 'Nackt')
            + (fehlend.length ? ` · nicht im Katalog: ${fehlend.join(', ')}` : '');
    }

    static async _anziehen(inst, kasten, stand) {
        const listen = [...kasten.querySelectorAll('select')];
        const namen = listen.map(s => s.value).filter(Boolean);
        listen.forEach(s => { s.disabled = true; });
        stand.textContent = 'Baut … (beim ersten Mal 6–14 s)';
        const beginn = performance.now();
        try {
            await inst.kleidungSetzen(namen);
            markDirty();
            const s = ((performance.now() - beginn) / 1000).toFixed(1);
            stand.textContent = `${Umapythonkleider._text(inst)} · ${s} s`;
        } catch (fehler) {
            stand.textContent = `Fehler: ${fehler.message}`;
        } finally {
            listen.forEach(s => { s.disabled = false; });
        }
    }
}
