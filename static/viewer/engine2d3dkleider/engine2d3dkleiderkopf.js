/**
 * Engine2d3dKleiderkopf — die Karte „Kopf" auf der Auftragsseite von „2D3D Kleider" (07.10.2026).
 *
 * Edgar: „mach einen extra Kopf lauf, extrahiere dazu die bilder vom Kopf, von alle drei seiten … extra UI. Per Check box (default an) anwählbar. wenn das ausgewählt ist, erstellst und
 * zeigst du die 3 Kopf Bilder im UI und rechnest den Kopf extra." Das Häkchen (`kopf.rechnen`) und die Wahl von Modell und Flächen baut `Meshoptionenformular` aus der Gruppe `kopf`
 * (siehe `Engine2d3dKleiderseite.aufbauen`); dieser Baustein bringt den Knopf „Kopf rechnen" (nur den Schritt: `ab = bis = kopf`) und zeigt aus `zustand.kopf`, was der Schritt gemacht hat —
 * die Kopfausschnitte (stehen schon, während Hunyuan3D rechnet) und danach das Kopfnetz mit seinem Icon.
 */
export class Engine2d3dKleiderkopf {

    constructor(seite) {
        this.seite = seite;
        this.liste = document.getElementById('kopf-fotos');
        this.netz = document.getElementById('kopf-netz');
        this._stand = null;
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.id = 'kopf-starten';
        this.knopf.className = 'btn btn-primary btn-sm';
        this.knopf.title = 'Rechnet nur den Schritt „Kopf“: den Kopf aus den drei vorbereiteten Fotos schneiden und daraus ein eigenes Kopfnetz rechnen — auch bei ausgeschaltetem Häkchen.';
        this.knopf.innerHTML = '<i class="fas fa-user"></i> <span>Kopf rechnen</span>';
        this.knopf.addEventListener('click', () => seite.starten('kopf', 'kopf', this.knopf));
        this.hinweis = document.createElement('span');
        this.hinweis.className = 'hb-hinweis';
        document.getElementById('kopf-zeile').append(this.knopf, this.hinweis);
    }

    zeigen(z) {
        this.knopf.disabled = !!z.laeuft;
        this.knopf.querySelector('span').textContent = z.laeuft && z.schritt === 'kopf' ? 'Berechnet …' : 'Kopf rechnen';
        const k = z.kopf;
        const an = ((z.optionen || {}).kopf || {}).rechnen !== 'aus';
        const stand = JSON.stringify([k, an]);
        if (stand === this._stand) return;
        this._stand = stand;
        this.liste.innerHTML = '';
        this.netz.innerHTML = '';
        if (!k || !k.bilder.length) {
            this.hinweis.textContent = an ? 'Noch nicht gerechnet.' : 'Häkchen aus — der Schritt entfällt im vollen Lauf; „Kopf rechnen“ läuft ihn trotzdem.';
            return;
        }
        const wann = k.stand ? new Date(k.stand).toLocaleString('de-DE') : '';
        this.hinweis.textContent = k.veraltet
            ? `Stand ${wann} — ${k.grund}; „Kopf rechnen“ rechnet neu.`
            : `Stand ${wann}.${an ? '' : ' Häkchen aus — die Körper-Kette nimmt das Kopfnetz nicht.'}`;
        this.hinweis.classList.toggle('hb-schlecht', !!k.veraltet);
        for (const bild of k.bilder) this.liste.appendChild(this._karte(bild, k));
        this._netz(k, an);
    }

    _karte(bild, k) {
        const karte = document.createElement('div');
        karte.className = 'mesh-fotokarte engine2d3dkleider-vorbereitet-karte' + (k.veraltet ? ' engine2d3dkleider-vorbereitet-veraltet' : '');
        const bildfeld = document.createElement('img');
        bildfeld.className = 'mesh-vorschau engine2d3dkleider-vorbereitet-bild';
        bildfeld.loading = 'lazy';
        bildfeld.alt = bild.datei;
        bildfeld.title = `${bild.datei} — aus ${bild.quelle}, ${bild.breite} × ${bild.hoehe} px`;
        bildfeld.src = `${this.seite.dateiAdresse('kopf', bild.datei)}?v=${encodeURIComponent(k.stand || '')}`;
        const text = document.createElement('div');
        text.className = 'hb-hinweis';
        text.textContent = `${bild.rolle} · ${bild.breite} × ${bild.hoehe} px · Kopf ${(100 * bild.kopf_anteil).toFixed(1).replace('.', ',')} % der Körperhöhe`;
        karte.append(bildfeld, text);
        return karte;
    }

    /** Das Kopfnetz: Icon und eine Zeile — oder der Hinweis, dass es noch rechnet bzw. nicht gerechnet ist. */
    _netz(k, an) {
        const text = document.createElement('div');
        text.className = 'hb-hinweis';
        const n = k.netz;
        if (!n) {
            text.textContent = this.seite.zustand.laeuft && this.seite.zustand.schritt === 'kopf'
                ? 'Kopfnetz wird gerechnet …' : 'Kein Kopfnetz — der Lauf ist nicht zu Ende gegangen.';
            this.netz.appendChild(text);
            return;
        }
        if (n.icon) {
            const icon = document.createElement('img');
            icon.className = 'engine2d3dkleider-kopfnetz-icon';
            icon.alt = 'Kopfnetz';
            icon.src = `${this.seite.dateiAdresse('kopf', n.icon)}?v=${encodeURIComponent(k.stand || '')}`;
            this.netz.appendChild(icon);
        }
        const flaechen = n.flaechen ? `${Number(n.flaechen).toLocaleString('de-DE')} Flächen` : 'Flächen unbekannt';
        const dauer = n.dauer_s ? `, ${Math.round(n.dauer_s)} s` : '';
        const eingesetzt = k.eingesetzt ? 'Die Körper-Kette setzt es ein.' : (an ? '' : 'Häkchen aus — die Körper-Kette setzt es nicht ein.');
        text.textContent = `Kopfnetz (${n.formmodell || 'Hunyuan3D'}, ${flaechen}${dauer}; Textur ${n.textur_quelle || 'unbekannt'}). ${eingesetzt} Wirkt auf das Gesicht erst, wenn „Körper“ neu rechnet.`;
        this.netz.appendChild(text);
    }
}
