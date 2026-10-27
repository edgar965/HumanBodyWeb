/**
 * Mesh3dailinien — Reihe „Messlinien“ (27.10.2026, Edgar: „Ich möchte auch bei dir ganz genau sehen, was du machst. Zeig mir den Input, den Output und die ganzen Linien, die du errechnet hast“)
 * auf der Seite „Formvariante“ (je Prüfprobe) und auf der Seite eines Testjobs (Probe 0, geschrieben vom Formschritt der Kette). Drei Felder, alle im Rahmen, den die KI sah:
 * Eingang (gemessen von der Grundfigur aus — das bekommt die KI) · Ausgang (von der Figur der KI aus — was danach fehlt) · Bezug (von der wahren Figur aus, nur mit Wahrheit).
 * Gezeichnet wie die Messpunkte der 2d-3d-AI (`Mesh3dailinienzeichner`): blau = Treffer auf der Wolke (Vorlage), schwarz = Figurpunkt (Ergebnis), rot = Abweichung dazwischen.
 * Weg MIA (A-Pose des Eingangs) oder Rig (Ruhe einer Rig-Figur). Daten `…/linien/<nr>/` (Server `Mesh3dailinien`, gerechnet auf der Karte).
 */
import { Mesh3daiansicht } from './mesh3daiansicht.js';
import { Mesh3dailinienzeichner as LZ } from './mesh3dailinienzeichner.js';

const de = (n, s = 0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });
const WAS = ['start', 'ergebnis', 'ziel'];
const KLASSEN = { haut: ['Haut', 1], stoff: ['Stoff', 2], haar: ['Haar', 3] };
const KAMERA = { position: [1.7, 1.5, 3.4], ziel: [0, 0.95, 0], boden: true };

export class Mesh3dailinien {
    /** Seite eines Testjobs: `data-kennung` am Abschnitt, Probe 0. */
    static testStarten(wurzel) {
        const linien = new Mesh3dailinien(wurzel, `/api/mesh3dai/test/${encodeURIComponent(wurzel.dataset.kennung)}`, '', KAMERA);
        window.__mesh3dailinien = linien;
        linien.probe(0);
        return linien;
    }

    constructor(wurzel, basis, laufParam, kamera = KAMERA) {
        this.wurzel = wurzel;
        this.basis = basis;
        this.laufParam = laufParam;
        this.weg = 'mia';
        this._wegGewaehlt = false;
        this.zeige = { vorlage: true, ergebnis: true, verbindung: true, wolke: false };
        this.klassen = { 1: true, 2: true, 3: true };
        this.pakete = new Map();
        this.geometrien = new Map();
        this.aktuell = null;
        this.fehler = null;
        this._auftrag = 0;
        const zeichner = { zeichnen: (inhalt, art) => this._zeichnen(inhalt, art) };
        this.ansichten = WAS.map(was => new Mesh3daiansicht(wurzel.querySelector(`.mesh3dai-leinwand[data-art="linien-${was}"]`), was, zeichner, kamera));
        for (const b of wurzel.querySelectorAll('[data-weg]')) b.addEventListener('click', () => {
            this.weg = b.dataset.weg;
            this._wegGewaehlt = true;
            this._neu();
        });
        for (const b of wurzel.querySelectorAll('[data-zeige]')) b.addEventListener('click', () => {
            this.zeige[b.dataset.zeige] = !this.zeige[b.dataset.zeige];
            this._neu();
        });
        for (const b of wurzel.querySelectorAll('[data-klasse]')) b.addEventListener('click', () => {
            this.klassen[b.dataset.klasse] = !this.klassen[b.dataset.klasse];
            this._neu();
        });
        this._knoepfe();
    }

    _neu() {
        this._knoepfe();
        this._texte();
        this.zeigen();
    }

    _text(name, text) {
        const feld = this.wurzel.querySelector(`[data-info="${name}"]`);
        if (feld) feld.textContent = text;
    }

    _knoepfe() {
        const an = (b, ja) => {
            b.classList.toggle('active', ja);
            b.setAttribute('aria-pressed', String(ja));
        };
        for (const b of this.wurzel.querySelectorAll('[data-weg]')) an(b, b.dataset.weg === this.weg);
        for (const b of this.wurzel.querySelectorAll('[data-zeige]')) an(b, this.zeige[b.dataset.zeige]);
        for (const b of this.wurzel.querySelectorAll('[data-klasse]')) an(b, this.klassen[b.dataset.klasse]);
    }

    /** Probe nr (Wolke k) der Seite; Linien gibt es nur für k = 0 (die Wolke, die die KI im Training sah). */
    async probe(nr, k = 0) {
        const auftrag = ++this._auftrag;
        this.aktuell = null;
        this.fehler = nr == null ? 'keine Probe' : (k !== 0 ? `Messlinien gibt es nur für Wolke 0 — gewählt ist Wolke ${k}` : null);
        if (!this.fehler) {
            if (!this.pakete.has(nr)) {
                const abruf = fetch(`${this.basis}/linien/${nr}/${this.laufParam}`).then(async a => {
                    if (!a.ok) throw new Error(a.status === 404 ? 'Keine Messlinien gerechnet' : `HTTP ${a.status}`);
                    return LZ.paket(await a.arrayBuffer());
                });
                abruf.catch(() => this.pakete.delete(nr));
                this.pakete.set(nr, abruf);
            }
            try {
                const paket = await this.pakete.get(nr);
                if (auftrag !== this._auftrag) return;
                this.aktuell = paket;
                // Ein Testjob kennt nur den Weg seiner Kette — mit ihm beginnen, solange niemand umgeschaltet hat.
                if (paket.kopf.weg && !this._wegGewaehlt) this.weg = paket.kopf.weg;
            } catch (fehler) {
                if (auftrag !== this._auftrag) return;
                this.fehler = fehler.message;
            }
        }
        this._neu();
    }

    _geometrie(schluessel, bauen) {
        if (!this.geometrien.has(schluessel)) this.geometrien.set(schluessel, bauen());
        return this.geometrien.get(schluessel);
    }

    _zeichnen(inhalt, was) {
        const p = this.aktuell;
        if (!p) return;
        const nr = p.kopf.nr;
        const d = p.daten;
        const s = `${this.weg}_${was}_`;
        const wolke = this.weg === 'rig' ? 'rig_wolke' : 'wolke';
        if (this.zeige.wolke && d[wolke]) inhalt.add(LZ.objekt('wolke', this._geometrie(`${nr}|${wolke}`, () => LZ.wolke(d[wolke]))));
        if (!d[s + 'ort']) return;
        const k = d[s + 'klasse'];
        const filter = Object.keys(this.klassen).filter(c => this.klassen[c]).join('');
        const gewaehlt = c => c > 0 && this.klassen[c];
        const bau = (art, f) => inhalt.add(LZ.objekt(art, this._geometrie(`${nr}|${s}${art}|${filter}`, f)));
        if (this.zeige.verbindung) bau('verbindung', () => LZ.verbindung(d[s + 'ort'], d[s + 'ende'], k, gewaehlt));
        if (this.zeige.vorlage) bau('vorlage', () => LZ.punkte(d[s + 'ende'], k, gewaehlt));
        if (this.zeige.ergebnis) {
            bau('ergebnis', () => LZ.punkte(d[s + 'ort'], k, gewaehlt));
            bau('offen', () => LZ.punkte(d[s + 'ort'], k, c => c === 0));
        }
    }

    _feldText(was) {
        const p = this.aktuell;
        if (!p) return this.fehler ?? '';
        const z = p.kopf.zahlen?.[this.weg]?.[was];
        if (!z) {
            if (was === 'ziel' && p.kopf.wahrheit === false) return 'Kein Bezug: dieser Testjob hat keine Wahrheit.';
            if (was === 'ergebnis' && this.weg === 'rig' && !p.kopf.rig_gelernt) return 'Dieser Lauf hat den Weg Rig nicht gelernt — kein Ergebnis.';
            return p.kopf.test ? `Die Kette hat diesen Job auf dem Weg ${p.kopf.weg === 'rig' ? 'Rig' : 'MIA'} gerechnet — hier gibt es keine Linien.` : 'keine Linien';
        }
        const teile = Object.entries(KLASSEN).map(([c, [name]]) => (z[c]?.linien ? `${name}: ${de(z[c].linien)} Linien, Abweichung Median ${de(z[c].median_mm, 1)} mm` : `${name}: —`));
        let text = `${teile.join(' · ')} · gefunden ${de(100 * z.gefunden, 1)} %, grau: nichts gefunden.`;
        if (was === 'ergebnis') {
            const r = p.kopf.zahlen?.regler_gesetzt?.[this.weg];
            if (r != null) text += ` ${de(r)} Regler gesetzt (|Wert| ≥ 0,01).`;
            const g = p.kopf.zahlen?.gegenprobe_max;
            if (this.weg === 'mia' && g != null) text += ` Gegenprobe gegen die gespeicherte Vorhersage des Laufs: größte Abweichung ${de(g, 4)}.`;
        }
        return text;
    }

    _texte() {
        for (const was of WAS) this._text(`linien-${was}`, this._feldText(was));
        const k = this.aktuell?.kopf;
        if (!k) {
            this._text('linien-kopf', this.fehler ?? '');
            return;
        }
        const r = k.rig || {};
        const wege = this.weg === 'rig'
            ? `Weg Rig: die Wolke in der Ruhe einer Rig-Figur${k.test ? ' (aus der Kette)' : ` (nachgestellt: Figur ein Stück zu einer anderen Trainingsfigur gezogen, Knochen verrauscht bis ${de(Math.max(...Object.values(r.sigma_grad || { a: 0 })), 1)}°, Wurzel ${de(r.wurzel_grad ?? 0, 1)}° und ${de(1000 * (r.wurzel_m ?? 0), 1)} mm)`}; die Figuren stehen in Ruhe, auf die Höhe der Wolke gestreckt.${k.rig_gelernt ? '' : ' Dieser Lauf hat den Weg nicht gelernt.'}`
            : 'Weg MIA: die A-Pose-Wolke, wie die KI sie sah; die Figuren stehen in der A-Pose des Eingangs, auf die Höhe der Wolke gestreckt.';
        const wer = k.test ? `Testjob ${k.test}` : `Probe ${k.nr}`;
        this._text('linien-kopf', `${wer}, Regler-KI ${k.lauf}, gerechnet ${k.erzeugt}. ${wege} Je Linie: vom Figurpunkt (schwarz) entlang der Normale bis zu der Fläche der Wolke, die die Messung dort findet (blau, höchstens 10 cm); rot ist die Abweichung.`);
    }

    zeigen() {
        for (const a of this.ansichten) a.zeigen(this.aktuell ? { echt: true } : null, this.fehler || 'wird geladen …');
    }
}
