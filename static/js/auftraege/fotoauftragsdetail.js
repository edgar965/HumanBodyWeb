/**
 * Fotoauftragsdetail — das Detailfenster einer Fotoanalyse: Foto, Ergebnis,
 * Silhouette, Textur und die drei Weiter-Knöpfe.
 *
 * Herausgeloest aus templates/photo_analysis_jobs.html (Umbau 16.08.2026):
 * `showDetailFromRow`, `setImgBox` und `closeDetail` — 40 Zeilen inline, in
 * denen zwölfmal `document.getElementById` stand und die Sichtbarkeit der drei
 * Bildkästen über `style.display` geregelt wurde.
 *
 * Alle Angaben kommen aus den `data-`Attributen der Zeile; die Adresse der
 * Zielseite wird EINMAL übergeben statt in jedem Knopf zusammengesetzt.
 */
export class Fotoauftragsdetail {

    /** Bildkästen: Kasten-Kennung, Bild-Kennung, Feld im data-Satz. */
    static BILDER = [
        ['detailResultBox', 'detailResult', 'result'],
        ['detailSilhouetteBox', 'detailSilhouette', 'silhouette'],
        ['detailTextureBox', 'detailTexture', 'texture'],
    ];

    /** Textfelder: Kennung -> Feld im data-Satz. */
    static TEXTE = {
        detailTitle: 'name', detailBackend: 'backend',
        detailBodyType: 'bodytype', detailDate: 'date',
    };

    static aufbauen(zielseite) {
        return new Fotoauftragsdetail(zielseite).aufbauen();
    }

    constructor(zielseite) {
        this.zielseite = zielseite;
        this.fenster = document.getElementById('detailModal');
        this.auftragId = null;
    }

    aufbauen() {
        document.querySelectorAll('[data-detail]').forEach(element => {
            element.addEventListener('click', () => this.zeigen(element));
        });
        document.getElementById('detailClose')
            ?.addEventListener('click', () => this.schliessen());
        // Klick auf den Hintergrund schliesst das Fenster.
        this.fenster?.addEventListener('click', ereignis => {
            if (ereignis.target === this.fenster) this.schliessen();
        });
        document.addEventListener('keydown', ereignis => {
            if (ereignis.key === 'Escape') this.schliessen();
        });
        return this;
    }

    zeigen(element) {
        const zeile = element.closest('tr');
        if (!zeile || !this.fenster) return;
        const daten = zeile.dataset;
        this.auftragId = daten.jobId;
        for (const [kennung, feld] of Object.entries(Fotoauftragsdetail.TEXTE)) {
            this._text(kennung, daten[feld]);
        }
        this._text('detailGender',
                   daten.gender === 'male' ? 'Männlich' : 'Weiblich');
        this._text('detailDuration', Fotoauftragsdetail.dauer(daten.duration));
        const foto = document.getElementById('detailPhoto');
        if (foto) foto.src = daten.photo;
        for (const [kasten, bild, feld] of Fotoauftragsdetail.BILDER) {
            this._bild(kasten, bild, daten[feld]);
        }
        this._knoepfe(daten.jobId);
        this.fenster.classList.add('offen');
    }

    /** Dauer in Sekunden mit einer Stelle, oder ein Gedankenstrich. */
    static dauer(wert) {
        const sekunden = parseFloat(wert);
        return sekunden > 0 ? sekunden.toFixed(1) + 's' : '—';
    }

    _text(kennung, wert) {
        const element = document.getElementById(kennung);
        if (element) element.textContent = wert || '';
    }

    _bild(kastenId, bildId, adresse) {
        const kasten = document.getElementById(kastenId);
        const bild = document.getElementById(bildId);
        if (!kasten || !bild) return;
        if (adresse) bild.src = adresse;
        kasten.classList.toggle('hb-versteckt', !adresse);
    }

    _knoepfe(auftragId) {
        const ziele = {
            detailBtn3D: '',
            detailBtnTextur: '&tab=textur',
            detailBtnReanalyze: '&reanalyze=1',
        };
        for (const [kennung, anhang] of Object.entries(ziele)) {
            const knopf = document.getElementById(kennung);
            if (knopf) knopf.href = `${this.zielseite}?job=${auftragId}${anhang}`;
        }
    }

    schliessen() {
        this.fenster?.classList.remove('offen');
    }
}
