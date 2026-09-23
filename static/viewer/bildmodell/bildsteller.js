/**
 * Bildsteller — die Wahlfelder und Knöpfe unter jeder Bildkachel.
 *
 * Edgar (19.09.2026): „Mach in jeder Zeile einen Button zum Bild hochladen,
 * mit dem ich ein anderes Bild hochladen kann, und eines zum Bild löschen.
 * … ein paar Combo-Boxen … Erste Combo Box: Hauptbild-Typ, zweite
 * Nebenbild-Typ, dritte nur Textur?"
 *
 * Drei Auswahlfelder aus `katalog.bildtypen` (`Bildmodellbildtypen`):
 * Bildtyp (Körper vorn/Seite/hinten/dreiviertel, Kopf vorn/Seite/hinten,
 * Video), zweite Box mit den Gruppen „Hauptbild" (Hauptbild vorn/hinten/
 * seitlich, Kopf-Hauptbild vorn/hinten/seitlich — Edgar, 20.09.2026: nur
 * die markierten bauen den Körper, `Bildmodellhauptgewicht`) und
 * „Nebenbild" (Körperteil: Hände, Gesicht, Oberkörper, Rücken, Hüfte, Arme,
 * Beine, Füße; Gruppe; ohne Befund), und Nutzung (Form und Textur / nur Form /
 * nur Textur / aus). Typ und Nebenbild schließen sich aus — wer einen Typ
 * wählt, leert das Nebenbild und umgekehrt; ein Hauptbild setzt den Typ mit.
 * Der Server schreibt Kategorie, Ansicht, Teil und Markierung. Dazu Gewicht, das Textur-Häkchen (`Texturwahl`),
 * „Ersetzen" (Datei wählen → `original/<quelle>/ersetzen/`, alle Ausschnitte
 * dieser Quelle gehen mit), „SMPL (GVHMR)" (`Gvhmrknopf`, 20.09.2026) und
 * „Löschen" (`bild/<datei>/loeschen/`).
 */
import { Texturwahl } from './texturwahl.js';
import { Gvhmrknopf } from './gvhmrknopf.js';
import { Flameknopf } from './flameknopf.js';
import { Freisteller } from './freisteller.js';

export class Bildsteller {

    static DATEIEN = '.jpg,.jpeg,.png,.webp,.bmp,.tif,.tiff,.mp4,.mov,.webm,.mkv,.avi,.m4v';
    static _freisteller = null;   // EIN Fenster je Seite (Tabelle und Kacheln teilen es)

    constructor(auftrag, katalog) {
        this.auftrag = auftrag;
        this.typen = (katalog || {}).bildtypen || { haupt: [], neben: [], nutzung: [] };
        this.gvhmr = new Gvhmrknopf(auftrag);
        this.flame = new Flameknopf(auftrag);   // „Kopf (FLAME)" an Kopfbildern (20.09.2026)
        this.freisteller = Bildsteller._freisteller || (Bildsteller._freisteller = new Freisteller(auftrag));
    }

    /** Das Feld unter der Kachel des Eintrags `b`. */
    feld(b) {
        const feld = document.createElement('div');
        feld.className = 'bildmodell-steller';
        feld.appendChild(this._wahlzeile(b));
        feld.appendChild(this._nutzungszeile(b));
        const info = (this.auftrag.zustand.texturbilder || []).find(e => e.datei === b.datei) || null;
        const textur = Texturwahl.feld(b, (datei, aenderung) => this.stellen(datei, aenderung), info);
        if (textur) feld.appendChild(textur);
        feld.appendChild(this._knopfzeile(b));
        return feld;
    }

    // ------------------------------------------------------------ Boxen

    _auswahl(liste, wert, titel, beiWahl) {
        const wahl = document.createElement('select');
        wahl.title = titel;
        const gruppen = new Map();
        for (const e of liste) {
            const o = document.createElement('option');
            o.value = e.wert; o.textContent = e.anzeige; o.selected = e.wert === wert;
            if (e.erklaerung) o.title = e.erklaerung;
            if (!e.gruppe) { wahl.appendChild(o); continue; }
            if (!gruppen.has(e.gruppe)) {
                const g = document.createElement('optgroup');
                g.label = e.gruppe;
                gruppen.set(e.gruppe, g);
                wahl.appendChild(g);
            }
            gruppen.get(e.gruppe).appendChild(o);
        }
        wahl.addEventListener('change', () => beiWahl(wahl.value));
        return wahl;
    }

    static haupt(b) {
        const k = b.kategorie;
        if (!['koerper', 'kopf', 'video'].includes(k)) return '';
        const ansicht = k === 'video' ? 'drehung' : (b.ansicht || 'vorne');
        return `${k}/${['vorne', 'seite', 'hinten', 'dreiviertel', 'drehung'].includes(ansicht) ? ansicht : 'vorne'}`;
    }

    static hauptbild(b) {
        if (!b.hauptbild || !['koerper', 'kopf'].includes(b.kategorie)) return '';
        if (!['vorne', 'hinten', 'seite'].includes(b.ansicht)) return '';
        return `haupt/${b.kategorie === 'kopf' ? 'kopf-' : ''}${b.ansicht}`;
    }

    static neben(b) {
        const k = b.kategorie || 'neben';
        if (['koerper', 'kopf', 'video'].includes(k)) return Bildsteller.hauptbild(b);
        if (k !== 'neben') return k;
        return b.teil ? `neben/${b.teil}` : 'neben';
    }

    /** Die beiden Boxen Hauptbild/Nebenbild allein — für die Tabelle der Proportionen. */
    wahlzeile(b) { return this._wahlzeile(b); }

    _wahlzeile(b) {
        const zeile = document.createElement('div');
        zeile.className = 'bildmodell-stellerzeile';
        const haupt = this._auswahl(this.typen.haupt, Bildsteller.haupt(b),
            'Bildtyp — Körperbilder gehen an den Schätzer, Kopfbilder an FLAME',
            wert => this.stellen(b.datei, { haupt: wert }));
        const neben = this._auswahl(this.typen.neben, Bildsteller.neben(b),
            'Hauptbild (nur die markierten bauen den Körper, das Kopf-Hauptbild den Kopf) oder Nebenbild '
            + '(Hände liefern die Fingerlänge, jedes Teil seine Fotofarbe)',
            wert => this.stellen(b.datei, { neben: wert }));
        if (b.video) neben.disabled = true;
        zeile.append(haupt, neben);
        return zeile;
    }

    _nutzungszeile(b) {
        const zeile = document.createElement('div');
        zeile.className = 'bildmodell-stellerzeile';
        const nutzung = this._auswahl(this.typen.nutzung, b.nutzung || 'form_textur',
            'Nutzung — wofür das Bild zählt', wert => this.stellen(b.datei, { nutzung: wert }));
        const gewicht = document.createElement('input');
        gewicht.type = 'range'; gewicht.min = '0'; gewicht.max = '1'; gewicht.step = '0.1';
        gewicht.value = String(b.gewicht ?? 0);
        gewicht.title = 'Gewicht in der Mischung (0 = nicht verwendet)';
        const wert = document.createElement('span');
        wert.className = 'bildmodell-gewicht';
        wert.textContent = Number(gewicht.value).toFixed(1);
        gewicht.addEventListener('input', () => { wert.textContent = Number(gewicht.value).toFixed(1); });
        gewicht.addEventListener('change', () => this.stellen(b.datei, { gewicht: Number(gewicht.value) }));
        zeile.append(nutzung, gewicht, wert);
        const kopf = this.kopfFeld(b);
        if (kopf) zeile.appendChild(kopf);
        if (b.manuell) {
            const m = document.createElement('span');
            m.className = 'bildmodell-manuell'; m.title = 'von Hand gestellt'; m.textContent = '✎';
            zeile.appendChild(m);
        }
        return zeile;
    }

    /** Häkchen „Kopf" (Edgar, 22.09.2026: „mehrere Fotos auswählen für den Kopf") — dieses Foto
     *  geht in die Kopf-Pipeline (`Bildmodellkopf.bilder`, Schritt „Kopf"). Kein Video; ohne
     *  Häkchen an irgendeinem Bild gelten die Kopf-Hauptbilder wie bisher. */
    kopfFeld(b) {
        if (b.video) return null;
        const feld = document.createElement('label');
        feld.className = 'bildmodell-kopfauswahl';
        feld.title = 'Für die Kopf-Pipeline (FLAME/MICA/FaceBuilder) verwenden — ohne Häkchen an '
            + 'irgendeinem Bild gelten die Kopf-Hauptbilder';
        const kasten = document.createElement('input');
        kasten.type = 'checkbox';
        kasten.checked = !!b.kopf_an;
        kasten.addEventListener('change', async () => {
            try { await this.auftrag.bildStellen(b.datei, { kopf_an: kasten.checked ? true : null }); }
            catch (fehler) { kasten.checked = !kasten.checked; window.alert(fehler.message); }
        });
        feld.append(kasten, document.createTextNode(' Kopf'));
        return feld;
    }

    // ----------------------------------------------------------- Knöpfe

    _knopfzeile(b) {
        const zeile = document.createElement('div');
        zeile.className = 'bildmodell-stellerzeile bildmodell-stellerknoepfe';
        const gvhmr = this.gvhmr.element(b) || this.flame.element(b);
        const frei = this.freisteller.element(b);
        zeile.append(this.ersetzenKnopf(b.quelle || b.datei), ...(gvhmr ? [gvhmr] : []), ...(frei ? [frei] : []), this.loeschenKnopf(
            `Bild ${b.datei} löschen?` + (b.quelle && b.quelle !== b.datei ? ' (Das Original bleibt, solange ein anderer Ausschnitt es braucht.)' : ''),
            () => this.auftrag.bildLoeschen(b.datei)));
        return zeile;
    }

    /** Ein Knopf „Ersetzen" mit verstecktem Dateifeld — für die Quelle `name`. */
    ersetzenKnopf(name) {
        const knopf = document.createElement('label');
        knopf.className = 'btn btn-secondary btn-sm bildmodell-hochladen';
        knopf.title = `${name} durch eine andere Datei ersetzen — die Ausschnitte dieser Datei werden neu gesichtet`;
        knopf.innerHTML = '<i class="fas fa-upload"></i> <span>Ersetzen</span>';
        const eingabe = document.createElement('input');
        eingabe.type = 'file'; eingabe.accept = Bildsteller.DATEIEN; eingabe.hidden = true;
        eingabe.addEventListener('change', async () => {
            if (!eingabe.files.length) return;
            try { await this.auftrag.originalErsetzen(name, eingabe.files[0]); }
            catch (fehler) { window.alert(`Nicht ersetzt: ${fehler.message}`); }
            eingabe.value = '';
        });
        knopf.appendChild(eingabe);
        return knopf;
    }

    loeschenKnopf(frage, tat) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-danger btn-sm';
        knopf.title = 'Löschen';
        knopf.innerHTML = '<i class="fas fa-trash"></i>';
        knopf.addEventListener('click', async () => {
            if (!window.confirm(frage)) return;
            try { await tat(); }
            catch (fehler) { window.alert(`Nicht gelöscht: ${fehler.message}`); }
        });
        return knopf;
    }

    async stellen(datei, aenderung) {
        try { await this.auftrag.bildStellen(datei, aenderung); }
        catch (fehler) { window.alert(fehler.message); }
    }
}
