/**
 * Blendermodellrundenbilder — die Bilder EINER Runde für die Unterzeile „Bilder" der Tabelle „Iterationen".
 *
 * Die Bilder tragen die Namen der 3D-Knöpfe über der Bühne (Edgar, 30.09.2026, viermal: „die Bilder bei den Iterationen sind
 * nicht dieselben wie im 3D View"): „Modell" ist das Modell aus Teilen mit den Farben der Vorlage (`je_ansicht[].textur`),
 * „Sichtmodell" der Sichtkörper mit Fototextur (`.sicht`) — beides sieht in der Bühne genauso aus. „Bewertung flach" ist der
 * Render mit flachen Farben (`.render`), nach dem benotet wird und den auch der Blender-Film zeigt; nur Runden ohne Modell haben
 * nichts anderes. Je Blickwinkel: Ziel (das Foto) · Modell · Sichtmodell · Bewertung flach.
 *
 * Bei der NEUESTEN Runde steht stattdessen Ziel · Bester · Aktuell (`vergleichen`; Edgar: „links das Ziel, mitte das beste
 * Ergebnis, rechts die aktuelle Iteration") — jeweils als Modell; hat die neueste Runde keines, das jüngste Modell (wie die
 * Bühne, beschriftet), erst ohne jedes Modell flach. `Kostuemabschluss` baut am Ende jedes Laufs das der neuesten Runde.
 * Die Leiste über den Kacheln (`leiste`) zeigt das Modell dieser Runde in der Bühne. Ein Klick auf eine Kachel öffnet sie groß
 * (`Blendermodellbildfenster`, ←/→ blättern). Auf- und Zuklappen macht die Tabelle (`Blendermodellrundentabelle`).
 */
export class Blendermodellrundenbilder {

    /** @param datei Adresse einer Datei aus `iterationen/`, @param foto Adresse eines Fotos der Bildauswahl,
     *  @param fenster `Blendermodellbildfenster` */
    constructor(datei, foto, fenster) {
        this.datei = datei;
        this.foto = foto;
        this.fenster = fenster;
        this.vergleich = { neueste: null, beste: null };
        /** (runde, art) → zeigt das Modell der Runde in der Bühne; `Blendermodelliterationen` setzt es. */
        this.dreid = null;
    }

    /** Für die NEUESTE Runde zeigt jeder Blickwinkel Ziel · Bester · Aktuell. `beste`: der Eintrag der besten Runde,
     *  `juengstes`: der jüngste Eintrag MIT Modell (das zeigt auch die Bühne) — Ersatz, wenn die neueste Runde keines hat. */
    vergleichen(neueste, beste, juengstes = null) {
        this.vergleich = { neueste, beste, juengstes };
    }

    /** Die neueste Runde als Bild: ihr Modell. Hat sie keines (verworfener Vorschlag der Prüf-KI, Lauf angehalten), das der
     *  jüngsten Runde mit Modell — beschriftet — statt eines flachen Renders, der neben dem texturierten Bild wie eine alte
     *  Runde aussieht (Edgar, 30.09.2026). Ohne jedes Modell: flach. */
    _aktuell(r, a, w) {
        const j = this.vergleich.juengstes;
        const ersatz = a.textur || !j ? null : (j.je_ansicht || []).find(x => x.original === a.original && x.textur);
        if (!ersatz) return this._bild(r.runde, a, w, 'Aktuell');
        return { src: this.datei(ersatz.textur),
                 titel: `Aktuell: Runde ${r.runde} hat kein Modell, jüngstes Modell (Runde ${j.runde}) ${w}` };
    }

    /** Die Ansicht der besten Runde im selben Blickwinkel (gleiches Foto) — nur für die neueste Runde, sonst null. */
    _bester(r, a) {
        const { neueste, beste } = this.vergleich;
        if (!beste || r.runde !== neueste) return null;
        return (beste.je_ansicht || []).find(x => x.original === a.original && x.render) || null;
    }

    static winkelText(grad) {
        const w = Math.round(grad);
        return `${w > 0 ? '+' : ''}${w}°`;
    }

    /** Das Bild einer Runde und Ansicht: das Modell, wo die Runde eines hat, sonst der flache Render (dann beschriftet). */
    _bild(runde, a, w, rolle = '') {
        const kopf = rolle ? `${rolle} (Runde ${runde}) ` : '';
        if (a.textur) return { src: this.datei(a.textur), titel: `${kopf}Modell ${w}` };
        return { src: this.datei(a.render), titel: `${kopf}flach, ohne Modell ${w}` };
    }

    /** [{titel, bilder: [{src, titel}], winkel}] — erst die Blickwinkel, dann Tafel bzw. Kachel. */
    gruppen(r) {
        const aus = [];
        const zahl = v => Number(v).toLocaleString('de-DE', { maximumFractionDigits: 2 });
        for (const a of r.je_ansicht || []) {
            if (!a.render) continue;
            const w = Blendermodellrundenbilder.winkelText(a.winkel);
            const bester = this._bester(r, a);
            const bilder = [{ src: this.foto(a.original), titel: `Ziel ${a.original}` }];
            let titel = `Runde ${r.runde} · ${w} · IoU ${zahl(a.iou)}, Farbe ${zahl(a.farbe)}`;
            if (bester) {
                const nr = this.vergleich.beste.runde;
                bilder.push(this._bild(nr, bester, w, 'Bester'), this._aktuell(r, a, w));
                titel += ` · Bester (Runde ${nr}): IoU ${zahl(bester.iou)}, Farbe ${zahl(bester.farbe)}`;
            } else {
                if (a.textur) bilder.push({ src: this.datei(a.textur), titel: `Modell ${w}` });
                if (a.sicht) bilder.push({ src: this.datei(a.sicht), titel: `Sichtmodell ${w}` });
                const modell = a.textur || a.sicht;
                bilder.push({ src: this.datei(a.render), titel: modell ? `Bewertung flach ${w}` : `flach, ohne Modell ${w}` });
            }
            aus.push({ titel, winkel: Math.round(a.winkel), bilder });
        }
        const d = r.dateien || {};
        if (d.vergleich) {
            aus.push({ titel: `Runde ${r.runde} · Tafel (oben Vorlage, unten flacher Render — so wird benotet)`,
                       bilder: [{ src: this.datei(d.vergleich), titel: 'Vergleichstafel' }] });
        }
        if (d.ansichten) {
            aus.push({ titel: `Runde ${r.runde} · vorn, rechts, hinten, links`,
                       bilder: [{ src: this.datei(d.ansichten), titel: 'Ansichten' }] });
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

    /** Die Leiste „In 3D zeigen" oder null: Knöpfe für die Modelle, die diese Runde hat; ohne Modell ein Hinweis. */
    leiste(r) {
        const d = r.dateien || {};
        const leiste = document.createElement('div');
        leiste.className = 'blendermodell-rundenbilder-leiste';
        const arten = [['modell', 'Modell', 'fa-hat-wizard'], ['sicht', 'Sichtmodell', 'fa-camera']];
        for (const [art, name, icon] of arten) {
            if (!d[art] || !this.dreid) continue;
            const knopf = document.createElement('button');
            knopf.type = 'button';
            knopf.className = 'btn btn-secondary btn-sm';
            knopf.title = `${name} der Runde ${r.runde} in der Bühne zeigen`;
            knopf.innerHTML = `<i class="fas ${icon}"></i> ${name} in 3D`;
            knopf.addEventListener('click', () => this.dreid(r.runde, art));
            leiste.appendChild(knopf);
        }
        if (!leiste.childElementCount) {
            const hinweis = document.createElement('span');
            hinweis.className = 'hb-hinweis';
            hinweis.textContent = `Runde ${r.runde} hat kein Modell — nur der flache Render (ein Modell entsteht für übernommene Runden, `
                + 'höchstens alle 45 s). Die Bühne zeigt das jüngste Modell.';
            leiste.appendChild(hinweis);
        }
        return leiste;
    }

    /** Das Raster der Kacheln oder null (Runde ohne Bilder). */
    raster(r) {
        const gruppen = this.gruppen(r);
        if (!gruppen.length) return null;
        const raster = document.createElement('div');
        raster.className = 'blendermodell-rundenbilder-raster';
        gruppen.forEach((g, i) => raster.appendChild(this._kachel(g, () => this.fenster.oeffnen(gruppen, i))));
        return raster;
    }

    _kachel(g, oeffnen) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'blendermodell-rundenbild' + (g.bilder.length > 1 ? '' : ' blendermodell-rundenbild-breit');
        knopf.title = `${g.titel} — groß ansehen`;
        const reihe = document.createElement('span');
        reihe.className = 'blendermodell-rundenbild-reihe';
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
