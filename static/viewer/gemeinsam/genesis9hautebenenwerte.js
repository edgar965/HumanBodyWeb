/**
 * Genesis9hautebenenwerte — die Regler der Hautebenen und was aus ihren Werten wird (17.10.2026), ohne Three.js und ohne Browser (in Node prüfbar).
 *
 * Die Werte liegen je Figur in `inst.hautebenen = {name: Prozent}` (`Genesis9hautebenen`); hier stehen die Felder (Titel, Bereich, Hilfe) für das Bedienfeld und die Rechnung
 * `wirksam`: Prozent → Anteile, mit der Kopplung ans Alter. Altersflecken und graue Haare folgen dem Alterswert (`Genesis9hautfalten.alter`, 0…1): der Regler addiert nichts, er
 * hebt nur an (Maximum aus Regler und Alter). Altersflecken beginnen bei Alterswert 0,2 (rund 38 Jahre) und stehen bei 0,8 voll; graue Haare ab 0,23 (40 Jahre) bis 1 (90 Jahre) —
 * gesetzt, nicht gemessen (Tabelle 5 und 7 in `genesis9-alter.md`: kein System auf der Platte tut es).
 */
export class Genesis9hautebenenwerte {

    /** Die Regler: Name, Titel, Bereich in Prozent, Hilfe. Reihenfolge = Reihenfolge im Bedienfeld. */
    static FELDER = [
        { name: 'ton', titel: 'Hautton (heller … dunkler)', min: -100, max: 100, gruppe: 'Haut',
          hilfe: 'Mehr Melanin: dunkler und gesättigter (Potenz auf die Albedo). Wirkt relativ auf jeden Hautsatz, auch auf einen schon dunklen. Die Streufarbe des Durchlichts wandert mit (dunkel: tiefes Rot, hell: Rosa).' },
        { name: 'roetung', titel: 'Blässe … Rötung', min: -100, max: 100, gruppe: 'Haut', hilfe: 'Links entsättigt und hellt etwas auf, rechts mehr Rot und weniger Grün/Blau.' },
        { name: 'sommer', titel: 'Sommersprossen', min: 0, max: 100, gruppe: 'Flecken',
          hilfe: 'Körper nach MB-Labs Sommersprossenmaske, Gesicht (Nase, Wangen, Stirnrand) gesetzt. Die Punkte entstehen im Shader, jeder Zug zeichnet sie neu.' },
        { name: 'sommer_groesse', titel: 'Sommersprossen: Größe', min: 25, max: 200, standard: 100, gruppe: 'Flecken', hilfe: '100 % = rund 2 mm.' },
        { name: 'altersflecken', titel: 'Altersflecken', min: 0, max: 100, gruppe: 'Flecken',
          hilfe: 'Handrücken, Unterarme, Stirn, Schläfen, Schultern. Folgt dem Alter (ab rund 38 Jahren); der Regler hebt es an.' },
        { name: 'muskel', titel: 'Muskelzeichnung', min: 0, max: 100, gruppe: 'Relief',
          hilfe: 'Muskeltrennlinien aus MB-Labs Verschiebungsbild (Kanal B) als Normalenschicht.' },
        { name: 'fett', titel: 'Fettzeichnung', min: 0, max: 100, gruppe: 'Relief', hilfe: 'Fettgewebe aus MB-Labs Verschiebungsbild (Kanal A) als Normalenschicht.' },
        { name: 'mimik', titel: 'Mimikfalten (Stärke)', min: 0, max: 200, standard: 100, gruppe: 'Relief',
          hilfe: 'Die 27 FACS-Details (Brauen, Lidfalten, Nasenrümpfen, Lippen, Kinn) als Normalen auf dem Kopf — sichtbar, sobald ein Ausdruck oder ein Mimikregler gestellt ist. 0 = aus.' },
        { name: 'ergrauen', titel: 'Graue Haare (Haar und Brauen)', min: 0, max: 100, gruppe: 'Haar',
          hilfe: 'Soviel Prozent der Strähnen werden grau-weiß, an der Wurzel zuerst. Folgt dem Alter (ab rund 40 Jahren); der Regler hebt es an.' },
    ];

    static standard(name) {
        return Genesis9hautebenenwerte.FELDER.find(f => f.name === name)?.standard ?? 0;
    }

    /** Der gestellte Wert in Prozent (Standard, wenn nichts gestellt ist). */
    static wert(inst, name) {
        const w = Number(inst?.hautebenen?.[name]);
        return Number.isFinite(w) ? w : Genesis9hautebenenwerte.standard(name);
    }

    static glatt(x) {
        const t = Math.min(1, Math.max(0, x));
        return t * t * (3 - 2 * t);
    }

    // ------------------------------------------------------------ Mimikfalten

    /** Die Zahl der Zellen im Atlas der Mimikfalten (`G9mimikfalten`: 27 FACS-Details) und das Merkmal ihrer Kanalnamen. */
    static MIMIK_ANZAHL = 27;
    static MIMIK_MUSTER = 'FACSDetails';

    /** Hat diese Stellung ein FACS-Detail mit Wert (`inst.hdwerte` der Netzantwort) — und will der Nutzer Mimikfalten (Regler > 0)? */
    static mimikAktiv(inst, regler) {
        if (!(regler > 0)) return false;
        return Object.entries(inst?.hdwerte || {}).some(([name, wert]) => name.includes(Genesis9hautebenenwerte.MIMIK_MUSTER) && Math.abs(Number(wert)) > 1e-3);
    }

    /** Die Gewichte in der Reihenfolge der Atlaszellen (`kanaele` aus der Liste des Servers) ins Feld `ziel` (0 für alles, was nicht in der Liste steht), höchstens 1,5. */
    static mimikGewichte(inst, kanaele, ziel) {
        ziel.fill(0);
        (kanaele || []).forEach((name, i) => {
            if (i < ziel.length) ziel[i] = Math.min(1.5, Math.max(0, Number(inst?.hdwerte?.[name]) || 0));
        });
        return ziel;
    }

    /** Die wirksamen Werte (−1…1 bzw. 0…1) bei diesem Alterswert (0…1). */
    static wirksam(inst, alter) {
        const p = name => Genesis9hautebenenwerte.wert(inst, name) / 100;
        return {
            ton: p('ton'), roetung: p('roetung'), sommer: p('sommer'), groesse: Math.max(0.25, p('sommer_groesse')),
            altersflecken: Math.max(p('altersflecken'), Genesis9hautebenenwerte.glatt((alter - 0.2) / 0.6)),
            muskel: p('muskel'), fett: p('fett'), mimik: p('mimik'),
            ergrauen: Math.max(p('ergrauen'), Math.min(1, Math.max(0, (alter - 0.23) / 0.77))),
        };
    }
}
