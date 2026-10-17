/**
 * Mesh3daiguete — die Tabelle „Wie gut ist das Ergebnis?“ unter dem Ergebnis JEDER Zeile auf der Seite „Mesh3D-AI“ (16.10.2026, Edgar: „mach beim Ergebnis in jeder Zeile eine genaue Ausgabe in mindestens
 * 10 Zahlen, wie gut das Ergebnis ist, in einer kleinen Tabelle“). Nur bei echten Daten — die Attrappe hat kein Netz, das man bewerten könnte.
 *
 * Grundlage sind die Rig-Punkte der Zeile: Fehler je Punkt (`teil.rig.je_mm`, vom Server mit voller Genauigkeit gerechnet), Soll und Ausgabe (`teil.rig.soll/ausgabe`, auf 0,1 mm gerundet) und die Eltern der
 * Knochen (`antwort.rig.knochen[].eltern`). Zwei Maßstäbe kommen vom Server, weil sie den Trainingssatz kennen (`Mesh3daivergleich`): mittlere Trainingspose und nächste Trainingspose.
 * „Versatz“ = Länge des mittleren Fehlervektors (die ganze Zeile sitzt verschoben); „ohne Versatz“ = Fehler, nachdem dieser Versatz abgezogen ist (Form der Zeile). Richtung und Länge je Knochen:
 * Strecke Elternknochen → Knochen, nur Paare innerhalb der Zeile, nur Strecken über 1 mm im Soll.
 */
const de = (n, stellen = 1) => n.toLocaleString('de-DE', { minimumFractionDigits: stellen, maximumFractionDigits: stellen });

export class Mesh3daiguete {
    /** Schwellen für „Anteil der Punkte unter …“ (mm). */
    static SCHWELLEN = [10, 25, 50];

    /** Wert an der Stelle `q` (0–1) der sortierten Liste, linear zwischen den Nachbarn (wie `numpy.percentile`). */
    static _quantil(sortiert, q) {
        const lage = (sortiert.length - 1) * q;
        const unten = Math.floor(lage);
        const oben = Math.min(unten + 1, sortiert.length - 1);
        return sortiert[unten] + (sortiert[oben] - sortiert[unten]) * (lage - unten);
    }

    /**
     * Die Kennzahlen einer Zeile oder `null`.
     * @param {object} teil Daten der Zeile (`rig.soll`, `rig.ausgabe`, `rig.je_mm`, `kennzahlen` mit `groesster_gelenk` und den Maßstäben des Servers)
     * @param {number[]} indizes globale Knochennummern der Rig-Punkte der Zeile (gleiche Reihenfolge wie `rig.soll`)
     * @param {{name: string, eltern: number}[]} knochen das Rig (`antwort.rig.knochen`)
     */
    static werte(teil, indizes, knochen) {
        const rig = teil?.rig;
        if (!rig?.je_mm?.length || !rig.soll || !rig.ausgabe || !indizes) return null;
        const f = rig.je_mm;
        const n = f.length;
        const sortiert = [...f].sort((a, b) => a - b);
        const summe = f.reduce((s, x) => s + x, 0);
        const versatz = [0, 1, 2].map(a => rig.ausgabe.reduce((s, p, i) => s + p[a] - rig.soll[i][a], 0) / n);
        const ohneVersatz = rig.ausgabe.reduce((s, p, i) => s + Math.hypot(...[0, 1, 2].map(a => p[a] - versatz[a] - rig.soll[i][a])), 0) / n * 1000;
        const platz = new Map(indizes.map((j, k) => [j, k]));
        let winkel = 0;
        let laenge = 0;
        let paare = 0;
        indizes.forEach((j, k) => {
            const e = platz.get(knochen[j]?.eltern);
            if (e === undefined) return;
            const s = [0, 1, 2].map(a => rig.soll[k][a] - rig.soll[e][a]);
            const v = [0, 1, 2].map(a => rig.ausgabe[k][a] - rig.ausgabe[e][a]);
            const ls = Math.hypot(...s);
            const lv = Math.hypot(...v);
            if (ls < 0.001 || lv < 1e-9) return;
            const cos = Math.max(-1, Math.min(1, (s[0] * v[0] + s[1] * v[1] + s[2] * v[2]) / (ls * lv)));
            winkel += Math.acos(cos) * 180 / Math.PI;
            laenge += Math.abs(lv - ls) * 1000;
            paare += 1;
        });
        const k = teil.kennzahlen ?? {};
        return {
            punkte: n, mittel: summe / n, median: Mesh3daiguete._quantil(sortiert, 0.5), p90: Mesh3daiguete._quantil(sortiert, 0.9),
            groesster: sortiert[n - 1], groessterName: k.groesster_gelenk ?? '', rms: Math.sqrt(f.reduce((s, x) => s + x * x, 0) / n),
            unter: Mesh3daiguete.SCHWELLEN.map(s => [s, 100 * f.filter(x => x < s).length / n]),
            versatz: Math.hypot(...versatz) * 1000, ohneVersatz,
            paare, winkel: paare ? winkel / paare : null, laenge: paare ? laenge / paare : null,
            mittlerePose: k.mittlere_pose_mm ?? null, naechstePose: k.naechste_pose_mm ?? null, naechsteNr: k.naechste_pose_nr ?? null,
        };
    }

    /** Die kleine Tabelle (Kennzahl · Wert · was sie heißt) zu `werte(…)`; `null` → leeres Element. */
    static tabelle(w) {
        const huelle = document.createElement('div');
        if (!w) return huelle;
        const mm = x => (x == null ? '—' : `${de(x)} mm`);
        const zeilen = [
            [`Ø Fehler (${w.punkte} Rig-Punkte)`, mm(w.mittel), 'Abstand Ergebnis ↔ Ziel, gemittelt'],
            ['Median', mm(w.median), 'die Hälfte der Punkte liegt darunter'],
            ['90 %-Wert', mm(w.p90), '90 % der Punkte liegen darunter'],
            ['Größter Fehler', `${mm(w.groesster)}${w.groessterName ? ` (${w.groessterName})` : ''}`, 'schlechtester Punkt'],
            ['RMS', mm(w.rms), 'Wurzel aus dem mittleren Quadrat — straft Ausreißer'],
            ...w.unter.map(([s, p]) => [`Punkte unter ${s} mm`, `${de(p, 0)} %`, 'Anteil der Punkte']),
            ['Versatz der Zeile', mm(w.versatz), 'Länge des mittleren Fehlervektors: um so viel sitzt alles verschoben'],
            ['Ø Fehler ohne Versatz', mm(w.ohneVersatz), 'nach Abzug des Versatzes: Fehler der Form (kann knapp über dem Ø liegen — abgezogen wird der mittlere Fehlervektor, er macht die Quadrate kleinste, nicht die Abstände)'],
            [`Ø Richtungsfehler (${w.paare} Knochen)`, w.winkel == null ? '—' : `${de(w.winkel)}°`, 'Winkel Eltern → Knochen gegen das Ziel'],
            ['Ø Längenfehler der Knochen', mm(w.laenge), 'Länge Eltern → Knochen gegen das Ziel'],
            ['Mittlere Trainingspose', mm(w.mittlerePose), 'Fehler, wenn man immer die mittlere Trainingspose sagt — das Netz muss darunter liegen'],
            [`Nächste Trainingspose${w.naechsteNr != null ? ` (Probe ${w.naechsteNr})` : ''}`, mm(w.naechstePose), 'Abstand zur ähnlichsten Trainingspose — wie weit die Pose vom Gelernten weg ist'],
        ];
        const tabelle = document.createElement('table');
        tabelle.className = 'mesh3dai-guetetabelle';
        const kopf = tabelle.createTHead().insertRow();
        for (const t of ['Wie gut?', 'Wert']) kopf.append(Object.assign(document.createElement('th'), { textContent: t }));
        const koerper = tabelle.createTBody();
        for (const [name, wert, hinweis] of zeilen) {
            const zeile = koerper.insertRow();
            zeile.title = hinweis;
            zeile.append(Object.assign(document.createElement('td'), { textContent: name }), Object.assign(document.createElement('td'), { textContent: wert, className: 'num' }));
        }
        huelle.append(tabelle);
        return huelle;
    }
}
