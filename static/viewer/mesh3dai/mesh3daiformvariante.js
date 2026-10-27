/**
 * Mesh3daiformvariante — die Seite EINER Formvariante im Formtraining (18.10.2026 abends, Edgar: „mach das: Formvariante als Jobseite“).
 * Drei gekoppelte Felder (`Mesh3daiansicht`): Start = die A-Pose-Wolke, die der Lauf gelesen hat · Ziel = Genesis-Körper aus den Soll-Reglern · Ergebnis = Genesis-Körper aus den vorhergesagten
 * Reglern dieser Probe oder ihrem Mittel über alle Proben (so misst die echte Nachrechnung des Laufs). Server: `core/api/mesh3daiformvariante.py`; Figuren baut `Mesh3daiformvariantezeichner`.
 * Ein anderer Lauf lädt die Seite neu (`?lauf=`); Probe, Wolke, Ergebnis und Ansicht schalten ohne Neuladen, jede Figur und Wolke wird einmal geholt.
 */
import { Mesh3daiansicht } from './mesh3daiansicht.js';
import { GRUPPE, Mesh3daiformvariantetabellen as T } from './mesh3daiformvariantetabellen.js';
import { Mesh3daiformvariantezeichner as Z } from './mesh3daiformvariantezeichner.js';
import { Mesh3dailinien } from './mesh3dailinien.js';

const de = (n, s = 0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });
const KAMERA = { position: [1.7, 1.5, 3.4], ziel: [0, 0.95, 0], boden: true };
const GESCHLECHT = { weiblich: 'weiblich', maennlich: 'männlich' };

export class Mesh3daiformvariante {
    static async starten(wurzel) {
        const seite = new Mesh3daiformvariante(wurzel);
        window.__mesh3daiformvariante = seite;
        await seite.laden();
        return seite;
    }

    constructor(wurzel) {
        this.wurzel = wurzel;
        this.figurName = wurzel.dataset.figur;
        this.basis = `/api/mesh3dai/formvariante/${encodeURIComponent(this.figurName)}`;
        this.laufParam = wurzel.dataset.lauf ? `?lauf=${encodeURIComponent(wurzel.dataset.lauf)}` : '';
        this.daten = null;
        this.koerper = null;
        this.ziel = null;
        this.ergebnis = null;
        this.wolke = null;
        this.fehler = {};
        this.figuren = new Map();
        this.wolken = new Map();
        this.probe = null;
        this.k = 0;
        this.ergebnisArt = 'probe';
        this.ansicht = 'textur';
        this._auftrag = 0;
        const zeichner = { zeichnen: (inhalt, art) => this._zeichnen(inhalt, art) };
        this.ansichten = ['eingabe', 'soll', 'ausgabe'].map(art => new Mesh3daiansicht(wurzel.querySelector(`.mesh3dai-leinwand[data-art="${art}"]`), art, zeichner, KAMERA));
        const linien = document.getElementById('mesh3dai-linien');
        this.linien = linien ? new Mesh3dailinien(linien, this.basis, this.laufParam, KAMERA) : null;
        Mesh3daiansicht.koppeln([...this.ansichten, ...(this.linien?.ansichten ?? [])]);
        Z.nachLaden = () => this.zeigen();
        wurzel.querySelector('[data-wahl="lauf"]').addEventListener('change', e => {
            const adresse = new URL(window.location.href);
            adresse.searchParams.set('lauf', e.target.value);
            window.location.href = adresse.toString();
        });
        this.probenwahl = wurzel.querySelector('[data-wahl="probe"]');
        this.probenwahl.addEventListener('change', () => {
            this.probe = this.daten.proben.find(p => String(p.nr) === this.probenwahl.value) ?? null;
            this.k = this.probe?.wolken.includes(this.k) ? this.k : (this.probe?.wolken[0] ?? 0);
            this._wolkenknoepfe();
            this._probeLaden();
        });
        this.wolkenleiste = wurzel.querySelector('[data-wahl="wolke"]');
        this.wolkenleiste.addEventListener('click', e => {
            const knopf = e.target.closest('[data-k]');
            if (!knopf || knopf.disabled) return;
            this.k = Number(knopf.dataset.k);
            this._wolkenknoepfe();
            this._probeLaden();
        });
        for (const b of wurzel.querySelectorAll('[data-ergebnis]')) b.addEventListener('click', () => this._schalten('ergebnis', b.dataset.ergebnis));
        for (const b of wurzel.querySelectorAll('[data-ansicht]')) b.addEventListener('click', () => this._schalten('ansicht', b.dataset.ansicht));
        this.legende = wurzel.querySelector('[data-legende]');
    }

    _text(name, text) {
        const feld = document.querySelector(`[data-info="${name}"]`);
        if (feld) feld.textContent = text;
    }

    async _json(adresse) {
        const antwort = await fetch(adresse);
        if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
        return antwort.json();
    }

    async _binaer(adresse) {
        const antwort = await fetch(adresse);
        if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
        return antwort.arrayBuffer();
    }

    _figur(was) {
        if (!this.figuren.has(was)) {
            const abruf = this._binaer(`${this.basis}/figur/${was}/${this.laufParam}`).then(b => Z.figur(b));
            abruf.catch(() => this.figuren.delete(was));
            this.figuren.set(was, abruf);
        }
        return this.figuren.get(was);
    }

    _wolke(nr, k) {
        const schluessel = `${nr}/${k}`;
        if (!this.wolken.has(schluessel)) {
            const abruf = this._json(`${this.basis}/wolke/${nr}/${k}/${this.laufParam}`).then(w => ({ daten: w, objekt: Z.wolke(w) }));
            abruf.catch(() => this.wolken.delete(schluessel));
            this.wolken.set(schluessel, abruf);
        }
        return this.wolken.get(schluessel);
    }

    async laden() {
        try {
            this.daten = await this._json(`${this.basis}/${this.laufParam}`);
        } catch (fehler) {
            this._text('kopf', `Formvariante nicht lesbar: ${fehler.message}`);
            return;
        }
        const d = this.daten;
        if (!d.lauf) {
            this._text('kopf', d.hinweis);
            this.linien?.probe(null);
            this.zeigen();
            return;
        }
        this._kopfText();
        this._probenFuellen();
        T.regler(d);
        // Ohne Zuordnung Zeile ↔ Probe (`Mesh3daiformvariante.zuordnung`) gibt es nur das Mittel.
        if (!d.proben.length) this.ergebnisArt = 'mittel';
        this._knoepfeSetzen();
        try {
            const [puffer, ziel] = await Promise.all([this._binaer(`${this.basis}/koerper/`), this._figur('ziel')]);
            this.koerper = Z.koerper(puffer, this.basis);
            this.ziel = ziel;
        } catch (fehler) {
            this.fehler.soll = `Ziel nicht geladen: ${fehler.message}`;
        }
        await this._probeLaden();
    }

    _was() {
        return this.ergebnisArt === 'mittel' || !this.probe ? 'mittel' : String(this.probe.nr);
    }

    async _probeLaden() {
        const auftrag = ++this._auftrag;
        const was = this._was();
        const p = this.probe;
        this.linien?.probe(p?.nr ?? null, this.k);
        const [w, e] = await Promise.allSettled([p ? this._wolke(p.nr, this.k) : Promise.reject(new Error('keine Probe mit Wolke in diesem Lauf')), this._figur(was)]);
        if (auftrag !== this._auftrag) return;           // inzwischen etwas anderes gewählt
        this.wolke = w.status === 'fulfilled' ? w.value : null;
        this.ergebnis = e.status === 'fulfilled' ? e.value : null;
        this.fehler.eingabe = w.status === 'rejected' ? `Wolke nicht geladen: ${w.reason.message}` : null;
        this.fehler.ausgabe = e.status === 'rejected' ? `Ergebnis nicht geladen: ${e.reason.message}` : null;
        this._felderText();
        T.zahlen(this.daten, this.ergebnis?.kopf ?? null);
        this.zeigen();
    }

    _schalten(art, wert) {
        if (art === 'ergebnis') {
            this.ergebnisArt = wert;
            this._probeLaden();
        } else {
            this.ansicht = wert;
            this.zeigen();
        }
        this._knoepfeSetzen();
    }

    _knoepfeSetzen() {
        for (const b of this.wurzel.querySelectorAll('[data-ergebnis]')) {
            const an = b.dataset.ergebnis === this.ergebnisArt;
            b.classList.toggle('active', an);
            b.setAttribute('aria-pressed', String(an));
        }
        for (const b of this.wurzel.querySelectorAll('[data-ansicht]')) {
            const an = b.dataset.ansicht === this.ansicht;
            b.classList.toggle('active', an);
            b.setAttribute('aria-pressed', String(an));
        }
    }

    _kopfText() {
        const d = this.daten;
        const l = d.lauf;
        const m = d.modell || {};
        const zahl = g => d.proben.filter(p => p.gruppe === g).length;
        const umfang = l.schritte ? `${de(l.schritte)} Schritte` : `${l.epochen ?? '?'} Epochen`;
        const teile = [`Lauf ${l.name}${l.fertig ? '' : ' (läuft noch)'}: ${l.ki || 'Formkopf'}, ${umfang}, ${l.formregler ? de(l.formregler) : '?'} ${l.schritte ? 'Regler' : 'Formregler'} (${l.formregler_datei || '?'}), Eingang ${l.eingang}, Wolken ${l.wolken.join(', ')}.`,
            `${d.figur}: Grundlage ${d.grundlage}${m.geschlecht ? ', ' + (GESCHLECHT[m.geschlecht] ?? m.geschlecht) : ''}${m.gruppe ? ', ' + (GRUPPE[m.gruppe] ?? m.gruppe) : ''}`
            + `${m.mblab_vorlage ? ', MB-Lab-Vorlage ' + m.mblab_vorlage : ''}${m.lebensalter_jahre ? ', ' + de(m.lebensalter_jahre, 0) + ' Jahre' : ''}${m.weites_stueck ? ', weites Stück ' + m.weites_stueck : ''}.`,
            `${d.proben.length} Proben in diesem Lauf (${zahl('training')} Training, ${zahl('pruefung')} Prüfung).`];
        const ohne = Object.entries(d.gruppen || {}).filter(([, g]) => !g.zugeordnet);
        if (ohne.length) teile.push(`Die Zeilen der Vorhersage (${ohne.map(([g, z]) => `${GRUPPE[g] ?? g} ${z.zeilen}`).join(', ')}) passen nicht zu den Proben auf der Platte — das Ergebnis zeigt nur das Mittel.`);
        if (d.fremde?.length) teile.push(`${d.fremde.length} Regler der Figur kennt der Lauf nicht (${d.fremde.join(', ')}) — sie fehlen im Ziel.`);
        this._text('kopf', teile.join(' '));
    }

    _probenFuellen() {
        const w = this.probenwahl;
        w.replaceChildren(...this.daten.proben.map(p => new Option(`Probe ${p.nr}: ${p.name}${p.gruppe === 'pruefung' ? ' (Prüfung)' : ''}`, String(p.nr))));
        w.disabled = !this.daten.proben.length;
        if (!this.daten.proben.length) w.replaceChildren(new Option('— keine Probe zugeordnet —', ''));
        this.probe = this.daten.proben[0] ?? null;
        this.k = this.probe?.wolken[0] ?? 0;
        this._wolkenknoepfe();
    }

    /** Ein Knopf je Wolke, die der Lauf liest; eine, die diese Probe nicht hat (fehlt oder durchgefallen), ist gesperrt und sagt warum. */
    _wolkenknoepfe() {
        const alle = this.daten?.lauf?.wolken ?? [];
        const leiste = this.wolkenleiste;
        leiste.replaceChildren();
        if (alle.length < 2) return;
        const titel = document.createElement('span');
        titel.className = 'mesh3dai-fv-titel';
        titel.textContent = 'Wolke:';
        leiste.append(titel);
        for (const k of alle) {
            const b = document.createElement('button');
            b.type = 'button';
            b.className = 'schaltknopf' + (k === this.k ? ' active' : '');
            b.dataset.k = String(k);
            b.textContent = String(k);
            b.setAttribute('aria-pressed', String(k === this.k));
            const da = this.probe?.wolken.includes(k);
            b.disabled = !da;
            b.title = da ? `Wolke k = ${k}` : `Wolke k = ${k} fehlt für diese Probe oder hat die MIA-Prüfung nicht bestanden — der Lauf hat sie nicht gelesen`;
            leiste.append(b);
        }
    }

    _felderText() {
        const d = this.daten;
        const w = this.wolke?.daten;
        this._text('eingabe', this.fehler.eingabe || (w ? `${w.datei} (Probe ${w.nr}): ${de(w.punkte.length)} Punkte in der A-Pose. Farben wie in der Datei — das Training färbt sie je nach Lauf um (Einstellungen des Laufs).` : ''));
        const z = this.ziel?.kopf;
        this._text('soll', this.fehler.soll || (z ? `Genesis-Körper aus ${de(z.regler_gesetzt)} gesetzten Soll-Reglern des Laufs, Ruhelage, ohne Kleider und Haar; Haut von ${d.grundlage}. Höhe ${de(z.hoehe_m, 3)} m.` : ''));
        const e = this.ergebnis?.kopf;
        if (this.fehler.ausgabe || !e) {
            this._text('ausgabe', this.fehler.ausgabe || '');
            return;
        }
        const quelle = e.was === 'mittel' ? `Mittel der Vorhersagen über alle ${d.proben.length || '?'} Proben (so misst die echte Nachrechnung des Laufs)` : `Vorhersage aus Probe ${e.was}`;
        const a = e.abstand;
        this._text('ausgabe', `${quelle}: ${de(e.regler_gesetzt)} Regler gesetzt (geklemmt, |Wert| < 0,01 weg). Höhe ${de(e.hoehe_m, 3)} m.`
            + (a ? `\nAbstand zum Ziel über die 25.182 Körperpunkte: RMS ${de(a.rms_mm, 1)} mm, Median ${de(a.median_mm, 1)}, 95 % ${de(a.p95_mm, 1)} mm.` : ''));
    }

    _zeichnen(inhalt, art) {
        if (art === 'eingabe') {
            if (this.wolke) inhalt.add(this.wolke.objekt);
            return;
        }
        const figur = art === 'soll' ? this.ziel : this.ergebnis;
        if (!this.koerper || !figur) return;
        // „Abweichung“ färbt nur das Ergebnis; das Ziel steht dann einfarbig daneben.
        const ansicht = art === 'soll' && this.ansicht === 'abweichung' ? 'oberflaeche' : this.ansicht;
        inhalt.add(Z.mesh(this.koerper, figur, ansicht, this.ziel));
    }

    zeigen() {
        const da = { eingabe: !!this.wolke, soll: !!(this.koerper && this.ziel), ausgabe: !!(this.koerper && this.ergebnis) };
        for (const a of this.ansichten) a.zeigen(da[a.art] ? { echt: true } : null, this.fehler[a.art] || (this.daten?.lauf ? 'wird geladen …' : 'kein Lauf'));
        if (this.legende) this.legende.hidden = this.ansicht !== 'abweichung';
    }
}
