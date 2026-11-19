/**
 * Meshoptionenhilfe — Hover-Hilfe und Wertebereich je Feld von `Meshoptionenformular` (19.11.2026, Edgar: „bei dem Render fenster mach eine Hilfe (Hover) und
 * range (wenn nicht verfügbar, dann empfohlene range) für jede einstellung“).
 *
 * Bereich = `min` bis `max` des Katalogs; fehlt eine Grenze, gilt `empfohlen` ([von, bis]) als „empfohlen …“. Der Tooltip liegt auf der ganzen Zeile (Titel und
 * Eingabe) und nennt Hinweis, Bereich oder Auswahl und Vorgabe; der Bereich steht zusätzlich klein neben dem Titel. Eingeschaltet über
 * `Meshoptionenformular.bauen(…, {hilfe: true})` (Exportleiste); die übrigen Formulare bleiben, wie sie sind.
 */
export class Meshoptionenhilfe {

    /** Zahl deutsch (Komma, echtes Minus). */
    static zahl(x) {
        return Number(x).toLocaleString('de-DE', { maximumFractionDigits: 6 }).replace('-', '−');
    }

    static einheit(feld) {
        const e = feld.einheit;
        if (!e) return '';
        return e === '%' || e === '°' ? e : ` ${e}`;
    }

    static _da(x) {
        return x !== null && x !== undefined && x !== '';
    }

    /** Bereich als Text („0 bis 80 %“, „empfohlen 1 bis 5 s“) oder '' (Wahl, Häkchen, Farbe, Text). */
    static bereich(feld) {
        if (feld.art !== 'zahl') return '';
        const z = Meshoptionenhilfe.zahl;
        const e = Meshoptionenhilfe.einheit(feld);
        if (Meshoptionenhilfe._da(feld.min) && Meshoptionenhilfe._da(feld.max)) return `${z(feld.min)} bis ${z(feld.max)}${e}`;
        if (Array.isArray(feld.empfohlen) && feld.empfohlen.length === 2) return `empfohlen ${z(feld.empfohlen[0])} bis ${z(feld.empfohlen[1])}${e}`;
        if (Meshoptionenhilfe._da(feld.min)) return `ab ${z(feld.min)}${e}`;
        if (Meshoptionenhilfe._da(feld.max)) return `bis ${z(feld.max)}${e}`;
        return '';
    }

    static vorgabe(feld) {
        if (feld.art === 'wahl') {
            const w = (feld.werte || []).find(x => x.wert === feld.vorgabe);
            return w ? w.text : String(feld.vorgabe ?? '');
        }
        if (feld.art === 'haken') return feld.vorgabe === true || feld.vorgabe === feld.an ? 'an' : 'aus';
        if (feld.art === 'zahl') return `${Meshoptionenhilfe.zahl(feld.vorgabe)}${Meshoptionenhilfe.einheit(feld)}`;
        return String(feld.vorgabe ?? '');
    }

    /** Tooltip: Hinweis, Bereich (Zahl) oder Auswahl (Wahl) oder „an oder aus“ (Häkchen), Vorgabe. */
    static text(feld) {
        const zeilen = [];
        if (feld.hinweis) zeilen.push(feld.hinweis);
        const bereich = Meshoptionenhilfe.bereich(feld);
        if (bereich) zeilen.push(`Bereich: ${bereich}`);
        if (feld.art === 'wahl') zeilen.push(`Auswahl: ${(feld.werte || []).map(w => w.text).join(' · ')}`);
        if (feld.art === 'haken') zeilen.push('Bereich: an oder aus');
        if (feld.art === 'farbe') zeilen.push('Bereich: jede Farbe');
        if (Meshoptionenhilfe._da(feld.vorgabe)) zeilen.push(`Vorgabe: ${Meshoptionenhilfe.vorgabe(feld)}`);
        return zeilen.join('\n');
    }

    /** An eine fertige Zeile hängen: Tooltip (`data-tip`, kein natives `title` — Regel `frontend`: im Dark Mode unlesbar) auf die Zeile, Bereich und „ⓘ“ an den Titel. */
    static anbringen(zeile, label, feld) {
        label.removeAttribute('title');
        zeile.dataset.tip = Meshoptionenhilfe.text(feld);
        zeile.classList.add('mesh-mit-hilfe');
        const bereich = Meshoptionenhilfe.bereich(feld);
        if (bereich) {
            const marke = document.createElement('span');
            marke.className = 'mesh-optionsbereich';
            marke.textContent = `(${bereich})`;
            label.append(' ', marke);
        }
        const zeichen = document.createElement('span');
        zeichen.className = 'mesh-optionszeichen';
        zeichen.setAttribute('aria-hidden', 'true');
        zeichen.textContent = 'ⓘ';
        label.append(' ', zeichen);
    }
}
