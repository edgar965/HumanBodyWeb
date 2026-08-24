/**
 * Bedienleiste — Menüleiste, Reiter und Werkzeugknöpfe der Theatre-Seite.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026): 138 Zeilen Verdrahtung, in
 * denen sich zwei Muster wiederholten —
 *
 *   * `document.querySelectorAll('.menu-item').forEach(mi =>
 *      mi.classList.remove('active'))` stand FÜNFMAL in der Datei (zweimal
 *     hier, dreimal in den Kamera-Menüs, siehe Kamerabahn),
 *   * drei Umschaltknöpfe (Lichter, Modell, Kleidung) bestanden aus demselben
 *     Ablauf: Zustand kippen, Sichtbarkeit setzen, Knopfklasse nachziehen —
 *     jeweils mit eigener Closure-Variable.
 */
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';
export class Bedienleiste {

    /**
     * @param {Object} buehne  { scene, lightIcons, transformControls }
     * @param {Object} vorgaben  { PRESETS, applyPreset, camera, lights, controls }
     */
    constructor(buehne, vorgaben) {
        this.buehne = buehne;
        this.vorgaben = vorgaben;
        this.sichtbar = { lichter: true, modell: true, kleidung: true };
    }

    verdrahten() {
        this.menueleiste();
        this.vorgabeknoepfe();
        this.reiter();
        this.werkzeuge();
        return this;
    }

    /** Alle geöffneten Menüs zuklappen. Stand fuenfmal ausgeschrieben da. */
    static menuesZuklappen() {
        document.querySelectorAll('.menu-item')
            .forEach(punkt => punkt.classList.remove('active'));
    }

    menueleiste() {
        document.querySelectorAll('.menu-item').forEach(punkt => {
            const klappe = punkt.querySelector('.menu-dropdown');
            if (!klappe) return;            // z. B. "Hilfe" ohne Untermenue
            punkt.addEventListener('click', ereignis => {
                ereignis.stopPropagation();
                const offen = punkt.classList.contains('active');
                Bedienleiste.menuesZuklappen();
                punkt.classList.toggle('active', !offen);
            });
            // Klick INS Menü darf es nicht schliessen.
            klappe.addEventListener('click', e => e.stopPropagation());
        });
        // Klick daneben schliesst alles.
        document.addEventListener('click', () => Bedienleiste.menuesZuklappen());
    }

    /** Licht-/Kamera-Vorgaben aus presets.js. */
    vorgabeknoepfe() {
        const { PRESETS, applyPreset, camera, lights, controls } = this.vorgaben;
        document.querySelectorAll('[data-preset]').forEach(knopf => {
            knopf.addEventListener('click', () => {
                const name = knopf.getAttribute('data-preset');
                const vorgabe = PRESETS[name];
                if (!vorgabe) {
                    console.error('Vorgabe nicht gefunden:', name);
                    return;
                }
                applyPreset(vorgabe, camera, lights, controls);
                Protokoll.debug('bedienleiste', '✓ Vorgabe angewendet:', vorgabe.name);
                Bedienleiste.menuesZuklappen();
            });
        });
    }

    reiter() {
        document.querySelectorAll('.panel-tab').forEach(reiter => {
            reiter.addEventListener('click', () => {
                document.querySelectorAll('.panel-tab')
                    .forEach(r => r.classList.remove('active'));
                document.querySelectorAll('.tab-pane')
                    .forEach(f => f.classList.remove('active'));
                reiter.classList.add('active');
                document.getElementById(reiter.getAttribute('data-tab'))
                    ?.classList.add('active');
            });
        });
    }

    werkzeuge() {
        this._modus('btn-translate-mode', 'translate', 'btn-rotate-mode');
        this._modus('btn-rotate-mode', 'rotate', 'btn-translate-mode');
        this._umschalter('btn-toggle-lights', 'lichter',
                         an => Object.values(this.buehne.lightIcons)
                                     .forEach(symbol => { symbol.visible = an; }));
        this._umschalter('btn-toggle-model', 'modell',
                         an => this._netzeSetzen(an, netz => !netz.userData.isGarment
                                                          && !netz.userData.isHair
                                                          && !netz.userData.isRig));
        this._umschalter('btn-toggle-clothes', 'kleidung',
                         an => this._netzeSetzen(an, netz => netz.userData.isGarment
                                                          || netz.userData.isHair));
    }

    /** Verschieben/Drehen — der jeweils andere Knopf verliert die Markierung. */
    _modus(id, modus, andererId) {
        const knopf = document.getElementById(id);
        if (!knopf) return;
        knopf.addEventListener('click', () => {
            this.buehne.transformControls.setMode(modus);
            knopf.classList.add('active');
            document.getElementById(andererId)?.classList.remove('active');
        });
    }

    /**
     * Ein Umschaltknopf: Zustand kippen, Wirkung ausfuehren, Knopf nachziehen.
     * Ersetzt drei gleich gebaute Bloecke mit je eigener Closure-Variable.
     */
    _umschalter(id, name, wirken) {
        const knopf = document.getElementById(id);
        if (!knopf) return;
        knopf.addEventListener('click', () => {
            this.sichtbar[name] = !this.sichtbar[name];
            wirken(this.sichtbar[name]);
            knopf.classList.toggle('active', this.sichtbar[name]);
        });
    }

    _netzeSetzen(sichtbar, gilt) {
        this.buehne.scene.traverse(objekt => {
            if (objekt.isMesh && gilt(objekt)) objekt.visible = sichtbar;
        });
    }
}
