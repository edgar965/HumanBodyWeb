import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderfotozusatz — die zwei Felder der Fotos mit Rolle „Nur Iterationen“ in der Bildauswahl von „2D3D Kleider“:
 * Blickwinkel (Grad ab vorn) und „Farbe und Textur“ (zählt das Foto auch für die Fotoprojektion?). Beide gehen an den Endpunkt `rolle/`
 * (`Engine2d3dKleiderfotoendpunkte.rolle`), Teil der Bildauswahl `Engine2d3dKleiderfotos`.
 */
export class Engine2d3dKleiderfotozusatz {

    /** `seite`: die Auftragsseite (`adresse`); `neuZeichnen`: baut die Liste neu auf, wenn ein Speichern scheitert. */
    constructor(seite, neuZeichnen) {
        this.seite = seite;
        this.neuZeichnen = neuZeichnen;
    }

    /** Blickwinkel eines Fotos „Nur Iterationen“: Grad ab vorn, positiv zur linken Seite der Figur; leer = die Pose schätzt ihn. */
    winkel(eintrag) {
        const zeile = document.createElement('label');
        zeile.className = 'mesh-indexzeile';
        zeile.append('Winkel ');
        const feld = document.createElement('input');
        feld.type = 'number';
        feld.className = 'viewer-eingabe mesh-indexfeld';
        feld.min = '-180';
        feld.max = '180';
        feld.step = '1';
        feld.placeholder = 'Pose';
        feld.value = typeof eintrag.winkel === 'number' ? String(eintrag.winkel) : '';
        feld.title = 'Blickwinkel in Grad ab vorn (45 = Schrägansicht zur linken Seite der Figur, −45 zur rechten); leer = geschätzt aus der Pose';
        feld.addEventListener('change', () => this._senden(eintrag, { winkel: feld.value === '' ? null : Number(feld.value) }));
        zeile.appendChild(feld);
        return zeile;
    }

    /** „Farbe und Textur“: Aus = das Foto zählt nur für Umriss und Note. Die Schrägansichten passen nicht deckungsgleich aufs Modell und
     *  verschmieren sonst den Aufdruck (Randy, Runde 41 gegen 40). */
    farbe(eintrag) {
        const zeile = document.createElement('label');
        zeile.className = 'mesh-indexzeile';
        const feld = document.createElement('input');
        feld.type = 'checkbox';
        feld.checked = eintrag.farbe !== false;
        feld.title = 'Aus: das Foto zählt nur für Umriss und Note, nicht für Farbe und Textur der Fotoprojektion';
        feld.addEventListener('change', () => this._senden(eintrag, { farbe: feld.checked }));
        zeile.append(feld, ' Farbe und Textur');
        return zeile;
    }

    async _senden(eintrag, felder) {
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse(`rolle/${encodeURIComponent(eintrag.datei)}/`),
                { rolle: eintrag.rolle, ...felder });
            Object.assign(eintrag, { winkel: antwort.bild.winkel, farbe: antwort.bild.farbe });
        } catch (fehler) {
            window.alert(`Einstellung konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
            this.neuZeichnen();
        }
    }
}
