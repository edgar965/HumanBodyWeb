/**
 * Ai2d3djobwahl — Fotoanzahl und Genesis-Grundfigur oben auf der Testseite von 2d-3d-AI (04.11.2026, Edgar: „Auswahl anzahl der fotos (1-6), wenn mehrere fotos dann Hochladen funktion bei den Ansichten“,
 * „Auswahl ob Genesis Männlich, weiblich oder Kind“; zu „Kind“ siehe `Ai2d3dgeschlecht`). Beide speichern sofort: ein vergessenes „Übernehmen“ ließe hochgeladene Fotos im nächsten Lauf still aus.
 * Die Bildplätze hören selbst auf die Anzahl (`ai2d3dpshumaneingabe.js`). Schreibt `POST /api/2d3dai/<job>/pshuman/` {anzahl | dichte | fototextur | hand_ersatz | genesis_aus_foto} und `POST /api/2d3dai/<job>/geschlecht/` {geschlecht}.
 * „mach beides, einstellbar ganz oben beim Job“: Netzdichte und Textur aus den Fotos; „mach das auch ganz oben“: das Häkchen der Foto-Kette.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Ai2d3djobwahl {
    static binden(form) {
        if (!form) throw new Error('Ai2d3djobwahl: Formular #ai2d3d-jobwahl fehlt');
        const basis = `/api/2d3dai/${encodeURIComponent(form.dataset.job)}`;
        const meldung = form.querySelector('[data-meldung]');
        const speichern = async (feld, adresse, rumpf, text) => {
            feld.disabled = true;
            meldung.textContent = 'Speichert …';
            try {
                await Serverabruf.senden(adresse, rumpf);
                meldung.textContent = `gespeichert: ${text} — gilt ab dem nächsten Lauf`;
            } catch (fehler) {
                meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
            } finally {
                feld.disabled = false;
            }
        };
        const anzahl = form.querySelector('select[name="anzahl"]');
        const geschlecht = form.querySelector('select[name="geschlecht"]');
        anzahl.addEventListener('change', () => speichern(anzahl, `${basis}/pshuman/`, { anzahl: Number(anzahl.value) }, `${anzahl.value} ${anzahl.value === '1' ? 'Foto' : 'Fotos'}`));
        geschlecht.addEventListener('change', () => speichern(geschlecht, `${basis}/geschlecht/`, { geschlecht: geschlecht.value }, `Genesis ${geschlecht.selectedOptions[0].textContent}`));
        const dichte = form.querySelector('select[name="dichte"]');
        dichte.addEventListener('change', () => speichern(dichte, `${basis}/pshuman/`, { dichte: Number(dichte.value) }, `Netz ${dichte.selectedOptions[0].textContent}`));
        for (const haken of form.querySelectorAll('input[type="checkbox"]')) {
            const text = haken.closest('label').textContent.trim();
            haken.addEventListener('change', () => speichern(haken, `${basis}/pshuman/`, { [haken.name]: haken.checked }, `${text} ${haken.checked ? 'an' : 'aus'}`));
        }
    }
}
