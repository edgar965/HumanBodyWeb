/**
 * Videoueberlagerung — das 2D-Skelett auf dem Video.
 *
 * Aus bvh_player.js herausgeloest (Umbau 16.08.2026).
 */

/** Ab welcher Zuverlaessigkeit ein Gelenk gezeichnet wird. */
const MINDESTGUETE = 0.3;

export class Videoueberlagerung {
    constructor(behaelter, video, daten) {
        this.behaelter = behaelter;
        this.video = video;
        this.daten = daten;
        this.leinwand = null;
        this.stift = null;
        if (!behaelter) return;
        this.leinwand = document.createElement('canvas');
        this.leinwand.className = 'spieler-ueberlagerung';
        behaelter.appendChild(this.leinwand);
        this.stift = this.leinwand.getContext('2d');
        this.groesseAnpassen();
    }

    groesseAnpassen() {
        if (!this.leinwand || !this.behaelter) return;
        const w = this.behaelter.clientWidth;
        const h = this.behaelter.clientHeight;
        if (w <= 0 || h <= 0) return;
        const dpr = window.devicePixelRatio;
        this.leinwand.width = w * dpr;
        this.leinwand.height = h * dpr;
        this.stift.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    /**
     * Bildbereich innerhalb des Behaelters.
     *
     * Das Video steht mit `object-fit: contain`, hat also schwarze Balken,
     * sobald die Seitenverhaeltnisse nicht passen. Ohne diese Rechnung liegt
     * das Skelett um die Balkenbreite daneben.
     */
    _bildbereich(cw, ch) {
        if (!this.video.videoWidth || !this.video.videoHeight) {
            return { rw: cw, rh: ch, ox: 0, oy: 0 };
        }
        const vAnteil = this.video.videoWidth / this.video.videoHeight;
        if (cw / ch > vAnteil) {
            const rw = ch * vAnteil;
            return { rw, rh: ch, ox: (cw - rw) / 2, oy: 0 };
        }
        const rh = cw / vAnteil;
        return { rw: cw, rh, ox: 0, oy: (ch - rh) / 2 };
    }

    zeichnen(zustand, format, nummernZeigen) {
        if (!this.stift || !this.leinwand) return;
        const cw = this.behaelter.clientWidth;
        const ch = this.behaelter.clientHeight;
        const dpr = window.devicePixelRatio;
        if (this.leinwand.width !== Math.round(cw * dpr)
            || this.leinwand.height !== Math.round(ch * dpr)) {
            this.leinwand.width = Math.round(cw * dpr);
            this.leinwand.height = Math.round(ch * dpr);
            this.stift.setTransform(dpr, 0, 0, dpr, 0, 0);
        }
        this.stift.clearRect(0, 0, cw, ch);

        const bild = this.daten.bildZuFortschritt(zustand.fortschritt);
        if (!zustand.sichtbar || !bild || !this.video.duration) return;
        if (!this.daten.erkanntBei(zustand.fortschritt)) return;

        const { rw, rh, ox, oy } = this._bildbereich(cw, ch);
        this._verbindungen(bild, rw, rh, ox, oy);
        this._gelenke(bild, rw, rh, ox, oy, format, nummernZeigen);
    }

    _verbindungen(bild, rw, rh, ox, oy) {
        this.stift.strokeStyle = '#00ff00';
        this.stift.lineWidth = 2.5;
        this.stift.lineCap = 'round';
        for (const [a, b] of this.daten.verbindungen) {
            const p1 = bild[a], p2 = bild[b];
            if (!p1 || !p2 || p1[2] <= MINDESTGUETE || p2[2] <= MINDESTGUETE) continue;
            this.stift.beginPath();
            this.stift.moveTo(p1[0] * rw + ox, p1[1] * rh + oy);
            this.stift.lineTo(p2[0] * rw + ox, p2[1] * rh + oy);
            this.stift.stroke();
        }
    }

    _gelenke(bild, rw, rh, ox, oy, format, nummernZeigen) {
        this.stift.font = 'bold 11px monospace';
        this.stift.textAlign = 'center';
        this.stift.textBaseline = 'bottom';
        for (const name of this.daten.gelenke) {
            const p = bild[name];
            if (!p || p[2] <= MINDESTGUETE) continue;
            const sx = p[0] * rw + ox;
            const sy = p[1] * rh + oy;
            this.stift.fillStyle = '#e94560';
            this.stift.beginPath();
            this.stift.arc(sx, sy, 4, 0, Math.PI * 2);
            this.stift.fill();
            const nummer = format.nummer(name);
            if (!nummernZeigen || nummer < 0) continue;
            const text = String(nummer);
            const breite = this.stift.measureText(text).width + 6;
            this.stift.fillStyle = 'rgba(0,0,0,0.7)';
            this.stift.fillRect(sx - breite / 2, sy - 18, breite, 14);
            this.stift.fillStyle = '#fbbf24';
            this.stift.fillText(text, sx, sy - 5);
        }
    }
}
