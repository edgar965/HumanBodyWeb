/**
 * Proportionen3dregler — die 19 Maße als Schieber neben dem 3D-Zielnetz.
 *
 * Edgar (20.09.2026): „sowas wie die Morph slider bei Genesis, mit denen ich
 * das 3D Modell modelliere." Eine Zeile je Maß (`katalog.proportionen`):
 * Name, Schieber, Zahlenfeld (cm) und das Ergebnis der Formung („→ 32,9",
 * `bericht[k].nachher`). Der Schieber läuft von 60 % bis 150 % des
 * gemessenen Ziels (mindestens 1..80 cm), Schritt 0,1. Ein Zug ruft
 * `beiWert(k, cm)` — derselbe Weg wie eine getippte Zahl im Popup, die
 * Pfeile im Bild folgen. × leert die Vorgabe (`beiWert(k, null)`).
 * `aktualisieren(werte, ziel, bericht)` zieht die Zeilen nach, wenn ein
 * Pfeil im Bild gezogen wurde — ohne einen neuen Zug auszulösen.
 */
export class Proportionen3dregler {

    static SPANNE = [0.6, 1.5];

    /**
     * @param feld     Container der Zeilen
     * @param katalog  `{proportionen: [{schluessel, name, ansicht}]}`
     * @param beiWert  `(schluessel, cm|null)`
     */
    constructor(feld, katalog, beiWert) {
        this.feld = feld;
        this.katalog = katalog || {};
        this.beiWert = beiWert;
        this.zeilen = {};
    }

    /** Zeilen aufbauen (einmal) und füllen: `werte` Eingaben, `ziel` gemessen (cm je Maß). */
    fuellen(werte, ziel, bericht = {}) {
        if (!Object.keys(this.zeilen).length) this._bauen();
        this.aktualisieren(werte, ziel, bericht);
    }

    _bauen() {
        this.feld.replaceChildren();
        for (const m of this.katalog.proportionen || []) {
            const k = m.schluessel;
            const zeile = document.createElement('div');
            zeile.className = 'bildmodell-3dzeile';
            zeile.dataset.mass = k;
            zeile.innerHTML = `<span class="name" title="${m.name} (${m.ansicht})">${m.name}</span>`
                + '<input type="range" min="1" max="80" step="0.1">'
                + '<input type="number" min="0.5" max="120" step="0.1" class="form-control form-control-sm">'
                + '<button type="button" class="btn btn-sm btn-secondary" data-tat="leeren" title="Vorgabe leeren">×</button>'
                + '<span class="nachher" title="Gemessen am geformten Zielnetz"></span>';
            const schieber = zeile.querySelector('input[type="range"]');
            const zahl = zeile.querySelector('input[type="number"]');
            schieber.addEventListener('input', () => { zahl.value = schieber.value; this._melden(k, schieber.value); });
            zahl.addEventListener('change', () => { schieber.value = zahl.value; this._melden(k, zahl.value); });
            zeile.querySelector('[data-tat="leeren"]').addEventListener('click', () => this.beiWert(k, null));
            this.feld.appendChild(zeile);
            this.zeilen[k] = { zeile, schieber, zahl, nachher: zeile.querySelector('.nachher') };
        }
    }

    _melden(k, wert) {
        const cm = Number(wert);
        if (Number.isFinite(cm) && cm > 0) this.beiWert(k, Math.round(cm * 10) / 10);
    }

    /** Zeilen auf den Stand bringen: Wert = Eingabe, sonst Ziel; Spanne um das Ziel; Ergebnis der Formung. */
    aktualisieren(werte, ziel, bericht = {}) {
        for (const [k, z] of Object.entries(this.zeilen)) {
            const eingabe = werte[k];
            const gemessen = Number(ziel[k]);
            const basis = Number.isFinite(gemessen) && gemessen > 0 ? gemessen : Number(eingabe) || 20;
            const [lo, hi] = Proportionen3dregler.SPANNE;
            z.schieber.min = String(Math.max(0.5, Math.floor(basis * lo)));
            z.schieber.max = String(Math.min(120, Math.ceil(basis * hi)));
            const wert = eingabe !== undefined && eingabe !== null && eingabe !== '' ? Number(eingabe) : basis;
            if (document.activeElement !== z.schieber && document.activeElement !== z.zahl) {
                z.schieber.value = String(wert);
                z.zahl.value = Number.isFinite(wert) ? wert.toFixed(1) : '';
            }
            z.zeile.classList.toggle('eingestellt', eingabe !== undefined && eingabe !== null && eingabe !== '');
            const b = bericht[k];
            z.nachher.textContent = b && b.nachher !== null && b.nachher !== undefined
                ? `→ ${Number(b.nachher).toFixed(1).replace('.', ',')}` : '';
        }
    }
}
