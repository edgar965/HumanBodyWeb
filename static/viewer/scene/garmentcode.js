/**
 * GarmentCode-Reiter — Kleidung aus Körpermaßen konstruieren.
 *
 * Der Gegenentwurf zum Assets-Reiter: dort wird ein fertiges Netz an den
 * Körper angepasst und sitzt nicht (gemessen am 06.09.2026: 14,3 % der
 * `.mhclo`-Anker fallen auf EINEN Körpervertex, Shrinkwrap liefert bis 36 %
 * Vertices im Körper). Hier wird der Schnitt aus Maßen gebaut — wo nichts
 * angepasst wird, kann nichts verrutschen.
 *
 * BEDIENUNG (Edgar, 06.09.2026: „T-Shirt auswählen, bauen"): Ein Knopf. Die
 * Maße kommen aus der gewählten Figur — mit ihren Reglerwerten, nicht aus dem
 * Grundkörper — und werden im Hintergrund geholt, während der Nutzer schon
 * das Kleidungsstück wählt. Sie sind Anzeige, keine Eingabe.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { state } from './state.js';
import { garmentcodeRegler } from './garmentcode_regler.js';
import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';

class GarmentcodeReiter {
    constructor() {
        this.laeuft = false;
        this.zustandDa = false;
        this.drapierbereit = false;
        this.aufgeklappt = false;
        /** Für welche Figur die Maße im Panel stehen. */
        this.masseFuer = null;
    }

    /**
     * Einhängen — notfalls erst, wenn das DOM steht.
     *
     * `boot.js` importiert dieses Modul; je nachdem, wann das geschieht,
     * gibt es den Reiter noch nicht. Ein `querySelector` liefert dann null,
     * und ohne diese Weiche bräche `starten()` still ab: kein Klick-Handler,
     * kein Zustand, ein Reiter, in dem nichts passiert.
     */
    starten() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.einhaengen(),
                                      { once: true });
        } else {
            this.einhaengen();
        }
    }

    einhaengen() {
        const reiter = document.querySelector('.panel-tab[data-tab="garmentcode"]');
        if (!reiter) return;
        reiter.addEventListener('click', () => this.oeffnen());

        const knopf = document.getElementById('gc-erzeugen');
        if (knopf) knopf.addEventListener('click', () => this.bauen());

        // Ein anderes Kleidungsstück hat andere Einstellungen — eine Hose
        // hat keinen Kragen. Deshalb bei jedem Wechsel neu holen.
        const auswahl = document.getElementById('gc-vorlage');
        if (auswahl) {
            auswahl.addEventListener('change',
                () => garmentcodeRegler.laden(auswahl.value));
        }

        // Vorlagen und Regler brauchen keine Figur — sofort holen, damit im
        // Reiter etwas steht, bevor jemand ihn anklickt.
        this.zustandLaden();
    }

    /**
     * Beim Öffnen: Inhalt zeigen, Maße nebenher holen.
     *
     * Der Inhalt bleibt IMMER sichtbar — Vorlagen und Einstellungen kann man
     * ansehen, ohne eine Figur zu wählen. Ohne Figur ist nur der Bau-Knopf
     * gesperrt, mit Hinweis daneben. (Vorher war der ganze Reiter leer,
     * sobald `state.selectedCharacterId` nicht gesetzt war.)
     */
    oeffnen() {
        const figur = this.figur();
        const inhalt = document.getElementById('gc-content');
        if (inhalt) inhalt.classList.remove('hb-versteckt');
        // Den Knopf NICHT sperren: Ein gesperrter Knopf ohne Erklärung ist
        // das, was "tut nichts" heißt. Fehlt die Figur, sagt der Klick es.
        const hinweis = document.getElementById('gc-empty');
        if (hinweis) hinweis.classList.toggle('hb-versteckt', !!figur);

        this.aufklappen();
        this.zustandLaden();
        if (figur && this.masseFuer !== figur.id) this.masseLaden();
    }

    /**
     * Beim ERSTEN Öffnen die beiden wichtigen Abschnitte aufklappen.
     *
     * Alle `panel-section` starten mit `collapsed` — bei einem eingeführten
     * Reiter ist das richtig, bei einem neuen sieht man dann nur vier
     * Überschriften und hält den Reiter für leer. Danach entscheidet wieder
     * der Nutzer: Wer zuklappt, findet es zugeklappt wieder.
     */
    aufklappen() {
        if (this.aufgeklappt) return;
        this.aufgeklappt = true;
        for (const schluessel of ['gc_bauen', 'gc_regler']) {
            const bereich = document.querySelector(
                `#tab-garmentcode [data-panel-key="${schluessel}"]`);
            if (bereich) bereich.classList.remove('collapsed');
        }
    }

    /**
     * Die gewählte Figur aus der Szene. Ohne sie würde der Grundkörper
     * gemessen — der Schnitt passte dann zu einer Figur, die niemand sieht.
     */
    figur() {
        const id = state.selectedCharacterId || state.currentPropsCharId;
        if (!id || !state.characters) return null;
        const inst = state.characters.get(id);
        return inst ? { id, inst } : null;
    }

    /** Geschlecht, Bauart und Morphs der Figur als Formulardaten. */
    figurdaten(figur) {
        const inst = figur.inst;
        const daten = new FormData();
        const bauart = inst.bodyType || inst.body_type || '';
        daten.append('geschlecht',
            bauart.toLowerCase().startsWith('m') ? 'male'
                : (inst.gender || 'female'));
        if (bauart) daten.append('bauart', bauart);
        daten.append('morphs', JSON.stringify(inst.morphs || {}));
        return daten;
    }

    // ------------------------------------------------------------- Zustand

    async zustandLaden() {
        if (this.zustandDa) return;
        const feld = document.getElementById('gc-status');
        try {
            const zustand = await Serverabruf.json('/api/garmentcode/zustand/');
            this.zustandDa = true;
            if (!zustand.vorhanden) {
                feld.textContent = zustand.hinweis || 'GarmentCode fehlt.';
                return;
            }
            this.drapierbereit = !!zustand.drapierbereit;
            const dreid = this.drapierbereit
                ? '3D-Drapierung bereit'
                : 'nur Schnittmuster (Simulation nicht eingerichtet)';
            feld.textContent = `Bereit — ${zustand.entwuerfe.length} Vorlagen, ${dreid}.`;
            this.vorlagenFuellen(zustand.entwuerfe);
            const auswahl = document.getElementById('gc-vorlage');
            if (auswahl && auswahl.value) garmentcodeRegler.laden(auswahl.value);
        } catch (fehler) {
            feld.textContent = `Status nicht abrufbar: ${fehler.message || fehler}`;
        }
    }

    /**
     * Die Liste kommt aus `GarmentCode/katalog.py` — fertige Kombinationen
     * der drei Bausteine (Oberteil, Bund, Unterteil), unter deutschen Namen.
     * Die zwei Dateien in `design_params` waren nie die Auswahl, sondern nur
     * zwei Beispiele.
     */
    vorlagenFuellen(entwuerfe) {
        const auswahl = document.getElementById('gc-vorlage');
        if (!auswahl || !entwuerfe.length) return;
        auswahl.innerHTML = '';
        for (const stueck of entwuerfe) {
            const eintrag = document.createElement('option');
            eintrag.value = stueck.name;
            eintrag.textContent = stueck.titel || stueck.name;
            auswahl.appendChild(eintrag);
        }
    }

    // ---------------------------------------------------------------- bauen

    async bauen() {
        if (this.laeuft) return;
        const meldung = document.getElementById('gc-meldung');
        const figur = this.figur();
        if (!figur) {
            meldung.textContent = 'Keine Figur gewählt — bitte links in der '
                + 'Charakterliste eine anklicken. Der Schnitt wird aus ihren '
                + 'Maßen gebaut.';
            return;
        }
        const knopf = document.getElementById('gc-erzeugen');
        const vorschau = document.getElementById('gc-vorschau');

        this.laeuft = true;
        knopf.disabled = true;
        meldung.textContent = '';
        vorschau.innerHTML = '';

        // Die Schritte im Voraus zeigen — dann weiß der Nutzer, was kommt
        // und dass die Drapierung der lange Teil ist.
        const schritte = [{ schluessel: 'schnitt', titel: 'Schnitt konstruieren' }];
        if (this.drapierbereit) {
            schritte.push({ schluessel: 'drape', titel: 'Stoff drapieren (dauert)' });
            schritte.push({ schluessel: 'rig', titel: 'Anziehen (Knochengewichte)' });
        }
        garmentcodeFortschritt.starten(schritte);
        garmentcodeFortschritt.laeuft('schnitt');

        try {
            const daten = this.figurdaten(figur);
            daten.append('vorlage', document.getElementById('gc-vorlage').value);
            daten.append('regler', garmentcodeRegler.alsJson());
            const ergebnis = await Serverabruf.formular(
                '/api/garmentcode/erzeugen/', daten);
            if (ergebnis.fehler) {
                garmentcodeFortschritt.gescheitert('schnitt', 'Fehler');
                meldung.textContent = `Fehlgeschlagen: ${ergebnis.fehler}`;
                return;
            }
            garmentcodeFortschritt.fertig('schnitt', ergebnis.name || 'fertig');
            const warnung = ergebnis.selbstdurchdringend
                ? ' — Achtung: Schnitt durchdringt sich selbst' : '';
            const eigene = garmentcodeRegler.anzahl;
            const zusatz = eigene ? ` (${eigene} eigene Einstellungen)` : '';
            meldung.textContent =
                `Schnitt fertig: ${ergebnis.name}${zusatz}${warnung}`;
            if (ergebnis.vorschau) {
                const bild = document.createElement('img');
                bild.src = ergebnis.vorschau;
                bild.alt = 'Schnittmuster';
                bild.style.maxWidth = '100%';
                vorschau.appendChild(bild);
            }
            // Zweiter Schritt: der Stoff fällt auf den Körper. Das dauert
            // deutlich länger als der Schnitt, deshalb erst danach und mit
            // eigener Meldung — der Nutzer sieht das Schnittmuster sofort.
            if (this.drapierbereit && ergebnis.spezifikation) {
                await this.drapieren(figur, ergebnis.spezifikation, meldung);
            }
            garmentcodeFortschritt.beenden();
        } catch (fehler) {
            garmentcodeFortschritt.gescheitert('schnitt',
                                               String(fehler.message || fehler));
            meldung.textContent = `Fehler: ${fehler.message || fehler}`;
        } finally {
            this.laeuft = false;
            knopf.disabled = false;
            garmentcodeFortschritt.beenden();
        }
    }

    /** Das Schnittmuster als 3D-Netz auf den Körper legen. */
    async drapieren(figur, spezifikation, meldung) {
        garmentcodeFortschritt.laeuft('drape');
        // Die Figurdaten müssen mit: aus ihnen kommen die Knochengewichte,
        // mit denen das drapierte Netz animierbar wird.
        const daten = this.figurdaten(figur);
        daten.append('spezifikation', spezifikation);
        try {
            const netz = await Serverabruf.formular(
                '/api/garmentcode/drapieren/', daten);
            if (netz.fehler) {
                garmentcodeFortschritt.gescheitert('drape', 'Fehler');
                meldung.textContent = `Schnitt fertig, Drapierung scheiterte: `
                    + `${netz.fehler}`;
                return;
            }
            garmentcodeFortschritt.fertig('drape',
                                          `${netz.punkte} Punkte, ${netz.dauer_s} s`);
            garmentcodeFortschritt.fertig('rig', netz.rig
                ? `${netz.rig_ohne_gewicht} ohne Gewicht` : 'kein Rig');
            const rig = netz.rig
                ? `, angezogen (${netz.rig_ohne_gewicht} Punkte ohne Gewicht)`
                : ', ohne Rig';
            meldung.textContent = `Fertig in 3D: ${netz.punkte} Punkte, `
                + `${netz.dreiecke} Dreiecke in ${netz.dauer_s} s${rig}`;
        } catch (fehler) {
            garmentcodeFortschritt.gescheitert('drape',
                                               String(fehler.message || fehler));
            meldung.textContent = `Drapierung fehlgeschlagen: `
                + `${fehler.message || fehler}`;
        }
    }

    // --------------------------------------------------------------- Maße

    async masseLaden() {
        const figur = this.figur();
        const liste = document.getElementById('gc-masse-liste');
        if (!figur || !liste) return;
        liste.innerHTML = '<div class="hb-hinweis">Figur wird vermessen …</div>';
        try {
            const antwort = await Serverabruf.formular(
                '/api/garmentcode/masse/', this.figurdaten(figur));
            this.masseFuer = figur.id;
            liste.innerHTML = '';
            for (const [name, wert] of Object.entries(antwort.masse)) {
                const zeile = document.createElement('div');
                zeile.className = 'slider-row';
                const woher = antwort.herkunft[name] === 'gemessen' ? '•' : '°';
                zeile.innerHTML = `<label>${woher} ${name}</label>`
                    + `<span class="slider-val">${wert}</span>`;
                liste.appendChild(zeile);
            }
        } catch (fehler) {
            liste.innerHTML = '<div class="hb-hinweis">Nicht abrufbar: '
                + `${fehler.message || fehler}</div>`;
        }
    }
}

export const garmentcodeReiter = new GarmentcodeReiter();
garmentcodeReiter.starten();
