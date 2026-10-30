/**
 * Mesh3daitestansicht — die Knöpfe über den Feldern der Testseite (24.10.2026, Edgar: „es fehlen die View Buttons für Kleider an / aus, usw. alle von …/mesh-3D-AI/rainy/“): die Ansichtsarten aus
 * `Mesh3daimaterial.MODI`, „Rig“ und „Kleider“ — dieselben Knöpfe, Texte und derselbe gemerkte Stand wie auf den Jobseiten (`Mesh3daizeile`, `Mesh3daiansichtgedaechtnis`). Kein „Ziel als Geist“ und keine
 * Wahl des Wegs: ein Test hat kein Ziel und nur einen Weg.
 * Die Testseite hält ihre Objekte fertig gehäutet; die Art legt `Mesh3daiansichtart` beim Zeichnen darüber. `beiAenderung(was)` ruft die Seite mit 'modus', 'rig' oder 'kleider'.
 */
import { Mesh3daiansichtgedaechtnis } from './mesh3daiansichtgedaechtnis.js';
import { Mesh3daimaterial } from './mesh3daimaterial.js';

export class Mesh3daitestansicht {
    constructor(wahl, beiAenderung) {
        this.beiAenderung = beiAenderung;
        this.modus = Mesh3daimaterial.VORGABE;
        this.rig = true;
        this.kleider = true;
        this._modusKnoepfe = Mesh3daimaterial.MODI.map(m => this._knopf(m.icon, m.name, `${m.hinweis} Gilt für beide Felder.`, () => this._setzen({ modus: m.schluessel })));
        Mesh3daimaterial.MODI.forEach((m, i) => { this._modusKnoepfe[i].dataset.modus = m.schluessel; });
        wahl?.querySelector('.mesh3dai-ansicht')?.replaceChildren(...this._modusKnoepfe);
        this._rigKnopf = this._knopf('fa-bone', 'Rig', 'Das Rig, das Mesh3D-AI vorhersagt, ein- und ausblenden — über beiden Feldern, in jeder Ansichtsart.', () => this._setzen({ rig: !this.rig }));
        this._kleiderKnopf = this._knopf('fa-tshirt', 'Kleider', 'Die Kleider, Bestandteile und das Haar der Karte darunter in der Ausgabe ein- und ausblenden; die Haut darunter wird wieder gezeigt.',
            () => this._setzen({ kleider: !this.kleider }));
        wahl?.querySelector('.mesh3dai-rigleiste')?.replaceChildren(this._rigKnopf, this._kleiderKnopf);
        // Die Ansichtsart gilt für alle Zeilen (28.10.2026): ein Klick in der ersten Zeile („ohne KI“, eigene Knöpfe) stellt auch diese um.
        document.addEventListener(Mesh3daiansichtgedaechtnis.EREIGNIS, e => {
            const modus = e.detail?.modus;
            if (!modus || modus === this.modus) return;
            this.modus = modus;
            this._anzeigen();
            this.beiAenderung?.('modus');
        });
        this._anzeigen();
    }

    _knopf(icon, text, titel, klick) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'schaltknopf';
        knopf.title = titel;
        knopf.innerHTML = `<i class="fas ${icon}"></i> `;
        knopf.append(text);
        knopf.addEventListener('click', klick);
        return knopf;
    }

    /** Der gemerkte Stand (alle Mesh3D-AI-Seiten teilen ihn), ohne zu zeichnen; eine Art, die es nicht mehr gibt, bleibt bei der Vorgabe. */
    gemerktSetzen(stand) {
        if (Mesh3daimaterial.MODI.some(m => m.schluessel === stand?.modus)) this.modus = stand.modus;
        if (typeof stand?.rig === 'boolean') this.rig = stand.rig;
        if (typeof stand?.kleider === 'boolean') this.kleider = stand.kleider;
        this._anzeigen();
    }

    _setzen(neu) {
        Object.assign(this, neu);           // vor `merken`: dessen Ereignis erreicht auch diese Ansicht, die dann nichts mehr zu tun hat
        Mesh3daiansichtgedaechtnis.merken(neu);
        this._anzeigen();
        this.beiAenderung?.(Object.keys(neu)[0]);
    }

    _anzeigen() {
        for (const k of this._modusKnoepfe) k.classList.toggle('active', k.dataset.modus === this.modus);
        for (const [knopf, an] of [[this._rigKnopf, this.rig], [this._kleiderKnopf, this.kleider]]) {
            knopf.classList.toggle('active', an);
            knopf.setAttribute('aria-pressed', String(an));
        }
    }
}
