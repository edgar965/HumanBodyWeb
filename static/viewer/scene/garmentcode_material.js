import { state } from './state.js';
import { _sliderVal } from './utils.js';
import { GarmentcodeAnziehen } from './garmentcode_anziehen.js';
import { Garmentstoff } from './garmentcode_stoff.js';

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
 * auswählbar. Ist keines ausgewählt, wird der Stand nur GEMERKT: Er gilt
 * dann für das nächste Stück, das gebaut wird, und fasst nichts an, was
 * schon hängt.
 *
 * BIS ZUM 09.09.2026 GALT ER OHNE AUSWAHL FÜR ALLE `gc_*`-NETZE, und das
 * war der Fehler hinter zwei Befunden Edgars („Farben … setzen die Farben
 * von allen Garments statt einem" und „modell gespeichert (farbe rot des
 * T-Shirt), neu geladen — Farbe ist weg"). Denn das Reitergedächtnis
 * stellt beim Seitenstart `gc-color` wieder her und feuert dabei `input`
 * (`reitergedaechtnis.js`) — zu diesem Zeitpunkt ist nie etwas ausgewählt.
 * Im Browser gemessen: Ein einziges solches `input` schrieb das aus der
 * Szene geladene Material (#dcd8d0, Rauheit 0,85) auf den Reglerstand
 * (#ff0000, Rauheit 1,0) um. Die gespeicherte Farbe war damit weg, bevor
 * sie jemand sehen konnte — ohne Fehler und ohne Meldung.
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
    static stand = { farbe: '#dcd8d0', rauheit: 0.85, metall: 0.0 };

    /** Die drei Bedienelemente verdrahten. */
    static einhaengen() {
        GarmentcodeMaterial._feld('gc-color', (wert) => {
            GarmentcodeMaterial.stand.farbe = wert;
        });
        GarmentcodeMaterial._schieber('gc-roughness', (wert) => {
            GarmentcodeMaterial.stand.rauheit = wert / 100;
        });
        GarmentcodeMaterial._schieber('gc-metalness', (wert) => {
            GarmentcodeMaterial.stand.metall = wert / 100;
        });
    }

    /**
     * Den eingestellten Stand auflegen — auf das GEWÄHLTE Stück, sonst auf
     * KEINES.
     *
     * BEFUND (Edgar, 08.09.2026): „Änderung der Farbe ändert ALLE farben
     * aller GarmentCode Items, obwohl nur einer ausgewählt ist." Die erste
     * Fassung wirkte bewusst auf alle, damit ein später gebautes Stück die
     * Farbe erbt. Das war falsch gedacht: Ein Stück ist seit dem
     * 08.09.2026 ein eigenes Objekt, das man anklicken kann — wenn eines
     * gewählt ist, gilt die Auswahl.
     *
     * OHNE AUSWAHL WIRD NICHTS ANGEFASST (09.09.2026). Der Stand steht
     * bereits in `GarmentcodeMaterial.stand`; von dort holt ihn das nächste
     * gebaute Stück (`aufStueck`). Ein Rückgriff auf alle hängenden Stücke
     * kann nur schaden — er trifft auch die, die ihre Farbe aus der
     * gespeicherten Szene mitgebracht haben. Siehe Modulkopf: Genau daran
     * ist die gespeicherte Farbe beim Laden verlorengegangen.
     */
    static anwenden(figur) {
        const inst = figur?.inst || figur;
        const gewaehlt = GarmentcodeMaterial.gewaehltesStueck(inst);
        if (!gewaehlt) return 0;
        return GarmentcodeMaterial._auflegen(gewaehlt);
    }

    /**
     * Den Stand auf GENAU EIN Stück legen — für ein frisch gebautes.
     *
     * `GarmentcodeAnziehen` hängt jedes Stück mit einem neuen Material ein;
     * ohne diesen Schritt spränge die eingestellte Farbe bei jedem Bau auf
     * die Vorgabe zurück (08.09.2026). Gezielt, nicht über alle: Der Bau
     * eines zweiten Stücks darf die Farbe des ersten nicht mitziehen.
     */
    static aufStueck(figur, stueck) {
        const inst = figur?.inst || figur;
        const netz = inst?.clothMeshes?.[
            GarmentcodeAnziehen.schluessel(stueck)];
        return netz ? GarmentcodeMaterial._auflegen(netz) : 0;
    }

    static _auflegen(netz) {
        return Garmentstoff.auflegen(netz, GarmentcodeMaterial.stand);
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

    static _feld(id, tun) {
        const feld = document.getElementById(id);
        feld?.addEventListener('input', () => {
            // Dieselbe Sperre wie im `Materialregler`: Das Nachziehen der
            // Anzeige löst selbst ein `input` aus und dürfte sonst den
            // Stand überschreiben, den es gerade anzeigt.
            if (state._syncingSliders) return;
            tun(feld.value);
            GarmentcodeMaterial.anwenden(GarmentcodeMaterial.figur());
        });
    }

    static _schieber(id, tun) {
        document.getElementById(id)?.addEventListener('input', () => {
            if (state._syncingSliders) return;
            tun(_sliderVal(id));
            GarmentcodeMaterial.anwenden(GarmentcodeMaterial.figur());
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
