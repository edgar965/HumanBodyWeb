/**
 * Fotogenesiskleiderregeln — der Block „Kleidungsregeln dieses Jobs“ oben auf der Testseite von Foto-Genesis (21.11.2026, Edgar: „mach weiter mit dem Plan“; Konzept
 * `2026-11-21_bibliothek-anpassen-konzept.md`, Abschnitt 10, Stufe 4). Je Regel eine Auswahl „wie Einstellungen“ / „an“ / „aus“; gespeichert wird sofort:
 * `POST /api/fotogenesis/<job>/pshuman/` {kleider_regeln: {Kennung: true | false | null}} (`null` = eigene Wahl zurücknehmen), gilt ab dem nächsten Lauf (`Fotogenesiskleiderregeln`).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Fotogenesiskleiderregeln {
    static WERT = { '': null, an: true, aus: false };

    static binden(block) {
        if (!block) return;
        const adresse = `/api/fotogenesis/${encodeURIComponent(block.dataset.job)}/pshuman/`;
        const meldung = block.querySelector('[data-meldung]');
        const zaehler = block.querySelector('[data-zaehler]');
        const zaehlen = () => {
            const eigene = [...block.querySelectorAll('select')].filter(s => s.value !== '').length;
            if (zaehler) zaehler.textContent = eigene ? `(${eigene} eigene Wahl)` : '(wie Einstellungen)';
        };
        zaehlen();
        for (const auswahl of block.querySelectorAll('select')) {
            auswahl.addEventListener('change', async () => {
                auswahl.disabled = true;
                meldung.textContent = 'Speichert …';
                try {
                    await Serverabruf.senden(adresse, { kleider_regeln: { [auswahl.name]: Fotogenesiskleiderregeln.WERT[auswahl.value] } });
                    meldung.textContent = `gespeichert: ${auswahl.closest('tr').querySelector('label').textContent} — gilt ab dem nächsten Lauf`;
                    zaehlen();
                } catch (fehler) {
                    meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
                } finally {
                    auswahl.disabled = false;
                }
            });
        }
    }
}
