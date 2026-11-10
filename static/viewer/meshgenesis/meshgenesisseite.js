/**
 * Meshgenesisseite — Einstieg der Seite EINES Jobs von „Mesh-Genesis“ (`/mesh-genesis/<job>/`, 14.10.2026; der Job steht als `data-job` am Block `#meshgenesis-job`, die Liste aller Jobs ist `meshgenesisliste.js`):
 * holt den Kurzstand (`/api/meshgenesis/jobs/`) und die Proben des Jobs, baut die Zeilen (ganzer Körper, Gesicht, Hände/Füße, Kleider; je Zeile
 * Eingabe · gewünschte Ausgabe · Ausgabe des Netzes), die Probenwahl und die Kennzahlen. Heute liefert der Server Dummies für „Ursula1“ (`attrappe: true`); die Seite zeigt es deutlich an und rechnet selbst nichts.
 */
import { Genesis9aufbau } from '../gemeinsam/genesis9aufbau.js';
import { Netzstufenschalter } from '../gemeinsam/netzstufenschalter.js';
import { Netzstufenstand } from '../gemeinsam/netzstufenstand.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshgenesisanimationsdaten } from './meshgenesisanimationsdaten.js';
import { Meshgenesisanimationsleiste } from './meshgenesisanimationsleiste.js';
import { Meshgenesisansichtgedaechtnis } from './meshgenesisansichtgedaechtnis.js';
import { Meshgenesisapose } from './meshgenesisapose.js';
import { Meshgenesisflaechen } from './meshgenesisflaechen.js';
import { Meshgenesisflaechennetz } from './meshgenesisflaechennetz.js';
import { Meshgenesisfigurbewegung } from './meshgenesisfigurbewegung.js';
import { Meshgenesisfigurbewegungsleiste } from './meshgenesisfigurbewegungsleiste.js';
import { Meshgenesisgenesisfigur } from './meshgenesisgenesisfigur.js';
import { Meshgenesiskikleiderfeld } from './meshgenesiskikleiderfeld.js';
import { Meshgenesisprobenwahl } from './meshgenesisprobenwahl.js';
import { Meshgenesisstand } from './meshgenesisstand.js';
import { Meshgenesiswegwahl } from './meshgenesiswegwahl.js';
import { Meshgenesiszeichenflaeche } from './meshgenesiszeichenflaeche.js';
import { Meshgenesiszeile } from './meshgenesiszeile.js';

export class Meshgenesisseite {
    static aufbauen() {
        const seite = new Meshgenesisseite();
        seite.starten().catch(fehler => seite.fehler(fehler));
        return seite;
    }

    constructor() {
        const hole = id => document.getElementById(id);
        Meshgenesiszeichenflaeche.renderer();          // vor der ersten Figur: der Renderer meldet sich beim `Texturweg` (Weg C prüft S3TC, bevor eine Adresse entsteht)
        this.jobId = hole('meshgenesis-job').dataset.job;
        this.jobinfo = hole('meshgenesis-jobinfo');
        this.zusammenfassung = hole('meshgenesis-zusammenfassung');
        this.probeninfo = hole('meshgenesis-probeninfo');
        this.geist = hole('meshgenesis-geist');
        this.kennzahlen = hole('meshgenesis-kennzahlentext');
        this.zeilen = [...document.querySelectorAll('.meshgenesis-zeile')].map(el => new Meshgenesiszeile(el));
        // Die Felder zeichnen nur auf Anforderung: ein Bild der Figur, das nach dem ersten Zeichnen kommt, muss sie neu zeichnen lassen.
        Meshgenesisflaechennetz.nachLaden = () => this.zeilen.forEach(zeile => zeile.ansichten.forEach(a => a.zeichnen()));
        // Genesis-Figuren in Ziel und Ergebnis (`Meshgenesisgenesisfigur`): fertig gebaut oder neue Netzstufe → die Felder hängen sie neu ein. Strg+Alt+H schaltet die Stufe wie in Charakter;
        // die Seite beginnt mit „grob“ (`<meta name="schnellanzeige">`) und lädt dabei nie neu.
        Meshgenesisgenesisfigur.neuZeichnen = () => this.zeilen.forEach(zeile => zeile.ansichten.forEach(a => (a.art === 'soll' || a.art === 'ausgabe') && a.neuZeigen()));
        Meshgenesisgenesisfigur.nurZeichnen = () => this.zeilen.forEach(zeile => zeile.ansichten.forEach(a => (a.art === 'soll' || a.art === 'ausgabe') && a.zeichnen()));
        Netzstufenschalter.einrichten(window, async ziel => (await Genesis9aufbau.stufeSetzen(Meshgenesisgenesisfigur.modelle(), ziel), Meshgenesisgenesisfigur.neuZeichnen(), true));
        this.wahl = new Meshgenesisprobenwahl({
            chips: hole('meshgenesis-chips'), zurueck: hole('meshgenesis-zurueck'), weiter: hole('meshgenesis-weiter'), zaehler: hole('meshgenesis-zaehler'),
            nurPruefung: hole('meshgenesis-nurpruefung'), schlechtZuerst: hole('meshgenesis-schlechtzuerst'),
        }, probe => this.zeigen(probe));
        this.daten = null;
        this.filter = { nurPruefung: hole('meshgenesis-nurpruefung'), schlechtZuerst: hole('meshgenesis-schlechtzuerst') };
        this.geist.addEventListener('change', () => {
            Meshgenesisansichtgedaechtnis.merken({ geist: this.geist.checked });
            this.zeilen.forEach(zeile => zeile.geistSetzen(this.geist.checked));
        });
        for (const [schluessel, kaestchen] of Object.entries(this.filter)) kaestchen.addEventListener('change', () => Meshgenesisansichtgedaechtnis.merken({ [schluessel]: kaestchen.checked }));
        document.addEventListener('keydown', Meshgenesisanimationsleiste.leertaste);
        // Standardanimation der Ergebnisfigur (22.10.2026, wie Mesh-3D): im Feld „Ergebnis“ der Zeile „Ganzer Körper“; ohne Tasten (Pfeile wählen die Probe, die Leertaste spielt die Zeilen).
        const feld = this.zeilen.find(z => z.schluessel === 'koerper')?.ansichten.find(a => a.art === 'ausgabe');
        const leiste = document.querySelector('[data-figurbewegung]');
        if (feld && leiste) {
            this.bewegung = new Meshgenesisfigurbewegung(feld, () => this._bewegungsquelle());
            const figurleiste = new Meshgenesisfigurbewegungsleiste(leiste, this.bewegung);
            figurleiste.wahlLaden(leiste.dataset.adresse);
            // Jobs ohne Spagat-Bewegung (Tripo-Jobs): Play in den Zeilenköpfen und die Leertaste bedienen diese Bewegung.
            figurleiste.nachAnzeige = () => Meshgenesisanimationsleiste.figurGeaendert();
            Meshgenesisanimationsleiste.figur = {
                umschalten: () => figurleiste.befehl(b => b.umschalten()),
                stellen: anteil => figurleiste.befehl(b => b.stellen(anteil * b.dauer)),
                zustand: () => figurleiste.zustand(),
            };
        }
        this._festhalten(hole('meshgenesis-oben'));
        // Die einzige ECHTE Karte der Seite: Datensatz und Training von der Platte, im Takt der Einstellung (Einstellungen → Mesh-Genesis).
        this.stand = Meshgenesisstand.aufbauen(this.jobId, hole('meshgenesis-stand'));
    }

    /**
     * Der Block oben bleibt beim Blättern stehen (CSS `position: sticky`); die Köpfe der Zeilen hängen darunter. Dafür müssen Höhe der Kopfleiste der Seite (`.topbar`, ebenfalls sticky) und Höhe des Blocks bekannt sein —
     * beide ändern sich (Fensterbreite, Zahl der Zeilen mit Kästchen), darum als CSS-Werte, die ein `ResizeObserver` nachführt.
     */
    _festhalten(oben) {
        const leiste = document.querySelector('.topbar');
        const wurzel = document.documentElement.style;
        const messen = () => {
            wurzel.setProperty('--meshgenesis-leiste', `${leiste ? Math.round(leiste.getBoundingClientRect().height) : 0}px`);
            wurzel.setProperty('--meshgenesis-oben', `${Math.round(oben.getBoundingClientRect().height)}px`);
        };
        const beobachter = new ResizeObserver(messen);
        beobachter.observe(oben);
        if (leiste) beobachter.observe(leiste);
        messen();
    }

    async starten() {
        // Die gemerkte Ansicht (Textur, Rig …) kommt mit, bevor die erste Probe gezeichnet wird (16.10.2026).
        const [antwort, gemerkt] = await Promise.all([Serverabruf.json('/api/meshgenesis/jobs/'), Meshgenesisansichtgedaechtnis.laden()]);
        Meshgenesiszeile.gemerktSetzen(gemerkt);
        // Filter und Geist wie beim letzten Mal (17.10.2026), bevor die Probenwahl aufbaut.
        for (const [schluessel, kaestchen] of Object.entries(this.filter)) if (typeof gemerkt[schluessel] === 'boolean') kaestchen.checked = gemerkt[schluessel];
        if (typeof gemerkt.geist === 'boolean') this.geist.checked = gemerkt.geist;
        this.jobs = antwort.jobs;
        await this.job(this.jobId);
        Netzstufenstand.seiteFertig();      // die Figuren der Felder sind angestoßen: ab jetzt meldet jede selbst (Anzeige rechts unten)
    }

    fehler(fehler) {
        this.jobinfo.textContent = `Nicht geladen: ${fehler.message ?? fehler}`;
        this.jobinfo.classList.add('fehlertext');
    }

    async job(id) {
        const j = this.jobs.find(x => x.id === id);
        this.jobinfo.classList.remove('fehlertext');
        this.jobinfo.textContent = `${j.proben} Proben: ${j.training} Training, ${j.pruefung} Prüfposen · Status: ${j.status}`;
        this.daten = await Serverabruf.json(`/api/meshgenesis/${encodeURIComponent(id)}/proben/`);
        Meshgenesisanimationsdaten.verwerfen();
        this.zeilen.forEach(zeile => zeile.jobSetzen(this.daten));
        const z = this.daten.zusammenfassung;
        if (this.echt) {
            // Echte Daten (15.10.2026): Fehler des Laufs je Gruppe (`lauf_ergebnis.json`, Abstand der 138 Rig-Punkte zum Soll), und die Prüfposen getrennt von den zurückgehaltenen Spagat-Bildern.
            const zahl = g => this.daten.proben.filter(p => p.gruppe === g).length;
            this.jobinfo.textContent = `${this.daten.proben.length} Proben: ${zahl('training')} Training, nie trainiert ${zahl('pruefung')} Prüfposen und ${zahl('spagat')} Spagat-Bilder · Lauf ${this.daten.lauf.name}`;
            this.zusammenfassung.replaceChildren(this._kurz('Ø Fehler Training', z.training_mittel_mm), this._kurz('Ø Prüfposen', z.pruefung_mittel_mm), this._kurz('Ø Spagat-Bilder', z.spagat_mittel_mm));
        } else {
            this.zusammenfassung.replaceChildren(this._kurz('Ø Gelenkfehler Training', z.training_mittel_mm), this._kurz('Ø Gelenkfehler Prüfposen', z.pruefung_mittel_mm));
        }
        this.wahl.laden(this.daten.proben, Meshgenesisansichtgedaechtnis.stand.probe?.[this.jobId] ?? null);
    }

    /** Zeigt die Seite echte Daten (Datensatz + Vorhersagen eines Laufs) statt der Attrappe? */
    get echt() {
        return this.daten?.attrappe === false;
    }

    _kurz(titel, mm) {
        const feld = document.createElement('div');
        feld.append(`${titel}: `);
        const wert = document.createElement('b');
        wert.textContent = mm == null ? '—' : `${mm.toLocaleString('de-DE')} mm`;
        feld.append(wert);
        if (!this.echt) feld.append(' (Dummy)');
        return feld;
    }

    /** Was die Standardanimation bewegt: die Figur des Ergebnisses dieser Probe (Regler, Haut, Anatomie-Stück) und die Stücke aus der KI — vom Server wie das stille Bild (`Meshgenesisgenesisfigur`). */
    async _bewegungsquelle() {
        const probe = this.aktuell;
        if (!probe || !this.echt) return null;
        const weg = probe.weg ?? '';
        const daten = await Meshgenesisgenesisfigur._datenHolen(this.jobId, probe.id, weg);
        if (!daten?.figur_ergebnis) return null;
        const ki = daten.ki_kleider ? await Meshgenesiskikleiderfeld.laden(daten.ki_kleider) : null;
        return {
            schluessel: `${this.jobId}|${probe.id}|${weg}`, figur: daten.figur_ergebnis, stuecke: ki?.stuecke ?? [],
            knochen: daten.ki_kleider?.knochen ?? this.daten.rig?.knochen?.map(k => k.name), ruhezentren: daten.ki_kleider?.ruhezentren ?? null,
        };
    }

    zeigen(probe) {
        if (probe !== this.aktuell) this.bewegung?.verwerfen();
        this.aktuell = probe;
        if (probe) {
            Meshgenesisansichtgedaechtnis.merkenJeJob('probe', this.jobId, probe.id);
            // Der zuletzt gewählte Weg zum Rig dieses Jobs (17.10.2026) — hat die Probe ihn nicht, bleibt ihre Vorgabe.
            const weg = Meshgenesisansichtgedaechtnis.stand.weg?.[this.jobId];
            if (weg) Meshgenesiswegwahl.waehlen(probe, weg);
        }
        for (const zeile of this.zeilen) zeile.probe(this.daten, probe, this.geist.checked);
        this._texte(probe);
        if (this.echt && probe?.eingabe?.echt) {
            if (!probe.eingabeEcht) this._wolkeHolen(probe);
            if (!probe.flaeche && !probe.flaecheFehlt) this._flaecheHolen(probe);
            if (probe.apose && !probe.aposeDaten && !probe.aposeFehlt) this._aposeHolen(probe);
        }
    }

    /** Das Zwischenbild „Rig → A-Pose“ (17.10.2026, `Meshgenesisapose`, MannLaufen rund 8 MB) — nur für die Probe, auf der die Vorstufe lief. */
    async _aposeHolen(probe) {
        try {
            probe.aposeDaten = await Meshgenesisapose.holen(this.jobId, probe.id);
        } catch (fehler) {
            probe.aposeFehlt = fehler.message ?? String(fehler);
        }
        this._neuZeichnen(probe);
    }

    /** Die Punktwolke einer echten Probe nachholen (rund 160 KB, erst bei Wahl der Probe) und die Zeilen neu zeichnen — nur, wenn die Probe dann noch gewählt ist. */
    async _wolkeHolen(probe) {
        try {
            // Tripo-Job (21.10.2026, Edgar: „2 Mio punkte!“): erst die dichte Wolke (Binärpaket, `Meshgenesiseingabedicht`), ohne sie die 16.384 Punkte
            if (probe.start === 'wolke') probe.eingabeEcht = await this._dichteWolke(probe);
            probe.eingabeEcht ??= await Serverabruf.json(`/api/meshgenesis/${encodeURIComponent(this.jobId)}/eingabe/${probe.id}/`);
        } catch (fehler) {
            this.probeninfo.append(` · Punktwolke nicht geladen: ${fehler.message ?? fehler}`);
            return;
        }
        this._neuZeichnen(probe);
    }

    /** Paket: uint32 Anzahl · float32 Einheit · int16 Lage (n × 3) · uint8 Farbe (n × 3) · int8 Teil (n); null bei 404. */
    async _dichteWolke(probe) {
        const antwort = await fetch(`/api/meshgenesis/${encodeURIComponent(this.jobId)}/eingabe/${probe.id}/dicht/`);
        if (antwort.status === 404) return null;
        if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
        const puffer = await antwort.arrayBuffer();
        const kopf = new DataView(puffer, 0, 8);
        const n = kopf.getUint32(0, true), einheit = kopf.getFloat32(4, true);
        const q = new Int16Array(puffer, 8, n * 3);
        const lage = new Float32Array(n * 3);
        for (let i = 0; i < lage.length; i++) lage[i] = q[i] * einheit;
        return { dicht: true, anzahl: n, von: n, lage, rgb: new Uint8Array(puffer, 8 + n * 6, n * 3), etikett: new Int8Array(puffer, 8 + n * 9, n) };
    }

    /** Die gehäutete Figur der Probe (rund 2 MB, `Meshgenesisflaechen`) für die Ansichtsarten; fehlt sie (404), zeigt die Eingabe die Punktwolke und sagt es. */
    async _flaecheHolen(probe) {
        try {
            probe.flaeche = await Meshgenesisflaechen.holen(this.jobId, probe.id);
        } catch (fehler) {
            probe.flaecheFehlt = fehler.message ?? String(fehler);
        }
        this._neuZeichnen(probe);
    }

    _neuZeichnen(probe) {
        if (this.aktuell === probe) for (const zeile of this.zeilen) zeile.probe(this.daten, probe, this.geist.checked);
    }

    _texte(probe) {
        if (!probe) {
            this.probeninfo.textContent = '';
            this.kennzahlen.replaceChildren();
            return;
        }
        const k = probe.kennzahlen;
        const pruef = probe.aufteilung === 'pruefung';
        const art = probe.gruppe === 'spagat' ? 'Spagat-Bild (nie trainiert)' : pruef ? 'Prüfpose (nie trainiert)' : 'Training';
        const marke = document.createElement('span');
        marke.className = `meshgenesis-marke${pruef ? ' pruefung' : ''}`;
        marke.textContent = art;
        this.probeninfo.replaceChildren(`Probe ${probe.id}: `, Object.assign(document.createElement('b'), { textContent: probe.name }), marke);
        // Mehrere Wege zum Rig (Job UrsulaSpagat, 16.10.2026): Knöpfe hinter der Probe; ein Wechsel zeichnet Texte und alle Zeilen neu.
        const wege = Meshgenesiswegwahl.knoepfe(probe, () => {
            Meshgenesisansichtgedaechtnis.merkenJeJob('weg', this.jobId, probe.weg);
            this.bewegung?.verwerfen();          // die Ergebnisfigur hängt am Weg
            this._texte(probe);
            this._neuZeichnen(probe);
        });
        if (wege) this.probeninfo.append(wege);
        const de = n => n.toLocaleString('de-DE');
        if (this.echt) {
            const gruppen = Object.entries(k.je_gruppe_mm).map(([g, mm]) => [`Ø Fehler ${g}`, `${de(mm)} mm`]);
            const weg = Meshgenesiswegwahl.gewaehlt(probe);
            this.kennzahlen.replaceChildren(this._werte([
                ['Aufteilung', art],
                ['Quelle', probe.quelle],
                ...(weg ? [['Weg', weg.name]] : []),
                [`Ø Fehler (${de(probe.rig.kennzahlen.knochen)} Rig-Punkte)`, `${de(k.mittel_mm)} mm`],
                ['Größter Fehler', `${de(k.groesster_mm)} mm (${k.groesster_gelenk})`],
                [`Rig-Punkte unter ${de(k.schwelle_mm)} mm`, `${de(k.unter_schwelle_prozent)} %`],
                ...gruppen,
                ['Lauf', this.daten.lauf.name],
                ['Heutige Anpassung (Basislinie)', 'nicht gerechnet'],
            ]));
            return;
        }
        const teile = Object.entries(probe.teile ?? {}).map(([schluessel, t]) => [`Ø Fehler ${this.daten.teile[schluessel].titel}`, `${de(t.kennzahlen.mittel_mm)} mm`]);
        this.kennzahlen.replaceChildren(this._werte([
            ['Aufteilung', pruef ? 'Prüfpose' : 'Training'],
            ['Quelle', probe.quelle],
            ['Ø Gelenkfehler (ganzer Körper)', `${de(k.mittel_mm)} mm`],
            ['Größter Gelenkfehler', `${de(k.groesster_mm)} mm (${k.groesster_gelenk})`],
            [`Gelenke unter ${de(k.schwelle_mm)} mm`, `${de(k.unter_schwelle_prozent)} %`],
            ...(probe.rig ? [[`Ø Rig-Fehler (${de(probe.rig.kennzahlen.knochen)} Knochen)`, `${de(probe.rig.kennzahlen.mittel_mm)} mm`]] : []),
            ...teile,
            ['Punkte der Eingabe (ganzer Körper)', de(probe.eingabe.punkte)],
            ['Heutige Anpassung (Basislinie)', 'nicht gerechnet'],
        ]));
    }

    _werte(paare) {
        const raster = document.createElement('div');
        raster.className = 'meshgenesis-werte';
        for (const [titel, wert] of paare) {
            const feld = document.createElement('div');
            feld.className = 'meshgenesis-wert';
            feld.append(Object.assign(document.createElement('span'), { textContent: titel }), Object.assign(document.createElement('b'), { textContent: wert }));
            raster.append(feld);
        }
        return raster;
    }
}
