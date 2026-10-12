/**
 * Engine2d3dKleiderpose — die Karte „Pose" auf der Auftragsseite von „2D3D Kleider" (11.10.2026).
 *
 * Edgar (11.10.2026), nach den Proben am Gemälde „Modigliani": „baue das in die Job Pipeline hinein, als extra Schritt, wo man auch das Ergebnis sehen kann." Das Häkchen (`pose.rechnen`), die Drehung,
 * die Gelenke zum Weglassen und den Maßstab baut `Meshoptionenformular` aus der Gruppe `pose` (siehe `Engine2d3dKleiderseite.aufbauen`); dieser Baustein bringt den Knopf „Pose rechnen" (nur den Schritt:
 * `ab = bis = pose`) und zeigt aus `zustand.pose`, was der Schritt gefunden hat — die vier Drehungen mit den Gelenken (die gewählte gerahmt), das Netz von vorn und von der Seite mit den Landmarken,
 * die Zahlen (Drehung, Gelenke, Silhouetten-IoU, Maßstab) und die Tabelle der Gelenke.
 */
export class Engine2d3dKleiderpose {

    static DREHUNGEN = [0, 90, 180, 270];
    static STAND = { innen: 'im Netz', ausserhalb: 'auf das Netz gezogen', weggelassen: 'weggelassen' };

    constructor(seite) {
        this.seite = seite;
        this.fotos = document.getElementById('pose-fotos');
        this.netz = document.getElementById('pose-netz');
        this.zahlen = document.getElementById('pose-zahlen');
        this.gelenke = document.getElementById('pose-gelenke');
        this._stand = null;
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.id = 'pose-starten';
        this.knopf.className = 'btn btn-primary btn-sm';
        this.knopf.title = 'Rechnet nur den Schritt „Pose“: die Gelenke am Foto „vorne“ finden (SAM 3D Body), ins Netz legen und den Maßstab ableiten — auch bei ausgeschaltetem Häkchen.';
        this.knopf.innerHTML = '<i class="fas fa-person"></i> <span>Pose rechnen</span>';
        this.knopf.addEventListener('click', () => seite.starten('pose', 'pose', this.knopf));
        this.hinweis = document.createElement('span');
        this.hinweis.className = 'hb-hinweis';
        document.getElementById('pose-zeile').append(this.knopf, this.hinweis);
    }

    zeigen(z) {
        this.knopf.disabled = !!z.laeuft;
        this.knopf.querySelector('span').textContent = z.laeuft && z.schritt === 'pose' ? 'Berechnet …' : 'Pose rechnen';
        const p = z.pose;
        const an = ((z.optionen || {}).pose || {}).rechnen === 'an';
        const stand = JSON.stringify([p, an]);
        if (stand === this._stand) return;
        this._stand = stand;
        for (const feld of [this.fotos, this.netz, this.zahlen, this.gelenke]) feld.innerHTML = '';
        if (!p) {
            this.hinweis.textContent = an
                ? 'Noch nicht gerechnet — die Körper-Kette bricht ab, bis „Pose rechnen“ gelaufen ist.'
                : 'Häkchen aus — der Schritt entfällt im vollen Lauf; „Pose rechnen“ läuft ihn trotzdem.';
            return;
        }
        const wann = p.stand ? new Date(p.stand).toLocaleString('de-DE') : '';
        this.hinweis.textContent = p.veraltet
            ? `Stand ${wann} — ${p.grund}; „Pose rechnen“ rechnet neu.${an ? ' Die Körper-Kette bricht so ab.' : ''}`
            : `Stand ${wann}.${p.eingesetzt ? ' Die Körper-Kette nimmt Landmarken und Maßstab.' : ' Häkchen aus — die Körper-Kette nimmt sie nicht.'}`;
        this.hinweis.classList.toggle('hb-schlecht', !!p.veraltet);
        for (const grad of Engine2d3dKleiderpose.DREHUNGEN) {
            const datei = p.bilder[`skelett_${grad}`];
            if (datei) this.fotos.appendChild(this._karte(p, grad, datei));
        }
        if (p.bilder.netz) this._netzbild(p);
        this._zahlen(p);
        this._tabelle(p);
    }

    _adresse(p, datei) {
        return `${this.seite.dateiAdresse('pose', datei)}?v=${encodeURIComponent(p.stand || '')}`;
    }

    _karte(p, grad, datei) {
        const gewaehlt = grad === p.drehung;
        const karte = document.createElement('div');
        karte.className = 'mesh-fotokarte engine2d3dkleider-vorbereitet-karte' + (gewaehlt ? ' engine2d3dkleider-pose-gewaehlt' : '') + (p.veraltet ? ' engine2d3dkleider-vorbereitet-veraltet' : '');
        const bild = document.createElement('img');
        bild.className = 'mesh-vorschau engine2d3dkleider-pose-bild';
        bild.loading = 'lazy';
        bild.alt = `Drehung ${grad}°`;
        bild.title = `SAM 3D Body am Foto, ${grad}° gegen den Uhrzeigersinn gedreht${gewaehlt ? ' — diese Drehung liefert die Landmarken' : ''}`;
        bild.src = this._adresse(p, datei);
        const text = document.createElement('div');
        text.className = 'hb-hinweis';
        text.textContent = gewaehlt ? `${grad}° — gewählt` : `${grad}°`;
        karte.append(bild, text);
        return karte;
    }

    _netzbild(p) {
        const bild = document.createElement('img');
        bild.alt = 'Netz von vorn und von der Seite mit den Landmarken';
        bild.title = 'Grün: Gelenk im Netz · orange: außerhalb des Netzes, auf die nächsten Netzpunkte gezogen';
        bild.loading = 'lazy';
        bild.src = this._adresse(p, p.bilder.netz);
        this.netz.appendChild(bild);
    }

    _zahl(text) {
        const zeile = document.createElement('div');
        zeile.className = 'hb-hinweis';
        zeile.textContent = text;
        this.zahlen.appendChild(zeile);
    }

    _zahlen(p) {
        const g = p.gelenke || {};
        const kom = (x, n = 2) => Number(x).toLocaleString('de-DE', { maximumFractionDigits: n });
        const f = p.foto || {};
        this._zahl(`Foto ${f.datei} (${f.breite} × ${f.hoehe} px): Person ${kom(f.seitenverhaeltnis)}-mal so breit wie hoch${f.liegt ? ' — sie LIEGT im Bild, eine Drehung von 90° oder 270° stellt sie auf' : ''}.`);
        this._zahl(`Gewählt: ${p.drehung}°. ${g.gesetzt} Gelenke im Netz (davon ${g.haupt_gesetzt} der 12 Hauptgelenke)${g.weggelassen?.length ? `, weggelassen: ${g.weggelassen.length}` : ''}${g.ausserhalb?.length ? `, auf das Netz gezogen: ${g.ausserhalb.length}` : ''}.`);
        const a = p.abbildung || {};
        this._zahl(`Netz ↔ Foto: Silhouetten-IoU ${kom(a.iou, 3)} (Lage ${a.variante}); ${kom((a.pixel_je_einheit || [0])[0], 1)} px je Netzeinheit waagerecht, ${kom((a.pixel_je_einheit || [0, 0])[1], 1)} senkrecht.`);
        const m = p.masstab;
        if (m) {
            this._zahl(`Maßstab: ${kom(m.faktor, 4)} m je Netzeinheit (SAM 3D Body: ${kom(m.abstand_m)} m Abstand, ${kom(m.meter_je_pixel * 1000, 2)} mm je Bildpixel); die längste Achse des Netzes misst damit ${kom(m.laengste_achse_m)} m.`);
        } else {
            this._zahl('Maßstab: aus (Option) — die Körper-Kette wendet die Einheitenregel an.');
        }
        if (p.dauer_sam_s) this._zahl(`SAM 3D Body ${p.sam_neu_gerechnet ? 'gerechnet' : 'aus der Ablage (Foto unverändert)'}${p.sam_neu_gerechnet ? `: ${kom(p.dauer_sam_s, 1)} s` : ''}.`);
    }

    _tabelle(p) {
        const liste = (p.gelenke || {}).liste || [];
        if (!liste.length) return;
        const tabelle = document.createElement('table');
        tabelle.className = 'doku engine2d3dkleider-stuecketabelle engine2d3dkleider-pose-gelenke';
        const kopf = tabelle.createTHead().insertRow();
        for (const text of ['Gelenk', 'Stand', 'Foto x', 'Foto y', 'Netz x', 'Netz y', 'Netz z']) {
            const th = document.createElement('th');
            th.textContent = text;
            kopf.appendChild(th);
        }
        const koerper = tabelle.createTBody();
        for (const e of liste) {
            const zeile = koerper.insertRow();
            const n = e.netz || [];
            const werte = [e.text, Engine2d3dKleiderpose.STAND[e.stand] || e.stand, e.foto[0], e.foto[1], n[0], n[1], n[2]];
            for (const w of werte) zeile.insertCell().textContent = w === undefined ? '—' : (typeof w === 'number' ? w.toLocaleString('de-DE', { maximumFractionDigits: 3 }) : w);
        }
        this.gelenke.appendChild(tabelle);
    }
}
