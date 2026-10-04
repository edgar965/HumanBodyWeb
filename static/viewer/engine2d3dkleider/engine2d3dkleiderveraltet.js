/**
 * Engine2d3dKleiderveraltet — sagt, wenn der offene Tab älter ist als der Code auf dem Server (03.10.2026).
 *
 * Edgar: „tab iterationen ist noch immer nicht funktional" — nach einer Korrektur, die ein offener Tab nie bekommt: Das Dokument und seine
 * Module bleiben, wie sie beim Laden waren, nur der Zustand wird nachgefragt. Die Module kommen unter `/statik/v-<Fassung>/…` (die Fassung
 * ist die jüngste Änderungszeit im Statik-Baum, `djangobase.fassungsstatik`); der Zustand trägt die aktuelle als `statik`. Weichen beide
 * ab, steht unten ein Band mit „Neu laden" — nichts lädt von selbst neu, ein offenes Formular soll nicht verloren gehen.
 */
export class Engine2d3dKleiderveraltet {

    /** Die Fassung, mit der DIESES Modul geladen wurde (aus seiner Adresse); null, wenn die Adresse keine trägt. */
    static GELADEN = (new URL(import.meta.url).pathname.match(/\/v-(\d+)\//) || [])[1] || null;

    constructor() {
        this.leiste = null;
    }

    pruefen(zustand) {
        const jetzt = zustand?.statik == null ? null : String(zustand.statik);
        if (!Engine2d3dKleiderveraltet.GELADEN || !jetzt || jetzt === Engine2d3dKleiderveraltet.GELADEN) return;
        this._zeigen();
    }

    _zeigen() {
        if (this.leiste) return;
        const leiste = document.createElement('div');
        leiste.className = 'engine2d3dkleider-veraltet';
        leiste.setAttribute('role', 'alert');
        const text = document.createElement('span');
        text.textContent = 'Diese Seite ist veraltet: Der Code auf dem Server hat sich geändert. Neu laden, damit Korrekturen wirken.';
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-primary btn-sm';
        knopf.textContent = 'Neu laden';
        knopf.addEventListener('click', () => location.reload());
        leiste.append(text, knopf);
        document.body.appendChild(leiste);
        this.leiste = leiste;
    }
}
