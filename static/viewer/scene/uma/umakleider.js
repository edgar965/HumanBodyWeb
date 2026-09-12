import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { escapeHtml } from '../utils.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Umagarderobe } from './umagarderobe.js';
import { Umatyp } from './umatyp.js';
import { Umabauerstand } from './umabauerstand.js';

/**
 * Umakleider — die Kleidung einer UMA-Figur wählen und von Unity bauen lassen.
 *
 * WARUM (06.09.2026, Edgar: „Was ist mit den Kleidern, auch Loop über Unity?"):
 * Ja, eine Schleife — aber eine für alles: je Kleidungsplatz ein Rezept aus
 * dem Angebot der Rasse (`GET uma-garderobe/`), dann ein Bau in Unity
 * (`POST uma-figur/bauen/` mit `kleidung`), danach steht die neue Datei im
 * Katalog und die Figur wird getauscht. Vorbelegt ist, was die Figur laut
 * Zettel trägt.
 */
export class Umakleider {

    static ADRESSE = '/api/character/uma-garderobe/';

    static async fuellen(element, figur) {
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        let garderobe = null;
        try {
            garderobe = await Umagarderobe.lesen(figur.datei);
        } catch (fehler) {
            Protokoll.warnung('Umakleider', 'Zettel nicht lesbar:', fehler);
        }
        const rasse = garderobe?.rasse;
        if (!rasse) {
            element.innerHTML = Umagarderobe.html(figur, garderobe)
                + '<div class="uma-garderobe-fuss">Ohne Rasse im Zettel gibt es keine Auswahl.</div>';
            return;
        }
        let angebot;
        try {
            angebot = await Serverabruf.json(`${Umakleider.ADRESSE}?rasse=${encodeURIComponent(rasse)}`);
        } catch (fehler) {
            element.innerHTML = `<div class="uma-garderobe">Angebot nicht ladbar: ${escapeHtml(fehler.message)}</div>`;
            return;
        }
        element.innerHTML = '';
        element.appendChild(Umakleider._kasten(figur, rasse, garderobe, angebot));
    }

    static _kasten(figur, rasse, garderobe, angebot) {
        const getragen = new Map((garderobe.teile || []).map(t => [t.platz, t.rezept]));
        const kasten = document.createElement('div');
        kasten.className = 'uma-garderobe';
        kasten.innerHTML = `<div class="uma-garderobe-kopf">${escapeHtml(figur.datei)} · ${escapeHtml(rasse)}</div>`
            + `<div>${angebot.anzahl} Rezepte für diese Rasse, je Platz eines:</div>`;
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
                if (getragen.get(platz.platz) === rezept.name) eintrag.selected = true;
                auswahl.appendChild(eintrag);
            }
            zeile.append(label, auswahl);
            kasten.appendChild(zeile);
        }
        const knopf = document.createElement('button');
        knopf.className = 'btn-toggle hb-volle-breite';
        knopf.innerHTML = '<i class="fas fa-hammer"></i> In Unity bauen';
        const stand = document.createElement('div');
        stand.className = 'uma-garderobe-fuss';
        const bauer = document.createElement('div');
        bauer.className = 'uma-garderobe-fuss';
        knopf.addEventListener('click', () => Umakleider.bauen(figur, rasse, kasten, stand));
        Umabauerstand.anzeigen(bauer, { vorwaermen: true });
        // Eine geänderte Liste ändert die Figur noch nicht — das sagt die Zeile
        // unter dem Knopf, bis gebaut wird (Edgar, 06.09.2026: „Warum ändern
        // sich die Kleider nicht, wenn ich die ändere?").
        for (const auswahl of kasten.querySelectorAll('select')) {
            auswahl.addEventListener('change', () => {
                const geaendert = [...kasten.querySelectorAll('select')]
                    .filter(s => (getragen.get(s.dataset.platz) || '') !== s.value)
                    .map(s => s.dataset.platz);
                knopf.classList.toggle('active', geaendert.length > 0);
                stand.textContent = geaendert.length
                    ? `Geändert: ${geaendert.join(', ')} — noch nicht gebaut. „In Unity bauen" drücken.`
                    : '';
            });
        }
        kasten.append(knopf, stand, bauer);
        return kasten;
    }

    /**
     * Die gewählten Rezepte bauen lassen — über `Umatyp.neuBauen`, das die
     * Farben der Figur mitnimmt und den Dateinamen aus Rasse und Auswahl bildet.
     */
    static bauen(figur, rasse, kasten, stand) {
        const kleidung = [...kasten.querySelectorAll('select')].map(s => s.value).filter(Boolean);
        return Umatyp.neuBauen(figur, { rasse, kleidung, stand });
    }
}
