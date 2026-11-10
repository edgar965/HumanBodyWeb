/**
 * Fotogenesiskoerpergroesse — das Feld „Körpergröße“ oben auf der Testseite von Foto-Genesis (24.10.2026, Edgar: „körpergröße kann ich angeben im Job oben, erstmal, mach ein UI dazu, 1,85 m“).
 * `POST /api/fotogenesis/<job>/koerpergroesse/` schreibt `koerpergroesse_m` in die job.json des Tests (`Fotogenesiskoerpergroesse`); leer = unbekannt. Die Fotoeinpassung liest den Wert von dort.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Fotogenesiskoerpergroesse {
    static binden(form) {
        if (!form) throw new Error('Fotogenesiskoerpergroesse: Formular #fotogenesis-groesse fehlt');
        const feld = form.querySelector('input[name="koerpergroesse_m"]');
        const knopf = form.querySelector('button[type="submit"]');
        const meldung = form.querySelector('[data-meldung]');
        form.addEventListener('submit', async e => {
            e.preventDefault();
            const text = feld.value.trim().replace(',', '.');
            knopf.disabled = true;
            meldung.textContent = 'Speichert …';
            try {
                const antwort = await Serverabruf.senden(`/api/fotogenesis/${encodeURIComponent(form.dataset.job)}/koerpergroesse/`,
                                                         { koerpergroesse_m: text === '' ? null : Number(text) });
                meldung.textContent = Fotogenesiskoerpergroesse.text(antwort.koerpergroesse_m, true);
            } catch (fehler) {
                meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
            } finally {
                knopf.disabled = false;
            }
        });
        meldung.textContent = Fotogenesiskoerpergroesse.text(feld.value === '' ? null : Number(feld.value), false);
    }

    static text(meter, neu) {
        if (meter === null || meter === undefined) return 'unbekannt — die Einpassung hat dann keinen Maßstab für die Figur';
        return `${neu ? 'gespeichert' : 'angegeben'}: ${meter.toFixed(2).replace('.', ',')} m, gilt ab der nächsten Einpassung`;
    }
}
