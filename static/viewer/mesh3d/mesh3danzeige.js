/**
 * Mesh3danzeige — die kleinen Bausteine, aus denen die Karten der Jobseite „Mesh-3D“ bestehen (11.10.2026): Zahlenzeilen, Bilder, Tabellen.
 *
 * Alles geht über `textContent`/DOM-Knoten, nie über Zeichenketten mit HTML: Namen und Texte stammen aus Dateien des Nutzers
 * (Netznamen einer .blend, Fehlermeldungen von Blender).
 */
export class Mesh3danzeige {

    /** Zahl mit deutschem Komma; `null` und `undefined` werden zu „—“. */
    static zahl(wert, stellen = 1) {
        if (wert === null || wert === undefined || Number.isNaN(Number(wert))) return '—';
        return Number(wert).toLocaleString('de-DE', { maximumFractionDigits: stellen });
    }

    static dauer(sekunden) {
        if (!sekunden) return '';
        const s = Math.round(Number(sekunden));
        return s >= 60 ? `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')} min` : `${s} s`;
    }

    /** Eine Zeile Text je Eintrag; ein Eintrag darf `{text, klasse}` sein. Leert das Ziel zuerst. */
    static zeilen(ziel, eintraege) {
        ziel.replaceChildren();
        for (const e of eintraege) {
            if (e === null || e === undefined || e === false) continue;
            const zeile = document.createElement('div');
            zeile.className = 'hb-hinweis' + (e.klasse ? ` ${e.klasse}` : '');
            zeile.textContent = typeof e === 'string' ? e : e.text;
            ziel.appendChild(zeile);
        }
    }

    /** Leerer Zustand einer Karte: ein kurzer Satz, grau und kursiv. */
    static leer(ziel, text) {
        ziel.replaceChildren();
        const zeile = document.createElement('div');
        zeile.className = 'mesh3d-leer';
        zeile.textContent = text;
        ziel.appendChild(zeile);
    }

    /** Bilder mit Unterschrift: `[{adresse, titel, gross?}]`; ohne Adresse entfällt der Eintrag. */
    static bilder(ziel, liste) {
        ziel.replaceChildren();
        for (const b of liste.filter(x => x && x.adresse)) {
            const rahmen = document.createElement('div');
            rahmen.className = 'mesh3d-bild' + (b.gross ? ' mesh3d-bild-gross' : '');
            const bild = document.createElement('img');
            bild.loading = 'lazy';
            bild.alt = b.titel;
            bild.src = b.adresse;
            const text = document.createElement('div');
            text.className = 'hb-hinweis';
            text.textContent = b.titel;
            rahmen.append(bild, text);
            ziel.appendChild(rahmen);
        }
    }

    /**
     * Tabelle: `spalten` = `[{titel, num?}]`, `zeilen` = Listen von Zellen; eine Zelle ist Text, eine Zahl oder `{text, klasse}`.
     * Leere Liste → „leer“-Satz statt Tabelle.
     */
    static tabelle(ziel, spalten, zeilen, leer = 'Nichts gelesen.') {
        ziel.replaceChildren();
        if (!zeilen.length) return Mesh3danzeige.leer(ziel, leer);
        const tabelle = document.createElement('table');
        tabelle.className = 'mesh3d-tabelle';
        const kopf = tabelle.createTHead().insertRow();
        for (const s of spalten) {
            const th = document.createElement('th');
            th.textContent = s.titel;
            if (s.num) th.className = 'num';
            kopf.appendChild(th);
        }
        const rumpf = tabelle.createTBody();
        for (const z of zeilen) {
            const tr = rumpf.insertRow();
            z.forEach((zelle, i) => {
                const td = tr.insertCell();
                const eintrag = zelle !== null && typeof zelle === 'object' ? zelle : { text: zelle };
                td.textContent = eintrag.text === null || eintrag.text === undefined ? '—' : String(eintrag.text);
                const klassen = [spalten[i]?.num ? 'num' : '', eintrag.klasse || ''].filter(Boolean).join(' ');
                if (klassen) td.className = klassen;
            });
        }
        ziel.appendChild(tabelle);
    }

    /** Ein Wert, der sich bei jedem Abfragetakt gleich bleibt, soll die Karte nicht neu zeichnen. */
    static geaendert(besitzer, schluessel, wert) {
        const neu = JSON.stringify(wert);
        if (besitzer[schluessel] === neu) return false;
        besitzer[schluessel] = neu;
        return true;
    }
}
