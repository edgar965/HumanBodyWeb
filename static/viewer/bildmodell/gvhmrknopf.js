import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Gvhmrfenster } from './gvhmrfenster.js';

/**
 * Gvhmrknopf — „SMPL (GVHMR)" an jeder Bildzeile und Bildkachel.
 *
 * Edgar (20.09.2026): „Die SMPL erkennung aus GVHMR ist doch ganz gut. Mach
 * einen extra button dafür in jeder Zeile mit der ich ein SMPL mit GVHMR
 * erzeuge und ansehen kann, für jedes Bild!" — „ich brauch kein ‚Bild neu'
 * sondern eines um eine GVHMR erkennung zu machen, mit ausgabe fenster dazu!"
 *
 * Ein Klick öffnet das Ausgabefenster (`Gvhmrfenster`, EINES je Seite — die
 * Zeilen der Proportionentabelle und die Kacheln unten teilen es) und startet
 * darin den Lauf, wenn für das Bild noch kein Ergebnis liegt: Arbeitsprozess
 * mit dem Einzelschritt `gvhmr` (`starten/` mit `schritte: ['gvhmr'], bild`,
 * `Bildmodellgvhmr`); danach rechnet derselbe Lauf das Modell neu aus GVHMR
 * (`Bildmodelllauf.NACH_GVHMR`, Körperschätzer und Weg stellt `Bildmodellstart`
 * um — Edgar, 20.09.2026: „Berechne auch die immer neu, mit dem GVHMR lauf").
 * Liegt ein Netz vor, zeigt das Fenster es sofort (Netz, Rig, Zahlen); „Neu
 * rechnen" steht im Fenster. `ansehen(datei)` legt das Netz
 * zusätzlich oben in die 3D-Ansicht der Seite (`Ansicht3d.gvhmrSetzen`).
 *
 * `ART`/`FENSTER` machen den Knopf für einen zweiten Einzelschritt nutzbar: `Flameknopf`
 * („Kopf (FLAME)" an Kopfbildern, 20.09.2026) — `passt(b)` sagt, an welchen Bildern der
 * Knopf steht (GVHMR: Körperbilder; ein Kopfausschnitt schätzt einen Körper, den GVHMR
 * nicht sieht).
 */
export class Gvhmrknopf {

    static _fenster = null;
    static FENSTER = Gvhmrfenster;
    static ART = {
        schritt: 'gvhmr', feld: 'gvhmr', endpunkt: 'gvhmr3d', name: 'GVHMR',
        ansehen: 'SMPL ansehen', rechnen: 'SMPL (GVHMR)',
        titelAnsehen: 'Ausgabefenster: SMPL-X-Netz und Rig aus GVHMR, Zahlen, „Neu rechnen"',
        titelRechnen: 'GVHMR für dieses Bild rechnen (30–70 s), danach das Modell neu aus GVHMR '
            + '(Vorher/Nachher-Bilder) — Ausgabefenster mit Netz, Rig und Zahlen',
    };

    constructor(auftrag) {
        this.auftrag = auftrag;
        this.art = this.constructor.ART;
    }

    /** Das eine Fenster der Seite (je Art eines). */
    get fenster() {
        const K = this.constructor;
        if (!Object.prototype.hasOwnProperty.call(K, '_fenster') || !K._fenster) K._fenster = new K.FENSTER(this.auftrag, this);
        return K._fenster;
    }

    /** Steht der Knopf an diesem Bild? GVHMR: Körperbilder (kein Video, kein Kopfbild). */
    static passt(b) { return !b.video && !Gvhmrknopf.kopfbild(b); }

    /** Läuft gerade GVHMR für dieses Bild? */
    static laeuft(zustand, datei) {
        if (zustand.status !== 'laeuft' || zustand.schritt !== this.ART.schritt) return false;
        const bild = (zustand.optionen || {}).gvhmr_bild;
        return Array.isArray(bild) ? bild.includes(datei) : bild === datei;
    }

    /** Kurztext zum Stand des Bildes — für die Tabellenzelle. `null` ohne Ergebnis. */
    static stand(b) {
        const g = b[this.ART.feld];
        if (!g) return null;
        // `sort` als deutsche Zahl — die djangoBase-Sortierung liest den Punkt als Tausenderpunkt.
        if (g.fehler) return { text: `Fehler: ${g.fehler}`, sort: '-1' };
        if (g.netz) {
            const was = g.hoehe_m ? g.hoehe_m.toFixed(2) + ' m' : g.punkte ? `${g.punkte.toLocaleString('de-DE')} Punkte` : 'Netz';
            return { text: `${was} · ${g.dauer_s ?? '?'} s`, sort: (g.hoehe_m || g.dauer_s || 0).toFixed(3).replace('.', ',') };
        }
        return null;
    }

    /** Zählt das GVHMR-Ergebnis des Bildes zur Form? Häkchen entscheidet; ohne Häkchen nur
     *  Körper-Hauptbilder (ein Kopfausschnitt schätzt einen Körper, den GVHMR nicht sieht). */
    static verwendet(b) {
        if (!b.gvhmr || !b.gvhmr.netz || Gvhmrknopf.kopfbild(b)) return false;
        if (b.gvhmr_an !== undefined && b.gvhmr_an !== null) return !!b.gvhmr_an;
        return b.kategorie === 'koerper';
    }

    /** Das Häkchen „Verwenden" für die Tabellenspalte — `null` ohne Ergebnis. */
    verwendenFeld(b) {
        if (!b.gvhmr || !b.gvhmr.netz || Gvhmrknopf.kopfbild(b)) return null;
        const feld = document.createElement('label');
        feld.className = 'bildmodell-gvhmrverwenden';
        feld.title = 'Dieses GVHMR-Ergebnis in die Form übernehmen (Schätzer „GVHMR" im Lauf)';
        const kasten = document.createElement('input');
        kasten.type = 'checkbox';
        kasten.checked = Gvhmrknopf.verwendet(b);
        kasten.addEventListener('change', async () => {
            try { await this.auftrag.bildStellen(b.datei, { gvhmr_an: kasten.checked }); }
            catch (fehler) { kasten.checked = !kasten.checked; window.alert(fehler.message); }
        });
        feld.append(kasten, document.createTextNode(' Verwenden'));
        return feld;
    }

    /** Kopfbild? GVHMR schätzt einen ganzen Körper und erfindet auf einem Kopfausschnitt einen
     *  (Damira: 1,38 m, Rumpf vor der Kamera) — kein Knopf, kein Bild, der Kopf kommt aus FLAME. */
    static kopfbild(b) { return b.kategorie === 'kopf'; }

    /** Der Knopf für den Eintrag `b` — keiner für ein Drehvideo (GVHMR läuft dort in der Schätzung)
     *  und keiner für ein Kopfbild. */
    element(b) {
        const K = this.constructor;
        if (!K.passt(b)) return null;
        const z = this.auftrag.zustand || {};
        const g = b[this.art.feld] || {};
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-sm bildmodell-gvhmr ' + (g.netz ? 'btn-secondary' : 'btn-primary');
        if (K.laeuft(z, b.datei)) {
            knopf.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${this.art.name} läuft …`;
            knopf.title = 'Läuft — Klick öffnet das Ausgabefenster mit dem Fortschritt';
        } else if (g.netz) {
            knopf.innerHTML = `<i class="fas fa-cube"></i> ${this.art.ansehen}`;
            knopf.title = this.art.titelAnsehen;
        } else {
            knopf.innerHTML = `<i class="fas fa-cube"></i> ${this.art.rechnen}`;
            knopf.title = this.art.titelRechnen;
            knopf.disabled = z.status === 'laeuft' && !K.laeuft(z, b.datei);
        }
        knopf.addEventListener('click', () => this.fenster.oeffnen(b.datei, false));
        return knopf;
    }

    /** Den Einzelschritt starten; `neu` verwirft ein vorhandenes Ergebnis. */
    async starten(datei, neu) {
        const z = this.auftrag.zustand || {};
        // Sofort als „läuft" zeichnen — der Server bestätigt es mit der nächsten Nachfrage.
        z.optionen = { ...(z.optionen || {}), gvhmr_bild: datei };
        try {
            await this.auftrag.starten(undefined, this.art.schritt, (z.optionen || {}).fest || {}, null,
                [this.art.schritt], { bild: datei, neu: !!neu });
        } catch (fehler) {
            window.alert(`${this.art.name} nicht gestartet: ${fehler.message}`);
        }
    }

    /** Das Netz oben in der 3D-Ansicht der Seite zeigen. */
    async ansehen(datei) {
        const ansicht = window.__bildmodell?.ansicht;
        if (!ansicht || !ansicht.gvhmrSetzen) { window.alert('Keine 3D-Ansicht auf dieser Seite.'); return; }
        try {
            const antwort = await Serverabruf.json(this.auftrag.adresse(`${this.art.endpunkt}/${encodeURIComponent(datei)}/`));
            if (!antwort || antwort.error) throw new Error((antwort || {}).error || 'keine Antwort');
            ansicht.gvhmrSetzen(antwort);
            this.fenster.schliessen();
            document.getElementById('ansicht3d')?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        } catch (fehler) {
            window.alert(`SMPL nicht geladen: ${fehler.message}`);
        }
    }
}
