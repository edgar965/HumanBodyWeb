import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { markDirty } from '../undo.js';
import { UmaFigur } from './umafigur.js';
import { Umagarderobe } from './umagarderobe.js';
import { Umabauerstand } from './umabauerstand.js';

/**
 * Umatyp — der Typ einer UMA-Figur: Mann, Frau, Elfe … (UMAs „Rasse").
 *
 * WARUM (06.09.2026, Edgar: „wo ist der Regler nach Typ (Elfe, Mann, Frau)?"):
 * Der Typ steckt in der GLB — UMA setzt Körper und Kleidung in Unity zusammen.
 * Die Auswahl zeigt darum zwei Gruppen: Figuren, die im Katalog liegen (sofort),
 * und Rassen, die Unity erst bauen muss (`POST uma-figur/bauen/`, dann Stand
 * abfragen, bis die Datei da ist). Danach wird die Figur in der Szene gegen die
 * neue Datei getauscht; Transform, Farben und gleichnamige Regler bleiben.
 *
 * `neuBauen` ist der eine Weg für alles, was Unity braucht — Kleidung
 * (Kleider-Reiter) und Farben (Eigenschaften): ein Auftrag, ein Dateiname aus
 * Rasse plus Kennung der Auswahl. Der Bauer wird vorgewärmt, sobald die Typ-
 * Zeile erscheint (`Umabauerstand`).
 */
export class Umatyp {

    static RASSEN = '/api/character/uma-rassen/';
    static BAUEN = '/api/character/uma-figur/bauen/';
    static ERMITTELN = '/api/character/uma-rassen/ermitteln/';
    static TAKT_MS = 500;      // bei offenem Bauer dauert ein Bau 4–6 s; 2 s Takt kostete davon ein Drittel
    static UMA3 = /(3\.0|30)$/;
    static FARBEN = ['haut', 'haar'];

    static async fuellen(inst, behaelter) {
        behaelter.innerHTML = '<div class="slider-row"><label>Typ</label>'
            + '<select id="prop-uma-typ-auswahl" class="viewer-select hb-dehnt-ohne-abstand">'
            + '<option>Lade …</option></select></div>'
            + '<div id="prop-uma-typ-stand" class="hb-font-size-0-72rem"></div>'
            + '<div id="prop-uma-bauer" class="hb-font-size-0-72rem"></div>';
        const auswahl = behaelter.querySelector('select');
        const stand = behaelter.querySelector('#prop-uma-typ-stand');
        let daten;
        try {
            daten = await Serverabruf.json(Umatyp.RASSEN);
        } catch (fehler) {
            stand.textContent = `Typen nicht ladbar: ${fehler.message}`;
            return;
        }
        auswahl.innerHTML = '';
        const katalog = document.createElement('optgroup');
        katalog.label = 'Im Katalog';
        for (const figur of daten.figuren) {
            const eintrag = new Option(`${figur.rasse || 'Rasse unbekannt'} · ${figur.name}`, `datei:${figur.name}`);
            eintrag.selected = figur.name === inst.datei;
            katalog.appendChild(eintrag);
        }
        auswahl.appendChild(katalog);
        const neu = document.createElement('optgroup');
        neu.label = 'Neu bauen (Unity)';
        const vorhanden = new Set(daten.figuren.map(f => f.rasse));
        for (const rasse of daten.rassen) {
            // Nur die UMA3-Rassen (Human Female 3.0, ElfMale30 …); die Liste aus
            // Unity führt auch UMA2-Altlasten (HumanMale, SkyCar) ohne UMA3-Kleidung.
            if (!Umatyp.UMA3.test(rasse) || vorhanden.has(rasse)) continue;
            neu.appendChild(new Option(rasse, `rasse:${rasse}`));
        }
        if (!daten.ermittelt) neu.appendChild(new Option('Rassenliste aus Unity holen …', 'ermitteln'));
        auswahl.appendChild(neu);
        auswahl.addEventListener('change', () => Umatyp._gewaehlt(inst, auswahl.value, stand));
        if (!daten.ermittelt) stand.textContent = 'Die Rassenliste kommt aus Unity — einmal holen.';
        // Den Bauer jetzt schon starten: Wer hier ist, baut gleich — und der
        // erste Bau nach einem Start kostet 90 s, jeder weitere 5 s.
        Umabauerstand.anzeigen(behaelter.querySelector('#prop-uma-bauer'), {
            vorwaermen: true,
            beiAenderung: (bauer) => { neu.label = `Neu bauen (${Umabauerstand.dauer(bauer)})`; },
        });
    }

    static _gewaehlt(inst, wert, stand) {
        if (wert.startsWith('datei:')) return Umatyp.wechseln(inst, wert.slice(6), stand);
        if (wert.startsWith('rasse:')) return Umatyp.bauen(inst, wert.slice(6), stand);
        if (wert === 'ermitteln') return Umatyp.ermitteln(inst, stand);
        return undefined;
    }

    /**
     * Die Figur gegen eine andere Katalogdatei tauschen — gleiche Kennung, gleicher
     * Platz. `farbenGebacken`: Die Farben stecken in der neuen Datei; die Tönung
     * im Browser fällt weg, sonst läge sie doppelt auf der Haut.
     */
    static async wechseln(inst, datei, stand, { farbenGebacken = false } = {}) {
        if (datei === inst.datei && !farbenGebacken) return;
        stand.textContent = `Lade ${datei} …`;
        const daten = inst.toJSON();
        daten.datei = datei;
        daten.presetName = null;
        if (farbenGebacken) daten.farben = null;
        Umagarderobe.vergessen(datei);           // ein neuer Bau, ein neuer Zettel
        const neu = new UmaFigur(inst.id, daten);
        try {
            await neu.load();
        } catch (fehler) {
            stand.textContent = `Fehler: ${fehler.message}`;
            return;
        }
        neu.group.position.copy(inst.group.position);
        neu.group.rotation.copy(inst.group.rotation);
        neu.group.scale.copy(inst.group.scale);
        if (state._animatedCharId === inst.id) fn.stopAnimation?.();
        state.scene.remove(inst.group);
        inst.dispose();
        state.characters.set(inst.id, neu);
        state.scene.add(neu.group);
        fn.updateCharacterListUI();
        fn.selectCharacter(inst.id);
        markDirty(`UMA-Typ ${datei}`);
    }

    /** Unity bauen lassen (Rasse mit UMAs Vorgabe-Garderobe), warten, dann wechseln. */
    static bauen(inst, rasse, stand) {
        return Umatyp.bauenMit(inst, { rasse }, stand);
    }

    /**
     * Die Figur in Unity neu bauen — mit der Kleidung (gegeben, sonst die vom
     * Zettel) und den Farben (gewünschte über gebackene). Der Dateiname trägt
     * Rasse und eine Kennung aus beidem: jede Kombination ihre eigene Datei.
     */
    static async neuBauen(inst, { rasse = null, kleidung = null, stand }) {
        const garderobe = await Umagarderobe.lesen(inst.datei).catch(() => null);
        rasse = rasse || garderobe?.rasse;
        if (!rasse) { stand.textContent = 'Ohne Rasse im Zettel kann Unity nicht bauen.'; return undefined; }
        kleidung = kleidung || (garderobe?.teile || []).map(t => t.rezept);
        const farben = Umatyp.farbenFuer(inst, garderobe);
        const merkmale = [...kleidung, ...Object.entries(farben).map(([k, v]) => `${k}=${v}`)];
        const koerper = { rasse, kleidung, name: `${Umatyp.nameFuer(rasse)}_k${Umatyp.kennung(merkmale)}` };
        if (Object.keys(farben).length) koerper.farben = farben;
        return Umatyp.bauenMit(inst, koerper, stand, { farbenGebacken: !!koerper.farben });
    }

    /** Gewünschte Farben (Tönung im Browser) über den gebackenen aus dem Zettel. */
    static farbenFuer(inst, garderobe) {
        const farben = {};
        for (const schluessel of Umatyp.FARBEN) {
            const wert = inst.farben?.[schluessel] || garderobe?.farben?.[schluessel];
            if (wert) farben[schluessel] = wert.toLowerCase();
        }
        return farben;
    }

    /** `koerper` = {rasse, name?, kleidung?, farben?} wie `POST uma-figur/bauen/`. */
    static async bauenMit(inst, koerper, stand, { farbenGebacken = false } = {}) {
        const lauf = await Umatyp._starten(Umatyp.BAUEN, koerper, stand);
        if (!lauf) return undefined;
        const ende = await Umatyp._warten(lauf.name, stand, `Unity baut ${koerper.rasse}`);
        if (!ende) return undefined;
        if (ende.datei) {
            await Umatyp.wechseln(inst, ende.datei, stand, { farbenGebacken });
        } else {
            stand.textContent = `Unity meldet Ende ${ende.exit}, keine Datei. ${ende.meldung || ''} (${ende.log})`;
        }
        return ende;
    }

    /** Dateiname aus der Rasse, wie `Umabauer.name_fuer`: „Human Female 3.0" → Uma_HumanFemale30. */
    static nameFuer(rasse) {
        return 'Uma_' + rasse.replace(/[^A-Za-z0-9]+/g, '');
    }

    /** Kurze, feste Kennung einer Auswahl (djb2 über die Namen), acht Hexzeichen. */
    static kennung(namen) {
        let h = 5381;
        for (const zeichen of namen.join(',')) h = (Math.imul(h, 33) ^ zeichen.charCodeAt(0)) >>> 0;
        return h.toString(16).padStart(8, '0');
    }

    /** Die Rassenliste holen; danach die Auswahl neu füllen. */
    static async ermitteln(inst, stand) {
        const lauf = await Umatyp._starten(Umatyp.ERMITTELN, {}, stand);
        if (!lauf) return;
        const ende = await Umatyp._warten(lauf.name, stand, 'Unity liest die Rassen');
        if (ende) await Umatyp.fuellen(inst, document.getElementById('prop-uma-typ'));
    }

    static async _starten(adresse, koerper, stand) {
        try {
            return await Serverabruf.json(adresse, {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(koerper),
            });
        } catch (fehler) {
            stand.textContent = `Nicht gestartet: ${fehler.message}`;
            return null;
        }
    }

    static async _warten(name, stand, text) {
        for (;;) {
            await new Promise(r => setTimeout(r, Umatyp.TAKT_MS));
            let lauf;
            try {
                lauf = await Serverabruf.json(`${Umatyp.BAUEN}${encodeURIComponent(name)}/stand/`);
            } catch (fehler) {
                stand.textContent = `Stand nicht lesbar: ${fehler.message}`;
                return null;
            }
            stand.textContent = `${text} … ${lauf.sekunden} s${lauf.meldung ? ' · ' + lauf.meldung : ''}`;
            if (!lauf.laeuft) return lauf;
        }
    }
}
