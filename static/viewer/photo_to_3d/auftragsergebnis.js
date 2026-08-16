import { enableTextureButtons } from './job_management.js';
import { API } from './state.js';
import { state } from './state.js';
import { Fotoanalyse } from './fotoanalyse.js';
import { showJobJson } from './auftragsjson.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
/**
 * Ergebnis eines Fotoauftrags laden und anzeigen.
 *
 * Aus job_management.js herausgeloest (Umbau 16.08.2026).
 */


// =========================================================================
// Show full JSON data in detection panel
// =========================================================================

/**
 * Ergebnis eines gespeicherten Auftrags laden und die Seite darauf einstellen.
 *
 * Umbau 16.08.2026: Diese Funktion hatte 128 Zeilen und war in ihren drei
 * Schritten — Zustand setzen, Regler nachziehen, Modelle laden — eine
 * Zeile-fuer-Zeile-Kopie von `Fotoanalyse`, inklusive der Ersatzbereiche fuer
 * die Metawerte und der Umrechnung um die Bereichsmitte. Der Unterschied ist
 * nur die Quelle: dort ein frisch analysiertes Foto, hier ein gespeicherter
 * Auftrag. Jetzt nutzen beide dieselben Methoden.
 */
export async function loadJobResult(auftragId) {
    try {
        const daten = await Serverabruf.json(`${API}/photo-job/${auftragId}/`);
        if (!daten.ok) {
            console.error('Auftrag nicht ladbar:', daten.error);
            return;
        }
        state.currentJobId = auftragId;
        state._previewDataCache = null;
        enableTextureButtons();
        _fotoZeigen(daten.photo_url);

        const analyse = new Fotoanalyse();
        analyse.zustandSetzen(daten);
        analyse.reglerNachziehen(daten);
        await analyse.modelleLaden(daten);

        _kopfzeile(daten);
        showJobJson(daten);
    } catch (fehler) {
        console.error('Auftrag nicht ladbar:', fehler);
    }
}

/** Das Foto des Auftrags anzeigen und die Ablegefläche verstecken. */
function _fotoZeigen(adresse) {
    if (!adresse) return;
    const bild = document.getElementById('photo-img');
    if (bild) {
        bild.src = adresse;
        bild.style.display = 'block';
    }
    for (const [id, sichtbar] of [['upload-zone', false], ['photo-preview', true],
                                  ['photo-actions', true]]) {
        const knoten = document.getElementById(id);
        if (knoten) knoten.style.display = sichtbar ? 'block' : 'none';
    }
}

/** Kurzfassung über dem Ergebnis: Geschlecht, Körperart, Backend. */
function _kopfzeile(daten) {
    const ergebnis = document.getElementById('detection-results');
    if (ergebnis) ergebnis.style.display = 'block';
    const felder = document.getElementById('detection-params');
    if (!felder) return;
    const geschlecht = daten.gender === 'male' ? 'Männlich' : 'Weiblich';
    felder.innerHTML = '<div class="auftrag-kopfzeile">'
        + `<b>Geschlecht:</b> ${geschlecht} &nbsp;|&nbsp;`
        + `<b>Body Type:</b> ${state.currentBodyType} &nbsp;|&nbsp;`
        + `<b>Backend:</b> ${daten.backend || '?'}</div>`;
}

export { showJobJson } from './auftragsjson.js';
