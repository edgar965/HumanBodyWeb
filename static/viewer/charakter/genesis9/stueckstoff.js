import { Dazkleidung } from './dazkleidung.js';
import { Umfaerbung } from '../../gemeinsam/umfaerbung.js';
import { Stoffwerte } from '../../gemeinsam/stoffwerte.js';
import { GEWEBEARTEN, gewebeart } from '../../gemeinsam/gewebearten.js';
import { markDirty } from '../undo.js';

/**
 * Stueckstoff — Rauheit, Metall und Gewebe eines getragenen Genesis-Stücks in
 * seinen Eigenschaften (`dazeigenschaften.js`).
 *
 * WARUM (Edgar, 25.09.2026: „auch die Material-Einstellungen fehlen"): Die aus
 * GarmentCode gebackenen Stücke hatten nur die Farbe; der GarmentCode-Reiter
 * hat Roughness, Metalness und Gewebe. Die Werte liegen als `werte.stoff =
 * {rauheit, metall, gewebe: {art, faeden, staerke}}` beim getragenen Stück
 * (wie `farbe`) und gehen mit der Figur in die Szene; gerechnet wird am
 * Material (`Stoffwerte`), ohne Serveranfrage. Gilt für jedes Genesis-Stück,
 * auch Daz' eigene — ein gewähltes Gewebe ersetzt dann dessen Normalkarte,
 * „Glatt" gibt sie zurück.
 */
export class Stueckstoff {

    /** Ohne eigenes Gewebe: aus. Eine Daz-Jeans behält so ihre Normalkarte. */
    static KEIN_GEWEBE = '';

    /** Die Bedienzeilen des Stücks (ein Kasten). */
    static felder(inst, kennung) {
        const werte = Dazkleidung.kleidung(inst)[kennung] || {};
        const stand = Stueckstoff.stand(inst, kennung, werte);
        const kasten = document.createElement('div');
        kasten.className = 'hb-stueckstoff';
        const aendern = (teil) => Stueckstoff.setzen(inst, kennung, teil);
        kasten.append(
            Stueckstoff._regler('Rauheit', stand.rauheit, (w) => aendern({ rauheit: w })),
            Stueckstoff._regler('Metall', stand.metall, (w) => aendern({ metall: w })),
            Stueckstoff._gewebe(stand.gewebe, (g) => aendern({ gewebe: g })));
        return kasten;
    }

    /** Gespeicherte Werte, sonst was das erste färbbare Material gerade zeigt. */
    static stand(inst, kennung, werte) {
        const stoff = werte.stoff || {};
        let material = null;
        for (const { netz } of Umfaerbung.netze(inst, kennung)) {
            material = Umfaerbung.materialien(netz).map((m) => m.material)
                .find((m) => Umfaerbung.faerbbar(m)) || null;
            if (material) break;
        }
        return {
            rauheit: typeof stoff.rauheit === 'number' ? stoff.rauheit : (material?.roughness ?? 0.8),
            metall: typeof stoff.metall === 'number' ? stoff.metall : (material?.metalness ?? 0),
            gewebe: stoff.gewebe || null,
        };
    }

    /** Einen Teil der Stoffwerte setzen und anwenden; false, wenn das Stück nicht getragen ist. */
    static setzen(inst, kennung, teil) {
        const werte = Dazkleidung.kleidung(inst)[kennung];
        if (!werte) return false;
        // Neues Objekt: die gespeicherte Figur hält eine flache Kopie der Werte.
        werte.stoff = { ...(werte.stoff || {}), ...teil };
        Stoffwerte.stueck(inst, kennung, werte);
        markDirty();
        return true;
    }

    static _regler(titel, wert, bei) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const name = document.createElement('label');
        name.textContent = titel;
        const regler = document.createElement('input');
        regler.type = 'range';
        regler.min = '0';
        regler.max = '100';
        regler.value = String(Math.round(wert * 100));
        const zahl = document.createElement('span');
        zahl.className = 'slider-value';
        zahl.textContent = (wert).toFixed(2);
        regler.addEventListener('input', () => {
            const w = Number(regler.value) / 100;
            zahl.textContent = w.toFixed(2);
            bei(w);
        });
        zeile.append(name, regler, zahl);
        return zeile;
    }

    static _gewebe(gewebe, bei) {
        const kasten = document.createElement('div');
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const name = document.createElement('label');
        name.textContent = 'Gewebe';
        const wahl = document.createElement('select');
        wahl.add(new Option('Wie geliefert', Stueckstoff.KEIN_GEWEBE));
        for (const [schluessel, art] of Object.entries(GEWEBEARTEN)) wahl.add(new Option(art.titel, schluessel));
        wahl.value = gewebe?.art || Stueckstoff.KEIN_GEWEBE;
        zeile.append(name, wahl);
        const art = gewebeart(wahl.value);
        const faeden = Stueckstoff._zahl('Fäden je cm', 1, 12, 0.5, gewebe?.faeden ?? art.faedenJeCm);
        const staerke = Stueckstoff._zahl('Struktur', 0, 1, 0.05, gewebe?.staerke ?? art.staerke);
        const melden = () => {
            const an = wahl.value !== Stueckstoff.KEIN_GEWEBE;
            faeden.hidden = staerke.hidden = !an;
            // „Wie geliefert" = Gewebe ohne Höhe: `Stoffwerte.gewebe` gibt die eigene Normalkarte zurück.
            bei(an ? { art: wahl.value, faeden: faeden.wert(), staerke: staerke.wert() }
                   : { art: 'glatt', faeden: 0, staerke: 0 });
        };
        wahl.addEventListener('change', () => {
            const neu = gewebeart(wahl.value);
            faeden.stellen(neu.faedenJeCm);
            staerke.stellen(neu.staerke);
            melden();
        });
        faeden.regler.addEventListener('input', melden);
        staerke.regler.addEventListener('input', melden);
        faeden.hidden = staerke.hidden = !gewebe?.art || gewebe.art === 'glatt';
        kasten.append(zeile, faeden, staerke);
        return kasten;
    }

    static _zahl(titel, min, max, schritt, wert) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const name = document.createElement('label');
        name.textContent = titel;
        const regler = document.createElement('input');
        Object.assign(regler, { type: 'range', min: String(min), max: String(max), step: String(schritt) });
        const zahl = document.createElement('span');
        zahl.className = 'slider-value';
        zeile.stellen = (w) => { regler.value = String(w); zahl.textContent = Number(w).toFixed(2); };
        zeile.wert = () => Number(regler.value);
        regler.addEventListener('input', () => { zahl.textContent = Number(regler.value).toFixed(2); });
        zeile.regler = regler;
        zeile.stellen(wert);
        zeile.append(name, regler, zahl);
        return zeile;
    }
}
