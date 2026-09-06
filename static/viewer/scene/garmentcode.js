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

class GarmentcodeReiter {
    constructor() {
        this.laeuft = false;
        this.zustandDa = false;
        this.drapierbereit = false;
        /** Für welche Figur die Maße im Panel stehen. */
        this.masseFuer = null;
    }

    starten() {
        const reiter = document.querySelector('.panel-tab[data-tab="garmentcode"]');
        if (!reiter) return;
        reiter.addEventListener('click', () => this.oeffnen());

        const knopf = document.getElementById('gc-erzeugen');
        if (knopf) knopf.addEventListener('click', () => this.bauen());
    }

    /** Beim Öffnen: Figur prüfen, Zustand und Maße nebenher holen. */
    oeffnen() {
        const figur = this.figur();
        const leer = document.getElementById('gc-empty');
        const inhalt = document.getElementById('gc-content');
        if (leer) leer.classList.toggle('hb-versteckt', !!figur);
        if (inhalt) inhalt.classList.toggle('hb-versteckt', !figur);
        if (!figur) return;

        // Beide Abrufe laufen nebenher — der Nutzer wartet auf keinen davon.
        this.zustandLaden();
        if (this.masseFuer !== figur.id) this.masseLaden();
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
        } catch (fehler) {
            feld.textContent = `Status nicht abrufbar: ${fehler.message || fehler}`;
        }
    }

    /**
     * Gezeigt werden die Parametersätze aus `design_params` — das sind die,
     * die `MetaGarment` direkt versteht. Die Programmnamen (`tee`, `pants`,
     * …) sind Bausteine, kein fertiger Entwurf, und liefen ins Leere.
     */
    vorlagenFuellen(entwuerfe) {
        const auswahl = document.getElementById('gc-vorlage');
        if (!auswahl || !entwuerfe.length) return;
        const beschriftung = { 't-shirt': 'T-Shirt', 'default': 'Grundentwurf' };
        auswahl.innerHTML = '';
        for (const name of entwuerfe) {
            const eintrag = document.createElement('option');
            eintrag.value = name;
            eintrag.textContent = beschriftung[name] || name;
            auswahl.appendChild(eintrag);
        }
    }

    // ---------------------------------------------------------------- bauen

    async bauen() {
        if (this.laeuft) return;
        const figur = this.figur();
        const meldung = document.getElementById('gc-meldung');
        if (!figur) {
            meldung.textContent = 'Keine Figur gewählt.';
            return;
        }
        const knopf = document.getElementById('gc-erzeugen');
        const vorschau = document.getElementById('gc-vorschau');

        this.laeuft = true;
        knopf.disabled = true;
        meldung.textContent = 'Schnitt wird für diese Figur konstruiert …';
        vorschau.innerHTML = '';

        try {
            const daten = this.figurdaten(figur);
            daten.append('vorlage', document.getElementById('gc-vorlage').value);
            const ergebnis = await Serverabruf.json('/api/garmentcode/erzeugen/', {
                method: 'POST', body: daten,
            });
            if (ergebnis.fehler) {
                meldung.textContent = `Fehlgeschlagen: ${ergebnis.fehler}`;
                return;
            }
            const warnung = ergebnis.selbstdurchdringend
                ? ' — Achtung: Schnitt durchdringt sich selbst' : '';
            meldung.textContent = `Schnitt fertig: ${ergebnis.name}${warnung}`;
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
        } catch (fehler) {
            meldung.textContent = `Fehler: ${fehler.message || fehler}`;
        } finally {
            this.laeuft = false;
            knopf.disabled = false;
        }
    }

    /** Das Schnittmuster als 3D-Netz auf den Körper legen. */
    async drapieren(figur, spezifikation, meldung) {
        meldung.textContent = 'Schnitt fertig — Stoff wird drapiert …';
        // Die Figurdaten müssen mit: aus ihnen kommen die Knochengewichte,
        // mit denen das drapierte Netz animierbar wird.
        const daten = this.figurdaten(figur);
        daten.append('spezifikation', spezifikation);
        try {
            const netz = await Serverabruf.json('/api/garmentcode/drapieren/', {
                method: 'POST', body: daten,
            });
            if (netz.fehler) {
                meldung.textContent = `Schnitt fertig, Drapierung scheiterte: `
                    + `${netz.fehler}`;
                return;
            }
            const rig = netz.rig
                ? `, angezogen (${netz.rig_ohne_gewicht} Punkte ohne Gewicht)`
                : ', ohne Rig';
            meldung.textContent = `Fertig in 3D: ${netz.punkte} Punkte, `
                + `${netz.dreiecke} Dreiecke in ${netz.dauer_s} s${rig}`;
        } catch (fehler) {
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
            const antwort = await Serverabruf.json('/api/garmentcode/masse/', {
                method: 'POST', body: this.figurdaten(figur),
            });
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
