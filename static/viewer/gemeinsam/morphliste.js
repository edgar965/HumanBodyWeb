/**
 * Morphliste — die Kategorienliste mit Schiebereglern für Morph-Werte.
 *
 * Umbau 16.08.2026: Diese Liste wurde an FÜNF Stellen von Hand gebaut, jedes
 * Mal mit denselben CSS-Klassen (`morph-category`, `morph-category-header`,
 * `morph-category-body`, `slider-row`, `slider-val`) und derselben Gliederung
 * "Kategorien alphabetisch, Kopfzeile mit Anzahl, Klick klappt auf":
 * viewer/morphs.js, photo_to_3d/humanbody_morphs.js, scene/properties.js,
 * vergleich/vergleichsregler.js und result_character/morphregler.js
 * (dort mit `rc-`-Präfix).
 *
 * Die Unterschiede zwischen den fünf Stellen waren nur: woher der Startwert
 * kommt und was beim Schieben passiert. Genau das sind hier die Rückrufe.
 */
export class Morphliste {

    static VON = -100;
    static BIS = 100;
    static SCHRITT = 1;

    /**
     * @param wahl.praefix   CSS-Präfix ('' oder 'rc-')
     * @param wahl.startwert (morphname) => Bruch -1..1, Vorgabe 0
     * @param wahl.geaendert (morphname, bruch) => void
     * @param wahl.ereignis  'input' (sofort) oder 'change' (erst beim
     *                       Loslassen — für Seiten, die dabei das Netz neu
     *                       laden; die Anzeige läuft trotzdem mit)
     * @param wahl.chevron   Pfeil vor dem Kategorienamen
     */
    constructor(wahl = {}) {
        this.praefix = wahl.praefix || '';
        this.startwert = wahl.startwert || (() => 0);
        this.geaendert = wahl.geaendert || (() => {});
        this.ereignis = wahl.ereignis || 'input';
        this.chevron = !!wahl.chevron;
    }

    /** Kategorien in den Behälter bauen. Vorhandenes wird ersetzt. */
    bauen(behaelter, morphs, kategorien) {
        behaelter.innerHTML = '';
        for (const [name, liste] of Morphliste.nachKategorie(morphs, kategorien)) {
            behaelter.appendChild(this.kategorie(name, liste));
        }
        return behaelter;
    }

    /**
     * Morphs nach Kategorie ordnen: Kategorien alphabetisch, leere ausgelassen.
     * Statisch, weil die Zuordnung auch ohne Bedienelemente gebraucht wird.
     */
    static nachKategorie(morphs, kategorien) {
        const nach = new Map();
        for (const morph of morphs || []) {
            if (!nach.has(morph.category)) nach.set(morph.category, []);
            nach.get(morph.category).push(morph);
        }
        const namen = kategorien?.length ? kategorien.slice().sort()
                                         : [...nach.keys()].sort();
        return namen.map(name => [name, nach.get(name)])
                    .filter(([, liste]) => liste?.length);
    }

    kategorie(name, morphs) {
        const block = document.createElement('div');
        block.className = this.praefix + 'morph-category';
        const kopf = document.createElement('div');
        kopf.className = this.praefix + 'morph-category-header';
        const beschriftung = `${name} (${morphs.length})`;
        if (this.chevron) {
            kopf.innerHTML = '<span class="cat-chevron">&#9654;</span> ';
            kopf.append(beschriftung);
        } else {
            kopf.textContent = beschriftung;
        }
        kopf.addEventListener('click', () => block.classList.toggle('open'));
        const inhalt = document.createElement('div');
        inhalt.className = this.praefix + 'morph-category-body';
        for (const morph of morphs) inhalt.appendChild(this.zeile(morph));
        block.append(kopf, inhalt);
        return block;
    }

    zeile(morph) {
        const zeile = document.createElement('div');
        zeile.className = this.praefix + 'slider-row';

        const text = document.createElement('label');
        // Der Name trägt vorn seine Kategorie ("nose_..."); die steht schon in
        // der Kopfzeile des Blocks.
        text.textContent = morph.name.split('_').slice(1).join(' ') || morph.name;
        text.title = morph.name;

        const regler = document.createElement('input');
        Object.assign(regler, { type: 'range', min: Morphliste.VON,
                                max: Morphliste.BIS, step: Morphliste.SCHRITT });
        regler.dataset.morph = morph.name;
        regler.value = Math.round((this.startwert(morph.name) || 0) * 100);

        const anzeige = document.createElement('span');
        anzeige.className = this.praefix + 'slider-val';
        anzeige.textContent = regler.value;

        // Die Anzeige läuft immer mit; gemeldet wird je nach `ereignis` sofort
        // oder erst beim Loslassen — Seiten, die dabei das Netz neu holen,
        // wollen nicht bei jedem Pixel eine Anfrage stellen.
        regler.addEventListener('input', () => {
            anzeige.textContent = regler.value;
        });
        regler.addEventListener(this.ereignis, () => {
            this.geaendert(morph.name, parseInt(regler.value, 10) / 100);
        });

        zeile.append(text, regler, anzeige);
        return zeile;
    }

    /**
     * Alle Regler im Behälter auf 0 — mit Anzeige. Stand an vier Stellen als
     * `querySelectorAll(...).forEach(s => { s.value = 0; s.nextElementSibling…`.
     */
    static zuruecksetzen(behaelter, jeMorph = null) {
        for (const regler of behaelter.querySelectorAll('input[type="range"]')) {
            regler.value = 0;
            if (regler.nextElementSibling) {
                regler.nextElementSibling.textContent = '0';
            }
            if (jeMorph && regler.dataset.morph) jeMorph(regler.dataset.morph);
        }
    }
}
