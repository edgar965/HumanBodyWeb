/**
 * Proportionenuebernahme — „Übernehmen" und „… und neu berechnen" des Proportionen-Popups.
 *
 * Aus `Proportionendialog` herausgelöst (20.09.2026, die Datei stand bei 297
 * Zeilen, als das 3D-Popup dazukam). Legt Werte UND die gezogenen Linien der
 * Fotos am Auftrag ab (POST `proportionen/`); mit `rechnen` startet der Lauf
 * ab „Anpassung" (ab „Zielnetz", wenn Größe oder Gewicht geändert sind).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Proportionenuebernahme {

    /** Je Foto: Linien der Maße mit Eingabe und alle von Hand gesetzten, dazu die entfernten Marker. */
    static linien(dialog) {
        const werte = dialog.werte();
        const aus = {};
        for (const [id, q] of Object.entries(dialog.quellen)) {
            if (q.art !== 'foto') continue;
            const linien = {};
            for (const [k, linie] of Object.entries(dialog.lagen[id] || {})) {
                const vomServer = JSON.stringify((dialog.serverStart[id] || {})[k] || null);
                if (werte[k] !== undefined || vomServer !== JSON.stringify(linie)) linien[k] = linie;
            }
            const entfernt = [...(dialog.entfernt[id] || [])];
            if (Object.keys(linien).length || entfernt.length) aus[q.datei] = { linien, entfernt };
        }
        return aus;
    }

    static async uebernehmen(dialog, rechnen) {
        const proportionen = dialog.werte();
        const linien = Proportionenuebernahme.linien(dialog);
        try {
            const antwort = await Serverabruf.senden(dialog.auftrag.adresse('proportionen/'), { proportionen, linien });
            if (antwort.error) throw new Error(antwort.error);
            dialog.auftrag.zustand.optionen = { ...(dialog.auftrag.zustand.optionen || {}), proportionen: antwort.proportionen,
                                                proportionen_linien: antwort.linien };
            for (const k of Object.keys(dialog.eingaben)) delete dialog.eingaben[k];
            Object.assign(dialog.eingaben, antwort.proportionen);
            dialog.dialog.close();
            dialog.aenderung();
            if (rechnen) {
                // Größe/Gewicht unverändert: das Zielnetz steht, ab „Anpassung" reicht (spart den Zielschritt).
                const p = window.__bildmodell?.person;
                if (p) await p.neuBerechnen(p.unveraendert() ? 'anpassung' : 'ziel');
            }
        } catch (fehler) {
            window.alert(`Proportionen nicht übernommen: ${fehler.message}`);
        }
    }
}
