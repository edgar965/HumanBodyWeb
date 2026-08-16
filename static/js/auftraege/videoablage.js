/**
 * Videoablage — Datei ablegen oder auswaehlen und das Upload-Formular
 * abschicken.
 *
 * Herausgeloest aus templates/upload.html und upload_v4.html (Umbau
 * 16.08.2026): Der Block stand in beiden Vorlagen, bis auf den
 * Doppelklick-Schutz buchstabengleich (24 bzw. 21 Zeilen).
 *
 * Der Schutz gegen doppeltes Absenden gilt jetzt auf BEIDEN Seiten — in
 * upload_v4.html fehlte er, und ein zweiter Klick auf das Ablagefeld waehrend
 * des Uploads schickte das Formular ein zweites Mal ab (zwei Auftraege zur
 * selben Datei).
 */
export class Videoablage {

    static aufbauen() {
        return new Videoablage().aufbauen();
    }

    constructor() {
        this.ziel = document.getElementById('dropTarget');
        this.feld = document.getElementById('videoInput');
        this.formular = document.getElementById('uploadForm');
        this.laeuft = false;
    }

    aufbauen() {
        if (!this.ziel || !this.feld) return this;
        this.formular?.addEventListener('submit', ereignis => {
            if (this.laeuft) { ereignis.preventDefault(); return; }
            this.laeuft = true;
        });
        this.ziel.addEventListener('click', () => this.feld.click());
        this.ziel.addEventListener('dragover', ereignis => {
            ereignis.preventDefault();
            this.ziel.classList.add('drag-over');
        });
        this.ziel.addEventListener('dragleave', () => {
            this.ziel.classList.remove('drag-over');
        });
        this.ziel.addEventListener('drop', ereignis => {
            ereignis.preventDefault();
            this.ziel.classList.remove('drag-over');
            if (!ereignis.dataTransfer.files.length) return;
            this.feld.files = ereignis.dataTransfer.files;
            this.absenden(this.feld.files[0].name);
        });
        this.feld.addEventListener('change', () => {
            if (this.feld.files.length) this.absenden(this.feld.files[0].name);
        });
        return this;
    }

    absenden(dateiname) {
        const anzeige = this.ziel.querySelector('p');
        if (anzeige) anzeige.textContent = dateiname;
        this.formular?.submit();
    }
}
