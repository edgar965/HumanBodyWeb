/**
 * Engine2d3dKleiderrundenbilder — die Bilder EINER Runde für die Unterzeile „Bilder" der Tabelle „Iterationen".
 *
 * Je Blickwinkel ein Paar: das Foto der Vorlage und der Render des Modells (`je_ansicht[].render`), dazu die Vergleichstafel — die
 * Fläche, nach der benotet wird. Ein Klick öffnet das Bild groß (`Engine2d3dKleiderbildfenster`, Vorlage und Render nebeneinander, ←/→
 * blättern).
 *
 * Auf- und Zuklappen und was gemerkt wird, macht die Tabelle (`Engine2d3dKleiderrundentabelle`).
 */
export class Engine2d3dKleiderrundenbilder {

    /** @param datei Adresse einer Datei aus `iterationen/`, @param foto Adresse eines Fotos der Bildauswahl,
     *  @param fenster `Engine2d3dKleiderbildfenster` */
    constructor(datei, foto, fenster) {
        this.datei = datei;
        this.foto = foto;
        this.fenster = fenster;
    }

    static winkelText(grad) {
        const w = Math.round(grad);
        return `${w > 0 ? '+' : ''}${w}°`;
    }

    /** [{titel, bilder: [{src, titel}], winkel}] — erst die Blickwinkel, dann Tafel bzw. Kachel. */
    gruppen(r) {
        const aus = [];
        const zahl = v => v == null ? '—' : Number(v).toLocaleString('de-DE', { maximumFractionDigits: 2 });
        for (const a of r.je_ansicht || []) {
            if (!a.render) continue;
            const w = Engine2d3dKleiderrundenbilder.winkelText(a.winkel);
            const bilder = [{ src: this.foto(a.original), titel: `Vorlage ${a.original}` },
                            { src: this.datei(a.render), titel: `Render ${w}` }];
            aus.push({
                titel: `Runde ${r.runde} · ${w} · IoU ${zahl(a.iou)}, Farbe ${zahl(a.farbe)}`,
                winkel: Math.round(a.winkel),
                bilder,
            });
        }
        const d = r.dateien || {};
        if (d.vergleich) {
            aus.push({ titel: `Runde ${r.runde} · Tafel (oben Vorlage, unten Render${r.aufloesung
                ? `, Note auf ${r.aufloesung} px` : ''})`,
                       bilder: [{ src: this.datei(d.vergleich), titel: 'Vergleichstafel' }] });
        }
        if (d.kopf) {   // Kopf aus jedem Fotowinkel: Mund, Gesicht, Haardeckung (Prüfbilder, 02.10.2026)
            aus.push({ titel: `Runde ${r.runde} · Kopf (oben Foto, unten Render)`,
                       bilder: [{ src: this.datei(d.kopf), titel: 'Kopftafel' }] });
        }
        return aus;
    }

    /** Große Ansicht öffnen, bei Blickwinkel `winkel` (Grad; ohne: bei der ersten Gruppe). */
    oeffnen(r, winkel = null) {
        const gruppen = this.gruppen(r);
        if (!gruppen.length) return;
        const index = winkel === null ? 0 : Math.max(0, gruppen.findIndex(g => g.winkel === winkel));
        this.fenster.oeffnen(gruppen, index);
    }

    /** Das Raster der Kacheln oder null (Runde ohne Bilder). */
    raster(r) {
        const gruppen = this.gruppen(r);
        if (!gruppen.length) return null;
        const raster = document.createElement('div');
        raster.className = 'engine2d3dkleider-rundenbilder-raster';
        gruppen.forEach((g, i) => raster.appendChild(this._kachel(g, () => this.fenster.oeffnen(gruppen, i))));
        return raster;
    }

    _kachel(g, oeffnen) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'engine2d3dkleider-rundenbild' + (g.bilder.length > 1 ? '' : ' engine2d3dkleider-rundenbild-breit');
        knopf.title = `${g.titel} — groß ansehen`;
        const reihe = document.createElement('span');
        reihe.className = 'engine2d3dkleider-rundenbild-reihe';
        for (const b of g.bilder) {
            const bild = document.createElement('img');
            bild.src = b.src;
            bild.alt = b.titel;
            bild.loading = 'lazy';
            reihe.appendChild(bild);
        }
        const unter = document.createElement('span');
        unter.textContent = g.titel.replace(/^Runde \d+ · /, '');
        knopf.append(reihe, unter);
        knopf.addEventListener('click', oeffnen);
        return knopf;
    }
}
