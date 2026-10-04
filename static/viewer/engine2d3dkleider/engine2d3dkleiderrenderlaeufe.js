/**
 * Engine2d3dKleiderrenderlaeufe — die Render-Läufe des Auftrags als eigene Tabelle unter dem Render-Schritt (04.10.2026).
 *
 * Edgar: „als nächstes, iterativ — evtl. mit getrenntem Abschnitt — die Render jobs. Rendere erstmal nur 10 Frames und verbessere die Qualität … wenn
 * die ersten 10 Frames gut sind, nimm 30, und dann das ganze BVH." Jeder fertige Lauf bleibt (`Engine2d3dKleiderrenderlaeufe` auf dem Server): ein
 * Bogen mit vier Bildern, das Video, die Anmerkung, was gegenüber dem Lauf davor geändert wurde. Neueste zuerst; die Zeilen ändern sich nur, wenn
 * ein Lauf dazukommt (der Zustand kommt im Takt, ein Neuaufbau je Takt flackerte).
 */
export class Engine2d3dKleiderrenderlaeufe {

    constructor(seite) {
        this.seite = seite;
        this.feld = document.getElementById('render-laeufe');
        this._stand = '';
    }

    zeigen(laeufe) {
        const liste = laeufe || [];
        const stand = liste.map(l => l.nr).join(',');
        if (stand === this._stand) return;
        this._stand = stand;
        this.feld.replaceChildren();
        if (!liste.length) return;
        const titel = document.createElement('div');
        titel.className = 'hb-hinweis';
        titel.textContent = `Render-Läufe (${liste.length}) — neueste zuerst`;
        // djangoBase-Tabelle (04.10.2026, Edgar: „Tabelle als djangoBase (sortierbar)"): `sortable` + `data-sort-key`; den Rest bindet `tabellen_auto.js`
        // (Beobachter, sobald die Kopfzeile da ist). Die Sortierung nimmt `data-sort` an der Zelle, die Anzeige darf formatiert sein.
        const rahmen = document.createElement('div');
        rahmen.className = 'db-tabelle-rahmen engine2d3dkleider-laufrahmen';
        this._groesseMerken(rahmen);
        const tabelle = document.createElement('table');
        tabelle.className = 'db-tabelle sortable';
        tabelle.dataset.sortKey = 'engine2d3dkleider-render-laeufe';
        const kopf = tabelle.createTHead().insertRow();
        for (const text of ['Lauf', 'Bilder', 'Größe · Proben', 'Erstellungszeit', 'Bogen', 'Anmerkung']) {
            const zelle = document.createElement('th');
            zelle.textContent = text;
            if (text === 'Bogen') zelle.dataset.sortAus = '1';
            kopf.appendChild(zelle);
        }
        const koerper = tabelle.createTBody();
        for (const lauf of liste) this._zeile(koerper.insertRow(), lauf);
        rahmen.appendChild(tabelle);
        this.feld.append(titel, rahmen);
    }

    /**
     * Der Rahmen lässt sich mit dem Griff unten rechts aufziehen (`resize: both`, CSS); seine Größe bleibt im Browser (04.10.2026, Edgar: „tabelle vergrößerbar,
     * merke dir die Größe, Spaltenbreiten"). Die Spaltenbreiten merkt djangoBase selbst (`TabellenBreiten`, Schlüssel `data-sort-key`). Gespeichert wird nur,
     * was der Nutzer gezogen hat — der Browser schreibt dann Breite und Höhe in `style`; die Größe beim Anlegen ist die des Inhalts und bleibt ungemerkt.
     */
    _groesseMerken(rahmen) {
        const schluessel = 'engine2d3dkleider-render-laeufe-groesse';
        try {
            const alt = JSON.parse(localStorage.getItem(schluessel) || 'null');
            if (alt && alt.breite > 0 && alt.hoehe > 0) {
                rahmen.style.width = `${alt.breite}px`;
                rahmen.style.height = `${alt.hoehe}px`;
            }
        } catch (fehler) {
            console.info('Render-Läufe: gemerkte Größe nicht lesbar', fehler);
        }
        if (typeof ResizeObserver === 'undefined') return;
        new ResizeObserver(() => {
            if (!rahmen.style.width && !rahmen.style.height) return;
            try {
                localStorage.setItem(schluessel, JSON.stringify({ breite: Math.round(rahmen.offsetWidth), hoehe: Math.round(rahmen.offsetHeight) }));
            } catch (fehler) {
                console.info('Render-Läufe: Größe nicht gemerkt', fehler);
            }
        }).observe(rahmen);
    }

    /** `476.2` → „7 min 56 s", `37` → „37 s" (die Sortierung läuft über den Rohwert in `data-sort`). */
    static dauerText(sekunden) {
        const s = Math.round(Number(sekunden) || 0);
        return s >= 60 ? `${Math.floor(s / 60)} min ${String(s % 60).padStart(2, '0')} s` : `${s} s`;
    }

    _adresse(name) {
        return this.seite.dateiAdresse('ergebnis', name);
    }

    _zeile(zeile, lauf) {
        const video = document.createElement('a');
        video.href = this._adresse(lauf.video);
        video.target = '_blank';
        video.textContent = `#${lauf.nr}`;
        video.title = `Video ansehen (${(lauf.bytes / 1048576).toFixed(1)} MB)`;
        const nummer = zeile.insertCell();
        nummer.dataset.sort = String(lauf.nr);
        nummer.appendChild(video);
        const bilder = zeile.insertCell();
        bilder.dataset.sort = String(lauf.bilder);
        bilder.textContent = `${lauf.bilder} (${String(lauf.sekunden).replace('.', ',')} s)`;
        zeile.insertCell().textContent = `${lauf.groesse} · ${lauf.spp}`;
        const dauer = zeile.insertCell();
        dauer.dataset.sort = String(lauf.dauer_s);
        dauer.title = `${lauf.dauer_s} s von der Anfrage bis zum fertigen Video (Figurcache, Stoff, Bilder, Ton)`;
        dauer.textContent = Engine2d3dKleiderrenderlaeufe.dauerText(lauf.dauer_s);
        const bogen = zeile.insertCell();
        if (lauf.blatt) {
            const link = document.createElement('a');
            link.href = this._adresse(lauf.blatt);
            link.target = '_blank';
            const bild = document.createElement('img');
            bild.src = this._adresse(lauf.blatt);
            bild.alt = `Bogen des Laufs ${lauf.nr}`;
            bild.className = 'engine2d3dkleider-laufbogen';
            link.appendChild(bild);
            bogen.appendChild(link);
        }
        zeile.insertCell().textContent = lauf.anmerkung || '';
    }
}
