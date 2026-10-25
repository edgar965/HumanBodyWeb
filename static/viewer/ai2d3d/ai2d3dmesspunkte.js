/**
 * Ai2d3dmesspunkte — Testzeile „Messpunkte des Körpers“ der Seite „2d-3d-AI“ (24.10.2026; Edgar: „warum erkennst du nicht die Formunterschiede zwischen Vorlage und Ziel? … Erkläre mir, was
 * du misst. Mach eine Testzeile unter der ersten Zeile mit den 3 Views, wo du zusätzlich in jeder View alle Messpunkte des Körpers einblendest, mit Zahlen, in einer Tabelle daneben die
 * Messpunkte und 2 Spalten für Vorlage und Ergebnis“).
 *
 * Gezeigt wird, was die Abnahme misst (`Koerpermesspunkte`, `koerperpruefung_lauf.py --seite` → `<Job>/abnahme/messpunkte.json`), für das in der Leiste gewählte Foto:
 *  1 das Foto mit den Punkten der Vorlage, 2 die Figur DIESER Seite aus der Kamera der Einpassung (`seite_<nr>.png`, `Ai2d3dseitenbild`) mit den Punkten des Ergebnisses,
 *  3 beide übereinander, jeder Punkt der Vorlage mit seinem Ergebnis verbunden. Felder 2 und 3 der ersten Zeile stellen ihre Kamera nach der Regel der Charakter-Seite, nicht nach der
 *  Einpassung — dort lägen die Punkte nicht auf dem Foto. Rot: über der Grenze; grau: nicht gewertet (Arm am Rumpf, Beine aneinander), der Grund steht im Tooltip der Zeile.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Ai2d3dmesslupe } from './ai2d3dmesslupe.js';

export class Ai2d3dmesspunkte {
    static HOEHE = 640;
    static RAND = 0.04;
    static FARBE = { vorlage: '#1c7ed6', ergebnis: '#f76707', ueber: '#e03131', offen: '#868e96' };

    /** @param {HTMLElement} karte die Karte `#ai2d3d-messpunkte` @param {string} job Kennung @param {{adresse: string}[]} fotos Fotos der Seite in ihrer Reihenfolge
     *  @param {{daten: string, seite: (nr: number) => string}} [adressen] Daten und Rendering je Foto (ab 1) — Vorgabe die Abnahme von 2d-3d-AI; Mesh3D-AI nimmt die Kostüm-Prüfung
     *  (`Mesh3daitestmesspunkte`, 24.10.2026 nachts) */
    constructor(karte, job, fotos, adressen = null) {
        this.karte = karte;
        this.job = job;
        this.fotos = fotos;
        this.adressen = adressen ?? { daten: `/api/2d3dai/${job}/abnahme/messpunkte/`, seite: nr => `/api/2d3dai/${job}/abnahme/seite/${nr}/` };
        this.info = karte.querySelector('[data-info]');
        this.flaechen = [...karte.querySelectorAll('canvas[data-ansicht]')];
        this.tabelle = karte.querySelector('tbody');
        this.hervor = null;
        this.tabelle.addEventListener('mouseover', e => this._hervorheben(e.target.closest('tr[data-nummern]')?.dataset.nummern ?? null));
        this.tabelle.addEventListener('mouseleave', () => this._hervorheben(null));
        this.bereit = Serverabruf.json(this.adressen.daten).then(d => { this.daten = d; })
            .catch(fehler => { this.info.textContent = `Keine Messpunkte: ${fehler.message}`; });
    }

    /** Das Foto Nummer `nr` (Reihenfolge der Seite; `messpunkte.json` zählt ab 1 in derselben Reihenfolge) zeigen. */
    async zeigen(nr) {
        const lauf = this._lauf = (this._lauf ?? 0) + 1;
        await this.bereit;
        const f = this.daten?.fotos?.[String(nr + 1)];
        if (!f) {
            if (this.daten) this.info.textContent = `Für Bild ${nr + 1} liegen keine Messpunkte vor.`;
            return;
        }
        const laden = adresse => new Promise((fertig, fehler) => {
            const b = new Image();
            b.onload = () => fertig(b);
            b.onerror = () => fehler(new Error(`${adresse} nicht geladen`));
            b.src = adresse;
        });
        try {
            [this.foto, this.seite] = await Promise.all([laden(this.fotos[nr].adresse), laden(this.adressen.seite(nr + 1))]);
        } catch (fehler) {
            this.info.textContent = fehler.message;
            return;
        }
        if (lauf !== this._lauf) return;          // inzwischen ein anderes Foto gewählt
        this.f = f;
        this._info();
        this._tabelle();
        this._zeichnen();
    }

    _info() {
        const f = this.f, d = this.daten, z = Ai2d3dmesspunkte._zahl;
        const rand = f.zeilen.filter(r => r.art === 'rand'), lage = f.zeilen.filter(r => r.art === 'lage');
        const zaehlen = zeilen => [zeilen.filter(r => r.ueber).length, zeilen.filter(r => r.hinweis).length, zeilen.length];
        const [ru, ro, rn] = zaehlen(rand), [lu, , ln] = zaehlen(lage);
        this.info.textContent = `${f.datei} · Stand ${d.stand}, gemessen ${d.gerechnet.replace('T', ' ')} · Umriss: ${ru} von ${rn} Randpunkten über ${z(d.grenzen.rand_mm)} mm, `
            + `${ro} nicht gewertet · ${f.texte?.lage_kurz ?? 'Gelenke'}: ${lu} von ${ln} ${f.texte ? 'Gruppen' : 'Punkten'} über ${z(d.grenzen.punkte_mm)} mm · `
            + `${z(f.mm_je_px, 2)} mm je Pixel · ${d.gelenke}, ${d.umriss}.`
            + (f.veraltet ? ' ACHTUNG: Das Rendering ist neuer als die Messung — erst koerperpruefung_lauf.py --seite.' : '');
        this.info.classList.toggle('ai2d3d-mess-warnung', !!f.veraltet);
    }

    static _zahl(x, stellen = 0) {
        return x === null || x === undefined ? '—' : new Intl.NumberFormat('de-DE', { maximumFractionDigits: stellen, minimumFractionDigits: stellen }).format(x);
    }

    _tabelle() {
        const z = Ai2d3dmesspunkte._zahl, zeilen = [];
        const kopf = () => Object.assign(document.createElement('tr'), { className: 'ai2d3d-mess-gruppe', innerHTML: '<td colspan="5"></td>' });
        let art = null;
        for (const r of this.f.zeilen) {
            if (r.art !== art) {
                art = r.art;
                const k = kopf();
                // Jede Zahl ist die Länge einer Linie im Bild (Edgar 25.10.2026: „es muss doch für jede Zahl eine Linie kommen“); die Lage der Punkte ab Hüftmitte steht im Tooltip
                // Texte der Kopfzeile (`Kopfmesspunkte.TEXTE`) kommen mit den Daten, die des Körpers stehen hier
                k.firstChild.textContent = this.f.texte?.[art] ?? (art === 'lage' ? 'Kopf, Gelenke, Füße (ViTPose): Abweichung = Linie vom blauen Punkt (Foto) zum orangen (Rendering)'
                    : 'Umriss (Sapiens2): Vorlage = blaue Linie Knochenachse → Rand im Foto (Feld 1), Ergebnis = orange Linie bis zum Rand im Rendering (Feld 2), '
                      + 'Abweichung = Ergebnis − Vorlage (+ zu breit, − zu schmal)');
                zeilen.push(k);
            }
            const mm = v => (v === null || v === undefined ? '—' : `${z(v)} mm`), lage = v => (v ? `${z(v[0])} / ${z(v[1])} mm` : '—');
            const tr = document.createElement('tr');
            tr.dataset.nummern = r.nummern.join(','), tr.className = r.ueber ? 'ai2d3d-mess-ueber' : r.hinweis ? 'ai2d3d-mess-offen' : '';
            const ursprung = this.f.texte?.ursprung ?? 'Hüftmitte der Vorlage';
            tr.title = `Grenze ${z(r.grenze_mm)} mm${r.art === 'lage' ? ` · Lage ab ${ursprung} (x rechts / y oben): Foto ${lage(r.vorlage)}, Rendering ${lage(r.ergebnis)}` : ''}`
                + `${r.hinweis ? ` · ${r.hinweis}` : ''} · Zeile berühren: Lupe in Feld 3`;
            const zellen = r.art === 'lage' ? ['Punkt', 'Punkt'] : [mm(r.vorlage), mm(r.ergebnis)];
            const n = r.nummern, nr = n.length > 2 ? `${n[0]}–${n[n.length - 1]}` : n.join('–');     // Gruppe des Kopfes: „1–17“ statt jeder Nummer
            for (const text of [nr, r.name, ...zellen, mm(r.abweichung_mm)]) tr.appendChild(document.createElement('td')).textContent = text;
            zeilen.push(tr);
        }
        this.tabelle.replaceChildren(...zeilen);
    }

    _hervorheben(nummern) {
        this.hervor = nummern ? new Set(nummern.split(',').map(Number)) : null;
        this.hervorZeile = nummern ? this.f?.zeilen.find(r => r.nummern.join(',') === nummern) ?? null : null;
        if (this.f) this._zeichnen();
    }

    /** Ausschnitt um beide Personen (Pixel des Fotos) und Maßstab auf die Fläche. */
    _ausschnitt(flaeche) {
        const [x0, y0, x1, y1] = this.f.kasten_px, [b, h] = this.f.groesse, r = Ai2d3dmesspunkte.RAND * (y1 - y0);
        const k = [Math.max(0, x0 - r), Math.max(0, y0 - r), Math.min(b, x1 + r), Math.min(h, y1 + r)];
        const breite = flaeche.parentElement.clientWidth || 300;
        const s = Math.min(breite / (k[2] - k[0]), Ai2d3dmesspunkte.HOEHE / (k[3] - k[1]));
        return { k, s, b: Math.round((k[2] - k[0]) * s), h: Math.round((k[3] - k[1]) * s) };
    }

    _zeichnen() {
        const status = new Map(this.f.zeilen.flatMap(r => r.nummern.map(n => [n, r.ueber ? 'ueber' : r.hinweis ? 'offen' : 'ok'])));
        for (const flaeche of this.flaechen) {
            const a = this._ausschnitt(flaeche), dpr = window.devicePixelRatio || 1, ansicht = flaeche.dataset.ansicht;
            Object.assign(flaeche, { width: Math.round(a.b * dpr), height: Math.round(a.h * dpr) });
            Object.assign(flaeche.style, { width: `${a.b}px`, height: `${a.h}px` });
            const c = flaeche.getContext('2d');
            c.setTransform(dpr, 0, 0, dpr, 0, 0);
            c.fillStyle = '#ffffff';
            c.fillRect(0, 0, a.b, a.h);
            const [kx, ky, kx1, ky1] = a.k, q = this.seite.naturalWidth / this.f.groesse[0];
            if (ansicht !== 'ergebnis') c.drawImage(this.foto, kx, ky, kx1 - kx, ky1 - ky, 0, 0, a.b, a.h);
            if (ansicht !== 'vorlage') {
                c.globalAlpha = ansicht === 'beide' ? 0.5 : 1;
                c.drawImage(this.seite, kx * q, ky * q, (kx1 - kx) * q, (ky1 - ky) * q, 0, 0, a.b, a.h);
                c.globalAlpha = 1;
            }
            const auf = p => [(p[0] - kx) * a.s, (p[1] - ky) * a.s];
            this._punkte(c, auf, ansicht, status);
            if (ansicht === 'beide' && this.hervorZeile) Ai2d3dmesslupe.zeichnen(c, a, this.foto, this.seite, q, this.hervorZeile, this.f.punkte, Ai2d3dmesspunkte.FARBE);
        }
    }

    _punkte(c, auf, ansicht, status) {
        const F = Ai2d3dmesspunkte.FARBE, seiten = ansicht === 'beide' ? ['vorlage', 'ergebnis'] : [ansicht];
        c.lineWidth = 1;
        for (const p of this.f.punkte) {
            const st = status.get(p.nr), hervor = this.hervor?.has(p.nr);
            if (this.hervor && !hervor) c.globalAlpha = 0.35;
            // Randpunkt: die Zahl der Tabelle ist die Länge der Linie Knochenachse → Rand (blau Foto, orange Rendering); Punkt: Linie blau → orange in Feld 3
            if (p.achse) {
                c.lineWidth = 2;
                for (const seite of seiten) {
                    if (!p[seite]) continue;
                    c.strokeStyle = F[seite];
                    Ai2d3dmesspunkte._strich(c, auf(p.achse), auf(p[seite]));
                }
            }
            // Punkt: die Linie blau → orange in allen drei Feldern (Edgar 25.10.2026: „bei den Messungen überall Linien zeigen“), am Umriss nur in Feld 3
            if (p.vorlage && p.ergebnis && (ansicht === 'beide' || !p.achse)) {
                c.strokeStyle = st === 'ueber' ? F.ueber : '#222222';
                c.lineWidth = 2;
                Ai2d3dmesspunkte._strich(c, auf(p.vorlage), auf(p.ergebnis));
            }
            c.lineWidth = 1;
            for (const seite of seiten) {
                if (!p[seite]) continue;
                const [x, y] = auf(p[seite]);
                c.fillStyle = st === 'offen' ? F.offen : F[seite];
                c.beginPath();
                c.arc(x, y, hervor ? 6 : 3, 0, 2 * Math.PI);
                c.fill();
                if (st === 'ueber') {
                    c.strokeStyle = F.ueber;
                    c.lineWidth = 2;
                    c.stroke();
                    c.lineWidth = 1;
                }
                if (seite === seiten[0]) Ai2d3dmesspunkte._nummer(c, String(p.nr), x + 4, y - 4, st === 'ueber' ? F.ueber : '#111111', hervor);
            }
            c.globalAlpha = 1;
        }
    }

    static _strich(c, a, b) {
        c.beginPath();
        c.moveTo(a[0], a[1]);
        c.lineTo(b[0], b[1]);
        c.stroke();
    }

    static _nummer(c, text, x, y, farbe, gross) {
        c.font = `${gross ? 'bold 14px' : '10px'} system-ui, sans-serif`;
        c.lineWidth = 3;
        c.strokeStyle = 'rgba(255, 255, 255, 0.9)';
        c.strokeText(text, x, y);
        c.fillStyle = farbe;
        c.fillText(text, x, y);
        c.lineWidth = 1;
    }
}
