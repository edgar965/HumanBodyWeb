import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';

/**
 * Recherchehuman3dprio — die Spalte „Prio" der Recherche-Tabelle (04.10.2026).
 *
 * Edgar: „mach in der Tabelle eine neue Spalte: Prio mit veränderbaren Zahlen, ich möchte darin die Prio eingeben, ob wir das testen / einbauen. keine zwei gleiche Prios, wenn ich was
 * ändere schiebt sich das dazwischen". Jede Zeile trägt ein Zahlenfeld (`input.rc-prio`, `data-id` = Projektkennung). Eine Änderung geht sofort an
 * `/hilfe/recherche/human-3d/prio/` (Server: `Rechercheprio`). Trägt die Zahl schon ein anderes Projekt, rückt dieses nach hinten — der Server liefert deshalb die ganze Zuordnung,
 * und `nachziehen` stellt damit die Felder ALLER Zeilen nach, sonst stünde in der Tabelle ein Stand, den der Server nicht mehr hat. Scheitert das Speichern, springt das Feld auf den alten
 * Wert zurück: ein stehen gebliebener neuer Wert behauptete etwas, das der Server nicht hat. Leer lassen = keine Prio.
 */
export class Recherchehuman3dprio {

    static ADRESSE = '/hilfe/recherche/human-3d/prio/';
    /** `data-sort` einer Zelle ohne Prio: ans Ende sortiert, nicht vor Prio 1 (wie `Rechercheprio::SORT_OHNE_PRIO`). */
    static SORT_OHNE_PRIO = 999999;

    /** Hört auf die Felder der Tabelle (Ereignisdelegation: eine Zeile muss nicht einzeln gebunden werden). */
    static binden(tabelle) {
        tabelle.addEventListener('change', e => {
            const feld = e.target instanceof Element ? e.target.closest('input.rc-prio') : null;
            if (feld) Recherchehuman3dprio.speichern(feld, tabelle);
        });
    }

    static async speichern(feld, tabelle) {
        const vorher = feld.dataset.vorher ?? '';
        const text = feld.value.trim();
        const zahl = text === '' ? null : Number(text.replace(',', '.'));
        if (zahl !== null && (!Number.isInteger(zahl) || zahl < 1)) {
            feld.value = vorher;
            window.alert('Die Prio muss eine ganze Zahl ab 1 sein (oder leer).');
            return;
        }
        feld.disabled = true;
        try {
            const antwort = await Serverabruf.senden(Recherchehuman3dprio.ADRESSE, { id: feld.dataset.id, prio: zahl });
            if (antwort.error) throw new Error(antwort.error);
            Recherchehuman3dprio.nachziehen(tabelle, antwort.prios || {});
        } catch (fehler) {
            feld.value = vorher;
            window.alert(`Die Prio konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
        } finally {
            feld.disabled = false;
        }
    }

    /** Stellt alle Felder nach dem Stand des Servers nach: `prios` = `{Projektkennung: Prio}` aller eingestuften Projekte. */
    static nachziehen(tabelle, prios) {
        for (const feld of tabelle.querySelectorAll('input.rc-prio')) {
            const prio = prios[feld.dataset.id] || 0;
            feld.value = prio ? String(prio) : '';
            feld.dataset.vorher = feld.value;
            feld.classList.toggle('rc-prio-gesetzt', Boolean(prio));
            feld.closest('td')?.setAttribute('data-sort', String(prio || Recherchehuman3dprio.SORT_OHNE_PRIO));
        }
    }
}
