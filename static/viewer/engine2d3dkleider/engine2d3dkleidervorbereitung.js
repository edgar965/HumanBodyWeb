/**
 * Engine2d3dKleidervorbereitung — der Schritt „Vorbereitung" auf der Auftragsseite von „2D3D Kleider" (03.10.2026).
 *
 * Edgar: „einen ersten Vorschritt mit Hintergrund entfernen und diesen Skalierungen. Dieser Schritt ist getrennt startbar. Zeige die Bilder nach dem
 * Schritt unter den Originalbildern." Der Knopf rechnet NUR den Schritt (`ab = bis = vorbereitung`); darunter stehen die Bilder des letzten Laufs (Vorschau
 * aus `vorbereitet/vorschau_<stamm>.webp`, `zustand.vorbereitet`) mit Rolle, Größe und dem Befund der Ausrichtung. Ist die Ablage veraltet (ein Foto ersetzt,
 * eine Option geändert), sagt eine Zeile es — gezeigt wird dann trotzdem, was da ist, aber nicht als aktueller Stand.
 *
 * Die Option „Körper senkrecht stellen" baut `Meshoptionenformular` aus der Gruppe `vorbereitung` (siehe `Engine2d3dKleiderseite.aufbauen`).
 */
export class Engine2d3dKleidervorbereitung {

    constructor(seite) {
        this.seite = seite;
        this.liste = document.getElementById('vorbereitete-fotos');
        this._stand = null;
        const zeile = document.getElementById('vorbereitung-zeile');
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.id = 'vorbereitung-starten';
        this.knopf.className = 'btn btn-primary btn-sm';
        this.knopf.title = 'Rechnet nur den Schritt „Vorbereitung“ (Hintergrund entfernen, Zuschnitt, Licht, auf Wunsch senkrecht stellen). Das Netz und die übrigen Schritte starten getrennt.';
        this.knopf.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> <span>Vorbereitung starten</span>';
        this.knopf.addEventListener('click', () => seite.starten('vorbereitung', 'vorbereitung', this.knopf));
        this.hinweis = document.createElement('span');
        this.hinweis.className = 'hb-hinweis';
        zeile.append(this.knopf, this.hinweis);
    }

    zeigen(z) {
        this.knopf.disabled = !!z.laeuft;
        this.knopf.querySelector('span').textContent = z.laeuft && z.schritt === 'vorbereitung' ? 'Berechnet …' : 'Vorbereitung starten';
        const v = z.vorbereitet;
        const stand = JSON.stringify(v);
        if (stand === this._stand) return;
        this._stand = stand;
        this.liste.innerHTML = '';
        if (!v || !v.bilder.length) {
            this.hinweis.textContent = 'Noch nicht gerechnet.';
            return;
        }
        const wann = v.stand ? new Date(v.stand).toLocaleString('de-DE') : '';
        this.hinweis.textContent = v.veraltet
            ? `Stand ${wann} — passt nicht mehr zu den Fotos oder Optionen (${v.grund}); „Vorbereitung starten“ rechnet neu.`
            : `Stand ${wann}.`;
        this.hinweis.classList.toggle('hb-schlecht', !!v.veraltet);
        for (const bild of v.bilder) this.liste.appendChild(this._karte(bild, v));
    }

    _karte(bild, v) {
        const karte = document.createElement('div');
        karte.className = 'mesh-fotokarte engine2d3dkleider-vorbereitet-karte' + (v.veraltet ? ' engine2d3dkleider-vorbereitet-veraltet' : '');
        const bildfeld = document.createElement('img');
        bildfeld.className = 'mesh-vorschau engine2d3dkleider-vorbereitet-bild';
        bildfeld.loading = 'lazy';
        bildfeld.alt = bild.datei;
        bildfeld.title = `${bild.datei} — ${bild.breite} × ${bild.hoehe} px`;
        bildfeld.src = `${this.seite.dateiAdresse('vorbereitet', bild.vorschau)}?v=${encodeURIComponent(v.stand || '')}`;
        const text = document.createElement('div');
        text.className = 'hb-hinweis';
        text.textContent = `${bild.rolle || ''} · ${bild.breite} px · ${Engine2d3dKleidervorbereitung.ausrichtung(bild.ausrichtung)}`;
        karte.append(bildfeld, text);
        return karte;
    }

    /** Der Befund der Ausrichtung als Satzteil: gedreht von … auf …, nicht gedreht (Grund) oder „nicht ausgerichtet". */
    static ausrichtung(a) {
        if (!a) return 'nicht ausgerichtet';
        if (a.grad === null || a.grad === undefined) return a.grund || 'ohne Silhouette';
        const grad = (x) => `${x > 0 ? '+' : ''}${Number(x).toFixed(1)}°`;
        const linie = a.linie === 'Mittelachse' ? 'Mitte' : 'Achse';
        const dreh = a.gedreht ? `${linie} ${grad(a.grad)} → ${grad(a.nachher ?? 0)}` : `${linie} ${grad(a.grad)} (nicht gedreht)`;
        // Mittelachse: Kopf, Rumpf und Hüfte waagerecht auf eine Achse geschoben — Abstand der drei Mitten vorher → nachher, in % der Höhe
        const geschoben = a.versatz && a.streuung_nachher !== null && a.streuung_nachher !== undefined
            ? ` · auf eine Achse geschoben (${a.streuung} % → ${a.streuung_nachher} % der Höhe)` : '';
        return dreh + geschoben;
    }
}
