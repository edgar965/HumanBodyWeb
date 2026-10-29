/**
 * Mesh3daimeshanpassung — erste Zeile der Testseite (28.10.2026, Edgar: „Mache in deinem Jobview auch eine erste Zeile mit der reinen Anpassung des Genesis Modells an das Mesh. Also ohne KI.“):
 * die Genesis-Figur, mit `G9meshgenesis` (Portierung von IPNet bzw. smplx transfer_model, Hilfe → Architektur → Genesis, Abschnitt 12) in das Netz eingepasst — keine Regler-KI.
 * Drei gekoppelte Felder: das Mesh · die eingepasste Figur · beide übereinander (Mesh halb durchsichtig). Ansichtsarten wie die Zeilen darunter (`Mesh3daimaterial.MODI`); „Textur“ zeigt
 * das Mesh in seinen Farben (Farbe je Punkt aus dem Texturbild der Datei) und die Figur in der Daz-Haut ihrer Startfigur.
 * Daten `…/meshanpassung/` (Server `Mesh3daitestanpassung`, gerechnet von `mesh3dai/mesh3dai_meshanpassung.py`).
 */
import * as THREE from 'three';
import { Genesis9texturen } from '../gemeinsam/genesis9texturen.js';
import { Mesh3daiansicht } from './mesh3daiansicht.js';
import { Mesh3daiansichtgedaechtnis } from './mesh3daiansichtgedaechtnis.js';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';
import { Mesh3daimaterial } from './mesh3daimaterial.js';
import { Mesh3dailinienzeichner as LZ } from './mesh3dailinienzeichner.js';

const de = (n, s = 0) => (n == null ? '—' : Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s }));
const KAMERA = { position: [1.2, 1.3, 2.9], ziel: [0, 0.95, 0], boden: true };
const FELDER = ['netz', 'figur', 'beide'];
const VERFAHREN = { ipnet: 'IPNet', transfer: 'smplx transfer_model' };
// `versatz_art` seit 28.10.2026 abends (`G9meshgenesis.VERSATZ`); ältere Ergebnisse haben keinen Eintrag und rechneten frei
// `kopf_frei` seit 28.10.2026 abends (`Mesh3daimeshgenesis`, `Mesh3daikopfversatz`): der Kopf danach frei je Punkt wie IPNet; davor nahm `G9meshgenesis` ihn aus (nur Kopfregler)
const VERSATZ = { normale: 'Versatz je Punkt nur längs der Normale, Kopf, Hände, Füße, Augen und Gelenkringe ohne (Kopf nur über seine Regler)', frei: 'freier Versatz je Punkt' };
const VERSATZ_KOPF = 'Versatz je Punkt längs der Normale, der Kopf danach frei je Punkt wie IPNet (Lider, Mundraum und Punkte ohne gleichsinnige Normale ohne eigenen Zug, sie folgen ihren Nachbarn);'
    + ' Hände, Füße und Gelenkringe ohne';

export class Mesh3daimeshanpassung {
    static NETZFARBE = 0xc9c2b8;
    static FIGURFARBE = 0xe0a882;
    static DECKKRAFT = 0.45;
    static ANATOMIE_MANN = [159 / 255, 120 / 255, 102 / 255];
    static ANATOMIE_FRAU = [160 / 255, 121 / 255, 104 / 255];

    static starten(wurzel) {
        const z = new Mesh3daimeshanpassung(wurzel);
        window.__mesh3daianpassung = z;          // für Messungen im Tab, wie `__mesh3daitest`
        z.laden();
        z.gemerktLaden();
        return z;
    }

    /**
     * Die gemerkte Ansichtsart aller Mesh3D-AI-Seiten (`Mesh3daiansichtgedaechtnis`) — bis 28.10.2026 abends startete diese Zeile immer in „Oberfläche“, während die Zeilen darunter die gemerkte
     * zeigten (Edgar, Bild: „texturen nicht Da!!“ — gemerkt war „Textur“, `ui_prefs.mesh3dai_ansicht.modus`). Ein Klick in einer anderen Zeile stellt diese mit um (`EREIGNIS`).
     */
    async gemerktLaden() {
        document.addEventListener(Mesh3daiansichtgedaechtnis.EREIGNIS, e => this._modusSetzen(e.detail?.modus));
        this._modusSetzen((await Mesh3daiansichtgedaechtnis.laden()).modus);
    }

    _modusSetzen(modus) {
        if (!Mesh3daimaterial.MODI.some(m => m.schluessel === modus) || modus === this.modus) return;
        this.modus = modus;
        this._neu();
    }

    constructor(wurzel) {
        this.wurzel = wurzel;
        this.modus = 'oberflaeche';
        this.kopf = null;
        this.fehler = null;
        const zeichner = { zeichnen: (inhalt, art) => this._zeichnen(inhalt, art) };
        this.ansichten = FELDER.map(f => new Mesh3daiansicht(wurzel.querySelector(`.mesh3dai-leinwand[data-art="anpassung-${f}"]`), f, zeichner, KAMERA));
        Mesh3daiansicht.koppeln(this.ansichten);
        wurzel.querySelector('.mesh3dai-ma-ansicht')?.append(...Mesh3daimaterial.MODI.map(m => {
            const b = document.createElement('button');
            b.type = 'button';
            b.className = 'schaltknopf';
            b.dataset.modus = m.schluessel;
            b.title = m.schluessel === 'textur' ? 'Das Mesh in seinen Farben (Farbe je Punkt), die Genesis-Figur in der Haut ihrer Startfigur (Daz-Bilder über die UV der Figur).' : m.hinweis;
            b.innerHTML = `<i class="fas ${m.icon}"></i> `;
            b.append(m.name);
            b.addEventListener('click', () => {
                this._modusSetzen(m.schluessel);
                Mesh3daiansichtgedaechtnis.merken({ modus: m.schluessel });
            });
            return b;
        }));
        this._neu();
    }

    static _geometrie(punkte, dreiecke, farbe = null) {
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
        if (farbe) g.setAttribute('color', new THREE.BufferAttribute(farbe, 3, true));
        g.setIndex(new THREE.BufferAttribute(dreiecke, 1));
        g.computeVertexNormals();
        g.userData.gemeinsam = true;
        return g;
    }

    /** Kopie von `geo`, deren Dreiecke `loch` entartet sind (alle Ecken auf der ersten) — Zahl und Gruppen der Dreiecke bleiben, gezeichnet wird dort nichts. */
    static _mitLoch(geo, loch) {
        const g = geo.clone();
        const index = g.getIndex().array.slice();
        for (const t of loch) index[3 * t + 1] = index[3 * t + 2] = index[3 * t];
        g.setIndex(new THREE.BufferAttribute(index, 1));
        g.userData.gemeinsam = true;
        return g;
    }

    async laden() {
        try {
            const a = await fetch(`/api/mesh3dai/test/${encodeURIComponent(this.wurzel.dataset.kennung)}/meshanpassung/`);
            if (!a.ok) throw new Error(a.status === 404 ? 'Noch nicht gerechnet (python14 mesh3dai/mesh3dai_meshanpassung.py --nur <Test>).' : `HTTP ${a.status}`);
            const { kopf, daten } = LZ.paket(await a.arrayBuffer());
            this.kopf = kopf;
            this.netz = Mesh3daimeshanpassung._geometrie(daten.netz_punkte, daten.netz_dreiecke, daten.netz_farbe);
            this.figur = Mesh3daimeshanpassung._geometrie(daten.figur, daten.figur_dreiecke);
            this.figurHaut = daten.uv && kopf.textur ? this._haut(daten, kopf.textur) : null;
            // das Anatomie-Stück der Startfigur am eingepassten Becken (`Mesh3daimeshanatomie`, seit 28.10.2026 abends — vorher fehlte es; ältere Ergebnisse haben es nicht)
            this.anatomie = daten.anatomie_punkte ? Mesh3daimeshanpassung._geometrie(daten.anatomie_punkte, daten.anatomie_dreiecke) : null;
            // „Textur“: die Haut der Startfigur am nächsten Käfigpunkt als Farbe je Punkt (`Mesh3daitestanpassung.anatomie_farbe`, linear; seit 28.10.2026 nachts, vorher eine Farbe)
            this.anatomieBunt = null;
            if (this.anatomie && daten.anatomie_farbe) {
                this.anatomieBunt = Mesh3daimeshanpassung._geometrie(daten.anatomie_punkte, daten.anatomie_dreiecke);
                this.anatomieBunt.setAttribute('color', new THREE.BufferAttribute(daten.anatomie_farbe, 3));
            }
            // die Dreiecke der Figur unter dem Stück (`anatomie_loch`, seit 28.10.2026 nachts): wo das Stück gezeigt wird, fehlen sie — Daz versteckt sie (`hidden_polys`)
            this.figurLoch = this.anatomie && daten.anatomie_loch ? Mesh3daimeshanpassung._mitLoch(this.figur, daten.anatomie_loch) : null;
            this.figurHautLoch = this.figurHaut && this.figurLoch ? Mesh3daimeshanpassung._mitLoch(this.figurHaut, daten.anatomie_loch) : null;
            // Seit 28.10.2026 nachmittags steht das Ziel schon vor der Einpassung auf y = 0 (`ziel.boden_m`); ältere Ergebnisse haben die Füße im Rahmen der Regler-KI bei y ≈ 0,95 m —
            // zur Anzeige beide um den tiefsten Punkt des Meshs auf den Boden (bei neuen ≈ 0)
            let boden = Infinity;
            for (let i = 1; i < daten.netz_punkte.length; i += 3) boden = Math.min(boden, daten.netz_punkte[i]);
            this.boden = boden;
            for (const g of [this.netz, this.figur, this.figurHaut, this.anatomie, this.anatomieBunt, this.figurLoch, this.figurHautLoch]) g?.translate(0, -boden, 0);
        } catch (fehler) {
            this.fehler = fehler.message;
        }
        this._neu();
    }

    /**
     * Die eingepasste Figur in der Haut der Startfigur (28.10.2026 abends, Edgar: „kannst du das eingepasste Genesis auch mit Textur zeigen?“): je UV-Punkt Lage und Normale seines
     * Käfigpunkts (`uv_ursprung`, `G9basisnetz`), Dreiecke und Materialgruppen der UV-Teilung, je Gruppe die Albedo aus der Daz-Bibliothek (`Genesis9texturen`, Weg der Seite).
     */
    _haut(daten, gruppen) {
        const u = daten.uv_ursprung, f = daten.figur, nf = this.figur.getAttribute('normal').array;
        const p = new Float32Array(u.length * 3), n = new Float32Array(u.length * 3);
        for (let i = 0; i < u.length; i++) {
            for (let k = 0; k < 3; k++) {
                p[3 * i + k] = f[3 * u[i] + k];
                n[3 * i + k] = nf[3 * u[i] + k];
            }
        }
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(p, 3));
        g.setAttribute('normal', new THREE.BufferAttribute(n, 3));
        g.setAttribute('uv', new THREE.BufferAttribute(daten.uv, 2));
        g.setIndex(new THREE.BufferAttribute(daten.uv_dreiecke, 1));
        g.userData.gemeinsam = true;
        this.hautMaterialien = gruppen.map((gruppe, i) => {
            g.addGroup(gruppe.index_ab, gruppe.index_anzahl, i);
            const m = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.7 });
            m.userData.gemeinsam = true;
            if (gruppe.albedo) {
                Genesis9texturen.holen(gruppe.albedo, true, m, t => {
                    m.map = t;
                    this._neu();
                });
            }
            return m;
        });
        return g;
    }

    /** Ein Netz in der gewählten Ansichtsart; Materialien geteilt (`Mesh3daigemeinsam`). Ohne Farbe je Punkt gilt „Textur“ wie „Oberfläche“. */
    _objekt(geo, farbe, deckkraft) {
        const bunt = !!geo.getAttribute('color');
        if (this.modus === 'punkte') {
            return new THREE.Points(geo, Mesh3daigemeinsam.material(`anpassung:punkte:${bunt ? 'bunt' : farbe}`,
                () => new THREE.PointsMaterial(bunt ? { vertexColors: true, size: 0.003 } : { color: farbe, size: 0.003 })));
        }
        if (this.modus === 'textur' && bunt) {
            return new THREE.Mesh(geo, Mesh3daigemeinsam.material(`anpassung:textur:${deckkraft}`,
                () => new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.85, transparent: deckkraft < 1, opacity: deckkraft, depthWrite: deckkraft >= 1 })));
        }
        const modus = this.modus === 'textur' ? 'oberflaeche' : this.modus;
        return Mesh3daimaterial.netz(geo, { modus, sollfarbe: farbe, deckkraft: modus === 'drahtnetz' || modus === 'roentgen' ? 1 : deckkraft });
    }

    _zeichnen(inhalt, feld) {
        const z = Mesh3daimeshanpassung;
        if (feld !== 'netz') {
            // Trägt ein Stück des Meshs die Anatomie (`Mesh3daimeshanatomie._im_stoff`, seit 28.10.2026 nachts, Regel wie Zeile 2 `Kleideranatomie`), zeigt „Beide“ sie nicht — wie die Haut
            // unter dem Stoff; das Feld „Figur“ zeigt sie. Mit dem Stück fehlen der Figur die Dreiecke darunter (`figurLoch`), ohne es ist die Haut geschlossen.
            const mitStueck = this.anatomie && !(feld === 'beide' && this.kopf.anatomie?.im_stoff?.verdeckt);
            inhalt.add(this.modus === 'textur' && this.figurHaut ? new THREE.Mesh(mitStueck && this.figurHautLoch ? this.figurHautLoch : this.figurHaut, this.hautMaterialien)
                : this._objekt(mitStueck && this.figurLoch ? this.figurLoch : this.figur, z.FIGURFARBE, 1));
            if (!mitStueck) {
                // ohne Stück
            } else if (this.modus === 'textur' && this.anatomieBunt) {
                // Das Stück hat keine eigene Textur: in „Textur“ die Haut der Startfigur je Punkt (`anatomie_farbe`), ohne sie die Mittelfarbe der Basishaut, sonst wie die Figur
                inhalt.add(new THREE.Mesh(this.anatomieBunt, Mesh3daigemeinsam.material('anpassung:anatomie:textur:bunt', () => new THREE.MeshStandardMaterial({
                    vertexColors: true, roughness: 0.7, side: THREE.DoubleSide }))));
            } else if (this.anatomie) {
                inhalt.add(this.modus === 'textur' ? new THREE.Mesh(this.anatomie, Mesh3daigemeinsam.material(`anpassung:anatomie:textur:${this.kopf.start}`, () => new THREE.MeshStandardMaterial({
                    color: new THREE.Color().setRGB(...(this.kopf.start === 'feminine' ? z.ANATOMIE_FRAU : z.ANATOMIE_MANN), THREE.SRGBColorSpace), roughness: 0.7, side: THREE.DoubleSide })))
                    : this._objekt(this.anatomie, z.FIGURFARBE, 1));
            }
        }
        if (feld !== 'figur') inhalt.add(this._objekt(this.netz, z.NETZFARBE, feld === 'beide' ? z.DECKKRAFT : 1));
    }

    _neu() {
        for (const b of this.wurzel.querySelectorAll('[data-modus]')) {
            b.classList.toggle('active', b.dataset.modus === this.modus);
            b.setAttribute('aria-pressed', String(b.dataset.modus === this.modus));
        }
        this._texte();
        for (const a of this.ansichten) a.zeigen(this.kopf ? { echt: true } : null, this.fehler || 'wird geladen …');
    }

    _text(name, text) {
        const feld = this.wurzel.querySelector(`[data-info="${name}"]`);
        if (feld) feld.textContent = text;
    }

    _texte() {
        const k = this.kopf;
        if (!k) {
            this._text('anpassung-kopf', this.fehler ?? 'Wird geladen …');
            for (const f of FELDER) this._text(`anpassung-${f}`, '');
            return;
        }
        const z = k.ziel || {};
        const kl = z.klassen || {};
        const m = k.masse || {};
        const p = k.stufe1 || {};
        const e = k.einpassung || {};
        const l = k.lage || {};
        const alt = k.veraltet ? `Achtung: gerechnet an der Kette ${k.kette}, der Test hat inzwischen ${k.juengste_kette} — neu rechnen. ` : '';
        // `innen` seit 28.10.2026 17:00 (`G9meshgenesis.INNEN` aus: Genesis legt sich über das Mesh); ältere Ergebnisse haben das Feld nicht und schoben die Haut 1 mm nach innen
        const innen = k.innen !== false;
        this._text('anpassung-kopf', `${alt}Ohne KI: Genesis (Start: Grundfigur ${k.start === 'masculine' ? 'männlich' : 'weiblich'}, keine Regler einer KI) mit ${VERFAHREN[k.verfahren] ?? k.verfahren}`
            + ` in das Netz eingepasst, ${k.kopf_frei && k.versatz_art === 'normale' ? VERSATZ_KOPF : VERSATZ[k.versatz_art ?? 'frei'] ?? k.versatz_art} (Genesis9.G9meshgenesis, Einstellungen → 2d-3d-AI), `
            + (innen ? `dann die Haut mindestens ${de(k.mindest_mm ?? 1, 1)} mm nach innen.` : 'ohne Pflicht nach innen: die Haut legt sich auf die Fläche, an Haar und Kleidung nur nicht hinaus.')
            + ` Gerechnet ${k.erzeugt}, ${de(k.sekunden)} s, Kette ${k.kette}.`
            + ` Rahmen und Größe wie die Regler-KI in der Pose des Eingangs (× ${de(z.massstab, 3)}, ${de(z.hoehe_m, 3)} m hoch), `
            + (z.boden_m != null ? `vor der Einpassung um ${de(z.boden_m, 3)} m auf den Boden gestellt.` : `zur Anzeige um ${de(this.boden, 3)} m auf den Boden gestellt.`));
        this._text('anpassung-netz', `Das Netz der Datei (${de(z.datei_punkte)} Punkte) in seiner eigenen Pose, zur Anzeige auf 3 mm zusammengefasst. Ziel der Einpassung: auf ${de(z.gitter_mm)} mm,`
            + ` ${de(z.punkte)} Punkte, ${de(z.dreiecke)} Dreiecke; Klasse je Punkt aus der Zerlegung: Haut ${de(kl.Haut)}, Kleidung ${de(kl.Kleidung)}, Haar ${de(kl.Haar)}, ungesehen ${de(kl.ungesehen)}`
            + ` (nur an der Haut liegt die Figur dicht an, sonst nur innen)`
            // `anliegend` seit 28.10.2026 nachts (`Mesh3daimeshanliegend`): Kleidung, deren Rand ohne Stufe in die Haut übergeht, zählt wie Haut
            + (z.anliegend ? `; anliegende Kleidung zählt wie Haut (Rand ohne Stufe zur Haut): ${Object.entries(z.anliegend).map(([art, a]) => `${art} ${a.anliegend ? 'ja' : 'nein'}`
                + ` (${de(100 * a.ohne_stufe)} % von ${de(a.rand)} Randpunkten ohne Stufe)`).join(', ') || 'keine Kleidung'}.` : '.'));
        // Mit `ruhelage_mm` ist das Soll der Mesh-Regler in die Ruhelage zurückgerechnet (G9meshgenesis seit 28.10.2026 15:09); ohne trugen sie die Pose des Eingangs als Form
        const ab = k.abgleich || {};
        // Seit 28.10.2026 abends legt `G9meshgenesis` bei nicht bestandener Abnahme keine Mesh-Regler ab (`abnahme.bestanden` false, mit Grund)
        const durchgefallen = k.abnahme && k.abnahme.bestanden === false;
        const grund = durchgefallen ? (k.abnahme.grund ?? k.abnahme.gruende) : null;
        const mr = !k.mesh_regler && durchgefallen ? ` Keine Mesh-Regler abgelegt: Abnahme nicht bestanden${grund ? ` (${Array.isArray(grund) ? grund.join('; ') : grund})` : ''};`
            + ' gezeigt wird der eingepasste Käfig selbst.'
            : !k.mesh_regler ? ' Keine Mesh-Regler abgelegt; gezeigt wird der eingepasste Käfig selbst.'
            : k.ruhelage_mm ? ` ${de(k.mesh_regler)} Mesh-Regler (Quelle m3a_${k.test}, im Bedienfeld unter Mesh), Soll in der Ruhelage: Mesh-Morph bis ${de(ab.morph_max_mm)} mm,`
                + ` Formung − Soll max ${de(ab.max_mm, 3)} mm.`
            : ` ${de(k.mesh_regler)} Mesh-Regler (Quelle m3a_${k.test}) — Achtung: sie tragen die Pose des Eingangs als Form (Mesh-Morph bis ${de(ab.morph_max_mm)} mm).`;
        this._text('anpassung-figur', `Genesis-Käfig (25.182 Punkte), ${de(k.regler - k.mesh_regler)} Regler.${mr}`
            + (innen ? ` Haut im Mittel ${de(m.haut_innen_mm, 2)} mm innen (Soll ${de(k.mindest_mm ?? 1, 1)} mm), außen ${de(m.aussen)} Punkte (kleinster Abstand ${de(m.kleinster_mm, 2)} mm),`
                + ` nach innen geschoben ${de(m.geschoben)} Punkte (bis ${de(m.groesster_schub_mm, 1)} mm).`
                : ` Haut im Mittel ${de(m.haut_innen_mm, 2)} mm innen, Abweichung von der Fläche ${de(m.haut_abweichung_mm, 2)} mm, außen ${de(m.aussen)} Punkte.`)
            + ` Haltung: größte Drehung ${de(l.haltung_max_grad, 1)}°.`
            // seit 28.10.2026 nachts auch die Hände (`Mesh3daimeshgenesis.FREI`, im Bericht `teile`); `kopf_frei` heißt im Bericht weiter so
            + (k.kopf_frei ? ` Frei je Punkt (${(k.kopf_frei.teile || ['kopf']).join(', ')}): ${de(k.kopf_frei.punkte)} Punkte${k.kopf_frei.mit_daten != null ? ` (davon ${de(k.kopf_frei.mit_daten)} mit Zug zum Netz)` : ''},`
                + ` bis ${de(k.kopf_frei.max_mm, 1)} mm (Mittel ${de(k.kopf_frei.mittel_mm, 2)} mm).` : '')
            + (k.anatomie?.stueck ? ` Anatomie: „${k.anatomie.stueck}“ am Becken der Figur (Lage aus ${de(k.anatomie.anker)} Käfigpunkten um den Ansatz, Rest ${de(k.anatomie.anker_rest_mm?.mittel, 1)} mm)`
                // `im_stoff` seit 28.10.2026 nachts (`Mesh3daimeshanatomie._im_stoff`): trägt ein Stück des Meshs sie, zeigt „Beide“ sie nicht
                + (k.anatomie.im_stoff?.verdeckt ? `, im Mesh unter ${k.anatomie.im_stoff.traeger.join(', ')} — „Beide“ zeigt sie dort nicht, wie die Haut unter dem Stoff`
                    + ` (${de(k.anatomie.im_stoff.aussen)} von ${de(k.anatomie.im_stoff.punkte)} Punkten ragen aus dem Stoff, ${de(k.anatomie.im_stoff.im_koerper)} im Körper).`
                    : k.anatomie.im_stoff ? `, nicht von Stoff verdeckt: ${de(k.anatomie.im_stoff.aussen)} von ${de(k.anatomie.im_stoff.punkte)} Punkten außerhalb des Meshs,`
                    + ` ${de(k.anatomie.im_stoff.im_koerper)} im Körper.` : '.')
                : k.anatomie?.aus ? ` Anatomie: ${k.anatomie.aus}.` : '')
            + (k.abnahme?.bestanden ? ' Abnahme (Gelenkdicke, umgeklappte Dreiecke gegen die Startfigur): bestanden.' : ''));
        this._text('anpassung-beide', `Mittlerer Abstand der Haut des Meshs zur Figur: nur Regler + Haltung ${de(p.ziel_haut_zur_figur_mm, 2)} mm (max ${de(p.ziel_haut_zur_figur_max_mm, 1)}),`
            + ` mit Versatz je Punkt ${de(e.ziel_haut_zur_figur_mm, 2)} mm, am Ende ${de(m.ziel_haut_zur_figur_mm, 2)} mm (max ${de(m.ziel_haut_zur_figur_max_mm, 1)}). Mesh halb durchsichtig.`
            // `pruefung` seit 28.10.2026 nachts (`Mesh3daimeshpruefung`): je Teil „fehlt“ (Haut des Netzes > 10 mm außerhalb) und „vor dem Netz“, dazu die Lippen
            + (k.pruefung ? (k.pruefung.rot.length ? ` Prüfung rot: ${k.pruefung.rot.join('; ')}.`
                : ` Prüfung grün: je Teil höchstens ${de(100 * k.pruefung.schwellen.fehlt_anteil)} % der Haut des Netzes mehr als ${de(k.pruefung.schwellen.fehlt_mm)} mm außerhalb der Figur,`
                + ` Lippen ${de(100 * k.pruefung.lippen.vor_anteil, 1)} % mehr als ${de(k.pruefung.schwellen.lippen_mm)} mm vor dem Netz.`) : ''));
    }
}
