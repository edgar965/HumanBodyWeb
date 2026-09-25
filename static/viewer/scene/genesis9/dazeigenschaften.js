import { escapeHtml } from '../utils.js';
import { state } from '../state.js';
import { Reiterzuordnung } from '../../gemeinsam/reiterzuordnung.js';
import { Umfaerbung } from '../../gemeinsam/umfaerbung.js';
import { Genesis9kleidung } from '../../gemeinsam/genesis9kleidung.js';
import { Dazkleidung } from './dazkleidung.js';
import { Stueckfarbe } from './stueckfarbe.js';
import { Stueckstoff } from './stueckstoff.js';
import { Gcherkunft } from './gcherkunft.js';

/**
 * Dazeigenschaften — der Eigenschaften-Bereich eines gewählten Daz-Stücks.
 *
 * WARUM (Edgar, 24.09.2026): „eine eigene Farbe je Gruppe über die
 * Teil-Auswahl in der Szene" und „die Teilnetze auch in den Eigenschaften des
 * Assets". Ein Klick auf ein Daz-Teil (`teilnetz_auswahl.js`) zeigt hier das
 * ganze Stück: oben seine Farbe, darunter JEDES Teilnetz (`kennung/n`, mit
 * seiner Beschriftung) und je Teilnetz seine Materialgruppen
 * (`material.userData.gruppe`, Kin Hair: `kin Hair`, `kin Cap`, `bangs`) mit
 * eigenem Farbfeld (`Stueckfarbe`). Das angeklickte Teilnetz ist
 * hervorgehoben, die angeklickte Gruppe (`state._getroffeneGruppe` =
 * `{key, gruppe}`, aus dem Dreieck des Treffers, `interaction.js`) markiert
 * und in Sicht gerollt.
 *
 * Gruppenfarben gelten je Gruppenname für das ganze Stück — dieselbe Gruppe
 * in zwei Teilnetzen (Daz teilt Materialien über Teile) ist dasselbe Material.
 */
export class Dazeigenschaften {

    static BEREICH = 'prop-daz-section';
    static INHALT = 'prop-daz-teile';

    /** Das Daz-Stück hinter einem gewählten Teilnetz — oder null. */
    static stueckVon(teilnetz) {
        if (!teilnetz || teilnetz.type !== 'cloth') return null;
        const stueck = Reiterzuordnung.stueckVon(teilnetz.key);
        return stueck?.liste === 'daz' ? stueck.kennung : null;
    }

    /** Zeigen (Daz-Teil gewählt) oder verstecken; true, wenn gezeigt. */
    static zeigen(teilnetz) {
        const bereich = document.getElementById(Dazeigenschaften.BEREICH);
        const kennung = Dazeigenschaften.stueckVon(teilnetz);
        const inst = kennung ? state.characters.get(teilnetz.charId) : null;
        const an = Boolean(inst && Dazkleidung.kleidung(inst)[kennung]);
        if (bereich) {
            bereich.classList.toggle('hb-versteckt', !an);
            bereich.style.display = an ? '' : 'none';
        }
        if (an) Dazeigenschaften.fuellen(inst, kennung, teilnetz.key);
        return an;
    }

    static async fuellen(inst, kennung, gewaehlt) {
        const inhalt = document.getElementById(Dazeigenschaften.INHALT);
        if (!inhalt) return;
        inhalt.dataset.stueck = `${inst.id}:${kennung}`;
        const name = await Genesis9kleidung.anzeigename(kennung);
        if (inhalt.dataset.stueck !== `${inst.id}:${kennung}`) return;   // inzwischen anderes gewählt
        const werte = Dazkleidung.kleidung(inst)[kennung] || {};
        inhalt.innerHTML = '';
        const kopf = document.createElement('div');
        kopf.className = 'slider-row';
        kopf.innerHTML = `<label class="stueckname">${escapeHtml(name)} — ganzes Stück</label>`;
        kopf.appendChild(Stueckfarbe.feld({ inst, kennung, wert: werte.farbe || '',
                                            titel: 'Farbe des Stücks' }));
        inhalt.appendChild(kopf);
        // Rauheit, Metall, Gewebe (25.09.2026) und bei GC-Stücken der Weg zurück in den Schnitt.
        inhalt.appendChild(Stueckstoff.felder(inst, kennung));
        const schnitt = Gcherkunft.knopf(inst, kennung);
        if (schnitt) inhalt.appendChild(schnitt);
        let getroffen = null;
        for (const { schluessel, netz } of Umfaerbung.netze(inst, kennung)) {
            const teil = document.createElement('div');
            teil.className = `daz-teil-kopf${schluessel === gewaehlt ? ' gewaehlt' : ''}`;
            teil.textContent = netz.userData?.beschriftung || schluessel;
            inhalt.appendChild(teil);
            for (const gruppe of Dazeigenschaften.gruppen(netz)) {
                const zeile = Dazeigenschaften._gruppenzeile(inst, kennung, gruppe, werte);
                const treffer = state._getroffeneGruppe;       // nur ein Klick in DIESES Teilnetz
                if (schluessel === gewaehlt && treffer?.key === gewaehlt && treffer.gruppe === gruppe) {
                    zeile.classList.add('getroffen');
                    getroffen = zeile;
                }
                inhalt.appendChild(zeile);
            }
        }
        getroffen?.scrollIntoView({ block: 'nearest' });
    }

    /** Die Materialgruppen eines Teilnetzes, ohne Doppel, in Netzreihenfolge. */
    static gruppen(netz) {
        const aus = [];
        for (const { material } of Umfaerbung.materialien(netz)) {
            const gruppe = material.userData?.gruppe;
            if (gruppe && !aus.includes(gruppe)) aus.push(gruppe);
        }
        return aus;
    }

    static _gruppenzeile(inst, kennung, gruppe, werte) {
        const zeile = document.createElement('div');
        zeile.className = 'daz-gruppe';
        zeile.innerHTML = `<span title="${escapeHtml(gruppe)}">${escapeHtml(gruppe)}</span>`;
        zeile.appendChild(Stueckfarbe.feld({ inst, kennung, gruppe, titel: gruppe,
                                             wert: werte.gruppenfarben?.[gruppe] || '' }));
        return zeile;
    }
}
