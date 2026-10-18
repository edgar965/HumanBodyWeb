/**
 * Genesis9garderobezeile — eine Zeile der Garderobe ausblenden oder in eine andere Kategorie hängen, OHNE die Liste neu zu bauen.
 *
 * Edgar, 18.10.2026: „nach jedem Löschen eines Garderobenteils wird das Menü neu aufgebaut - mach das asynchron" und danach
 * „nach verschieben eines Assets wird das menü wieder geschlossen, gleicher fehler". Beides lief über `Genesis9garderobe.fuellen`:
 * Katalog neu, Liste neu, und alle Kategorien standen wieder zu (nur die des gewählten Stücks offen, `Genesis9garderobekategorien.offen`).
 * Jetzt bewegt sich nur die eine Zeile samt ihrem Reglerkasten (`zeile._regler`, `Genesis9garderobe._eintrag`); was aufgeklappt
 * ist, bleibt aufgeklappt. Die Zahl im Kopf einer Kategorie zählt mit, eine leere Kategorie verschwindet.
 */
export class Genesis9garderobezeile {

    /** Zeile und Reglerkasten aus- (`false`) oder wieder einblenden. */
    static zeigen(zeile, sichtbar) {
        for (const teil of [zeile, zeile._regler]) {
            if (teil) teil.style.display = sichtbar ? '' : 'none';
        }
        Genesis9garderobezeile.zaehlen(zeile.closest('details.g9-kategorie'));
    }

    /** Zeile und Reglerkasten endgültig entfernen. */
    static entfernen(zeile) {
        const kategorie = zeile.closest('details.g9-kategorie');
        zeile._regler?.remove();
        zeile.remove();
        Genesis9garderobezeile.zaehlen(kategorie);
    }

    /**
     * Die Zeile in die Kategorie `name` hängen — fehlt sie in der Liste (leer gewesen, neu angelegt), entsteht sie an der Stelle,
     * die `reihenfolge` (die Kategorien des Stands) ihr gibt. Innerhalb der Kategorie nach dem Namen einsortiert.
     */
    static verschieben(zeile, name, reihenfolge = []) {
        const alt = zeile.closest('details.g9-kategorie');
        const behaelter = alt?.parentElement;
        if (!behaelter) return false;
        const ziel = Genesis9garderobezeile._kategorie(behaelter, name, reihenfolge);
        const eigener = zeile.querySelector('.stueckname')?.textContent || '';
        const davor = [...ziel.querySelectorAll(':scope > .slider-row')].find(
            andere => (andere.querySelector('.stueckname')?.textContent || '').localeCompare(eigener, 'de') > 0);
        ziel.insertBefore(zeile, davor || null);
        if (zeile._regler) zeile.after(zeile._regler);
        Genesis9garderobezeile.zaehlen(alt);
        Genesis9garderobezeile.zaehlen(ziel);
        return true;
    }

    /** Zahl im Kopf nachziehen; ohne sichtbare Zeile verschwindet die Kategorie. */
    static zaehlen(kategorie) {
        if (!kategorie) return;
        const anzahl = [...kategorie.querySelectorAll(':scope > .slider-row')].filter(z => z.style.display !== 'none').length;
        const zahl = kategorie.querySelector(':scope > summary .gedaempft');
        if (zahl) zahl.textContent = `(${anzahl})`;
        kategorie.style.display = anzahl ? '' : 'none';
    }

    static _kategorie(behaelter, name, reihenfolge) {
        const alle = [...behaelter.querySelectorAll(':scope > details.g9-kategorie')];
        const da = alle.find(k => k.dataset.kategorie === name);
        if (da) return da;
        const kasten = document.createElement('details');
        kasten.className = 'g9-kategorie';
        kasten.dataset.kategorie = name;
        const kopf = document.createElement('summary');
        kopf.className = 'aufklappkopf';
        const zahl = document.createElement('span');
        zahl.className = 'gedaempft';
        kopf.append(`${name} `, zahl);
        kasten.appendChild(kopf);
        const stelle = reihenfolge.indexOf(name);
        const danach = stelle < 0 ? null : alle.find(k => reihenfolge.indexOf(k.dataset.kategorie) > stelle);
        behaelter.insertBefore(kasten, danach || null);
        return kasten;
    }
}
