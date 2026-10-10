import { Serverabruf } from './serverabruf.js';

/**
 * Figurwahlimporte — abgebrochene Blender-Importe in der Liste „Gespeicherte Modelle" des Genesis-9-Reiters (10.10.2026).
 *
 * Edgar (10.10.2026): „ein abgebrochener Import soll bei der Modell-Liste (mit Fehlerzeichen) sichtbar sein, damit ich ihn löschen
 * kann". Ein Import, der nicht fertig wurde (gescheitert, angehalten, Arbeitsprozess weg) hat kein Modell und wäre nirgends zu
 * finden; der Server nennt ihn „verwaist" (`/api/character/blendimport/verwaist/`, `Blendimportloeschen`). Er steht in der Liste
 * wie ein Modell — mit rotem Warnzeichen vor dem Namen, dem Grund und der Größe in der Unterzeile — und lässt sich nur löschen.
 */
export class Figurwahlimporte {

    static ADRESSE = '/api/character/blendimport/verwaist/';

    /**
     * Die Zeilen der verwaisten Importe für `Figurkataloge`. Ein Fehler beim Abruf lässt die Modelle nicht verschwinden: leere Liste.
     * `name` ist die Kennung des Imports (eindeutig), `anzeige` der Name der Figur. Nur der Genesis-9-Reiter hat Importe: für jede
     * andere `quelle` kommt die leere Liste, ohne dass der Server gefragt wird.
     */
    static async zeilen(quelle = 'genesis9') {
        if (quelle !== 'genesis9') return [];
        try {
            const antwort = await Serverabruf.json(Figurwahlimporte.ADRESSE);
            return (antwort.importe || []).map(Figurwahlimporte.zeile);
        } catch (_) {
            return [];
        }
    }

    static zeile(plan) {
        const datum = Figurwahlimporte.datum(plan.kennung);
        return {
            name: plan.kennung,
            anzeige: `${plan.name} (Import)`,
            unterzeile: `${plan.verwaist} · ${datum} · ${plan.mb} MB`,
            warnung: `Abgebrochener Import — ${plan.verwaist}`,
            bereich: 'gespeichert',
            verwaist: true,
            importKennung: plan.kennung,
        };
    }

    /** `2026.10.09.23.08.44` → `09.10.2026 23:08`; eine fremde Form bleibt, wie sie ist. */
    static datum(kennung) {
        const teile = String(kennung).split('.');
        return teile.length >= 5
            ? `${teile[2]}.${teile[1]}.${teile[0]} ${teile[3]}:${teile[4]}` : String(kennung);
    }

    /**
     * Am Ende der gespeicherten Liste: „Alle verwaisten Importe löschen (N)", wenn es welche gibt.
     * @param behaelter  der Reiter (`#<kennung>-liste-genesis9`)
     * @param zahl       Anzahl der verwaisten Zeilen
     * @param tun        () => void — ruft die Pflege
     */
    static aufraeumen(behaelter, zahl, tun) {
        behaelter.querySelector('li[data-aufraeumen]')?.remove();
        const liste = behaelter.querySelector('ul[data-bereich="gespeichert"]');
        if (!liste || !zahl) return;
        const li = document.createElement('li');
        li.dataset.aufraeumen = '1';
        li.className = 'gedaempft';
        li.innerHTML = '<button class="knopf-schmal" type="button"><i class="fas fa-eraser"></i> '
            + `Alle verwaisten Importe löschen (${zahl})</button>`;
        li.querySelector('button').addEventListener('click', tun);
        liste.appendChild(li);
    }
}
