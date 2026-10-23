/**
 * Mesh3daiechtteile — Daten und Texte der Zeilen bei ECHTEN Daten auf der Seite „Mesh3D-AI“ (15.10.2026, Edgar: „fixe alles“).
 * Der Server (`Mesh3daidatenteile`) schickt je Zeile nur Kennzahlen und Ausschnitte (Mitte, Ziel, Radius, Knochen); die Rig-Punkte nimmt diese Klasse aus dem Rig der Probe (`probe.rig`, 138 Punkte) —
 * die Knochen der Zeile (`antwort.rig.zeilen`), um `ziel − mitte` ihres Ausschnitts gerückt (Gesicht auf die Kopfmitte, Hände und Füße auf ihre Plätze). Soll und Ausgabe werden um dieselbe Strecke gerückt.
 * Das Netz sagt NUR die 138 Rig-Punkte voraus — eine Zeile ist ein Ausschnitt davon, keine eigene Vorhersage; die Flächen sind die gehäutete Figur der Probe (`Mesh3daiflaechen`).
 */
const de = n => n.toLocaleString('de-DE');

export class Mesh3daiechtteile {
    /** `{beschreibung, teil}` der Zeile `schluessel` oder `null`; das Ergebnis wird an der Probe gemerkt (die Zeile wird bei jedem Ansichtswechsel neu gezeichnet). */
    static daten(antwort, probe, schluessel) {
        const beschreibung = antwort.teile?.[schluessel];
        const roh = probe.teile?.[schluessel];
        if (!beschreibung || !roh || !probe.rig) return null;
        probe._zeilen ??= {};
        probe._zeilen[schluessel] ??= Mesh3daiechtteile._bauen(antwort.rig.zeilen[schluessel], probe.rig, roh);
        return { beschreibung, teil: probe._zeilen[schluessel] };
    }

    static _bauen(indizes, rig, roh) {
        const verschub = new Map();
        for (const a of roh.ausschnitte) {
            const v = a.ziel.map((z, i) => z - a.mitte[i]);
            for (const j of a.knochen) verschub.set(j, v);
        }
        const ruecken = lagen => indizes.map(j => {
            const v = verschub.get(j);
            const p = lagen[j];
            return v ? [p[0] + v[0], p[1] + v[1], p[2] + v[2]] : p;
        });
        // Zwischenschritt „nur Rig“ (16.10.2026): das Skelett von „Mesh to 3D“ in der Außenfläche, um dieselbe Strecke gerückt wie Soll und Ausgabe.
        const auto = rig.autorig ? { ...rig.autorig, rig: ruecken(rig.autorig.rig), je_mm: indizes.map(j => rig.autorig.je_mm[j]) } : null;
        return { ...roh, rig: { ...roh.rig, soll: ruecken(rig.soll), ausgabe: ruecken(rig.ausgabe), je_mm: indizes.map(j => rig.je_mm[j]), autorig: auto } };
    }

    /** Zeile unter „Start“: das Rig im Netz (Knopf „Rig“) ist das, was Mesh3D-AI vorhersagt (16.10.2026, `Mesh3dairigzeichner.ueberlagern`), mit seinem Abstand zum Ziel-Rig (Mittel über die Rig-Punkte der Zeile). */
    static kiRigText(teil, weg = null) {
        const je = teil.rig?.je_mm;
        if (!je?.length) return '';
        const mittel = je.reduce((s, x) => s + x, 0) / je.length;
        // Mehrere Wege (Job UrsulaSpagat, 16.10.2026): das Rig im Netz ist das des gewählten Wegs (`Mesh3daiwegwahl`).
        // Kurz seit 20.10.2026 abends (Edgar: „ich brauche keine Romane“).
        const wer = weg ? `Rig (Weg „${weg.name}“)` : 'Rig der KI';
        return `\n${wer}: Ø ${de(Math.round(mittel * 10) / 10)} mm zum Ziel.`;
    }

    /** Text unter „Ergebnis“: Fehler je Gruppe von Rig-Punkten. Ø, größter, Anteile und Maßstäbe stehen seit 16.10.2026 in der Tabelle darunter (`Mesh3daiguete`). */
    static ausgabeText(k, knochen, zusatz = '') {
        const gruppen = Object.entries(k.je_gruppe_mm).map(([g, mm]) => `${g} ${de(mm)}`).join(' · ');
        return `${zusatz}Ø Fehler (mm): ${gruppen}`;
    }

    /** Was das Eingabefeld zeigt: Fläche (Ansichtsart) oder Punktwolke. */
    static eingabeText(probe, modus, flaecheText, wolkeText) {
        const w = probe.eingabeEcht;
        const wolke = w ? `${wolkeText}: ${de(w.anzahl ?? w.punkte.length)} von ${de(w.von)} Punkten` : 'Punkte werden geholt …';
        if (modus === 'punkte' && w) return wolke;
        if (probe.flaeche) {
            const bild = probe.animation ? ' (Bild der Animation, ohne Haar)' : '';
            return `${flaecheText}${bild}.`;
        }
        if (probe.flaecheFehlt) return `Fläche: ${probe.flaecheFehlt} — hier die Punktwolke.\n${wolke}`;
        return probe.animation ? 'Flächen der Animation werden geholt (ein Paket für alle Bilder, rund 38 MB) …' : 'Fläche wird geholt …';
    }

    /** Die drei Texte einer Zeile; `modell` = die Figur des Jobs (Server `Mesh3daidaten`, Feld `modell` — bis 16.10.2026 stand hier fest „Ursula1“, auch auf der Seite von Mann1). */
    static texte(schluessel, probe, teil, modus, modell = 'Ursula1') {
        const z = Mesh3daiechtteile;
        const texte = z._texte(schluessel, probe, teil, modus, modell);
        const weg = probe.wege?.[probe.weg] ?? null;
        if (texte.eingabe) texte.eingabe += z.kiRigText(teil, weg);
        // Nur der Name des Wegs (20.10.2026 abends); seine lange Beschreibung (`weg.text`) steht nicht mehr unter dem Feld.
        if (weg && texte.ausgabe) texte.ausgabe = `Weg „${weg.name}“\n${texte.ausgabe}`;
        return texte;
    }

    static _texte(schluessel, probe, teil, modus, m) {
        const z = Mesh3daiechtteile;
        const knochen = teil.rig.kennzahlen.knochen;
        // Ursula_Pose1, Probe 1: die Eingabe kommt aus einer OBJ-Datei (gelesen wie von einem Datenlader; Außenfläche und Punkte aus ihrer Geometrie).
        const ausDatei = probe.datei ? `Datei ${probe.datei}: ` : '';
        // Seit 19.10.2026 spätabends (Edgar: „das Ergebnis soll direkt aus der KI kommen“): die Fläche im Ergebnis ist die Figur der KI (`Mesh3daiergebnisfigur`), nie die des Jobs.
        // Kurz seit 20.10.2026 abends (Edgar: „ich brauche keine Romane, kurz und bündig“).
        const ohneFlaeche = probe.rig?.dreh ? `Figur der KI (nicht ${m}).\n` : 'Nur Rig-Punkte, keine Fläche.\n';
        const rig = `Rig ${de(knochen)} Knochen`;
        switch (schluessel) {
            case 'koerper':
                return {
                    eingabe: z.eingabeText(probe, modus, probe.start === 'wolke' ? `${ausDatei}Tripo-Netz mit Textur` : `${ausDatei}Außenfläche von ${m}`, 'Punkte'),
                    soll: `${probe.quelle} · ${m}, ${rig}`,
                    ausgabe: z.ausgabeText(teil.kennzahlen, knochen, ohneFlaeche),
                };
            case 'koerper_nackt':
                return {
                    eingabe: z.eingabeText(probe, modus, 'Außenfläche mit Kleidern', 'Punkte'),
                    soll: `Haut von ${m}, ${rig}`,
                    ausgabe: z.ausgabeText(teil.kennzahlen, knochen, ohneFlaeche),
                };
            case 'gesicht':
                return {
                    eingabe: z.eingabeText(probe, modus, 'Außenfläche um den Kopf', 'Punkte'),
                    soll: `Kopf von ${m}, ${rig}`,
                    ausgabe: z.ausgabeText(teil.kennzahlen, knochen, ohneFlaeche),
                };
            case 'haende':
                return {
                    eingabe: z.eingabeText(probe, modus, 'Hände oben, Füße unten', 'Punkte'),
                    soll: `Hände und Füße von ${m}, ${rig}`,
                    ausgabe: z.ausgabeText(teil.kennzahlen, knochen, ohneFlaeche),
                };
            case 'kleider':
                return {
                    eingabe: z.eingabeText(probe, modus, 'Stoff der Außenfläche', 'Punkte'),
                    soll: `Kleider von ${m}, ${rig}`,
                    ausgabe: z.ausgabeText(teil.kennzahlen, knochen, ohneFlaeche),
                };
            default:
                return {};
        }
    }
}
