import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderqualitaet — die Handwertung „Qualität …" in der Liste von „2D3D Kleider" (03.10.2026).
 *
 * Jede Zeile trägt acht Auswahlfelder (`select.engine2d3dkleider-qualitaet`, `data-id`, `data-feld` = mesh | 3d | textur | mesh_gesamt |
 * kleider | haar | gesicht | koerper). Der Wert ist der RANG des Laufs in dieser Spalte: 1 = der beste, jeder Rang höchstens einmal. Eine
 * Änderung geht sofort an `/api/engine2d3dkleider/<id>/qualitaet/` — ohne Neuberechnung, es ist eine Kennzeichnung (Server:
 * `Engine2d3dKleiderqualitaet`, `Engine2d3dKleiderrang`). Vergibt man einen Rang, den schon ein anderer Lauf trägt, schiebt der Server die
 * anderen nach hinten und liefert die ganze Rangliste zurück; `nachziehen` stellt damit die Felder ALLER Zeilen der Spalte nach — sonst
 * stünde in der Liste ein Stand, den der Server nicht mehr hat.
 * Scheitert das Speichern, springt das Feld auf den alten Wert zurück: Ein stehen gebliebener neuer Wert würde etwas behaupten, was der
 * Server nicht hat.
 */
export class Engine2d3dKleiderqualitaet {

    static ADRESSE = id => `/api/engine2d3dkleider/${id}/qualitaet/`;
    static NAMEN = {
        mesh: 'Qualität Mesh', '3d': 'Qualität 3D', textur: 'Qualität Textur', mesh_gesamt: 'Qualität Mesh insgesamt',
        kleider: 'Qualität Kleider', haar: 'Qualität Haar', gesicht: 'Qualität Gesicht', koerper: 'Qualität Körper',
    };
    /** `data-sort` einer Zelle ohne Rang: ans Ende sortiert, nicht vor Rang 1 (wie `Engine2d3dKleiderqualitaet::SORT_OHNE_RANG`). */
    static SORT_OHNE_RANG = 999999;

    /** Hört auf die Auswahlfelder der Tabelle (Ereignisdelegation: die Zeilen entstehen auch neu, wenn die Liste sich aktualisiert). */
    static binden(tabelle) {
        tabelle.addEventListener('change', e => {
            const feld = e.target.closest('select.engine2d3dkleider-qualitaet');
            if (feld) Engine2d3dKleiderqualitaet.speichern(feld, tabelle);
        });
    }

    static async speichern(feld, tabelle) {
        const vorher = feld.dataset.vorher ?? '0';
        feld.disabled = true;
        try {
            const antwort = await Serverabruf.senden(Engine2d3dKleiderqualitaet.ADRESSE(feld.dataset.id),
                { feld: feld.dataset.feld, wert: Number(feld.value) });
            if (antwort.error) throw new Error(antwort.error);
            Engine2d3dKleiderqualitaet.nachziehen(tabelle, feld.dataset.feld, antwort.raenge || {});
        } catch (fehler) {
            feld.value = vorher;
            const name = Engine2d3dKleiderqualitaet.NAMEN[feld.dataset.feld] || 'Qualität';
            window.alert(`${name} konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
        } finally {
            feld.disabled = false;
        }
    }

    /**
     * Stellt alle Felder einer Spalte nach dem Stand des Servers nach: `raenge` = `{id: Rang}` aller bewerteten Läufe. Die Auswahl eines
     * Felds reicht bis zum nächsten freien Rang (bewertete Läufe + 1, solange der Lauf selbst keinen hat) — wie `Engine2d3dKleidertabelle._qualitaet`.
     */
    static nachziehen(tabelle, feldname, raenge) {
        const bewertet = Object.keys(raenge).length;
        for (const feld of tabelle.querySelectorAll(`select.engine2d3dkleider-qualitaet[data-feld="${feldname}"]`)) {
            const rang = raenge[feld.dataset.id] || 0;
            const bis = Math.max(bewertet + (rang ? 0 : 1), rang, 1);
            feld.replaceChildren(...Array.from({ length: bis + 1 }, (_, wert) => {
                const option = document.createElement('option');
                option.value = String(wert);
                option.textContent = wert ? String(wert) : '–';
                return option;
            }));
            feld.value = String(rang);
            feld.dataset.vorher = String(rang);
            feld.closest('td')?.setAttribute('data-sort', String(rang || Engine2d3dKleiderqualitaet.SORT_OHNE_RANG));
            feld.title = `${feld.title.split(' — jetzt: ')[0]} — jetzt: ${rang ? `Rang ${rang}` : 'nicht bewertet'}`;
        }
    }
}
