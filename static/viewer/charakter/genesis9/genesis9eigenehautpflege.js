import { Kontextmenue } from '../../gemeinsam/kontextmenue.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Genesis9eigenehaut } from '../../gemeinsam/genesis9eigenehaut.js';
import { markDirty } from '../undo.js';

/**
 * Genesis9eigenehautpflege — „Meine Häute": die gespeicherten eigenen Häute im Popup der Haut, mit Rechtsklick-Menü Umbenennen und Löschen (18.10.2026).
 *
 * Edgar, 18.10.2026: „es sollen doch ALLE Assets umbenannt und gelöscht werden können?" — eigene Häute (`Genesis9eigenehaut`) ließen sich nur speichern. Die Auswahl „Haut" ist ein
 * `<select>`, dessen Einträge kein Menü tragen können; darum steht die Liste unter „Als eigene Haut speichern" im Popup (`Genesis9hautdialogblock`).
 *
 *   Umbenennen  ändert nur den Anzeigenamen; die Kennung `eigen:<schluessel>` bleibt, gespeicherte Modelle nennen sie weiter (Server: `G9eigenehautpflege`).
 *   Löschen     ohne Rückfrage; das Rezept liegt danach im Papierkorb des Servers. Trägt die Figur die Haut gerade, bekommt sie den Grundsatz des Rezepts zurück (dieselben Bilder,
 *               die Regler bleiben); andere Figuren mit dieser Haut nehmen beim nächsten Bau die Haut ihres Katalogeintrags.
 */
export class Genesis9eigenehautpflege {

    static adresse(eintrag, aktion) {
        const schluessel = eintrag.id.slice(Genesis9eigenehaut.PRAEFIX.length);
        return `${Genesis9eigenehaut.ADRESSE}${encodeURIComponent(schluessel)}/${aktion}/`;
    }

    /**
     * Die Liste der eigenen Häute (ein Kasten, `kasten.neu()` baut sie aus `plan.haut` neu); ohne Häute bleibt er unsichtbar.
     *
     * @param nachher  `() => void` — nach einer Änderung die Hautauswahl neu bauen (`Genesis9materialdialog.form.hautNeu`)
     */
    static liste(inst, plan, nachher) {
        const kasten = document.createElement('div');
        kasten.className = 'hb-hautspeichern hb-eigenehaeute';
        const neu = () => {
            const haeute = (plan.haut || []).filter(h => Genesis9eigenehaut.ist(h.id));
            kasten.hidden = !haeute.length;
            kasten.replaceChildren();
            const kopf = document.createElement('div');
            kopf.className = 'hb-formkopf';
            kopf.textContent = 'Meine Häute';
            const hinweis = document.createElement('div');
            hinweis.className = 'hb-font-size-0-72rem';
            hinweis.textContent = 'Rechtsklick auf eine Haut: Umbenennen, Löschen.';
            kasten.append(kopf, hinweis);
            for (const haut of haeute) kasten.appendChild(Genesis9eigenehautpflege._zeile(inst, plan, haut, () => { nachher?.(); neu(); }));
        };
        kasten.neu = neu;
        neu();
        return kasten;
    }

    static _zeile(inst, plan, haut, danach) {
        const zeile = document.createElement('div');
        zeile.className = 'hb-eigenehaut-zeile';
        zeile.textContent = haut.rezept?.name || haut.id;       // Namen des Nutzers — als TEXT
        zeile.title = 'Rechtsklick: Umbenennen, Löschen';
        Kontextmenue.binden(zeile, () => Genesis9eigenehautpflege.eintraege(inst, plan, haut, danach));
        return zeile;
    }

    static eintraege(inst, plan, haut, danach) {
        return [
            { symbol: 'fa-pen', text: 'Umbenennen …', tun: () => Genesis9eigenehautpflege.umbenennen(haut, danach) },
            { symbol: 'fa-trash', text: 'Löschen', tun: () => Genesis9eigenehautpflege.loeschen(inst, plan, haut, danach) },
        ];
    }

    static async umbenennen(haut, danach) {
        const alt = haut.rezept?.name || '';
        const neu = window.prompt(`Neuer Name für die Haut „${alt}":`, alt);
        if (neu === null || neu.trim() === alt) return;
        let antwort;
        try {
            antwort = await Serverabruf.senden(Genesis9eigenehautpflege.adresse(haut, 'umbenennen'), { name: neu });
        } catch (fehler) {
            Genesis9eigenehautpflege._misslungen('Umbenennen', alt, fehler);
            return;
        }
        if (antwort?.eintrag) Object.assign(haut, antwort.eintrag);     // der Eintrag in `plan.haut` bleibt dasselbe Objekt: Name und Rezept neu
        danach();
    }

    static async loeschen(inst, plan, haut, danach) {
        const name = haut.rezept?.name || haut.id;
        try {
            await Serverabruf.senden(Genesis9eigenehautpflege.adresse(haut, 'loeschen'), {});
        } catch (fehler) {
            Genesis9eigenehautpflege._misslungen('Löschen', name, fehler);
            return;
        }
        plan.haut = (plan.haut || []).filter(h => h.id !== haut.id);
        if (inst.haut === haut.id) {            // die Figur trägt sie: zurück auf den Grundsatz (gleiche Bilder), die Regler bleiben
            await inst.hautSetzen(haut.rezept?.grund || '');
            markDirty();
        }
        danach();
    }

    static _misslungen(titel, name, fehler) {
        const grund = fehler?.daten?.fehler || fehler?.message || 'unbekannter Fehler';
        Protokoll.fehler('Haut', `${titel} der Haut „${name}" fehlgeschlagen`, fehler);
        window.alert(`${titel} fehlgeschlagen: ${grund}`);
    }
}
