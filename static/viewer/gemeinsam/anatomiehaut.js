import { Anatomieton } from './anatomieton.js';
import { Anatomiekarten } from './anatomiekarten.js';
import { Anatomiebacken } from './anatomiebacken.js';

/**
 * Anatomiehaut — das starre Anatomie-Stück (Daz-Geograft „Daz Anatomie Frau|Mann", Scham/Penis aus einer .blend) folgt der
 * gewählten Haut (11.10.2026, Edgar: „wenn ich die Haut eines Daz-Modells ändere, wird die Textur der Scham nicht angepasst").
 *
 * URSACHE: Das Stück trägt seine Textur als VARIANTE (`daz_anatomie_frau_ursula`, `…_damira`, `…_hautton_kin`), im Modell fest
 * eingetragen. Ein Hautwechsel (`Genesis9Modell.hautSetzen`) baut nur den Körper neu; das Stück behält seine Variante — Ursulas
 * helle Karte stand als weißer Fleck auf einer dunklen Haut.
 *
 * HIER: Der Hautton wird RINGS UM DAS STÜCK gemessen (Median der Texel an den UV der Körperpunkte im erweiterten Kasten des Stücks, `Anatomieton`)
 * und mit dem Ton verglichen, den das Stück selbst zeigt (Median der Texel an SEINEN UV, mal Farbe). Hat die Haut Farbkarten, zeigt das Stück IMMER Karten, die aus denen der Haut gerechnet sind
 * (`Anatomiebacken`, seit 11.10.2026 abends: Farbe, Normalen und Rauheit im Atlas des Stücks, Texel für Texel von der Stelle der Haut darunter —
 * Edgar: „die neue Skin Textur erscheint da nicht, nur die Farbe"; vorher stand es in einer einfachen Farbe im Hautton, ohne Poren). Bis sie fertig
 * sind (in Häppchen auf dem Hauptfaden) steht das Stück in dieser einfachen Farbe; schlägt die Rechnung fehl, bleibt es dabei.
 *
 * KEINE TONSCHWELLE MEHR MIT KARTEN (12.10.2026, Edgar: „fixe alle skins"): Bis dahin behielt das Stück seine eigene Textur, solange sein Ton höchstens `TOLERANZ`
 * von der Haut abwich. Gemessen im Chrome auf `G9 Feminine Skin 01` (sehr hell): das Stück stand auf seiner eigenen Karte (keine Ablage am Material), obwohl es sich im Bild
 * sichtbar als Fleck abhob — die Schwelle stammt aus drei Haut-Paaren, keine Reihe. Jetzt entscheidet kein Ton mehr, sondern nur, ob die Haut Karten hat. Ohne Farbkarte der Haut
 * (Rechnung nicht möglich) gilt die Schwelle weiter: ein Stück mit passendem Ton bleibt, wie es war. Die Farbe liegt im Material, nicht in der Umfärbung (`umfaerbung.js`): deren Shader-Patch ließ am
 * oberen Rand des Stücks eine dunkle Linie stehen (10.10.2026, `Dazgeograftvarianten.hautton`).
 *
 * AUCH AUF DER KATALOG-HAUT (18.10.2026, Edgar: „Figur Matt0 - textur vom Genital wird nicht von der textur des Körpers übernommen", danach „fixe das bei allen
 * Modellen"): Bis dahin galt das alles nur mit gewählter Haut; ohne (`inst.haut` leer) behielt das Stück seine Variante. Gemessen im Chrome an Matt0: „Daz Anatomie Mann"
 * hat keine Variante und keine Karte, nur die Farbe #9f7866 — es stand einfarbig ohne Poren auf den 4096er-Karten von `G9Masculine04`. Jetzt folgt ein Stück OHNE
 * eigene Karte auch der Katalog-Haut. MIT eigener Karte (Varianten der Frau: `Damira_genital`, Ursula, Olesia, Allyne; gebackene Scham eines Imports) behält es sie
 * auf der Katalog-Haut — die Karte IST das Genital (Labien), gebacken aus der glatten Haut darunter war es weg (Regression, Edgar 18.10.2026 abends).
 *
 * Nichts davon wird gespeichert — es wird bei jedem Körperneubau und Anziehen neu abgeleitet (`Genesis9ersatz.nachziehen`). Mit eigener Farbe des Stücks (`werte.farbe`, `gruppenfarben`) gilt es, wie es ist.
 * Die Bilder kommen asynchron: gerechnet wird erst, wenn alle Bilder im Vorrat da sind (`Genesis9texturen.wartenAufAlle`).
 */
export class Anatomiehaut {

    /**
     * Gilt nur noch für eine Haut OHNE Farbkarte (mit Karten folgt das Stück jeder Haut, siehe oben). Ab diesem Farbabstand (ΔE76, `Anatomieton.abstand`) passt der Ton des Stücks nicht mehr zur Haut. Gemessen im Chrome
     * (11.10.2026, Ton des Stücks 183/125/109 = Ursula-Geograft): auf Ursulas eigener Haut ΔE 11,0, auf Damiras heller Haut 8,8 —
     * im Bild unauffällig, das Stück bleibt; auf `G9 Feminine Skin 04` (115/81/62) 22,1, mit dem Damira-Geograft (190/120/105) 24,5 —
     * ein heller Fleck auf dunkler Haut, das Stück geht in den Hautton. Die Schwelle liegt dazwischen (drei Haut-Paare, keine Reihe).
     */
    static TOLERANZ = 15;
    /** So weit (m) um das Stück herum zählt die Haut mit. */
    static RAND_M = 0.04;
    /** Die Gruppen des Körpernetzes, die Haut sind. */
    static HAUT = ['Head', 'Body', 'Arms', 'Legs'];
    /** Höchstens so viele Warterunden (die Bilder eines neuen Körpers kommen in Wellen). */
    static RUNDEN = 6;

    /** Die Stücke der Figur mit Hauttiefe (starre Anatomie): `[{kennung, netz}]`. */
    static stuecke(inst) {
        return Object.entries(inst?.clothMeshes || {})
            .filter(([, netz]) => netz?.userData?.hautTiefe > 0)
            .map(([schluessel, netz]) => ({ kennung: String(schluessel).split('/')[0], netz }));
    }

    /** Alle Materialien eines Netzes. */
    static materialien(netz) {
        const aus = [];
        netz?.traverse?.((kind) => {
            for (const m of [kind.material].flat()) if (m) aus.push(m);
        });
        return aus;
    }

    /** Der Hautton rings um das Stück (linear `[r, g, b]`) — null, solange ein Bild fehlt oder keine Haut in der Nähe liegt. */
    static hautton(inst, netz) {
        const koerper = inst?.bodyMesh, geo = koerper?.geometry;
        if (!geo || !netz?.geometry) return null;
        const kasten = Anatomieton.kasten(netz.geometry, Anatomiehaut.RAND_M);
        const material = [koerper.material].flat();
        const proben = [];
        for (const gruppe of geo.groups || []) {
            const m = material[gruppe.materialIndex];
            if (!Anatomiehaut.HAUT.includes(m?.userData?.gruppe)) continue;
            const punkte = Anatomieton.nahe(geo, gruppe, kasten);
            if (!punkte.size) continue;
            const p = Anatomieton.proben(m, geo.attributes.uv, punkte);
            if (!p) return null;
            proben.push(...p);
        }
        return Anatomieton.median(proben);
    }

    /** Der Ton, den das Material des Stücks zeigt (linear) — null, solange seine Karte fehlt. */
    static eigenton(material, geo) {
        return Anatomieton.median(Anatomieton.proben(material, geo.attributes.uv, Anatomieton.alle(geo)));
    }

    /** Passt `eigen` zu `haut` (beide linear)? Farbabstand höchstens `TOLERANZ`. */
    static passt(eigen, haut) {
        return Anatomieton.abstand(eigen, haut) <= Anatomiehaut.TOLERANZ;
    }

    /** Woran man erkennt, dass sich nichts geändert hat: Haut, Körpernetz, Stücknetze, ihre Variante und Farbe. */
    static stand(inst) {
        return [inst?.haut || '', inst?.bodyMesh?.uuid || '', ...Anatomiehaut.stuecke(inst).map(({ kennung, netz }) =>
            [netz.uuid, inst.kleidung?.[kennung]?.variante || '', inst.kleidung?.[kennung]?.farbe || ''].join('/'))].join('|');
    }

    /**
     * Die Stücke in die Haut setzen oder zurück — sofort; fehlen Bilder, bleibt der Stand, wie er ist. Gibt zurück, ob alles gerechnet wurde.
     * Passt der Ton des Stücks nicht zur Haut, zeigt es die aus der Haut gerechneten Karten (`Anatomiebacken`, Ablage am Material `Anatomiekarten`) — bis sie
     * da sind (der Lauf wird angestoßen, danach `_neu`) und wenn der Körper keine Farbkarte hat oder die Rechnung scheitert, eine einfache Farbe im Hautton.
     */
    static anwenden(inst) {
        let fertig = true;
        for (const { kennung, netz } of Anatomiehaut.stuecke(inst)) {
            const werte = inst.kleidung?.[kennung] || {};
            const eigene = Boolean(werte.farbe) || Object.keys(werte.gruppenfarben || {}).length > 0;
            const haut = eigene ? null : Anatomiehaut.hautton(inst, netz);       // auch die Katalog-Haut (`inst.haut` leer), siehe oben
            if (!eigene && !haut) { fertig = false; continue; }
            const schluessel = haut ? Anatomiekarten.schluessel(inst, netz, Anatomiehaut.HAUT) : null;
            const gebacken = schluessel ? Anatomiekarten.gebacken(netz, schluessel) : null;
            for (const m of Anatomiehaut.materialien(netz)) {
                const ablage = m.userData.anatomieHaut;
                if (ablage && m.map && m.map !== ablage.hautKarte) { ablage.karte = m.map; m.map = null; }   // die EIGENE Karte kam nach dem Umstellen an: wieder weg
                const eigen = Anatomiehaut.eigenton(ablage ? { map: ablage.karte, color: ablage.farbe } : m, netz.geometry);
                if (!eigen) { fertig = false; continue; }
                const bleibt = !inst.haut && Boolean(ablage ? ablage.karte : m.map);    // Katalog-Haut + eigene Karte (Genitalvariante): bleibt, siehe oben
                // Mit Karten der Haut (`schluessel`) folgt das Stück JEDER Haut; nur ohne sie (Haut ohne Farbkarte) entscheidet der Ton.
                if (haut && !bleibt && (schluessel || !Anatomiehaut.passt(eigen, haut))) {
                    if (schluessel && !gebacken) Anatomiebacken.anstossen(inst, netz, Anatomiekarten.original(m), schluessel, Anatomiehaut.HAUT, () => Anatomiehaut._neu(inst));
                    Anatomiehaut._setzen(m, haut, gebacken);
                } else {
                    Anatomiehaut._zurueck(m);    // Zuordnung schon im Hintergrund rechnen: ein Hautwechsel backt danach nur noch die Karten
                    Anatomiebacken.vorrechnen(inst, netz, Anatomiekarten.original(m), Anatomiehaut.HAUT);
                }
            }
        }
        return fertig;
    }

    /** Die gerechneten Karten sind da: beim nächsten `nachziehen` gilt der Stand als verändert. */
    static _neu(inst) {
        inst._anatomieStand = null;
        Anatomiehaut.nachziehen(inst);
    }

    static _setzen(m, ton, gebacken) {
        if (!m.userData.anatomieHaut) m.userData.anatomieHaut = { karte: m.map || null, farbe: m.color.clone() };
        const ablage = m.userData.anatomieHaut;
        if (gebacken && !gebacken.leer) {
            Anatomiekarten.setzen(m, gebacken, ablage);
            return;
        }
        Anatomiekarten.zuruecknehmen(m, ablage);        // vorher Hautkarten, jetzt noch keine (wird gerechnet) oder keine mehr: Normalen und Rauheit des Stücks zurück
        m.map = null;
        m.color.setRGB(ton[0], ton[1], ton[2]);
        m.needsUpdate = true;
    }

    static _zurueck(m) {
        const ablage = m.userData.anatomieHaut;
        if (!ablage) return;
        Anatomiekarten.zuruecknehmen(m, ablage);
        m.map = ablage.karte;
        m.color.copy(ablage.farbe);
        m.needsUpdate = true;
        delete m.userData.anatomieHaut;
    }

    /**
     * Nach jedem Körperneubau und Anziehen (`Genesis9ersatz.nachziehen`, oft aufgerufen): ohne Anatomie-Stück nichts, bei
     * unverändertem Stand nichts, sonst einmal je Figur auf die Bilder warten und anwenden. Ein zweiter Aufruf in der Wartezeit
     * schließt sich dem ersten an.
     */
    static nachziehen(inst) {
        if (!inst || inst._anatomieWartet || !Anatomiehaut.stuecke(inst).length) return null;
        if (inst._anatomieStand === Anatomiehaut.stand(inst)) return null;
        inst._anatomieWartet = Anatomiehaut._warten(inst)
            .catch(fehler => console.warn(`Anatomiehaut: ${fehler.message}`))     // kein Protokoll-Import: bliebe in Node-Tests hängen
            .finally(() => { inst._anatomieWartet = null; });
        return inst._anatomieWartet;
    }

    static async _warten(inst) {
        const { Genesis9texturen } = await import('./genesis9texturen.js');
        for (let runde = 0; runde < Anatomiehaut.RUNDEN; runde++) {
            await Genesis9texturen.wartenAufAlle();
            const stand = Anatomiehaut.stand(inst);
            const fertig = Anatomiehaut.anwenden(inst);
            await Anatomiehaut._randAbgleichen(inst);
            if (fertig) { inst._anatomieStand = stand; return; }
        }
    }

    /**
     * Zeigt das Stück jetzt die Karten der Haut (oder nicht mehr), ändert sich die Angleichung an der Naht (`Hautloch.randAbgleichen`: Relief der Haut, Farbrand
     * des Stücks). Dynamischer Import wie bei den Texturen: `hautloch.js` zieht Three.js und die Shader nach, die die Node-Tests dieser Klasse nicht brauchen.
     */
    static async _randAbgleichen(inst) {
        try {
            const { Hautloch } = await import('./hautloch.js');
            Hautloch.randAbgleichen(inst);
        } catch (fehler) {
            console.warn(`Anatomiehaut: Rand der Naht: ${fehler.message}`);
        }
    }
}
