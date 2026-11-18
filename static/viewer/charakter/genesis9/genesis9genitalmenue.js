import { Genesis9stueckmenue } from './genesis9stueckmenue.js';
import { Genesis9garderobezeile } from './genesis9garderobezeile.js';
import { Genesis9genitalkasten } from './genesis9genitalkasten.js';

/**
 * Genesis9genitalmenue — das Kontextmenü der Kästen im Bereich „Genitalien" (`Genesis9genitalien`): Verschieben, Umbenennen, Löschen.
 *
 * Edgar, 18.10.2026 (mit Bild des Kastens „Daz · weiblich — Daz Anatomie Frau"): „mach mir bei den Einträgen im Tab ein Kontextmenü mit
 * dem ich die Assets löschen, verschieben und umbenennen kann". Die Stücke dieses Bereichs SIND Stücke der Garderobe (`anatomie` an
 * einem Eintrag des Katalogs), also gilt dasselbe wie dort — es wird nichts Eigenes gespeichert:
 *
 *   Umbenennen   ändert den ANZEIGENAMEN (`Genesis9garderobepflege`); die Kennung bleibt, Rezepte und Aufträge nennen sie weiter.
 *   Löschen      ein eigenes Stück (Import, Foto, GarmentCode, MakeHuman) liegt danach im Papierkorb, ein Stück der Daz-Bibliothek ist nur
 *                ausgeblendet — die Daz-Dateien werden nie angefasst. Wie in der Garderobe ohne Rückfrage.
 *   Verschieben  in eine andere KATEGORIE DER GARDEROBE (Oberteile, Hosen, Zubehör …). Dieser Bereich gliedert nach Herkunft und Art, nicht
 *                nach Kategorien — im Kasten ändert sich beim Verschieben also nichts, das Stück steht danach in der Garderobe (Assets-Reiter)
 *                woanders. Darum heißt der Eintrag „In der Garderobe verschieben nach".
 *
 * Nichts wird neu aufgebaut (Edgar, 18.10.2026, zum Löschen und Verschieben in der Garderobe): der Kasten verschwindet oder behält seinen
 * Platz, und die Zeile desselben Stücks in der Garderobe zieht mit — sofern sie schon gebaut ist. Das Nachziehen in beide Richtungen
 * (Kopf des Kastens, Name und Zeile in der Garderobe, Löschen) erledigt `Genesis9garderobepflege`; der Kasten merkt sich dafür sein Stück
 * (`Genesis9genitalkasten.merken`).
 */
export class Genesis9genitalmenue {

    /**
     * Rechtsklick auf den Kopf des Kastens und auf die Zeile „angelegt" öffnet das Menü.
     * (Nicht auf den ganzen Kasten: darin liegen die Regler, deren Rechtsklick niemand abfangen soll.)
     *
     * @param titel  `stueck => Text` — der Kopf des Kastens; kommt von `Genesis9genitalien`, damit sich die beiden nicht gegenseitig importieren
     */
    static binden(kasten, zeile, inst, stueck, titel) {
        Genesis9genitalkasten.merken(kasten, stueck, titel);
        const kopf = kasten.querySelector(':scope > summary');
        for (const ziel of [kopf, zeile]) {
            if (ziel) Genesis9stueckmenue.binden(ziel, stueck, () => Genesis9genitalmenue.optionen(kasten, stueck));
        }
    }

    /**
     * Die Optionen des Menüs (`Genesis9stueckmenue`, seit 16.11.2026 dieselbe Klasse wie in der Garderobe). Der Kasten ist die „Zeile“:
     * er verschwindet beim Löschen sofort und kommt bei einem Fehler zurück. Die Zeile der Garderobe wird beim Öffnen gesucht — sie kann
     * inzwischen gebaut worden sein — und wandert beim Verschieben mit.
     */
    static optionen(kasten, stueck) {
        return { zeile: kasten, garderobezeile: Genesis9garderobezeile.zeileVon(stueck.id), text: 'In der Garderobe verschieben nach' };
    }
}
