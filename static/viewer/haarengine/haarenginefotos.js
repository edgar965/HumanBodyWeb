import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshfotowahl } from '../mesh/meshfotowahl.js';

/**
 * Haarenginefotos — die Bildauswahl der Auftragsseite „Haar Engine": die Vorlagen der Iterationen.
 *
 * Je Foto eine Karte mit Rolle, Gewicht (%), Platz sowie „Ersetzen" und „Entfernen"; darüber „Fotos hinzufügen" (Dateidialog ODER
 * ganzer Ordner, `Meshfotowahl`). Aufgebaut wie der Kasten „Fotos" auf der Seite des Reiters „Mesh" (`Meshauftragseite._fotoliste` und
 * Nachbarn).
 *
 * Rolle, Gewicht, Platz, Hinzufügen, Ersetzen und Entfernen gehen alle auch während eines Laufs — die Fotos sind Referenz für die
 * Note, kein Live-Eingang; der Server schützt Rolle, Gewicht und Reihenfolge gegen ein Rückschreiben des Laufs (siehe
 * `Haarengineauftrag.bilder_sichern`). Neu gezeichnet wird nur, wenn sich die Liste geändert hat — und nicht, solange man gerade in
 * einem Feld der Liste ist: Die Nachfrage im Takt würde sonst den Regler unter der Maus und das Feld unter dem Cursor zurücksetzen.
 */
export class Haarenginefotos {

    static GEWICHT_SPEICHERN_MS = 500;

    constructor(seite) {
        this.seite = seite;
        this.liste = document.getElementById('fotoliste');
        this.knoepfe = document.getElementById('foto-knoepfe');
        this._stand = null;
        this._uhren = {};
        this._hinzufuegen = this._knopfBauen();
    }

    /** „Fotos hinzufügen" über der Liste — einmal gebaut, nicht bei jedem Neuzeichnen. */
    _knopfBauen() {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-secondary btn-sm';
        knopf.innerHTML = '<i class="fas fa-plus"></i> <span>Fotos hinzufügen</span>';
        knopf.addEventListener('click', () => this.hinzufuegen(knopf));
        this.knoepfe.appendChild(knopf);
        return knopf;
    }

    zeigen(z) {
        const stand = JSON.stringify(z.bilder);
        if (stand === this._stand) return;
        const aktiv = document.activeElement;
        if (aktiv && this.liste.contains(aktiv) && aktiv.matches('input, select')) return;
        this._stand = stand;
        this._zeichnen(z);
    }

    neuZeichnen() {
        this._stand = null;
        this.zeigen(this.seite.zustand);
    }

    _zeichnen(z) {
        this.liste.innerHTML = '';
        const bilder = z.bilder || [];
        bilder.forEach((eintrag, i) => this.liste.appendChild(this._karte(eintrag, i, bilder.length)));
    }

    // ------------------------------------------------------------- Karte

    _karte(eintrag, index, gesamt) {
        const karte = document.createElement('div');
        karte.className = 'mesh-fotokarte' + (eintrag.rolle === 'aus' ? ' haarengine-foto-aus' : '');
        const bild = document.createElement('img');
        bild.className = 'mesh-vorschau';
        bild.loading = 'lazy';
        bild.alt = eintrag.original || eintrag.datei;
        bild.title = eintrag.original || eintrag.datei;
        bild.src = this.seite.fotoAdresse(eintrag.datei);
        karte.append(bild, this._rolle(eintrag, karte), this._gewicht(eintrag), this._platz(eintrag, index, gesamt),
                     this._tausch(eintrag));
        return karte;
    }

    _rolle(eintrag, karte) {
        const rolle = document.createElement('select');
        rolle.className = 'viewer-select mesh-rollenwahl';
        for (const opt of this.seite.katalog.rollen) {
            const option = document.createElement('option');
            option.value = opt.wert;
            option.textContent = opt.text;
            option.selected = opt.wert === eintrag.rolle;
            rolle.appendChild(option);
        }
        rolle.addEventListener('change', () => this.rolleSetzen(eintrag, rolle.value, karte));
        return rolle;
    }

    _gewicht(eintrag) {
        const zeile = document.createElement('div');
        zeile.className = 'mesh-gewichtzeile';
        const regler = document.createElement('input');
        regler.type = 'range';
        regler.min = '0';
        regler.max = '100';
        regler.value = String(eintrag.gewicht ?? 100);
        regler.title = 'Gewicht dieses Fotos in der Note der Iterationen (0 = zählt nicht)';
        const wert = document.createElement('span');
        wert.className = 'mesh-gewichtwert';
        wert.textContent = `${regler.value} %`;
        regler.addEventListener('input', () => {
            wert.textContent = `${regler.value} %`;
            this.gewichtSetzen(eintrag, Number(regler.value));
        });
        zeile.append(regler, wert);
        return zeile;
    }

    _platz(eintrag, index, gesamt) {
        const zeile = document.createElement('label');
        zeile.className = 'mesh-indexzeile';
        zeile.append('Platz ');
        const feld = document.createElement('input');
        feld.type = 'number';
        feld.className = 'viewer-eingabe mesh-indexfeld';
        feld.min = '1';
        feld.max = String(gesamt);
        feld.value = String(index + 1);
        feld.title = 'Platz in der Reihenfolge — Platz 1 ist die Vorlage in der Übersicht';
        feld.addEventListener('change', () => this.reihenfolgeSetzen(eintrag.datei, Number(feld.value)));
        zeile.appendChild(feld);
        return zeile;
    }

    /** „Ersetzen" und „Entfernen" je Foto — auch während eines Laufs bedienbar (Edgar, 29.09.2026:
     *  „die sollen nicht gesperrt sein beim Lauf"). */
    _tausch(eintrag) {
        const zeile = document.createElement('div');
        zeile.className = 'mesh-tauschzeile';
        const ersetzen = document.createElement('button');
        ersetzen.type = 'button';
        ersetzen.className = 'btn btn-secondary btn-sm';
        ersetzen.title = 'Dieses Foto durch ein anderes ersetzen — Rolle, Gewicht und Platz bleiben';
        ersetzen.innerHTML = '<i class="fas fa-right-left"></i> <span>Ersetzen</span>';
        ersetzen.addEventListener('click', () => this.ersetzen(eintrag.datei, ersetzen));
        const entfernen = document.createElement('button');
        entfernen.type = 'button';
        entfernen.className = 'btn btn-secondary btn-sm';
        entfernen.title = 'Dieses Foto aus dem Auftrag entfernen';
        entfernen.innerHTML = '<i class="fas fa-trash"></i>';
        entfernen.addEventListener('click', () => this.entfernen(eintrag.datei, entfernen));
        zeile.append(ersetzen, entfernen);
        return zeile;
    }

    // ---------------------------------------------- Rolle, Gewicht, Platz

    async rolleSetzen(eintrag, rolle, karte) {
        const vorher = eintrag.rolle;
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse(`rolle/${encodeURIComponent(eintrag.datei)}/`), { rolle });
            eintrag.rolle = antwort.bild.rolle;
            karte.classList.toggle('haarengine-foto-aus', eintrag.rolle === 'aus');
        } catch (fehler) {
            eintrag.rolle = vorher;
            window.alert(`Rolle konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
            this.neuZeichnen();
        }
    }

    /** Gewicht sofort lokal übernehmen, an den Server erst `GEWICHT_SPEICHERN_MS` nach der letzten Bewegung — ein
     *  Regler, der bei jedem Pixel eine Anfrage schickt, würde den Server fluten. */
    gewichtSetzen(eintrag, gewicht) {
        eintrag.gewicht = gewicht;
        clearTimeout(this._uhren[eintrag.datei]);
        this._uhren[eintrag.datei] = setTimeout(async () => {
            try {
                await Serverabruf.senden(this.seite.adresse(`gewicht/${encodeURIComponent(eintrag.datei)}/`), { gewicht });
            } catch (fehler) {
                window.alert(`Gewicht konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
            }
        }, Haarenginefotos.GEWICHT_SPEICHERN_MS);
    }

    async reihenfolgeSetzen(datei, index) {
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('reihenfolge/'), { datei, index });
            if (antwort.bilder) this.seite.zustand.bilder = antwort.bilder;
        } catch (fehler) {
            window.alert(`Reihenfolge konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
        }
        this.neuZeichnen();
    }

    // -------------------------------------- hinzufügen, ersetzen, entfernen

    async hinzufuegen(knopf) {
        const dateien = await Meshfotowahl.oeffnen({ mehrfach: true, titel: 'Fotos hinzufügen', uebernehmen: 'Hinzufügen' });
        if (!dateien.length) return;
        const daten = new FormData();
        dateien.forEach(datei => daten.append('bilder', datei, datei.name));
        await this._senden(knopf, this.seite.adresse('fotos/'), daten, 'Lädt hoch …');
    }

    async ersetzen(datei, knopf) {
        const gewaehlt = await Meshfotowahl.oeffnen({ mehrfach: false, titel: `„${datei}“ ersetzen durch`, uebernehmen: 'Ersetzen' });
        if (!gewaehlt.length) return;
        const daten = new FormData();
        daten.append('bild', gewaehlt[0], gewaehlt[0].name);
        await this._senden(knopf, this.seite.adresse(`foto/${encodeURIComponent(datei)}/ersetzen/`), daten, 'Ersetzt …');
    }

    async entfernen(datei, knopf) {
        if (!window.confirm(`Foto „${datei}“ aus dem Auftrag entfernen?`)) return;
        await this._senden(knopf, this.seite.adresse(`foto/${encodeURIComponent(datei)}/loeschen/`), null, 'Entfernt …');
    }

    /** Gemeinsamer Weg der drei Fotoänderungen: senden, Liste übernehmen, neu zeichnen. */
    async _senden(knopf, adresse, daten, text) {
        const beschriftung = knopf.querySelector('span');
        const vorher = beschriftung ? beschriftung.textContent : null;
        try {
            await Knopfsperre.waehrend(knopf, async () => {
                const antwort = daten ? await Serverabruf.formular(adresse, daten) : await Serverabruf.senden(adresse, {});
                if (antwort.error) throw new Error(antwort.error);
                this.seite.zustand.bilder = antwort.bilder;
            }, text);
        } catch (fehler) {
            window.alert(fehler.daten?.error || fehler.message);
            return;
        }
        // `Knopfsperre` lässt den Knopf nach Erfolg gesperrt und beschriftet („Lädt hoch …"). Die Knöpfe je Foto
        // entstehen beim Neuzeichnen neu; „Fotos hinzufügen" bleibt bestehen und bekommt seinen Text zurück
        // (frei gibt ihn `zeigen`, je nach Lauf).
        if (knopf.isConnected && beschriftung && vorher !== null) beschriftung.textContent = vorher;
        this.neuZeichnen();
    }
}
