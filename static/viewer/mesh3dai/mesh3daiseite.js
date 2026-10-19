/**
 * Mesh3daiseite — Einstieg der Seite EINES Jobs von „Mesh3D-AI“ (`/mesh-3D-AI/<job>/`, 14.10.2026; der Job steht als `data-job` am Block `#mesh3dai-job`, die Liste aller Jobs ist `mesh3dailiste.js`):
 * holt den Kurzstand (`/api/mesh3dai/jobs/`) und die Proben des Jobs, baut die Zeilen (ganzer Körper, Gesicht, Hände/Füße, Kleider; je Zeile
 * Eingabe · gewünschte Ausgabe · Ausgabe des Netzes), die Probenwahl und die Kennzahlen. Heute liefert der Server Dummies für „Ursula1“ (`attrappe: true`); die Seite zeigt es deutlich an und rechnet selbst nichts.
 */
import { Genesis9aufbau } from '../gemeinsam/genesis9aufbau.js';
import { Netzstufenschalter } from '../gemeinsam/netzstufenschalter.js';
import { Netzstufenstand } from '../gemeinsam/netzstufenstand.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3daianimationsdaten } from './mesh3daianimationsdaten.js';
import { Mesh3daianimationsleiste } from './mesh3daianimationsleiste.js';
import { Mesh3daiansichtgedaechtnis } from './mesh3daiansichtgedaechtnis.js';
import { Mesh3daiapose } from './mesh3daiapose.js';
import { Mesh3daiflaechen } from './mesh3daiflaechen.js';
import { Mesh3daiflaechennetz } from './mesh3daiflaechennetz.js';
import { Mesh3daigenesisfigur } from './mesh3daigenesisfigur.js';
import { Mesh3daiprobenwahl } from './mesh3daiprobenwahl.js';
import { Mesh3daistand } from './mesh3daistand.js';
import { Mesh3daiwegwahl } from './mesh3daiwegwahl.js';
import { Mesh3daizeichenflaeche } from './mesh3daizeichenflaeche.js';
import { Mesh3daizeile } from './mesh3daizeile.js';

export class Mesh3daiseite {
    static aufbauen() {
        const seite = new Mesh3daiseite();
        seite.starten().catch(fehler => seite.fehler(fehler));
        return seite;
    }

    constructor() {
        const hole = id => document.getElementById(id);
        Mesh3daizeichenflaeche.renderer();          // vor der ersten Figur: der Renderer meldet sich beim `Texturweg` (Weg C prüft S3TC, bevor eine Adresse entsteht)
        this.jobId = hole('mesh3dai-job').dataset.job;
        this.jobinfo = hole('mesh3dai-jobinfo');
        this.zusammenfassung = hole('mesh3dai-zusammenfassung');
        this.probeninfo = hole('mesh3dai-probeninfo');
        this.geist = hole('mesh3dai-geist');
        this.kennzahlen = hole('mesh3dai-kennzahlentext');
        this.zeilen = [...document.querySelectorAll('.mesh3dai-zeile')].map(el => new Mesh3daizeile(el));
        // Die Felder zeichnen nur auf Anforderung: ein Bild der Figur, das nach dem ersten Zeichnen kommt, muss sie neu zeichnen lassen.
        Mesh3daiflaechennetz.nachLaden = () => this.zeilen.forEach(zeile => zeile.ansichten.forEach(a => a.zeichnen()));
        // Genesis-Figuren in Ziel und Ergebnis (`Mesh3daigenesisfigur`): fertig gebaut oder neue Netzstufe → die Felder hängen sie neu ein. Strg+Alt+H schaltet die Stufe wie in Charakter;
        // die Seite beginnt mit „grob“ (`<meta name="schnellanzeige">`) und lädt dabei nie neu.
        Mesh3daigenesisfigur.neuZeichnen = () => this.zeilen.forEach(zeile => zeile.ansichten.forEach(a => (a.art === 'soll' || a.art === 'ausgabe') && a.neuZeigen()));
        Mesh3daigenesisfigur.nurZeichnen = () => this.zeilen.forEach(zeile => zeile.ansichten.forEach(a => (a.art === 'soll' || a.art === 'ausgabe') && a.zeichnen()));
        Netzstufenschalter.einrichten(window, async ziel => (await Genesis9aufbau.stufeSetzen(Mesh3daigenesisfigur.modelle(), ziel), Mesh3daigenesisfigur.neuZeichnen(), true));
        this.wahl = new Mesh3daiprobenwahl({
            chips: hole('mesh3dai-chips'), zurueck: hole('mesh3dai-zurueck'), weiter: hole('mesh3dai-weiter'), zaehler: hole('mesh3dai-zaehler'),
            nurPruefung: hole('mesh3dai-nurpruefung'), schlechtZuerst: hole('mesh3dai-schlechtzuerst'),
        }, probe => this.zeigen(probe));
        this.daten = null;
        this.filter = { nurPruefung: hole('mesh3dai-nurpruefung'), schlechtZuerst: hole('mesh3dai-schlechtzuerst') };
        this.geist.addEventListener('change', () => {
            Mesh3daiansichtgedaechtnis.merken({ geist: this.geist.checked });
            this.zeilen.forEach(zeile => zeile.geistSetzen(this.geist.checked));
        });
        for (const [schluessel, kaestchen] of Object.entries(this.filter)) kaestchen.addEventListener('change', () => Mesh3daiansichtgedaechtnis.merken({ [schluessel]: kaestchen.checked }));
        document.addEventListener('keydown', Mesh3daianimationsleiste.leertaste);
        this._festhalten(hole('mesh3dai-oben'));
        // Die einzige ECHTE Karte der Seite: Datensatz und Training von der Platte, im Takt der Einstellung (Einstellungen → Mesh3D-AI).
        this.stand = Mesh3daistand.aufbauen(this.jobId, hole('mesh3dai-stand'));
    }

    /**
     * Der Block oben bleibt beim Blättern stehen (CSS `position: sticky`); die Köpfe der Zeilen hängen darunter. Dafür müssen Höhe der Kopfleiste der Seite (`.topbar`, ebenfalls sticky) und Höhe des Blocks bekannt sein —
     * beide ändern sich (Fensterbreite, Zahl der Zeilen mit Kästchen), darum als CSS-Werte, die ein `ResizeObserver` nachführt.
     */
    _festhalten(oben) {
        const leiste = document.querySelector('.topbar');
        const wurzel = document.documentElement.style;
        const messen = () => {
            wurzel.setProperty('--mesh3dai-leiste', `${leiste ? Math.round(leiste.getBoundingClientRect().height) : 0}px`);
            wurzel.setProperty('--mesh3dai-oben', `${Math.round(oben.getBoundingClientRect().height)}px`);
        };
        const beobachter = new ResizeObserver(messen);
        beobachter.observe(oben);
        if (leiste) beobachter.observe(leiste);
        messen();
    }

    async starten() {
        // Die gemerkte Ansicht (Textur, Rig …) kommt mit, bevor die erste Probe gezeichnet wird (16.10.2026).
        const [antwort, gemerkt] = await Promise.all([Serverabruf.json('/api/mesh3dai/jobs/'), Mesh3daiansichtgedaechtnis.laden()]);
        Mesh3daizeile.gemerktSetzen(gemerkt);
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
        this.daten = await Serverabruf.json(`/api/mesh3dai/${encodeURIComponent(id)}/proben/`);
        Mesh3daianimationsdaten.verwerfen();
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
        this.wahl.laden(this.daten.proben, Mesh3daiansichtgedaechtnis.stand.probe?.[this.jobId] ?? null);
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

    zeigen(probe) {
        this.aktuell = probe;
        if (probe) {
            Mesh3daiansichtgedaechtnis.merkenJeJob('probe', this.jobId, probe.id);
            // Der zuletzt gewählte Weg zum Rig dieses Jobs (17.10.2026) — hat die Probe ihn nicht, bleibt ihre Vorgabe.
            const weg = Mesh3daiansichtgedaechtnis.stand.weg?.[this.jobId];
            if (weg) Mesh3daiwegwahl.waehlen(probe, weg);
        }
        for (const zeile of this.zeilen) zeile.probe(this.daten, probe, this.geist.checked);
        this._texte(probe);
        if (this.echt && probe?.eingabe?.echt) {
            if (!probe.eingabeEcht) this._wolkeHolen(probe);
            if (!probe.flaeche && !probe.flaecheFehlt) this._flaecheHolen(probe);
            if (probe.apose && !probe.aposeDaten && !probe.aposeFehlt) this._aposeHolen(probe);
        }
    }

    /** Das Zwischenbild „Rig → A-Pose“ (17.10.2026, `Mesh3daiapose`, MannLaufen rund 8 MB) — nur für die Probe, auf der die Vorstufe lief. */
    async _aposeHolen(probe) {
        try {
            probe.aposeDaten = await Mesh3daiapose.holen(this.jobId, probe.id);
        } catch (fehler) {
            probe.aposeFehlt = fehler.message ?? String(fehler);
        }
        this._neuZeichnen(probe);
    }

    /** Die Punktwolke einer echten Probe nachholen (rund 160 KB, erst bei Wahl der Probe) und die Zeilen neu zeichnen — nur, wenn die Probe dann noch gewählt ist. */
    async _wolkeHolen(probe) {
        try {
            probe.eingabeEcht = await Serverabruf.json(`/api/mesh3dai/${encodeURIComponent(this.jobId)}/eingabe/${probe.id}/`);
        } catch (fehler) {
            this.probeninfo.append(` · Punktwolke nicht geladen: ${fehler.message ?? fehler}`);
            return;
        }
        this._neuZeichnen(probe);
    }

    /** Die gehäutete Figur der Probe (rund 2 MB, `Mesh3daiflaechen`) für die Ansichtsarten; fehlt sie (404), zeigt die Eingabe die Punktwolke und sagt es. */
    async _flaecheHolen(probe) {
        try {
            probe.flaeche = await Mesh3daiflaechen.holen(this.jobId, probe.id);
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
        marke.className = `mesh3dai-marke${pruef ? ' pruefung' : ''}`;
        marke.textContent = art;
        this.probeninfo.replaceChildren(`Probe ${probe.id}: `, Object.assign(document.createElement('b'), { textContent: probe.name }), marke);
        // Mehrere Wege zum Rig (Job UrsulaSpagat, 16.10.2026): Knöpfe hinter der Probe; ein Wechsel zeichnet Texte und alle Zeilen neu.
        const wege = Mesh3daiwegwahl.knoepfe(probe, () => {
            Mesh3daiansichtgedaechtnis.merkenJeJob('weg', this.jobId, probe.weg);
            this._texte(probe);
            this._neuZeichnen(probe);
        });
        if (wege) this.probeninfo.append(wege);
        const de = n => n.toLocaleString('de-DE');
        if (this.echt) {
            const gruppen = Object.entries(k.je_gruppe_mm).map(([g, mm]) => [`Ø Fehler ${g}`, `${de(mm)} mm`]);
            const weg = Mesh3daiwegwahl.gewaehlt(probe);
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
        raster.className = 'mesh3dai-werte';
        for (const [titel, wert] of paare) {
            const feld = document.createElement('div');
            feld.className = 'mesh3dai-wert';
            feld.append(Object.assign(document.createElement('span'), { textContent: titel }), Object.assign(document.createElement('b'), { textContent: wert }));
            raster.append(feld);
        }
        return raster;
    }
}
