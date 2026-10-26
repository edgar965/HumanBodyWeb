/**
 * Dazschnittfelder — welche Eigen-Regler ein Daz-Stück hat: Ausschnitt und Säume NUR als Wegschneiden, Saumband, Kragen und Knopfleiste als Abziehbild
 * (Stufe K2c, 25.10.2026, Edgar: „könnte man diese Einstellungen auch an alle existierenden Genesis-Teile anhängen? Dann bei allen Eigenschaften eines
 * Genesis-Kleidungsstückes einen Regler, der diese ‚Eigen‘-Regler aufmacht?“). Rechnung und Ablage: `Dazschnittwerte`; Vorbild: `Eigenkleidfelder` (K2a).
 *
 * ANDERS ALS BEIM EIGENEN STÜCK: Ein Daz-Stück hat seine Form schon. Jeder Schnitt nimmt nur weg (Flächen und Pixel jenseits der Kante), nichts wird angebaut —
 * deshalb kein Stehkragen, kein Sitz, kein längerer Saum. Jeder Schnitt hat einen Wert „wie geliefert“ (`aus`, das Ende seines Bereichs, und die Vorgabe):
 * an diesem Wert schneidet er nichts. Ein Stück, an dem niemand dreht, bleibt unverändert und kostet nichts.
 *
 * EINHEITEN wie bei den eigenen Stücken (`G9koerperkoordinaten`): `Rumpf` = Rumpfhöhe (0 Halsansatz … 1 Schritt, darunter weiter: Knie ≈ 1,45),
 * `Arm`/`Bein` = Anteil der Kette (Ellbogen ≈ 0,49, Handgelenk 1; Knie ≈ 0,49, Knöchel 1). Vorgaben der Abziehbilder GESETZT (Augenmaß), nicht gemessen.
 * Die Werte stehen als `schnitt:<feld>` in den Reglern des Stücks (`inst.kleidung[kennung].regler`) — sie reisen mit „Modell speichern“, gehen aber nicht an
 * den Server (`Dazschnittwerte.ohne`).
 */
export class Dazschnittfelder {

    static PRAEFIX = 'schnitt:';
    /** Formen des Halsausschnitts; Index 0 = wie geliefert, sonst Form = Index − 1 wie `EigenkleidschnittGLSL.kkForm` (ohne Stehkragen: der baute an). */
    static FORMEN = ['wie geliefert', 'rund', 'V-Ausschnitt', 'U-Ausschnitt', 'Boot'];
    static BLOECKE = [['ausschnitt', 'Ausschnitt (nur wegschneiden)'], ['saeume', 'Säume (nur wegschneiden)'],
                      ['kragen', 'Kragen und Knopfleiste (Abziehbild)']];

    /** Welche Gruppen von Feldern zu welcher Kategorie der Garderobe gehören; fehlt die Kategorie: alle. */
    static OBEN = ['ausschnitt', 'saum', 'aermel', 'band'];
    static UNTEN = ['bund', 'bein', 'band'];
    static JE_KATEGORIE = {
        'Oberteile': Dazschnittfelder.OBEN, 'Hosen': Dazschnittfelder.UNTEN, 'Shorts': Dazschnittfelder.UNTEN,
        'Röcke': ['bund', 'saum', 'band'], 'Unterwäsche': ['ausschnitt', 'saum', 'bund', 'bein', 'band'],
    };

    static FELDER = [
        { feld: 'ausschnitt_form', gruppe: 'ausschnitt', block: 'ausschnitt', titel: 'Ausschnitt', wahl: Dazschnittfelder.FORMEN, vorgabe: 0, aus: 0,
          hilfe: 'Form des Halsausschnitts; „wie geliefert“ schneidet nichts' },
        { feld: 'ausschnitt', gruppe: 'ausschnitt', block: 'ausschnitt', titel: 'Tiefe vorn', min: 0, max: 0.4, schritt: 0.005, vorgabe: 0.07, einheit: 'Rumpf',
          hilfe: 'Tiefe des Ausschnitts vorn unter dem Halsansatz; auch Anfang der Knopfleiste' },
        { feld: 'ausschnitt_hinten', gruppe: 'ausschnitt', block: 'ausschnitt', titel: 'Tiefe hinten', min: 0, max: 0.2, schritt: 0.005, vorgabe: 0.02,
          einheit: 'Rumpf', hilfe: 'Tiefe des Ausschnitts hinten (immer rund)' },
        { feld: 'ausschnitt_breite', gruppe: 'ausschnitt', block: 'ausschnitt', titel: 'Breite', min: 120, max: 360, schritt: 2, vorgabe: 180, einheit: 'mm',
          hilfe: 'Ganze Breite des Ausschnitts; außerhalb fällt nur weg, was über dem Halsansatz liegt' },
        { feld: 'saum', gruppe: 'saum', block: 'saeume', titel: 'Saum unten', min: 0.3, max: 2.3, schritt: 0.005, vorgabe: 2.3, aus: 2.3, einheit: 'Rumpf',
          hilfe: 'Alles unter dieser Rumpfhöhe fällt weg (1 = Schritt, Knie ≈ 1,45); ganz rechts: wie geliefert' },
        { feld: 'aermel', gruppe: 'aermel', block: 'saeume', titel: 'Ärmellänge', min: 0, max: 1.2, schritt: 0.005, vorgabe: 1.2, aus: 1.2, einheit: 'Arm',
          hilfe: 'Ärmel kürzen (0 = ärmellos, Ellbogen ≈ 49 %, 1 = Handgelenk); ganz rechts: wie geliefert' },
        { feld: 'bund', gruppe: 'bund', block: 'saeume', titel: 'Bund tiefer', min: -0.1, max: 0.95, schritt: 0.005, vorgabe: -0.1, aus: -0.1, einheit: 'Rumpf',
          hilfe: 'Alles über dieser Rumpfhöhe fällt weg (0 = Halsansatz, 1 = Schritt); ganz links: wie geliefert' },
        { feld: 'bein', gruppe: 'bein', block: 'saeume', titel: 'Hosenbein', min: 0.12, max: 1.2, schritt: 0.005, vorgabe: 1.2, aus: 1.2, einheit: 'Bein',
          hilfe: 'Hosenbein kürzen (Knie ≈ 49 %, 1 = Knöchel); ganz rechts: wie geliefert' },
        { feld: 'saumbreite', gruppe: 'band', block: 'saeume', titel: 'Saumband', min: 0, max: 30, schritt: 0.5, vorgabe: 0, einheit: 'mm',
          hilfe: 'Band an den neuen Schnittkanten (eigene Helligkeit, leichte Wulst, Steppnaht); 0 = ohne' },
        { feld: 'kragen', gruppe: 'ausschnitt', block: 'kragen', titel: 'Kragenband', min: 0, max: 60, schritt: 1, vorgabe: 0, einheit: 'mm',
          hilfe: 'Gezeichneter Kragen entlang des Ausschnitts (nur Textur und Relief, keine Geometrie); 0 = ohne' },
        { feld: 'knoepfe', gruppe: 'ausschnitt', block: 'kragen', titel: 'Knöpfe', min: 0, max: 8, schritt: 1, vorgabe: 0, einheit: 'Stück',
          hilfe: 'Gezeichnete Knopfleiste vorn ab der Tiefe des Ausschnitts (0 = keine Leiste)' },
        { feld: 'leiste', gruppe: 'ausschnitt', block: 'kragen', titel: 'Knopfleiste Länge', min: 0.03, max: 0.6, schritt: 0.005, vorgabe: 0.18, einheit: 'Rumpf',
          hilfe: 'Länge der Knopfleiste' },
        { feld: 'leiste_breite', gruppe: 'ausschnitt', block: 'kragen', titel: 'Knopfleiste Breite', min: 14, max: 50, schritt: 1, vorgabe: 28, einheit: 'mm',
          hilfe: 'Breite der Knopfleiste' },
        { feld: 'saum_hell', gruppe: 'band', block: 'kragen', titel: 'Saum heller/dunkler', min: -50, max: 50, schritt: 1, vorgabe: -12, einheit: '%',
          hilfe: 'Helligkeit des Saumbands gegenüber dem Stoff' },
        { feld: 'kragen_hell', gruppe: 'ausschnitt', block: 'kragen', titel: 'Kragen heller/dunkler', min: -50, max: 50, schritt: 1, vorgabe: -8, einheit: '%',
          hilfe: 'Helligkeit des Kragenbands gegenüber dem Stoff' },
    ];

    static angaben(feld) {
        return Dazschnittfelder.FELDER.find(f => f.feld === feld) || null;
    }

    /** Die Felder für ein Stück der Kategorie `kategorie` (Garderobe, `G9dazkategorien`). */
    static fuer(kategorie) {
        const gruppen = Dazschnittfelder.JE_KATEGORIE[kategorie];
        return gruppen ? Dazschnittfelder.FELDER.filter(f => gruppen.includes(f.gruppe)) : Dazschnittfelder.FELDER;
    }
}
