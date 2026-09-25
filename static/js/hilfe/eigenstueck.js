import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';

/**
 * Eigenstueckformular — ein OBJ hochladen, als Genesis-9-Stück bauen, Proben zeigen.
 *
 * Edgar (25.09.2026): „mach mir ein UI für ein neues garment laut Punkt 2, erstmal in
 * dieser Hilfeseite. Browser zur Angabe des obj, Ausgabe in einem Verzeichnis, Test
 * der Ausgabe auf Genesis und HumanBody Modell (Screenshot)". Server:
 * `core/api/eigenstueck.py` → `Genesis9/eigenstueck.py`, Probe
 * `core/dienste/eigenstueckprobe.py`.
 *
 * Ein Lauf dauert 10–40 s (erster Aufruf nach dem Serverstart länger: Grundfigur
 * und HumanBody-Paarung werden aufgebaut). Der Knopf ist solange gesperrt, der
 * Stand zählt die Sekunden — ein stummer Knopf sieht aus wie ein toter.
 * Das Formular über seine ID, nie `querySelector('form')` (die Seitenleiste führt
 * das Abmeldeformular früher im DOM).
 */
export class Eigenstueckformular {

    static ADRESSE = '/api/character/eigenstueck/bauen/';

    static binden() {
        const formular = document.getElementById('eigenstueck-formular');
        if (!formular) return;
        formular.addEventListener('submit', (ereignis) => {
            ereignis.preventDefault();
            Eigenstueckformular.senden(formular);
        });
    }

    static async senden(formular) {
        const knopf = document.getElementById('eigenstueck-bauen');
        const stand = document.getElementById('eigenstueck-stand');
        const ergebnis = document.getElementById('eigenstueck-ergebnis');
        const daten = new FormData(formular);
        daten.set('zentrieren', formular.elements.zentrieren.checked ? '1' : '0');
        const start = performance.now();
        const uhr = setInterval(() => {
            stand.textContent = `Baue und prüfe … ${Math.round((performance.now() - start) / 1000)} s`;
        }, 500);
        knopf.disabled = true;
        ergebnis.replaceChildren();
        try {
            const antwort = await fetch(Eigenstueckformular.ADRESSE, {
                method: 'POST', body: daten, headers: { 'X-CSRFToken': Serverabruf.csrfToken() },
            });
            const inhalt = await antwort.json().catch(() => ({ fehler: `Antwort ${antwort.status}` }));
            if (!antwort.ok || inhalt.fehler) throw new Error(inhalt.fehler || `Antwort ${antwort.status}`);
            const sekunden = Math.round((performance.now() - start) / 1000);
            stand.textContent = `Fertig in ${sekunden} s.`;
            ergebnis.append(Eigenstueckformular.bilanz(inhalt.bilanz), Eigenstueckformular.proben(inhalt.proben));
        } catch (fehler) {
            stand.textContent = `Fehler: ${fehler.message}`;
        } finally {
            clearInterval(uhr);
            knopf.disabled = false;
        }
    }

    /** Die Bilanz als Liste: was gebaut wurde, wie gut es liegt, wo es liegt. */
    static bilanz(b) {
        const zeilen = [
            ['Stück', `${b.name} (Garderobe: ${b.stueck})`],
            ['Netz', `${b.punkte} Punkte, ${b.flaechen} Flächen, Höhe ${b.hoehe_m} m, Einheit ${b.einheit}`
                     + (b.uv ? ', mit UV' : ', ohne UV') + (b.textur ? ', Textur' : '')],
            ['Sitz', `Hautabstand median ${b.haut_median_mm} mm; im Körper ${b.innen_vorher} → ${b.innen_nachher}`
                     + ` Punkte; fern vom Körper (> 15 cm) ${b.fern_anteil} %`],
            ['Genesis-Stück', b.duf],
            ['Arbeitsordner', b.ordner],
        ];
        const liste = document.createElement('dl');
        liste.className = 'eigenstueck-bilanz';
        for (const [name, wert] of zeilen) {
            const dt = document.createElement('dt');
            dt.textContent = name;
            const dd = document.createElement('dd');
            dd.textContent = wert;
            liste.append(dt, dd);
        }
        if (b.fern_anteil > 20) {
            const warnung = document.createElement('p');
            warnung.className = 'eigenstueck-warnung';
            warnung.textContent = 'Ein Fünftel der Punkte liegt fern vom Körper — Einheit, Achse oder Versatz prüfen.';
            liste.append(warnung);
        }
        return liste;
    }

    /** Je Figur das Probebild (vier Ansichten) oder die Fehlermeldung. */
    static proben(proben) {
        const kasten = document.createElement('div');
        kasten.className = 'eigenstueck-proben';
        const namen = { genesis: 'Genesis 9', humanbody: 'HumanBody' };
        for (const [figur, titel] of Object.entries(namen)) {
            const p = proben?.[figur];
            if (!p) continue;
            const abschnitt = document.createElement('figure');
            const unter = document.createElement('figcaption');
            if (p.fehler) {
                unter.textContent = `${titel}: ${p.fehler}`;
            } else {
                const bild = document.createElement('img');
                bild.src = `${p.bild}?t=${Date.now()}`;
                bild.alt = `${titel}: Probe`;
                abschnitt.append(bild);
                unter.textContent = `${titel}: ${p.pixel} Hautpixel vor dem Stoff (rot), vier Ansichten`;
            }
            abschnitt.append(unter);
            kasten.append(abschnitt);
        }
        return kasten;
    }
}

Eigenstueckformular.binden();
