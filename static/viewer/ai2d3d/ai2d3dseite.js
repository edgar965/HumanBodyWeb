/**
 * Ai2d3dseite — die Jobseite `/2d-3d-AI/<job>/` (24.10.2026): Fotos · Netz · Genesis-Modell · Ergebnis und der Vergleich aus allen Perspektiven.
 * Edgar: „passe dazu die Jobs an, so dass Eingabe (Fotos), ggf. Mesh (Hunyuan), Genesis Modell und das Ergebnis zu sehen ist, mit den ganzen Views und Filter (z.B. Textur, Kleider) so wie bei den
 * Mesh3d-AI Jobs“. Die beiden 3D-Felder sind `Mesh3daiansicht` (ein Renderer für alle Felder, `Mesh3daizeichenflaeche`); die Perspektive stellt beide Kameras nach der Regel der Exportfotos
 * (`Ai2d3dkamera`), ziehen dreht frei. Ist die Genesis-Figur fertig (`Mesh3daigenesisfigur.neuZeichnen`), rechnet `Ai2d3dergebnis` Feld 4 und den Vergleich neu.
 */
import * as THREE from 'three';
import { Mesh3daiansicht } from '../mesh3dai/mesh3daiansicht.js';
import { Mesh3daigenesisfigur } from '../mesh3dai/mesh3daigenesisfigur.js';
import { Ai2d3dansicht } from './ai2d3dansicht.js';
import { Ai2d3dbloecke } from './ai2d3dbloecke.js';
import { Ai2d3dergebnis } from './ai2d3dergebnis.js';
import { Ai2d3dfotomass } from './ai2d3dfotomass.js';
import { Ai2d3dfotos } from './ai2d3dfotos.js';
import { Ai2d3dgenesis } from './ai2d3dgenesis.js';
import { Ai2d3dkamera } from './ai2d3dkamera.js';
import { Ai2d3dmeshzeile } from './ai2d3dmeshzeile.js';
import { Ai2d3dmesspunkte } from './ai2d3dmesspunkte.js';
import { Ai2d3dnetz } from './ai2d3dnetz.js';
import { Ai2d3dseitenbild } from './ai2d3dseitenbild.js';
import { Ai2d3dsteuerung } from './ai2d3dsteuerung.js';
import { Ai2d3dtestfigur } from './ai2d3dtestfigur.js';
import { Ai2d3dtrainingfigur } from './ai2d3dtrainingfigur.js';

export class Ai2d3dseite {
    static KAMERA = { position: [0, 1, 4], ziel: [0, 0.9, 0], boden: false };

    static aufbauen() {
        const quelle = document.getElementById('ai2d3d-daten');
        if (!quelle) throw new Error('Ai2d3dseite: Seitendaten #ai2d3d-daten fehlen');
        // Messzugang für die Browser-Prüfung (wie `__characters` der Charakter-Seite)
        window.__ai2d3d = new Ai2d3dseite(JSON.parse(quelle.textContent));
        return window.__ai2d3d;
    }

    /** Die Figur dieser Seite aus der Kamera jedes Fotos an den Server geben — Eingang der Abnahme (`Ai2d3dseitenbild`, `koerperpruefung_lauf.py --seite`). */
    seitenbilder() {
        return Ai2d3dseitenbild.aufnehmen(this);
    }

    /** Der eine Grund aller Felder (24.10.2026, Edgar: „heller sein, und gleich“): weiß wie die freigestellten Fotos; bei Exporten der Grund der Exportfotos (die Fotos selbst tragen ihn). */
    static grund(daten) {
        return daten.kamera?.grund ?? [255, 255, 255];
    }

    constructor(daten) {
        this.daten = daten;
        const feld = name => document.querySelector(`[data-feld="${name}"]`);
        const grund = Ai2d3dseite.grund(daten);
        Ai2d3dansicht.grund = new THREE.Color().setRGB(...grund.map(v => v / 255), THREE.SRGBColorSpace).getHex();
        document.documentElement.style.setProperty('--ai2d3d-grund', `rgb(${grund.join(', ')})`);
        this.steuerung = new Ai2d3dsteuerung(document.getElementById('ai2d3d-steuerung'), daten, was => this._geaendert(was));
        this.fotos = new Ai2d3dfotos(feld('fotos'), document.getElementById('ai2d3d-daumen'), daten.fotos, nr => this.steuerung.setzen('foto', nr));
        this.netz = new Ai2d3dnetz(text => { this.netzfeld.hinweis.hidden = false; this.netzfeld.hinweis.textContent = text; }, () => this._netzZeigen(true));
        this.netzfeld = new Ai2d3dansicht(feld('netz'), 'eingabe', this.netz, Ai2d3dseite.KAMERA);
        this.ergebnis = new Ai2d3dergebnis(feld('ergebnis'), document.getElementById('ai2d3d-ergebnisinfo'), document.getElementById('ai2d3d-vergleich'), daten, this.fotos);
        this.ergebnis.seite = this;          // Feld „Ergebnis“ aus Kamera und Haltung der Einpassung, wenn der Job sie hat (26.10.2026, `Ai2d3dergebnis._einpassung`)
        // 27.10.2026: mit gerechneter Figur der Kopf-KI steht sie in Feld 2 (3D), das Genesis-Modell in Feld 3, kein Ergebnis-Feld (`Ai2d3dtrainingfigur`, Template)
        if (daten.trainingfigur) {
            this.trainingfigur = new Ai2d3dtrainingfigur(daten.trainingfigur);
            this.trainingfeld = new Ai2d3dansicht(feld('trainingfigur'), 'ausgabe', this.trainingfigur, Ai2d3dseite.KAMERA);
            this.trainingfigur.bereit.then(() => { this._trainingZeigen(); this._kameras(); });
        }
        this.genesis = daten.genesis ? new Ai2d3dgenesis(daten.genesis) : daten.test?.adresse ? new Ai2d3dtestfigur(daten.test) : null;
        this.genesisfeld = new Ai2d3dansicht(feld('genesis'), 'ausgabe', this.genesis ?? { zeichnen: inhalt => { inhalt.userData.hinweis = Ai2d3dseite.ohneGenesis(daten); } }, Ai2d3dseite.KAMERA);
        this.genesisInfo = document.getElementById('ai2d3d-genesisinfo');
        // alle 3D-Felder drehen gemeinsam (24.10.2026, „synchron … so wie bei Mesh3d-AI“), seit 28.10.2026 auch die der Mesh-Zeile ganz oben (`Ai2d3dmeshzeile`)
        this.meshzeile = Ai2d3dmeshzeile.aufbauen(this);
        Mesh3daiansicht.koppeln([this.netzfeld, this.trainingfeld, this.genesisfeld, ...(this.meshzeile?.felder ?? [])].filter(Boolean));
        // Größe wie die Person im Foto (27.10.2026, `_rand`): ist das neue Foto geladen, die Kameras nachstellen
        this.fotos.gross.addEventListener('load', () => this._kameras());
        // Die Figur wird im Hintergrund gebaut; ist sie da (oder eine feinere Netzstufe), zeigt das Feld sie neu und der Vergleich rechnet nach.
        Mesh3daigenesisfigur.neuZeichnen = () => this._genesisZeigen(false);
        if (this.genesis instanceof Ai2d3dtestfigur) this.genesis.nachgeladen = () => { clearTimeout(this._uhr); this._uhr = setTimeout(() => this._vergleich(), 500); };
        // Testzeilen „Messpunkte des Körpers“ und (25.10.2026) „… des Kopfes“ (nur Tests aus Fotos; Karten stehen nur dann im Template) — folgen der Wahl des Fotos
        const messkarte = document.getElementById('ai2d3d-messpunkte'), kopfkarte = document.getElementById('ai2d3d-kopfmesspunkte');
        const reglerkarte = document.getElementById('ai2d3d-reglermesspunkte');     // 25.10.2026 abends: an den Anfassern der Eigenregler (`Reglermesspunkte`)
        const umrisskarte = document.getElementById('ai2d3d-reglerumrisse');        // 26.10.2026: die ganzen Umrisse der Eigenregler (`Reglerumrisse`)
        // 26.10.2026: die 478 Punkte von MediaPipe — Messung der Kopf-KI und die zwei Karten ihres Fehlers (`Gesichtsmesspunkte`); `data-gesichtspunkte` = Adresse der Daten
        const gesichtskarten = [...document.querySelectorAll('[data-gesichtspunkte]')];
        const seite = nr => `/api/2d3dai/${daten.id}/abnahme/seite/${nr}/`, zeile = (karte, name) => karte
            && new Ai2d3dmesspunkte(karte, daten.id, daten.fotos, { daten: `/api/2d3dai/${daten.id}/abnahme/${name}/`, seite });
        this.messpunkte = [messkarte && new Ai2d3dmesspunkte(messkarte, daten.id, daten.fotos), zeile(kopfkarte, 'kopfmesspunkte'),
                           zeile(reglerkarte, 'reglermesspunkte'), zeile(umrisskarte, 'reglerumrisse'),
                           ...gesichtskarten.map(k => zeile(k, k.dataset.gesichtspunkte))].filter(Boolean);
        // Ampel und Blöcke Kopf/Körper vorne/seitlich (26.10.2026, Seite aufgeräumt) — mit eigener Fotowahl, sie folgen der Leiste nicht
        if (document.querySelector('[data-block]')) this.bloecke = new Ai2d3dbloecke(daten);
        this.fotos.waehlen(this.steuerung.foto);
        for (const m of this.messpunkte) m.zeigen(this.steuerung.foto);
        this._netzZeigen(true);
        if (this.genesis) this.genesis.bereit.then(() => this._genesisZeigen(true));
        else {
            this.genesisfeld.zeigen({}, Ai2d3dseite.ohneGenesis(daten));
            this.ergebnis.leeren(Ai2d3dseite.ohneGenesis(daten));
        }
    }

    static ohneGenesis(daten) {
        return daten.test && !daten.test.eigen ? `Noch kein Genesis-Modell für 2d-3d-AI. Messlatte A (Tripo-Netz → Mesh3D-AI) steht auf der Testseite ${daten.test.kennung}.`
            : 'Noch kein Genesis-Modell für diesen Job.';
    }

    get winkel() {
        return this.daten.fotos[this.steuerung.foto]?.winkel ?? null;
    }

    _geaendert(was) {
        if (was !== 'netz') { this._trainingZeigen(); this.meshzeile?.aktualisieren(); }
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
    }

    _netzZeigen(neuStellen) {
        const netz = this.daten.netze[this.steuerung.netz] ?? null;
        this.netzfeld.zeigen({ netz, modus: this.steuerung.modus }, netz ? null : 'Für diesen Job liegt kein Netz aus den Fotos vor.');
        if (neuStellen && this.winkel !== null) Ai2d3dkamera.feldStellen(this.netzfeld, this.winkel, new THREE.Quaternion(), this._rand(this.netzfeld), this.kopf);
    }

    get kopf() {
        return this.steuerung.ausschnitt === 'kopf';
    }

    /**
     * Luft um die Figur (`Ai2d3dkamera.feldStellen`), sodass sie in `ansicht` so hoch steht wie die Person im Foto von Feld 1 (27.10.2026, Edgar: „die Größen aller Figuren bitte
     * gleich machen“; bis dahin 1,08 auf die Hülle, die gerechnete Figur aus der Kamera des Fotos — drei verschiedene Größen). Beim Ausschnitt „Kopf“ und ohne geladenes Foto die Vorgabe.
     */
    _rand(ansicht) {
        const px = this.kopf || !this.fotos.gross.complete ? null : Ai2d3dfotomass.personPx(this.fotos.gross, this.fotos.feld);
        return px ? ansicht.feld.clientHeight / px : undefined;
    }

    /** Feld „Gerechnete Figur“ neu zeigen (die Kamera stellt `_kameras`). */
    _trainingZeigen() {
        if (!this.trainingfeld) return;
        this.trainingfeld.zeigen({ nr: this.steuerung.foto, modus: this.steuerung.modus });
        // kein Text unter dem Feld (27.10.2026, Edgar: „entferne diesen Text aus dem Geometrie view“), nur ein Fehler beim Laden
        document.getElementById('ai2d3d-trainingfigurinfo').textContent = this.trainingfigur.fehler ? `Gerechnete Figur nicht geladen: ${this.trainingfigur.fehler}` : '';
    }

    _auftrag() {
        return this.genesis.auftrag(this.steuerung.quelle, this.steuerung.modus, this.steuerung.kleider, this.steuerung.rig);
    }

    /** Feld 3 neu zeigen; `neuStellen`: die Kamera auf die Perspektive setzen (bei neuer Figur, nicht beim Wechsel der Ansichtsart). */
    _genesisZeigen(neuStellen) {
        if (!this.genesis?.probe) {
            this.genesisfeld.zeigen({}, this.genesis?.fehler || Ai2d3dseite.ohneGenesis(this.daten));
            return;
        }
        const d = this._auftrag();
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

    /** Der Rahmen der Fotos: bei Exporten an der wahren Figur gemessen (`Ai2d3dgenesis.rahmen`, baut sie bei Bedarf), sonst keine Drehung. */
    _rahmen() {
        return (this.daten.wahrheit && this.genesis?.rahmen()) || new THREE.Quaternion();
    }

    _kameras(versuch = 0) {
        if (this.winkel === null) return;
        // Gekoppelt übernimmt das zweite Feld die Kamera des ersten — darum zuerst Netz und gerechnete Figur, zuletzt das Genesis-Modell (sein Rahmen gilt für alle).
        const eins = new THREE.Quaternion();
        Ai2d3dkamera.feldStellen(this.netzfeld, this.winkel, eins, this._rand(this.netzfeld), this.kopf);
        // Ein Feld zeichnet erst, wenn es im Fenster steht (`Mesh3daiansicht`): bis dahin ist seine Hülle leer — nachfassen, bis die Figur darin liegt.
        let offen = !!this.trainingfigur?.daten && !Ai2d3dkamera.feldStellen(this.trainingfeld, this.winkel, eins, this._rand(this.trainingfeld), this.kopf);
        if (this.genesis?.fertig(this._auftrag())) {
            offen = !Ai2d3dkamera.feldStellen(this.genesisfeld, this.winkel, this._rahmen(), this._rand(this.genesisfeld), this.kopf) || offen;
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
            .catch(fehler => { this.ergebnis.info.textContent = `Vergleich gescheitert: ${fehler.message}`; console.warn(`Ai2d3dseite: ${fehler.message}`); });
    }
}
