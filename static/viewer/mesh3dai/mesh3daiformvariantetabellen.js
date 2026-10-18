/**
 * Mesh3daiformvariantetabellen — die zwei Tabellen unter den Feldern der Seite „Formvariante“ (18.10.2026, aus `Mesh3daiformvariante` gelöst — die Datei wäre über 300 Zeilen gewachsen):
 * „Wie gut?“ (Abstand Ergebnis ↔ Ziel auf dieser Seite, echte Nachrechnung des Laufs, Zahlen des Laufs je Gruppe) und „Regler: Ziel gegen Vorhersage“. Alles per `textContent`, nichts als HTML.
 */
const de = (n, s = 0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });
export const GRUPPE = { training: 'Training', pruefung: 'Prüfform (nie trainiert)' };

export class Mesh3daiformvariantetabellen {
    static _text(name, text) {
        const feld = document.querySelector(`[data-info="${name}"]`);
        if (feld) feld.textContent = text;
    }

    static _zeile(tabelle, zellen) {
        const tr = document.createElement('tr');
        for (const [inhalt, num] of zellen) {
            const td = document.createElement('td');
            td.textContent = inhalt;
            if (num) td.className = 'num';
            tr.append(td);
        }
        tabelle.append(tr);
        return tr;
    }

    /** @param daten Antwort von `/api/mesh3dai/formvariante/<figur>/` @param ergebnis Kopf des Ergebnispakets (`Mesh3daiformvariantefigur.paket`) oder null */
    static zahlen(daten, ergebnis) {
        const t = document.querySelector('[data-tabelle="zahlen"]');
        if (!t) return;
        t.replaceChildren();
        const z = (name, wert, quelle) => Mesh3daiformvariantetabellen._zeile(t, [[name, false], [wert, true], [quelle, false]]);
        if (ergebnis?.abstand) {
            const welche = ergebnis.was === 'mittel' ? 'Ergebnis = Mittel aller Proben' : `Ergebnis = Probe ${ergebnis.was}`;
            z('Ergebnis ↔ Ziel, RMS', `${de(ergebnis.abstand.rms_mm, 1)} mm`, `diese Seite, G9formung heute (${welche})`);
            z('Ergebnis ↔ Ziel, Median', `${de(ergebnis.abstand.median_mm, 1)} mm`, 'ebenso');
            z('Ergebnis ↔ Ziel, 95 %-Wert', `${de(ergebnis.abstand.p95_mm, 1)} mm`, 'ebenso');
            z('Höhe Ziel / Ergebnis', `${de(ergebnis.hoehe_ziel_m, 3)} / ${de(ergebnis.hoehe_m, 3)} m`, 'ebenso');
        }
        const echt = daten.echt;
        if (echt?.vorhersage) {
            z('Echte Nachrechnung: Vorhersage (Mittel), RMS', `${de(echt.vorhersage.rms_mm, 1)} mm`, 'formen_pruefung_echt.json (Morphe zur Zeit des Laufs)');
            z('Echte Nachrechnung: mittlere Form, RMS', `${de(echt.mittlere_form.rms_mm, 1)} mm`, 'ebenso');
            z('Echte Nachrechnung: Grundfigur, RMS', `${de(echt.grundfigur.rms_mm, 1)} mm`, 'ebenso');
            z('Echte Nachrechnung: Höhe Soll / Vorhersage', `${de(echt.hoehe_soll_m, 3)} / ${de(echt.hoehe_vorhersage_m, 3)} m`, 'ebenso');
        }
        for (const w of daten.werte || []) {
            const wert = Number.isInteger(w.wert) && !w.schluessel.endsWith('_mm') ? de(w.wert) : de(w.wert, 1);
            z(`${GRUPPE[w.gruppe] ?? w.gruppe}: ${w.name}`, wert, 'lauf_ergebnis.json → je_figur');
        }
        Mesh3daiformvariantetabellen._text('zahlen', 'Linear = Formmaß des Trainings (Näherung über die Wirkung je Regler); echt = Figur aus den Reglern gebaut. Die Seite baut beide Figuren mit dem HEUTIGEN '
            + 'Stand der Morphe — weicht ihr Wert von der echten Nachrechnung des Laufs ab, haben sich Morphe seitdem geändert.');
    }

    static regler(daten) {
        const t = document.querySelector('[data-tabelle="regler"]');
        if (!t) return;
        t.replaceChildren();
        const r = daten.regler;
        if (!r) {
            Mesh3daiformvariantetabellen._text('regler', 'Der Lauf hat keine Reglerliste (formregler_liste.json) — ohne sie keine Figur und kein Vergleich.');
            return;
        }
        for (const z of r.zeilen) {
            const tr = Mesh3daiformvariantetabellen._zeile(t, [[z.anzeige, false], [z.bereich, false], [de(z.soll, 3), true], [de(z.vorhersage, 3), true],
                [(z.delta > 0 ? '+' : '') + de(z.delta, 3), true]]);
            tr.firstChild.title = z.name;
        }
        Mesh3daiformvariantetabellen._text('regler', `${de(r.gesetzt_soll)} von ${de(r.gesamt)} Reglern im Ziel gesetzt, ${de(r.gesetzt_vorhersage)} in der Vorhersage (Mittel aller Proben, `
            + `geklemmt, |Wert| < 0,01 weg); die ${r.zeilen.length} mit der größten Abweichung. Regler wirken verschieden stark — die Abweichung in Reglerwerten ist keine in Millimetern.`);
    }
}
