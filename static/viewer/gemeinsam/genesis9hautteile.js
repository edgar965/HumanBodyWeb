import * as THREE from 'three';
import { Bildmittel } from './bildmittel.js';
import { Protokoll } from './protokoll.js';
import { Genesis9hautteilmerkmale } from './genesis9hautteilmerkmale.js';

/**
 * Genesis9hautteile — Hautfarbe und Tattoo je Körperteil (25.10.2026, Edgar: „bei den Reglern für die einzelnen Körperteile mach jeweils auch Regler für die Textur“ und
 * „den Code für Haut-KI kannst du einige Punkte entnehmen, z.B. Tattoos, Hautfarbe usw“). Die Regler stehen im Abschnitt „Eigen“ (`Genesis9hautteilregler`), gerechnet wird im
 * Shader der Hautebenen (`Genesis9hautteileGLSL`) — ein Zug baut weder Körper noch Programm.
 *
 * WO: die Teilkarte vom Server (`G9hautteile`, Produkt `teile` der Hautkarten, Fassung 4): je Texel die Anteile der 24 Kanäle `TEILE` (weich, 50/50 an der Grenze) — in der
 * Feinheit der Formregler (Edgar: „pro Körperteil brauche ich die Texturregler, z.B. Nase, Augen, Rumpf, wo sind die???“): Nase, Mund, Augen, Brauen, Ohren, Brust, Hüfte
 * und Gesäß aus denselben Punktmengen wie die Formregler. Die alten Ziele `kopf` und `rumpf` gelten weiter (jetzt „ganz“: alle Teile des Kopfs bzw. Rumpfs).
 * WERTE in `inst.hautebenen` (gehen mit „Modell speichern“ und der eigenen Haut mit — die nimmt nur Zahlen bis ±1000 und höchstens 80 Felder):
 *   eigen_farbe_<ziel>            Stärke %          eigen_farbe_<ziel>_r/_g/_b     Zielfarbe sRGB 0–255 (fehlt = mittlere Hautfarbe, wirkt also nicht)
 *   eigen_tattoo_<ziel>           Deckung %         _muster 1–999, _groesse mm, _flaeche %, _stil (0 Ranken, 1 Flächen), _r/_g/_b Tinte
 * HAUTFARBE wie `Hautfaerbung.ton` der Haut-KI: je Kanal linear Ziel ÷ Mittel der Haut — Poren, Lippen und Wangen bleiben als Verhältnis, nur der Grundton wechselt;
 * Faktor = mix(1, Ziel/Mittel, Stärke). Das Mittel ist die mittlere lineare Farbe der Hautkarten Kopf, Rumpf, Arme, Beine (`Bildmittel`).
 * „beide“ (Arme, Hände, Beine, Füße) ist eine eigene Ebene über beiden Seiten: ihr Faktor multipliziert sich mit dem des Einzelreglers; ihr Tattoo ist gespiegelt (|x|).
 * TATTOO wie `Hautfaerbung.tattoos`: Linien aus den Nulldurchgängen eines groben Rauschens (Ranken) oder Flächen über einer Schwelle, im Objektraum (haftet an der Haut),
 * in Flecken aus gröberem Rauschen (Fläche %). Tintenvorgabe TINTE_DUNKEL der Haut-KI. Höchstens `TATTOO_MAX` Tattoos gleichzeitig. WO ein Tattoo liegt, sagt `uHtTatC`:
 * x = −2 die ganze Haut, x = −3 die Teile der Bitmaske in w (Bit i = Teil i, 24 Bit sind in float32 exakt), z = gespiegelt.
 */
export class Genesis9hautteile {

    /** Kanalreihenfolge der Teilkarte (`G9hautteile.TEILE`, Server gleich). */
    static TEILE = ['kopfhaut', 'gesicht', 'mund', 'nase', 'auge_links', 'auge_rechts', 'braue_links', 'braue_rechts', 'ohr_links', 'ohr_rechts', 'hals', 'bauch_ruecken',
                    'brust_links', 'brust_rechts', 'gesaess_links', 'gesaess_rechts', 'arm_links', 'arm_rechts', 'hand_links', 'hand_rechts', 'bein_links', 'bein_rechts',
                    'fuss_links', 'fuss_rechts'];
    static KANAELE = 24;
    static KOPF = ['kopfhaut', 'gesicht', 'mund', 'nase', 'auge_links', 'auge_rechts', 'braue_links', 'braue_rechts', 'ohr_links', 'ohr_rechts'];
    static RUMPF = ['bauch_ruecken', 'brust_links', 'brust_rechts', 'gesaess_links', 'gesaess_rechts'];
    static TATTOO_MAX = 6;
    static PRAEFIX = 'eigen_';
    static HAUT = /^(Head|Body|Arms|Legs)$/;

    /** Reihenfolge = Reihenfolge im Bedienfeld. */
    static ZIELE = [
        // Die ganze Haut (Edgar, 25.10.2026: „ich sehe die Hautregler nicht (gesamt)“) — Gruppe „Haut“ vor den Körperteilen; Tattoo-Maske −2 = überall
        { ziel: 'gesamt', gruppe: 'Haut', name: 'gesamt', teile: [...Genesis9hautteile.TEILE], ganz: true },
        // Kopf und Rumpf in der Reihenfolge der Formregler (`G9eigenkatalog`); `kopf`/`rumpf` = der ganze Kopf bzw. Rumpf (Schlüssel von Fassung 3, bleiben gültig)
        { ziel: 'kopf', gruppe: 'Kopf', name: 'Kopf (ganz)', teile: Genesis9hautteile.KOPF },
        { ziel: 'gesicht', gruppe: 'Kopf', name: 'Gesicht', teile: ['gesicht'] },
        { ziel: 'kopfhaut', gruppe: 'Kopf', name: 'Kopfhaut', teile: ['kopfhaut'] },
        { ziel: 'mund', gruppe: 'Kopf', name: 'Mund', teile: ['mund'] },
        { ziel: 'nase', gruppe: 'Kopf', name: 'Nase', teile: ['nase'] },
        ...Genesis9hautteile._paar('augen', 'auge', 'Kopf', 'Augen', 'Auge'),
        ...Genesis9hautteile._paar('brauen', 'braue', 'Kopf', 'Augenbrauen', 'Augenbraue'),
        ...Genesis9hautteile._paar('ohren', 'ohr', 'Kopf', 'Ohren', 'Ohr'),
        { ziel: 'hals', gruppe: 'Hals', name: 'Hals', teile: ['hals'] },
        { ziel: 'rumpf', gruppe: 'Rumpf', name: 'Rumpf (ganz)', teile: Genesis9hautteile.RUMPF },
        ...Genesis9hautteile._paar('brust', 'brust', 'Rumpf', 'Brust', 'Brust'),
        ...Genesis9hautteile._paar('gesaess', 'gesaess', 'Rumpf', 'Hüfte und Gesäß', 'Hüfte und Gesäß'),
        { ziel: 'bauch_ruecken', gruppe: 'Rumpf', name: 'Bauch und Rücken', teile: ['bauch_ruecken'] },
        ...Genesis9hautteile._paar('arme', 'arm', 'Arme', 'Arme', 'Arm'),
        ...Genesis9hautteile._paar('haende', 'hand', 'Hände', 'Hände', 'Hand'),
        ...Genesis9hautteile._paar('beine', 'bein', 'Beine', 'Beine', 'Bein'),
        ...Genesis9hautteile._paar('fuesse', 'fuss', 'Füße', 'Füße', 'Fuß'),
    ];

    static _paar(beide, teil, gruppe, mehrzahl, einzahl) {
        return [
            { ziel: beide, gruppe, name: `${mehrzahl} (beide)`, teile: [`${teil}_links`, `${teil}_rechts`], beide: true },
            { ziel: `${teil}_links`, gruppe, name: `${einzahl} links`, teile: [`${teil}_links`] },
            { ziel: `${teil}_rechts`, gruppe, name: `${einzahl} rechts`, teile: [`${teil}_rechts`] },
        ];
    }

    /** Vorgaben je Feld (Tinte: TINTE_DUNKEL der Haut-KI, sRGB 0,06/0,07/0,10). */
    static VORGABE = {
        farbe: { '': 0 },
        tattoo: { '': 0, muster: 1, groesse: 25, flaeche: 30, stil: 0, r: 15, g: 18, b: 26 },
        merkmal: Genesis9hautteilmerkmale.vorgabe(),          // Hautebenen je Teil (26.10.2026, `Genesis9hautteilmerkmale`)
    };

    static schluessel(art, ziel, feld = '') {
        return `${Genesis9hautteile.PRAEFIX}${art}_${ziel}${feld ? `_${feld}` : ''}`;
    }

    /** Ein Wert (Zahl) oder die Vorgabe; bei der Zielfarbe ohne Eintrag `null`. */
    static wert(inst, art, ziel, feld = '') {
        const w = Number(inst?.hautebenen?.[Genesis9hautteile.schluessel(art, ziel, feld)]);
        if (Number.isFinite(w)) return w;
        return Genesis9hautteile.VORGABE[art][feld] ?? null;
    }

    /** Werte schreiben (`{schluessel: zahl|null}`, null = Vorgabe). Anwenden muss der Rufer (`Genesis9hautebenen.anwenden`). */
    static setzen(inst, eintraege) {
        inst.hautebenen = { ...(inst.hautebenen || {}) };
        for (const [k, v] of Object.entries(eintraege || {})) {
            const zahl = Number(v);
            if (v === null || v === '' || !Number.isFinite(zahl)) delete inst.hautebenen[k];
            else inst.hautebenen[k] = Math.round(zahl);
        }
    }

    /** Alle Schlüssel eines Reglers (für „Zurücksetzen“). */
    static felder(art, ziel) {
        return Object.keys(Genesis9hautteile.VORGABE[art]).concat(art === 'farbe' ? ['r', 'g', 'b'] : []).map(f => Genesis9hautteile.schluessel(art, ziel, f));
    }

    static aktiv(inst) {
        return Genesis9hautteile.ZIELE.some(z => Genesis9hautteile.wert(inst, 'farbe', z.ziel) > 0 || Genesis9hautteile.wert(inst, 'tattoo', z.ziel) > 0)
            || Genesis9hautteile._merkmale(inst).an;
    }

    static _merkmale(inst) {
        return Genesis9hautteilmerkmale.rechnen(Genesis9hautteile.ZIELE, Genesis9hautteile.TEILE, (art, ziel, feld) => Genesis9hautteile.wert(inst, art, ziel, feld));
    }

    // ------------------------------------------------------------------ Farbe

    static linear(byte) { return Bildmittel.linear(Math.max(0, Math.min(255, byte))); }

    static srgbByte(lin) {
        const c = Math.max(0, Math.min(1, lin));
        return Math.round(255 * (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055));
    }

    /** Die mittlere lineare Farbe der Hautkarten (Kopf, Rumpf, Arme, Beine) — oder null, solange kein Bild da ist. */
    static mittel(inst) {
        const material = inst?.bodyMesh?.material;
        const farben = (Array.isArray(material) ? material : [material])
            .filter(m => m?.map && Genesis9hautteile.HAUT.test(m.userData?.gruppe || ''))
            .map(m => Bildmittel.von(m.map)).filter(Boolean);
        if (!farben.length) return null;
        return [0, 1, 2].map(k => farben.reduce((s, f) => s + f[k], 0) / farben.length);
    }

    /** Die Zielfarbe eines Farbreglers als sRGB-Bytes (ohne Eintrag: die mittlere Hautfarbe, sonst ein mittlerer Hautton). */
    static zielfarbe(inst, ziel) {
        const r = Genesis9hautteile.wert(inst, 'farbe', ziel, 'r');
        if (r !== null) return [r, Genesis9hautteile.wert(inst, 'farbe', ziel, 'g') ?? r, Genesis9hautteile.wert(inst, 'farbe', ziel, 'b') ?? r];
        const m = Genesis9hautteile.mittel(inst);
        return m ? m.map(Genesis9hautteile.srgbByte) : [196, 150, 125];
    }

    // ------------------------------------------------------------------ Shader

    /** Die Uniforms beim Einrichten der Hautebenen (`platzhalter`: 1×1-Bild, bis die Karte da ist). */
    static uniforms(platzhalter) {
        const n = Genesis9hautteile.TATTOO_MAX;
        return {
            uHtTeilAn: { value: 0 }, uHtTeile: { value: platzhalter },
            uHtTeilF: { value: Array.from({ length: Genesis9hautteile.KANAELE }, () => new THREE.Vector3(1, 1, 1)) },
            uHtTatA: { value: Array.from({ length: n }, () => new THREE.Vector4()) },
            uHtTatB: { value: Array.from({ length: n }, () => new THREE.Vector4()) },
            uHtTatC: { value: Array.from({ length: n }, () => new THREE.Vector4()) },
            ...Genesis9hautteilmerkmale.uniforms(),
        };
    }

    static _gewarnt = new Set();

    static _warnen(text) {
        if (Genesis9hautteile._gewarnt.has(text)) return;
        Genesis9hautteile._gewarnt.add(text);
        Protokoll.warnung('Hautteile', text);
    }

    /** → `{an, fehlt, faktoren: [[r,g,b] × KANAELE], tattoos: [{a, b, c}]}` aus den Werten der Figur (einmal je `Genesis9hautebenen.anwenden`). */
    static rechnen(inst) {
        const faktoren = Array.from({ length: Genesis9hautteile.KANAELE }, () => [1, 1, 1]);
        const tattoos = [];
        let an = false, fehlt = false;
        const mittel = Genesis9hautteile.mittel(inst);
        for (const z of Genesis9hautteile.ZIELE) {
            const staerke = Genesis9hautteile.wert(inst, 'farbe', z.ziel) / 100;
            if (staerke > 0) {
                an = true;
                if (!mittel) fehlt = true;
                else {
                    const ziel = Genesis9hautteile.zielfarbe(inst, z.ziel).map(Genesis9hautteile.linear);
                    const f = ziel.map((c, k) => Math.max(0.02, Math.min(30, 1 + Math.min(1, staerke) * (c / Math.max(mittel[k], 1e-4) - 1))));
                    for (const teil of z.teile) faktoren[Genesis9hautteile.TEILE.indexOf(teil)].forEach((_, k, a) => { a[k] *= f[k]; });
                }
            }
            const deckung = Genesis9hautteile.wert(inst, 'tattoo', z.ziel) / 100;
            if (deckung > 0) {
                an = true;
                if (tattoos.length >= Genesis9hautteile.TATTOO_MAX) {
                    Genesis9hautteile._warnen(`Mehr als ${Genesis9hautteile.TATTOO_MAX} Tattoos — die übrigen werden nicht gezeigt.`);
                    continue;
                }
                tattoos.push(Genesis9hautteile._tattoo(inst, z, Math.min(1, deckung)));
            }
        }
        const merkmale = Genesis9hautteile._merkmale(inst);
        return { an: an || merkmale.an, fehlt, faktoren, tattoos, merkmale };
    }

    static NACHHOLEN_MS = 1500;
    static NACHHOLEN_MAX = 20;

    /**
     * Hautfarbe gestellt, aber noch kein Hautbild gelesen (gleich nach dem Laden einer gespeicherten Figur kommen die Bilder nach `Genesis9hautebenen.anwenden`): bis zu
     * `NACHHOLEN_MAX`-mal später noch einmal anwenden, dann eine Warnung im Protokoll.
     */
    static nachholen(inst, rechnung, anwenden) {
        if (!rechnung.fehlt) { inst._hautteileVersuche = 0; return; }
        inst._hautteileVersuche = (inst._hautteileVersuche || 0) + 1;
        if (inst._hautteileVersuche <= Genesis9hautteile.NACHHOLEN_MAX) setTimeout(anwenden, Genesis9hautteile.NACHHOLEN_MS);
        else Genesis9hautteile._warnen('Kein Hautbild lesbar — die Hautfarbe je Körperteil bleibt ohne Wirkung (Bildmittel ohne Bild oder ohne Leinwand).');
    }

    static _tattoo(inst, z, deckung) {
        const w = feld => Genesis9hautteile.wert(inst, 'tattoo', z.ziel, feld);
        const tinte = ['r', 'g', 'b'].map(k => Genesis9hautteile.linear(w(k)));
        return {
            a: [deckung, Math.max(2, w('groesse')) / 1000, Genesis9hautteile.schwelle(w('flaeche') / 100), w('stil') >= 0.5 ? 1 : 0],
            b: [...tinte, w('muster')],
            c: z.ganz ? [-2, 0, 0, 0] : [-3, 0, z.beide ? 1 : 0, Genesis9hautteile.maske(z.teile)],
        };
    }

    /** Bitmaske der Teile (Bit i = `TEILE[i]`) — höchstens 24 Bit, in float32 exakt. */
    static maske(teile) {
        return [...new Set(teile)].reduce((m, t) => m + 2 ** Genesis9hautteile.TEILE.indexOf(t), 0);
    }

    /**
     * Schwelle der Fleckenmaske für einen Flächenanteil: `g9Fbm` ist gemessen etwa normal mit Mittel 0,500 und Streuung 0,114 (`Genesis9hautrauschenGLSL`) —
     * Anteil f über der Schwelle 0,5 + 0,114·z(1 − f). 0 % = nie, 100 % = überall.
     */
    static schwelle(f) {
        if (f >= 0.995) return -1;
        if (f <= 0.005) return 2;
        return 0.5 + 0.114 * Genesis9hautteile._quantil(1 - f);
    }

    /** Quantil der Standardnormalverteilung (Abramowitz/Stegun 26.2.23, Fehler < 4,5·10⁻⁴). */
    static _quantil(p) {
        const q = p < 0.5 ? p : 1 - p;
        const t = Math.sqrt(-2 * Math.log(q));
        const z = t - (2.515517 + 0.802853 * t + 0.010328 * t * t) / (1 + 1.432788 * t + 0.189269 * t * t + 0.001308 * t * t * t);
        return p < 0.5 ? -z : z;
    }

    /** Die Rechnung in die Uniforms eines Materials; `bereit` = die Teilkarte liegt schon an. */
    static eintragen(u, rechnung, bereit) {
        if (!u.uHtTeilF) return;
        u.uHtTeilAn.value = rechnung.an && bereit ? 1 : 0;
        rechnung.faktoren.forEach((f, i) => u.uHtTeilF.value[i].set(...f));
        for (let i = 0; i < Genesis9hautteile.TATTOO_MAX; i++) {
            const t = rechnung.tattoos[i];
            u.uHtTatA.value[i].set(...(t ? t.a : [0, 0.025, 2, 0]));
            u.uHtTatB.value[i].set(...(t ? t.b : [0, 0, 0, 0]));
            u.uHtTatC.value[i].set(...(t ? t.c : [0, 0, 0, 0]));
        }
        if (rechnung.merkmale) Genesis9hautteilmerkmale.eintragen(u, { an: rechnung.merkmale.an && bereit, werte: rechnung.merkmale.werte });
    }

    /** Die Teilkarte ist da: ohne Mip-Stufen (sonst mischen die sechs Teilbilder an ihren Rändern), an den Shader. */
    static bild(h, bild) {
        bild.generateMipmaps = false;
        bild.minFilter = THREE.LinearFilter;
        bild.magFilter = THREE.LinearFilter;
        bild.needsUpdate = true;
        h.uniforms.uHtTeile.value = bild;
        h.uniforms.uHtTeilAn.value = 1;
        h.teileBereit = true;
    }
}
