/**
 * Ai2d3dkoerpergroesse — das Feld „Körpergröße“ oben auf der Testseite von 2d-3d-AI (24.10.2026, Edgar: „körpergröße kann ich angeben im Job oben, erstmal, mach ein UI dazu, 1,85 m“).
 * `POST /api/2d3dai/<job>/koerpergroesse/` schreibt `koerpergroesse_m` in die job.json des Tests (`Ai2d3dkoerpergroesse`); leer = unbekannt. Die Fotoeinpassung liest den Wert von dort.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Ai2d3dkoerpergroesse {
    static binden(form) {
        if (!form) throw new Error('Ai2d3dkoerpergroesse: Formular #ai2d3d-groesse fehlt');
        const feld = form.querySelector('input[name="koerpergroesse_m"]');
        const knopf = form.querySelector('button[type="submit"]');
        const meldung = form.querySelector('[data-meldung]');
        form.addEventListener('submit', async e => {
            e.preventDefault();
            const text = feld.value.trim().replace(',', '.');
            knopf.disabled = true;
            meldung.textContent = 'Speichert …';
            try {
                const antwort = await Serverabruf.senden(`/api/2d3dai/${encodeURIComponent(form.dataset.job)}/koerpergroesse/`,
                                                         { koerpergroesse_m: text === '' ? null : Number(text) });
                meldung.textContent = Ai2d3dkoerpergroesse.text(antwort.koerpergroesse_m, true);
            } catch (fehler) {
                meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
            } finally {
                knopf.disabled = false;
            }
        });
        meldung.textContent = Ai2d3dkoerpergroesse.text(feld.value === '' ? null : Number(feld.value), false);
    }

    static text(meter, neu) {
        if (meter === null || meter === undefined) return 'unbekannt — die Einpassung hat dann keinen Maßstab für die Figur';
        return `${neu ? 'gespeichert' : 'angegeben'}: ${meter.toFixed(2).replace('.', ',')} m, gilt ab der nächsten Einpassung`;
    }
}
