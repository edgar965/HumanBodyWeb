import { markDirty } from '../undo.js';
import { Stoffarten } from '../../gemeinsam/stoffarten.js';
import { Eigenkleidstoff } from '../../gemeinsam/eigenkleidstoff.js';
import { Eigenkleidwerte } from '../../gemeinsam/eigenkleidwerte.js';
import { Eigenkleider } from '../../gemeinsam/eigenkleider.js';
import { Stueckstoff } from './stueckstoff.js';
import { Stueckstoffzeilen } from './stueckstoffzeilen.js';

/**
 * Genesis9eigenkleidstoff — der Block „Stoff“ eines eigenen Stücks (Oberteil, Hose, Socken) mit DENSELBEN Zeilen wie am Daz-Stück (`Stueckstoff`, `Stueckstoffzeilen`:
 * Stoffart, Rauheit, Metall, Glanz, Glanzsaum, Saum weich, Saumfarbe, Relief, Gewebe mit Fäden je cm und Struktur), 25.10.2026 nachts.
 *
 * Unterschied ist nur die Ablage: Die Werte stehen als Zahlen in den Reglern der Figur (`Eigenkleidwerte`, Felder `Eigenkleidstoff.FELDER`, Anteile in Prozent);
 * `ZEILEN` rechnet zwischen der Zeile (0…1 bzw. 0…2 wie am Daz-Stück) und dem Feld um. Ein Zug zeigt sofort (`Eigenkleider.vorschau`: nur Uniforms), erst
 * das Loslassen schreibt den Wert in die Figur (`markDirty`) — wie die übrigen Schieber des Kastens (`Genesis9eigenkleidkasten`). Jedes Eingabefeld trägt
 * `data-eigenkleid="<art>:<feld>"`: Daran sperrt der Kasten die Felder eines abgelegten Stücks, und daran findet die Prüfung im Browser den Schieber.
 */
export class Genesis9eigenkleidstoff {

    /** Zeile → [Feld, Faktor Zeile → Feld, Titel, min, max, Schritt]. */
    static ZEILEN = {
        rauheit: ['rauheit', 100, 'Rauheit', 0, 1, 0.01], metall: ['metall', 100, 'Metall', 0, 1, 0.01], glanz: ['glanz', 100, 'Glanz', 0, 2, 0.05],
        saum: ['glanzsaum', 100, 'Glanzsaum', 0, 1, 0.05], saumstreuung: ['glanzsaum_weich', 100, 'Saum weich', 0, 1, 0.05],
        relief: ['relief', 100, 'Relief', 0, 2, 0.05],
    };
    /** Felder, die dieser Block führt — der Kasten baut für sie keine eigenen Schieber. */
    static FELDER = new Set(['rauheit', ...Eigenkleidstoff.FELDER.map(f => f.feld)]);

    static block(inst, art) {
        const Z = Stueckstoffzeilen, H = Stueckstoff.HILFE, kasten = document.createElement('div');
        kasten.className = 'hb-stueckstoff g9-eigenkleid-stoff';
        kasten.dataset.eigenkleidStoff = art;
        const wert = feld => Eigenkleidwerte.wert(inst, art, feld);
        const arten = [['', '– eigene Werte –'], ...Object.entries(Stoffarten.ARTEN).map(([s, a]) => [s, a.titel])];
        const stoffart = Z.wahl('stoffart', 'Stoffart', arten, Eigenkleidstoff.STOFFARTEN[wert('stoffart')] || '', (name) => {
            Genesis9eigenkleidstoff.setzen(inst, art, name ? Eigenkleidstoff.ausStoffart(name) : { stoffart: 0 });
            if (name) kasten.replaceWith(Genesis9eigenkleidstoff.block(inst, art));        // alle Zeilen auf die neuen Werte
        }, H.stoffart);
        Genesis9eigenkleidstoff._kennung(stoffart.wahl, art, 'stoffart');
        kasten.appendChild(stoffart);
        for (const [zeile, [feld, faktor, titel, min, max, schritt]] of Object.entries(Genesis9eigenkleidstoff.ZEILEN)) {
            if (zeile === 'relief') kasten.appendChild(Genesis9eigenkleidstoff._farbe(inst, art, H.saumfarbe));
            const z = Z.regler(zeile, titel, min, max, schritt, wert(feld) / faktor, w => Eigenkleider.vorschau(inst, art, feld, w * faktor), H[zeile] || '');
            z.regler.addEventListener('change', () => Genesis9eigenkleidstoff.setzen(inst, art, { [feld]: z.wert() * faktor }));
            Genesis9eigenkleidstoff._kennung(z.regler, art, feld);
            kasten.appendChild(z);
        }
        kasten.appendChild(Genesis9eigenkleidstoff._gewebe(inst, art));
        return kasten;
    }

    /** Mehrere Felder auf einmal: anzeigen und in die Figur schreiben. */
    static setzen(inst, art, teil) {
        for (const [feld, w] of Object.entries(teil)) {
            Eigenkleidwerte.setzen(inst, art, feld, w);
            Eigenkleider.vorschau(inst, art, feld, Eigenkleidwerte.wert(inst, art, feld));
        }
        markDirty();
    }

    /** Gesperrt wird nach dem Bau vom Kasten (`Genesis9eigenkleidkasten.stand`) — ein neu gebauter Block (Stoffart) entsteht nur am angelegten Stück. */
    static _kennung(feld, art, name) {
        feld.dataset.eigenkleid = `${art}:${name}`;
    }

    static _farbe(inst, art, hilfe) {
        const z = Stueckstoffzeilen.farbe('saumfarbe', 'Saumfarbe', Eigenkleidstoff.hex(Eigenkleidwerte.wert(inst, art, 'glanzsaum_farbe')),
            hex => Genesis9eigenkleidstoff.setzen(inst, art, { glanzsaum_farbe: hex ? Eigenkleidwerte.ausHex(hex) : -1 }), hilfe);
        for (const feld of z.querySelectorAll('input')) feld.dataset.eigenkleid = `${art}:glanzsaum_farbe`;
        return z;
    }

    /** Gewebe mit Fäden je cm und Struktur (wie `Stueckstoff._gewebe`); „ohne“ = keine Bindung über dem Stoff. */
    static _gewebe(inst, art) {
        const Z = Stueckstoffzeilen, H = Stueckstoff.HILFE, kasten = document.createElement('div');
        const index = Eigenkleidwerte.wert(inst, art, 'gewebe');
        const wahl = Z.wahl('gewebe', 'Gewebe', [['', 'ohne'], ...Stoffarten.gewebewahl()], Eigenkleidstoff.GEWEBE[index] || '', null);
        const faeden = Z.regler('faeden', 'Fäden je cm', 0.5, 40, 0.5, Eigenkleidwerte.wert(inst, art, 'faeden'), w => Eigenkleider.vorschau(inst, art, 'faeden', w), H.faeden);
        const staerke = Z.regler('staerke', 'Struktur', 0, 1, 0.05, Eigenkleidwerte.wert(inst, art, 'struktur') / 100,
            w => Eigenkleider.vorschau(inst, art, 'struktur', w * 100), H.staerke);
        faeden.regler.addEventListener('change', () => Genesis9eigenkleidstoff.setzen(inst, art, { faeden: faeden.wert() }));
        staerke.regler.addEventListener('change', () => Genesis9eigenkleidstoff.setzen(inst, art, { struktur: staerke.wert() * 100 }));
        wahl.wahl.addEventListener('change', () => {
            const i = Math.max(0, Eigenkleidstoff.GEWEBE.indexOf(wahl.wahl.value)), neu = Eigenkleidstoff.gewebevorgabe(i);
            faeden.stellen(neu.faeden);
            staerke.stellen(neu.struktur / 100);
            faeden.hidden = staerke.hidden = !i;
            Genesis9eigenkleidstoff.setzen(inst, art, { gewebe: i, faeden: neu.faeden, struktur: neu.struktur });
        });
        faeden.hidden = staerke.hidden = !index;
        for (const [feld, name] of [[wahl.wahl, 'gewebe'], [faeden.regler, 'faeden'], [staerke.regler, 'struktur']]) feld.dataset.eigenkleid = `${art}:${name}`;
        kasten.append(wahl, faeden, staerke);
        return kasten;
    }
}
