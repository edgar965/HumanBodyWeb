import * as THREE from 'three';
import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { Eigenhaut } from './eigenhaut.js';
import { Modell } from './modell.js';
import { float32ToBase64 } from './kodierung.js';
import { Smpldetails } from './smpldetails.js';
import { Smplnetz } from './smplnetz.js';

/**
 * SmplModell — ein Referenzkörper von GarmentCode oder ein SMPL-X-Körper,
 * als `Modell` für jede Seite.
 *
 * WARUM (Edgar, 06.09.2026: „keine experimente, baue erstmal das Online tool
 * nach!"): Das Online-Tool drapiert auf `mean_all` mit dessen vorgegebenen
 * Maßen. Für diese Körper (mean_all, mean_female, mean_male, die zwei
 * SMPL-X-Durchschnitte) kennt GarmentCode Maße und Segmentierung — der
 * GarmentCode-Reiter läuft auf ihnen exakt wie das Tool. Das ist die
 * Messlatte für die HumanBody-Figur.
 *
 * SEIT 15.09.2026 SMPL-X (Edgar: „die SMPL Modelle auf SMPL-X umstellen (also
 * inkl. Gesichtsknochen)"): Netz 10.475 Punkte, Skelett 55 Gelenke — Körper,
 * Kiefer (`Jaw`), Augen (`Left_eye`/`Right_eye`), 30 Finger — und die
 * Hautgewichte des Modells; alles vom Server (`core/dienste/smplxrig.py`).
 * GarmentCodes eigene Körper bekommen dasselbe Skelett übertragen.
 *
 * Das Netz kommt vom Server in Metern mit Y oben — so rechnet GarmentCode,
 * und so rechnet Three.js; nichts wird gedreht. Keine Morphs.
 *
 * Dieselben Felder wie `CharacterInstance` und `UmaFigur`, damit Liste,
 * Auswahl, Zählung und Speichern nicht je Quelle unterscheiden müssen.
 *
 * Seit 13.09.2026 in `gemeinsam/`; die Szene erbt als `SmplModell` nur das Speichern.
 */
export class SmplModell extends Modell {

    static QUELLE = 'smpl';
    static ADRESSE = '/api/character/smpl-figur/';
    static FORMADRESSE = '/api/character/smpl-figur/formen/';

    /** Hautfarbe des Referenzkörpers — bewusst grau, kein Mensch (Vorgabe,
     *  solange niemand eine eigene Hautfarbe gesetzt hat, `haut.farbe`). */
    static FARBE = 0x9a9a9a;

    /** Die acht ungemessenen Formregler (Beta 2..9) — Reihenfolge wie `SMPL/form.py`. */
    static WEITERE_FORMEN = Array.from({ length: 8 }, (_, i) => `form${i + 3}`);

    /** Textur-Adresse je Geschlecht (`core/api/smplfigur.py::textur`) —
     *  gecacht, damit ein Formregler-Zug sie nicht neu lädt (25.09.2026). */
    static TEXTURADRESSE = '/api/character/smpl-figur/textur/';
    static _texturVorrat = new Map();
    //: Dieselben Schlüssel wie `_texturVorrat`, aber als Promise — löst sich
    //: erst, wenn das Bild wirklich da ist (`Sanduhr` in `smplhautregler.js`).
    static _texturBereit = new Map();

    static _textur(geschlecht) {
        const schluessel = geschlecht === 'male' ? 'male' : 'female';
        if (!SmplModell._texturVorrat.has(schluessel)) {
            const textur = new THREE.TextureLoader().load(
                `${SmplModell.TEXTURADRESSE}${schluessel}/`,
                () => SmplModell._texturBereit.get(schluessel)?._geloest(),
                undefined,
                () => SmplModell._texturBereit.get(schluessel)?._geloest());
            textur.colorSpace = THREE.SRGBColorSpace;
            SmplModell._texturVorrat.set(schluessel, textur);
            SmplModell._texturBereit.set(schluessel, SmplModell._versprechen());
        }
        return SmplModell._texturVorrat.get(schluessel);
    }

    /** Die BEDLAM-Hautfotos (26.09.2026, „du hast doch eine Textur
     *  heruntergeladen, wende sie an") — je Geschlecht+Schlüssel gecacht,
     *  wie `_textur`. `haut.textur` trägt dann `bedlam:<schlüssel>`. */
    static BEDLAM_ADRESSE = '/api/character/smpl-figur/bedlam/';
    static _bedlamVorrat = new Map();
    static _bedlamBereit = new Map();

    static _bedlamTextur(geschlecht, schluessel) {
        const g = geschlecht === 'male' ? 'male' : 'female';
        const eintrag = `${g}:${schluessel}`;
        if (!SmplModell._bedlamVorrat.has(eintrag)) {
            const textur = new THREE.TextureLoader().load(
                `${SmplModell.BEDLAM_ADRESSE}${g}/${encodeURIComponent(schluessel)}/`,
                () => SmplModell._bedlamBereit.get(eintrag)?._geloest(),
                undefined,
                () => SmplModell._bedlamBereit.get(eintrag)?._geloest());
            textur.colorSpace = THREE.SRGBColorSpace;
            SmplModell._bedlamVorrat.set(eintrag, textur);
            SmplModell._bedlamBereit.set(eintrag, SmplModell._versprechen());
        }
        return SmplModell._bedlamVorrat.get(eintrag);
    }

    /** Ein Promise, dessen Auflösung von außen ausgelöst wird (`_geloest`
     *  hängt es hinein) — `TextureLoader.load` kennt nur Callbacks. */
    static _versprechen() {
        let geloest;
        const versprechen = new Promise((r) => { geloest = r; });
        versprechen._geloest = geloest;
        return versprechen;
    }

    /**
     * Wird `haut.textur` gerade zum ERSTEN Mal gebraucht, ist das Bild noch
     * unterwegs — der Aufrufer (`Smplhautregler`) zeigt solange die Sanduhr.
     * Schon geladen oder „keine": `null`, dann ist nichts abzuwarten.
     */
    static texturBereit(geschlecht, texturwert) {
        if (!texturwert || texturwert === 'keine') return null;
        const g = geschlecht === 'male' ? 'male' : 'female';
        if (texturwert.startsWith('bedlam:')) {
            const eintrag = `${g}:${texturwert.slice(7)}`;
            return SmplModell._bedlamVorrat.has(eintrag) ? SmplModell._bedlamBereit.get(eintrag) : null;
        }
        return SmplModell._texturVorrat.has(g) ? SmplModell._texturBereit.get(g) : null;
    }

    constructor(id, daten) {
        super(id, SmplModell.QUELLE);
        this.koerper = daten.koerper || 'mean_all';
        this.presetName = daten.presetName || `GarmentCode · ${this.koerper}`;
        this.bodyType = 'GarmentCode';
        this.geschlecht = daten.geschlecht || null;
        this.masse = daten.masse || {};
        this.hoehe = 0;
        // Form der Figur: zehn Regler, -100..+100, 0 = Durchschnittskörper
        // des Tools (SMPL-X führt zehn Shape-Betas; nur die ersten zwei sind
        // gemessen benannt — Größe/Fülle —, die übrigen acht laufen als
        // form3..form10 ungemessen mit, 25.09.2026 „Vollausstattung"). Das
        // Online-Tool hat diese Regler gar nicht — gemessen bleibt sein
        // 3D-Körper bei jedem Maß derselbe (siehe smplform.py).
        this.form = {
            groesse: Number(daten.form?.groesse) || 0,
            fuelle: Number(daten.form?.fuelle) || 0,
        };
        for (const schluessel of SmplModell.WEITERE_FORMEN) {
            this.form[schluessel] = Number(daten.form?.[schluessel]) || 0;
        }
        // Dazu die benannten Maßregler (armlaenge, brustgroesse, …, 25.09.2026
        // `SMPL/xmassregler.py`) — ihre Liste kommt vom Server, deshalb hier
        // jeder weitere Zahlenwert, den die gespeicherte Figur trägt.
        for (const [schluessel, wert] of Object.entries(daten.form || {})) {
            if (!(schluessel in this.form) && Number.isFinite(Number(wert))) {
                this.form[schluessel] = Number(wert);
            }
        }
        this.betas = daten.betas || [];
        // Haut: eigene Farbe/Rauheit/Glanz statt des grauen Referenzkörpers
        // (25.09.2026, Edgar: „SMPL-X für Vollausstattung"). `farbe` leer
        // (0) heißt „noch nicht gesetzt" — dann bleibt es beim Grau.
        // Dieselben Detailfelder wie HumanBody (`Koerperdetails`, Feld `details`).
        this.details = Smpldetails.aus(daten);
        this.haut = {
            farbe: Number(daten.haut?.farbe) || 0,
            rauheit: typeof daten.haut?.rauheit === 'number' ? daten.haut.rauheit : 0.7,
            glanz: typeof daten.haut?.glanz === 'number' ? daten.haut.glanz : 0.0,
            // 'foto' (eigenes Meshcapade-Hautbild), 'keine' (nur `farbe`) oder
            // 'bedlam:<schlüssel>' (eine der 100 BEDLAM-Hauttexturen, 26.09.2026,
            // „du hast doch eine Textur heruntergeladen, wende sie an"). Ohne
            // Feld = Foto: SMPLX1 trug aus der Zeit vor der Textur #d31717, und
            // Farbe × Foto machte die Haut rot.
            textur: /^(foto|keine|bedlam:.+)$/.test(daten.haut?.textur) ? daten.haut.textur : 'foto',
        };
    }

    async bauen() {
        const geformt = Object.values(this.form).some((wert) => Number(wert));
        const daten = geformt
            ? await Serverabruf.senden(SmplModell.FORMADRESSE, {
                geschlecht: this.geschlecht || 'female',
                ...this.form,
            })
            : await Serverabruf.json(
                `${SmplModell.ADRESSE}${encodeURIComponent(this.koerper)}/netz/`);
        if (daten.fehler) throw new Error(daten.fehler);
        if (daten.name) this.koerper = daten.name;
        this.betas = daten.betas || this.betas;
        const punkte = daten.punkte || [];
        const dreiecke = daten.dreiecke || [];
        if (!punkte.length || !dreiecke.length) {
            throw new Error(`Referenzkörper ${this.koerper} ohne Netz`);
        }
        // Browsernetz an den UV-Nähten geteilt (11.313 statt 10.475 Punkte,
        // `Smplxuv` im Server) — nur bei echten SMPL-X-Körpern, GarmentCodes
        // eigene Referenzkörper bleiben ohne UV (25.09.2026, „SMPL-X-
        // Texturen"). `_uvUrsprung` wird gebraucht, um die Hautgewichte
        // (die am UNGETEILTEN Netz stehen) auf dieselben Punkte zu ziehen.
        this._uvUrsprung = daten.smpl && daten.uv_ursprung ? daten.uv_ursprung : null;
        this.bodyMesh = Smplnetz.bauen(punkte, dreiecke, daten.uv, daten.uv_dreiecke, this._uvUrsprung);
        this.bodyMesh.name = `garmentcode_koerper_${this.koerper}`;
        // Nur ein echter SMPL-X-Körper hat die passende UV — ein Hautfoto
        // (eigenes oder BEDLAM) auf GarmentCodes eigenen Körpern wäre falsch verzerrt.
        this._fotoFaehig = !!(daten.smpl && this._uvUrsprung);
        if (this._fotoFaehig) {
            this._fototextur = SmplModell._textur(daten.geschlecht || this.geschlecht);
        }
        this.hautAnwenden();
        // ERST das Skelett, DANN das Netz einhängen: Die Bindung braucht
        // die Knochen in ihrer Ruhelage (`Eigenhaut.einhaengen`).
        this.skelettBauen(daten.skelett);
        this._hautBinden(daten.hautgewichte);
        // Augen, Brauen, Lippen, Nägel, Wimpern, Mund (25.09.2026, `Smpldetails`).
        await Smpldetails.bauen(this, punkte, dreiecke, daten.hautgewichte);
        this.geschlecht = daten.geschlecht || this.geschlecht;
        this.masse = daten.masse || {};
        this.hoehe = daten.hoehe || 0;
        // Stabiles Etikett statt des internen Koerpernamens (25.09.2026):
        // eine geformte Variante traegt einen Beta-Fingerabdruck
        // (`smplx_f_351c76912d35…`) — als Unterzeile der Charakterliste sah
        // das wie „GarmentCode-Körper" aus, egal wie die Figur gespeichert
        // war (Edgar: „warum heisst mein SMPLX: GarmentCode-Körper??").
        // `daten.smpl` kommt von BEIDEN Endpunkten (Netz UND Formung).
        this.bodyType = daten.smpl ? 'SMPL-X' : `GarmentCode · ${this.koerper}`;
        Protokoll.debug('SmplModell',
            `${this.koerper}: ${punkte.length} Punkte, ${dreiecke.length} Dreiecke, ${this.hoehe.toFixed(2)} m`);
        return this;
    }

    /** Details neu anwenden (`Detailbedienung`, ein Feld oder alles). */
    detailfeldAnwenden(feld = null) {
        return Smpldetails.anwenden(this, feld);
    }

    /**
     * Das Netz an das eigene Skelett binden — sonst bleibt es beim Abspielen
     * starr, während die Knochen sich bewegen.
     *
     * Die Gewichte stammen aus dem SMPL-X-Modell selbst (`weights`, 10475 × 55,
     * je Punkt die vier größten); für GarmentCodes eigene Körper (23.752
     * Punkte) sind sie über den nächstgelegenen SMPL-X-Punkt übertragen.
     * Ohne Skelett oder ohne Gewichte
     * hängt hier ein gewöhnliches `Mesh` — die Figur ist dann sichtbar, aber
     * nicht animierbar.
     */
    _hautBinden(haut) {
        // Die Gewichte kommen vom Server am UNGETEILTEN Netz (10.475 Punkte) —
        // das Browsernetz hat mit UV-Nähten mehr Punkte (`_uvUrsprung`,
        // `bauen()`). Ohne diese Erweiterung träfe `Eigenhaut.binden` ein zu
        // kurzes Gewichtsfeld auf ein längeres Positionsfeld.
        const hautFuersNetz = (haut && this._uvUrsprung)
            ? SmplModell._hautErweitern(haut, this._uvUrsprung) : haut;
        if (this.skelett && hautFuersNetz) {
            this.bodyMesh = Eigenhaut.binden(this.bodyMesh, this.skelett, hautFuersNetz);
        }
        Eigenhaut.einhaengen(this.group, this.bodyMesh, this.skelett);
        this.isSkinned = !!this.bodyMesh.isSkinnedMesh;
    }

    /** Hautgewichte je Original-Punkt auf die (an den UV-Nähten geteilten)
     *  Browserpunkte ziehen — derselbe Punkt bekommt an jeder Naht dieselben
     *  Gewichte, nur einen anderen Platz im Feld. */
    static _hautErweitern(haut, ursprung) {
        const { index, gewicht } = Eigenhaut.gewichte(haut);
        const n = ursprung.length;
        const indexNeu = new Float32Array(n * 4);
        const gewichtNeu = new Float32Array(n * 4);
        for (let j = 0; j < n; j++) {
            const quelle = ursprung[j] * 4;
            const ziel = j * 4;
            for (let k = 0; k < 4; k++) {
                indexNeu[ziel + k] = index[quelle + k];
                gewichtNeu[ziel + k] = gewicht[quelle + k];
            }
        }
        return {
            knochen: haut.knochen,
            skin_indices: float32ToBase64(indexNeu),
            skin_weights: float32ToBase64(gewichtNeu),
        };
    }

    /**
     * Die eigene Hautfarbe (Farbe/Rauheit/Glanz, `this.haut`) auf das Material
     * legen — ohne gesetzte Farbe bleibt es beim grauen Referenzkörper
     * (`FARBE`). Aufrufen nach jedem Netzbau, das Material wird dabei nicht
     * ersetzt (`Eigenhaut.binden` reicht dasselbe Material weiter).
     */
    hautAnwenden() {
        const material = this.bodyMesh?.material;
        if (!material) return;
        // Mit Foto ist die Farbe WEISS — Three multipliziert Farbe × Textur,
        // jede andere Farbe tönte das Foto um. `haut.farbe` gilt nur ohne Foto.
        let foto = null;
        if (this._fotoFaehig && this.haut.textur !== 'keine') {
            if (this.haut.textur.startsWith('bedlam:')) {
                foto = SmplModell._bedlamTextur(this.geschlecht, this.haut.textur.slice(7));
            } else {
                foto = this._fototextur || null;
            }
        }
        material.map = foto;
        material.color.set(foto ? 0xffffff : (this.haut.farbe || SmplModell.FARBE));
        material.roughness = this.haut.rauheit;
        material.metalness = 0.0;
        // Glanz = ein zusätzlicher Klarlack-Anteil (feuchte/glänzende Haut),
        // wie bei den Genesis-Stücken (`Stueckstoff`) — 0 heißt „aus".
        if (this.haut.glanz > 0) {
            material.clearcoat = this.haut.glanz;
            material.clearcoatRoughness = 0.3;
        } else {
            material.clearcoat = 0;
        }
        material.needsUpdate = true;
    }
}
