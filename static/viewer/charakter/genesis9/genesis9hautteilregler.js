import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Genesis9hautteile } from '../../gemeinsam/genesis9hautteile.js';
import { Genesis9hautteilfenster } from './genesis9hautteilfenster.js';

/**
 * Genesis9hautteilregler — die Texturregler je Körperteil im Abschnitt „Eigen“ (25.10.2026, Edgar: „bei den Reglern für die einzelnen Körperteile mach jeweils auch Regler für
 * die Textur“, „den Code für Haut-KI kannst du einige Punkte entnehmen, z.B. Tattoos, Hautfarbe usw“).
 *
 * Je Ziel der Gruppe (`Genesis9hautteile.ZIELE`: Kopf, Hals, Rumpf; Arme/Hände/Beine/Füße je „beide“, links, rechts) zwei Zeilen: „Hautfarbe …“ (Schieber = Stärke) und
 * „Tattoo …“ (Schieber = Deckung), dazu der Knopf ins Fenster (`Genesis9hautteilfenster`) mit einem Farbtupfer der Zielfarbe bzw. Tinte. Ein Zug wirkt sofort (Uniforms);
 * gespeichert wird mit der Figur (`inst.hautebenen`). Eingehängt von `Genesis9eigenregler.fuellen` hinter den Formreglern der Gruppe.
 */
export class Genesis9hautteilregler {

    static ARTEN = {
        farbe: { titel: 'Hautfarbe', knopf: 'Farbe …', ohne: 'Farbe wählen …',
                 hilfe: 'Stärke: färbt die Haut dieses Teils zur Zielfarbe hin (Poren und Zeichnung bleiben). Die Zielfarbe steht im Fenster „Farbe …“.' },
        tattoo: { titel: 'Tattoo', knopf: 'Tattoo …', ohne: 'Tattoo …',
                  hilfe: 'Deckung des Tattoos auf diesem Teil. Muster, Fläche, Größe, Stil und Tinte im Fenster „Tattoo …“.' },
        // Hautebenen je Teil (26.10.2026, `Genesis9hautteilmerkmale`): Schieber = Stärke aller Merkmale dieses Teils, die Merkmale im Fenster
        merkmal: { titel: 'Hautmerkmale', knopf: 'Merkmale …', ohne: 'Merkmale …',
                   hilfe: 'Stärke der Hautmerkmale dieses Teils (Sommersprossen, Muttermale, Aknenarben, Pickel, Cellulite, Ton, Rötung …) — die Merkmale selbst im Fenster „Merkmale …“, als Zuschlag auf die Hautregler der ganzen Figur.' },
    };

    static REIHE = ['farbe', 'tattoo', 'merkmal'];

    /** Die Zeilen einer Gruppe des Abschnitts „Eigen“ (Kopf, Hals, Rumpf, Arme, Hände, Beine, Füße) — erst alle Hautfarben, dann alle Tattoos, dann die Hautmerkmale. */
    static zeilen(inst, gruppe) {
        const ziele = Genesis9hautteile.ZIELE.filter(z => z.gruppe === gruppe && !(z.ganz));
        const ganz = Genesis9hautteile.ZIELE.filter(z => z.gruppe === gruppe && z.ganz);
        // „gesamt“ (Gruppe Haut) hat keine Hautmerkmale — das sind die Hautregler der ganzen Figur
        return Genesis9hautteilregler.REIHE.flatMap(art => (art === 'merkmal' ? ziele : [...ganz, ...ziele]).map(z => Genesis9hautteilregler.zeile(inst, art, z)));
    }

    static zeile(inst, art, z) {
        const a = Genesis9hautteilregler.ARTEN[art];
        const schluessel = Genesis9hautteile.schluessel(art, z.ziel);
        const kennung = `g9-hautteil-${art}-${z.ziel}`;
        const wert = Math.round(Genesis9hautteile.wert(inst, art, z.ziel));
        const zeile = document.createElement('div');
        zeile.className = 'slider-row g9-hautteil-zeile';
        zeile.innerHTML = `
            <label for="${kennung}" title="${escapeHtml(a.hilfe)}">${escapeHtml(`${a.titel} ${z.name}`)}</label>
            <input type="range" id="${kennung}" data-hautteil="${schluessel}" min="0" max="100" step="1" value="${wert}"
                   title="${escapeHtml(a.hilfe)} · Doppelklick: 0">
            <span class="slider-value">${wert} %</span>`;
        const schieber = zeile.querySelector('input');
        schieber.addEventListener('input', () => {
            const neu = parseInt(schieber.value, 10) || 0;
            Genesis9hautteilregler._zeigen(schluessel, neu);
            Genesis9hautteilfenster.stellen(inst, { [schluessel]: neu });
        });
        schieber.addEventListener('change', () => markDirty());
        schieber.addEventListener('dblclick', () => {
            schieber.value = 0;
            schieber.dispatchEvent(new Event('input'));
            markDirty();
        });
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn-toggle g9-eigenregler-knopf';
        knopf.dataset.hautteilKnopf = `${art}:${z.ziel}`;
        knopf.title = `${a.titel} ${z.name} einstellen`;
        knopf.addEventListener('click', () => Genesis9hautteilfenster.oeffnen({ inst, art, ziel: z, nachher: () => Genesis9hautteilregler.nachziehen(inst) }));
        zeile.appendChild(knopf);
        Genesis9hautteilregler._knopf(inst, knopf);
        return zeile;
    }

    /** Knopftext mit Farbtupfer (Zielfarbe bzw. Tinte); ohne gewählte Zielfarbe „Farbe wählen …“. */
    static _knopf(inst, knopf) {
        const [art, ziel] = knopf.dataset.hautteilKnopf.split(':');
        const a = Genesis9hautteilregler.ARTEN[art];
        if (art === 'merkmal') { knopf.textContent = a.knopf; return; }           // kein Farbtupfer
        const gewaehlt = art === 'tattoo' || Genesis9hautteile.wert(inst, 'farbe', ziel, 'r') !== null;
        const farbe = Genesis9hautteilfenster.hex(Genesis9hautteilfenster.farbe(inst, art, ziel));
        knopf.innerHTML = `<span class="g9-hautteil-tupfer" style="background:${farbe}"></span>${escapeHtml(gewaehlt ? a.knopf : a.ohne)}`;
    }

    static _zeigen(schluessel, wert) {
        for (const schieber of document.querySelectorAll(`input[data-hautteil="${schluessel}"]`)) {
            if (String(schieber.value) !== String(wert)) schieber.value = wert;
            const anzeige = schieber.parentElement?.querySelector('.slider-value');
            if (anzeige) anzeige.textContent = `${wert} %`;
        }
    }

    /** Alle Zeilen auf den Stand der Figur (nach dem Fenster, nach „Zurücksetzen“). */
    static nachziehen(inst) {
        for (const z of Genesis9hautteile.ZIELE) {
            for (const art of Genesis9hautteilregler.REIHE) Genesis9hautteilregler._zeigen(Genesis9hautteile.schluessel(art, z.ziel), Math.round(Genesis9hautteile.wert(inst, art, z.ziel)));
        }
        for (const knopf of document.querySelectorAll('[data-hautteil-knopf]')) Genesis9hautteilregler._knopf(inst, knopf);
    }
}
