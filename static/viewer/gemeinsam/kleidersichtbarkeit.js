/**
 * Kleidersichtbarkeit — „Kleider ein/aus" überlebt den Neubau der Stücke (11.10.2026).
 *
 * Edgar: „Der Toggle Kleider ein/aus funktioniert nicht bei den Genesis Modellen." Gemessen im Chrome (Ursula1, `ProjektTemp/_wegwerf`-Probe): Der Schalter
 * setzt `visible = false` an allen Netzen von `inst.clothMeshes` — sofort stimmt das. Beim Wechsel vom groben aufs feine Netz (Stufe 1, nach ~30 s) zieht aber
 * `Genesis9kleidung.anziehen` jedes Stück NEU an: neue Netze, `visible` wieder `true`, der Knopf zeigt weiter „aus". Dasselbe bei jedem Reglerzug, Hautwechsel
 * mit neuem Skelett (`Genesis9Modell._kleiderBinden`), bei Frisur und Daz-Kleidung.
 *
 * Regel hier: ein neu gebautes Netz erbt die Sichtbarkeit des Netzes, das es ersetzt (auch eine einzeln ausgeblendete Hose bleibt aus); ein Stück, das es noch nicht gab,
 * folgt dem Schalter (`inst.kleiderSichtbar`, gesetzt von `menubar.js`; ohne Schalter: sichtbar).
 */
export class Kleidersichtbarkeit {

    /**
     * Ist das Netz ein Teil des KÖRPERS und keine Kleidung? Ein starres Anatomie-Stück (Scham aus einer .blend, `userData.hautTiefe` > 0) liegt in `clothMeshes`,
     * weil es wie ein Kleidungsstück an die Figur gebunden wird — „Kleider aus" lässt es trotzdem stehen (Edgar, 12.10.2026, mit Bild: „bei cute Girl Daz gar keine neue
     * Scham", nachdem er die Kleider über den Knopf ausgeschaltet hatte: das Stück war weg, das Loch in der Haut zu, und die eingebaute Körper-Scham kam zum Vorschein).
     * Ebenso ein Stück, das Teile der Figur ERSETZT (`userData.ersetzt`, die Originalaugen — `Genesis9ersatz`): die Augen der Figur sind dafür schon ausgeblendet,
     * mit dem Stück wären es leere Höhlen (Edgar, 12.10.2026: „bei dem Push auf den Kleider disable Button verschwinden die Augen").
     */
    static istKoerperteil(netz) {
        return netz?.userData?.hautTiefe > 0 || netz?.userData?.ersetzt?.length > 0;
    }

    /** Der Schalter „Kleider" gilt für diese Figur: `an = false` heißt, neue Stücke entstehen unsichtbar. */
    static setzen(inst, an) {
        if (inst) inst.kleiderSichtbar = !!an;
    }

    /**
     * Alle Stücke der Figur nach dem Schalter ein- oder ausblenden — Körperteile (`istKoerperteil`) bleiben sichtbar. Ausnahme: Ersatz-Augen, die die gewählten
     * Augen der Figur verdrängt haben (`userData.ersatzGewichen`, `Genesis9ersatz`) — sie blieben sonst als zweites Paar neben den gewählten stehen.
     */
    static anwenden(inst, an) {
        for (const netz of Object.values(inst?.clothMeshes || {})) {
            if (netz) netz.visible = Kleidersichtbarkeit.istKoerperteil(netz) ? !netz.userData.ersatzGewichen : !!an;
        }
        // Eigene Stücke (Schale, Kragen, Rock; `userData.eigenkleid`, Stufe K5, 25.10.2026) stehen nicht in `clothMeshes`, sondern neben dem Körper
        inst?.bodyMesh?.parent?.traverse((netz) => { if (netz.userData?.eigenkleid) netz.visible = !!an; });
    }

    /**
     * Soll ein Netz des Stücks `name` sichtbar entstehen? `name` ist der Schlüssel in `inst.clothMeshes` ohne die Teilnummer
     * (`kennung`, `dazkleidung:kennung`, `frisur`) oder ein ganzer Schlüssel. Gibt es das Stück schon, gilt sein Stand (sichtbar, wenn ein Teil sichtbar ist);
     * sonst der Schalter. Vor dem Entfernen der alten Netze aufrufen.
     */
    static fuer(inst, name) {
        const alt = Object.entries(inst?.clothMeshes || {}).filter(([schluessel, netz]) => netz && (schluessel === name || schluessel.startsWith(`${name}/`)));
        if (alt.length) return alt.some(([, netz]) => Kleidersichtbarkeit.istKoerperteil(netz) || netz.visible !== false);
        return inst?.kleiderSichtbar !== false;
    }
}
