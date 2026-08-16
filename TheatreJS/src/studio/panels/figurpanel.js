import { Panel } from './panel.js';
import { Koerperfrage } from '../../laden/koerperfrage.js';
import { Kodierung } from '../../../../static/viewer/gemeinsam/kodierung.js';

/**
 * Figurpanel — Meta-Parameter, Morphs, Position und Drehung einer Figur.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026): 320 Zeilen in vier Funktionen.
 * Drei Befunde beim Lesen, alle behoben:
 *
 * 1. DOPPELTER CODE. `populateMetaSliders` und `populateMorphSliders` waren
 *    Zeile fuer Zeile dieselbe Funktion — Schieberliste bauen, Wert anzeigen,
 *    Netz nachladen. Unterschiedlich waren nur die Wertequelle und das
 *    Namenspraefix. Jetzt eine Methode mit zwei Aufrufen.
 *
 * 2. KEINE ENTPRELLUNG. Jede Schieberbewegung rief `reloadCharacterMesh` —
 *    eine Anfrage, die ein 5,2-MB-Netz zurueckgibt. Wer einen Schieber
 *    durchzieht, loeste Dutzende davon aus. In main.js stand sogar eine
 *    Variable `reloadDebounceTimer` mit dem Kommentar "Debounce for character
 *    reload" — sie wurde nie benutzt. Jetzt wird gewartet, bis der Schieber
 *    ruht, und eine laufende Anfrage wird nicht von der naechsten ueberholt.
 *
 * 3. SIEBTE KOPIE der base64-Umsetzung. `base64ToFloat32` und der Z-oben-
 *    nach-Y-oben-Tausch (letzterer zweimal in derselben Funktion) stehen seit
 *    dem 15.08.2026 in static/viewer/gemeinsam/kodierung.js. Von dort kommen
 *    sie jetzt auch hier.
 */
export class Figurpanel {

    static GRAD = 180 / Math.PI;

    /** Ruhezeit in Millisekunden, bevor das Netz neu geholt wird. */
    static RUHE_MS = 180;

    /** Meta-Parameter mit Grenzen und deutscher Beschriftung. */
    static META = [
        ['age', 'Alter'],
        ['mass', 'Gewicht'],
        ['tone', 'Muskeltonus'],
        ['height', 'Höhe'],
    ];
    static META_MIN = -1.0;
    static META_MAX = 1.0;
    static SCHRITT = 0.01;

    constructor() {
        this._wartend = null;      // Zeitgeber der Entprellung
        this._laufend = false;     // laeuft gerade eine Anfrage?
        this._nachholen = null;    // Figur, die danach dran ist
    }

    zeigen(figur) {
        const ziel = Panel.oeffnen();
        if (!ziel) return;
        const name = figur.userData.presetName || 'Figur';
        const art = figur.userData.bodyType || 'unbekannt';
        const grad = Figurpanel.GRAD;

        ziel.innerHTML = `<div class="pnl-inhalt">
            ${Panel.kopf('fa-user', name)}
            <div class="pnl-zeile"><span class="pnl-achse">Body Type:</span>
                <span class="pnl-wert">${art}</span></div>

            <div class="pnl-gruppe">
                <h4 class="pnl-untertitel"><i class="fas fa-sliders-h"></i>
                    Meta-Parameter</h4>
                <div id="meta-sliders-container"></div>
            </div>

            <div class="pnl-gruppe">
                <h4 class="pnl-untertitel"><i class="fas fa-palette"></i> Morphs</h4>
                <div id="morph-sliders-container" class="pnl-rollbar-kurz"></div>
            </div>

            ${Panel.dreierblock('Position', 'char-pos',
                                [figur.position.x.toFixed(2),
                                 figur.position.y.toFixed(2),
                                 figur.position.z.toFixed(2)])}
            ${Panel.dreierblock('Rotation (Grad)', 'char-rot',
                                [(figur.rotation.x * grad).toFixed(1),
                                 (figur.rotation.y * grad).toFixed(1),
                                 (figur.rotation.z * grad).toFixed(1)], 5)}
            ${Panel.hinweis('Die Transform-Controls in der Szene ändern '
                            + 'Position und Drehung ebenfalls')}
        </div>`;

        this._lage(figur);
        this._metaSchieber(figur);
        this._morphSchieber(figur);
    }

    // ------------------------------------------------------------ Schieber

    _metaSchieber(figur) {
        const werte = figur.userData.meta
            || Object.fromEntries(Figurpanel.META.map(([schluessel]) => [schluessel, 0]));
        figur.userData.meta = werte;
        this._schieberliste('meta-sliders-container', 'meta',
            Figurpanel.META.map(([schluessel, titel]) => ({
                schluessel, titel, wert: werte[schluessel] || 0,
                min: Figurpanel.META_MIN, max: Figurpanel.META_MAX,
            })),
            (schluessel, wert) => { werte[schluessel] = wert; },
            figur);
    }

    _morphSchieber(figur) {
        const werte = figur.userData.morphs || {};
        const eintraege = Object.entries(werte).map(([schluessel, wert]) => ({
            schluessel, titel: schluessel, wert: wert || 0, min: 0, max: 1,
        }));
        if (!eintraege.length) {
            const ziel = document.getElementById('morph-sliders-container');
            if (ziel) ziel.innerHTML = '<div class="pnl-leer">Keine Morphs</div>';
            return;
        }
        this._schieberliste('morph-sliders-container', 'morph', eintraege,
            (schluessel, wert) => { werte[schluessel] = wert; }, figur);
    }

    /**
     * Eine Liste beschrifteter Schieber bauen und verdrahten.
     * Ersetzt die beiden gleichlautenden Funktionen fuer Meta und Morphs.
     */
    _schieberliste(zielId, praefix, eintraege, uebernehmen, figur) {
        const ziel = document.getElementById(zielId);
        if (!ziel) return;
        ziel.innerHTML = eintraege.map(e => `
            <div class="pnl-schieberzeile">
                <div class="pnl-schieberkopf">
                    <span class="pnl-achse">${e.titel}</span>
                    <span class="pnl-wert" id="${praefix}-${e.schluessel}-value">${e.wert.toFixed(2)}</span>
                </div>
                <input type="range" id="${praefix}-${e.schluessel}" class="pnl-schieber"
                       min="${e.min}" max="${e.max}" step="${Figurpanel.SCHRITT}"
                       value="${e.wert}">
            </div>`).join('');

        for (const e of eintraege) {
            const schieber = document.getElementById(`${praefix}-${e.schluessel}`);
            const anzeige = document.getElementById(`${praefix}-${e.schluessel}-value`);
            if (!schieber) continue;
            schieber.oninput = () => {
                const wert = parseFloat(schieber.value);
                if (anzeige) anzeige.textContent = wert.toFixed(2);
                uebernehmen(e.schluessel, wert);
                this.netzNachladenBald(figur);
            };
        }
    }

    _lage(figur) {
        const orte = Panel.felder('char-pos-x', 'char-pos-y', 'char-pos-z');
        if (orte) {
            const setzen = () => figur.position.set(
                ...orte.map(f => parseFloat(f.value)));
            orte.forEach(f => { f.oninput = setzen; });
        }
        const winkel = Panel.felder('char-rot-x', 'char-rot-y', 'char-rot-z');
        if (winkel) {
            const setzen = () => figur.rotation.set(
                ...winkel.map(f => parseFloat(f.value) / Figurpanel.GRAD));
            winkel.forEach(f => { f.oninput = setzen; });
        }
    }

    // --------------------------------------------------------- Netz nachladen

    /**
     * Nachladen anmelden. Erst wenn der Schieber RUHE_MS still steht, geht eine
     * Anfrage raus — sonst waeren es Dutzende à 5,2 MB je Schieberzug.
     */
    netzNachladenBald(figur) {
        clearTimeout(this._wartend);
        this._wartend = setTimeout(() => this.netzNachladen(figur),
                                   Figurpanel.RUHE_MS);
    }

    async netzNachladen(figur) {
        // Laeuft schon eine Anfrage, wird die naechste vorgemerkt statt
        // parallel gestartet: Zwei Antworten in falscher Reihenfolge wuerden
        // sonst ein veraltetes Netz zurueckschreiben.
        if (this._laufend) {
            this._nachholen = figur;
            return;
        }
        this._laufend = true;
        try {
            await this._holen(figur);
        } finally {
            this._laufend = false;
            const naechste = this._nachholen;
            this._nachholen = null;
            if (naechste) this.netzNachladen(naechste);
        }
    }

    async _holen(figur) {
        try {
            const antwort = await fetch('/api/character/mesh/?' + this._frage(figur));
            if (!antwort.ok) throw new Error('Netz-API: ' + antwort.status);
            const daten = await antwort.json();
            const koerper = figur.children.find(
                k => k.isMesh && !k.userData.isHair && !k.userData.isGarment);
            if (!koerper) {
                console.warn('Kein Koerpernetz zum Aktualisieren gefunden');
                return;
            }
            const punkte = Kodierung.blenderNachThree(
                Kodierung.zuFloat32(daten.vertices));
            koerper.geometry.attributes.position.array.set(punkte);
            koerper.geometry.attributes.position.needsUpdate = true;

            if (daten.normals) {
                const normalen = Kodierung.blenderNachThree(
                    Kodierung.zuFloat32(daten.normals));
                koerper.geometry.attributes.normal.array.set(normalen);
                koerper.geometry.attributes.normal.needsUpdate = true;
            } else {
                koerper.geometry.computeVertexNormals();
            }
        } catch (fehler) {
            console.error('Netz nicht neu ladbar:', fehler);
        }
    }

    /**
     * Anfrage aus Körpertyp, Morphs und Meta-Werten — dieselbe, die auch das
     * Laden einer Vorgabe und das Anpassen von Kleidung brauchen. Sie stand
     * dreimal im Projekt und liegt jetzt in laden/koerperfrage.js.
     */
    _frage(figur) {
        const frage = new Koerperfrage(figur.userData).felder();
        if (!frage.has('body_type')) {
            frage.set('body_type', Koerperfrage.VORGABE_KOERPER);
        }
        return frage.toString();
    }
}
