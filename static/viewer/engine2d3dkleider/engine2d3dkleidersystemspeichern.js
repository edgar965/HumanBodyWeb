import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleidersystemspeichern — „Modell im System Speichern", rechts oben im Lauf unter „Neu berechnen" (08.10.2026).
 *
 * Edgar: „… einen Button „Modell im System Speichern", damit wird es gespeichert und erscheint das Modell bei den Genesis Modellen,
 * wenn ich es z.B. im Studio oder Charakter hinzufügen möchte". Ein Klick, kein Dialog: derselbe Weg wie „Modell speichern" weiter
 * unten mit dem Format „Eigenes Format" (`POST …/modell/`, `Engine2d3dKleiderspeichern.modell_speichern` — Modell in `data/models`,
 * Kacheln daneben, Kleider und Haar der Iterationen, falls es welche gibt). **Der Name ist der des Auftrags, wie er oben auf der Seite
 * steht (`#auftrag-name`) — ohne Zusatz** (Edgar: „das Modell soll exakt unter dem aktuellen Modellnamen gespeichert werden" — „also was
 * oben steht"); das Feld „Name" des Knopfes weiter unten gilt hier nicht. Ein eigenes Modell dieses Auftrags unter demselben Namen wird
 * mit dem neuen Stand ersetzt, eine fremde Figur nie — der Server lehnt ab und die Meldung bleibt im Fehlerband stehen. Der Server
 * lässt nur Buchstaben, Ziffern, Leerzeichen und Bindestrich im Dateinamen stehen (`Meshfigurspeichern.modell_speichern`, wie jedes
 * Speichern von Modellen im Projekt); die Meldung nennt den Namen, unter dem es wirklich liegt.
 *
 * Gesperrt wie der Knopf unten (`Meshfigurspeicher`): solange der Lauf rechnet oder es noch keine Figur gibt — dieselben zwei
 * Bedingungen prüft der Endpunkt mit 409.
 */
export class Engine2d3dKleidersystemspeichern {

    static TITEL = 'Speichert die Figur (mit Kleidern und Haar der Iterationen, falls es welche gibt) als Genesis-Modell — danach '
        + 'unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle" in Szene, Studio und Theatre wählbar.';

    constructor(seite) {
        this.seite = seite;
        this.knopf = document.getElementById('modell-im-system-speichern');
        this.meldung = document.getElementById('modell-im-system-meldung');
        this.knopf?.addEventListener('click', () => this.speichern());
    }

    zeigen(z) {
        if (!this.knopf) return;
        const keineFigur = !Object.keys(z.stellung || {}).length;
        this.knopf.disabled = !!z.laeuft || keineFigur || !!this._laeuft;
        this.knopf.title = z.laeuft ? 'Erst wenn der Lauf fertig ist'
            : keineFigur ? 'Erst wenn die Figur fertig ist (Schritt „Grundfigur" oder „Körper")'
                : Engine2d3dKleidersystemspeichern.TITEL;
    }

    _melden(text) {
        if (this.meldung) this.meldung.textContent = text;
    }

    async speichern() {
        const feld = document.getElementById('modell-name');
        // Der Name oben auf der Seite (nach „Umbenennen" schon neu, der Zustand zieht erst im nächsten Takt nach).
        const name = (document.getElementById('auftrag-name')?.textContent || this.seite.zustand.name || '').trim();
        if (!name) { this.seite.fehler('Modell im System speichern fehlgeschlagen: Der Auftrag hat keinen Namen.'); return; }
        this._laeuft = true;
        this.knopf.disabled = true;
        this._melden('Wird gespeichert …');
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('modell/'), { name });
            if (antwort.error) throw new Error(antwort.error);
            this.seite.zustand.modell = antwort.modell;
            if (feld && !feld.value) feld.value = antwort.modell;
            this._melden(`Gespeichert als „${antwort.modell}" — unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle" (Szene, Studio, Theatre).`);
        } catch (fehler) {
            this._melden('');
            this.seite.fehler(`Modell im System speichern fehlgeschlagen: ${fehler.daten?.error || fehler.message}`);
        } finally {
            this._laeuft = false;
            this.zeigen(this.seite.zustand);
        }
    }
}
