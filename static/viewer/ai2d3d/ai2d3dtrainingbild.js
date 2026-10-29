/**
 * Ai2d3dtrainingbild — Feld 3 der Kopf- und Körperzeilen der Jobseite: die Geometrie, die das Training der Kopf-KI misst (27.10.2026, Edgar: „dann soll das Training erst die geometrische
 * Form zeigen, die muss perfekt sein. mach ggf. ein viertes Bild rechts in jeder Zeile wo das geometrische Ergebnis zu sehen ist“; später an 3. Stelle).
 *
 * Daten: `<Job>/abnahme/training.json` (`Traininggeometrie`, vom Lauf selbst geschrieben — ohne Übernahme und Kette; die Seite baut die Figur aus den Reglern neu, und die lag
 * gemessen im Mittel 10 mm neben der des Trainings). Je Foto (Nummer wie `seite_<nr>.png`): die Umrisse der Kopf-Eigenregler — blau der Rand im Foto, grün der Rand der Figur des
 * Trainings (das, was der Verlust misst), rot je Strahl blau → grün — und die Gesichtspunkte (insightface im Foto, an der Figur die Punkte, auf die trainiert wurde). In den Körperzeilen
 * (`koerper`) der Umriss des ganzen Körpers (`Umrissabstand.zeichnung`): blau Foto, grün Figur, rot je Punkt zum nächsten der anderen Seite.
 * Ausschnitt und Maßstab wie die übrigen Felder der Zeile (27.10.2026, Edgar: „mach das Geometrie bild im gleichen Massstab wie die anderen“), darauf schwarz der Umriss des
 * Genesis-Ergebnisses („mach die schwarze Linie drauf des Genesis Ergebnisses“) — seit 29.10.2026 das des Laufs aus training.json (`_genesis`), vorher die Linien des Blocks.
 * Hintergrund: das Foto, blass.
 */
import { Ai2d3dmessstrich } from './ai2d3dmessstrich.js';

export class Ai2d3dtrainingbild {
    /** Die gerechnete Figur grün (27.10.2026, Edgar: „die Maße und Linien der geometrischen Figur bitte grün“; bis dahin schwarz); schwarz das Genesis-Ergebnis. */
    static FARBE = { vorlage: '#1c7ed6', ergebnis: '#2f9e44', verbindung: '#e03131', genesis: '#000000' };

    /** Feld 3 in `element` für Bild `nr` (ab 1). `daten`: training.json oder {fehler}; `zeile`: die `Ai2d3dmesspunkte` der Zeile (Foto, Ausschnitt, Linien des Genesis-Ergebnisses). */
    static zeichnen(element, nr, daten, zeile, koerper = false) {
        const flaeche = element.querySelector('canvas[data-training]'), info = element.querySelector('[data-training-info]');
        const f = daten?.fotos?.[String(nr)], k = koerper ? f?.koerper : null;
        if (!f || (koerper && !k)) {
            info.textContent = daten?.fehler ? `Kein Trainingsergebnis: ${daten.fehler}`
                : f ? `Lauf ${daten.lauf} hat den Körper nicht gerechnet, nur den Kopf.` : `Dieses Foto war nicht im Training (${daten?.lauf ?? '—'}).`;
            Object.assign(flaeche, { width: 0, height: 0 });
            return;
        }
        if (!zeile.f || !zeile.foto) {
            info.textContent = 'Die Zeile hat kein Foto geladen — kein Ausschnitt.';
            return;
        }
        const a = zeile._ausschnitt(flaeche);
        const dpr = window.devicePixelRatio || 1;
        Object.assign(flaeche, { width: Math.round(a.b * dpr), height: Math.round(a.h * dpr) });
        Object.assign(flaeche.style, { width: `${a.b}px`, height: `${a.h}px` });
        const c = flaeche.getContext('2d');
        c.setTransform(dpr, 0, 0, dpr, 0, 0);
        c.fillStyle = '#ffffff';
        c.fillRect(0, 0, a.b, a.h);
        const [kx, ky, kx1, ky1] = a.k;
        c.globalAlpha = 0.5;
        c.drawImage(zeile.foto, kx, ky, kx1 - kx, ky1 - ky, 0, 0, a.b, a.h);
        c.globalAlpha = 1;
        const auf = p => [(p[0] - kx) * a.s, (p[1] - ky) * a.s], F = Ai2d3dtrainingbild.FARBE;
        if (k) Ai2d3dtrainingbild._koerper(c, auf, k, zeile, F);
        else Ai2d3dtrainingbild._kopf(c, auf, f, zeile, F);
        // Hover wie in den anderen Feldern (27.10.2026, `Ai2d3dmesszeiger`): der Punkt unter dem Zeiger blau (Foto) — schwarz nicht mehr (29.10.2026): die Punkte der Zeile gehören
        // zum Rendering des Blocks, Schwarz in diesem Feld ist das Genesis-Ergebnis des Laufs (`_genesis`)
        if (zeile.zeiger) {
            zeile.zeiger.anmelden(flaeche);
            zeile.zeiger.merken(flaeche, auf, zeile.f, 'beide');
            for (const p of zeile.f.punkte) {
                if (!zeile.zeiger.zeigt(p.nr)) continue;
                for (const [seite, farbe] of [['vorlage', F.vorlage]]) {
                    if (!p[seite]) continue;
                    const [x, y] = auf(p[seite]);
                    c.fillStyle = farbe;
                    c.beginPath();
                    c.arc(x, y, 3, 0, 2 * Math.PI);
                    c.fill();
                    if (seite === 'vorlage') Ai2d3dmessstrich.nummer(c, String(p.nr), x + 4, y - 4, '#111111', false);
                }
            }
        }
        const z = x => (x === null || x === undefined ? '—' : new Intl.NumberFormat('de-DE', { maximumFractionDigits: 1, minimumFractionDigits: 1 }).format(x));
        const neu = f.mm.gesicht_neu === null || f.mm.gesicht_neu === undefined ? '' : ` (neu erkannt ${z(f.mm.gesicht_neu)} mm)`;
        // Zusatzfotos (Konzept „vier Fotos“): gerechnet nur die Punkte, die keine Master-Ansicht sieht, die übrigen nur geprüft
        const teil = (t, m) => (m ? `${t} ${z(m.mittel)} mm (90 %: ${z(m.p90)} mm, ${m.punkte} Punkte)` : `${t} —`);
        const umriss = k?.mm_gerechnet !== undefined ? `${teil('gerechnet', k.mm_gerechnet)}, ${teil('nur geprüft', k.mm_geprueft)}`
            : teil('Umriss des Körpers', k?.mm);
        const g = f.koerper?.genesis;
        const schwarz = g ? `schwarz das Genesis-Ergebnis (${teil('Umriss', g.mm)})` : 'schwarz: zu diesem Lauf noch kein Genesis-Ergebnis';
        info.textContent = k ? `Lauf ${daten.lauf} · ${f.datei}: ${umriss} — blau Foto, grün die gerechnete Figur, ${schwarz}.`
            : `Lauf ${daten.lauf} · ${f.datei}: Umriss ${z(f.mm.umriss)} mm (${f.mm.strahlen} Strahlen), Gesicht ${z(f.mm.gesicht)} mm${neu}, `
            + `ViTPose ${z(f.mm.vit)} mm — blau Foto, grün die gerechnete Figur, ${schwarz}.`;
    }

    /**
     * Schwarz: der Umriss des Genesis-Ergebnisses DIESES Laufs (29.10.2026, Edgar: „den Unterschied zwischen den linien siehst du. Das soll als Fehlerfall gelten“) — Genesis-Figur
     * mit Augen und Hüllen in derselben Kamera wie Blau und Grün (`Genesisumriss`, `koerper.genesis` in training.json). Bis dahin die Linien des Blocks: am 27.10.2026 gerendert und
     * gemessen (Stand nurjob4), also eine andere Figur als die des Laufs. Fehlt das Ergebnis, steht kein Schwarz da — nie das eines anderen Laufs.
     */
    static _genesis(c, auf, f, F) {
        const g = f.koerper?.genesis;
        if (g) Ai2d3dtrainingbild._punkte(c, auf, g.ergebnis, F.genesis, 1.6);
    }

    static _kopf(c, auf, f, zeile, F) {
        // Blau breit darunter: liegen Foto und Figur aufeinander, verdeckte die Linie der Figur die blaue ganz (27.10.2026, Edgar: „Die blaue Linie … fehlt“)
        c.lineWidth = 4;
        c.strokeStyle = F.vorlage;
        for (const u of f.umrisse) Ai2d3dmessstrich._kette(c, auf, u.vorlage, u.geschlossen);
        Ai2d3dtrainingbild._genesis(c, auf, f, F);
        Ai2d3dmessstrich.umrisse(c, auf, f.umrisse, ['ergebnis'], F, null);
        c.strokeStyle = F.verbindung;
        for (const u of f.umrisse) u.vorlage.forEach((p, i) => { if (p && u.ergebnis[i]) Ai2d3dmessstrich.strich(c, auf(p), auf(u.ergebnis[i])); });
        Ai2d3dtrainingbild._gesicht(c, auf, f, F);
        Ai2d3dtrainingbild._ohren(c, auf, f, zeile, F);
    }

    /** Regler des Ohrs → Name in `Ohrabstand.zeichnung` */
    static OHR = { 'KO-12': 'Ohr links', 'KO-13': 'Ohr rechts' };

    /** Die Ohren (27.10.2026, `Ohrabstand`): SAM-3-Umriss im Foto blau breit, Ohr der gerechneten Figur grün, rot je Stelle. Misst der Lauf ein Ohr nicht (Zusatzfoto, ältere
     *  Läufe), steht das Foto-Ohr trotzdem blau da — aus den Umrissen der Zeile (`ohren.json`), wie in Feld 1 (27.10.2026, Edgar: „das blaue Ohr fehlt noch“). */
    static _ohren(c, auf, f, zeile, F) {
        const gemessen = new Set((f.ohren ?? []).map(o => o.name));
        c.lineWidth = 4;
        c.strokeStyle = F.vorlage;
        for (const u of zeile.f.umrisse ?? []) {
            const name = Ai2d3dtrainingbild.OHR[u.regler];
            if (name && !gemessen.has(name)) Ai2d3dmessstrich._kette(c, auf, u.vorlage, true);
        }
        for (const o of f.ohren ?? []) {
            c.lineWidth = 4;
            c.strokeStyle = F.vorlage;
            Ai2d3dmessstrich._kette(c, auf, o.vorlage, true);
            c.lineWidth = 2;
            c.strokeStyle = F.ergebnis;
            Ai2d3dmessstrich._kette(c, auf, o.ergebnis, true);
            for (const t of o.teile ?? []) Ai2d3dmessstrich._kette(c, auf, t, true);      // weitere Flecken der Figurmaske (gemessen wird der Rand aller)
            // rot je Fotopunkt zum nächsten Punkt der Figur — so misst `Ohrabstand`; bis 28.10.2026 Punkt i zu Punkt i, das ergab bei verschieden geformten Umrissen einen Fächer
            c.lineWidth = 1;
            c.strokeStyle = F.verbindung;
            const figur = [o.ergebnis, ...(o.teile ?? [])].flat().filter(Boolean);
            for (const p of o.vorlage) {
                if (!p || !figur.length) continue;
                const q = figur.reduce((a, b) => ((b[0] - p[0]) ** 2 + (b[1] - p[1]) ** 2 < (a[0] - p[0]) ** 2 + (a[1] - p[1]) ** 2 ? b : a));
                Ai2d3dmessstrich.strich(c, auf(p), auf(q));
            }
        }
    }

    /** Körper: Umriss als Punkte (ungeordnet, darum keine Kette) — blau Foto, rot je Punkt zum nächsten der anderen Seite, grün die Figur. */
    static _koerper(c, auf, k, _zeile, F) {
        Ai2d3dtrainingbild._genesis(c, auf, { koerper: k }, F);
        Ai2d3dtrainingbild._punkte(c, auf, k.vorlage, F.vorlage, 2);
        c.strokeStyle = F.verbindung;
        c.lineWidth = 1;
        for (const [p, q] of k.linien) Ai2d3dmessstrich.strich(c, auf(p), auf(q));
        Ai2d3dtrainingbild._punkte(c, auf, k.ergebnis, F.ergebnis, 1.3);
    }

    static _punkte(c, auf, punkte, farbe, r) {
        c.fillStyle = farbe;
        for (const p of punkte) {
            const [x, y] = auf(p);
            c.fillRect(x - r / 2, y - r / 2, r, r);
        }
    }

    /** Gesichtspunkte: Ketten des Schemas blau (Foto) und grün (Training), je Punkt die rote Linie. */
    static _gesicht(c, auf, f, F) {
        const nach = new Map(f.gesicht.map(p => [p.nr, p]));
        for (const k of f.ketten) {
            for (const [seite, breite] of [['vorlage', 3.5], ['ergebnis', 1.5]]) {      // Blau breit darunter, Grün schmal darüber
                c.lineWidth = breite;
                c.strokeStyle = F[seite];
                Ai2d3dmessstrich._kette(c, auf, k.punkte.map(i => nach.get(i)?.[seite] ?? null), k.geschlossen);
            }
        }
        c.lineWidth = 1;
        c.strokeStyle = F.verbindung;
        for (const p of f.gesicht) Ai2d3dmessstrich.strich(c, auf(p.vorlage), auf(p.ergebnis));
        // keine Punkte — nur der unter dem Zeiger (27.10.2026, Edgar: „mache die Punkte weg … und zeige sie nur an bei hover“)
    }
}
