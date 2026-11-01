/**
 * Exportleisteaufloesung — Auflösung eines Videos der Exportleiste: Auswahl (`_exportleiste_aufloesungen.html`) plus Breite × Höhe (31.10.2026, Edgar: „mp4 video … mit Auflösung die man
 * einstellen kann“). Eine Vorgabe füllt die Felder; ein Feld von Hand gibt „frei“. Gerade Zahlen (H.264), 64 bis 4096 Pixel — der Server prüft dasselbe (`Exportleisterender._groesse`).
 */
export class Exportleisteaufloesung {

    static GRENZEN = [64, 4096];

    constructor(wahl, breite, hoehe) {
        this.wahl = wahl;
        this.breite = breite;
        this.hoehe = hoehe;
        this._fuellen();
        wahl.addEventListener('change', () => this._fuellen());
        for (const feld of [breite, hoehe]) feld.addEventListener('input', () => { this.wahl.value = 'frei'; });
    }

    _fuellen() {
        const [b, h] = this.wahl.value.split('x').map(Number);
        if (b && h) { this.breite.value = String(b); this.hoehe.value = String(h); }
    }

    /** `{breite, hoehe}` auf gerade Zahlen in den Grenzen. */
    wert() {
        const [lo, hi] = Exportleisteaufloesung.GRENZEN;
        const zahl = feld => Math.min(hi, Math.max(lo, Math.round(Number(feld.value) / 2) * 2 || lo));
        return { breite: zahl(this.breite), hoehe: zahl(this.hoehe) };
    }

    sperren(gesperrt) {
        for (const feld of [this.wahl, this.breite, this.hoehe]) feld.disabled = gesperrt;
    }
}
