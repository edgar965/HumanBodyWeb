/**
 * Mesh3dhaut — die Karte „Haut und Augen“ (Schritte „Haut“, „Augen“) der Jobseite „Mesh-3D“ (11.10.2026).
 *
 * Abstand der Figur zum Original (in Ruhelage), Deckung und geglättete Normalen je Kachel. Die Kacheln selbst sind bis 8192 × 8192 px groß — sie
 * stehen als Verweise da, nicht als Bilder; das Augenbild (klein) wird gezeigt.
 */
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3dhaut {
    static KACHEL = { 1001: 'Kopf', 1002: 'Rumpf', 1003: 'Beine', 1004: 'Arme', 1005: 'Nägel' };

    constructor() {
        this.zahlen = document.getElementById('haut-zahlen');
        this.bilder = document.getElementById('haut-bilder');
        this._stand = '';
    }

    zeigen(z) {
        if (!Mesh3danzeige.geaendert(this, '_stand', [z.haut, z.augen])) return;
        const h = z.haut, a = z.augen;
        const d = h?.abstand || {};
        Mesh3danzeige.zeilen(this.zahlen, [
            h ? `Abstand Original → Figurfläche (Ruhelage): Median ${Mesh3danzeige.zahl(d.median_mm, 2)} mm, p95 ${Mesh3danzeige.zahl(d.p95_mm, 1)} mm, RMS ${Mesh3danzeige.zahl(d.rms_mm, 1)} mm, `
                + `über 8 mm: ${Mesh3danzeige.zahl((d.ueber_8mm || 0) * 100, 1)} %.` : 'Haut: noch nicht gebacken.',
            a ? (a.art === 'original' ? 'Augen: Originalbild übertragen.' : 'Augen: das Bild von „Mesh to 3D“ (Genesis-Augen).') : null,
        ]);
        this.bilder.replaceChildren();
        const kacheln = document.createElement('div');
        const augen = document.createElement('div');
        this.bilder.append(kacheln, augen);
        this._kacheln(kacheln, h);
        Mesh3danzeige.bilder(augen, a?.bild ? [{ adresse: a.bild, titel: 'Augenbild' }] : []);
    }

    _kacheln(ziel, h) {
        if (!h || !h.kacheln.length) return;
        Mesh3danzeige.tabelle(ziel, [{ titel: 'Kachel' }, { titel: 'Teil' }, { titel: 'Deckung %', num: true }, { titel: 'Normalen geglättet %', num: true }, { titel: 'Datei' }],
            h.kacheln.map(k => [k.nummer, Mesh3dhaut.KACHEL[k.nummer] || '', Mesh3danzeige.zahl((h.deckung || {})[k.nummer], 1), Mesh3danzeige.zahl((h.normalen_flach || {})[k.nummer], 1), '']));
        h.kacheln.forEach((k, i) => {
            const zelle = ziel.querySelectorAll('tbody tr')[i]?.cells[4];
            if (!zelle || !k.farbe) return;
            const verweis = document.createElement('a');
            verweis.href = k.farbe;
            verweis.target = '_blank';
            verweis.textContent = 'Farbkachel öffnen';
            zelle.replaceChildren(verweis);
        });
    }
}
