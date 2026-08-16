import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

/**
 * Fotoergebnis — die Anzeige dessen, was der Erkenner im Foto gefunden hat.
 *
 * Aus fotoanalyse.js herausgeloest (Umbau 16.08.2026): Die Klasse war nach dem
 * Schnitt von `analyzePhoto()` selbst 393 Zeilen lang. Getrennt wird nach dem
 * naheliegenden Schnitt — hier steht, was ANGEZEIGT wird, dort, was mit den
 * Werten GESCHIEHT.
 *
 * Die Inline-Stile der frueheren Fassung liegen als `.foto-*` und
 * `.haut-tupfer` im Stilblock von templates/photo_to_3d.html.
 */
export class Fotoergebnis {

    /** Deutsche Namen der Ausdrucks-Parameter, in der Reihenfolge des Modells. */
    static AUSDRUCK_NAMEN = [
        'Kiefer offen', 'Lächeln', 'Brauen hoch', 'Brauen runter', 'Lippe hoch',
        'Mundwinkel', 'Wangen', 'Zusammenkneifen', 'Nase', 'Augen weit',
    ];
    static ANZAHL = 10;
    /** Nur Ausdruckswerte über dieser Stärke werden aufgezählt. */
    static AUSDRUCK_SCHWELLE = 0.3;

    static MASSE_NAMEN = {
        height_cm: 'Körpergröße', shoulder_cm: 'Schulterbreite',
        hip_cm: 'Hüftbreite', torso_cm: 'Torsolänge',
        leg_cm: 'Beinlänge', arm_cm: 'Armlänge',
    };
    static META_NAMEN = {
        height: 'Größe (cm)', mass: 'Gewicht (kg)',
        tone: 'Muskeltonus', age: 'Alter',
    };

    constructor(ergebnisfeld, parameterfeld) {
        this.ergebnisfeld = ergebnisfeld;
        this.parameterfeld = parameterfeld;
    }

    ergebnisZeigen(daten) {
        this.parameterfeld.innerHTML = '';
        this._kopfzeile(daten);
        for (const [name, wert] of this.parameterliste(daten)) {
            const zeile = document.createElement('div');
            zeile.className = 'detection-param';
            zeile.innerHTML = `<span class="param-name">${name}</span>`
                            + `<span class="param-val">${wert}</span>`;
            this.parameterfeld.appendChild(zeile);
        }
        this.parameterfeld.appendChild(this.geschlechtswahl(daten));
        if (daten.mock === true) this.parameterfeld.appendChild(this._mockhinweis());
        this.ergebnisfeld.style.display = 'block';
    }

    _kopfzeile(daten) {
        const kopf = this.ergebnisfeld.querySelector('h4');
        if (!kopf) return;
        const erkenner = daten.backend || state.selectedBackend;
        const name = daten.mock === true
            ? 'Mock-Daten'
            : (state.backendStatus[erkenner]?.label || erkenner);
        const klasse = daten.mock === true ? 'mock' : 'real';
        kopf.innerHTML = 'Erkannte Parameter '
            + `<span class="detection-model-badge ${klasse}">${name}</span>`;
    }

    /** Alle Zeilen der Ergebnisliste als [Name, Wert]. */
    parameterliste(daten) {
        const geschlecht = daten.gender === 'male' ? 'Männlich' : 'Weiblich';
        const liste = [
            ['Geschlecht', geschlecht + (daten.estimated_gender ? ' (auto)' : '')],
            ['Body Type', String(daten.body_type).replace('_', ' ')],
        ];
        if (daten.mock !== true) {
            liste.push(['Confidence', (daten.confidence * 100).toFixed(0) + '%']);
        }
        if (daten.skin_color) {
            liste.push(['Hautfarbe',
                `<span class="haut-tupfer" style="background:${daten.skin_color};"></span>`
                + daten.skin_color]);
        }
        this._benannt(liste, daten.measurements, Fotoergebnis.MASSE_NAMEN, ' cm');
        this._benannt(liste, daten.meta_sliders, Fotoergebnis.META_NAMEN, '');
        if (daten.betas) {
            liste.push(['Shape-Parameter', this._anzahl(daten.betas) + ' erkannt']);
        }
        this._ausdruck(liste, daten.expression);
        for (const [name, wert] of Object.entries(daten.morphs || {})) {
            const kurz = name.split('_').slice(1).join(' ') || name;
            liste.push([kurz, (wert >= 0 ? '+' : '') + (wert * 100).toFixed(0) + '%']);
        }
        return liste;
    }

    _benannt(liste, werte, namen, einheit) {
        for (const [schluessel, wert] of Object.entries(werte || {})) {
            liste.push([namen[schluessel] || schluessel, wert + einheit]);
        }
    }

    _anzahl(feld) {
        return Math.min(feld.length, Fotoergebnis.ANZAHL);
    }

    /** Die drei stärksten Ausdruckswerte in Worten. */
    _ausdruck(liste, werte) {
        if (!werte?.length) return;
        liste.push(['Expression-Parameter', this._anzahl(werte) + ' erkannt']);
        const stark = werte
            .map((wert, i) => ({ name: Fotoergebnis.AUSDRUCK_NAMEN[i] || `Expr ${i}`, wert }))
            .filter(e => Math.abs(e.wert) > Fotoergebnis.AUSDRUCK_SCHWELLE)
            .sort((a, b) => Math.abs(b.wert) - Math.abs(a.wert))
            .slice(0, 3);
        if (!stark.length) return;
        liste.push(['Ausdruck', stark.map(
            e => `${e.name} ${e.wert >= 0 ? '+' : ''}${e.wert.toFixed(1)}`).join(', ')]);
    }

    /** Auswahlfeld, mit dem man das erkannte Geschlecht überstimmt. */
    geschlechtswahl(daten) {
        const erkannt = daten.gender === 'male' ? 'Männlich' : 'Weiblich';
        const zeile = document.createElement('div');
        zeile.className = 'foto-geschlechtszeile';
        const beschriftung = document.createElement('span');
        beschriftung.className = 'foto-beschriftung';
        beschriftung.textContent = 'Geschlecht:';
        const feld = document.createElement('select');
        feld.className = 'viewer-select foto-geschlechtsfeld';
        for (const [wert, text] of [['auto', `Automatisch (${erkannt})`],
                                    ['male', 'Männlich'], ['female', 'Weiblich']]) {
            feld.appendChild(new Option(text, wert));
        }
        feld.value = 'auto';
        feld.addEventListener('change', () => this._geschlechtSetzen(feld.value, daten));
        zeile.appendChild(beschriftung);
        zeile.appendChild(feld);
        return zeile;
    }

    _geschlechtSetzen(wahl, daten) {
        const geschlecht = wahl === 'auto' ? daten.gender : wahl;
        const vorsatz = geschlecht === 'male' ? 'Male' : 'Female';
        // Die Herkunft bleibt, nur der erste Teil des Körpertyps wechselt.
        const herkunft = state.currentBodyType.split('_')[1] || 'Caucasian';
        state.currentBodyType = `${vorsatz}_${herkunft}`;
        state.smplxGender = geschlecht;
        const typfeld = document.getElementById('body-type-select');
        if (typfeld) {
            typfeld.value = state.currentBodyType;
            typfeld.dispatchEvent(new Event('change'));
        }
        const geschlechtsfeld = document.getElementById('smplx-gender');
        if (geschlechtsfeld) geschlechtsfeld.value = state.smplxGender;
        fn.loadSmplxModel();
    }

    _mockhinweis() {
        const feld = document.createElement('div');
        feld.className = 'foto-mockhinweis';
        feld.innerHTML = '<i class="fas fa-info-circle"></i> SMPL-X Modell oder '
            + 'MediaPipe Pose nicht verfügbar. Werte sind zufällige Testdaten.';
        return feld;
    }
    /** Meldung statt Ergebnis — Analyse fehlgeschlagen oder Fehler. */
    meldung(text, art) {
        this.parameterfeld.innerHTML =
            `<div class="foto-meldung foto-${art}">${text}</div>`;
        this.ergebnisfeld.style.display = 'block';
    }
}
