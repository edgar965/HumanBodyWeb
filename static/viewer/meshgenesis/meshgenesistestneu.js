/**
 * Meshgenesistestneu — Formular „Neuer Test aus einem Mesh“ im Reiter „Test“ von `/mesh-genesis/` (23.10.2026): Datei hochladen (`POST /api/meshgenesis/test-neu/`, Formulardaten mit CSRF),
 * danach rechnet der Lauf von selbst (`Meshgenesisrechenschlange`), die Seite springt auf den neuen Test (dort Fortschritt, `Meshgenesisrechnen`).
 */
export class Meshgenesistestneu {
    static binden(form) {
        if (!form) return;
        const meldung = form.querySelector('[data-meldung]');
        form.addEventListener('submit', async e => {
            e.preventDefault();
            const knopf = form.querySelector('button[type="submit"]');
            knopf.disabled = true;
            meldung.textContent = 'Lädt hoch …';
            try {
                const csrf = document.cookie.split('; ').find(x => x.startsWith('csrftoken='))?.split('=')[1] || '';
                const antwort = await fetch('/api/meshgenesis/test-neu/', { method: 'POST', body: new FormData(form), headers: { 'X-CSRFToken': csrf } });
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
