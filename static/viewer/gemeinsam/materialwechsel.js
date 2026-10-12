/**
 * Materialwechsel — der eine Weg für jede Auswahl, die nur das Material der Figur ändert (12.10.2026).
 *
 * Edgar: „erzeuge eine generische Methode für alle Wechsel." Haut, Augen, Brauen, Brauenstil und Makeup bewegen keinen Knochen: Das Gewählte wird gesetzt, der Körper OHNE
 * neues Skelett neu geholt (`Genesis9Modell.koerperAufbauen(null, false)`). Dieselben zwei Zeilen standen in sechs Methoden; jede neue Abhängigkeit von der Haut (Scham, Naht) hätte
 * an sechs Stellen nachgetragen werden müssen. Die Nacharbeit selbst (Hautverdeckung planen, Anatomie-Stück der Haut folgen lassen) hängt am Bau
 * (`Genesis9maske.nachMaterialwechsel`), nicht am Aufrufer — ein Wechsel, der hier durchgeht, bekommt sie ohne eigenen Code.
 *
 * Das Netz wird dabei nicht neu geholt (12.10.2026, Edgar: „Bei einem reinen Hautwechsel das Netz nicht neu holen und nur die Texturen tauschen"): Der Bau nimmt die Netzantwort,
 * die die Figur für diese Stufe hält, und holt vom Server nur die Materialien (`Genesis9materialabruf`, `Genesis9antwortspeicher`). Das gilt von selbst nur, solange die Gestalt
 * dieselbe ist — wer mit dem Wechsel Brauenstil, Regler oder Pose ändert, bekommt die volle Antwort.
 *
 * Eigene Klasse ohne Three.js, damit sie in Node prüfbar ist (`Genesis9Modell` zieht die ganze Szene nach).
 */
export class Materialwechsel {

    /**
     * @param modell   die Figur (`koerperAufbauen(stufen, skelettFrisch)`)
     * @param aendern  setzt, was gewählt wurde; läuft VOR dem Bau, und wirft sie, wird nichts gebaut
     * @returns das Ergebnis des Baus
     */
    static async ausfuehren(modell, aendern) {
        aendern();
        return modell.koerperAufbauen(null, false);
    }
}
