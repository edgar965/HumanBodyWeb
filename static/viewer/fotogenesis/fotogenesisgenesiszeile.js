/**
 * Fotogenesisgenesiszeile — dritte Zeile der Jobseite bei PSHuman-Jobs (04.11.2026, Edgar: „3. Zeile: Genesis - Mesh3d-AI, Genesis - 2d3dai (aus Fotos), Genesis Ergebnis (mes3d-ai)“).
 *
 * Feld 1 „Genesis – Mesh-Genesis“: die Einpassung ohne KI aus dem Mesh-Genesis-Test zum PSHuman-Netz (`Fotogenesisanpassungsfigur`); Feld 2 SMPL-X (`Fotogenesissmplx`, folgt der Leiste dieser Zeile); Feld 3 das
 * Feld „Genesis-Modell“ der Seite (`Fotogenesisseite.genesisfeld`, nur hierher verlegt). „Genesis-Ergebnis (Mesh-Genesis)“, die Figur des fertigen Tests (`Fotogenesistestfigur`, wie Messlatte A), zeichnet diese
 * Klasse auch, es steht seit 04.11.2026 abends aber eine Zeile höher und folgt der Leiste oben (Edgar: „Genesis-Ergebnis (Mesh3D-AI) in die zweite Zeile (eine darüber)“). Daten
 * `daten.genesiszeile`. Die Felder folgen der Ansichtsart der Seite, drehen mit den übrigen (`Meshgenesisansicht.koppeln` in `Fotogenesisseite`) und stehen so groß wie die Person im
 * Foto (`Fotogenesisseite._rand`). Template `fotogenesis_genesiszeile.html`.
 */
import * as THREE from 'three';
import { Exportleiste } from '../exportleiste/exportleiste.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshgenesisfigurbewegungsleiste } from '../meshgenesis/meshgenesisfigurbewegungsleiste.js';
import { Meshgenesisflaechennetz } from '../meshgenesis/meshgenesisflaechennetz.js';
import { Meshgenesistestfaelle } from '../meshgenesis/meshgenesistestfaelle.js';
import { Fotogenesisanpassungsfigur } from './fotogenesisanpassungsfigur.js';
import { Fotogenesisansicht } from './fotogenesisansicht.js';
import { Fotogenesisexportfigur } from './fotogenesisexportfigur.js';
import { Fotogenesisjoblauf } from './fotogenesisjoblauf.js';
import { Fotogenesiskamera } from './fotogenesiskamera.js';
import { Fotogenesistestfigur } from './fotogenesistestfigur.js';
import { Fotogenesiszeilenleiste } from './fotogenesiszeilenleiste.js';

export class Fotogenesisgenesiszeile {
    static KAMERA = { position: [0, 1, 4], ziel: [0, 0.9, 0], boden: false };

    /** Die Zeile zu `seite` (`Fotogenesisseite`) — null ohne Zeile im Template oder ohne Daten. */
    static aufbauen(seite) {
        const zeile = document.getElementById('fotogenesis-genesiszeile');
        if (!zeile || !seite.daten.genesiszeile) return null;
        return new Fotogenesisgenesiszeile(seite, zeile);
    }

    /** Knopf „Genesis rechnen“: neuer Test aus dem PSHuman-Netz (`Fotogenesisgenesisstart`), danach dessen Seite mit dem Fortschritt. */
    static async _rechnen(knopf) {
        if (!confirm('Genesis aus dem PSHuman-Netz rechnen? Die Karte ist rund 20 Minuten belegt.')) return;
        knopf.disabled = true;
        try {
            const { adresse } = await Serverabruf.senden(knopf.dataset.adresse, {});
            location.href = adresse;
        } catch (fehler) {
            alert(`Nicht gestartet: ${fehler.message}`);
            knopf.disabled = false;
        }
    }

    constructor(seite, zeile) {
        this.seite = seite;
        zeile.querySelector('[data-aktion="genesis-rechnen"]')?.addEventListener('click', ereignis => Fotogenesisgenesiszeile._rechnen(ereignis.currentTarget));
        Fotogenesisjoblauf.aufbauen(zeile);
        const g = seite.daten.genesiszeile, feld = name => document.querySelector(`[data-feld="${name}"]`);
        // eigene Leiste (04.11.2026, Edgar: „in jeder Zeile ab Zeile 3 diese ansichten plus die Rig, Kleider Toggle buttons“) — gilt für alle drei Felder der Zeile (`Fotogenesisseite._auftrag`, `Fotogenesissmplx.zeigen`)
        this.leiste = Fotogenesiszeilenleiste.aufbauen(zeile.querySelector('[data-zeilenleiste]'), () => { this.zeigen(false); seite.smplx?.zeigen(false); seite._genesisZeigen(false); });
        const neu = () => this.zeigen(false);
        let ergebnis = null;
        if (g.ergebnis) {
            // `Fotogenesistestfigur` setzt `Meshgenesisflaechennetz.nachLaden` für sich allein — den Ruf der Figur im Feld „Genesis-Modell“ (vorher gebaut) nicht verlieren
            const vorher = Meshgenesisflaechennetz.nachLaden;
            // in der A-Pose, wenn das Feld „PSHuman“ sie zeigt (10.11.2026, Edgar: „damit man das besser vergleichen kann“; `pshuman_port14/pshuman_apose.py`). Wo das Netz in der A-Pose
            // zerreißt (verwachsene Glieder, Robe mit Stab), zeigen beide Felder die Haltung des Fotos — sonst wären sie nicht vergleichbar
            ergebnis = new Fotogenesistestfigur({ kennung: g.test, adresse: g.ergebnis, apose: seite.daten.pshuman?.art === 'pshuman_apose' });
            const eigen = Meshgenesisflaechennetz.nachLaden;
            Meshgenesisflaechennetz.nachLaden = () => { vorher?.(); eigen?.(); neu(); };
        }
        this.eintraege = [['genesis-meshgenesis', g.meshgenesis ? new Fotogenesisanpassungsfigur(g.meshgenesis, neu) : null, g.hinweise.meshgenesis, this.leiste],
                          ['genesis-ergebnis', ergebnis, g.hinweise.ergebnis, null]]
            .map(([name, figur, hinweis, leiste]) => ({ figur, hinweis, leiste, ansicht: new Fotogenesisansicht(feld(name), 'ausgabe', figur ?? { zeichnen: () => {} }, Fotogenesisgenesiszeile.KAMERA) }));
        // Abspielleiste und Export unter beiden Feldern (04.11.2026, Edgar: „playleiste und export für alle 3“) — derselbe Code wie unter dem Feld „Genesis-Modell“ (`Fotogenesisexportfigur`, `Fotogenesisbewegung`):
        // die Einpassung ist die Form der Zeile 1 ohne Haut und Stücke der KI, das Ergebnis die Figur der Mesh-Genesis-Testseite
        this.exportfiguren = [Fotogenesisgenesiszeile._leisten(feld('genesis-meshgenesis'), this.eintraege[0].ansicht, g.figur, true),
                              Fotogenesisgenesiszeile._leisten(feld('genesis-ergebnis'), this.eintraege[1].ansicht, g.ergebnis, false)];
        seite.fotos.gross.addEventListener('load', () => this.kameras());
        for (const e of this.eintraege) e.figur?.bereit.then(() => this.zeigen(true));
        // Testfälle des Tests wie auf der Mesh-Genesis-Testseite (06.11.2026, Edgar: „mach den besten code den wir haben in beiden pipelines“)
        const testfaelle = document.getElementById('meshgenesis-testfaelle');
        if (testfaelle) new Meshgenesistestfaelle(testfaelle).laden(`${testfaelle.dataset.adresse}?t=${Date.now()}`);
    }

    /** Das Feld Genesis-Ergebnis für „Haut angleichen“ (`Fotogenesishautangleich`). */
    get hautort() {
        const { ansicht, figur } = this.eintraege[1];
        return { ansicht, bereit: figur?.bereit, materialien: () => (figur?.koerper ? [figur.koerper.an.material].flat() : []) };
    }

    /** Leiste und Export der Karte um `feld` an die Figur unter `adresse` (`/api/meshgenesis/test/<k>/`) — null ohne Adresse oder ohne Leiste im Template. */
    static _leisten(feld, ansicht, adresse, nackt) {
        const karte = feld.closest('section'), leiste = karte.querySelector('[data-figurbewegung]'), ausfuhr = karte.querySelector('.exportleiste');
        if (!adresse || !leiste) return null;
        const figur = new Fotogenesisexportfigur(adresse, ansicht, { nackt });
        new Meshgenesisfigurbewegungsleiste(leiste, figur.bewegung).wahlLaden(leiste.dataset.adresse);
        // BVH-Vorschlag = die Standardanimation der Leiste, wie auf der Mesh-Genesis-Testseite (`Meshgenesisexportquelle.bvh`); `Fotogenesisexportfigur.bvh` gibt keinen
        if (ausfuhr) Exportleiste.starten(ausfuhr, { modell: angaben => figur.modell(angaben), bvh: () => figur.bewegung.wahl || null });
        return figur;
    }

    get felder() {
        return this.eintraege.map(e => e.ansicht);
    }

    /** Einpassung nach der Leiste der Zeile, Ergebnis nach der Leiste oben zeigen; `neuStellen`: Kameras auf die Perspektive des Fotos. */
    zeigen(neuStellen) {
        const st = this.seite.steuerung;
        for (const { figur, hinweis, ansicht, leiste } of this.eintraege) {
            const z = leiste ?? st;
            ansicht.zeilenart = leiste?.art ?? null;
            // ohne Auftrag (null) zeigt das Feld nur den Text
            if (!figur) ansicht.zeigen(null, hinweis);
            else if (figur instanceof Fotogenesistestfigur) ansicht.zeigen(figur.probe ? figur.auftrag(st.quelle, z.modus, z.kleider, z.rig) : null, figur.fehler || 'Figur wird gebaut …');
            else ansicht.zeigen({ modus: z.modus, kleider: z.kleider });
        }
        if (neuStellen) this.kameras();
    }

    kameras(versuch = 0) {
        const s = this.seite;
        if (s.winkel === null) return;
        const eins = new THREE.Quaternion();
        let offen = false;
        for (const a of this.felder) offen = !Fotogenesiskamera.feldStellen(a, s.winkel, eins, s._rand(a), s.kopf) || offen;
        // solange eine Figur noch lädt, ist ihre Hülle leer: nachfassen
        if (offen && versuch < 40) {
            clearTimeout(this._uhr);
            this._uhr = setTimeout(() => this.kameras(versuch + 1), 250);
        }
    }
}
