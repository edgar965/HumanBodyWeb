import { escapeHtml } from '../utils.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Bildnachlader } from '../../gemeinsam/bildnachlader.js';
import { Kategoriekasten } from '../../gemeinsam/kategoriekasten.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/**
 * Mhkatalogliste — die 181 MakeHuman-Stücke, nach Kategorie aufklappbar.
 *
 * Ein Klick zieht an, ein zweiter aus. Es gibt keinen „Anpassen"-Knopf und
 * keine Fit-Regler: Auf dem Körper, für den ein Stück entworfen wurde, ist der
 * Sitz durch die `.mhclo` festgelegt (siehe `mhkleidstueck.js`).
 *
 * VORSCHAUBILDER ERST BEIM AUFKLAPPEN (`Bildnachlader`): Alle auf einmal wären
 * auf dieser Seite schon einmal 125 Bilder mit 4,77 MB beim Start gewesen —
 * gemessen am 17.08.2026, siehe den Kopf des Nachladers. Die Bilder brauchen
 * dafür eine feste Größe aus CSS; die haben sie über `.garment-thumb`.
 */
export class Mhkatalogliste {

    static ADRESSE = '/api/character/mh-figur/garderobe/';
    static _bestand = null;

    /** Der Bestand — einmal je Seite geholt. */
    static async bestand() {
        if (!Mhkatalogliste._bestand) {
            Mhkatalogliste._bestand =
                await Serverabruf.json(Mhkatalogliste.ADRESSE);
        }
        return Mhkatalogliste._bestand;
    }

    /**
     * @param inst          die MakeHuman-Figur
     * @param behaelter     Zielelement
     * @param nachAenderung () => void, nach Anziehen oder Ausziehen
     */
    static async fuellen(inst, behaelter, nachAenderung) {
        if (!behaelter) return;
        behaelter.innerHTML =
            '<div class="hb-hinweis"><i class="fas fa-spinner fa-spin"></i>'
            + ' Lade Garderobe …</div>';
        let daten;
        try {
            daten = await Mhkatalogliste.bestand();
        } catch (fehler) {
            behaelter.innerHTML = '<div class="fehlertext">Garderobe nicht '
                + `abrufbar: ${escapeHtml(fehler.message)}</div>`;
            return;
        }
        behaelter.innerHTML = '';
        const nach = new Map();
        for (const stueck of daten.stuecke || []) {
            if (!nach.has(stueck.kategoriename)) {
                nach.set(stueck.kategoriename, []);
            }
            nach.get(stueck.kategoriename).push(stueck);
        }
        if (!nach.size) {
            behaelter.innerHTML =
                '<div class="hb-hinweis">Keine MakeHuman-Stücke gefunden.</div>';
            return;
        }
        for (const [kategorie, stuecke] of nach) {
            const { kasten, koerper } = Kategoriekasten.bauen(kategorie,
                                                              stuecke.length);
            for (const stueck of stuecke) {
                koerper.appendChild(
                    Mhkatalogliste._zeile(inst, stueck, nachAenderung));
            }
            behaelter.appendChild(kasten);
        }
    }

    static _zeile(inst, stueck, nachAenderung) {
        const zeile = document.createElement('div');
        zeile.className = 'anim-item garment-item';
        zeile.dataset.kennung = stueck.id;
        const getragen = Boolean(inst.kleidung[stueck.id]);
        if (getragen) zeile.classList.add('active');
        if (stueck.vorschau) {
            const bild = document.createElement('img');
            bild.className = 'garment-thumb';
            Bildnachlader.vormerken(
                bild, `/api/character/garment/thumb/${stueck.id}/`);
            zeile.appendChild(bild);
        }
        const name = document.createElement('span');
        name.className = 'garment-name';
        name.textContent = stueck.name;
        name.title = stueck.id;
        zeile.appendChild(name);
        const haken = document.createElement('span');
        haken.className = 'garment-haken';
        haken.innerHTML = getragen ? '<i class="fas fa-check"></i>' : '';
        zeile.appendChild(haken);
        zeile.addEventListener('click', () => Mhkatalogliste._umschalten(
            inst, stueck, zeile, nachAenderung));
        return zeile;
    }

    static async _umschalten(inst, stueck, zeile, nachAenderung) {
        if (zeile.dataset.laeuft === '1') return;
        if (inst.kleidung[stueck.id]) {
            inst.ausziehen(stueck.id);
            nachAenderung();
            return;
        }
        zeile.dataset.laeuft = '1';
        zeile.classList.add('gedaempft');
        try {
            await inst.anziehen(stueck.id);
        } catch (fehler) {
            Protokoll.fehler('MhKleid', `${stueck.id} nicht ladbar`, fehler);
            alert(`Kleidungsstück nicht ladbar: ${fehler.message}`);
        } finally {
            zeile.dataset.laeuft = '0';
            zeile.classList.remove('gedaempft');
        }
        nachAenderung();
    }
}
