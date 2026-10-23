/**
 * Mesh3daifigurbewegungsleiste — die Leiste unter der Ergebnisfigur von Mesh3D-AI (22.10.2026): ⏮ ◀ ▶/⏸ ⏹ ▶ ⏭, Schieber, Zeit, Bild, darunter die Standardanimation (Kategorie, Datei) — wie die Leiste
 * der Mesh-3D-Jobseite (`mesh3d_auftrag.html`, `Engine2d3dKleideranimationsbedienung`, `Mesh3danimationswahlfeld`). Die Wahl liegt je Job bzw. Test auf dem Server (`data-adresse`,
 * `Mesh3daianimationswahl`, Vorgabe A_Results/DanceKurz).
 *
 * Jeder Befehl außer Stopp läuft durch `befehl`: der erste baut die Figur in der Ruhelage und holt die Bewegung (`Mesh3daifigurbewegung.vorbereiten`, einige Sekunden), Klicks in dieser Zeit fallen weg.
 * Tasten (Leertaste, ← →, Pos1, Ende) nur, wo die Seite sie nicht selbst braucht (`tasten`: Testseite ja; die Jobseite hat dafür Probenwahl und Spagat-Zeilen).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Mesh3daifigurbewegungsleiste {
    static TASTEN = {
        Space: b => b.umschalten(),
        ArrowLeft: b => b.bild(-1),
        ArrowRight: b => b.bild(1),
        Home: b => b.springen(false),
        End: b => b.springen(true),
    };

    constructor(element, bewegung, { tasten = false } = {}) {
        this.b = bewegung;
        const teil = name => element.querySelector(`[data-bewegung="${name}"]`);
        this.play = teil('play');
        this.schieber = teil('schieber');
        this.zeit = teil('zeit');
        this.bildfeld = teil('bild');
        this.meldung = teil('meldung');
        this.kategorie = teil('kategorie');
        this.datei = teil('datei');
        this.wahlmeldung = teil('wahlmeldung');
        this._belegt = false;
        this._ziehen = false;
        this._eintraege = new Map();
        this._zustand = null;
        bewegung.beiAenderung = () => this.anzeigen();
        const knopf = (name, tun) => teil(name)?.addEventListener('click', () => this.befehl(tun));
        knopf('anfang', b => b.springen(false));
        knopf('zurueck', b => b.bild(-1));
        knopf('play', b => b.umschalten());
        knopf('vor', b => b.bild(1));
        knopf('ende', b => b.springen(true));
        teil('stopp')?.addEventListener('click', () => this.b.stoppen());
        this.schieber.addEventListener('input', () => this.befehl(b => b.stellen((Number(this.schieber.value) / 1000) * b.dauer)));
        this.schieber.addEventListener('pointerdown', () => { this._ziehen = true; });
        window.addEventListener('pointerup', () => { this._ziehen = false; });
        this.kategorie.addEventListener('change', () => this._kategorieGewaehlt());
        this.datei.addEventListener('change', () => this._dateiGewaehlt());
        if (tasten) document.addEventListener('keydown', ereignis => this._taste(ereignis));
        this.anzeigen();
    }

    async befehl(tun) {
        if (this._belegt) return;
        this._belegt = true;
        try {
            if (await this.b.vorbereiten()) tun(this.b);
        } catch (fehler) {
            this.b.text = `Animation nicht möglich: ${fehler.message ?? fehler}`;
            console.error(fehler);
        } finally {
            this._belegt = false;
            this.anzeigen();
        }
    }

    _taste(ereignis) {
        const tun = Mesh3daifigurbewegungsleiste.TASTEN[ereignis.code];
        if (!tun || ereignis.ctrlKey || ereignis.metaKey || ereignis.altKey) return;
        const ziel = ereignis.target;
        const art = ziel?.tagName;
        const schieber = art === 'INPUT' && ziel.type === 'range';
        if (ziel && (ziel.isContentEditable || /^(TEXTAREA|SELECT|BUTTON)$/.test(art) || (art === 'INPUT' && !schieber))) return;
        if (schieber && ereignis.code !== 'Space') return;
        ereignis.preventDefault();
        this.befehl(tun);
    }

    // ------------------------------------------------------------------ Anzeige

    static _mmss(s) {
        if (!Number.isFinite(s)) return '0:00';
        return `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, '0')}`;
    }

    anzeigen() {
        const b = this.b;
        const icon = this.play?.querySelector('i');
        if (icon) icon.className = b.spielt ? 'fas fa-pause' : 'fas fa-play';
        const z = Mesh3daifigurbewegungsleiste._mmss;
        if (b.action && b.dauer) {
            const t = b.action.isScheduled() ? b.action.time : 0;
            if (!this._ziehen) this.schieber.value = String(Math.round((t / b.dauer) * 1000));
            this.zeit.textContent = `${z(t)} / ${z(b.dauer)}`;
            this.bildfeld.textContent = `Bild ${Math.min(b.bilder, Math.floor(t * b.fps + 1e-6) + 1)} / ${b.bilder}`;
        } else {
            this.schieber.value = '0';
            this.zeit.textContent = '0:00 / 0:00';
            this.bildfeld.textContent = 'Bild 0 / 0';
        }
        const name = (b.wahl || '').split('/')[1] || '';
        this.meldung.textContent = b.text || (this._belegt ? '' : b.aktiv
            ? `Bewegung „${name}“ auf der Figur${b.kleider.length ? ` mit ${b.kleider.length} Stücken aus der KI` : ''} — Stopp zeigt wieder die Haltung der KI.`
            : b.modell ? `Play spielt „${name}“ auf der Figur.` : 'Play baut die Figur in der Ruhelage und spielt die Standardanimation.');
        this.meldung.title = b.rahmenMm == null ? '' : `Ruhegelenke der Stücke gegen die gebaute Figur: ${b.rahmenMm.toFixed(2)} mm (starr ausgeglichen)`;
        this.nachAnzeige?.();
    }

    /** Für die Zeilen der Jobseite, die diese Bewegung mitbedienen (`Mesh3daianimationsleiste.figur`): läuft sie, wo steht sie, was steht in der Zeile. */
    zustand() {
        const b = this.b;
        const name = (b.wahl || '').split('/')[1] || 'Standardanimation';
        const t = b.action?.isScheduled() ? b.action.time : 0;
        return { spielt: b.spielt, anteil: b.dauer ? t / b.dauer : 0, text: b.text || `${name} auf der Ergebnisfigur · ${this.bildfeld.textContent}` };
    }

    // ------------------------------------------------------------------ Standardanimation

    /** Wahl und Kategorien holen, die Felder füllen, der Bewegung die Datei sagen. */
    async wahlLaden(adresse) {
        this.adresse = adresse;
        try {
            const a = await Serverabruf.json(adresse);
            const wahl = a.fehlt ? a.standardwahl : a.wahl;
            this.kategorie.replaceChildren(...(a.kategorien || []).map(k => new Option(`${k.name} (${k.anzahl})`, k.name)));
            this.kategorie.value = wahl.split('/')[0];
            await this._eintraegeLaden(this.kategorie.value);
            this.datei.value = wahl;
            this.kategorie.disabled = this.datei.disabled = false;
            this._zustand = a;
            this._wahltext(a);
            this.b.wahlSetzen(wahl);
            this.anzeigen();
        } catch (fehler) {
            this.wahlmeldung.textContent = `Standardanimation nicht lesbar: ${fehler.message}`;
        }
    }

    async _eintraegeLaden(kategorie) {
        if (!this._eintraege.has(kategorie)) {
            const daten = await Serverabruf.json(`/api/animationen/${encodeURIComponent(kategorie)}/?wertformat=pfad`);
            this._eintraege.set(kategorie, daten.animationen || []);
        }
        this.datei.replaceChildren(...this._eintraege.get(kategorie).map(e => new Option(e.label, e.value)));
    }

    async _kategorieGewaehlt() {
        this.datei.disabled = true;
        try {
            await this._eintraegeLaden(this.kategorie.value);
            this.wahlmeldung.textContent = 'Eine Animation dieser Kategorie wählen.';
        } catch (fehler) {
            this.wahlmeldung.textContent = `Animationen nicht lesbar: ${fehler.message}`;
        } finally {
            this.datei.disabled = false;
        }
    }

    async _dateiGewaehlt() {
        const wert = this.datei.value;
        if (!wert) return;
        this.kategorie.disabled = this.datei.disabled = true;
        try {
            const a = await Serverabruf.senden(this.adresse, { bvh: wert });
            this._zustand = a;
            this._wahltext(a);
            const aktiv = this.b.aktiv;
            const lief = this.b.wahlSetzen(a.fehlt ? a.standardwahl : a.wahl);
            // Lief die alte Bewegung, läuft die neue gleich an; stand sie, zeigt die Figur das erste Bild der neuen.
            if (lief) await this.befehl(b => b.umschalten());
            else if (aktiv) await this.befehl(b => b.stellen(0));
        } catch (fehler) {
            this.wahlmeldung.textContent = `Standardanimation nicht gespeichert: ${fehler.daten?.error || fehler.message}`;
            if (this._zustand) this.datei.value = this._zustand.wahl;
        } finally {
            this.kategorie.disabled = this.datei.disabled = false;
            this.anzeigen();
        }
    }

    _wahltext(a) {
        this.wahlmeldung.textContent = a.fehlt
            ? `„${a.wahl}“ gibt es nicht mehr in der Bibliothek — gespielt wird ${a.standardwahl}.`
            : (a.standard ? 'Vorgabe.' : `Gewählt für diese Seite (Vorgabe: ${a.standardwahl}).`);
    }
}
