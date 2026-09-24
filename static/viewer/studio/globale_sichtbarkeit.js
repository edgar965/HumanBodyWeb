import { state } from './state.js';

/**
 * Globale Sichtbarkeits-Schalter „alle Lichter/alle Modelle/alle Kleidung" —
 * ein reiner Anzeige-Zustand (Vorbild: Theatre, `theatre.html:899-907`).
 *
 * BEWUSST NICHT über `track.muted`: `muted` ist Projektdaten (gespeichert,
 * Undo-fähig, schließt die Spur vom Export aus — `export_nutzlast.js:77`).
 * Ein Blick-Schalter, den man beim Arbeiten kurz umlegt, darf weder im
 * gespeicherten Projekt landen noch versehentlich einen Export beschneiden.
 *
 * WARUM `anwenden()` und nicht nur `track.light.visible = false` an Ort und
 * Stelle: `applyPlayhead()` läuft bei jeder Zustandsänderung neu und setzt
 * Licht- (`syncLightVisibility()`) und Modell-Sichtbarkeit
 * (`Modellspur.anwenden()`) dabei JEDES MAL neu — ein einmaliges Umschalten
 * wäre beim nächsten Bild wieder weg. `anwenden()` haengt darum als letzter
 * Schritt hinter die normale Berechnung in `applyPlayhead()`.
 */
export class GlobaleSichtbarkeit {
    lichter = true;
    modell = true;
    kleidung = true;

    /** Nach der normalen Spur-Anwendung aufrufen: erzwingt „aus", wo gewählt. */
    anwenden() {
        if (!this.lichter) {
            for (const track of state.project.lightTracks) {
                if (track.light) track.light.visible = false;
                if (track.lightHelper) track.lightHelper.visible = false;
            }
        }
        if (!this.modell) {
            for (const track of state.project.modelTracks) {
                const bewegung = state.project.getLinkedAnimation(track);
                if (bewegung?.group) bewegung.group.visible = false;
            }
        }
    }

    /**
     * Kleidung steckt an keiner eigenen Spur, sondern an Kind-Objekten der
     * Modell-Gruppe. HumanBody/GarmentCode markieren mit `userData.isGarment`
     * (`gemeinsam/modellzubehoer.js:79`), Genesis 9 stattdessen mit
     * `userData.art === 'kleidung'` (`gemeinsam/genesis9kleidung.js:104` —
     * `art` unterscheidet dort zusätzlich `haar`/`requisit`, die nicht als
     * Kleidung gelten sollen). Beide Markierungen prüfen, sonst blieb Genesis-9-
     * Kleidung vom Knopf „Alle Kleider ausblenden" unberührt.
     * Nichts setzt das pro Bild neu — direktes Umschalten reicht, ohne Haken
     * in `applyPlayhead()`.
     */
    kleidungUmschalten(sichtbar) {
        this.kleidung = sichtbar;
        for (const track of state.project.modelTracks) {
            const bewegung = state.project.getLinkedAnimation(track);
            if (!bewegung?.group) continue;
            bewegung.group.traverse(obj => {
                const ud = obj.userData;
                if (ud?.isGarment || ud?.art === 'kleidung') obj.visible = sichtbar;
            });
        }
    }
}

export const globaleSichtbarkeit = new GlobaleSichtbarkeit();
