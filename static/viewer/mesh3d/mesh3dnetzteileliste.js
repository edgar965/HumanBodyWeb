/**
 * Mesh3dnetzteileliste — die Teile des Netzes als Reihe von Knöpfen unter der Leiste „Netz bearbeiten“ (13.10.2026, `Mesh3dnetzwerkzeug`).
 *
 * Ein Knopf je Teil ab 50 Flächen (Nummer, Flächen, Anteil); Klick wählt den Teil, Umschalt+Klick nimmt ihn aus der Auswahl. Rot (`active`) ist ein Teil, der ganz gewählt ist, durchgestrichen einer,
 * der ganz entfernt ist. Die Zahlen sind die der gezeigten Kopie (`Mesh3dnetzinseln`); kleinere Teile stehen als eine Zeile dahinter.
 */
export class Mesh3dnetzteileliste {
    static zahl(n) { return n.toLocaleString('de-DE'); }

    static prozent(anteil) { return `${(anteil * 100).toLocaleString('de-DE', { maximumFractionDigits: 1 })} %`; }

    /**
     * @param {HTMLElement} feld Behälter (wird geleert)
     * @param {Mesh3dnetzwahl} wahl Auswahl mit Zerlegung
     * @param {Function} beiKlick `(nr, plus)` — Klick auf einen Teil
     */
    static zeichnen(feld, wahl, beiKlick) {
        const gewaehlt = new Int32Array(wahl.zerlegung.groessen.length);
        for (let f = 0; f < wahl.flaechen; f++) if (wahl.auswahl[f]) gewaehlt[wahl.zerlegung.insel[f]]++;
        const gross = wahl.teile();
        const knoepfe = gross.map(t => {
            const knopf = document.createElement('button');
            knopf.type = 'button';
            knopf.className = 'schaltknopf';
            if (t.entfernt === t.flaechen) knopf.classList.add('entfernt');
            else if (gewaehlt[t.nr] === t.flaechen) knopf.classList.add('active');
            knopf.title = `Teil ${t.nr + 1}: ${Mesh3dnetzteileliste.zahl(t.flaechen)} Flächen (in der Ansicht). Klick wählt, Umschalt+Klick nimmt aus der Auswahl.`;
            knopf.append(`Teil ${t.nr + 1} `);
            const klein = document.createElement('small');
            klein.textContent = `${Mesh3dnetzteileliste.zahl(t.flaechen)} · ${Mesh3dnetzteileliste.prozent(t.anteil)}`;
            knopf.appendChild(klein);
            knopf.addEventListener('click', e => beiKlick(t.nr, !e.shiftKey));
            return knopf;
        });
        const rest = wahl.zerlegung.groessen.length - gross.length;
        if (rest > 0) {
            const flaechen = Array.from(wahl.zerlegung.groessen).reduce((s, n) => s + n, 0) - gross.reduce((s, t) => s + t.flaechen, 0);
            const hinweis = document.createElement('span');
            hinweis.className = 'hb-hinweis';
            hinweis.textContent = `+ ${rest} kleinere Teile (${Mesh3dnetzteileliste.zahl(flaechen)} Flächen) — mit dem Rahmen oder durch Klick im Netz`;
            knoepfe.push(hinweis);
        }
        feld.replaceChildren(...knoepfe);
    }
}
