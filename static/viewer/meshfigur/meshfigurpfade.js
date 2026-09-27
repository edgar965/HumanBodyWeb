/**
 * Meshfigurpfade — die Pfade von Körper- und Kopfnetz auf der Auftragsseite „Mesh to 3D" (27.09.2026).
 *
 * Edgar: „Textboxen für die Eingabepfade der Ursprungs-Meshes, auch beim Job, falls ich neu berechnen
 * will". Gefüllt einmal aus dem Eingang des Auftrags (`ursprung`); beim „Neu berechnen" gehen beide
 * Felder mit (`pfade`), der Server liest geänderte oder neu geschriebene Dateien neu ein
 * (`Meshfigureingang.aendern`). Ein hochgeladenes Körpernetz hat keinen Pfad — das leere Feld lässt
 * es stehen; ein leeres Kopffeld nimmt das Kopfnetz heraus.
 */
export class Meshfigurpfade {

    constructor() {
        this.koerper = document.getElementById('pfad-koerper');
        this.kopf = document.getElementById('pfad-kopf');
        this.hinweis = document.getElementById('pfad-hinweis');
    }

    fuellen(eingang) {
        const e = eingang || {};
        if (!this.koerper || !this.kopf) {
            this.melden('Pfadfelder fehlen — Seite neu laden', true);
            return;
        }
        this.koerper.value = e.ursprung || '';
        this.koerper.placeholder = e.ursprung ? '' : `hochgeladen: ${e.original || e.datei || '—'} (leer = so lassen)`;
        this.kopf.value = (e.kopf || {}).ursprung || '';
        this.kopf.placeholder = 'Pfad eines Kopfnetzes (GLB, GLTF, OBJ, PLY, STL, OFF)';
    }

    lesen() {
        return { koerper: this.koerper?.value.trim() || '', kopf: this.kopf?.value.trim() || '' };
    }

    melden(text, fehler = false) {
        if (!this.hinweis) return;
        this.hinweis.textContent = text;
        this.hinweis.classList.toggle('hb-schlecht', fehler);
    }
}
