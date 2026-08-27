/**
 * Vergleichstafel — die dritte Spalte der Ergebnisseite: 2D gegen 3D je Knochen.
 *
 * Aus `updateDebugOverlay` in bvh_player.js herausgeloest (Umbau 16.08.2026).
 * Die Rechnung steht in vergleichsdaten.js; hier wird nur angezeigt.
 */
import { VERGLEICHSKNOCHEN } from './skelettformate.js';
import { Vergleichsdaten } from './vergleichsdaten.js';

/** Farbschwellen fuer die Abweichung zwischen 2D und 3D. */
const GRUEN = 0.15;
const GELB = 0.4;

const KOPFZEILE = '<tr class="vt-kopf">'
    + '<th class="vt-nr">#</th>'
    + '<th class="vt-name-kopf">Bone</th>'
    + '<th class="vt-mitte vt-video" colspan="3">Video/2D</th>'
    + '<th class="vt-mitte vt-drei-d">3D</th>'
    + '<th class="vt-mitte">Diff</th></tr>'
    + '<tr class="vt-unterkopf">'
    + '<td></td><td></td>'
    + '<td class="vt-zahl vt-video">dist</td>'
    + '<td class="vt-zahl vt-video">ang°</td>'
    + '<td class="vt-zahl vt-video">Δdist</td>'
    + '<td class="vt-zahl vt-drei-d">dist</td>'
    + '<td class="vt-zahl">Δdist</td></tr>';

/** Gliedmassen der Zusammenfassung: [Beschriftung, oben, unten]. */
const GLIEDER = [
    ['L arm', 'Left_shoulder', 'Left_wrist'],
    ['R arm', 'Right_shoulder', 'Right_wrist'],
    ['L leg', 'Left_hip', 'Left_ankle'],
    ['R leg', 'Right_hip', 'Right_ankle'],
];

export class Vergleichstafel {
    constructor() {
        this.feld = document.getElementById('debugBonePanel');
        this.daten = new Vergleichsdaten(VERGLEICHSKNOCHEN);
        if (this.feld) this._warten();
    }

    get aktiv() {
        return !!this.feld;
    }

    _warten() {
        this.feld.innerHTML = '<div class="vt-hinweis">'
                            + 'Warte auf BVH-Daten...</div>';
    }

    auffrischen(zustand, skelett, spielerdaten, fps) {
        if (!this.feld) return;
        if (!skelett.wurzel) { this._warten(); return; }
        const bild = spielerdaten.bildZuFortschritt(zustand.fortschritt);
        this.daten.erheben(bild, skelett);
        this.feld.innerHTML =
            this._kopf(zustand, skelett, spielerdaten, fps)
            + `<table class="vt-tabelle doku">`
            + KOPFZEILE + this._zeilen() + '</table>'
            + this._zusammenfassung() + this._rohwerte();
    }

    _kopf(zustand, skelett, spielerdaten, fps) {
        const bild2d = spielerdaten.bildnummer(zustand.fortschritt);
        const bilddauer = skelett.bilddauer(fps);
        const bild3d = skelett.klipdauer > 0
            ? Math.floor((zustand.fortschritt * skelett.klipdauer) / bilddauer) : 0;
        return '<div class="vt-titelzeile">'
            + '<div class="vt-titel">Bone-Vergleich</div>'
            + `<div class="vt-bildnummer">Frame `
            + `${Math.floor(zustand.zeit * fps)} | 2D:${bild2d} 3D:${bild3d} `
            + `(${zustand.zeit.toFixed(2)}s)</div></div>`;
    }

    _zeilen() {
        const { zweiD, dreiD } = this.daten;
        return VERGLEICHSKNOCHEN.map((name, nr) => {
            const d2 = Vergleichsdaten.abstand(zweiD, name);
            const d3 = Vergleichsdaten.abstand(dreiD, name);
            const winkel = Vergleichsdaten.winkel(zweiD, name);
            const abschnitt = Vergleichsdaten.abschnitt(zweiD, name);
            const { text: diff, stufe } = Vergleichstafel._abweichung(d2, d3);
            return '<tr class="vt-reihe">'
                + `<td class="vt-nr-zelle">${nr}</td>`
                + `<td class="vt-name">${name}</td>`
                + Vergleichstafel._zelle(d2 === null ? '—' : d2.toFixed(2), '#1a0f2e')
                + Vergleichstafel._zelle(winkel === null ? '—' : `${winkel.toFixed(0)}°`, 'vt-video')
                + Vergleichstafel._zelle(abschnitt === null ? '—' : abschnitt.toFixed(2), 'vt-video')
                + Vergleichstafel._zelle(d3 === null ? '—' : d3.toFixed(2), 'vt-drei-d', '')
                + `<td class="vt-zahl-klein vt-${stufe}">${diff}</td></tr>`;
        }).join('');
    }

    /**
     * Zahlenzelle. `spalte` ist die Klasse der Spaltengruppe (Video oder 3D),
     * `betont` die Textfarbe — beides ueber CSS, nicht als Hex im Code
     * (Umbau 16.08.2026).
     */
    static _zelle(inhalt, spalte, betont = 'vt-betont') {
        return `<td class="vt-zahl-klein ${spalte} ${betont}">${inhalt}</td>`;
    }

    /**
     * Abweichung mit ihrer Guetestufe. Die Stufe wird als CSS-Klasse gezeigt
     * (`vt-gut`/`vt-mittel`/`vt-schlecht`) — welche Farbe dazu gehoert, steht im
     * Stylesheet und nicht hier.
     */
    static _abweichung(d2, d3) {
        if (d2 === null || d3 === null) return { text: '—', stufe: 'leer' };
        const dd = d3 - d2;
        const betrag = Math.abs(dd);
        return {
            text: (dd >= 0 ? '+' : '') + dd.toFixed(2),
            stufe: betrag < GRUEN ? 'gut' : betrag < GELB ? 'mittel' : 'schlecht',
        };
    }

    _zusammenfassung() {
        const teile = GLIEDER.map(([beschriftung, oben, unten]) =>
            `${beschriftung}: `
            + `2D=${Vergleichsdaten.gefaelle(this.daten.zweiD, oben, unten)} `
            + `3D=${Vergleichsdaten.gefaelle(this.daten.dreiD, oben, unten)}`);
        return '<div class="vt-zusammenfassung">'
            + teile.join(' &nbsp;|&nbsp; ') + ' &nbsp;|&nbsp; </div>';
    }

    _rohwerte() {
        const namen = ['Pelvis', 'Left_shoulder', 'Left_wrist',
                       'Right_shoulder', 'Right_wrist'];
        const werte = namen.map(n => {
            const p = this.daten.roh3d[n];
            return p ? `${n}=[${p.x.toFixed(0)},${p.y.toFixed(0)},${p.z.toFixed(0)}] ` : '';
        }).join('');
        return '<div class="vt-fussnote">'
             + 'Raw 3D (cm): ' + werte + '</div>';
    }
}
