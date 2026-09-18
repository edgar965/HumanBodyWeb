/**
 * Bildauswahl — eine Auswahl mit Bild je Eintrag.
 *
 * Edgar (18.09.2026): „bei den Assets bitte auch in der Combo box die
 * Farben / icons in der richtigen Farbe". Ein natives `<select>` zeigt keine
 * Bilder — Chrome malt seine Liste selbst, `<option>` nimmt keinen Inhalt
 * außer Text. Deshalb ein Knopf (Bild + Name, Pfeil) und darunter eine
 * aufklappbare Liste, in der jede Variante mit Daz' Vorschaubild steht
 * (`garderobe/<kennung>/vorschau/?variante=…`, das PNG neben der `.duf`).
 *
 * Nach außen wie ein `<select>`: `.value` (lesen und setzen), `.disabled`,
 * Ereignis `change` beim Wählen — `Genesis9garderobe.werte` liest weiter
 * `wahl.value`. Bilder werden erst geladen, wenn die Liste zum ersten Mal
 * aufgeht (34 Varianten beim Eirgrid-Haar; zu sind sie nur Text).
 *
 * Gebaut über `createElement`, nicht `innerHTML` — so läuft der Test
 * (`test_js_bildauswahl`) mit einer kleinen DOM-Attrappe in Node.
 */
export class Bildauswahl {

    static KLASSE = 'bildauswahl';

    /**
     * @param {Array<{id: string, name: string}>} eintraege die Wahlmöglichkeiten
     * @param {string} vorgabe die anfangs gewählte `id`
     * @param {(eintrag) => string|null} bild Bildadresse je Eintrag, null = ohne Bild
     * @returns {HTMLElement} das Auswahlfeld
     */
    static bauen(eintraege, vorgabe, bild) {
        const feld = Bildauswahl._element('div', Bildauswahl.KLASSE);
        const knopf = Bildauswahl._element('button', 'bildauswahl-knopf');
        knopf.type = 'button';
        knopf.appendChild(Bildauswahl._element('img', 'bildauswahl-bild'));
        knopf.appendChild(Bildauswahl._element('span', 'bildauswahl-name'));
        const pfeil = Bildauswahl._element('span', 'bildauswahl-pfeil');
        pfeil.textContent = '▾';
        knopf.appendChild(pfeil);
        const liste = Bildauswahl._element('ul', 'bildauswahl-liste hb-versteckt');
        liste.setAttribute('role', 'listbox');
        feld.appendChild(knopf);
        feld.appendChild(liste);
        const stand = { wert: '', geladen: false, eintraege, bild };
        for (const eintrag of eintraege) {
            const zeile = Bildauswahl._element('li', '');
            zeile.dataset.id = eintrag.id;
            zeile.setAttribute('role', 'option');
            const img = Bildauswahl._element('img', 'bildauswahl-bild');
            const adresse = bild?.(eintrag) || null;
            if (adresse) img.dataset.adresse = adresse;
            else img.classList.add('hb-versteckt');
            const name = Bildauswahl._element('span', 'bildauswahl-name');
            name.textContent = eintrag.name;
            zeile.appendChild(img);
            zeile.appendChild(name);
            zeile.addEventListener('click', () => {
                Bildauswahl._setzen(feld, stand, eintrag.id);
                Bildauswahl._zu(feld);
                feld.dispatchEvent(new Event('change', { bubbles: true }));
            });
            liste.appendChild(zeile);
        }
        knopf.addEventListener('click', () => {
            if (feld.disabled) return;
            if (liste.classList.contains('hb-versteckt')) Bildauswahl._auf(feld, stand);
            else Bildauswahl._zu(feld);
        });
        feld.addEventListener('keydown', (e) => { if (e.key === 'Escape') Bildauswahl._zu(feld); });
        Object.defineProperty(feld, 'value', {
            get: () => stand.wert,
            set: (wert) => Bildauswahl._setzen(feld, stand, wert),
        });
        Object.defineProperty(feld, 'disabled', {
            get: () => knopf.disabled,
            set: (aus) => { knopf.disabled = Boolean(aus); feld.classList.toggle('gedaempft', Boolean(aus)); },
        });
        feld.value = vorgabe;
        return feld;
    }

    static _element(tag, klassen) {
        const e = document.createElement(tag);
        if (klassen) e.className = klassen;
        return e;
    }

    static _setzen(feld, stand, wert) {
        const eintrag = stand.eintraege.find(e => e.id === wert) || stand.eintraege[0];
        stand.wert = eintrag?.id ?? '';
        const knopf = feld.querySelector('.bildauswahl-knopf');
        knopf.querySelector('.bildauswahl-name').textContent = eintrag?.name ?? '';
        const adresse = eintrag ? stand.bild?.(eintrag) : null;
        const img = knopf.querySelector('.bildauswahl-bild');
        img.classList.toggle('hb-versteckt', !adresse);
        if (adresse && img.getAttribute('src') !== adresse) img.setAttribute('src', adresse);
        feld.querySelectorAll('li').forEach(li => li.classList.toggle('gewaehlt', li.dataset.id === stand.wert));
    }

    static _auf(feld, stand) {
        const liste = feld.querySelector('.bildauswahl-liste');
        if (!stand.geladen) {
            // Erst jetzt die Bilder holen — zu bleibt die Liste ohne Anfragen.
            liste.querySelectorAll('img[data-adresse]').forEach(img => { img.setAttribute('src', img.dataset.adresse); });
            stand.geladen = true;
        }
        // Fest am Bildschirm platziert (`position: fixed`), nicht in der Zeile:
        // der Assets-Baum rollt (`overflow: auto`) und schnitte eine absolut
        // gesetzte Liste an seinem Rand ab.
        const r = feld.querySelector('.bildauswahl-knopf').getBoundingClientRect();
        liste.style.left = `${r.left}px`;
        liste.style.top = `${r.bottom + 2}px`;
        liste.style.width = `${Math.max(r.width, 180)}px`;
        liste.classList.remove('hb-versteckt');
        feld.classList.add('offen');
        const draussen = (e) => { if (!feld.contains(e.target)) Bildauswahl._zu(feld); };
        // Rollen in der Liste selbst schließt sie nicht — nur Rollen drumherum.
        const weg = (e) => { if (!(e?.target && liste.contains(e.target))) Bildauswahl._zu(feld); };
        feld._hoerer = { draussen, weg };
        document.addEventListener('mousedown', draussen);
        window.addEventListener('scroll', weg, true);
        window.addEventListener('resize', weg);
    }

    static _zu(feld) {
        feld.querySelector('.bildauswahl-liste').classList.add('hb-versteckt');
        feld.classList.remove('offen');
        const h = feld._hoerer;
        if (!h) return;
        feld._hoerer = null;
        document.removeEventListener('mousedown', h.draussen);
        window.removeEventListener('scroll', h.weg, true);
        window.removeEventListener('resize', h.weg);
    }
}
