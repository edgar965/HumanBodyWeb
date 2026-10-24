/**
 * Ai2d3dtestneu — Formular „Neuer Test aus Fotos“ im Reiter „Test“ von `/2d-3d-AI/` (24.10.2026, wie `Mesh3daitestneu`): Fotos hochladen (`POST /api/2d3dai/test-neu/`, Formulardaten mit CSRF),
 * danach springt die Seite auf den neuen Test. Gerechnet wird noch nichts — 2d-3d-AI hat noch keine eigene KI.
 */
export class Ai2d3dtestneu {
    static binden(form) {
        if (!form) throw new Error('Ai2d3dtestneu: Formular fehlt');
        const meldung = form.querySelector('[data-meldung]');
        form.addEventListener('submit', async e => {
            e.preventDefault();
            const knopf = form.querySelector('button[type="submit"]');
            knopf.disabled = true;
            meldung.textContent = 'Lädt hoch …';
            try {
                const csrf = document.cookie.split('; ').find(x => x.startsWith('csrftoken='))?.split('=')[1] || '';
                const antwort = await fetch('/api/2d3dai/test-neu/', { method: 'POST', body: new FormData(form), headers: { 'X-CSRFToken': csrf } });
                const d = await antwort.json();
                if (!antwort.ok) throw new Error(d.error || `HTTP ${antwort.status}`);
                window.location.href = d.adresse;
            } catch (fehler) {
                meldung.textContent = `Nicht angelegt: ${fehler.message}`;
                knopf.disabled = false;
            }
        });
    }
}
