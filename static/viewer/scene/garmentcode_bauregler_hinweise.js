/**
 * Die Hover-Texte der Bauregler — herausgelöst aus
 * `garmentcode_bauregler.js` (11.09.2026), als der Regler „An die Haut
 * ziehen" dazukam und die Datei über 243 Zeilen ging.
 *
 * Was die Regler tun — im Klartext, nicht als Parametername.
 *
 * Edgar, 09.09.2026: „die Hover texte verständlich, z.B. bei Netzfeinheit
 * die Info was das ist, und Auswirkung auf Rechenzeit usw." Jeder Text
 * sagt dasselbe in derselben Reihenfolge: WAS es ist, was HOCH bewirkt,
 * was RUNTER bewirkt, was es KOSTET.
 */
export const BAUREGLER_HINWEISE = {
    'gc-hautabstand':
        'Wie weit der Stoff nach der Simulation mindestens vor der Haut '
        + 'liegen soll. Höher: kein Durchscheinen der Haut, aber das '
        + 'Stück steht sichtbar ab. Niedriger: liegt enger an, dafür '
        + 'können Brustwarze, Nabel oder Knie durch den Stoff stoßen. '
        + 'Kostet keine Rechenzeit — die Korrektur läuft nach der '
        + 'Simulation. 1,0 mm ist die Vorgabe: Gemessen an drei Stücken '
        + 'räumt sie genauso viele durchstehende Stellen weg wie die '
        + '6,0 mm von vorher, ohne deren 2,5 mm Aufschlag. Achtung: Wie '
        + 'eng es überhaupt werden KANN, entscheidet nicht dieser '
        + 'Regler, sondern der Kollisionsabstand der Simulation (im '
        + 'Bereich „Simulation" darunter, Vorgabe 0,05 cm).',
    'gc-aufloesung':
        'Wie fein das Stoffnetz für die Simulation vernäht wird — die '
        + 'Zahl der Stoffpunkte, nicht die Bildauflösung. Höher: feinere '
        + 'Falten und weniger Durchstich, weil eine Wölbung von 2,5 mm '
        + 'nicht mehr zwischen zwei Stoffpunkten verschwindet (bei 1,0 '
        + 'ist das Netz am Oberschenkel rund 1 cm grob). Niedriger: '
        + 'gröber und schneller. Kostet Rechenzeit: Ein T-Shirt braucht '
        + 'bei 1,0 gemessen rund 17 bis 23 s, und die Zeit wächst mit '
        + 'der Zahl der Punkte. Bei hohen Werten muss „Netzbau '
        + 'höchstens (s)" darunter mitwachsen, sonst bricht der Bau ab.',
    'gc-anliegen':
        'Zieht das fertige Stück NACH der Simulation auf diesen Abstand an die '
        + 'Haut — überall, auch dort, wo der Schnitt weit ist. Das ist die '
        + 'Leggings-Einstellung: GarmentCode schneidet ein Hosenbein mit 5 cm '
        + 'Zugabe und gerade zum Saum, enger geht der Schnitt nicht (gemessen '
        + '20 cm Luft am Knie). Eine Hose wird vorher hochgezogen: Schritt an '
        + 'den Schritt, Saum nicht unter die Ferse. 0 = aus. Höher: mehr Abstand. '
        + 'Preis: Falten der Simulation werden glattgezogen und der überschüssige '
        + 'Stoff rückt zusammen — für Röcke und weite Hosen der falsche Schritt. '
        + 'Kostet rund eine Sekunde.',
};
