/**
 * Ai2d3dergebnis — Feld 4 „Ergebnis“ und die Karte „Vergleich aus allen Perspektiven“ der Seite „2d-3d-AI“ (24.10.2026).
 *
 * Feld 4: die Genesis-Figur aus Feld 3, gerendert aus der Perspektive des gewählten Fotos — so, wie die Charakter-Seite ein Exportfoto aufnimmt (`Ai2d3dkamera`). Die Karte: je Foto mit bekanntem Winkel
 * Foto | Rendering | Überlagerung und die Zahlen aus `Ai2d3dvergleich`. Ohne bekannte Kamera (echte Fotos) gibt es das Rendering mit FOV 20°, aber keine Zahl.
 */
import { Ai2d3dkamera } from './ai2d3dkamera.js';
import { Ai2d3dvergleich } from './ai2d3dvergleich.js';

export class Ai2d3dergebnis {
    static KLEIN = [192, 256];
    /** Echte Fotos: Kamera unbekannt; Grund weiß wie die freigestellten Fotos (24.10.2026, `Ai2d3dseite.grund`). */
    static REGEL_OHNE = { fov: 20, rand: 1.08, grund: [255, 255, 255] };

    /**
     * @param {HTMLElement} feld Feld 4 (Leinwand-Fläche) @param {HTMLElement} info Text unter Feld 4 @param {HTMLElement} karte Inhalt der Vergleichskarte
     * @param {object} daten Seitendaten (`kamera`, `fotos`) @param {import('./ai2d3dfotos.js').Ai2d3dfotos} fotos
     */
    constructor(feld, info, karte, daten, fotos) {
        this.feld = feld;
        this.info = info;
        this.karte = karte;
        this.daten = daten;
        this.fotos = fotos;
        this.regel = daten.kamera ?? Ai2d3dergebnis.REGEL_OHNE;
        this.leinwand = feld.appendChild(document.createElement('canvas'));
        this.leinwand.className = 'ai2d3d-rendering';
        this._lauf = 0;
    }

    leeren(text) {
        this.leinwand.hidden = true;
        this.info.textContent = text;
        this.karte.replaceChildren(Object.assign(document.createElement('p'), { className: 'hb-hinweis', textContent: text }));
    }

    /**
     * Feld 4 und die Karte neu rechnen. @param ansicht Feld 3 (`Mesh3daiansicht`, die Figur hängt in `ansicht.inhalt`) @param {THREE.Quaternion} rahmen Fotos → Welt
     * @param {number} nr das gewählte Foto
     */
    async zeigen(ansicht, rahmen, nr) {
        const lauf = ++this._lauf;
        const box = Ai2d3dkamera.huelle(ansicht.inhalt, rahmen);
        if (box.isEmpty()) return this.leeren('Keine sichtbare Genesis-Figur.');
        const foto = this.daten.fotos[nr];
        const [b, h] = this._groesse(nr);
        this.leinwand.hidden = false;
        if (foto.winkel === null) {
            this.info.textContent = 'Für dieses Foto ist der Winkel unbekannt — kein Rendering.';
            this.leinwand.hidden = true;
        } else {
            Ai2d3dvergleich.rendern(ansicht, box, foto.winkel, rahmen, this.leinwand, b, h, this.regel);
            this.info.textContent = this.daten.kamera ? `${foto.name} · gerendert nach der Regel der Charakter-Seite (20°, Hülle × 1,08).`
                : `${foto.name} · Kamera der Fotos unbekannt: gerendert mit 20° auf die Hülle der Figur — zum Ansehen, keine Messung.`;
        }
        await this._karte(ansicht, box, rahmen, lauf);
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
            spalte.className = 'ai2d3d-vergleichsspalte';
            const titel = spalte.appendChild(document.createElement('figcaption'));
            const reihe = spalte.appendChild(document.createElement('div'));
            reihe.className = 'ai2d3d-vergleichsbilder';
            const bild = await this.fotos.bild(foto.nr).catch(f => { titel.textContent = f.message; return null; });
            if (lauf !== this._lauf) return;
            const [b, h] = this.daten.kamera ? Ai2d3dergebnis.KLEIN : [Ai2d3dergebnis.KLEIN[0], Math.round(Ai2d3dergebnis.KLEIN[0] * (bild ? bild.naturalHeight / bild.naturalWidth : 4 / 3))];
            const rendering = document.createElement('canvas');
            Ai2d3dvergleich.rendern(ansicht, box, foto.winkel, rahmen, rendering, b, h, this.regel);
            if (bild) reihe.append(Object.assign(bild.cloneNode(), { className: 'ai2d3d-vergleichsbild', alt: foto.name }));
            reihe.append(rendering);
            if (this.daten.kamera && bild) {
                const maske = document.createElement('canvas');
                Ai2d3dvergleich.rendern(ansicht, box, foto.winkel, rahmen, maske, b, h, this.regel, Ai2d3dvergleich.SCHLUESSEL);
                const ueber = reihe.appendChild(document.createElement('canvas'));
                const m = Ai2d3dvergleich.messen(bild, rendering, maske, ueber, this.regel.grund);
                titel.textContent = `${foto.name} (${foto.winkel}°) · ${Ai2d3dvergleich.text(m)}`;
                zeilen.push(m);
            } else {
                titel.textContent = `${foto.name} (${foto.winkel}°) · Kamera unbekannt, keine Zahl`;
            }
            spalten.push(spalte);
        }
        if (lauf !== this._lauf) return;
        const summe = document.createElement('p');
        summe.className = 'ai2d3d-vergleichssumme';
        if (zeilen.length) {
            const deckung = zeilen.reduce((s, m) => s + m.deckung, 0) / zeilen.length;
            summe.textContent = `Mittel über ${zeilen.length} Perspektiven: Umriss-Deckung ${p.format(deckung * 100)} % — grau: beide, rot: nur im Foto, türkis: nur im Rendering.`;
        } else {
            summe.textContent = spalten.length ? 'Kamera der Fotos unbekannt: Renderings zum Ansehen, keine Zahlen.' : 'Kein Foto mit bekanntem Winkel.';
        }
        this.karte.replaceChildren(summe, ...spalten);
    }
}
