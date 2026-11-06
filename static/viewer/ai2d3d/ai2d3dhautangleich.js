/**
 * Ai2d3dhautangleich — Regler „Haut angleichen“ unter dem Feld Genesis-Ergebnis (05.11.2026, Edgar: „Ein paar slider wo man die Haut anpasst, z.B. mehr von Vorne auf die anderen flächen, oder
 * mehr von seitlich? Der Ton sollte hauptsächlich angepasst werden, die Textur (Haare, Brustwarzen, Hautflecken ) sollten bleiben“).
 *
 * Ein Schritt nach dem Job: „Vorbereiten“ rechnet einmal die Felder (`KoerperKI_Fotos.Hautangleich`, Server `Ai2d3dhautangleich`), danach läuft jeder Regler im Browser ohne Rechenlauf
 * (`Ai2d3dhautangleichgl`). Zu sehen ist das gleich im Feld, an der stehenden wie an der bewegten Figur (`_tauschen`); auf der Platte und im Export erst nach „Speichern“. Alle Regler auf 0 lassen alles, wie es war.
 * Jeder Regler wirkt für sich (Edgar, 05.11.2026: „ich möchte die Änderungen gleich sehen, wenn ich regler ändere!“), nur die Reichweite wirkt über die ersten drei Regler.
 */
import * as THREE from 'three';
import { Aktionsprotokoll } from '../gemeinsam/aktionsprotokoll.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Serverfehler } from '../gemeinsam/serverfehler.js';
import { Mesh3daizeichenflaeche } from '../mesh3dai/mesh3daizeichenflaeche.js';
import { Ai2d3dhautangleichgl } from './ai2d3dhautangleichgl.js';

export class Ai2d3dhautangleich {
    static VORGABE = { dunkel: 0, hell: 0, unsichtbar: 0, zeichnung: 0, bezug: 0, reichweite: 0.5 };
    static KACHEL = /^10\d\d\.jpg$/;
    static HAUTBILD = /\/figur\/[^/]+\/bild\/[^/]+$/;
    static PAUSE_MS = 2000;
    static NACHHOLEN_MS = 5000;

    /** @param {HTMLElement|null} element `#ai2d3d-hautangleich` @param seite `Ai2d3dseite` */
    static binden(element, seite) {
        return element ? new Ai2d3dhautangleich(element, seite) : null;
    }

    constructor(element, seite) {
        this.element = element;
        this.seite = seite;
        this.adresse = element.dataset.adresse;
        this.gl = null;
        this.stand = null;
        this.offen = false;
        this.angefasst = false;         // Griffe, solange die Figur noch lädt: Sie gelten, sobald die Regler stehen
        this.eigen = false;             // erst nach dem ersten Griff zeigt das Feld die gerechneten Kacheln
        this.ziele = new WeakMap();     // Bild der Figur → Ziel seiner Kachel (`_ziel`)
        this.getauscht = 0;             // so viele Bilder trug der letzte Durchgang (`_melden`)
        this.gemeldet = -Infinity;
        this.meldung = element.querySelector('[data-meldung]');
        this.vorbereitenKnopf = element.querySelector('[data-vorbereiten]');
        this.flaeche = element.querySelector('[data-regler]');
        this.regler = [...element.querySelectorAll('input[type="range"]')];
        this.speichernKnopf = element.querySelector('[data-speichern]');
        this.zuruecksetzenKnopf = element.querySelector('[data-zuruecksetzen]');
        this.vorbereitenKnopf.addEventListener('click', () => this._vorbereiten());
        this.speichernKnopf.addEventListener('click', () => this._speichern());
        this.zuruecksetzenKnopf.addEventListener('click', () => this._zuruecksetzen());
        for (const r of this.regler) r.addEventListener('input', () => this._griff(r));
        this._beschriften();
        this._laden();
    }

    _sagen(text) {
        this.meldung.textContent = text;
    }

    _griff(regler) {
        this.angefasst = true;
        this._beschriften();
        const { dunkel, hell, unsichtbar } = this.werte;
        if (regler.name === 'reichweite' && !(dunkel || hell || unsichtbar)) this._sagen('Die Reichweite wirkt erst, wenn einer der ersten drei Regler über 0 steht.');
        this._planen();
    }

    get werte() {
        return Object.fromEntries(this.regler.map(r => [r.name, Number(r.value) / 100]));
    }

    _setzen(werte) {
        for (const r of this.regler) r.value = Math.round((werte[r.name] ?? 0) * 100);
        this._beschriften();
    }

    _beschriften() {
        for (const r of this.regler) r.closest('label').querySelector('output').textContent = `${r.value} %`;
    }

    /** Eine Antwort des Servers; ohne Erfolg ein Fehler mit `status`, den `Serverfehler` einordnen kann. */
    static async _holen(adresse) {
        const antwort = await fetch(adresse);
        if (!antwort.ok) throw Object.assign(new Error(`HTTP ${antwort.status}`), { status: antwort.status, adresse });
        return antwort;
    }

    /**
     * Stand holen und zeigen. Der Autoreload reißt Anfragen ab, sobald nebenan eine Sitzung Python speichert (05.11.2026 19:45:29, mitten im Warten auf „Vorbereiten“ von Edgar 1: das Feld blieb
     * bei „Failed to fetch“ stehen, obwohl der Lauf fertig wurde). Ist der Server weg, holt das Feld sich alles selbst nach (`Serverfehler.text`); andere Fehler bleiben stehen.
     */
    async _laden() {
        try {
            this.stand = await (await Ai2d3dhautangleich._holen(this.adresse)).json();
            await this._zeigen();
        } catch (fehler) {
            if (fehler.status === 404) {
                this.element.hidden = true;
                return;
            }
            const weg = Serverfehler.text(fehler);
            this._sagen(weg ? `${weg} Das Feld versucht es weiter.` : `Nicht geladen: ${fehler.message}`);
            if (weg) setTimeout(() => this._laden(), Ai2d3dhautangleich.NACHHOLEN_MS);
        }
    }

    async _zeigen() {
        const s = this.stand;
        this.vorbereitenKnopf.hidden = s.bereit || s.laeuft;
        this.flaeche.hidden = !s.bereit;
        if (s.laeuft) {
            this._sagen('Die Haut wird vorbereitet …');
            setTimeout(() => this._laden(), Ai2d3dhautangleich.PAUSE_MS);
        } else if (!s.bereit) {
            this._sagen(s.fehler ? `Vorbereiten ist fehlgeschlagen: ${s.fehler}` : 'Einmal vorbereiten, danach wirken die Regler sofort.');
        } else if (!this.gl) {
            this._sagen('Regler werden geladen …');
            await this._aufbauen();
        }
    }

    /**
     * Das Bild einer Figur → sein Name in `10xx.jpg`, null für alles andere. Die stille Figur trägt die Namen von `bilder` (`m0.jpg`), die bewegte die Kacheln (`Mesh3daitesthaut.kacheln`).
     * Nur Adressen unter `/figur/<g>/bild/` sind Haut: Die Stücke heißen ebenso (`/kleid/<g>/k/ki_hose/bild/m0.jpg`), sonst bekommt die Hose die Hautkachel.
     */
    _datei(karte) {
        const pfad = String(karte?.userData?.adresse ?? karte?.image?.src ?? '').split('?')[0];
        if (!Ai2d3dhautangleich.HAUTBILD.test(pfad)) return null;
        const name = pfad.split('/').pop(), datei = this.stand.bilder[name] ?? name;
        return Ai2d3dhautangleich.KACHEL.test(datei) ? datei : null;
    }

    /** Die Körper-Bilder der stillen Figur im Feld Genesis-Ergebnis. */
    _hautbilder() {
        const figur = this.seite.genesiszeile?.eintraege?.[1]?.figur;
        return figur?.koerper ? [figur.koerper.an.material].flat().map(m => m.map).filter(k => this._datei(k)) : [];
    }

    /** Das Renderziel zu einem Bild der Figur, null ohne Kachel; das Ergebnis bleibt nur für Bilder, die ihre Quelle schon kennen. */
    _ziel(karte) {
        if (this.ziele.has(karte)) return this.ziele.get(karte);
        const datei = this._datei(karte), ziel = datei ? this.gl.kacheln.get(Number(datei.slice(0, 4)))?.ziel ?? null : null;
        if (karte.userData?.adresse || karte.image?.src) this.ziele.set(karte, ziel);
        return ziel;
    }

    /**
     * Für EINEN Durchgang im Feld die Hautbilder gegen die gerechneten Kacheln tauschen, an jeder Figur im Feld, auch der bewegten (`Mesh3daifigurbewegung` baut ein eigenes Modell), → Rückweg.
     * Dauerhaft getauscht scheiterte der Export: `GLTFExporter` liest `material.map.image`, ein Renderziel hat kein Bild.
     */
    _tauschen() {
        if (!this.eigen) return null;
        const getauscht = [];
        this.ansicht.inhalt.traverse(o => {
            for (const material of [o.material].flat()) {
                const ziel = material?.map ? this._ziel(material.map) : null;
                if (ziel) {
                    getauscht.push([material, material.map]);
                    material.map = ziel.texture;
                }
            }
        });
        this.getauscht = getauscht.length;
        return () => { for (const [material, karte] of getauscht) material.map = karte; };
    }

    /** Das Feld als 32 × 32 Punkte, wie es auf der Seite steht. */
    _feldbild() {
        const klein = document.createElement('canvas');
        klein.width = klein.height = 32;
        const z = klein.getContext('2d', { willReadFrequently: true });
        z.drawImage(this.ansicht.leinwand, 0, 0, 32, 32);
        return z.getImageData(0, 0, 32, 32).data;
    }

    /**
     * Ins `client.log`, höchstens einmal je Sekunde: Wurde die Figur nach dem Griff wirklich anders gezeichnet? `getauscht` 0 = die Hautbilder wurden nicht gefunden.
     * `feld_abw` ist die größte Änderung an 32 × 32 Punkten: 0 trotz Tausch hieß am 05.11.2026, dass ein Regler den anderen überdeckte (Chrome und Opera gleich, Prüfung `griffe` in `Hautangleichpruefung`).
     */
    _melden(vorher) {
        this.gemeldet = performance.now();
        const nachher = this._feldbild();
        let abw = 0;
        for (let i = 0; i < nachher.length; i++) abw = Math.max(abw, Math.abs(nachher[i] - vorher[i]));
        const r = Mesh3daizeichenflaeche.renderer(), gl = r.getContext(), info = gl.getExtension('WEBGL_debug_renderer_info');
        Aktionsprotokoll.melden('haut_griff', `getauscht=${this.getauscht} feld_abw=${abw} im_bild=${this.ansicht._imBild} art=${this.ansicht.ansichtsart} kontext_weg=${gl.isContextLost()} karte=${info ? gl.getParameter(info.UNMASKED_RENDERER_WEBGL) : '?'}`);
    }

    async _aufbauen() {
        const eintrag = this.seite.genesiszeile?.eintraege?.[1];
        await eintrag?.figur?.bereit;
        const haut = await this._warten();
        if (!haut.length) throw new Error('Figur ohne Hautkacheln');
        const [felder, netz] = await Promise.all([this.stand.felder, this.stand.netz].map(async a => (await Ai2d3dhautangleich._holen(a)).arrayBuffer()));
        const [originale, zeichnung] = await Promise.all([this.stand.original, this.stand.zeichnung].map(a => Ai2d3dhautangleich._bilder(a)));
        this.gl = new Ai2d3dhautangleichgl(Mesh3daizeichenflaeche.renderer(), this.stand.kopf, new Float32Array(felder), netz, originale, zeichnung, haut[0]);
        this.ansicht = eintrag.ansicht;
        this.ansicht.hauttausch = () => this._tauschen();
        if (this.angefasst) this._planen();
        else this._setzen(this.stand.regler ?? Ai2d3dhautangleich.VORGABE);
        this._sagen(this.stand.regler ? 'Gespeicherter Stand.' : 'Regler ziehen, die Figur ändert sich sofort, auch während der Animation. Gespeichert wird erst mit „Speichern“.');
    }

    /** {Kachel: Adresse} → {Kachel: Textur}. */
    static async _bilder(adressen) {
        const lader = new THREE.TextureLoader(), aus = {};
        await Promise.all(Object.entries(adressen).map(async ([kachel, adresse]) => {
            const bild = URL.createObjectURL(await (await Ai2d3dhautangleich._holen(adresse)).blob());     // über `_holen`: der TextureLoader wirft bei einer abgerissenen Verbindung nur ein Ereignis ohne Text
            const t = await lader.loadAsync(bild);
            URL.revokeObjectURL(bild);
            t.colorSpace = THREE.SRGBColorSpace;
            t.generateMipmaps = false;
            t.minFilter = THREE.LinearFilter;
            aus[kachel] = t;
        }));
        return aus;
    }

    /** Die Bilder der Figur kommen nach dem Bau: warten, bis jedes Hautmaterial sein Bild kennt. */
    async _warten() {
        for (let i = 0; i < 40; i++) {
            const haut = this._hautbilder();
            if (haut.length) return haut;
            await new Promise(fertig => setTimeout(fertig, 250));
        }
        return [];
    }

    _planen() {
        if (this.offen || !this.gl) return;
        this.offen = true;
        requestAnimationFrame(() => {
            this.offen = false;
            const faellig = performance.now() - this.gemeldet >= 1000, vorher = faellig ? this._feldbild() : null;
            this.gl.anwenden(this.werte);
            this.eigen = true;
            this.ansicht.zeichnen();
            if (faellig) this._melden(vorher);
        });
    }

    async _vorbereiten() {
        this.vorbereitenKnopf.disabled = true;
        this._sagen('Die Haut wird vorbereitet …');
        try {
            this.stand = await Serverabruf.senden(`${this.adresse}vorbereiten/`, {});
            await this._zeigen();
        } catch (fehler) {
            this._sagen(`Vorbereiten ging nicht: ${fehler.message}`);
        } finally {
            this.vorbereitenKnopf.disabled = false;
        }
    }

    async _speichern() {
        this.speichernKnopf.disabled = true;
        this._sagen('Wird gespeichert …');
        try {
            this.gl.anwenden(this.werte);
            const formular = new FormData();
            formular.append('regler', JSON.stringify(this.werte));
            for (const kachel of this.gl.kacheln.keys()) formular.append(`k${kachel}`, await this.gl.jpeg(kachel), `${kachel}.jpg`);
            this.stand = await Serverabruf.formular(`${this.adresse}speichern/`, formular);
            this._sagen('Gespeichert. Export und Animation nehmen ab jetzt diese Haut.');
        } catch (fehler) {
            this._sagen(`Nicht gespeichert: ${fehler.message}`);
        } finally {
            this.speichernKnopf.disabled = false;
        }
    }

    async _zuruecksetzen() {
        this.zuruecksetzenKnopf.disabled = true;
        try {
            this.stand = await Serverabruf.senden(`${this.adresse}zuruecksetzen/`, {});
            this._setzen(Ai2d3dhautangleich.VORGABE);
            this._planen();
            this._sagen('Haut steht wieder wie vor dem Angleichen.');
        } catch (fehler) {
            this._sagen(`Nicht zurückgesetzt: ${fehler.message}`);
        } finally {
            this.zuruecksetzenKnopf.disabled = false;
        }
    }
}
