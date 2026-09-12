import { state } from './state.js';
import { _sliderVal } from './utils.js';
import { GarmentcodeAnziehen } from './garmentcode_anziehen.js';
import { Garmentstoff } from './garmentcode_stoff.js';
import { GarmentcodeGewebe } from './garmentcode_gewebe.js';
import { Materialziel } from './materialziel.js';

/**
 * Farbe und Material der GarmentCode-Stücke.
 *
 * Edgar, 08.09.2026: „mach noch einstellungen im Garment Code für die Farbe,
 * metallness, roughess (ganz oben im Tab), so wie das bei Garment Fit ist."
 *
 * WORAUF SIE WIRKEN
 * =================
 * Auf das ANGEKLICKTE Stück, wie im Kleider-Reiter — ein GarmentCode-Stück
 * ist seit dem 08.09.2026 ein eigenes Objekt in `clothMeshes` und damit
 * auswählbar. Ist keines ausgewählt, wirkt ein Regler, den der NUTZER
 * bedient, auf alle GarmentCode-Stücke der Figur (12.09.2026, Edgar:
 * „ändere ich das Gewebe, oder andere Einstellungen, tut sich nichts" —
 * die Überschrift versprach es, der Code tat es nicht). Der Stand wird
 * dazu GEMERKT und gilt für das nächste Stück, das gebaut wird.
 *
 * VOM 09. BIS 12.09.2026 FASSTE ER OHNE AUSWAHL NICHTS AN, davor galt er
 * ohne Auswahl für alle `gc_*`-Netze — und das war der Fehler hinter zwei
 * Befunden Edgars („Farben … setzen die Farben von allen Garments statt
 * einem" und „modell gespeichert (farbe rot des T-Shirt), neu geladen —
 * Farbe ist weg"). Denn das Reitergedächtnis stellt beim Seitenstart
 * `gc-color` wieder her und feuert dabei `input` (`reitergedaechtnis.js`)
 * — zu diesem Zeitpunkt ist nie etwas ausgewählt. Im Browser gemessen: Ein
 * einziges solches `input` schrieb das aus der Szene geladene Material
 * (#dcd8d0, Rauheit 0,85) auf den Reglerstand (#ff0000, Rauheit 1,0) um.
 * Die gespeicherte Farbe war damit weg, bevor sie jemand sehen konnte.
 *
 * Die Grenze liegt deshalb nicht bei der Auswahl, sondern beim URHEBER:
 * `isTrusted` unterscheidet den Nutzer am Feld von `dispatchEvent` aus dem
 * Code (Reitergedächtnis, Vorbild, Gewebe-Vorgaben). Nur der Nutzer wirkt
 * breit; die Entscheidung steht in `Materialziel` (in Node geprüft).
 *
 * Der vorhandene `Materialregler` passt trotzdem nicht: Er kennt nur den
 * Fall mit Auswahl und hält keinen Stand, den ein späterer Bau erben
 * könnte.
 *
 * DIE WERTE ÜBERLEBEN DEN NÄCHSTEN BAU. `GarmentcodeAnziehen` legt für jedes
 * Stück ein frisches `MeshStandardMaterial` an; ohne diesen Schritt spränge
 * die Farbe bei jedem Bau auf #dcd8d0 zurück, und die Einstellung wäre nur so
 * lange gültig, bis man sie braucht. `anwenden` läuft deshalb am Ende des
 * Anziehens (`GarmentcodeDrapierung.anziehen`) noch einmal.
 */
export class GarmentcodeMaterial {

    /** Die Vorgabe ist die, mit der `GarmentcodeAnziehen` einhängt. */
    static stand = { farbe: '#dcd8d0', rauheit: 0.85, metall: 0.0,
                     gewebe: { ...Garmentstoff.GEWEBE } };

    /** Die Bedienelemente verdrahten — dazu das Gewebe (11.09.2026). */
    static einhaengen() {
        GarmentcodeGewebe.einhaengen(GarmentcodeMaterial);
        GarmentcodeMaterial._feld('gc-color', (wert) => {
            GarmentcodeMaterial.stand.farbe = wert;
            return { farbe: wert };
        });
        GarmentcodeMaterial._schieber('gc-roughness', (wert) => {
            GarmentcodeMaterial.stand.rauheit = wert / 100;
            return { rauheit: wert / 100 };
        });
        GarmentcodeMaterial._schieber('gc-metalness', (wert) => {
            GarmentcodeMaterial.stand.metall = wert / 100;
            return { metall: wert / 100 };
        });
    }

    /**
     * Den eingestellten Stand auflegen — auf das GEWÄHLTE Stück; ohne
     * Auswahl auf alle GarmentCode-Stücke der Figur, aber NUR wenn der
     * Nutzer das Feld bedient hat (`nutzer`), sonst auf keines.
     *
     * BEFUND (Edgar, 08.09.2026): „Änderung der Farbe ändert ALLE farben
     * aller GarmentCode Items, obwohl nur einer ausgewählt ist." — wenn
     * eines gewählt ist, gilt die Auswahl. Was ohne Auswahl geschieht,
     * entscheidet `Materialziel`; die Begründung steht im Modulkopf.
     *
     * `werte`: NUR die Eigenschaft, die der Nutzer gerade bewegt hat (ein
     * Gewebewechsel bringt nicht die Farbe des Feldes mit — ohne Auswahl
     * tragen die Stücke ihre eigenen Farben, gemessen: ein Wechsel auf
     * Köper färbte beide Stücke der Figur auf das Farbfeld um). Ohne
     * `werte` der ganze Stand, wie beim Bau.
     */
    static anwenden(figur, nutzer = false, werte = null) {
        const inst = figur?.inst || figur;
        const netze = Materialziel.netze({
            gewaehlt: GarmentcodeMaterial.gewaehltesStueck(inst),
            stuecke: inst?.clothMeshes, nutzer });
        let gesetzt = 0;
        for (const netz of netze) {
            gesetzt += GarmentcodeMaterial._auflegen(netz, werte);
        }
        return gesetzt;
    }

    /**
     * Den Stand auf GENAU EIN Stück legen — für ein frisch gebautes.
     *
     * `GarmentcodeAnziehen` hängt jedes Stück mit einem neuen Material ein;
     * ohne diesen Schritt spränge die eingestellte Farbe bei jedem Bau auf
     * die Vorgabe zurück (08.09.2026). Gezielt, nicht über alle: Der Bau
     * eines zweiten Stücks darf die Farbe des ersten nicht mitziehen.
     */
    static aufStueck(figur, stueck, werte = null) {
        const inst = figur?.inst || figur;
        const netz = inst?.clothMeshes?.[
            GarmentcodeAnziehen.schluessel(stueck)];
        return netz ? GarmentcodeMaterial._auflegen(netz, werte) : 0;
    }

    /** `werte` statt des Stands: das Material, das ein Stück der
     *  Kombiliste mitbringt (`garmentcode_gemeinsam.js`, 11.09.2026). */
    static _auflegen(netz, werte = null) {
        return Garmentstoff.auflegen(netz, werte || GarmentcodeMaterial.stand);
    }

    /**
     * Das Aussehen, das ein getragenes Stück GERADE hat — oder `null`.
     *
     * Das ist die Farbe, die der Nutzer sieht und die er dem Stück gegeben
     * hat (Klick auf das Stück, dann der Farbwähler). `stand` dagegen ist
     * nur der letzte Wert im Panel — und der gilt für alle Stücke gleich.
     * Wer ein Stück neu baut, das schon hängt, nimmt dessen Aussehen mit
     * (Edgar, 11.09.2026: „verschiedene Farben vorgegeben, es wurde nur
     * 1 Farbe genommen").
     */
    static getragen(figur, stueck) {
        const inst = figur?.inst || figur;
        const netz = inst?.clothMeshes?.[
            GarmentcodeAnziehen.schluessel(stueck)];
        return netz ? Garmentstoff.werte(netz) : null;
    }

    /**
     * Das angeklickte GarmentCode-Stück dieser Figur — oder `null`.
     *
     * Gelesen wie im Kleider-Reiter (`_selectedGarmentMesh`): über
     * `state._selectedSubMesh`. Der Präfix `gc_` grenzt ab; ein
     * ausgewähltes MakeHuman- oder Assets-Stück gehört nicht hierher und
     * darf von diesen Reglern nicht angefasst werden.
     */
    static gewaehltesStueck(inst) {
        const wahl = state._selectedSubMesh;
        if (!wahl || wahl.type !== 'cloth' || !wahl.key) return null;
        if (!String(wahl.key).startsWith('gc_')) return null;
        if (inst && wahl.charId && inst.id && wahl.charId !== inst.id) return null;
        const traeger = inst || (state.characters?.get?.(wahl.charId));
        return traeger?.clothMeshes?.[wahl.key] || null;
    }

    /** `tun(wert)` schreibt den Stand und liefert die geänderte Eigenschaft. */
    static _feld(id, tun) {
        const feld = document.getElementById(id);
        feld?.addEventListener('input', (ereignis) => {
            // Dieselbe Sperre wie im `Materialregler`: Das Nachziehen der
            // Anzeige löst selbst ein `input` aus und dürfte sonst den
            // Stand überschreiben, den es gerade anzeigt.
            if (state._syncingSliders) return;
            const werte = tun(feld.value);
            // `isTrusted`: der Nutzer am Feld, nicht `dispatchEvent`.
            GarmentcodeMaterial.anwenden(GarmentcodeMaterial.figur(),
                                         ereignis.isTrusted, werte);
        });
    }

    static _schieber(id, tun) {
        document.getElementById(id)?.addEventListener('input', (ereignis) => {
            if (state._syncingSliders) return;
            const werte = tun(_sliderVal(id));
            GarmentcodeMaterial.anwenden(GarmentcodeMaterial.figur(),
                                         ereignis.isTrusted, werte);
        });
    }

    /**
     * Die Figur, auf die sich der Reiter bezieht.
     *
     * Wird von aussen gesetzt (`GarmentcodeMaterial.figurgeber = …`), damit
     * dieses Modul den Reiter nicht kennen muss — sonst hinge das Material
     * an der Bedienung und wäre nicht mehr für sich prüfbar.
     */
    static figurgeber = null;

    static figur() {
        return GarmentcodeMaterial.figurgeber
            ? GarmentcodeMaterial.figurgeber() : null;
    }

    /** Der Name eines Stücks — für Aufrufer, die nur den Schlüssel haben. */
    static name(stueck) {
        return GarmentcodeAnziehen.name(stueck);
    }
}
