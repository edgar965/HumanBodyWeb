/**
 * Ordnerwahl — das Fenster „Verschieben nach …": vorhandene Ordner zur Auswahl,
 * daneben ein neuer Name.
 *
 * Herausgelöst aus `Animationsmenue` (17.10.2026), als der Reiter „Posen" dasselbe
 * Fenster brauchte (Edgar: „Funktionen zum Verschieben … so wie bei Animationen").
 * Zwei Fassungen desselben Fensters wären die Fehlerklasse „DIESELBEN LISTEN,
 * ZWEIMAL".
 *
 * WARUM KEIN `prompt` (Edgar, 08.09.2026, Animationen): Die Ordner heißen
 * `Bandai 1`, `MixamoDance`, `Bondai Dance` — wer den Namen tippt, tippt ihn
 * falsch, und der Server legt dann stillschweigend einen zweiten Ordner an.
 *
 * Kein `<dialog>`: Die Seite läuft mit einem eigenen Fensterstil, und ein modales
 * `dialog` legt sich über die Szene, während man noch sehen will, welche Figur
 * gewählt ist.
 *
 * `data-reihenfolge="fest"`: Die Ordner kommen schon in Baumreihenfolge; ohne die
 * Marke sortierte `Combosortierung` „Neuer Ordner …" alphabetisch zwischen sie
 * (gesehen 17.10.2026 im Chrome: zwischen „Kin …" und „Space …").
 */
export class Ordnerwahl {

    static NEU = '__neu__';

    /**
     * @param titel   Zeile über der Auswahl („„x" liegt in „y"") — als TEXT gesetzt
     * @param ordner  `[{wert, text, aktuell}]` — der aktuelle ist nicht wählbar
     * @param wahl    `{knopf, neuHinweis}` — Beschriftung des Knopfs, Platzhalter des Felds
     * @returns Promise mit dem gewählten Wert, dem neuen Namen oder `null`
     */
    static waehlen(titel, ordner, { knopf = 'Verschieben', neuHinweis = 'Name des neuen Ordners' } = {}) {
        return new Promise((fertig) => {
            const hinter = document.createElement('div');
            // Die Klassen der Seite, nicht eigene: `.scene-modal-overlay` und
            // `.scene-modal` sind in `scene_config.html` gestaltet. Ein eigener
            // Kasten hätte kein Aussehen — weißer Text auf weißem Grund.
            hinter.className = 'scene-modal-overlay visible';
            hinter.innerHTML = `
                <div class="scene-modal">
                  <div class="scene-modal-header">
                    <h4><i class="fas fa-arrows-alt"></i> <span data-knopftitel></span></h4>
                    <button class="scene-modal-close" data-ab>&times;</button>
                  </div>
                  <div class="scene-modal-body">
                    <div class="dialoghinweis" data-titel></div>
                    <select class="viewer-select hb-dehnt-ohne-abstand" data-liste data-reihenfolge="fest"></select>
                    <input class="scene-name-input hb-versteckt" type="text" data-neu>
                  </div>
                  <div class="scene-modal-footer">
                    <button data-ab>Abbrechen</button>
                    <button class="primary" data-ok></button>
                  </div>
                </div>`;
            const nimm = (was) => hinter.querySelector(`[${was}]`);
            // Namen kommen aus Verzeichnissen auf der Platte — als TEXT setzen, nicht als HTML.
            nimm('data-titel').textContent = titel;
            nimm('data-knopftitel').textContent = knopf;
            nimm('data-ok').textContent = knopf;
            const liste = nimm('data-liste');
            const feld = nimm('data-neu');
            feld.placeholder = neuHinweis;
            for (const eintrag of ordner) {
                const option = document.createElement('option');
                option.value = eintrag.wert;
                option.textContent = eintrag.text + (eintrag.aktuell ? ' (aktuell)' : '');
                option.disabled = !!eintrag.aktuell;
                liste.appendChild(option);
            }
            const neuer = document.createElement('option');
            neuer.value = Ordnerwahl.NEU;
            neuer.textContent = 'Neuer Ordner …';
            liste.appendChild(neuer);
            // Ohne wählbaren Ordner steht gleich „Neuer Ordner" da.
            const erster = [...liste.options].find((o) => !o.disabled);
            if (erster) liste.value = erster.value;
            const umschalten = () => {
                feld.classList.toggle('hb-versteckt', liste.value !== Ordnerwahl.NEU);
                if (liste.value === Ordnerwahl.NEU) feld.focus();
            };
            liste.addEventListener('change', umschalten);
            document.body.appendChild(hinter);
            umschalten();
            const schliessen = (wert) => { hinter.remove(); fertig(wert || null); };
            const nehmen = () => schliessen(liste.value === Ordnerwahl.NEU ? feld.value.trim() : liste.value);
            nimm('data-ok').addEventListener('click', nehmen);
            feld.addEventListener('keydown', (ereignis) => { if (ereignis.key === 'Enter') nehmen(); });
            for (const knopfAb of hinter.querySelectorAll('[data-ab]')) {
                knopfAb.addEventListener('click', () => schliessen(null));
            }
            // Ein Klick auf den Hintergrund bricht ab, einer im Kasten nicht.
            hinter.addEventListener('click', (ereignis) => {
                if (ereignis.target === hinter) schliessen(null);
            });
            if (liste.value !== Ordnerwahl.NEU) liste.focus();
        });
    }
}
