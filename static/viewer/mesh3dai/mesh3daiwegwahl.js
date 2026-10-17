/**
 * Mesh3daiwegwahl — Wahl des Wegs zum Rig einer Probe auf der Jobseite von Mesh3D-AI (16.10.2026, Job UrsulaSpagat).
 * Edgar: „ist ja noch sehr schlecht, sowohl das Rig bei dem Mesh ist falsch als das Ergebnis“ — die Seite zeigte nur das Netz direkt auf der Spagat-Pose. Hat eine Probe mehrere Wege (Server `Mesh3daiwege`:
 * Rig → A-Pose → Netz · Netz direkt · Rig allein), steht über den Zeilen je Weg ein Schaltknopf; der gewählte Weg setzt Rig (im Start und im Ergebnis), Kennzahlen und Zeilen der Probe.
 * Vorgabe ist der Weg, den der Server als `weg` schickt.
 */
const de = n => n.toLocaleString('de-DE');

export class Mesh3daiwegwahl {
    /** Die Knopfreihe für `probe` oder `null` (keine Wege). `beiWechsel` zeichnet die Seite neu. */
    static knoepfe(probe, beiWechsel) {
        if (!probe?.wege || !probe.wege_reihe?.length) return null;
        const leiste = document.createElement('span');
        leiste.className = 'schalterleiste mesh3dai-wegwahl';
        leiste.setAttribute('role', 'group');
        leiste.setAttribute('aria-label', 'Weg zum Rig dieser Probe');
        leiste.append(Object.assign(document.createElement('span'), { className: 'mesh3dai-wegwahl-titel', textContent: 'Weg:' }));
        for (const schluessel of probe.wege_reihe) {
            const w = probe.wege[schluessel];
            const knopf = document.createElement('button');
            knopf.type = 'button';
            knopf.className = `schaltknopf${probe.weg === schluessel ? ' active' : ''}`;
            knopf.setAttribute('aria-pressed', String(probe.weg === schluessel));
            knopf.dataset.weg = schluessel;
            knopf.title = `${w.text} Ø ${de(w.kennzahlen.mittel_mm)} mm zum Ziel-Rig (138 Rig-Punkte).`;
            knopf.textContent = `${w.name} · ${de(w.kennzahlen.mittel_mm)} mm`;
            knopf.addEventListener('click', () => {
                if (Mesh3daiwegwahl.waehlen(probe, schluessel)) beiWechsel();
            });
            leiste.append(knopf);
        }
        return leiste;
    }

    /** Den Weg `schluessel` an der Probe einsetzen — `false`, wenn es ihn nicht gibt oder er schon gilt. Die Zeilen der Probe (`_zeilen`) werden neu gebaut. */
    static waehlen(probe, schluessel) {
        const w = probe.wege?.[schluessel];
        if (!w || probe.weg === schluessel) return false;
        // Das Skelett von „Mesh to 3D“ (`autorig`, Ursula1) hängt an der Probe, nicht am Weg.
        probe.rig = { ...w.rig, autorig: probe.rig?.autorig ?? null };
        probe.kennzahlen = w.kennzahlen;
        probe.teile = w.teile;
        probe.weg = schluessel;
        delete probe._zeilen;
        return true;
    }

    /** Name und Text des gewählten Wegs der Probe oder `null`. */
    static gewaehlt(probe) {
        return probe?.wege?.[probe.weg] ?? null;
    }
}
