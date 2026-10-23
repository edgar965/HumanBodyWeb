/**
 * Mesh3daitestkleidname — Name und Kategorie eines Stücks in der Karte „Kleider und Bestandteile“ der Testseite (22.10.2026, Server `Mesh3daitestkleidspeichern`).
 * Edgar: „… eine Möglichkeit, sie unter einem bestimmten Namen und in einer Kategorie zu speichern. Mach die Namenänderung möglich und die Kategorieauswahl der Combo, zum Beispiel Oberteile, Schuhe“.
 * Nur Stücke, die bei „Übernehmen und als Modell speichern“ eigene Genesis-Stücke werden (Wege b, k, s, f, g); ein Katalogstück (a) oder eine Frisur der Bibliothek (h) ist schon in der Garderobe.
 * Leerer Name = „<Modellname> <Stück>“ (der Platzhalter zeigt ihn); gespeichert wird bei jeder Änderung, angewandt bei der Übernahme.
 */
export class Mesh3daitestkleidname {
    /** → [Zelle Name, Zelle Kategorie]; `senden({stueck, name?, kategorie?})` speichert. */
    static zellen(st, kategorien, modellname, senden) {
        const tdName = document.createElement('td');
        const tdKategorie = document.createElement('td');
        const sp = st.speichern;
        if (!sp?.eigen) {
            tdName.textContent = tdKategorie.textContent = '—';
            tdName.title = st.art === 'haut' ? 'Die Haut ist kein Stück der Garderobe.'
                : st.wahl === 'aus' ? 'Ausgeschaltet — kommt nicht ins Modell.' : 'Schon ein Stück der Garderobe (Katalog bzw. Frisur der Bibliothek) — Name und Kategorie dort.';
            return [tdName, tdKategorie];
        }
        const feld = document.createElement('input');
        feld.type = 'text';
        feld.maxLength = 80;
        feld.className = 'mesh3dai-kleider-stueckname';
        feld.value = sp.name;
        feld.placeholder = `${modellname || ''} ${st.name}`.trim();
        feld.title = 'Name des Stücks in der Garderobe (leer: Modellname und Stück)';
        feld.addEventListener('change', () => senden({ stueck: st.id, name: feld.value }));
        tdName.append(feld);
        const wahl = document.createElement('select');
        wahl.className = 'mesh3dai-kleider-kategorie';
        wahl.title = `Kategorie in der Garderobe (Vorgabe nach der Art des Stücks: ${sp.kategorie_vorgabe})`;
        for (const k of new Set([...(kategorien || []), sp.kategorie])) wahl.append(new Option(k, k));
        wahl.value = sp.kategorie;
        wahl.addEventListener('change', () => senden({ stueck: st.id, kategorie: wahl.value }));
        tdKategorie.append(wahl);
        return [tdName, tdKategorie];
    }
}
