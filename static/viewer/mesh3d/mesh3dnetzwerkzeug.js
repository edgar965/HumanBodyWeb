import * as THREE from 'three';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3dnetzfarbwahl } from './mesh3dnetzfarbwahl.js';
import { Mesh3dnetzhover } from './mesh3dnetzhover.js';
import { Mesh3dnetzspeichern } from './mesh3dnetzspeichern.js';
import { Mesh3dnetztasten } from './mesh3dnetztasten.js';
import { Mesh3dnetzteileliste } from './mesh3dnetzteileliste.js';
import { Mesh3dnetzwahl } from './mesh3dnetzwahl.js';

/**
 * Mesh3dnetzwerkzeug — „Netz bearbeiten“ in der Karte „Mesh-Ansicht“ der Jobseite „Mesh-3D“ (13.10.2026, Konzept `Docu/konzepte/2026-10-13_mesh-3d-netz-ausschneiden-konzept.md`).
 *
 * Edgar: „ich möchte diesen störenden zusammenhängenden zweiten Unterarm vor dem Arm der Ballerina ausschneiden, das Mesh speichern, und dann das 3D Modell neu rechnen“. Die Leiste über der Ansicht:
 * Bereich per Hover (14.10.2026, die Vorgabe: der Bereich ähnlicher Farbe unter dem Zeiger leuchtet, Regler „Granularität“, Klick wählt ihn) · Teil wählen (Klick auf das Netz wählt den ganzen zusammenhängenden Teil) · Rahmen (Rechteck aufziehen) ·
 * Farbe (alles Gleichfarbige im Umkreis um den Klick) · Umkehren · Aufheben · Entfernen · Zurück (Strg+Z) · Wiederholen (Strg+Y, `Mesh3dnetztasten`) · Speichern · Speichern, übernehmen und rechnen · Schnitt zurücknehmen
 * (14.10.2026: macht einen schon gespeicherten und übernommenen Schnitt rückgängig, `Mesh3dnetzspeichern.zuruecknehmen`). Die älteren Werkzeuge bleiben, wie sie waren.
 * Die Auswahl und die Anzeige liegen in `Mesh3dnetzwahl`, das Leuchten unter dem Zeiger in `Mesh3dnetzhover`, die Teileliste in `Mesh3dnetzteileliste`; hier sind Maus, Tasten, die Zahlen vom Server und die Aufrufe, die schreiben.
 *
 * Der Browser schickt nur ORTE (`schritte` der Auswahl, `schnitte` = die entfernten Auswahlen); der Server (`Mesh3dnetzschnitt`) übersetzt sie auf dem ORIGINAL und schreibt eine neue GLB mit unveränderter Textur
 * neben die Quelle — die Quelle selbst bleibt unberührt, bis „Als Quelle übernehmen“ (oder „… und rechnen“) sie ersetzt. Die Zahlen unter der Leiste sind die des Servers; die Ansicht rechnet auf ihrer (vielleicht
 * vereinfachten) Kopie und weicht höchstens um deren Vereinfachung ab — ab 1,5 Prozentpunkten steht eine Warnung da.
 */
export class Mesh3dnetzwerkzeug {
    static KLICK_PX = 5;
    static PAUSE_MS = 250;
    static ABWEICHUNG = 0.015;
    static HILFE = 'Teil wählen: Klick auf das Netz wählt den ganzen zusammenhängenden Teil (Umschalt+Klick nimmt ihn weg) · Rahmen: Rechteck aufziehen · Entfernen nimmt die Auswahl aus der Ansicht, Speichern schreibt die Datei.';
    static HILFE_FARBE = 'Farbe im Umkreis: Klick wählt alles, was im eingestellten Umkreis um den Klick liegt und höchstens um den eingestellten Farbabstand (ΔE) von der Farbe unter dem Klick abweicht — auch wenn es nicht am Körper hängt (Umschalt+Klick nimmt weg).';
    static HILFE_HOVER = 'Bereich per Hover: Fahren Sie über das Netz — der Bereich ähnlicher Farbe unter dem Zeiger leuchtet orange. „Granularität“ (Farbabstand ΔE) macht ihn enger oder weiter, „Umkreis“ begrenzt ihn räumlich. Klick wählt den Bereich (Umschalt+Klick nimmt ihn weg), Ziehen dreht weiter.';

    constructor(buehne, seite) {
        this.buehne = buehne;
        this.seite = seite;
        this.feld = document.getElementById('netz-werkzeug');
        if (!this.feld) return;
        const el = id => document.getElementById(id);
        this.meldung = el('netz-wz-meldung');
        this.teile = el('netz-wz-teile');
        this.ergebnis = el('netz-wz-ergebnis');
        this.knoepfe = Object.fromEntries(['hover', 'teil', 'rahmen', 'farbe', 'umkehren', 'aufheben', 'entfernen', 'zurueck', 'wiederholen', 'speichern', 'rechnen', 'rueckgaengig', 'schnittwieder'].map(n => [n, el(`netz-wz-${n}`)]));
        this.hoverInfo = el('netz-wz-hover-info');
        this.farbwahl = new Mesh3dnetzfarbwahl();
        this.farbwahl.bei(() => this.hover?.neu());
        this.wahl = null;
        this.hover = null;
        this.modus = 'hover';
        this.server = null;
        this.serverEntfernt = null;
        this._start = null;
        this._lauf = 0;
        this._zeit = null;
        this._arbeitet = false;
        const w = () => this.wahl;
        this.knoepfe.hover.addEventListener('click', () => this._umschalten('hover'));
        this.knoepfe.teil.addEventListener('click', () => this._umschalten('teil'));
        this.knoepfe.rahmen.addEventListener('click', () => this._umschalten('rahmen'));
        this.knoepfe.farbe.addEventListener('click', () => this._umschalten('farbe'));
        this.knoepfe.umkehren.addEventListener('click', () => w()?.umkehren());
        this.knoepfe.aufheben.addEventListener('click', () => w()?.aufheben());
        this.knoepfe.entfernen.addEventListener('click', () => w()?.entfernen());
        this.knoepfe.zurueck.addEventListener('click', () => w()?.zurueck());
        this.knoepfe.wiederholen.addEventListener('click', () => w()?.wiederholen());
        this.knoepfe.speichern.addEventListener('click', () => this._speichern(false));
        this.knoepfe.rechnen.addEventListener('click', () => this._speichern(true));
        this.knoepfe.rueckgaengig.addEventListener('click', () => this._gespeichertesZurueck());
        this.knoepfe.schnittwieder.addEventListener('click', () => this._gespeichertesWieder());
        document.addEventListener('keydown', e => { if (Mesh3dnetztasten.seite(e, this.wahl, this.feld)) e.preventDefault(); });
        this.speicher = new Mesh3dnetzspeichern(seite, this.ergebnis, text => this._melden(text), (ja, text) => this._arbeiten(ja, text));
        this._maus();
    }

    // ------------------------------------------------------------------ Netz kommt und geht

    /** Die Ansicht hat ein Netz geladen: Auswahl anlegen, wenn die Datei genau ein Netz enthält. */
    netzGeladen() {
        if (!this.feld) return;
        this.netzWeg();
        const wurzel = this.buehne.netze.gruppe?.children[0]?.children[0];
        const netze = [];
        wurzel?.traverse(o => { if (o.isMesh) netze.push(o); });
        this.feld.hidden = false;
        this.speicher.gemerktes();
        if (netze.length !== 1) {
            this._melden(netze.length ? `Die Datei enthält ${netze.length} Netze — Ausschneiden geht nur bei einem Netz.` : 'Kein Netz geladen.');
            this._knoepfe();
            return;
        }
        this.wahl = new Mesh3dnetzwahl(netze[0], wurzel, () => this._geaendert());
        this.hover = new Mesh3dnetzhover(this.wahl, this.buehne, this.farbwahl, text => this._hoverText(text));
        this.server = this.serverEntfernt = null;
        this._modusAnwenden();
        this._geaendert();
    }

    /** Das Netz wird ersetzt oder entfernt: die Auswahl samt Anzeige freigeben. */
    netzWeg() {
        this.hover?.freigeben();
        this.hover = null;
        this.wahl?.freigeben();
        this.wahl = null;
        if (this.feld) { this._knoepfe(); this.teile.replaceChildren(); this._melden(''); }
    }

    // ------------------------------------------------------------------ Maus und Tasten

    /** Ein Knopf der Betriebsart: der gedrückte schaltet sie ein, ein zweiter Druck schaltet auf Drehen zurück. */
    _umschalten(art) {
        this.modus = this.modus === art ? null : art;
        this._modusAnwenden();
    }

    _modusAnwenden() {
        for (const art of ['hover', 'teil', 'rahmen', 'farbe']) {
            this.knoepfe[art].classList.toggle('active', this.modus === art);
            this.buehne.feld.classList.toggle(`wz-${art}`, this.modus === art);
        }
        this.buehne.steuerung.enabled = this.modus !== 'rahmen';
        this.hover?.aktiv(this.modus === 'hover');
        this._hoverText('');
        this._melden({ hover: Mesh3dnetzwerkzeug.HILFE_HOVER, farbe: Mesh3dnetzwerkzeug.HILFE_FARBE }[this.modus] ?? (this.modus ? Mesh3dnetzwerkzeug.HILFE : ''));
    }

    _maus() {
        const c = this.buehne.canvas;
        c.tabIndex = 0;
        c.style.outline = 'none';
        c.addEventListener('pointerdown', e => this._runter(e));
        c.addEventListener('pointermove', e => this._bewegt(e));
        c.addEventListener('pointerup', e => this._hoch(e));
        c.addEventListener('pointerleave', () => this.hover?.weg());
        c.addEventListener('keydown', e => this._taste(e));
    }

    /** Der Text zum Bereich unter dem Zeiger, neben dem Regler „Granularität“. */
    _hoverText(text) {
        if (this.hoverInfo) this.hoverInfo.textContent = text;
    }

    _ndc(x, y) {
        const r = this.buehne.canvas.getBoundingClientRect();
        return new THREE.Vector2(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1);
    }

    _runter(e) {
        if (!this.wahl || !this.modus || e.button !== 0) return;
        this._start = { x: e.clientX, y: e.clientY, umschalt: e.shiftKey };
        if (this.modus === 'hover') this.hover?.weg();                          // beim Drehen leuchtet nichts (und es kostet nichts)
        if (this.modus === 'rahmen') {
            this.buehne.canvas.setPointerCapture(e.pointerId);
            this._rahmenFeld = document.createElement('div');
            this._rahmenFeld.className = 'mesh3d-rahmen';
            this.buehne.feld.appendChild(this._rahmenFeld);
            this._bewegt(e);
        }
    }

    _bewegt(e) {
        if (this.modus === 'hover' && !this._start && e.buttons === 0) this.hover?.bewegt(this._ndc(e.clientX, e.clientY), e.clientX, e.clientY);
        if (!this._start || !this._rahmenFeld) return;
        const r = this.buehne.feld.getBoundingClientRect();
        const s = this._start;
        Object.assign(this._rahmenFeld.style, { left: `${Math.min(s.x, e.clientX) - r.left}px`, top: `${Math.min(s.y, e.clientY) - r.top}px`,
            width: `${Math.abs(e.clientX - s.x)}px`, height: `${Math.abs(e.clientY - s.y)}px` });
    }

    _hoch(e) {
        const s = this._start;
        this._start = null;
        this._rahmenFeld?.remove();
        this._rahmenFeld = null;
        if (!s || !this.wahl) return;
        const dx = e.clientX - s.x, dy = e.clientY - s.y;
        if (['hover', 'teil', 'farbe'].includes(this.modus) && Math.hypot(dx, dy) <= Mesh3dnetzwerkzeug.KLICK_PX) {
            const t = this.wahl.treffer(this._ndc(e.clientX, e.clientY), this.buehne.kamera);
            if (!t) this._melden('Dort ist kein Netz (entfernte Flächen zählen nicht).');
            else if (this.modus === 'teil') this.wahl.insel(t.flaeche, t.punkt, !s.umschalt);
            else if (!this.wahl.farbe(t.flaeche, t.punkt, this.farbwahl.radiusSzene(this.wahl.wurzel), this.farbwahl.farbabstand(), !s.umschalt)) {
                this._melden('Dieses Netz hat keine lesbare Farbtextur — „Farbe im Umkreis“ und der Bereich per Hover gehen hier nicht.');
            }
        } else if (this.modus === 'rahmen' && Math.abs(dx) > Mesh3dnetzwerkzeug.KLICK_PX && Math.abs(dy) > Mesh3dnetzwerkzeug.KLICK_PX) {
            this.wahl.rahmen(this._ebenen(this._ndc(s.x, s.y), this._ndc(e.clientX, e.clientY)), !s.umschalt);
        }
    }

    _taste(e) {
        if (!this.wahl) return;
        if (e.key === 'Escape') this.wahl.aufheben();
        else if (e.key === 'Delete') this.wahl.entfernen();
        else if (!Mesh3dnetztasten.rueckgaengig(e, this.wahl)) return;
        e.preventDefault();
    }

    /** Die vier Seitenebenen des Sichtprismas durch das Rechteck (Koordinaten der Szene der Datei; innen = `distanceToPoint ≥ 0`). */
    _ebenen(a, b) {
        const kamera = this.buehne.kamera;
        kamera.updateMatrixWorld();
        const c = kamera.getWorldPosition(new THREE.Vector3());
        const richtung = (x, y) => new THREE.Vector3(x, y, 0.5).unproject(kamera).sub(c).normalize();
        const [x0, x1, y0, y1] = [Math.min(a.x, b.x), Math.max(a.x, b.x), Math.min(a.y, b.y), Math.max(a.y, b.y)];
        const ecken = [richtung(x0, y1), richtung(x1, y1), richtung(x1, y0), richtung(x0, y0)];
        const innen = c.clone().add(richtung((x0 + x1) / 2, (y0 + y1) / 2));
        this.wahl.wurzel.updateWorldMatrix(true, false);
        const zurueck = this.wahl.wurzel.matrixWorld.clone().invert();
        return ecken.map((d, i) => {
            const ebene = new THREE.Plane().setFromCoplanarPoints(c, c.clone().add(d), c.clone().add(ecken[(i + 1) % 4]));
            if (ebene.distanceToPoint(innen) < 0) ebene.negate();
            return ebene.applyMatrix4(zurueck);
        });
    }

    // ------------------------------------------------------------------ Anzeige

    _geaendert() {
        this.buehne.takt.wach();
        this.hover?.neu();                                                      // entfernte Flächen leuchten nicht mehr
        Mesh3dnetzteileliste.zeichnen(this.teile, this.wahl, (nr, plus) => this.wahl.inselNr(nr, plus));
        this._knoepfe();
        window.clearTimeout(this._zeit);
        this._zeit = window.setTimeout(() => this._vorschau(), Mesh3dnetzwerkzeug.PAUSE_MS);
        this._text();
    }

    _knoepfe() {
        const w = this.wahl, offen = !!w?.schritte.length;
        const sperre = { umkehren: !w, aufheben: !offen, entfernen: !w?.nAuswahl, zurueck: !w?.historie.length, wiederholen: !w?.zukunft.length, hover: !w, teil: !w, rahmen: !w, farbe: !w,
            speichern: !w?.schnitte.length || offen || this._arbeitet, rechnen: !w?.schnitte.length || offen || this._arbeitet,
            rueckgaengig: !w || this._arbeitet || !this._quelleBearbeitet(), schnittwieder: !w || this._arbeitet || !this.seite.zustand?.quelle?.nachschnitt };
        for (const [name, knopf] of Object.entries(this.knoepfe)) knopf.disabled = !!sperre[name];
        this.knoepfe.speichern.title = offen ? 'Die Auswahl ist noch nicht entfernt — erst „Entfernen“ oder „Aufheben“.' : 'Das Netz ohne die entfernten Flächen als neue GLB-Datei speichern. Die Quelle des Auftrags bleibt, wie sie ist.';
    }

    /** Die Zahlen des Servers zur Auswahl und zu den entfernten Flächen (Original, nicht die Kopie der Ansicht). */
    async _vorschau() {
        const lauf = ++this._lauf, w = this.wahl;
        if (!w) return;
        const frage = async schnitte => (schnitte.length ? Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/netzauswahl/`, { schnitte }).catch(f => ({ fehler: f.message })) : null);
        const [auswahl, entfernt] = await Promise.all([frage(w.schritte.length ? [w.schritte] : []), frage(w.schnitte)]);
        if (lauf !== this._lauf) return;
        this.server = auswahl;
        this.serverEntfernt = entfernt;
        this._text();
    }

    _text() {
        const w = this.wahl;
        if (!w) return;
        const z = Mesh3dnetzteileliste.zahl;
        const teile = [];
        if (w.nAuswahl) teile.push(this._zahlen('Auswahl', w.nAuswahl / w.flaechen, this.server));
        if (w.nEntfernt) teile.push(this._zahlen('Entfernt', w.nEntfernt / w.flaechen, this.serverEntfernt));
        if (!teile.length) teile.push(`Netz: ${z(w.flaechen)} Flächen in der Ansicht, ${w.zerlegung.groessen.length} zusammenhängende Teile.`);
        this._melden(teile.join(' · '));
    }

    /** „Auswahl: 5.758 von 51.096 Flächen (11,3 %)“ nach dem Server; bis er antwortet (oder fehlt) der Anteil der Ansicht. */
    _zahlen(name, anteil, server) {
        const z = Mesh3dnetzteileliste.zahl, p = Mesh3dnetzteileliste.prozent;
        if (!server) return `${name}: ca. ${p(anteil)} (Ansicht; der Server rechnet …)`;
        if (server.fehler) return `${name}: ${p(anteil)} (Ansicht) — Server: ${server.fehler}`;
        const n = name === 'Auswahl' ? server.schnitte[0].flaechen : server.entfernt;
        const abweichung = Math.abs(n / server.flaechen - anteil) > Mesh3dnetzwerkzeug.ABWEICHUNG ? ` — Achtung: die Ansicht zeigt ${p(anteil)}` : '';
        return `${name}: ${z(n)} von ${z(server.flaechen)} Flächen (${p(n / server.flaechen)})${abweichung}`;
    }

    _melden(text) { this.meldung.textContent = text; }

    // ------------------------------------------------------------------ Schreiben (`Mesh3dnetzspeichern`)

    /** Ist die Quelle des Auftrags eine mit „Netz bearbeiten“ gespeicherte Datei (`…_bearbeitet_<Zeit>.glb`)? Nur dann gibt es einen gespeicherten Schnitt zurückzunehmen. */
    _quelleBearbeitet() {
        return /_bearbeitet_[0-9.]+\.glb$/i.test(this.seite.zustand?.quelle?.datei || '');
    }

    _gespeichertesZurueck() {
        if (!this.wahl || this._arbeitet) return Promise.resolve();
        return this.speicher.zuruecknehmen(this.wahl);
    }

    /** Den zurückgenommenen Schnitt wiederholen: `zustand.quelle.nachschnitt` nennt die Datei, die aus der jetzigen Quelle entstand (der Server findet sie über die Begleitdateien). */
    _gespeichertesWieder() {
        if (!this.wahl || this._arbeitet) return Promise.resolve();
        return this.speicher.wiederholen(this.wahl);
    }

    _speichern(uebernehmen) {
        const w = this.wahl;
        if (!w || !w.schnitte.length || w.schritte.length || this._arbeitet) return Promise.resolve();
        return this.speicher.speichern(w, uebernehmen);
    }

    _arbeiten(ja, text = '') {
        this._arbeitet = ja;
        this._knoepfe();
        if (text) this._melden(text);
        else if (!ja && this.wahl) this._text();
    }
}
