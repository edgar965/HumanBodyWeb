/**
 * Meshfigurberichte — die Zahlen und Bilder eines Auftrags „Mesh to 3D" auf der Seite.
 *
 * Alles kommt aus `zustand.ergebnis` (gemessen im Lauf, nichts geschätzt): Kennzahlen (Abstand
 * Figur ↔ Netz, Höhe, Eigenmorph, Testfall), das Vergleichsbild, je Kette die Stufen mit ihren
 * Abständen, die gestellten Regler und die Übersichtsbilder der Erkennung. Neu gezeichnet wird nur,
 * wenn sich das Ergebnis geändert hat.
 */
export class Meshfigurberichte {

    static TEILE = ['Kopf', 'Hals', 'Rumpf', 'Becken', 'Schulter l', 'Oberarm l', 'Unterarm l', 'Hand l', 'Schulter r',
        'Oberarm r', 'Unterarm r', 'Hand r', 'Oberschenkel l', 'Unterschenkel l', 'Fuß l', 'Oberschenkel r',
        'Unterschenkel r', 'Fuß r', 'Auge'];

    constructor(seite) {
        this.seite = seite;
        this._stand = null;
    }

    static mm(wert) { return wert === null || wert === undefined ? '–' : `${Number(wert).toFixed(1).replace('.', ',')} mm`; }

    zeigen(z) {
        const stand = JSON.stringify([z.ergebnis, z.status]);
        if (stand === this._stand) return;
        this._stand = stand;
        const e = z.ergebnis || {};
        this.kennzahlen(e, z);
        this.vergleich(e);
        this.ketten(e);
        this.regler(e);
        this.erkennung(e);
    }

    _dl(zeilen) {
        const dl = document.getElementById('kennzahlen');
        dl.innerHTML = '';
        for (const [titel, wert, hinweis] of zeilen) {
            const dt = document.createElement('dt');
            dt.textContent = titel;
            const dd = document.createElement('dd');
            dd.textContent = wert;
            if (hinweis) dd.title = hinweis;
            dl.append(dt, dd);
        }
    }

    kennzahlen(e, z) {
        const a = (e.vorschau || {}).abstand || {};
        const zeilen = [
            ['Figur → Netz', Meshfigurberichte.mm(a.figur_netz_rms_mm), 'RMS über die Hautpunkte der Figur, p95 ' + Meshfigurberichte.mm(a.figur_netz_p95_mm)],
            ['Netz → Figur', Meshfigurberichte.mm(a.netz_figur_rms_mm), 'RMS über die Hautproben des Netzes, p95 ' + Meshfigurberichte.mm(a.netz_figur_p95_mm)],
            ['Größe', (e.vorschau || {}).hoehe_cm ? `${String(e.vorschau.hoehe_cm).replace('.', ',')} cm` : '–', 'Scheitel, ohne Haar'],
            ['Regler gestellt', String(((e.regler || {}).geaendert || []).length)],
            ['Eigenmorph', (e.rest || {}).regler ? `${Meshfigurberichte.mm(e.rest.rest_rms_mm)} Rest` : ((e.rest || {}).aus ? 'aus' : '–')],
            ['Modell', z.modell || '–', 'gespeichert unter HumanBody/data/models'],
            ['Ablage', ((e.gespeichert || {}).ablage || {}).ordner || '–'],
        ];
        const t = e.testfall;
        if (t && !t.fehler) {
            zeilen.push([`Testfall ${t.anzeige}${t.blind ? ' (blind)' : ''}`, `${Meshfigurberichte.mm(t.flaeche_ausgerichtet_mm)} Fläche`,
                `Punkt für Punkt ${Meshfigurberichte.mm(t.punkt_ausgerichtet_mm)} nach Procrustes (Maßstab ${t.procrustes_massstab}); ` +
                `nur Regler ${Meshfigurberichte.mm(t.nur_regler_flaeche_mm)}; Grundfigur ${Meshfigurberichte.mm(t.grundfigur_flaeche_mm)}; ` +
                `Höhe ${t.hoehe_cm.modell} / ${t.hoehe_cm.referenz} cm`]);
        }
        this._dl(zeilen);
    }

    _bild(ordner, name, klasse) {
        const bild = document.createElement('img');
        bild.className = klasse;
        bild.loading = 'lazy';
        bild.src = `${this.seite.dateiAdresse(ordner, name)}?t=${encodeURIComponent(this.seite.zustand.updated_at || '')}`;
        return bild;
    }

    vergleich(e) {
        const feld = document.getElementById('vergleich');
        feld.innerHTML = '';
        const name = ((e.vorschau || {}).dateien || {}).vergleich;
        if (!name) { feld.textContent = 'Noch kein Vergleich — kommt im Schritt „Vorschau".'; return; }
        feld.appendChild(this._bild('ergebnis', name, 'meshfigur-vergleichsbild'));
    }

    ketten(e) {
        const feld = document.getElementById('ketten');
        feld.innerHTML = '';
        const tabelle = document.createElement('table');
        tabelle.className = 'doku meshfigur-kettentabelle';
        tabelle.innerHTML = '<thead><tr><th>Kette</th><th>Stufe</th><th>Regler frei</th><th>Figur → Netz</th>'
            + '<th>Netz → Figur</th><th>Sekunden</th></tr></thead>';
        const koerper = ((e.koerper || {}).runden || []).flatMap(r => (r.verlauf || []).map(v => [`Körper, Runde ${r.runde}`, v]));
        const gesicht = ((e.gesicht || {}).verlauf || []).map(v => ['Gesicht', v]);
        const rumpf = document.createElement('tbody');
        for (const [kette, v] of [...koerper, ...gesicht]) {
            const zeile = document.createElement('tr');
            for (const wert of [kette, v.stufe, v.regler_frei, Meshfigurberichte.mm(v.figur_netz_rms_mm),
                Meshfigurberichte.mm(v.netz_figur_rms_mm), v.sekunden]) {
                const zelle = document.createElement('td');
                zelle.textContent = wert ?? '–';
                zeile.appendChild(zelle);
            }
            rumpf.appendChild(zeile);
        }
        tabelle.appendChild(rumpf);
        if (!rumpf.children.length) { feld.textContent = 'Noch keine Kette gerechnet.'; return; }
        feld.appendChild(tabelle);
        const letzte = [...koerper, ...gesicht].pop();
        if (letzte && letzte[1].je_teil_mm) {
            const teile = document.createElement('p');
            teile.className = 'hb-hinweis';
            teile.textContent = 'Figur → Netz je Körperteil: ' + Object.entries(letzte[1].je_teil_mm)
                .map(([k, w]) => `${Meshfigurberichte.TEILE[Number(k)] || k} ${Meshfigurberichte.mm(w)}`).join(' · ');
            feld.appendChild(teile);
        }
    }

    regler(e) {
        const feld = document.getElementById('regler');
        feld.innerHTML = '';
        const liste = (e.regler || {}).geaendert || [];
        if (!liste.length) { feld.textContent = 'Noch keine Regler gestellt.'; return; }
        const raster = document.createElement('div');
        raster.className = 'meshfigur-reglerraster';
        for (const [name, wert] of liste) {
            const zeile = document.createElement('div');
            zeile.className = 'meshfigur-reglerzeile';
            const balken = document.createElement('span');
            balken.className = `meshfigur-reglerbalken ${wert < 0 ? 'negativ' : ''}`;
            balken.style.width = `${Math.min(100, Math.abs(wert) * 50)}%`;
            const text = document.createElement('span');
            text.className = 'meshfigur-reglertext';
            text.textContent = `${name.replace(/-0x[0-9a-f]+$/, '')}  ${wert.toFixed(3).replace('.', ',')}`;
            zeile.append(balken, text);
            raster.appendChild(zeile);
        }
        feld.appendChild(raster);
    }

    erkennung(e) {
        const feld = document.getElementById('erkennung');
        feld.innerHTML = '';
        const k = e.erkennung || {};
        if (!k.bilder) { feld.textContent = 'Noch keine Erkennung.'; return; }
        const text = document.createElement('p');
        text.className = 'hb-hinweis';
        text.textContent = `Körper ${k.koerper_punkte} Punkte (Fehler ${k.koerper_fehler_px} px), Gesicht ${k.gesicht_punkte} Punkte`
            + ` (${k.gesicht_fehler_px} px); vorn bei ${(k.ausrichtung || {}).azimut}°, nachgedreht ${k.feinausrichtung_grad}°`
            + `; Einheit ${(k.einheit || {}).grund}${k.skalierung ? `; auf ${k.skalierung.ziel_cm} cm gestreckt (× ${k.skalierung.faktor})` : ''}.`;
        feld.appendChild(text);
        for (const name of Object.values(k.bilder)) feld.appendChild(this._bild('ergebnis', name, 'meshfigur-erkennungsbild'));
    }
}
