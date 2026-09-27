/**
 * Meshpfadliste — die Ablageorte des Netzes auf der Auftragsseite, kopierbar.
 *
 * Edgar (27.09.2026): „zeige mir in den Job seiten … wo das Mesh gespeichert ist, so dass
 * ich den Pfad kopieren kann". Die Daten kommen fertig vom Server (`zustand.pfade`,
 * `core/dienste/meshpfade.py`) — hier nur die Darstellung: je Zeile ein `readonly`-Feld
 * (markierbar, Strg+C geht immer) und ein Knopf, der in die Zwischenablage schreibt.
 *
 * `navigator.clipboard` gibt es nur in sicheren Kontexten — über `http://` auf einer
 * anderen Maschine als `localhost` fehlt es. Deshalb der Rückfall auf `select()` +
 * `document.execCommand('copy')`, und wenn auch das scheitert, bleibt das markierte Feld
 * stehen statt einer Erfolgsmeldung, die keine ist.
 */
export class Meshpfadliste {

    static ZURUECK_MS = 1500;

    /** Baut die Liste in `behaelter` neu auf. `pfade` = `[{art,label,pfad,fehlt}, …]`. */
    static zeichnen(behaelter, pfade) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        for (const eintrag of pfade || []) {
            behaelter.appendChild(Meshpfadliste._zeile(eintrag));
        }
    }

    static _zeile(eintrag) {
        const zeile = document.createElement('div');
        zeile.className = 'mesh-pfadzeile' + (eintrag.fehlt ? ' mesh-pfad-fehlt' : '');
        const label = document.createElement('span');
        label.className = 'mesh-pfadlabel';
        label.textContent = eintrag.label;
        const feld = document.createElement('input');
        feld.type = 'text';
        feld.className = 'mesh-pfadfeld';
        feld.readOnly = true;
        feld.value = eintrag.pfad;
        feld.title = eintrag.fehlt ? `${eintrag.pfad}\n(liegt (noch) nicht auf der Platte)` : eintrag.pfad;
        feld.addEventListener('focus', () => feld.select());
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-secondary btn-sm mesh-pfadkopie';
        knopf.title = 'Pfad in die Zwischenablage';
        knopf.innerHTML = '<i class="fas fa-copy"></i>';
        knopf.addEventListener('click', () => Meshpfadliste._kopieren(feld, knopf));
        zeile.append(label, feld, knopf);
        return zeile;
    }

    static async _kopieren(feld, knopf) {
        const vorher = knopf.innerHTML;
        let gelungen = false;
        try {
            await navigator.clipboard.writeText(feld.value);
            gelungen = true;
        } catch (fehler) {
            feld.select();
            try { gelungen = document.execCommand('copy'); } catch (zweiter) { gelungen = false; }
        }
        if (!gelungen) { knopf.title = 'Kopieren ging nicht — das Feld ist markiert, Strg+C'; return; }
        knopf.innerHTML = '<i class="fas fa-check"></i>';
        setTimeout(() => { knopf.innerHTML = vorher; }, Meshpfadliste.ZURUECK_MS);
    }
}
