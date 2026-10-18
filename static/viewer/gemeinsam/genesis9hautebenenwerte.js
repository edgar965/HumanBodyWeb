/**
 * Genesis9hautebenenwerte — die Regler der Hautebenen und was aus ihren Werten wird (17.10.2026), ohne Three.js und ohne Browser (in Node prüfbar).
 *
 * Die Werte liegen je Figur in `inst.hautebenen = {name: Prozent}` (`Genesis9hautebenen`); hier stehen die Felder (Titel, Bereich, Hilfe) für das Bedienfeld und die Rechnung
 * `wirksam`: Prozent → Anteile, mit der Kopplung ans Alter. Altersflecken und graue Haare folgen dem Alterswert (`Genesis9hautfalten.alter`, 0…1): der Regler addiert nichts, er
 * hebt nur an (Maximum aus Regler und Alter). Altersflecken beginnen bei Alterswert 0,2 (rund 38 Jahre) und stehen bei 0,8 voll; graue Haare ab 0,23 (40 Jahre) bis 1 (90 Jahre) —
 * gesetzt, nicht gemessen (Tabelle 5 und 7 in `genesis9-alter.md`: kein System auf der Platte tut es).
 *
 * 18.10.2026 (Edgar: „neue Regler … Sommersprossen, Falten, Farbfehler, Farbton usw. … möglichst viele Regler, damit ich möglichst komplexe Haut erstellen kann"): Farbton, Olivton,
 * Sättigung, Helligkeit, Hautstruktur, ungleichmäßiger Teint, Wangenröte, Augenringe, Äderchen, Dichte und Ausbreitung der Sommersprossen, Pigment- und Weißflecken, Muttermale,
 * Pickel, Altersfalten, Cellulite, Aknenarben. Alle Stärken und Größen darin sind GESETZT (Augenmaß), nicht an Fotos gemessen.
 */
export class Genesis9hautebenenwerte {

    /** Die Gruppen in der Reihenfolge des Bedienfelds; `haut: false` = gehört nicht zur Haut (nicht im Haut-Popup, nicht in einer gespeicherten Haut). */
    static GRUPPEN = [
        { name: 'Farbe und Teint', haut: true },
        { name: 'Flecken', haut: true },
        { name: 'Relief', haut: true },
        { name: 'Haar', haut: false },
    ];

    /** Die Regler: Name, Titel, Bereich in Prozent, Hilfe. Reihenfolge = Reihenfolge im Bedienfeld. */
    static FELDER = [
        { name: 'ton', titel: 'Hautton (heller … dunkler)', min: -100, max: 100, gruppe: 'Farbe und Teint',
          hilfe: 'Mehr Melanin: dunkler und gesättigter (Potenz auf die Albedo). Wirkt relativ auf jeden Hautsatz, auch auf einen schon dunklen. Die Streufarbe des Durchlichts wandert mit (dunkel: tiefes Rot, hell: Rosa).' },
        { name: 'roetung', titel: 'Blässe … Rötung', min: -100, max: 100, gruppe: 'Farbe und Teint', hilfe: 'Links entsättigt und hellt etwas auf, rechts mehr Rot und weniger Grün/Blau.' },
        { name: 'farbton', titel: 'Farbton (rosig … gelblich)', min: -100, max: 100, gruppe: 'Farbe und Teint',
          hilfe: 'Dreht den Farbton um die Grauachse, bis ±20°: links zu Rosa/Rot, rechts zu Gelb/Gold. Helligkeit bleibt.' },
        { name: 'oliv', titel: 'Olivton', min: 0, max: 100, gruppe: 'Farbe und Teint', hilfe: 'Grünlich-gelber Unterton (weniger Rot und Blau bei gleicher Helligkeit).' },
        { name: 'saettigung', titel: 'Sättigung', min: -100, max: 100, gruppe: 'Farbe und Teint', hilfe: 'Links grau, rechts bis doppelt so kräftig.' },
        { name: 'helligkeit', titel: 'Helligkeit', min: -100, max: 100, gruppe: 'Farbe und Teint', hilfe: 'Reine Helligkeit (±0,8 Blendenstufen), ohne Farbverschiebung — anders als der Hautton.' },
        { name: 'struktur', titel: 'Hautstruktur (glatter … betonter)', min: -100, max: 100, gruppe: 'Farbe und Teint',
          hilfe: 'Kontrast der feinen Farbunterschiede der Textur (Poren, Äderchen, Fleckchen) gegen ihren Mittelwert: links weichgezeichnet, rechts doppelt so stark.' },
        { name: 'teint', titel: 'Ungleichmäßiger Teint', min: 0, max: 100, gruppe: 'Farbe und Teint',
          hilfe: 'Wolkige, wenige Zentimeter große Zonen etwas röter/dunkler und heller — wie ungeschminkte Haut. Größe: „Flecken: Größe".' },
        { name: 'wangen', titel: 'Wangen- und Nasenröte', min: 0, max: 100, gruppe: 'Farbe und Teint',
          hilfe: 'Gerötete Wangen, Nase und Kinn, mit feinen Äderchen (Couperose). Gebiet aus den Gesichtslandmarken, gesetzt.' },
        { name: 'augenringe', titel: 'Augenringe', min: 0, max: 100, gruppe: 'Farbe und Teint', hilfe: 'Dunkler, leicht violetter Halbmond unter den Augen. Gebiet aus den Lid-Landmarken, gesetzt.' },
        { name: 'adern', titel: 'Äderchen (durchscheinend)', min: 0, max: 100, gruppe: 'Farbe und Teint',
          hilfe: 'Bläuliche Venenzeichnung, am stärksten an Armen und Beinen, schwach im Gesicht.' },
        { name: 'sommer', titel: 'Sommersprossen', min: 0, max: 100, gruppe: 'Flecken',
          hilfe: 'Körper nach MB-Labs Sommersprossenmaske, Gesicht (Nase, Wangen, Stirnrand) gesetzt. Die Punkte entstehen im Shader, jeder Zug zeichnet sie neu.' },
        { name: 'sommer_groesse', titel: 'Sommersprossen: Größe', min: 25, max: 200, standard: 100, gruppe: 'Flecken', hilfe: '100 % = rund 2 mm.' },
        { name: 'sommer_dichte', titel: 'Sommersprossen: Dichte', min: 10, max: 100, standard: 80, gruppe: 'Flecken', hilfe: 'Anteil der 6-mm-Zellen, die einen Punkt tragen.' },
        { name: 'sommer_weite', titel: 'Sommersprossen: Ausbreitung', min: 0, max: 100, gruppe: 'Flecken',
          hilfe: '0 = nur an den typischen Stellen (Gesicht, Schultern, Rücken, Arme), 100 = am ganzen Körper.' },
        { name: 'altersflecken', titel: 'Altersflecken', min: 0, max: 100, gruppe: 'Flecken',
          hilfe: 'Handrücken, Unterarme, Stirn, Schläfen, Schultern. Folgt dem Alter (ab rund 38 Jahren); der Regler hebt es an.' },
        { name: 'pigment', titel: 'Pigmentflecken (Melasma)', min: 0, max: 100, gruppe: 'Flecken',
          hilfe: 'Größere, unscharfe braune Flecken (Hyperpigmentierung), im Gesicht stärker.' },
        { name: 'vitiligo', titel: 'Weißflecken (Vitiligo)', min: 0, max: 100, gruppe: 'Flecken',
          hilfe: 'Scharf begrenzte, pigmentlose helle Flächen; der Regler bestimmt, wie viel Haut sie bedecken.' },
        { name: 'flecken_groesse', titel: 'Flecken: Größe', min: 25, max: 300, standard: 100, gruppe: 'Flecken',
          hilfe: 'Größe von Teint-Zonen, Pigment- und Weißflecken. 100 % = Teint 3,5 cm, Pigment 6 cm, Weißflecken 8 cm.' },
        { name: 'muttermale', titel: 'Muttermale', min: 0, max: 100, gruppe: 'Flecken', hilfe: 'Dunkelbraune runde Male, verstreut am ganzen Körper.' },
        { name: 'muttermale_groesse', titel: 'Muttermale: Größe', min: 25, max: 300, standard: 100, gruppe: 'Flecken', hilfe: '100 % = rund 2–5 mm Durchmesser.' },
        { name: 'pickel', titel: 'Hautunreinheiten (Pickel)', min: 0, max: 100, gruppe: 'Flecken',
          hilfe: 'Kleine gerötete, leicht erhabene Stellen — am meisten im Gesicht, weniger an Brust, Rücken und Schultern.' },
        { name: 'falten', titel: 'Altersfalten', min: 0, max: 100, gruppe: 'Relief',
          hilfe: 'Die Falten des Alters (Augen, Stirn, Hals, Mundwinkel) auch ohne Alterswert. Folgt sonst dem Alter; der Regler hebt es an.' },
        { name: 'muskel', titel: 'Muskelzeichnung', min: 0, max: 100, gruppe: 'Relief',
          hilfe: 'Muskeltrennlinien aus MB-Labs Verschiebungsbild (Kanal B) als Normalenschicht.' },
        { name: 'fett', titel: 'Fettzeichnung', min: 0, max: 100, gruppe: 'Relief', hilfe: 'Fettgewebe aus MB-Labs Verschiebungsbild (Kanal A) als Normalenschicht.' },
        { name: 'mimik', titel: 'Mimikfalten (Stärke)', min: 0, max: 200, standard: 100, gruppe: 'Relief',
          hilfe: 'Die 27 FACS-Details (Brauen, Lidfalten, Nasenrümpfen, Lippen, Kinn) als Normalen auf dem Kopf — sichtbar, sobald ein Ausdruck oder ein Mimikregler gestellt ist. 0 = aus.' },
        { name: 'cellulite', titel: 'Cellulite', min: 0, max: 100, gruppe: 'Relief', hilfe: 'Dellen an Oberschenkeln, Po und Hüften (Licht, keine Formänderung).' },
        { name: 'narben', titel: 'Aknenarben', min: 0, max: 100, gruppe: 'Relief', hilfe: 'Kleine Vertiefungen auf Wangen, Schläfen und Stirn (Licht, keine Formänderung).' },
        { name: 'ergrauen', titel: 'Graue Haare (Haar und Brauen)', min: 0, max: 100, gruppe: 'Haar',
          hilfe: 'Soviel Prozent der Strähnen werden grau-weiß, an der Wurzel zuerst. Folgt dem Alter (ab rund 40 Jahren); der Regler hebt es an.' },
    ];

    static standard(name) {
        return Genesis9hautebenenwerte.FELDER.find(f => f.name === name)?.standard ?? 0;
    }

    /** Die Felder, die zur Haut gehören (Haut-Popup, gespeicherte Haut) — ohne die grauen Haare. */
    static hautfelder() {
        const haut = new Set(Genesis9hautebenenwerte.GRUPPEN.filter(g => g.haut).map(g => g.name));
        return Genesis9hautebenenwerte.FELDER.filter(f => haut.has(f.gruppe));
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

    /** Die wirksamen Werte (−1…1 bzw. 0…1, Größen als Faktor) bei diesem Alterswert (0…1). */
    static wirksam(inst, alter) {
        const p = name => Genesis9hautebenenwerte.wert(inst, name) / 100;
        return {
            ton: p('ton'), roetung: p('roetung'), sommer: p('sommer'), groesse: Math.max(0.25, p('sommer_groesse')),
            altersflecken: Math.max(p('altersflecken'), Genesis9hautebenenwerte.glatt((alter - 0.2) / 0.6)),
            muskel: p('muskel'), fett: p('fett'), mimik: p('mimik'),
            ergrauen: Math.max(p('ergrauen'), Math.min(1, Math.max(0, (alter - 0.23) / 0.77))),
            farbton: p('farbton'), oliv: p('oliv'), saettigung: p('saettigung'), helligkeit: p('helligkeit'), struktur: p('struktur'),
            teint: p('teint'), wangen: p('wangen'), augenringe: p('augenringe'), adern: p('adern'),
            dichte: Math.min(1, Math.max(0.1, p('sommer_dichte'))), weite: p('sommer_weite'),
            pigment: p('pigment'), vitiligo: p('vitiligo'), flecken: Math.max(0.25, p('flecken_groesse')),
            muttermale: p('muttermale'), muttermaleGroesse: Math.max(0.25, p('muttermale_groesse')), pickel: p('pickel'),
            falten: p('falten'), cellulite: p('cellulite'), narben: p('narben'),
        };
    }

    /** Färbt irgendein Wert die Haut? (Sonst bekommt kein Material den Farbzusatz.) */
    static mitFarbe(w) {
        return ['ton', 'roetung', 'farbton', 'saettigung', 'helligkeit', 'struktur'].some(n => w[n] !== 0)
            || ['sommer', 'altersflecken', 'oliv', 'teint', 'wangen', 'augenringe', 'adern', 'pigment', 'vitiligo', 'muttermale', 'pickel'].some(n => w[n] > 0);
    }

    /** Ändert irgendein Wert das Licht über eine Beulenschicht (Cellulite, Aknenarben, erhabene Pickel)? */
    static mitBeulen(w) {
        return w.cellulite > 0 || w.narben > 0 || w.pickel > 0;
    }

    /** Braucht es die Gebietskarte (Sommersprossen R, Altersflecken G, Wangen B, Augenringe A)? */
    static mitGebiet(w) {
        return w.sommer > 0 || w.altersflecken > 0 || w.wangen > 0 || w.augenringe > 0 || w.narben > 0;
    }
}
