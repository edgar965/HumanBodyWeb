import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/**
 * Umabauerstand — lebt der Unity-Bauer? Und ihn vorwärmen, wenn nicht.
 *
 * WARUM (06.09.2026, Edgar: „warum dauert Unity bauen immer noch 1,5 Minuten,
 * ich dachte, du hättest was von ein paar Sekunden gesagt?"): Ein Bau im
 * offenen Editor dauert 4–6 s — aber der ERSTE nach einem Start rund 90 s
 * (Editor, Skripte, Rezept-Index, erster Export). Der Editor endete nach zehn
 * Minuten Leerlauf; jede Pause kostete den Neustart beim nächsten Klick.
 *
 * Jetzt bleibt der Editor offen, und sobald die Szene eine UMA-Figur zeigt,
 * wird er gestartet und baut einmal ins Leere (`POST uma-figur/bauer/
 * vorwaermen/`). Die Zeile hier sagt, woran man ist: bereit (Sekunden),
 * startet (Minuten), aus.
 */
export class Umabauerstand {

    static ADRESSE = '/api/character/uma-figur/bauer/';
    static TAKT_MS = 3000;
    static HOECHSTENS_MS = 10 * 60 * 1000;

    static async holen() {
        return Serverabruf.json(Umabauerstand.ADRESSE);
    }

    static async vorwaermen() {
        return Serverabruf.json(`${Umabauerstand.ADRESSE}vorwaermen/`, { method: 'POST' });
    }

    /** Was ein Bau jetzt kostet — für Knopf- und Gruppenbeschriftungen. */
    static dauer(stand) {
        if (!stand) return '';
        if (stand.lebt) return stand.stand === 'baut' ? 'Unity baut gerade, danach etwa 5 s' : 'etwa 5 s';
        if (stand.startet) return 'Unity startet, erster Bau etwa 1½ Minuten';
        return 'Unity ist aus, erster Bau etwa 1½ Minuten';
    }

    static text(stand) {
        if (!stand) return 'Unity-Bauer: Stand unbekannt';
        if (stand.lebt) return `Unity-Bauer bereit (${stand.stand}) · ein Bau dauert etwa 5 s`;
        if (stand.startet) return 'Unity-Bauer startet im Hintergrund … (einmalig etwa 1½ Minuten)';
        return 'Unity-Bauer ist aus — der erste Bau startet ihn (etwa 1½ Minuten)';
    }

    /**
     * Die Zeile in `element` füllen und nachhalten, bis der Bauer bereit ist.
     * `vorwaermen` = true startet ihn, falls er nicht lebt. `beiAenderung(stand)`
     * darf andere Beschriftungen nachziehen.
     */
    static async anzeigen(element, { vorwaermen = false, beiAenderung = null } = {}) {
        let stand = null;
        try {
            stand = await Umabauerstand.holen();
            if (vorwaermen && !stand.lebt && !stand.startet) {
                const antwort = await Umabauerstand.vorwaermen();
                stand = antwort.bauer || stand;
            }
        } catch (fehler) {
            Protokoll.warnung('Umabauerstand', 'Bauer-Stand nicht lesbar', fehler);
            if (element) element.textContent = `Unity-Bauer: ${fehler.message}`;
            return null;
        }
        Umabauerstand._zeigen(element, stand, beiAenderung);
        if (!stand.lebt) Umabauerstand._nachhalten(element, beiAenderung);
        return stand;
    }

    static _zeigen(element, stand, beiAenderung) {
        if (element) element.textContent = Umabauerstand.text(stand);
        if (beiAenderung) beiAenderung(stand);
    }

    static _nachhalten(element, beiAenderung) {
        if (Umabauerstand._laeuft) return;
        Umabauerstand._laeuft = true;
        const ende = Date.now() + Umabauerstand.HOECHSTENS_MS;
        const tick = async () => {
            let stand = null;
            try { stand = await Umabauerstand.holen(); } catch (fehler) { /* nächster Takt */ }
            if (stand) Umabauerstand._zeigen(element, stand, beiAenderung);
            if (stand?.lebt || Date.now() > ende) { Umabauerstand._laeuft = false; return; }
            setTimeout(tick, Umabauerstand.TAKT_MS);
        };
        setTimeout(tick, Umabauerstand.TAKT_MS);
    }
}
