/**
 * Rigstart — das HumanBody-Rig kommt beim Seitenstart, nicht nach dem Play.
 *
 * Edgar (12.09.2026): „nach dem Play startet das Video oben mit einem
 * anderen Rig, erst nach einigen Sekunden ändert sich das Rig, und startet
 * auch das untere Video" — und: „gleich nach dem Wechsel in den Result soll
 * das richtige Rig der Animation geladen werden".
 *
 * Vorher lud der Spieler erst die BVH-Datei, dann das Rig mit einem eigenen
 * Retarget-Abruf; bis der da war, zeigte das Fenster das BVH-Skelett (das
 * „andere Rig"), und die 3D-Figur unten wartete auf ihren eigenen Abruf.
 * Jetzt:
 *
 *   1. Das Rig wird SOFORT gebaut, parallel zur BVH-Datei.
 *   2. Seinen Clip nimmt es von der 3D-Figur (`Klipquelle`) — derselbe
 *      Abruf, dieselbe Höhe, dieselbe Bewegung oben wie unten.
 *   3. Solange es lädt, bleibt das BVH-Skelett unsichtbar und Abspielen
 *      gesperrt (Knopf, Leertaste). Wer Play drückt, sieht dann von Anfang
 *      an das richtige Rig, oben und unten zugleich.
 *
 * Bleibt das Rig aus (Figur nicht auf der Seite, Abruf gescheitert), gibt
 * `FRIST_MS` das Abspielen frei und das Fenster zeigt das BVH-Skelett — mit
 * Meldung in der Konsole, nie stumm gesperrt.
 */
import * as THREE from 'three';
import { Humanbodyrig } from './humanbodyrig.js';
import { Klipquelle } from '../../viewer/gemeinsam/klipquelle.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';

export class Rigstart {
    /** Länger wartet niemand auf das Rig — danach spielt das BVH-Skelett. */
    static FRIST_MS = 20000;

    constructor(spieler) {
        this.spieler = spieler;
        /** @type {Promise<Humanbodyrig|null>|null} */
        this.ladung = null;
        /** Gestartet und noch nicht da (oder gescheitert). */
        this.ausstehend = false;
        /** Am BVH-Skelett angelegt — genau einmal, `anlegen` verschiebt kumulativ. */
        this.angelegt = false;
    }

    /** Beim Seitenstart rufen — parallel zur BVH-Datei. */
    beginnen() {
        if (this.ladung || !this.spieler.jobId) return this.ladung;
        this.ausstehend = true;
        this.spieler.bedienung.bereitschaft(false);
        const beginn = performance.now();
        this.ladung = Humanbodyrig.laden(this.spieler.szene, this.spieler.jobId,
                                         Klipquelle.holen())
            .then((rig) => {
                Klipquelle.beiWechsel(klip => rig.klipUebernehmen(klip));
                Protokoll.debug('bvh_player', 'HumanBody-Rig da nach',
                                Math.round(performance.now() - beginn), 'ms');
                return rig;
            })
            .catch((fehler) => {
                console.error('[bvh_player] HumanBody-Rig nicht geladen:', fehler);
                return null;
            })
            .finally(() => this._freigeben());
        setTimeout(() => {
            if (!this.ausstehend) return;
            Protokoll.warnung('bvh_player', 'HumanBody-Rig nach',
                              Rigstart.FRIST_MS, 'ms nicht da — BVH-Skelett');
            this._freigeben();
        }, Rigstart.FRIST_MS);
        return this.ladung;
    }

    _freigeben() {
        this.ausstehend = false;
        this.spieler.bedienung.bereitschaft(true);
    }

    /** Das fertige Rig (oder null), an das BVH-Skelett angelegt. */
    async rig() {
        const rig = await (this.ladung || this.beginnen());
        const wurzel = this.spieler.skelett.wurzel;
        if (rig && wurzel && !this.angelegt) {
            this.spieler.skelett.zeitSetzen(0);
            rig.anlegen(wurzel.getWorldPosition(new THREE.Vector3()));
            this.angelegt = true;
        }
        return rig;
    }
}
