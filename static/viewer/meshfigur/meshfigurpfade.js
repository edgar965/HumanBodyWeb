/**
 * Meshfigurpfade — die Pfade von Körper- und Kopfnetz auf der Auftragsseite „Mesh to 3D" (27.09.2026).
 *
 * Edgar: „Textboxen für die Eingabepfade der Ursprungs-Meshes, auch beim Job, falls ich neu berechnen
 * will". Gefüllt einmal aus dem Eingang des Auftrags (`ursprung`). Ein hochgeladenes Körpernetz hat keinen
 * Pfad — das leere Feld lässt es stehen.
 *
 * DAS KOPFNETZ IST ABSCHALTBAR (29.09.2026, Edgar: „mach mir bei den Jobs Mesh to 3D die auswahl des Kopfes
 * optional … aus der glb Edgar alles erzeugen"): Schalter „Kopfnetz verwenden". Aus = der Lauf nimmt Kopf,
 * Gesicht und Haar aus dem Körpernetz; der Pfad bleibt im Feld (ausgegraut) und beim Server gemerkt
 * (`eingang.kopf_gemerkt`), damit Einschalten ihn wieder nimmt. Gespeichert wird jede Änderung sofort
 * (`Meshfigureinstellungen`), nicht erst mit „Neu berechnen".
 */
export class Meshfigurpfade {

    constructor() {
        this.koerper = document.getElementById('pfad-koerper');
        this.kopf = document.getElementById('pfad-kopf');
        this.kopfAn = document.getElementById('kopf-an');
        this.hinweis = document.getElementById('pfad-hinweis');
        this.kopfAn?.addEventListener('change', () => this._kopfSchalter());
    }

    fuellen(eingang) {
        const e = eingang || {};
        if (!this.koerper || !this.kopf || !this.kopfAn) {
            this.melden('Pfadfelder fehlen — Seite neu laden', true);
            return;
        }
        this.koerper.value = e.ursprung || '';
        this.koerper.placeholder = e.ursprung ? '' : `hochgeladen: ${e.original || e.datei || '—'} (leer = so lassen)`;
        this.kopfAn.checked = Boolean(e.kopf);
        this.kopf.value = (e.kopf || {}).ursprung || e.kopf_gemerkt || '';
        this.kopf.placeholder = 'Pfad eines Kopfnetzes (GLB, GLTF, OBJ, PLY, STL, OFF)';
        this._kopfSchalter();
    }

    _kopfSchalter() {
        this.kopf.disabled = !this.kopfAn.checked;
    }

    lesen() {
        return { koerper: this.koerper?.value.trim() || '', kopf: this.kopf?.value.trim() || '' };
    }

    kopfVerwenden() {
        return Boolean(this.kopfAn?.checked);
    }

    melden(text, fehler = false) {
        if (!this.hinweis) return;
        this.hinweis.textContent = text;
        this.hinweis.classList.toggle('hb-schlecht', fehler);
    }
}
