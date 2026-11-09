/**
 * Ai2d3dgenesiszeile — dritte Zeile der Jobseite bei PSHuman-Jobs (04.11.2026, Edgar: „3. Zeile: Genesis - Mesh3d-AI, Genesis - 2d3dai (aus Fotos), Genesis Ergebnis (mes3d-ai)“).
 *
 * Feld 1 „Genesis – Mesh3D-AI“: die Einpassung ohne KI aus dem Mesh3D-AI-Test zum PSHuman-Netz (`Ai2d3danpassungsfigur`); Feld 2 SMPL-X (`Ai2d3dsmplx`, folgt der Leiste dieser Zeile); Feld 3 das
 * Feld „Genesis-Modell“ der Seite (`Ai2d3dseite.genesisfeld`, nur hierher verlegt). „Genesis-Ergebnis (Mesh3D-AI)“, die Figur des fertigen Tests (`Ai2d3dtestfigur`, wie Messlatte A), zeichnet diese
 * Klasse auch, es steht seit 04.11.2026 abends aber eine Zeile höher und folgt der Leiste oben (Edgar: „Genesis-Ergebnis (Mesh3D-AI) in die zweite Zeile (eine darüber)“). Daten
 * `daten.genesiszeile`. Die Felder folgen der Ansichtsart der Seite, drehen mit den übrigen (`Mesh3daiansicht.koppeln` in `Ai2d3dseite`) und stehen so groß wie die Person im
 * Foto (`Ai2d3dseite._rand`). Template `ai2d3d_genesiszeile.html`.
 */
import * as THREE from 'three';
import { Exportleiste } from '../exportleiste/exportleiste.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3daifigurbewegungsleiste } from '../mesh3dai/mesh3daifigurbewegungsleiste.js';
import { Mesh3daiflaechennetz } from '../mesh3dai/mesh3daiflaechennetz.js';
import { Mesh3daitestfaelle } from '../mesh3dai/mesh3daitestfaelle.js';
import { Ai2d3danpassungsfigur } from './ai2d3danpassungsfigur.js';
import { Ai2d3dansicht } from './ai2d3dansicht.js';
import { Ai2d3dexportfigur } from './ai2d3dexportfigur.js';
import { Ai2d3djoblauf } from './ai2d3djoblauf.js';
import { Ai2d3dkamera } from './ai2d3dkamera.js';
import { Ai2d3dtestfigur } from './ai2d3dtestfigur.js';
import { Ai2d3dzeilenleiste } from './ai2d3dzeilenleiste.js';

export class Ai2d3dgenesiszeile {
    static KAMERA = { position: [0, 1, 4], ziel: [0, 0.9, 0], boden: false };

    /** Die Zeile zu `seite` (`Ai2d3dseite`) — null ohne Zeile im Template oder ohne Daten. */
    static aufbauen(seite) {
        const zeile = document.getElementById('ai2d3d-genesiszeile');
        if (!zeile || !seite.daten.genesiszeile) return null;
        return new Ai2d3dgenesiszeile(seite, zeile);
    }

    /** Knopf „Genesis rechnen“: neuer Test aus dem PSHuman-Netz (`Ai2d3dgenesisstart`), danach dessen Seite mit dem Fortschritt. */
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
        zeile.querySelector('[data-aktion="genesis-rechnen"]')?.addEventListener('click', ereignis => Ai2d3dgenesiszeile._rechnen(ereignis.currentTarget));
        Ai2d3djoblauf.aufbauen(zeile);
        const g = seite.daten.genesiszeile, feld = name => document.querySelector(`[data-feld="${name}"]`);
        // eigene Leiste (04.11.2026, Edgar: „in jeder Zeile ab Zeile 3 diese ansichten plus die Rig, Kleider Toggle buttons“) — gilt für alle drei Felder der Zeile (`Ai2d3dseite._auftrag`, `Ai2d3dsmplx.zeigen`)
        this.leiste = Ai2d3dzeilenleiste.aufbauen(zeile.querySelector('[data-zeilenleiste]'), () => { this.zeigen(false); seite.smplx?.zeigen(false); seite._genesisZeigen(false); });
        const neu = () => this.zeigen(false);
        let ergebnis = null;
        if (g.ergebnis) {
            // `Ai2d3dtestfigur` setzt `Mesh3daiflaechennetz.nachLaden` für sich allein — den Ruf der Figur im Feld „Genesis-Modell“ (vorher gebaut) nicht verlieren
            const vorher = Mesh3daiflaechennetz.nachLaden;
            ergebnis = new Ai2d3dtestfigur({ kennung: g.test, adresse: g.ergebnis });
            const eigen = Mesh3daiflaechennetz.nachLaden;
            Mesh3daiflaechennetz.nachLaden = () => { vorher?.(); eigen?.(); neu(); };
        }
        this.eintraege = [['genesis-mesh3dai', g.mesh3dai ? new Ai2d3danpassungsfigur(g.mesh3dai, neu) : null, g.hinweise.mesh3dai, this.leiste],
                          ['genesis-ergebnis', ergebnis, g.hinweise.ergebnis, null]]
            .map(([name, figur, hinweis, leiste]) => ({ figur, hinweis, leiste, ansicht: new Ai2d3dansicht(feld(name), 'ausgabe', figur ?? { zeichnen: () => {} }, Ai2d3dgenesiszeile.KAMERA) }));
        // Abspielleiste und Export unter beiden Feldern (04.11.2026, Edgar: „playleiste und export für alle 3“) — derselbe Code wie unter dem Feld „Genesis-Modell“ (`Ai2d3dexportfigur`, `Ai2d3dbewegung`):
        // die Einpassung ist die Form der Zeile 1 ohne Haut und Stücke der KI, das Ergebnis die Figur der Mesh3D-AI-Testseite
        this.exportfiguren = [Ai2d3dgenesiszeile._leisten(feld('genesis-mesh3dai'), this.eintraege[0].ansicht, g.figur, true),
                              Ai2d3dgenesiszeile._leisten(feld('genesis-ergebnis'), this.eintraege[1].ansicht, g.ergebnis, false)];
        seite.fotos.gross.addEventListener('load', () => this.kameras());
        for (const e of this.eintraege) e.figur?.bereit.then(() => this.zeigen(true));
        // Testfälle des Tests wie auf der Mesh3D-AI-Testseite (06.11.2026, Edgar: „mach den besten code den wir haben in beiden pipelines“)
        const testfaelle = document.getElementById('mesh3dai-testfaelle');
        if (testfaelle) new Mesh3daitestfaelle(testfaelle).laden(`${testfaelle.dataset.adresse}?t=${Date.now()}`);
    }

    /** Das Feld Genesis-Ergebnis für „Haut angleichen“ (`Ai2d3dhautangleich`). */
    get hautort() {
        const { ansicht, figur } = this.eintraege[1];
        return { ansicht, bereit: figur?.bereit, materialien: () => (figur?.koerper ? [figur.koerper.an.material].flat() : []) };
    }

    /** Leiste und Export der Karte um `feld` an die Figur unter `adresse` (`/api/mesh3dai/test/<k>/`) — null ohne Adresse oder ohne Leiste im Template. */
    static _leisten(feld, ansicht, adresse, nackt) {
        const karte = feld.closest('section'), leiste = karte.querySelector('[data-figurbewegung]'), ausfuhr = karte.querySelector('.exportleiste');
        if (!adresse || !leiste) return null;
        const figur = new Ai2d3dexportfigur(adresse, ansicht, { nackt });
        new Mesh3daifigurbewegungsleiste(leiste, figur.bewegung).wahlLaden(leiste.dataset.adresse);
        // BVH-Vorschlag = die Standardanimation der Leiste, wie auf der Mesh3D-AI-Testseite (`Mesh3daiexportquelle.bvh`); `Ai2d3dexportfigur.bvh` gibt keinen
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
            else if (figur instanceof Ai2d3dtestfigur) ansicht.zeigen(figur.probe ? figur.auftrag(st.quelle, z.modus, z.kleider, z.rig) : null, figur.fehler || 'Figur wird gebaut …');
            else ansicht.zeigen({ modus: z.modus, kleider: z.kleider });
        }
        if (neuStellen) this.kameras();
    }

    kameras(versuch = 0) {
        const s = this.seite;
        if (s.winkel === null) return;
        const eins = new THREE.Quaternion();
        let offen = false;
        for (const a of this.felder) offen = !Ai2d3dkamera.feldStellen(a, s.winkel, eins, s._rand(a), s.kopf) || offen;
        // solange eine Figur noch lädt, ist ihre Hülle leer: nachfassen
        if (offen && versuch < 40) {
            clearTimeout(this._uhr);
            this._uhr = setTimeout(() => this.kameras(versuch + 1), 250);
        }
    }
}
