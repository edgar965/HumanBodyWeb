/**
 * Ai2d3dseite — die Jobseite `/2d-3d-AI/<job>/` (24.10.2026): Fotos · Netz · Genesis-Modell · Ergebnis und der Vergleich aus allen Perspektiven.
 *
 * Edgar: „passe dazu die Jobs an, so dass Eingabe (Fotos), ggf. Mesh (Hunyuan), Genesis Modell und das Ergebnis zu sehen ist, mit den ganzen Views und Filter (z.B. Textur, Kleider) so wie bei den
 * Mesh3d-AI Jobs“. Die beiden 3D-Felder sind `Mesh3daiansicht` (ein Renderer für alle Felder, `Mesh3daizeichenflaeche`); die Perspektive stellt beide Kameras nach der Regel der Exportfotos
 * (`Ai2d3dkamera`), ziehen dreht frei. Ist die Genesis-Figur fertig (`Mesh3daigenesisfigur.neuZeichnen`), rechnet `Ai2d3dergebnis` Feld 4 und den Vergleich neu.
 */
import * as THREE from 'three';
import { Mesh3daiansicht } from '../mesh3dai/mesh3daiansicht.js';
import { Mesh3daigenesisfigur } from '../mesh3dai/mesh3daigenesisfigur.js';
import { Ai2d3dergebnis } from './ai2d3dergebnis.js';
import { Ai2d3dfotos } from './ai2d3dfotos.js';
import { Ai2d3dgenesis } from './ai2d3dgenesis.js';
import { Ai2d3dkamera } from './ai2d3dkamera.js';
import { Ai2d3dnetz } from './ai2d3dnetz.js';
import { Ai2d3dsteuerung } from './ai2d3dsteuerung.js';

export class Ai2d3dseite {
    static KAMERA = { position: [0, 1, 4], ziel: [0, 0.9, 0], boden: false };

    static aufbauen() {
        const quelle = document.getElementById('ai2d3d-daten');
        if (!quelle) throw new Error('Ai2d3dseite: Seitendaten #ai2d3d-daten fehlen');
        return new Ai2d3dseite(JSON.parse(quelle.textContent));
    }

    constructor(daten) {
        this.daten = daten;
        const feld = name => document.querySelector(`[data-feld="${name}"]`);
        this.steuerung = new Ai2d3dsteuerung(document.getElementById('ai2d3d-steuerung'), daten, was => this._geaendert(was));
        this.fotos = new Ai2d3dfotos(feld('fotos'), document.getElementById('ai2d3d-daumen'), daten.fotos, nr => this.steuerung.setzen('foto', nr));
        this.netz = new Ai2d3dnetz(text => { this.netzfeld.hinweis.hidden = false; this.netzfeld.hinweis.textContent = text; }, () => this._netzZeigen(true));
        this.netzfeld = new Mesh3daiansicht(feld('netz'), 'eingabe', this.netz, Ai2d3dseite.KAMERA);
        this.ergebnis = new Ai2d3dergebnis(feld('ergebnis'), document.getElementById('ai2d3d-ergebnisinfo'), document.getElementById('ai2d3d-vergleich'), daten, this.fotos);
        this.genesis = daten.genesis ? new Ai2d3dgenesis(daten.genesis) : null;
        this.genesisfeld = new Mesh3daiansicht(feld('genesis'), 'ausgabe', this.genesis ?? { zeichnen: inhalt => { inhalt.userData.hinweis = Ai2d3dseite.ohneGenesis(daten); } }, Ai2d3dseite.KAMERA);
        this.genesisInfo = document.getElementById('ai2d3d-genesisinfo');
        // Die Figur wird im Hintergrund gebaut; ist sie da (oder eine feinere Netzstufe), zeigt das Feld sie neu und der Vergleich rechnet nach.
        Mesh3daigenesisfigur.neuZeichnen = () => this._genesisZeigen(false);
        this.fotos.waehlen(this.steuerung.foto);
        this._netzZeigen(true);
        if (this.genesis) this.genesis.bereit.then(() => this._genesisZeigen(true));
        else {
            this.genesisfeld.zeigen({}, Ai2d3dseite.ohneGenesis(daten));
            this.ergebnis.leeren(Ai2d3dseite.ohneGenesis(daten));
        }
    }

    static ohneGenesis(daten) {
        return daten.test ? `Noch kein Genesis-Modell für 2d-3d-AI. Messlatte A (Tripo-Netz → Mesh3D-AI) steht auf der Testseite ${daten.test.kennung}.`
            : 'Noch kein Genesis-Modell für diesen Job.';
    }

    get winkel() {
        return this.daten.fotos[this.steuerung.foto]?.winkel ?? null;
    }

    _geaendert(was) {
        if (was === 'foto') {
            this.fotos.waehlen(this.steuerung.foto);
            this._kameras();
            this._vergleich();
        } else if (was === 'netz') {
            this._netzZeigen(true);
        } else {
            this._netzZeigen(false);
            this._genesisZeigen(was !== 'modus');
        }
    }

    _netzZeigen(neuStellen) {
        const netz = this.daten.netze[this.steuerung.netz] ?? null;
        this.netzfeld.zeigen({ netz, modus: this.steuerung.modus }, netz ? null : 'Für diesen Job liegt kein Netz aus den Fotos vor.');
        if (neuStellen && this.winkel !== null) Ai2d3dkamera.feldStellen(this.netzfeld, this.winkel, new THREE.Quaternion());
    }

    _auftrag() {
        return this.genesis.auftrag(this.steuerung.quelle, this.steuerung.modus, this.steuerung.kleider);
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
        this.genesisInfo.textContent = fertig ? (this.genesis.text ?? '') : 'Genesis-Figur wird gebaut …';
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

    _kameras() {
        if (this.winkel === null) return;
        Ai2d3dkamera.feldStellen(this.netzfeld, this.winkel, new THREE.Quaternion());
        if (this.genesis?.fertig(this._auftrag())) Ai2d3dkamera.feldStellen(this.genesisfeld, this.winkel, this._rahmen());
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
