/**
 * Szeneneinstellungen — die gespeicherte Beleuchtung auf eine Szene legen.
 *
 * WARUM DIESES MODUL (Umbau 28.08.2026, Befund `doppelcode`): Dieselben rund
 * 40 Zeilen standen VIERMAL im Projekt und unterschieden sich nur darin, WO
 * die Teile herkamen:
 *
 *     animation/material.js          Lichter als Parameter, Rest aus `Seitenzustand`
 *     result_character/scene_setup   alles als Parameter
 *     viewer/scene_settings.js       alles aus `state`
 *     scene/lighting.js              alles aus `state`, Umgebungslicht heisst
 *                                    dort `ambientLight`, danach zwei UI-Zeilen
 *     scene/session.js               dasselbe aus dem sessionStorage
 *     scene/szenenzustand.js         dasselbe aus einer gespeicherten Szene
 *
 * Die letzten beiden lesen nicht aus dem localStorage, sondern aus einem
 * uebergebenen Objekt — deshalb ist `uebernehmen(werte)` oeffentlich und
 * `anwenden()` nur die Kurzform „nimm, was im localStorage steht".
 *
 * Genau dieses „woher" gehoert an die Aufrufstelle, die Rechnung nicht. Die
 * vierte Fassung war schon auseinandergelaufen: Sie setzt nach dem Laden das
 * Auswahlfeld zurueck, die anderen drei nicht.
 *
 * Die Schluessel im gespeicherten Objekt sind DRAHTFORMAT — sie stehen so im
 * localStorage und in gespeicherten Szenen-JSONs. Wer hier umbenennt, macht
 * gespeicherte Szenen still wirkungslos (siehe `tonwerte.js` daneben).
 */
import { Protokoll } from './protokoll.js';


export class Szeneneinstellungen {

    /** Der localStorage-Schluessel. Drahtformat, nicht umbenennen. */
    static SCHLUESSEL = 'humanbody_scene_settings';

    /**
     * @param teile {keyLight, fillLight, backLight, ambient, renderer, scene,
     *               camera, controls, tonwerte, woher} — jedes Stueck darf
     *               fehlen; was fehlt, wird uebergangen statt zu werfen.
     */
    constructor(teile) {
        this.teile = teile;
        this.woher = teile.woher || 'szeneneinstellungen';
    }

    /** Das gespeicherte Objekt — oder null, wenn nichts (Gueltiges) da ist. */
    static gespeichert() {
        const roh = localStorage.getItem(Szeneneinstellungen.SCHLUESSEL);
        if (!roh) return null;
        try {
            return JSON.parse(roh);
        } catch (e) {
            Protokoll.warnung('szeneneinstellungen',
                              'Failed to load scene settings:', e);
            return null;
        }
    }

    /**
     * Die gespeicherten HAUT-Werte auf ein Material legen.
     *
     * BEFUND `doppelcode` (30.08.2026): `applySceneSkinSettings` stand dreimal
     * — `animation/material.js`, `viewer/scene_settings.js`,
     * `result_character/scene_setup.js`. Gleiche Schluessel, gleiche
     * Reihenfolge, drei Fassungen.
     *
     * DIE HAUTFARBE BLEIBT AUSSEN VOR, und das ist der Punkt: Sie kommt aus
     * `SKIN_COLORS` je Koerpertyp, nicht aus den Szeneneinstellungen. Wer sie
     * hier mitschreibt, ueberschreibt die Hautfarbe der Figur mit der des
     * zuletzt betrachteten Modells — sichtbar, aber nicht als Fehler
     * erkennbar. In einer der drei Fassungen stand das als Kommentar, in den
     * anderen beiden nicht.
     *
     * @param {Object} material Three-Material (oder null)
     * @returns {boolean} true, wenn Werte uebernommen wurden — daran haengt
     *          auf der Viewer-Seite das Nachziehen der Regler
     */
    static hautWerte(material) {
        if (!material) return false;
        const werte = Szeneneinstellungen.gespeichert();
        if (!werte || !werte.skin) return false;
        if (werte.skin.roughness !== undefined) {
            material.roughness = werte.skin.roughness;
        }
        if (werte.skin.metalness !== undefined) {
            material.metalness = werte.skin.metalness;
        }
        return true;
    }

    /** Das erste Material eines Netzes — Netze koennen mehrere tragen. */
    static erstesMaterial(netz) {
        const m = netz && netz.material;
        if (!m) return null;
        return Array.isArray(m) ? m[0] : m;
    }

    /**
     * Anwenden.
     *
     * @returns true, wenn wirklich etwas angewendet wurde. Der Rueckgabewert
     *          ist wichtig: `scene/lighting.js` haengt zwei UI-Schritte daran,
     *          und die sollen — wie bisher — ausbleiben, wenn nichts geladen
     *          wurde oder unterwegs etwas schiefging.
     */
    anwenden() {
        return this.uebernehmen(Szeneneinstellungen.gespeichert());
    }

    /**
     * Diese Werte uebernehmen — aus einer gespeicherten Szene, aus der
     * Sitzung, aus dem localStorage. `null` heisst „nichts da".
     *
     * @returns true, wenn wirklich etwas uebernommen wurde.
     */
    uebernehmen(werte) {
        if (!werte) return false;
        try {
            this._lichter(werte.lighting);
            this._bild(werte.renderer);
            this._kamera(werte.camera);
            return true;
        } catch (e) {
            Protokoll.warnung(this.woher, 'Failed to load scene settings:', e);
            return false;
        }
    }

    _lichter(licht) {
        if (!licht) return;
        for (const name of ['key', 'fill', 'back']) {
            const werte = licht[name];
            const lampe = this.teile[name + 'Light'];
            if (!werte || !lampe) continue;
            lampe.intensity = werte.intensity;
            lampe.color.set(werte.color);
            lampe.position.set(...werte.pos);
        }
        if (licht.ambient && this.teile.ambient) {
            this.teile.ambient.intensity = licht.ambient.intensity;
            this.teile.ambient.color.set(licht.ambient.color);
        }
    }

    _bild(bild) {
        const { renderer, scene, tonwerte } = this.teile;
        if (!bild) return;
        if (renderer) {
            if (bild.toneMapping && tonwerte
                    && tonwerte[bild.toneMapping] !== undefined) {
                renderer.toneMapping = tonwerte[bild.toneMapping];
            }
            if (bild.exposure !== undefined) {
                renderer.toneMappingExposure = bild.exposure;
            }
        }
        if (bild.background && scene) scene.background.set(bild.background);
    }

    /**
     * Sichtfeld, und — wenn die Seite eine Steuerung hat — auch Ort und Ziel.
     *
     * Ort und Ziel stehen nur in gespeicherten Szenen und in der Sitzung; der
     * localStorage-Eintrag fuehrt nur `fov`. Wer keine `controls` uebergibt,
     * bekommt genau das alte Verhalten der drei Betrachter-Seiten.
     */
    _kamera(kamera) {
        const { camera, controls } = this.teile;
        if (!kamera || !camera) return;
        if (kamera.fov) {
            camera.fov = kamera.fov;
            camera.updateProjectionMatrix();
        }
        if (kamera.position) camera.position.fromArray(kamera.position);
        if (!controls) return;
        if (kamera.target) controls.target.fromArray(kamera.target);
        controls.update();
    }
}
