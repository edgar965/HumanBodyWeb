import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { escapeHtml } from '../utils.js';

/**
 * Umagarderobe — was eine UMA-Figur trägt: Rasse und Kleidungsstücke aus dem
 * Beipackzettel des Figurkatalogs, für die Reiter „Kleider" und „Assets".
 *
 * WARUM (05.09.2026): Dort stand für UMA-Figuren nur der Satz „Kleidung
 * kommt aus Unity" (Edgar: „was soll dieser dumme Hinweis??"). Die Kleidung
 * wird in Unity zusammengebaut — hier steht deshalb, WAS gebaut wurde.
 *
 * Der Zettel nennt Rasse und Stücke im Feld `hinweis` als Satz:
 * „Rasse Human Male 3.0, 12 Kleidungsstücke: A (Face), B (Hair) … . Erzeugt …".
 * Eine bewegte Fassung (`…_bewegt.glb`) trägt im Zettel nur die Animationen;
 * ihre Vorlage liegt unverändert daneben, also gilt deren Zettel.
 */
export class Umagarderobe {

    static ADRESSE = '/api/character/uma-figur/';
    static MUSTER = /Rasse ([^,]+),\s*\d+ Kleidungsstücke:\s*(.*?)\.\s*Erzeugt/s;
    static STUECK = /^(.*?)\s*\(([^()]*)\)$/;
    static BEWEGT = /_bewegt(\.glb)$/i;
    static _gelesen = new Map();

    /** `{rasse, teile: [{rezept, platz}], stand}` aus dem Zettel — `null`, wenn er nichts sagt. */
    static parsen(zettel) {
        const treffer = Umagarderobe.MUSTER.exec(zettel?.hinweis || '');
        if (!treffer) return null;
        const teile = treffer[2].split(/,\s*/).map(text => {
            const t = Umagarderobe.STUECK.exec(text.trim());
            return t ? { rezept: t[1], platz: t[2] } : { rezept: text.trim(), platz: '' };
        });
        return { rasse: treffer[1].trim(), teile, stand: zettel.stand || '' };
    }

    /** Die Garderobe einer Figur; bewegte Fassung → Zettel der Vorlage. Einmal je Datei. */
    static lesen(datei) {
        if (!Umagarderobe._gelesen.has(datei)) {
            Umagarderobe._gelesen.set(datei, Umagarderobe._holen(datei));
        }
        return Umagarderobe._gelesen.get(datei);
    }

    static async _holen(datei) {
        for (const name of [datei, datei.replace(Umagarderobe.BEWEGT, '$1')]) {
            try {
                const garderobe = Umagarderobe.parsen(await Serverabruf.json(
                    `${Umagarderobe.ADRESSE}${encodeURIComponent(name)}/zettel/`));
                if (garderobe) return garderobe;
            } catch (fehler) {
                if (fehler?.status !== 404) throw fehler;
            }
        }
        return null;
    }

    /** Den Platzhalter eines Reiters mit der Garderobe der Figur füllen. */
    static async fuellen(element, figur) {
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        let garderobe = null;
        try {
            garderobe = await Umagarderobe.lesen(figur.datei);
        } catch (fehler) {
            console.warn('Umagarderobe: Zettel nicht lesbar:', fehler);
        }
        element.innerHTML = Umagarderobe.html(figur, garderobe);
    }

    static html(figur, garderobe) {
        const kopf = `<div class="uma-garderobe-kopf">${escapeHtml(figur.datei)}</div>`;
        if (!garderobe) {
            return `<div class="uma-garderobe">${kopf}<div>Der Beipackzettel nennt keine Kleidung.</div></div>`;
        }
        const zeilen = garderobe.teile.map(t =>
            `<li><span class="uma-garderobe-platz">${escapeHtml(t.platz)}</span>`
            + `${escapeHtml(t.rezept)}</li>`).join('');
        return `<div class="uma-garderobe">${kopf}`
            + `<div><b>Rasse</b> ${escapeHtml(garderobe.rasse)}</div>`
            + `<ul>${zeilen}</ul>`
            + `<div class="uma-garderobe-fuss">In Unity gebaut, Stand ${escapeHtml(garderobe.stand)}</div>`
            + '</div>';
    }
}
