/**
 * Fotogenesisergebnis — Feld 4 „Ergebnis“ und die Karte „Vergleich aus allen Perspektiven“ der Seite „Foto-Genesis“ (24.10.2026).
 *
 * Feld 4: die Genesis-Figur aus Feld 3, gerendert aus der Perspektive des gewählten Fotos — so, wie die Charakter-Seite ein Exportfoto aufnimmt (`Fotogenesiskamera`). Die Karte: je Foto mit bekanntem Winkel
 * Foto | Rendering | Überlagerung und die Zahlen aus `Fotogenesisvergleich`. Ohne bekannte Kamera (echte Fotos) gibt es das Rendering mit FOV 20°, aber keine Zahl.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Fotogenesiskamera } from './fotogenesiskamera.js';
import { Fotogenesisseitenbild } from './fotogenesisseitenbild.js';
import { Fotogenesisvergleich } from './fotogenesisvergleich.js';

export class Fotogenesisergebnis {
    static KLEIN = [192, 256];
    /** Echte Fotos: Kamera unbekannt; Grund weiß wie die freigestellten Fotos (24.10.2026, `Fotogenesisseite.grund`). */
    static REGEL_OHNE = { fov: 20, rand: 1.08, grund: [255, 255, 255] };

    /**
     * @param {HTMLElement|null} feld Feld 4 (Leinwand-Fläche) @param {HTMLElement|null} info Text unter Feld 4 @param {HTMLElement} karte Inhalt der Vergleichskarte
     * @param {object} daten Seitendaten (`kamera`, `fotos`) @param {import('./fotogenesisfotos.js').Fotogenesisfotos} fotos
     * Ohne `feld` (27.10.2026: mit gerechneter Figur steht oben kein Ergebnis-Feld, `Fotogenesistrainingfigur`) nur die Vergleichskarte; die Meldungen stehen dann über ihr.
     */
    constructor(feld, info, karte, daten, fotos) {
        this.feld = feld;
        this.info = info ?? karte.parentElement.insertBefore(Object.assign(document.createElement('p'), { className: 'hb-hinweis' }), karte);
        this.karte = karte;
        this.daten = daten;
        this.fotos = fotos;
        this.regel = daten.kamera ?? Fotogenesisergebnis.REGEL_OHNE;
        this.leinwand = feld ? feld.appendChild(document.createElement('canvas')) : null;
        if (this.leinwand) this.leinwand.className = 'fotogenesis-rendering';
        this._lauf = 0;
    }

    leeren(text) {
        if (this.leinwand) this.leinwand.hidden = true;
        this.info.textContent = text;
        this.karte.replaceChildren(Object.assign(document.createElement('p'), { className: 'hb-hinweis', textContent: text }));
    }

    /**
     * Feld 4 und die Karte neu rechnen. @param ansicht Feld 3 (`Meshgenesisansicht`, die Figur hängt in `ansicht.inhalt`) @param {THREE.Quaternion} rahmen Fotos → Welt
     * @param {number} nr das gewählte Foto
     */
    async zeigen(ansicht, rahmen, nr) {
        const lauf = ++this._lauf;
        const box = Fotogenesiskamera.huelle(ansicht.inhalt, rahmen);
        if (box.isEmpty()) return this.leeren('Keine sichtbare Genesis-Figur.');
        if (this.leinwand) await this._feld(ansicht, box, rahmen, nr, lauf);
        if (lauf !== this._lauf) return;
        await this._karte(ansicht, box, rahmen, lauf);
    }

    /** Feld 4: die Figur aus der Perspektive des Fotos `nr`. */
    async _feld(ansicht, box, rahmen, nr, lauf) {
        const foto = this.daten.fotos[nr];
        const [b, h] = this._groesse(nr);
        this.leinwand.hidden = false;
        if (foto.winkel === null) {
            this.info.textContent = 'Für dieses Foto ist der Winkel unbekannt — kein Rendering.';
            this.leinwand.hidden = true;
        } else {
            // Mit Kameras der Einpassung (26.10.2026, Edgar: „es gibt auch Unterschiede zwischen dem 3D View oben und den Ergebnis fotos, z.B. augen, warum?“): dasselbe Bild wie die
            // Testzeilen und die Abnahme — vorher stand hier die Figur in der Grundhaltung aus einer Kamera mit 20° auf die Hülle, also aus anderem Abstand, Winkel und mit anderer Haltung
            const eigen = await this._einpassung(nr).catch(fehler => { console.warn(`Fotogenesisergebnis: ${fehler.message}`); return null; });
            if (lauf !== this._lauf) return;
            if (eigen?.figur) {
                await this._bildZeigen(eigen);
                this.info.textContent = `${foto.name} · Kamera der Einpassung, Haltung ${eigen.haltung === 'je Foto' ? 'dieses Fotos' : 'gemeinsam'} — dasselbe Bild wie in den Testzeilen.`;
            } else {
                this.leinwand.classList.remove('fotogenesis-wiefoto');
                Fotogenesisvergleich.rendern(ansicht, box, foto.winkel, rahmen, this.leinwand, b, h, this.regel);
                this.info.textContent = this.daten.kamera ? `${foto.name} · gerendert nach der Regel der Charakter-Seite (20°, Hülle × 1,08).`
                    : `${foto.name} · Kamera der Fotos unbekannt: gerendert mit 20° auf die Hülle der Figur — zum Ansehen, keine Messung.`;
            }
        }
    }

    /** Bild aus Kamera und Haltung der Einpassung für Foto `nr` (0-basiert; `kameras.json` zählt ab 1) — null, wenn der Job keine Kameras hat oder die Seite fehlt. */
    async _einpassung(nr) {
        if (!this.seite) return null;
        this._kameras ??= Promise.all([Serverabruf.json(`/api/fotogenesis/${this.daten.id}/abnahme/kameras/`).catch(() => null),
                                       Serverabruf.json(`/api/fotogenesis/${this.daten.id}/abnahme/haltungen/`).catch(() => ({ fotos: {} }))]);
        const [kameras, haltungen] = await this._kameras;
        const k = Object.values(kameras?.kameras || {}).find(x => Number(x.nr) === nr + 1);
        return k ? Fotogenesisseitenbild.inHaltung(this.seite, k, haltungen?.fotos || {}) : null;
    }

    async _bildZeigen(b) {
        const bild = new Image();
        bild.src = b.url;
        await bild.decode();
        // so groß wie das Foto in Feld 1 (Edgar 26.10.2026: „mache Vorlage und Ergebnis gleich groß“): dasselbe Bildformat, dieselbe Einpassung in die Fläche (object-fit wie .fotogenesis-foto)
        Object.assign(this.leinwand, { width: b.breite, height: b.hoehe });
        this.leinwand.removeAttribute('style');
        this.leinwand.classList.add('fotogenesis-wiefoto');
        const c = this.leinwand.getContext('2d');
        c.fillStyle = '#ffffff';
        c.fillRect(0, 0, this.leinwand.width, this.leinwand.height);
        c.drawImage(bild, 0, 0, this.leinwand.width, this.leinwand.height);
    }

    /** Größe des Renderings in Feld 4: so groß wie die Fläche erlaubt, im Seitenverhältnis des Fotos. */
    _groesse(nr) {
        const bild = this.fotos.gross;
        const verhaeltnis = this.daten.kamera ? this.daten.kamera.breite / this.daten.kamera.hoehe
            : (bild?.naturalWidth && bild.naturalHeight && Number(bild.dataset.nr) === nr ? bild.naturalWidth / bild.naturalHeight : 0.75);
        const h = Math.max(this.feld.clientHeight - 4, 64), b = Math.min(Math.round(h * verhaeltnis), this.feld.clientWidth || h);
        return [b, Math.round(b / verhaeltnis)];
    }

    async _karte(ansicht, box, rahmen, lauf) {
        const zeilen = [], spalten = [];
        const p = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 1 });
        for (const foto of this.daten.fotos.filter(f => f.winkel !== null)) {
            const spalte = document.createElement('figure');
            spalte.className = 'fotogenesis-vergleichsspalte';
            const titel = spalte.appendChild(document.createElement('figcaption'));
            const reihe = spalte.appendChild(document.createElement('div'));
            reihe.className = 'fotogenesis-vergleichsbilder';
            const bild = await this.fotos.bild(foto.nr).catch(f => { titel.textContent = f.message; return null; });
            if (lauf !== this._lauf) return;
            const [b, h] = this.daten.kamera ? Fotogenesisergebnis.KLEIN : [Fotogenesisergebnis.KLEIN[0], Math.round(Fotogenesisergebnis.KLEIN[0] * (bild ? bild.naturalHeight / bild.naturalWidth : 4 / 3))];
            const rendering = document.createElement('canvas');
            Fotogenesisvergleich.rendern(ansicht, box, foto.winkel, rahmen, rendering, b, h, this.regel);
            if (bild) reihe.append(Object.assign(bild.cloneNode(), { className: 'fotogenesis-vergleichsbild', alt: foto.name }));
            reihe.append(rendering);
            if (this.daten.kamera && bild) {
                const maske = document.createElement('canvas');
                Fotogenesisvergleich.rendern(ansicht, box, foto.winkel, rahmen, maske, b, h, this.regel, Fotogenesisvergleich.SCHLUESSEL);
                const ueber = reihe.appendChild(document.createElement('canvas'));
                const m = Fotogenesisvergleich.messen(bild, rendering, maske, ueber, this.regel.grund);
                titel.textContent = `${foto.name} (${foto.winkel}°) · ${Fotogenesisvergleich.text(m)}`;
                zeilen.push(m);
            } else {
                titel.textContent = `${foto.name} (${foto.winkel}°) · Kamera unbekannt, keine Zahl`;
            }
            spalten.push(spalte);
        }
        if (lauf !== this._lauf) return;
        const summe = document.createElement('p');
        summe.className = 'fotogenesis-vergleichssumme';
        if (zeilen.length) {
            const deckung = zeilen.reduce((s, m) => s + m.deckung, 0) / zeilen.length;
            summe.textContent = `Mittel über ${zeilen.length} Perspektiven: Umriss-Deckung ${p.format(deckung * 100)} % — grau: beide, rot: nur im Foto, türkis: nur im Rendering.`;
        } else {
            summe.textContent = spalten.length ? 'Kamera der Fotos unbekannt: Renderings zum Ansehen, keine Zahlen.' : 'Kein Foto mit bekanntem Winkel.';
        }
        this.karte.replaceChildren(summe, ...spalten);
    }
}
