import { Netzstufenstand } from './netzstufenstand.js';

/**
 * Zeichenstand — was an einer Genesis-Figur noch nicht fertig gezeichnet ist (19.10.2026).
 *
 * Edgar, 19.10.2026: „die meldung kommt Netz grob, aber die Scham wird erst ein paar Sekunden später gezeichnet. Machst du da eine
 * Zwischenmeldung, bei allen Stufen, so dass klar wird, dass die Scham (Oder andere Teile auch), auch nicht gezeichnet sind" — und: „es dauert
 * auch bei Netz grob mehr als 10 s bis die Scham im Ergebnis richtig gezeichnet wird, mach eine Sanduhr oder eine Anzeige … bis alles geladen
 * ist". Die Anzeige rechts unten (`Netzstufenschalter`) meldete die Stufe, sobald Körper und Stücke GEBAUT waren. Danach kommen noch: die Bilder
 * (`Genesis9texturen`), die Haut des Anatomie-Stücks (`Anatomiehaut`: auf die Bilder warten, Karten rechnen), die Naht verschweißter Stücke
 * (`Hautloch`) und die Haut-Maske unter der Kleidung (`Hautverdeckung`, im Worker).
 *
 * Hier wird im Takt NACHGESEHEN, was davon aussteht, und als `offen` an `Netzstufenstand` gemeldet — die Anzeige schreibt „⏳ … lädt noch: …".
 * Nachsehen statt melden: Die Zustände liegen schon an den Figuren (`_anatomieWartet`, `anatomieBackt`, `Hautverdeckung._ausstehend` …); eine
 * Meldung je Stelle wäre ein Eingriff in sechs Klassen, und eine vergessene ließe die Sanduhr für immer stehen. Der Takt kostet je Figur
 * Bruchteile einer Millisekunde und läuft nur, solange eine Figur beobachtet wird.
 *
 * Steht der Anatomie-Stand neu und niemand rechnet (die Bilder des Körpers kamen nach dem letzten Durchlauf, `Anatomiehaut.stand`), stößt der Takt
 * `Anatomiehaut.nachziehen` an — einmal je Stand. Sonst bliebe die Scham bis zum nächsten Umbau in der Farbe vor den Bildern stehen.
 *
 * Die schweren Module (Three.js, Shader) kommen per `import()`: `genesis9aufbau.js` und `genesis9kleidung.js` laden dieses Modul, ihre
 * Node-Tests brauchen sie nicht.
 */
export class Zeichenstand {

    static TAKT_MS = 400;
    /** Die beobachteten Figuren (Objekte, nicht Kennungen: eine neue Figur kann die Kennung einer entsorgten tragen). */
    static _figuren = new Set();
    static _takt = null;
    static _module = null;

    /** Eine Figur beobachten (`Genesis9aufbau.alles`): ab jetzt steht in der Anzeige, was an ihr noch fehlt. */
    static beobachten(inst) {
        if (!inst?.id || typeof window === 'undefined' || Netzstufenstand.entsorgt(inst)) return;
        Zeichenstand._figuren.add(inst);
        if (!inst.bodyMesh) Netzstufenstand.offen(inst, ['Körper']);     // sofort, nicht erst im nächsten Takt
        if (!Zeichenstand._takt) {
            Zeichenstand._takt = setInterval(() => { Zeichenstand._pruefen(); }, Zeichenstand.TAKT_MS);
            Zeichenstand._takt?.unref?.();                                // Node: der Takt hält keinen Test am Leben
        }
    }

    /**
     * Ein Stück wird geholt (`Genesis9kleidung.anziehen`): Solange noch KEIN Netz von ihm steht, fehlt es in der Anzeige. Ein Stück, das schon steht
     * und nur neu kommt (feine Stufe, Reglerzug), zählt nicht — das sagt der Zähler der Stufe.
     * @returns `versprechen`, unverändert (ein Fehlschlag kommt beim Aufrufer an)
     */
    static laden(inst, kennung, versprechen) {
        if (!inst || !versprechen?.then) return versprechen;
        const laufend = inst._zeichenLaedt || (inst._zeichenLaedt = new Map());
        laufend.set(kennung, (laufend.get(kennung) || 0) + 1);
        const fertig = () => {
            const n = (laufend.get(kennung) || 1) - 1;
            if (n > 0) laufend.set(kennung, n); else laufend.delete(kennung);
        };
        versprechen.then(fertig, fertig);
        return versprechen;
    }

    /** Die Module, die nachgesehen werden — einmal geladen; null, wenn das scheitert (dann schweigt der Takt, die Anzeige bleibt wie bisher). */
    static module() {
        if (!Zeichenstand._module) {
            Zeichenstand._module = Promise.all([
                import('./anatomiehaut.js'), import('./hautloch.js'), import('./stueckloch.js'), import('./hautverdeckung.js'),
                import('./genesis9texturen.js'), import('./genesis9kleidung.js'),
            ]).then(([a, h, s, v, t, k]) => ({
                Anatomiehaut: a.Anatomiehaut, Hautloch: h.Hautloch, Stueckloch: s.Stueckloch, Hautverdeckung: v.Hautverdeckung,
                Genesis9texturen: t.Genesis9texturen, Genesis9kleidung: k.Genesis9kleidung,
            })).catch((fehler) => {
                console.warn(`Zeichenstand: ${fehler.message}`);
                return null;
            });
        }
        return Zeichenstand._module;
    }

    static async _pruefen() {
        if (Zeichenstand._laeuft) return;
        Zeichenstand._laeuft = true;
        try {
            const m = await Zeichenstand.module();
            for (const inst of [...Zeichenstand._figuren]) {
                if (Netzstufenstand.entsorgt(inst)) { Zeichenstand._figuren.delete(inst); continue; }
                if (!m) continue;
                Zeichenstand._anstossen(inst, m.Anatomiehaut);
                Netzstufenstand.offen(inst, Zeichenstand.offen(inst, m));
            }
        } catch (fehler) {
            console.warn(`Zeichenstand: ${fehler.message}`);
        } finally {
            Zeichenstand._laeuft = false;
        }
        if (!Zeichenstand._figuren.size && Zeichenstand._takt) {
            clearInterval(Zeichenstand._takt);
            Zeichenstand._takt = null;
        }
    }

    /** Ein neuer Anatomie-Stand, für den niemand rechnet: einmal anstoßen (siehe oben). */
    static _anstossen(inst, Anatomiehaut) {
        if (inst._anatomieWartet || !Anatomiehaut.stuecke(inst).length) return;
        const stand = Anatomiehaut.stand(inst);
        if (stand === inst._anatomieStand || stand === inst._anatomieAufgegeben || stand === inst._zeichenAngestossen) return;
        inst._zeichenAngestossen = stand;
        Anatomiehaut.nachziehen(inst);
    }

    /** Was an der Figur noch fehlt — Texte in Alltagssprache, in der Reihenfolge, in der es kommt. */
    static offen(inst, { Anatomiehaut, Hautloch, Stueckloch, Hautverdeckung, Genesis9texturen, Genesis9kleidung }) {
        const aus = [];
        const koerper = inst.bodyMesh, geo = koerper?.geometry;
        if (!koerper) aus.push('Körper');
        const stuecke = Object.keys(inst.clothMeshes || {});
        for (const kennung of inst._zeichenLaedt?.keys() || []) {
            if (!stuecke.some((s) => s.startsWith(`${kennung}/`))) aus.push(Genesis9kleidung.gemerkterName(kennung) || kennung);
        }
        if (Zeichenstand.bilderOffen(inst, Genesis9texturen)) aus.push('Texturen');
        for (const netz of Anatomiehaut.offen(inst)) aus.push(`${Zeichenstand.name(netz)} (Hautfarbe)`);
        const anzahl = (geo?.userData?.indexVoll?.index?.length || 0) / 3;
        if (anzahl) {
            const genaeht = Hautloch._loecher.get(geo)?.schluessel || [];
            for (const [schluessel, netz] of Hautverdeckung.zaehlende(inst)) {
                if (Stueckloch.fassung(netz, anzahl) && !genaeht.includes(schluessel)) aus.push(`${Zeichenstand.name(netz)} (Naht)`);
            }
        }
        if (koerper && (Hautverdeckung._ausstehend.has(inst) || inst._maskeRechnet)) aus.push('Haut unter der Kleidung');
        return aus;
    }

    /** Wartet ein Material der Figur noch auf ein Bild (`Genesis9texturen.offen`)? */
    static bilderOffen(inst, Genesis9texturen) {
        let offen = false;
        inst.group?.traverse?.((kind) => {
            if (!offen) offen = [kind.material].flat().some((m) => m && Genesis9texturen.offen(m) > 0);
        });
        return offen;
    }

    /** Der Name eines Stücks aus seinem Schild (`Genesis9kleidung.beschriftung`), ohne Herkunft und Teil. */
    static name(netz) {
        const schild = netz?.userData?.beschriftung || netz?.name || 'Stück';
        return schild.replace(/\s*\([^)]*\)\s*$/, '').replace(/\s*·.*$/, '');
    }
}
