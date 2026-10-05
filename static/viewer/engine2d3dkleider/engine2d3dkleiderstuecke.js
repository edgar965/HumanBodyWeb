/**
 * Engine2d3dKleiderstuecke — die Karte „Kleiderstücke" auf der Auftragsseite von „2D3D Kleider" (04.10.2026).
 *
 * Edgar: „die Kleider sind im 3D View noch nicht wegklickbar … vor den Iterationen" und „dafür fehlt mir eine Messgröße". Der Schritt `kleiderstuecke` baut Oberteil, Hose und Socken aus dem Netz der Fotos als eigene
 * Genesis-Stücke und misst sie (`Kleiderstuecknote`); die Bühne trägt sie danach schon vor Runde 1 („Kleider" schaltet sie). Der Knopf rechnet NUR diesen Schritt (`ab = bis = kleiderstuecke`; braucht „Körper"
 * und „Grundfigur"). Die Tabelle zeigt je Stück die Messung aus `zustand.kleiderstuecke`; die Zahlen erklärt ein Satz darunter — Maß und Maßstab stehen in `Kleiderstuecknote` / `Kleiderstueckmessung` (Server).
 */
export class Engine2d3dKleiderstuecke {

    static NAMEN = { oberteil: 'Oberteil', hose: 'Hose', socken: 'Socken' };

    constructor(seite) {
        this.seite = seite;
        this.tabelle = document.getElementById('kleiderstuecke-tabelle');
        this._stand = null;
        const zeile = document.getElementById('kleiderstuecke-zeile');
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.id = 'kleiderstuecke-starten';
        this.knopf.className = 'btn btn-primary btn-sm';
        this.knopf.title = 'Rechnet nur den Schritt „Kleiderstücke“ (Oberteil, Hose, Socken aus dem Netz bauen und messen). Braucht den Körper und die Grundfigur. Beim ersten Mal rund 2–3 Minuten; ' +
            'ein zweiter Lauf baut nur neu, wenn sich Netz, Maske oder Figur geändert haben.';
        this.knopf.innerHTML = '<i class="fas fa-shirt"></i> <span>Kleiderstücke bauen und messen</span>';
        this.knopf.addEventListener('click', () => seite.starten('kleiderstuecke', 'kleiderstuecke', this.knopf));
        this.hinweis = document.createElement('span');
        this.hinweis.className = 'hb-hinweis';
        zeile.append(this.knopf, this.hinweis);
    }

    zeigen(z) {
        this.knopf.disabled = !!z.laeuft;
        this.knopf.querySelector('span').textContent = z.laeuft && z.schritt === 'kleiderstuecke' ? 'Berechnet …' : 'Kleiderstücke bauen und messen';
        const k = z.kleiderstuecke;
        const stand = JSON.stringify(k);
        if (stand === this._stand) return;
        this._stand = stand;
        this.tabelle.innerHTML = '';
        if (!k) {
            this.hinweis.textContent = 'Noch nicht gerechnet.';
            return;
        }
        const namen = Object.keys(k.stuecke || {});
        if (!namen.length) {
            this.hinweis.textContent = `Keine Stücke: ${k.grund || 'unbekannt'}. Die Iterationen nehmen dann Bibliotheksstücke.`;
            this.hinweis.classList.add('hb-schlecht');
            return;
        }
        this.hinweis.classList.remove('hb-schlecht');
        const sek = k.sekunden || {};
        this.hinweis.textContent = `${namen.length} Stücke, Abweichung gesamt ${Engine2d3dKleiderstuecke.zahl(k.abweichung, 3)} (kleiner ist besser) — bauen ${Engine2d3dKleiderstuecke.zahl(sek.bauen, 1)} s (gemerkte Stücke: 0), messen ${Engine2d3dKleiderstuecke.zahl(sek.messen, 1)} s.`;
        this.tabelle.appendChild(this._tabelle(k, namen));
        const koerper = document.createElement('p');
        koerper.className = 'hb-hinweis';
        const h = k.koerper || {};
        koerper.textContent = h.haut_mm == null ? '' : `Körper der Figur gegen die nackte Haut des Netzes: Mittel ${Engine2d3dKleiderstuecke.zahl(h.haut_mm, 1)} mm, 95 % unter ${Engine2d3dKleiderstuecke.zahl(h.haut_p95_mm, 1)} mm, ` +
            `${Engine2d3dKleiderstuecke.prozent(h.deckung)} der Haut näher als ${k.nah_mm} mm.`;
        const erklaerung = document.createElement('p');
        erklaerung.className = 'hb-hinweis';
        erklaerung.textContent = `Deckung: Anteil der Stofffläche des Netzes (laut Maske), die näher als ${k.nah_mm} mm am Stück liegt — fehlt Stoff? Treue: Anteil des Stücks, der näher als ${k.nah_mm} mm am Stoff des Netzes liegt — ` +
            'hat das Stück Stoff, den das Foto nicht zeigt? Abweichung = 1 − F (F: harmonisches Mittel beider). Randschleifen: offene Ränder (Oberteil: Ausschnitt, Saum, zwei Ärmel = 4); eine zusätzliche wäre ein Loch. ' +
            'Bibliothek: dieselbe Messung für das Bibliotheksstück, das die Runden vor den Fotostücken anzogen. Sitz: Abstand des Stücks zur Haut der Figur (Median / 99 %).';
        this.tabelle.append(koerper, this._seitentiefe(k.seitentiefe), erklaerung);
    }

    /** Die Rumpftiefe gegen die Silhouette des Seitenfotos (`Seitentiefemessung`, 05.10.2026): „Hemd +12 mm im Mittel, bis +40 mm" — + = tiefer als das Foto. */
    _seitentiefe(t) {
        const p = document.createElement('p');
        p.className = 'hb-hinweis';
        if (!t) return p;
        if (t.grund) {
            p.textContent = `Rumpftiefe gegen das Seitenfoto: nicht gemessen (${t.grund}).`;
            return p;
        }
        const satz = (name, a) => a ? `${name} ${Engine2d3dKleiderstuecke.vorzeichen(a.mittel_mm)} mm im Mittel, bis ${Engine2d3dKleiderstuecke.vorzeichen(a.max_mm)} mm` : null;
        const teile = [satz('Hemd', t.abweichung_hemd), satz('Körper', t.abweichung_koerper), satz('Netz', t.abweichung_netz)].filter(Boolean);
        p.textContent = `Rumpftiefe gegen die Silhouette des Seitenfotos (Höhe ${t.band[0]}–${t.band[1]} der Größe; + = tiefer als das Foto): ${teile.join(' · ')}. Das Foto zeigt auch den hängenden Arm und hat Perspektive — ` +
            'es kann die Tiefe überschätzen, nicht unterschätzen; 0 heißt „nicht tiefer als das Foto“. Die Note oben misst gegen das Netz und sieht deshalb nicht, ob das Netz selbst zu tief ist.';
        return p;
    }

    static vorzeichen(v) {
        return v == null ? '–' : `${Number(v) > 0 ? '+' : ''}${Number(v).toLocaleString('de-DE', { maximumFractionDigits: 0 })}`;
    }

    _tabelle(k, namen) {
        const tabelle = document.createElement('table');
        tabelle.className = 'doku engine2d3dkleider-stuecketabelle';
        const kopf = ['Stück', 'Flächen', 'Deckung', 'Treue', 'Abweichung', 'Bibliothek', 'Inseln', 'Randschleifen', 'Sitz (Median / 99 %)'];
        const tr = tabelle.createTHead().insertRow();
        for (const titel of kopf) tr.appendChild(Object.assign(document.createElement('th'), { textContent: titel }));
        const rumpf = tabelle.createTBody();
        for (const name of namen) {
            const s = k.stuecke[name];
            const zeile = rumpf.insertRow();
            const bib = (k.bibliothek || {})[name];
            const werte = s.note ? [
                Engine2d3dKleiderstuecke.NAMEN[name] || name, s.aufbau.flaechen.toLocaleString('de-DE'), Engine2d3dKleiderstuecke.prozent(s.note.deckung), Engine2d3dKleiderstuecke.prozent(s.note.treue),
                Engine2d3dKleiderstuecke.zahl(s.note.abweichung, 3),
                bib ? `${Engine2d3dKleiderstuecke.zahl(bib.abweichung, 3)} (${bib.sorte})${bib.abweichung > s.note.abweichung ? ' — Fotostück besser' : ' — Fotostück NICHT besser'}` : '–',
                s.aufbau.inseln, s.aufbau.randschleifen,
                s.angezogen ? `${Engine2d3dKleiderstuecke.zahl(s.angezogen.median_mm, 1)} / ${Engine2d3dKleiderstuecke.zahl(s.angezogen.p99_mm, 1)} mm` : '–',
            ] : [Engine2d3dKleiderstuecke.NAMEN[name] || name, s.fehler || 'nicht gemessen', '', '', '', '', '', '', ''];
            for (const wert of werte) zeile.insertCell().textContent = wert;
        }
        return tabelle;
    }

    static prozent(v) {
        return v == null ? '–' : `${(Number(v) * 100).toFixed(0)} %`;
    }

    static zahl(v, stellen) {
        return v == null ? '–' : Number(v).toLocaleString('de-DE', { minimumFractionDigits: stellen, maximumFractionDigits: stellen });
    }
}
