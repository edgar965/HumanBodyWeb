import { Eigenkleidstoff } from './eigenkleidstoff.js';

/**
 * Eigenkleidfelder — welche Regler ein eigenes Stück hat: Titel, Bereich, Schritt, Vorgabe, Block (Stufe K2a, 25.10.2026). Rechnung und Ablage: `Eigenkleidwerte`.
 *
 * EINHEITEN: `Rumpf`/`Arm`/`Bein` = Anteil der Kette der Körperkoordinaten (`G9koerperkoordinaten`: Rumpf 0 = Halsansatz … 1 = Schritt, Arm 0 = Schulter …
 * 1 = Handgelenk, Bein 0 = Hüfte … 1 = Knöchel); `mm` über der Haut bzw. als Breite; `%`; `Stück`; `wahl` = Index in `wahl`; `farbe` = 0xRRGGBB (`leer`: −1 = keine).
 * Sitz-Korridore der Abnahme: Oberteil 2–30, Hose 1–30, Socken 1–4 mm. Die Vorgaben sind GESETZT (Augenmaß: kurzärmliges T-Shirt mit rundem Ausschnitt, Shorts bis über
 * das Knie, Socken bis zur Wade), nicht gemessen. Ausschnitt, Kragen, Saumband und Brücke: Edgar, 25.10.2026 spät („rund mit saum, oder V-förmig“, „kragen
 * konfiguration mit knöpfen“, „legt sich nicht an der Haut zwischen den Brüsten“). 25.10.2026 nachts: Socken (K2b), Kragen als Geometrie (`Eigenkragen`), Stoff wie am
 * Daz-Stück (`Eigenkleidstoff.FELDER`).
 */
export class Eigenkleidfelder {

    /** Art → Titel, Kategorie der Garderobe (`G9dazkategorien.REIHENFOLGE`), Nummer im Shader (`uKkArt`). */
    static ARTEN = {
        oberteil: { titel: 'Eigenes Oberteil', kategorie: 'Oberteile', nummer: 1 },
        hose: { titel: 'Eigene Hose', kategorie: 'Hosen', nummer: 2 },
        socke: { titel: 'Eigene Socken', kategorie: 'Socken', nummer: 3 },
        rock: { titel: 'Eigener Rock', kategorie: 'Röcke', nummer: 4 },
        kleid: { titel: 'Eigenes Kleid', kategorie: 'Kleider', nummer: 1 },
    };
    /** Kragen als eigene Geometrie (`Eigenkragen`): Index = Wert im Regler `kragen_form`. */
    static KRAGEN = ['ohne', 'Stehkragen', 'Umlegekragen (Polo, Hemd)'];
    static KRAGENFELDER = [
        { feld: 'kragen_form', block: 'kragen', titel: 'Kragen', wahl: Eigenkleidfelder.KRAGEN, vorgabe: 0,
          hilfe: 'Kragen als eigene Fläche am Ausschnittrand: stehend (Stehkragen) oder umgelegt (Polo, Hemd)' },
        { feld: 'kragen_hoehe', block: 'kragen', titel: 'Kragen Höhe', min: 10, max: 80, schritt: 1, vorgabe: 38, einheit: 'mm',
          hilfe: 'Stehkragen: Höhe über dem Ausschnitt; umgelegt: Breite des umgeschlagenen Teils (der Steg darunter ist gut halb so hoch)' },
        { feld: 'kragen_spitze', block: 'kragen', titel: 'Spitzenlänge', min: 0, max: 60, schritt: 1, vorgabe: 14, einheit: 'mm',
          hilfe: 'Wie weit die vorderen Enden des umgelegten Kragens als Spitzen über die Kragenbreite hinausreichen (0 = runde Enden wie am Stehkragen)' },
        { feld: 'kragen_abstand', block: 'kragen', titel: 'Abstand vom Hals', min: 0, max: 20, schritt: 0.5, vorgabe: 3, einheit: 'mm',
          hilfe: 'Luft zwischen Kragen und Hals' },
    ];
    static BLOECKE = [['saeume', 'Säume'], ['kragen', 'Kragen und Knopfleiste'], ['sitz', 'Sitz'], ['bruecke', 'Drapierung über Mulden (zwischen den Brüsten, Rücken)'],
                      ['form', 'Weite und Falten (Ärmel, Rock)'], ['drapieren', 'Drapieren (Rock)'], ['stoff', 'Stoff'], ['textur', 'Textur']];
    /** Rock und Rockteil des Kleids (`Eigenrock`, Stufe K3, 25.10.2026 nachts). Vorgaben gesetzt (knielanger, leicht ausgestellter Rock), nicht gemessen. */
    static ROCKFELDER = [
        { feld: 'laenge', block: 'saeume', titel: 'Rocklänge', min: 0.05, max: 1, schritt: 0.005, vorgabe: 0.42, einheit: 'Bein',
          hilfe: 'Saum des Rocks als Anteil des Beins (Knie ≈ 49 %, 1 = Knöchel)' },
        { feld: 'sitz_rock', block: 'sitz', titel: 'Rock am Bund', min: 1, max: 30, schritt: 0.5, vorgabe: 3, einheit: 'mm', hilfe: 'Abstand des Rocks zur Haut am Bund und an der Hüfte' },
        { feld: 'weite_vorn', block: 'form', titel: 'Weite vorn', min: 0, max: 40, schritt: 0.5, vorgabe: 3, einheit: 'cm', hilfe: 'Wie weit der Saum vorn absteht (ab der Hüfte, linear zum Saum)' },
        { feld: 'weite_hinten', block: 'form', titel: 'Weite hinten', min: 0, max: 40, schritt: 0.5, vorgabe: 5, einheit: 'cm', hilfe: 'Wie weit der Saum hinten absteht' },
        { feld: 'weite_seite', block: 'form', titel: 'Weite seitlich', min: 0, max: 40, schritt: 0.5, vorgabe: 5, einheit: 'cm', hilfe: 'Wie weit der Saum seitlich absteht' },
        { feld: 'falten_zahl', block: 'form', titel: 'Falten', min: 0, max: 40, schritt: 1, vorgabe: 14, einheit: 'Stück', hilfe: 'Eingelegte Falten rundum (Startform fürs Drapieren)' },
        { feld: 'falten_tiefe', block: 'form', titel: 'Faltentiefe', min: 0, max: 60, schritt: 1, vorgabe: 10, einheit: 'mm', hilfe: 'Tiefe der Falten am Saum' },
        { feld: 'steif', block: 'drapieren', titel: 'Steifigkeit', min: 0, max: 100, schritt: 1, vorgabe: 25, einheit: '%',
          hilfe: '0 = weich (fällt senkrecht, wirft die Weite in Falten), 100 = steif (behält die Startform)' },
        { feld: 'gewicht', block: 'drapieren', titel: 'Gewicht', min: 20, max: 200, schritt: 5, vorgabe: 100, einheit: '%', hilfe: 'Schwere des Stoffs beim Fallen' },
        { feld: 'drapiert', block: 'drapieren', titel: 'Drapieren', knopf: true, wahl: ['Grundform', 'drapiert'], vorgabe: 0,
          hilfe: 'Stoff fallen lassen (Schwerkraft, Steifigkeit, Körper als Hülle); bleibt gespeichert und fällt nach jeder Änderung neu' },
    ];
    /** Formen des Halsausschnitts — Index = Wert im Regler und im Shader (`EigenkleidschnittGLSL.kkForm`). */
    static FORMEN = ['rund', 'V-Ausschnitt', 'U-Ausschnitt', 'Boot', 'Stehkragen'];

    /**
     * Wann ein Feld überhaupt wirkt (`werte` = alle Felder des Stücks, `art`) — sonst graut der Kasten es aus (26.10.2026, Edgar: „die Regler, die nicht aktiviert werden können,
     * graue aus (z.B. die bei Stehkragen, wenn kein Stehkragen aktiviert ist)“). Abgelesen am Shader: Stehkragen-Höhe nur mit Ausschnitt „Stehkragen“ (`EigenkleidschnittGLSL`,
     * dort gilt die Tiefe nicht); Knopfleiste nur mit Knöpfen (`uKkKragen.z > 0.5`); Brücke ohne Ausbreitung aus (`kkHub`); der Fall nur an Oberteil und Kleid (`oben`).
     */
    static AKTIV = {
        kragen: w => Math.round(w.ausschnitt_form) === 4,
        ausschnitt: w => Math.round(w.ausschnitt_form) !== 4,
        ausschnitt_hinten: w => Math.round(w.ausschnitt_form) !== 4,
        kragen_hoehe: w => Math.round(w.kragen_form) > 0,
        kragen_abstand: w => Math.round(w.kragen_form) > 0,
        kragen_spitze: w => Math.round(w.kragen_form) === 2,
        leiste: w => Math.round(w.knoepfe) >= 1,
        leiste_breite: w => Math.round(w.knoepfe) >= 1,
        sitz_aermel: w => w.aermel > 0.001,
        aermel_weite: w => w.aermel > 0.001,
        aermel_falten: w => w.aermel > 0.001,
        aermel_faltentiefe: w => w.aermel > 0.001 && Math.round(w.aermel_falten) >= 1,
        abstand: w => w.ausbreitung > 0,
        glaettung: w => w.ausbreitung > 0,
        fall: (w, art) => w.ausbreitung > 0 && art !== 'hose',
        glanzsaum_weich: w => w.glanzsaum > 0,
        glanzsaum_farbe: w => w.glanzsaum > 0,
        faeden: w => Math.round(w.gewebe) > 0,
        struktur: w => Math.round(w.gewebe) > 0,
        falten_tiefe: w => Math.round(w.falten_zahl) >= 1,
        steif: w => w.drapiert >= 0.5,
        gewicht: w => w.drapiert >= 0.5,
    };

    /** Die drei Regler des Drapierers an Hosen (`Genesis9/drapierer.py`), allgemein beschriftet (Edgar, 25.10.2026 spät); Hindernis = Wölbungen der Haut. */
    static BRUECKE = [
        { feld: 'abstand', block: 'bruecke', titel: 'Abstand', min: 0, max: 20, schritt: 0.5, einheit: 'mm', vorgabe: 3,
          hilfe: 'Abstand des Stoffs über der Brücke (über Mulden zwischen Wölbungen: zwischen den Brüsten, Rückenrinne, Nabel, Gesäßfalte)' },
        { feld: 'ausbreitung', block: 'bruecke', titel: 'Ausbreitung', min: 0, max: 60, schritt: 0.5, einheit: 'cm', vorgabe: 12,
          hilfe: 'Wie weit die Brücke von den Wölbungen (Brust, Schulterblätter, Gesäß) seitlich und nach unten reicht; 0 = Stoff liegt überall an' },
        { feld: 'glaettung', block: 'bruecke', titel: 'Glättung', min: 0, max: 100, schritt: 1, einheit: '%', vorgabe: 50,
          hilfe: '0 = straff (gerade gespannt, Zelt), 100 = weich (rund an den Wölbungen)' },
        { feld: 'fall', block: 'bruecke', titel: 'Fall unter Wölbungen', min: 0, max: 100, schritt: 1, einheit: '%', vorgabe: 50,
          hilfe: 'Wie schnell der Stoff unter Brust, Bauch und Gesäß zur Haut zurückkommt: 0 = fällt senkrecht, 50 = einen halben Meter je Meter, 100 = so schnell, wie er tiefer kommt' },
    ];
    static SAUMBREITE = { feld: 'saumbreite', block: 'saeume', titel: 'Saumbreite', min: 0, max: 30, schritt: 0.5, einheit: 'mm',
                          hilfe: 'Breite des Saumbands an allen Rändern (eigene Helligkeit, leichte Wulst); 0 = ohne Saum' };
    static SAUMHELL = { feld: 'saum_hell', block: 'textur', titel: 'Saum heller/dunkler', min: -50, max: 50, schritt: 1, einheit: '%',
                        hilfe: 'Helligkeit des Saumbands gegenüber dem Stoff' };

    static FELDER = {
        oberteil: [
            { feld: 'ausschnitt_form', block: 'saeume', titel: 'Ausschnitt', wahl: Eigenkleidfelder.FORMEN, vorgabe: 0, hilfe: 'Form des Halsausschnitts' },
            { feld: 'ausschnitt', block: 'saeume', titel: 'Tiefe vorn', min: 0, max: 0.4, schritt: 0.005, vorgabe: 0.07, einheit: 'Rumpf',
              hilfe: 'Tiefe des Ausschnitts vorn unter dem Halsansatz' },
            { feld: 'ausschnitt_hinten', block: 'saeume', titel: 'Tiefe hinten', min: 0, max: 0.2, schritt: 0.005, vorgabe: 0.02, einheit: 'Rumpf',
              hilfe: 'Tiefe des Ausschnitts hinten (immer rund)' },
            { feld: 'ausschnitt_breite', block: 'saeume', titel: 'Breite', min: 120, max: 360, schritt: 2, vorgabe: 180, einheit: 'mm',
              hilfe: 'Ganze Breite des Ausschnitts; außerhalb bleibt der Stoff bis zum Halsansatz' },
            { feld: 'saum', block: 'saeume', titel: 'Saum unten', min: 0.3, max: 1, schritt: 0.005, vorgabe: 0.82, einheit: 'Rumpf',
              hilfe: 'Unterer Saum (1 = Schritt); darüber liegende Beinpunkte (Gesäß) deckt das Oberteil mit' },
            { feld: 'aermel', block: 'saeume', titel: 'Ärmellänge', min: 0, max: 1, schritt: 0.005, vorgabe: 0.3, einheit: 'Arm',
              hilfe: 'Ärmel (0 = ärmellos, Schnitt durch das Schultergelenk; Ellbogen ≈ 49 %; 1 = Handgelenk)' },
            { ...Eigenkleidfelder.SAUMBREITE, vorgabe: 8 },
            ...Eigenkleidfelder.KRAGENFELDER,
            { feld: 'kragen', block: 'kragen', titel: 'Stehkragen Höhe', min: 0, max: 60, schritt: 1, vorgabe: 25, einheit: 'mm',
              hilfe: 'Höhe des Stehkragens über dem Halsansatz (nur bei Ausschnitt „Stehkragen“: der Stoff selbst läuft den Hals hinauf, ohne eigene Fläche)' },
            { feld: 'knoepfe', block: 'kragen', titel: 'Knöpfe', min: 0, max: 8, schritt: 1, vorgabe: 0, einheit: 'Stück', hilfe: 'Anzahl Knöpfe der Knopfleiste (0 = keine Leiste)' },
            { feld: 'leiste', block: 'kragen', titel: 'Knopfleiste Länge', min: 0.03, max: 0.6, schritt: 0.005, vorgabe: 0.18, einheit: 'Rumpf',
              hilfe: 'Länge der Knopfleiste vom Ausschnitt abwärts' },
            { feld: 'leiste_breite', block: 'kragen', titel: 'Knopfleiste Breite', min: 14, max: 50, schritt: 1, vorgabe: 28, einheit: 'mm', hilfe: 'Breite der Knopfleiste' },
            { feld: 'sitz_oben', block: 'sitz', titel: 'Rumpf oben', min: 2, max: 30, schritt: 0.5, vorgabe: 3, einheit: 'mm', hilfe: 'Abstand zur Haut an Schultern und Brust' },
            { feld: 'sitz_mitte', block: 'sitz', titel: 'Rumpf Mitte', min: 2, max: 30, schritt: 0.5, vorgabe: 6, einheit: 'mm', hilfe: 'Abstand zur Haut an der Taille' },
            { feld: 'sitz_unten', block: 'sitz', titel: 'Rumpf unten', min: 2, max: 30, schritt: 0.5, vorgabe: 9, einheit: 'mm', hilfe: 'Abstand zur Haut am Saum' },
            { feld: 'sitz_aermel', block: 'sitz', titel: 'Ärmel', min: 2, max: 30, schritt: 0.5, vorgabe: 6, einheit: 'mm', hilfe: 'Abstand zur Haut am Ärmel' },
            // Ärmel-Drapierung (Edgar, 25.10.2026 nachts: „an den Ärmeln fehlt die Drapierung - mehr falten, nicht so eng“, „sollte einstellbar sein“); Vorgaben gesetzt
            { feld: 'aermel_weite', block: 'form', titel: 'Ärmel: Weite am Saum', min: 0, max: 60, schritt: 1, vorgabe: 10, einheit: 'mm',
              hilfe: 'Wie weit der Ärmel zum Saum hin vom Arm absteht (wächst von der Schulter an, der Ärmel hängt)' },
            { feld: 'aermel_falten', block: 'form', titel: 'Ärmel: Falten', min: 0, max: 16, schritt: 1, vorgabe: 6, einheit: 'Stück', hilfe: 'Längsfalten rund um den Ärmel' },
            { feld: 'aermel_faltentiefe', block: 'form', titel: 'Ärmel: Faltentiefe', min: 0, max: 30, schritt: 0.5, vorgabe: 4, einheit: 'mm',
              hilfe: 'Tiefe der Ärmelfalten am Saum (zur Schulter hin flacher)' },
            // Oberteil hängt wie ein lockeres Shirt (Edgar, 26.10.2026 nachts: „Nimm z.B. Asian Female Shirt, die Drapierung soll so weit gehen, dass keine Körperformen
            // erkennbar sind“) — mit 12 cm / 50 % zeichnete sich die Brust samt Unterkante ab (im Chrome gesehen); die Hose behält die Vorgaben des Drapierers
            ...Eigenkleidfelder.BRUECKE.map(f => ({ ausbreitung: { ...f, vorgabe: 30 }, fall: { ...f, vorgabe: 20 } }[f.feld] || f)),
            { feld: 'falten', block: 'stoff', titel: 'Faltenstärke', min: 0, max: 100, schritt: 1, vorgabe: 35, einheit: '%',
              hilfe: 'Falten quer zur Kette; wo der Stoff von einer Brücke hängt, senkrecht' },
            { feld: 'rauheit', block: 'stoff', titel: 'Rauheit', min: 0, max: 100, schritt: 1, vorgabe: 85, einheit: '%', hilfe: 'Rauheit des Stoffs (0 = glänzend)' },
            ...Eigenkleidstoff.FELDER,
            { feld: 'farbe', block: 'textur', titel: 'Farbe', farbe: true, vorgabe: 0x3b5f8c, hilfe: 'Farbe des Stoffs' },
            { ...Eigenkleidfelder.SAUMHELL, vorgabe: -12 },
        ],
        hose: [
            { feld: 'bund', block: 'saeume', titel: 'Bund', min: 0.4, max: 0.95, schritt: 0.005, vorgabe: 0.66, einheit: 'Rumpf',
              hilfe: 'Höhe des Bunds (0 = Halsansatz, 1 = Schritt)' },
            { feld: 'bein', block: 'saeume', titel: 'Beinlänge', min: 0.12, max: 1, schritt: 0.005, vorgabe: 0.4, einheit: 'Bein',
              hilfe: 'Hosenbein (Knie ≈ 49 %, 1 = Knöchel). Unter 12 % liefe die Kante in die Grenze Rumpf/Bein der Karte und würde zackig' },
            { ...Eigenkleidfelder.SAUMBREITE, max: 50, vorgabe: 14, hilfe: 'Breite von Bund und Beinsaum (eigene Helligkeit, leichte Wulst); 0 = ohne' },
            { feld: 'sitz_bund', block: 'sitz', titel: 'Bund', min: 1, max: 30, schritt: 0.5, vorgabe: 2, einheit: 'mm', hilfe: 'Abstand zur Haut am Bund' },
            { feld: 'sitz_gesaess', block: 'sitz', titel: 'Gesäß', min: 1, max: 30, schritt: 0.5, vorgabe: 5, einheit: 'mm', hilfe: 'Abstand zur Haut an Gesäß und Schritt' },
            { feld: 'sitz_bein', block: 'sitz', titel: 'Bein', min: 1, max: 30, schritt: 0.5, vorgabe: 8, einheit: 'mm', hilfe: 'Abstand zur Haut am Hosenbein' },
            ...Eigenkleidfelder.BRUECKE,
            { feld: 'falten', block: 'stoff', titel: 'Faltenstärke', min: 0, max: 100, schritt: 1, vorgabe: 25, einheit: '%', hilfe: 'Falten quer zur Kette' },
            { feld: 'rauheit', block: 'stoff', titel: 'Rauheit', min: 0, max: 100, schritt: 1, vorgabe: 80, einheit: '%', hilfe: 'Rauheit des Stoffs (0 = glänzend)' },
            ...Eigenkleidstoff.FELDER,
            { feld: 'farbe', block: 'textur', titel: 'Farbe', farbe: true, vorgabe: 0x34343c, hilfe: 'Farbe des Stoffs' },
            { ...Eigenkleidfelder.SAUMHELL, vorgabe: -12 },
        ],
        socke: [
            { feld: 'buendchen', block: 'saeume', titel: 'Bündchen', min: 0.3, max: 0.97, schritt: 0.005, vorgabe: 0.8, einheit: 'Bein',
              hilfe: 'Oberer Rand der Socke als Anteil des Beins (Knie ≈ 49 %, Wade ≈ 65–80 %, Knöchel ≈ 95 %); der Fuß ist immer ganz bedeckt' },
            { ...Eigenkleidfelder.SAUMBREITE, titel: 'Bündchenbreite', max: 40, vorgabe: 15, hilfe: 'Breite des Bündchens (eigene Helligkeit, leichte Wulst); 0 = ohne' },
            { feld: 'sitz_fuss', block: 'sitz', titel: 'Fuß', min: 1, max: 4, schritt: 0.25, vorgabe: 1.5, einheit: 'mm',
              hilfe: 'Abstand zur Haut am Fuß (Korridor der Abnahme für Socken: 1–4 mm)' },
            { feld: 'sitz_bein', block: 'sitz', titel: 'Schaft', min: 1, max: 4, schritt: 0.25, vorgabe: 2, einheit: 'mm', hilfe: 'Abstand zur Haut am Schaft (Knöchel bis Bündchen)' },
            { feld: 'falten', block: 'stoff', titel: 'Faltenstärke', min: 0, max: 100, schritt: 1, vorgabe: 10, einheit: '%', hilfe: 'Falten quer zum Bein' },
            { feld: 'rauheit', block: 'stoff', titel: 'Rauheit', min: 0, max: 100, schritt: 1, vorgabe: 90, einheit: '%', hilfe: 'Rauheit des Stoffs (0 = glänzend)' },
            ...Eigenkleidstoff.FELDER,
            { feld: 'farbe', block: 'textur', titel: 'Farbe', farbe: true, vorgabe: 0xe4e4e0, hilfe: 'Farbe des Stoffs' },
            { ...Eigenkleidfelder.SAUMHELL, vorgabe: -8 },
        ],
        rock: [
            { feld: 'bund', block: 'saeume', titel: 'Bund', min: 0.3, max: 0.95, schritt: 0.005, vorgabe: 0.62, einheit: 'Rumpf',
              hilfe: 'Höhe des Bunds (0 = Halsansatz, 1 = Schritt; Taille ≈ 55 %)' },
            ...Eigenkleidfelder.ROCKFELDER,
            { feld: 'rauheit', block: 'stoff', titel: 'Rauheit', min: 0, max: 100, schritt: 1, vorgabe: 80, einheit: '%', hilfe: 'Rauheit des Stoffs (0 = glänzend)' },
            ...Eigenkleidstoff.FELDER,
            { feld: 'farbe', block: 'textur', titel: 'Farbe', farbe: true, vorgabe: 0x2f3a56, hilfe: 'Farbe des Stoffs' },
        ],
    };

    // Kleid = Oberteil (Saum an der Taille, Schale mit Ausschnitt, Ärmeln, Kragen) + Rockteil (`Eigenrock`, setzt am Saum an) in einer Farbe und einem Stoff
    static {
        // Brücke straffer und bis zur Taille (Edgar, 25.10.2026 nachts, mit Bild: „das Kleid ist schon sehr gut, nur bei den Brüsten fehlt die Drapierung“ — mit den
        // T-Shirt-Vorgaben 12 cm / 50 % lag das Oberteil unter und zwischen den Brüsten an); gesetzt, im Chrome angesehen
        const kleid = { saum: { vorgabe: 0.55, hilfe: 'Taille des Kleids: hier setzt der Rockteil an' }, farbe: { vorgabe: 0x6b2b3a }, ausbreitung: { vorgabe: 45 }, glaettung: { vorgabe: 10 }, fall: { vorgabe: 20 },
                        aermel_weite: { vorgabe: 25 }, aermel_falten: { vorgabe: 7 }, aermel_faltentiefe: { vorgabe: 8 } };
        const oben = Eigenkleidfelder.FELDER.oberteil.map(f => (kleid[f.feld] ? { ...f, ...kleid[f.feld] } : f));
        Eigenkleidfelder.FELDER.kleid = [...oben, ...Eigenkleidfelder.ROCKFELDER];
    }
}
