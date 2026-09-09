import { Serverabruf } from '/static/djangobase/js/serverabruf.js';
import { garmentcodeRegler } from './garmentcode_regler.js';

/**
 * Vorbilder — die Bibliotheksstücke als Knöpfe unter den Voreinstellungen.
 *
 * AUFTRAG (Edgar, 09.09.2026): „Mach doch stattdessen neue buttons unter den
 * Checkboxen mit «Eng anliegend», «weit fallend» mit den Namen der Garment
 * Fit items. Bei Klick darauf werden die eingestellt und später gebaut?"
 *
 * ZWEI ANLÄUFE DAVOR WAREN FALSCH, und beide aus demselben Grund: Sie machten
 * aus einem Bibliotheksstück etwas Eigenes — erst einen Knopf im Assets-Reiter,
 * der in den GarmentCode-Reiter sprang („das UI verheddert sich"), dann einen
 * zweiten Eintrag im Auswahlfeld. Ein Bibliotheksstück ist aber nichts
 * Eigenes: Es ist ein Satz Reglerwerte mit einem Namen, also dasselbe wie
 * „Eng anliegend". Deshalb steht es an derselben Stelle.
 *
 * NICHTS WIRD GEMERKT. `garmentcodeRegler.mehrereSetzen` würde über
 * `merken()` nach `garmentcode/werte:<vorlage>` in den localStorage
 * schreiben — gemessen wurde daraus ein „Sommerkleid", das sich fortan mit
 * den Maßen eines Assets öffnete („baut mal das alte Sommerkleid, mal das
 * neue??"). Ein Vorbild ist eine ABLEITUNG, keine Einstellung des Nutzers.
 * Gesetzt wird deshalb wie in `Garmentcodegedaechtnis.anwenden`: Wert und
 * Schieber, sonst nichts.
 */
export class GarmentcodeVorbilder {

    static ADRESSE = '/api/garmentcode/vorbilder/';

    /** Für welches Kleidungsstück die Knöpfe gerade stehen. */
    static fuerVorlage = null;

    /**
     * Am Auswahlfeld hören und beim Start einmal zeichnen.
     *
     * Ein DELEGIERTER HÖRER am Feld, keine Bindung an den Reiteraufbau: Die
     * Regler entstehen erst, wenn der Server sie liefert, und werden bei
     * jedem Wechsel neu gebaut. Wer sich an deren Aufbau hängt, verpasst den
     * ersten Durchlauf oder doppelt sich beim zweiten.
     */
    static verdrahten() {
        const auswahl = document.getElementById('gc-vorlage');
        if (!auswahl) return false;
        auswahl.addEventListener('change',
                                 () => GarmentcodeVorbilder.laden(auswahl.value));
        if (auswahl.value) GarmentcodeVorbilder.laden(auswahl.value);
        return true;
    }

    /** Die Vorbilder dieses Kleidungsstücks holen und zeichnen. */
    static async laden(vorlage) {
        const ziel = document.getElementById('gc-vorbilder');
        if (!ziel || !vorlage) return 0;
        if (GarmentcodeVorbilder.fuerVorlage === vorlage) return 0;
        GarmentcodeVorbilder.fuerVorlage = vorlage;
        ziel.innerHTML = '<div class="hb-hinweis">Vorbilder werden geholt …</div>';
        let antwort;
        try {
            antwort = await Serverabruf.json(
                `${GarmentcodeVorbilder.ADRESSE}?vorlage=${encodeURIComponent(vorlage)}`);
        } catch (fehler) {
            ziel.innerHTML = '<div class="hb-hinweis">Vorbilder nicht '
                + `abrufbar: ${fehler.message || fehler}</div>`;
            return 0;
        }
        return GarmentcodeVorbilder._zeichnen(ziel, antwort);
    }

    static _zeichnen(ziel, antwort) {
        const liste = antwort.vorbilder || [];
        ziel.innerHTML = '';
        if (!liste.length) {
            // Kein Vorbild ist hier die Regel, nicht der Ausnahmefall: Für
            // vier der fünfzehn Kleidungsstücke wurde keines gedeutet. Das
            // zu sagen ist besser als ein leerer Kasten, der wie ein
            // Ladefehler aussieht.
            ziel.innerHTML = '<div class="hb-hinweis">'
                + (antwort.gesamt
                    ? 'Für dieses Kleidungsstück gibt es kein Vorbild aus der '
                      + 'Kleiderbibliothek.'
                    : 'Noch keine Vorbilder vermessen — '
                      + '<code>werkzeug/vorbilder_messen.py</code> starten.')
                + '</div>';
            return 0;
        }
        // AUFKLAPPBAR SEIT 09.09.2026 (Edgar: „Der Bereich «Nach Vorbild der
        // Kleiderbibliothek» soll «Kleiderbibliothek» heissen und auf-
        // zuklappbar werden"). Beim T-Shirt sind es 29 Knoepfe — offen
        // schieben sie alles darunter aus dem Bild.
        const kasten = document.createElement('details');
        kasten.appendChild(GarmentcodeVorbilder._ueberschrift(liste.length));
        // OHNE eigene Klasse: `hb-knopfreihe` gab es nicht — eine erfundene
        // Klasse wirkt nicht und faellt niemandem auf. Die Knoepfe stapeln
        // sich untereinander, und das ist bei Namen wie „Dress Strapless
        // Ruffle Top" ohnehin besser lesbar als eine Reihe.
        const reihe = document.createElement('div');
        for (const vorbild of liste) {
            reihe.appendChild(GarmentcodeVorbilder._knopf(vorbild));
        }
        kasten.appendChild(reihe);
        ziel.appendChild(kasten);
        return liste.length;
    }

    static _ueberschrift(anzahl) {
        const kopf = document.createElement('summary');
        kopf.className = 'hb-font-size-0-72rem';
        kopf.textContent = `Kleiderbibliothek (${anzahl})`;
        kopf.title = 'Bibliotheksstücke als Vorlage. Ein Klick stellt die '
            + 'Regler auf die gemessenen Maße dieses Stücks und übernimmt '
            + 'Farbe und Glanz; gebaut wird danach wie immer mit „Bauen '
            + '2D + 3D". Übernommen wird die Silhouette — Länge, Weite, '
            + 'Ärmel —, nicht Muster und Rüschen.';
        return kopf;
    }

    /**
     * Ein Knopf je Vorbild. Der Hinweis steht im `title` — dort nennt er die
     * gemessenen Zahlen, aus denen die Reglerwerte stammen.
     */
    static _knopf(vorbild) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        // `vorbild-knopf` richtet Bild und Name links aus — ein `<button>`
        // zentriert seinen Inhalt sonst, und die Bilder ständen dann je nach
        // Namenslänge auf verschiedenen Kanten.
        knopf.className = 'btn-toggle vorbild-knopf';
        knopf.title = vorbild.hinweis || '';
        knopf.dataset.schluessel = vorbild.schluessel;
        if (vorbild.bild) knopf.appendChild(GarmentcodeVorbilder._bild(vorbild));
        knopf.appendChild(document.createTextNode(vorbild.titel));
        knopf.addEventListener('click',
                               () => GarmentcodeVorbilder._anwenden(knopf, vorbild));
        return knopf;
    }

    /**
     * Das Vorschaubild des Assets — dasselbe, das die Asset-Liste zeigt.
     *
     * Edgar, 09.09.2026: „sind auch icons möglich im UI bei den Checkboxen,
     * so wie bei GarmentFit?" Ja, und ohne neue Bilder: Der Endpunkt
     * `/api/character/garment/thumb/<id>/` liefert sie schon für den
     * Assets-Reiter (`garments.js`), 121 von 121 Vorbildern haben eines.
     *
     * `loading="lazy"` statt des `Bildnachladers` aus dem Assets-Reiter: Dort
     * geht es um 181 Bilder in einer Liste, hier um höchstens 29 in einem
     * offenen Kasten. Ein zweiter Beobachter für diese Zahl wäre Aufwand
     * ohne Wirkung.
     */
    static _bild(vorbild) {
        const bild = document.createElement('img');
        bild.src = `/api/character/garment/thumb/${vorbild.bild}/`;
        bild.alt = '';
        bild.loading = 'lazy';
        bild.className = 'kleidungsbild';
        return bild;
    }

    static _anwenden(knopf, vorbild) {
        const gesetzt = GarmentcodeVorbilder._reglerStellen(vorbild.werte || {});
        const material = GarmentcodeVorbilder._material(vorbild.material);
        // Nur EIN Vorbild kann gelten — zwei gleichzeitig hiessen zwei
        // Wertesätze auf denselben Reglern, und der zweite gewönne stumm.
        for (const anderer of knopf.parentElement.children) {
            anderer.classList.toggle('active', anderer === knopf);
        }
        GarmentcodeVorbilder._melden(
            `„${vorbild.titel}" übernommen (${gesetzt} Regler${material}). `
            + 'Jetzt „Bauen 2D + 3D" drücken.');
    }

    /**
     * Farbe und Glanz des Vorbilds in die Materialfelder des Reiters.
     *
     * WOHER SIE KOMMEN (Edgar, 09.09.2026: „soll auch die Farbe, Roughness,
     * Textur usw. vom Garment Fit herüberkommen"): aus der `.mhmat` neben dem
     * Netz, die `Vorbildmaterial` liest — 121 von 121 Stücken haben eine.
     * NICHT aus `garment.json`: Deren `color` steht bei allen 181 Stücken auf
     * [0.30, 0.35, 0.50], das ist die Vorgabe des Fitters, keine Eigenschaft
     * des Stücks.
     *
     * Die TEXTUR bleibt weg, und das ist kein Versehen: Die UVs des Schnitts
     * gehören zu seinen Panels, `CamisoleDressUV.png` ist auf das
     * MakeHuman-Netz gemalt. Dieselbe Datei darauf legt Ärmelpixel auf den
     * Rock.
     */
    static _material(material) {
        if (!material || !material.farbe) return '';
        const feld = document.getElementById('gc-color');
        if (feld) {
            feld.value = GarmentcodeVorbilder._hex(material.farbe);
            feld.dispatchEvent(new Event('input', { bubbles: true }));
        }
        GarmentcodeVorbilder._schieber('gc-roughness', material.roughness);
        GarmentcodeVorbilder._schieber('gc-metalness', material.metalness);
        return ', Farbe und Glanz';
    }

    /** Ein Materialschieber steht in Prozent, der Wert kommt als 0…1. */
    static _schieber(kennung, wert) {
        if (wert === undefined || wert === null) return false;
        const feld = document.getElementById(kennung);
        if (!feld) return false;
        feld.value = String(Math.round(wert * 100));
        feld.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
    }

    static _hex(farbe) {
        const teil = (wert) => Math.round(Math.min(1, Math.max(0, wert)) * 255)
            .toString(16).padStart(2, '0');
        return `#${teil(farbe[0])}${teil(farbe[1])}${teil(farbe[2])}`;
    }

    /** Werte in die Regler schreiben — ohne sie zu merken (siehe Kopf). */
    static _reglerStellen(werte) {
        let gesetzt = 0;
        for (const [pfad, wert] of Object.entries(werte)) {
            // Nur Pfade, die es in DIESER Vorlage gibt. Ein Pfad ohne Regler
            // ginge stumm an den Server und würde dort verworfen.
            if (!(pfad in garmentcodeRegler.vorgaben)) continue;
            garmentcodeRegler.werte[pfad] = wert;
            if (garmentcodeRegler.nachziehen[pfad]) {
                garmentcodeRegler.nachziehen[pfad](wert);
            }
            gesetzt += 1;
        }
        return gesetzt;
    }

    static _melden(text) {
        const feld = document.getElementById('gc-meldung');
        if (feld) feld.textContent = text;
    }
}

// Selbststartend wie `garmentcode.js`: Der Reiter wird aus `boot.js` geladen,
// und das Auswahlfeld steht dann schon im DOM. Beim Laden vor dem DOM (Modul
// im `<head>`) waere `gc-vorlage` noch nicht da — deshalb die Weiche.
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded',
                              () => GarmentcodeVorbilder.verdrahten());
} else {
    GarmentcodeVorbilder.verdrahten();
}
