import { Dazkleidung } from './dazkleidung.js';
import { Umfaerbung } from '../../gemeinsam/umfaerbung.js';
import { Stoffwerte } from '../../gemeinsam/stoffwerte.js';
import { Stoffarten } from '../../gemeinsam/stoffarten.js';
import { markDirty } from '../undo.js';
import { Stueckstoffzeilen } from './stueckstoffzeilen.js';

/**
 * Stueckstoff — der Block „Stoff“ eines getragenen Genesis-Stücks: in Assets → Eigen (`Genesis9eigenstueck`) und in den Eigenschaften des
 * gewählten Daz-Stücks (`dazeigenschaften.js`).
 *
 * WARUM (Edgar, 25.09.2026: „auch die Material-Einstellungen fehlen"): Die aus
 * GarmentCode gebackenen Stücke hatten nur die Farbe; der GarmentCode-Reiter
 * hat Roughness, Metalness und Gewebe. Dann (25.10.2026: „beim Regler: Stoff gibt es noch mehr Optionen … die Anzahl der Fäden, Glanz,
 * stoffart usw.“): die Vorwahl Stoffart (`Stoffarten`), Glanz, Glanzsaum mit Weichheit und Farbe, Relief der eigenen Normalkarte, und
 * die Bindung im Shader statt als Ersatz-Normalkarte (`Stoffshader`).
 *
 * Die Werte liegen als `werte.stoff` beim getragenen Stück (wie `farbe`, Form `Stoffarten.werte`) und gehen mit der Figur in die Szene;
 * gerechnet wird am Material bzw. in dessen Shader (`Stoffwerte`), ohne Serveranfrage und ohne Neubau. Gilt für jedes Genesis-Stück, auch
 * Daz' eigene. Eine Stoffart setzt alle Felder außer Relief (das gehört der Normalkarte des Stücks, nicht dem Stoff); danach ist jedes
 * Feld einzeln verstellbar, die Auswahl zeigt weiter, wovon man ausging.
 */
export class Stueckstoff {

    /** Ohne eigenes Gewebe: aus. Eine Daz-Jeans behält so ihre Normalkarte ohne Bindung darüber. */
    static KEIN_GEWEBE = '';

    static HILFE = {
        stoffart: 'Setzt Rauheit, Glanz, Glanzsaum und Gewebe auf passende Werte — danach ist jedes Feld einzeln verstellbar.',
        glanz: 'Stärke der Spiegelung (Daz: Glossy Layered Weight). 1 = wie geliefert, 0 = keine Spiegelung, 2 = doppelt.',
        saum: 'Glanzsaum (Sheen): der helle Rand der Fasern unter streifendem Licht — Samt, Satin, Wolle. 0 = aus.',
        saumstreuung: 'Klein = harter Schimmer (Satin, Seide), groß = weicher Flaum (Wolle, Baumwolle).',
        saumfarbe: 'Ohne Haken trägt der Saum die Farbe des Stoffs (ein weißer Saum sieht auf dunklem Stoff wie Haut aus).',
        relief: 'Stärke der eigenen Normalkarte des Stücks (Nähte, Daz-Struktur, gebackene Falten). 1 = wie geliefert.',
        faeden: 'Fäden (bei Leder: Narben) je Zentimeter an der UV des Stücks. Feiner als ein Bildpunkt blendet die Bindung aus.',
        staerke: 'Wie stark sich die Bindung im Licht abzeichnet.',
    };

    /** Die Bedienzeilen des Stücks (ein Kasten, `data-stueckstoff` = Kennung). */
    static felder(inst, kennung) {
        const werte = Dazkleidung.kleidung(inst)[kennung] || {};
        const stand = Stueckstoff.stand(inst, kennung, werte);
        const kasten = document.createElement('div');
        kasten.className = 'hb-stueckstoff';
        kasten.dataset.stueckstoff = kennung;
        const Z = Stueckstoffzeilen;
        const H = Stueckstoff.HILFE;
        const aendern = (teil) => Stueckstoff.setzen(inst, kennung, teil);
        const arten = [['', '– eigene Werte –'], ...Object.entries(Stoffarten.ARTEN).map(([s, a]) => [s, a.titel])];
        kasten.append(
            Z.wahl('stoffart', 'Stoffart', arten, stand.stoffart, (art) => {
                if (!art) { aendern({ stoffart: '' }); return; }
                Stueckstoff.stoffart(inst, kennung, art);
                kasten.replaceWith(Stueckstoff.felder(inst, kennung));   // alle Schieber auf die neuen Werte
            }, H.stoffart),
            Z.regler('rauheit', 'Rauheit', 0, 1, 0.01, stand.rauheit, (w) => aendern({ rauheit: w })),
            Z.regler('metall', 'Metall', 0, 1, 0.01, stand.metall, (w) => aendern({ metall: w })),
            Z.regler('glanz', 'Glanz', 0, 2, 0.05, stand.glanz, (w) => aendern({ glanz: w }), H.glanz),
            Z.regler('saum', 'Glanzsaum', 0, 1, 0.05, stand.saum, (w) => aendern({ saum: w }), H.saum),
            Z.regler('saumstreuung', 'Saum weich', 0, 1, 0.05, stand.saumstreuung, (w) => aendern({ saumstreuung: w }), H.saumstreuung),
            Z.farbe('saumfarbe', 'Saumfarbe', stand.saumfarbe, (hex) => aendern({ saumfarbe: hex }), H.saumfarbe),
            Z.regler('relief', 'Relief', 0, 2, 0.05, stand.relief, (w) => aendern({ relief: w }), H.relief),
            Stueckstoff._gewebe(stand.gewebe, (g) => aendern({ gewebe: g })));
        return kasten;
    }

    /** Gespeicherte Werte, sonst was das erste färbbare Material gerade zeigt bzw. die Vorgabe (`Stoffarten.VORGABE`). */
    static stand(inst, kennung, werte) {
        const stoff = werte.stoff || {};
        let material = null;
        for (const { netz } of Umfaerbung.netze(inst, kennung)) {
            material = Umfaerbung.materialien(netz).map((m) => m.material)
                .find((m) => Umfaerbung.faerbbar(m)) || null;
            if (material) break;
        }
        const v = Stoffarten.VORGABE;
        const zahl = (w, ersatz) => (typeof w === 'number' ? w : ersatz);
        return {
            stoffart: Stoffarten.ARTEN[stoff.stoffart] ? stoff.stoffart : '',
            rauheit: zahl(stoff.rauheit, material?.roughness ?? 0.8),
            metall: zahl(stoff.metall, material?.metalness ?? 0),
            glanz: zahl(stoff.glanz, v.glanz),
            saum: zahl(stoff.saum, v.saum),
            saumstreuung: zahl(stoff.saumstreuung, v.saumstreuung),
            saumfarbe: stoff.saumfarbe || v.saumfarbe,
            relief: zahl(stoff.relief, Math.abs(material?.normalScale?.x ?? v.relief)),
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

    /** Eine Stoffart wählen: alle Stoffwerte außer Relief auf ihre Zeile (`Stoffarten.werte`). */
    static stoffart(inst, kennung, name) {
        const neu = Stoffarten.werte(name);
        return neu ? Stueckstoff.setzen(inst, kennung, neu) : false;
    }

    static _gewebe(gewebe, bei) {
        const Z = Stueckstoffzeilen;
        const kasten = document.createElement('div');
        const an = gewebe?.art && gewebe.art !== 'glatt' ? gewebe.art : Stueckstoff.KEIN_GEWEBE;
        const wahl = Z.wahl('gewebe', 'Gewebe', [['', 'Wie geliefert'], ...Stoffarten.gewebewahl()], an, null);
        const vorgabe = Stoffarten.gewebevorgabe(an || 'leinwand');
        const faeden = Z.regler('faeden', 'Fäden je cm', 0.5, 40, 0.5, gewebe?.faeden ?? vorgabe.faeden, null, Stueckstoff.HILFE.faeden);
        const staerke = Z.regler('staerke', 'Struktur', 0, 1, 0.05, gewebe?.staerke ?? vorgabe.staerke, null, Stueckstoff.HILFE.staerke);
        const melden = () => {
            const aktiv = wahl.wahl.value !== Stueckstoff.KEIN_GEWEBE;
            faeden.hidden = staerke.hidden = !aktiv;
            // „Wie geliefert" = keine Bindung über der eigenen Normalkarte (`Stoffshader`: Art 0).
            bei(aktiv ? { art: wahl.wahl.value, faeden: faeden.wert(), staerke: staerke.wert() }
                      : { art: 'glatt', faeden: 0, staerke: 0 });
        };
        wahl.wahl.addEventListener('change', () => {
            const neu = Stoffarten.gewebevorgabe(wahl.wahl.value || 'leinwand');
            faeden.stellen(neu.faeden);
            staerke.stellen(neu.staerke);
            melden();
        });
        faeden.regler.addEventListener('input', melden);
        staerke.regler.addEventListener('input', melden);
        faeden.hidden = staerke.hidden = !an;
        kasten.append(wahl, faeden, staerke);
        return kasten;
    }
}
