/**
 * Meshgenesistestansicht — die Knöpfe über den Feldern der Testseite (24.10.2026, Edgar: „es fehlen die View Buttons für Kleider an / aus, usw. alle von …/mesh-3D-AI/rainy/“): die Ansichtsarten aus
 * `Meshgenesismaterial.MODI`, „Rig“ und „Kleider“ — dieselben Knöpfe, Texte und derselbe gemerkte Stand wie auf den Jobseiten (`Meshgenesiszeile`, `Meshgenesisansichtgedaechtnis`). Kein „Ziel als Geist“ und keine
 * Wahl des Wegs: ein Test hat kein Ziel und nur einen Weg.
 * Die Testseite hält ihre Objekte fertig gehäutet; die Art legt `Meshgenesisansichtart` beim Zeichnen darüber. `beiAenderung(was)` ruft die Seite mit 'modus', 'rig', 'kleider' oder 'ohneGlieder'.
 */
import { Meshgenesisansichtgedaechtnis } from './meshgenesisansichtgedaechtnis.js';
import { Meshgenesismaterial } from './meshgenesismaterial.js';

export class Meshgenesistestansicht {
    constructor(wahl, beiAenderung) {
        this.beiAenderung = beiAenderung;
        this.modus = Meshgenesismaterial.VORGABE;
        this.rig = true;
        this.kleider = true;
        this._modusKnoepfe = Meshgenesismaterial.MODI.map(m => this._knopf(m.icon, m.name, `${m.hinweis} Gilt für beide Felder.`, () => this._setzen({ modus: m.schluessel })));
        Meshgenesismaterial.MODI.forEach((m, i) => { this._modusKnoepfe[i].dataset.modus = m.schluessel; });
        wahl?.querySelector('.meshgenesis-ansicht')?.replaceChildren(...this._modusKnoepfe);
        this._rigKnopf = this._knopf('fa-bone', 'Rig', 'Das Rig, das Mesh-Genesis vorhersagt, ein- und ausblenden — über beiden Feldern, in jeder Ansichtsart.', () => this._setzen({ rig: !this.rig }));
        this._kleiderKnopf = this._knopf('fa-tshirt', 'Kleider', 'Die Kleider, Bestandteile und das Haar der Karte darunter in der Ausgabe ein- und ausblenden; die Haut darunter wird wieder gezeigt.',
            () => this._setzen({ kleider: !this.kleider }));
        // 31.10.2026, Edgar (mann_gold): „bei dem Modell sind die Beine und Arme nicht vorhanden im Mesh. Kannst du eine Option machen, so dass die beim Ergebnis nicht angezeigt werden?“
        this.ohneGlieder = false;
        this._ohneKnopf = this._knopf('fa-user-slash', 'Ohne fehlende Glieder', 'Die Haut der Glieder, die das Netz des Eingangs nicht hat (Schritt „Kleider“: mehr als die Hälfte '
            + 'eines Knochens liegt weiter als 4 cm vom Eingang, z. B. Arme in einer geschlossenen Kugel), in der Ausgabe ausblenden — im Stand und im Tanz.', () => this._setzen({ ohneGlieder: !this.ohneGlieder }));
        wahl?.querySelector('.meshgenesis-rigleiste')?.replaceChildren(this._rigKnopf, this._kleiderKnopf, this._ohneKnopf);
        // Die Ansichtsart gilt für alle Zeilen (28.10.2026): ein Klick in der ersten Zeile („ohne KI“, eigene Knöpfe) stellt auch diese um.
        document.addEventListener(Meshgenesisansichtgedaechtnis.EREIGNIS, e => {
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

    /** Der gemerkte Stand (alle Mesh-Genesis-Seiten teilen ihn), ohne zu zeichnen; eine Art, die es nicht mehr gibt, bleibt bei der Vorgabe. */
    gemerktSetzen(stand) {
        if (Meshgenesismaterial.MODI.some(m => m.schluessel === stand?.modus)) this.modus = stand.modus;
        if (typeof stand?.rig === 'boolean') this.rig = stand.rig;
        if (typeof stand?.kleider === 'boolean') this.kleider = stand.kleider;
        if (typeof stand?.ohneGlieder === 'boolean') this.ohneGlieder = stand.ohneGlieder;
        this._anzeigen();
    }

    _setzen(neu) {
        Object.assign(this, neu);           // vor `merken`: dessen Ereignis erreicht auch diese Ansicht, die dann nichts mehr zu tun hat
        Meshgenesisansichtgedaechtnis.merken(neu);
        this._anzeigen();
        this.beiAenderung?.(Object.keys(neu)[0]);
    }

    _anzeigen() {
        for (const k of this._modusKnoepfe) k.classList.toggle('active', k.dataset.modus === this.modus);
        for (const [knopf, an] of [[this._rigKnopf, this.rig], [this._kleiderKnopf, this.kleider], [this._ohneKnopf, this.ohneGlieder]]) {
            knopf.classList.toggle('active', an);
            knopf.setAttribute('aria-pressed', String(an));
        }
    }
}
