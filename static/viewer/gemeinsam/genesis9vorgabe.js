/**
 * Genesis9vorgabe — einen Katalogeintrag auf ein Genesis9Modell legen, das nur seinen Namen kennt.
 *
 * Studio und Theatre kennen von einem gespeicherten Modell nur den Namen (17.09.2026): Regler
 * kommen immer aus dem Eintrag, bei einem GESPEICHERTEN Modell dazu Haut, Augen, Brauen,
 * Schminke, Pose, Kleidung und seit 27.09.2026 die Fotokacheln — jeweils nur, soweit am Modell
 * noch nichts gesetzt ist. Aus `genesis9modell.js` herausgelöst, als die Fotokacheln dazukamen
 * (die Datei stand bei 360 Zeilen).
 */
export class Genesis9vorgabe {

    static uebernehmen(modell, eintrag) {
        modell.regler = { ...(eintrag?.regler || {}) };
        if (!eintrag?.gespeichert) return;
        const leer = wert => !Object.keys(wert || {}).length;
        if (!modell.haut) modell.haut = eintrag.haut || '';
        if (modell.augen === '01' && eintrag.augen) modell.augen = eintrag.augen;
        if (eintrag.augen_gewaehlt) modell._augenGewaehlt = true;   // die gespeicherte Augenwahl gilt vor Fotokachel und Ersatz-Augen
        if (!modell.brauen) modell.brauen = eintrag.brauen || '';
        if (!modell.brauenstil) modell.brauenstil = eintrag.brauenstil || '';
        if (leer(modell.praesets)) modell.praesets = { ...(eintrag.praesets || {}) };
        if (leer(modell.hautmischung)) modell.hautmischung = { ...(eintrag.hautmischung || {}) };
        if (leer(modell.teilmaterial)) modell.teilmaterial = { ...(eintrag.teilmaterial || {}) };
        if (!modell.pose) modell.pose = eintrag.pose || '';
        if (!modell.ausdruck) modell.ausdruck = eintrag.ausdruck || '';
        if (leer(modell.kleidung)) modell.kleidung = { ...(eintrag.kleidung || {}) };
        if (leer(modell.fototextur)) modell.fototextur = { ...(eintrag.fototextur || {}) };
    }
}
