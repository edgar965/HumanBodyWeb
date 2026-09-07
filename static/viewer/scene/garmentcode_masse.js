import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * GarmentcodeMasse — die Maßliste des Reiters.
 *
 * Herausgelöst am 07.09.2026, als `garmentcode.js` beim Einbau des
 * 2D-Knopfes über ihre 290 Zeilen gewachsen wäre
 * (`~/.claude/rules/struktur.md`: Eine Datei wird beim Anfassen nicht
 * größer, als sie war). Die Maße sind der geschlossenste Block darin und
 * haben mit dem Bauen nichts zu tun.
 *
 * DAS ZEICHEN VOR DEM NAMEN IST DER BEFUND, NICHT ZIERDE: `•` heißt am
 * Netz GEMESSEN, `°` heißt aus der Vorlage übernommen oder von der
 * Bändigung begrenzt. Am 06.09.2026 stand `bust` roh bei 44,5 cm und wurde
 * still auf 73,8 gehoben — der Schnitt bekam ein zu schmales Vorderteil,
 * und niemand konnte es der Zahl ansehen.
 */
export class GarmentcodeMasse {

    /** Die Maße der gewählten Figur holen und auflisten. */
    static async laden(reiter) {
        const figur = reiter.figur();
        const liste = document.getElementById('gc-masse-liste');
        if (!figur || !liste) return;
        liste.innerHTML = '<div class="hb-hinweis">Figur wird vermessen …</div>';
        try {
            const antwort = await Serverabruf.formular(
                '/api/garmentcode/masse/', reiter.figurdaten(figur));
            reiter.masseFuer = figur.id;
            liste.innerHTML = '';
            for (const [name, wert] of Object.entries(antwort.masse)) {
                liste.appendChild(GarmentcodeMasse.zeile(
                    name, wert, antwort.herkunft[name]));
            }
        } catch (fehler) {
            liste.innerHTML = '<div class="hb-hinweis">Nicht abrufbar: '
                + `${fehler.message || fehler}</div>`;
        }
    }

    static zeile(name, wert, herkunft) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const woher = herkunft === 'gemessen' ? '•' : '°';
        zeile.innerHTML = `<label>${woher} ${name}</label>`
            + `<span class="slider-val">${wert}</span>`;
        return zeile;
    }
}
