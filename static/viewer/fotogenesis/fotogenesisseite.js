/**
 * Fotogenesisseite — die Jobseite `/foto-genesis/<job>/` (24.10.2026): Fotos · Netz · Genesis-Modell · Ergebnis und der Vergleich aus allen Perspektiven.
 * Edgar: „passe dazu die Jobs an, so dass Eingabe (Fotos), ggf. Mesh (Hunyuan), Genesis Modell und das Ergebnis zu sehen ist, mit den ganzen Views und Filter (z.B. Textur, Kleider) so wie bei den
 * Mesh3d-AI Jobs“. Die beiden 3D-Felder sind `Meshgenesisansicht` (ein Renderer für alle Felder, `Meshgenesiszeichenflaeche`); die Perspektive stellt beide Kameras nach der Regel der Exportfotos
 * (`Fotogenesiskamera`), ziehen dreht frei. Ist die Genesis-Figur fertig (`Meshgenesisgenesisfigur.neuZeichnen`), rechnet `Fotogenesisergebnis` Feld 4 und den Vergleich neu.
 */
import * as THREE from 'three';
import { Meshgenesisansicht } from '../meshgenesis/meshgenesisansicht.js';
import { Meshgenesisgenesisfigur } from '../meshgenesis/meshgenesisgenesisfigur.js';
import { Fotogenesisansicht } from './fotogenesisansicht.js';
import { Fotogenesisbloecke } from './fotogenesisbloecke.js';
import { Fotogenesisergebnis } from './fotogenesisergebnis.js';
import { Fotogenesisfotomass } from './fotogenesisfotomass.js';
import { Fotogenesisfotos } from './fotogenesisfotos.js';
import { Fotogenesisgenesis } from './fotogenesisgenesis.js';
import { Fotogenesiskamera } from './fotogenesiskamera.js';
import { Fotogenesismeshzeile } from './fotogenesismeshzeile.js';
import { Fotogenesismesspunkte } from './fotogenesismesspunkte.js';
import { Fotogenesisnetz } from './fotogenesisnetz.js';
import { Fotogenesisseitenbild } from './fotogenesisseitenbild.js';
import { Fotogenesissmplx } from './fotogenesissmplx.js';
import { Fotogenesisgenesiszeile } from './fotogenesisgenesiszeile.js';
import { Fotogenesissteuerung } from './fotogenesissteuerung.js';
import { Fotogenesistestfigur } from './fotogenesistestfigur.js';
import { Fotogenesistrainingfigur } from './fotogenesistrainingfigur.js';
import { Fotogenesiszeilenleiste } from './fotogenesiszeilenleiste.js';

export class Fotogenesisseite {
    static KAMERA = { position: [0, 1, 4], ziel: [0, 0.9, 0], boden: false };

    static aufbauen() {
        const quelle = document.getElementById('fotogenesis-daten');
        if (!quelle) throw new Error('Fotogenesisseite: Seitendaten #fotogenesis-daten fehlen');
        // Messzugang für die Browser-Prüfung (wie `__characters` der Charakter-Seite)
        window.__fotogenesis = new Fotogenesisseite(JSON.parse(quelle.textContent));
        return window.__fotogenesis;
    }

    /**
     * Die Figur dieser Seite aus der Kamera jedes Fotos an den Server geben — Eingang der Abnahme (`Fotogenesisseitenbild`, `koerperpruefung_lauf.py --seite`).
     * Das Feld der Figur baut erst, wenn es ins Bild kommt (`Meshgenesisansicht._auftrag`); ohne Scrollen brach die Aufnahme mit „zeigt keine Figur“ ab (03.11.2026). Darum hier auf die
     * Figur warten und das Feld sofort bauen lassen — auch eine feinere Stufe, die währenddessen nachkommt, höchstens 60 s.
     */
    async seitenbilder() {
        if (this.genesis) {
            await this.genesis.bereit;
            this.genesisfeld.jetztFuellen();
            for (let i = 0; i < 240 && this.genesis instanceof Fotogenesistestfigur && !this.genesis.figur?.parent; i++) {
                await new Promise(r => setTimeout(r, 250));
                this.genesisfeld.jetztFuellen();
            }
        }
        return Fotogenesisseitenbild.aufnehmen(this);
    }

    /** Der eine Grund aller Felder (24.10.2026, Edgar: „heller sein, und gleich“): weiß wie die freigestellten Fotos; bei Exporten der Grund der Exportfotos (die Fotos selbst tragen ihn). */
    static grund(daten) {
        return daten.kamera?.grund ?? [255, 255, 255];
    }

    constructor(daten) {
        this.daten = daten;
        const feld = name => document.querySelector(`[data-feld="${name}"]`);
        const grund = Fotogenesisseite.grund(daten);
        Fotogenesisansicht.grund = new THREE.Color().setRGB(...grund.map(v => v / 255), THREE.SRGBColorSpace).getHex();
        document.documentElement.style.setProperty('--fotogenesis-grund', `rgb(${grund.join(', ')})`);
        this.steuerung = new Fotogenesissteuerung(document.getElementById('fotogenesis-steuerung'), daten, was => this._geaendert(was));
        // Zeile „Test: Netz aus den Fotos“ mit eigener Leiste (04.11.2026, „in jeder Zeile ab Zeile 3“) — ohne Kleider und Rig: das rohe Netz hat beides nicht
        this.netzleiste = Fotogenesiszeilenleiste.aufbauen(document.querySelector('[data-zeilenleiste="netz"]'), () => this._netzZeigen(false), { kleider: false, rig: false });
        this.fotos = new Fotogenesisfotos(feld('fotos'), document.getElementById('fotogenesis-daumen'), daten.fotos, nr => this.steuerung.setzen('foto', nr));
        this.netz = new Fotogenesisnetz(text => { this.netzfeld.hinweis.hidden = false; this.netzfeld.hinweis.textContent = text; }, () => this._netzZeigen(true));
        this.netzfeld = new Fotogenesisansicht(feld('netz'), 'eingabe', this.netz, Fotogenesisseite.KAMERA);
        this.ergebnis = new Fotogenesisergebnis(feld('ergebnis'), document.getElementById('fotogenesis-ergebnisinfo'), document.getElementById('fotogenesis-vergleich'), daten, this.fotos);
        this.ergebnis.seite = this;          // Feld „Ergebnis“ aus Kamera und Haltung der Einpassung, wenn der Job sie hat (26.10.2026, `Fotogenesisergebnis._einpassung`)
        // 27.10.2026: mit gerechneter Figur der Kopf-KI steht sie in Feld 2 (3D), das Genesis-Modell in Feld 3, kein Ergebnis-Feld (`Fotogenesistrainingfigur`, Template)
        if (daten.trainingfigur) {
            this.trainingfigur = new Fotogenesistrainingfigur(daten.trainingfigur);
            // PSHuman-Jobs haben in Zeile 2 kein Feld dafür (Fotos · PSHuman · SMPL-X); die Figur bleibt für die Mesh-Zeile und Feld 2 (`Fotogenesiszeile1`) — ohne die Prüfung
            // brach edgartrip seit dem Layout vom 04.11.2026 beim Aufbau ab (Feld ohne Behälter, im Chrome gesehen)
            const f = feld('trainingfigur');
            if (f) this.trainingfeld = new Fotogenesisansicht(f, 'ausgabe', this.trainingfigur, Fotogenesisseite.KAMERA);
            this.trainingfigur.bereit.then(() => { this._trainingZeigen(); this._kameras(); });
        }
        this.genesis = daten.genesis ? new Fotogenesisgenesis(daten.genesis) : daten.test?.adresse ? new Fotogenesistestfigur(daten.test, this) : null;
        this.genesisfeld = new Fotogenesisansicht(feld('genesis'), 'ausgabe', this.genesis ?? { zeichnen: inhalt => { inhalt.userData.hinweis = Fotogenesisseite.ohneGenesis(daten); } }, Fotogenesisseite.KAMERA);
        this.genesisInfo = document.getElementById('fotogenesis-genesisinfo');
        // alle 3D-Felder drehen gemeinsam (24.10.2026, „synchron … so wie bei Mesh-Genesis“), seit 28.10.2026 auch die der Mesh-Zeile ganz oben (`Fotogenesismeshzeile`)
        this.meshzeile = Fotogenesismeshzeile.aufbauen(this);
        this.smplx = Fotogenesissmplx.aufbauen(this);             // 03.11.2026: PSHumans SMPL-X in jeder Zeile (nur PSHuman-Jobs), seit 04.11. Feld 3
        this.pshuman = Fotogenesissmplx.aufbauen(this, 'pshuman');   // 04.11.2026: Feld 2 jeder Zeile, PSHumans Endnetz (nur PSHuman-Jobs)
        this.genesiszeile = Fotogenesisgenesiszeile.aufbauen(this);  // 04.11.2026: dritte Zeile, drei Wege vom PSHuman-Netz zum Genesis-Modell (nach `genesis` gebaut, s. dort)
        Meshgenesisansicht.koppeln([this.netzfeld, this.trainingfeld, this.genesisfeld, ...(this.meshzeile?.felder ?? []), ...(this.smplx?.felder ?? []),
                                 ...(this.pshuman?.felder ?? []), ...(this.genesiszeile?.felder ?? [])].filter(Boolean));
        // Größe wie die Person im Foto (27.10.2026, `_rand`): ist das neue Foto geladen, die Kameras nachstellen
        this.fotos.gross.addEventListener('load', () => this._kameras());
        // Die Figur wird im Hintergrund gebaut; ist sie da (oder eine feinere Netzstufe), zeigt das Feld sie neu und der Vergleich rechnet nach.
        Meshgenesisgenesisfigur.neuZeichnen = () => this._genesisZeigen(false);
        // Vergleich nach nachgeladenen Texturen: einmal, wenn der Browser frei ist (08.11.2026) — vorher 500 ms nach JEDER Textur, und die Stücke kamen einzeln: der ganze Vergleich (acht
        // Perspektiven, je Rendering, Maske, Pixelvergleich) lief so bis zu zwölfmal, während die übrigen Felder noch luden
        if (this.genesis instanceof Fotogenesistestfigur) this.genesis.nachgeladen = () => {
            clearTimeout(this._uhr);
            this._uhr = setTimeout(() => (window.requestIdleCallback ?? (f => f()))(() => this._vergleich(), { timeout: 5000 }), 1500);
        };
        // Testzeilen „Messpunkte des Körpers“ und (25.10.2026) „… des Kopfes“ (nur Tests aus Fotos; Karten stehen nur dann im Template) — folgen der Wahl des Fotos
        const messkarte = document.getElementById('fotogenesis-messpunkte'), kopfkarte = document.getElementById('fotogenesis-kopfmesspunkte');
        const reglerkarte = document.getElementById('fotogenesis-reglermesspunkte');     // 25.10.2026 abends: an den Anfassern der Eigenregler (`Reglermesspunkte`)
        const umrisskarte = document.getElementById('fotogenesis-reglerumrisse');        // 26.10.2026: die ganzen Umrisse der Eigenregler (`Reglerumrisse`)
        // 26.10.2026: die 478 Punkte von MediaPipe — Messung der Kopf-KI und die zwei Karten ihres Fehlers (`Gesichtsmesspunkte`); `data-gesichtspunkte` = Adresse der Daten
        const gesichtskarten = [...document.querySelectorAll('[data-gesichtspunkte]')];
        const seite = nr => `/api/fotogenesis/${daten.id}/abnahme/seite/${nr}/`, zeile = (karte, name) => karte
            && new Fotogenesismesspunkte(karte, daten.id, daten.fotos, { daten: `/api/fotogenesis/${daten.id}/abnahme/${name}/`, seite });
        this.messpunkte = [messkarte && new Fotogenesismesspunkte(messkarte, daten.id, daten.fotos), zeile(kopfkarte, 'kopfmesspunkte'),
                           zeile(reglerkarte, 'reglermesspunkte'), zeile(umrisskarte, 'reglerumrisse'),
                           ...gesichtskarten.map(k => zeile(k, k.dataset.gesichtspunkte))].filter(Boolean);
        // Ampel und Blöcke Kopf/Körper vorne/seitlich (26.10.2026, Seite aufgeräumt) — mit eigener Fotowahl, sie folgen der Leiste nicht
        if (document.querySelector('[data-block]')) this.bloecke = new Fotogenesisbloecke(daten);
        this.fotos.waehlen(this.steuerung.foto);
        for (const m of this.messpunkte) m.zeigen(this.steuerung.foto);
        this._netzZeigen(true);
        this.smplx?.zeigen(true);
        this.pshuman?.zeigen(true);
        this.genesiszeile?.zeigen(true);
        if (this.genesis) this.genesis.bereit.then(() => this._genesisZeigen(true));
        else {
            this.genesisfeld.zeigen({}, Fotogenesisseite.ohneGenesis(daten));
            this.ergebnis.leeren(Fotogenesisseite.ohneGenesis(daten));
        }
    }

    static ohneGenesis(daten) {
        if (daten.genesiszeile) return 'Die Foto-Kette ist stillgelegt (09.11.2026): Das Genesis-Modell kommt aus Mesh-Genesis, Feld „Genesis-Ergebnis“.';
        return daten.test && !daten.test.eigen ? `Noch kein Genesis-Modell für Foto-Genesis. Messlatte A (Tripo-Netz → Mesh-Genesis) steht auf der Testseite ${daten.test.kennung}.`
            : 'Noch kein Genesis-Modell für diesen Job.';
    }

    get winkel() {
        return this.daten.fotos[this.steuerung.foto]?.winkel ?? null;
    }

    _geaendert(was) {
        if (was === 'ansicht') {          // Ansicht der Leiste oben (04.11.2026 mit „Normale“ und „Netz farbig“): für die Felder wie bisher eine Änderung der Ansichtsart
            Fotogenesisansicht.seitenart = this.steuerung.art;
            was = 'modus';
        }
        if (was !== 'netz') { this._trainingZeigen(); this.meshzeile?.aktualisieren(); if (was === 'foto') this._genesisZeigen(false); }   // Feld 3 je Foto (`Fotogenesiszeile1`)
        if (was === 'foto') {
            this.fotos.waehlen(this.steuerung.foto);
            for (const m of this.messpunkte) m.zeigen(this.steuerung.foto);
            this._kameras();
            this._vergleich();
        } else if (was === 'ausschnitt') {
            this._kameras();
        } else if (was === 'netz') {
            this._netzZeigen(true);
        } else {
            this._netzZeigen(false);
            this._genesisZeigen(was !== 'modus' && was !== 'rig');
        }
        if (was !== 'netz') for (const z of [this.smplx, this.pshuman, this.genesiszeile]) z?.zeigen(was === 'foto' || was === 'ausschnitt');
    }

    _netzZeigen(neuStellen) {
        const netz = this.daten.netze[this.steuerung.netz] ?? null;
        this.netzfeld.zeilenart = this.netzleiste?.art ?? null;
        this.netzfeld.zeigen({ netz, modus: (this.netzleiste ?? this.steuerung).modus }, netz ? null : 'Für diesen Job liegt kein Netz aus den Fotos vor.');
        if (neuStellen && this.winkel !== null) Fotogenesiskamera.feldStellen(this.netzfeld, this.winkel, new THREE.Quaternion(), this._rand(this.netzfeld), this.kopf);
    }

    get kopf() {
        return this.steuerung.ausschnitt === 'kopf';
    }

    /**
     * Luft um die Figur (`Fotogenesiskamera.feldStellen`), sodass sie in `ansicht` so hoch steht wie die Person im Foto von Feld 1 (27.10.2026, Edgar: „die Größen aller Figuren bitte
     * gleich machen“; bis dahin 1,08 auf die Hülle, die gerechnete Figur aus der Kamera des Fotos — drei verschiedene Größen). Beim Ausschnitt „Kopf“ und ohne geladenes Foto die Vorgabe.
     */
    _rand(ansicht) {
        const px = this.kopf || !this.fotos.gross.complete ? null : Fotogenesisfotomass.personPx(this.fotos.gross, this.fotos.feld);
        return px ? ansicht.feld.clientHeight / px : undefined;
    }

    /** Feld „Gerechnete Figur“ neu zeigen (die Kamera stellt `_kameras`). */
    _trainingZeigen() {
        if (!this.trainingfeld) return;
        this.trainingfeld.zeigen({ nr: this.steuerung.foto, modus: this.steuerung.modus });
        // kein Text unter dem Feld (27.10.2026, Edgar: „entferne diesen Text aus dem Geometrie view“), nur ein Fehler beim Laden
        document.getElementById('fotogenesis-trainingfigurinfo').textContent = this.trainingfigur.fehler ? `Gerechnete Figur nicht geladen: ${this.trainingfigur.fehler}` : '';
    }

    /** Steht das Genesis-Modell in der dritten Zeile, gilt deren Leiste (04.11.2026, `Fotogenesiszeilenleiste`), sonst die oben. */
    _auftrag() {
        const z = this.genesiszeile?.leiste ?? this.steuerung;
        return this.genesis.auftrag(this.steuerung.quelle, z.modus, z.kleider, z.rig);
    }

    /** Feld 3 neu zeigen; `neuStellen`: die Kamera auf die Perspektive setzen (bei neuer Figur, nicht beim Wechsel der Ansichtsart). */
    _genesisZeigen(neuStellen) {
        if (!this.genesis?.probe) {
            this.genesisfeld.zeigen({}, this.genesis?.fehler || Fotogenesisseite.ohneGenesis(this.daten));
            return;
        }
        const d = this._auftrag();
        this.genesisfeld.zeilenart = this.genesiszeile?.leiste?.art ?? null;
        this.genesisfeld.zeigen(d);
        const fertig = this.genesis.fertig(d);
        this.genesisInfo.textContent = fertig ? '' : 'Genesis-Figur wird gebaut …';      // die Beschreibung der Figur steht nicht mehr unter dem Feld (Edgar 26.10.2026: „entferne den Text“)
        if (!fertig) return;
        const neueFigur = this._gezeigt !== `${d.quelle}|${d.zeile}|${d.kleider}`;
        this._gezeigt = `${d.quelle}|${d.zeile}|${d.kleider}`;
        // Der Rahmen der Fotos kommt bei Exporten erst, wenn auch die Wahrheit gebaut ist — dann einmal Kameras und Vergleich nachziehen.
        const rahmenNeu = this.daten.wahrheit && !this._mitRahmen && !!this.genesis.rahmen();
        if (rahmenNeu) this._mitRahmen = true;
        if (neuStellen || neueFigur || rahmenNeu) this._kameras();
        if (neueFigur || rahmenNeu) this._vergleich();
    }

    /** Der Rahmen der Fotos: bei Exporten an der wahren Figur gemessen (`Fotogenesisgenesis.rahmen`, baut sie bei Bedarf), sonst keine Drehung. */
    _rahmen() {
        return (this.daten.wahrheit && this.genesis?.rahmen()) || new THREE.Quaternion();
    }

    _kameras(versuch = 0) {
        if (this.winkel === null) return;
        // Gekoppelt übernimmt das zweite Feld die Kamera des ersten — darum zuerst Netz und gerechnete Figur, zuletzt das Genesis-Modell (sein Rahmen gilt für alle).
        const eins = new THREE.Quaternion();
        Fotogenesiskamera.feldStellen(this.netzfeld, this.winkel, eins, this._rand(this.netzfeld), this.kopf);
        // Ein Feld zeichnet erst, wenn es im Fenster steht (`Meshgenesisansicht`): bis dahin ist seine Hülle leer — nachfassen, bis die Figur darin liegt.
        let offen = !!this.trainingfeld && !!this.trainingfigur?.daten && !Fotogenesiskamera.feldStellen(this.trainingfeld, this.winkel, eins, this._rand(this.trainingfeld), this.kopf);
        if (this.genesis?.fertig(this._auftrag())) {
            offen = !Fotogenesiskamera.feldStellen(this.genesisfeld, this.winkel, this._rahmen(), this._rand(this.genesisfeld), this.kopf) || offen;
        }
        if (offen && versuch < 40) {
            clearTimeout(this._nachfassen);
            this._nachfassen = setTimeout(() => this._kameras(versuch + 1), 250);
        }
    }

    _vergleich() {
        if (!this.genesis?.fertig(this._auftrag())) return;
        if (this.daten.wahrheit && !this.genesis.rahmen()) {
            // Die Wahrheit wird für den Rahmen gebaut; ist sie fertig, ruft `neuZeichnen` hier wieder an.
            this.ergebnis.info.textContent = 'Rahmen der Fotos wird an der wahren Figur gemessen …';
            return;
        }
        this.ergebnis.zeigen(this.genesisfeld, this._rahmen(), this.steuerung.foto)
            .catch(fehler => { this.ergebnis.info.textContent = `Vergleich gescheitert: ${fehler.message}`; console.warn(`Fotogenesisseite: ${fehler.message}`); });
    }
}
