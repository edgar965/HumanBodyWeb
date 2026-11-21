/**
 * Fotogenesiskleidermethode — Umschalter der Kleider im Feld „Genesis-Ergebnis“ (19.11.2026, Edgar: „benenne um, Methode: Kleiderbibliothek (ehemals Garderobe)
 * und Drapieren — das soll einstellbar sein im Job, am besten rechnest du 2 Ergebnisse … vielleicht toggle für beide Ergebnisse im genesis view?“).
 * Derselbe Körper (Genesis-Modell, Haltung, Gesicht), nur die Stücke wechseln (`Fotogenesistestfigur.methodeSetzen`):
 *   Kleiderbibliothek  nur die fertigen Stücke der Bibliothek, angepasst (Vorgabe, Weg z)
 *   Drapieren          nur die Stücke, die als Schnittmuster aus dem Netz genäht und als Stoff drapiert sind (Weg f, `meshgenesis_drapieren_lauf.py`); die übrigen
 *                      fehlen — seit 19.11.2026 abends (Edgar: „über den Toggle … sehe ich nicht, welches was ist, mach einen dritten Button der mir entweder das eine
 *                      oder das andere zeigt, nicht beide zugleich“)
 *   Gemischt           drapiert, wo es ein brauchbares Stück gibt, sonst das der Kleiderbibliothek (bis dahin „Drapieren“)
 *   Eigen              nur die eigenen Stücke, an das Stück aus dem Netz gepasst, Form und Farbe aus dem Netz (Weg e, `meshgenesis_eigen_lauf.py`; 20.11.2026, Edgar:
 *                      „mach doch einen dritten Modus für die Kleider - "Eigen" neben Drapieren und Bibliothek“); übrige Kleidung fehlt, Haar, Hut, Requisiten wie Bibliothek
 * Der Hinweis sagt, wie viele Stücke drapiert bzw. eigen sind.
 */
import { Fotogenesisschalterleiste } from './fotogenesisschalterleiste.js';

export class Fotogenesiskleidermethode extends Fotogenesisschalterleiste {
    /** Leiste über dem Feld `feld` (Behälter wird davor eingefügt) für die Figur `figur` (`Fotogenesistestfigur`); `neu()` zeichnet das Feld neu. */
    static aufbauen(feld, figur, neu) {
        if (!feld || !figur) return null;
        const behaelter = document.createElement('div');
        behaelter.className = 'fotogenesis-zeilenleiste';
        feld.parentNode.insertBefore(behaelter, feld);
        return new Fotogenesiskleidermethode(behaelter, figur, neu);
    }

    constructor(behaelter, figur, neu) {
        super(behaelter, () => this._wechseln());
        this.figur = figur;
        this.neu = neu;
        this.methode = 'bibliothek';
        this._gruppe('Kleider', [
            { wert: 'bibliothek', text: 'Kleiderbibliothek', titel: 'Nur die fertigen Stücke der Kleiderbibliothek, in Länge, Weite und Farbe an das Stück aus dem Netz angepasst' },
            { wert: 'drapieren', text: 'Drapieren', titel: 'Nur die Stücke aus dem Netz als Schnittmuster, von GarmentCode genäht und als Stoff drapiert — Stücke ohne Drapierergebnis fehlen' },
            // „Gemischt“ nicht mehr als Knopf (21.11.2026, Edgar: „gemischt methode ist auch gaga, am besten entferne die aus dem UI“): es erbt die Schwächen beider Wege. `methodeSetzen('gemischt')`
            // und die Hinweise unten bleiben, damit sich der Knopf wieder einsetzen lässt: { wert: 'gemischt', text: 'Gemischt', titel: 'Drapiert, wo es ein brauchbares Stück gibt, sonst das Stück der Kleiderbibliothek' }
            { wert: 'eigen', text: 'Eigen', titel: 'Kleidung als eigene Stücke, an das Stück aus dem Netz gepasst — Form und Farbe aus dem Netz; Haar, Hut, Requisiten und Schuhe wie in der Kleiderbibliothek' },
        ], 'methode');
        this.hinweis = behaelter.appendChild(Object.assign(document.createElement('span'), { className: 'fotogenesis-steuername' }));
    }

    async _wechseln() {
        const methode = this.methode;
        const name = methode === 'eigen' ? 'Eigen' : 'Drapieren';
        this.hinweis.textContent = methode === 'bibliothek' ? '' : `${name} wird geladen …`;
        const zahl = await this.figur.methodeSetzen(methode);
        if (methode !== this.methode) return;            // inzwischen umgeschaltet: der spätere Ruf schreibt den Hinweis
        if (methode !== 'bibliothek') {
            const rest = methode === 'gemischt' ? 'die übrigen aus der Kleiderbibliothek'
                : methode === 'eigen' ? 'die übrigen Kleidungsstücke sind ausgeblendet; Haar, Hut, Requisiten und Schuhe wie in der Kleiderbibliothek' : 'die übrigen sind ausgeblendet';
            this.hinweis.textContent = !zahl ? `${name} nicht geladen`
                : zahl.versucht ? `${zahl.gezeigt} von ${zahl.versucht} Kleidungsstücken ${methode === 'eigen' ? 'eigen' : 'drapiert'}, ${rest}`
                    : methode === 'gemischt' ? 'Für diesen Test ist Drapieren nicht gerechnet — alle Stücke aus der Kleiderbibliothek'
                        : `Für diesen Test ist ${name} nicht gerechnet — keine ${methode === 'eigen' ? 'eigenen' : 'drapierten'} Stücke`;
        }
        this.neu();
    }
}
