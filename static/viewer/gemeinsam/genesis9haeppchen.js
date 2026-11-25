import { Protokoll } from './protokoll.js';
import { Figuraufbaustand } from './figuraufbaustand.js';
import { Nutzerruhe } from './nutzerruhe.js';
import { Netzstufenstand } from './netzstufenstand.js';
import { Genesis9vorrat } from './genesis9vorrat.js';
import { Genesis9materialabruf } from './genesis9materialabruf.js';

/**
 * Genesis9haeppchen — die gewählte Stufe (fein oder ultrafein) STÜCK FÜR STÜCK nachholen, auf Wunsch erst nach Ruhe.
 *
 * Edgar, 09.10.2026: „die feine Stufe nur nach Ruhe, in kleinen Häppchen laden … Nach dem Laden lade die mittlere Stufe nach
 * und nach, und ändere die Anzeige, wenn fertig." Der Nachzug der ganzen Figur auf einmal (`Genesis9aufbau.alles(inst, null)`)
 * hielt den Hauptfaden gemessen 15,7 s und danach 71 s an (Zeitgeber-Lücken im Chrome, DOM unverändert, keine Serveranrufe in
 * dieser Zeit): Der Käfig stand, aber die Figur ließ sich nicht drehen.
 *
 * Jetzt: erst der Körper, dann Stück für Stück. Mit `ruhe` wird jede Antwort erst gebaut, wenn der Nutzer
 * `Nutzerruhe.RUHE_MS` lang nichts bewegt hat (`vorBau` in `koerperAufbauen`/`anziehen`: die Antwort ist da, der Bau wartet).
 * Ohne `ruhe` (Strg+Alt+H, Export) läuft es ohne Warten, aber immer noch nacheinander — zwischen zwei Stücken kommen
 * Eingaben dran. Nach jedem Stück meldet `Netzstufenstand` den Fortschritt; am Ende steht die neue Stufe in der Anzeige.
 *
 * Reglerzüge (`neuFormen`) bauen weiter alles sofort und auf einmal: Dort wartet der Nutzer auf das Ergebnis.
 */
export class Genesis9haeppchen {

    /** Ein Stück der gewählten Stufe schon anfragen — eingetragen von `Genesis9kleidung` (ein Import dorthin wäre ein Ring). */
    static vorab = null;

    /** Was nach dem ersten Zug noch in der gewählten Stufe fehlt: Stücke und 'koerper', ohne die in `schon` (sie kamen gleich so, `Genesis9aufbau.progressiv`). */
    static rest(inst, schon = null) {
        return [...inst.getragen(), 'koerper'].filter(teil => !schon?.has(teil));
    }

    /**
     * Ein Zug auf die gewählte Stufe. Zwei Züge einer Figur laufen nie zugleich: Der zweite wartet auf den ersten.
     * @param ruhe true = jedes Stück erst in der Ruhe bauen (das automatische Nachladen nach dem Laden)
     * @param schon was schon in der gewählten Stufe steht (Set aus Kennungen und 'koerper'), oder null
     */
    static zug(inst, ruhe, schon = null) {
        if (!ruhe) inst._feinDringend = true;
        if (inst._grobHalt) {                 // Wer hochschaltet, hebt die Sperre auf, die „grob gewählt" dem Export setzte
            inst._grobHalt = false;
            Figuraufbaustand.beenden(inst);
        }
        const davor = inst._feinZug || Promise.resolve();
        // Die Stufe nachladen ist eine Anzeige: der Server legt die Antworten dauerhaft ab (`Genesis9vorrat`, 19.10.2026).
        const zug = davor.then(() => Genesis9vorrat.laden(inst, () => Genesis9haeppchen._lauf(inst, ruhe, schon)));
        inst._feinZug = zug.catch(() => {});
        return zug;
    }

    static async _lauf(inst, ruhe, schon = null) {
        const ziel = Netzstufenstand.wahl;
        if (ziel === 'grob') return inst;                    // der Nutzer will grob: nichts nachholen
        const dringend = () => Boolean(inst._feinDringend);
        // `_bauStart`: ab hier wird gebaut (die Antwort ist da, die Ruhe auch) — die Bauzeit je Stück steht in `inst._bauzeiten`.
        const vorBau = ruhe ? async () => { await Nutzerruhe.abwarten(dringend); inst._bauStart = performance.now(); } : null;
        inst._bauzeiten = [];
        const rest = Genesis9haeppchen.rest(inst, schon), stuecke = rest.filter(teil => teil !== 'koerper'), koerper = rest.includes('koerper');
        const gesamt = rest.length;
        const vorher = Netzstufenstand.stufeVon(inst) || 'grob';
        let fertig = 0;
        const melden = () => Netzstufenstand.melden(inst, vorher, true, fertig, gesamt);
        Figuraufbaustand.beginnen(inst);
        try {
            melden();
            // Die Stücke zuerst, der Körper ZULETZT: Solange der grobe Körper steht, passt seine Haut-Maske zu ihm; der feine
            // hat noch keine, sein Skelett wäre neu und das Umbinden aller Stücke käme vor dem Ende (`Hautverdeckung`: 3,25 s).
            // Angefragt wird der Körper aber schon jetzt, gebaut weiter zuletzt (`Genesis9materialabruf.vorab`, 18.11.2026).
            if (koerper && stuecke.length && inst.constructor.ADRESSE) Genesis9materialabruf.vorab(inst, `${inst.constructor.ADRESSE}${encodeURIComponent(inst.figur)}/netz/`);
            // Ebenso die Stücke: alle zugleich, gebaut weiter eines nach dem anderen (24.11.2026 — vorher jedes erst nach dem Bau des vorigen angefragt).
            if (inst.constructor.ADRESSE) for (const kennung of stuecke) Genesis9haeppchen.vorab?.(inst, kennung);
            for (const kennung of stuecke) {
                if (Netzstufenstand.wahl !== ziel) break;     // inzwischen umgeschaltet
                await Genesis9haeppchen._stueck(inst, kennung, vorBau);
                Genesis9haeppchen._gebaut(inst, kennung);
                fertig += 1; melden();
            }
            if (Netzstufenstand.wahl === ziel && koerper) {
                await inst.koerperAufbauen(null, true, vorBau);
                Genesis9haeppchen._gebaut(inst, 'koerper');
                fertig += 1; melden();
            }
            if (Netzstufenstand.wahl === ziel) Netzstufenstand.melden(inst, ziel, false);
        } catch (fehler) {
            Protokoll.warnung('Genesis 9', `Stufe „${ziel}" nicht geladen: ${fehler.message}`);
            Netzstufenstand.melden(inst, vorher, false);
        } finally {
            Figuraufbaustand.beenden(inst);
        }
        return inst;
    }

    /** Die Bauzeit eines Häppchens (ms) merken — nur mit Ruhe gemessen, sonst ist Warten auf den Server dabei. */
    static _gebaut(inst, name) {
        if (inst._bauStart === undefined) return;
        inst._bauzeiten.push([name, Math.round(performance.now() - inst._bauStart)]);
        inst._bauStart = undefined;
    }

    /** Ein Stück holen; wurde die Antwort verworfen (Reglerzug, Hautwechsel währenddessen), einmal neu. */
    static async _stueck(inst, kennung, vorBau) {
        for (let versuch = 0; versuch < 2 && inst.kleidung[kennung]; versuch += 1) {
            const lauf = inst._lauf;
            try {
                await inst.anziehen(kennung, inst.kleidung[kennung], null, false, vorBau);
            } catch (fehler) {
                Protokoll.warnung('Genesis 9', `${kennung} nicht fein geladen: ${fehler.message}`);
                return;
            }
            if (inst._lauf === lauf) return;
        }
    }
}
