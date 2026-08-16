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

const KOPFZEILE = '<tr style="color:#f472b6;border-bottom:2px solid #475569">'
    + '<th style="text-align:center;padding:3px 1px;width:14px">#</th>'
    + '<th style="text-align:left;padding:3px 3px">Bone</th>'
    + '<th style="text-align:center;padding:3px 2px;background:#1a0f2e" colspan="3">Video/2D</th>'
    + '<th style="text-align:center;padding:3px 2px;background:#1e1a2e">3D</th>'
    + '<th style="text-align:center;padding:3px 2px">Diff</th></tr>'
    + '<tr style="color:#999;font-size:9px;border-bottom:1px solid #334155">'
    + '<td></td><td></td>'
    + '<td style="text-align:right;padding:1px 3px;background:#1a0f2e">dist</td>'
    + '<td style="text-align:right;padding:1px 3px;background:#1a0f2e">ang°</td>'
    + '<td style="text-align:right;padding:1px 3px;background:#1a0f2e">Δdist</td>'
    + '<td style="text-align:right;padding:1px 3px;background:#1e1a2e">dist</td>'
    + '<td style="text-align:right;padding:1px 3px">Δdist</td></tr>';

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
        this.feld.innerHTML = '<div style="padding:8px;color:#fbbf24">'
                            + 'Warte auf BVH-Daten...</div>';
    }

    auffrischen(zustand, skelett, spielerdaten, fps) {
        if (!this.feld) return;
        if (!skelett.wurzel) { this._warten(); return; }
        const bild = spielerdaten.bildZuFortschritt(zustand.fortschritt);
        this.daten.erheben(bild, skelett);
        this.feld.innerHTML =
            this._kopf(zustand, skelett, spielerdaten, fps)
            + `<table style="width:100%;border-collapse:collapse;font-size:11px;padding:0 6px">`
            + KOPFZEILE + this._zeilen() + '</table>'
            + this._zusammenfassung() + this._rohwerte();
    }

    _kopf(zustand, skelett, spielerdaten, fps) {
        const bild2d = spielerdaten.bildnummer(zustand.fortschritt);
        const bilddauer = skelett.bilddauer(fps);
        const bild3d = skelett.klipdauer > 0
            ? Math.floor((zustand.fortschritt * skelett.klipdauer) / bilddauer) : 0;
        return '<div style="padding:8px;border-bottom:1px solid #334155;margin-bottom:4px">'
            + '<div style="color:#16c784;font-size:13px;font-weight:bold">Bone-Vergleich</div>'
            + `<div style="color:#ccc;font-size:10px">Frame `
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
            const { text: diff, farbe } = Vergleichstafel._abweichung(d2, d3);
            return '<tr style="border-top:1px solid #1e293b">'
                + `<td style="text-align:center;padding:2px 1px;color:#64748b;font-size:10px">${nr}</td>`
                + `<td style="padding:2px 3px;color:#8cb4ff;white-space:nowrap;font-size:10px">${name}</td>`
                + Vergleichstafel._zelle(d2 === null ? '—' : d2.toFixed(2), '#1a0f2e')
                + Vergleichstafel._zelle(winkel === null ? '—' : `${winkel.toFixed(0)}°`, '#1a0f2e')
                + Vergleichstafel._zelle(abschnitt === null ? '—' : abschnitt.toFixed(2), '#1a0f2e')
                + Vergleichstafel._zelle(d3 === null ? '—' : d3.toFixed(2), '#1e1a2e', '')
                + `<td style="text-align:right;padding:2px 3px;color:${farbe}">${diff}</td></tr>`;
        }).join('');
    }

    static _zelle(inhalt, hintergrund, farbe = '#c084fc') {
        return `<td style="text-align:right;padding:2px 3px;background:${hintergrund};`
             + (farbe ? `color:${farbe}` : '') + `">${inhalt}</td>`;
    }

    static _abweichung(d2, d3) {
        if (d2 === null || d3 === null) return { text: '—', farbe: '#64748b' };
        const dd = d3 - d2;
        const betrag = Math.abs(dd);
        return {
            text: (dd >= 0 ? '+' : '') + dd.toFixed(2),
            farbe: betrag < GRUEN ? '#16c784' : betrag < GELB ? '#fbbf24' : '#ef4444',
        };
    }

    _zusammenfassung() {
        const teile = GLIEDER.map(([beschriftung, oben, unten]) =>
            `${beschriftung}: `
            + `2D=${Vergleichsdaten.gefaelle(this.daten.zweiD, oben, unten)} `
            + `3D=${Vergleichsdaten.gefaelle(this.daten.dreiD, oben, unten)}`);
        return '<div style="margin-top:6px;border-top:1px solid #475569;'
            + 'padding-top:4px;color:#fbbf24;font-size:12px">'
            + teile.join(' &nbsp;|&nbsp; ') + ' &nbsp;|&nbsp; </div>';
    }

    _rohwerte() {
        const namen = ['Pelvis', 'Left_shoulder', 'Left_wrist',
                       'Right_shoulder', 'Right_wrist'];
        const werte = namen.map(n => {
            const p = this.daten.roh3d[n];
            return p ? `${n}=[${p.x.toFixed(0)},${p.y.toFixed(0)},${p.z.toFixed(0)}] ` : '';
        }).join('');
        return '<div style="margin-top:4px;color:#64748b;font-size:10px">'
             + 'Raw 3D (cm): ' + werte + '</div>';
    }
}
