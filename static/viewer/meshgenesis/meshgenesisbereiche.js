/**
 * Meshgenesisbereiche — die Zeilen der Seite „Mesh-Genesis“ (14.10.2026): ganzer Körper, nur Körper (ohne Kleider), Gesicht, Hände/Füße, Kleider. Je Zeile: wer zeichnet, wo die Kamera steht, woher die Daten kommen und was unter den Feldern steht.
 * Eine neue Zeile ist ein Eintrag hier, ein Block im Template und ein Zeichner — die Seite selbst ändert sich nicht.
 *
 * Die Daten einer Zeile (`daten(antwort, probe)`) haben immer dieselbe Form: `{beschreibung: {punkte, …}, teil: {soll, ausgabe, kennzahlen, eingabe, …}}`. Der ganze Körper liegt in der Probe selbst
 * (`gelenke`, `soll`, …), die anderen Zeilen unter `probe.teile[schluessel]` mit ihrer Beschreibung unter `antwort.teile[schluessel]`.
 */
import { Meshgenesisgesichtzeichner } from './meshgenesisgesichtzeichner.js';
import { Meshgenesiskapselzeichner } from './meshgenesiskapselzeichner.js';

const de = n => n.toLocaleString('de-DE');

/** Text unter dem Feld „Ausgabe des Netzes“: Fehler gesamt; mit `ausfuehrlich` zusätzlich der Anteil unter der Schwelle und eine Zeile je Gruppe. */
function fehlertext(k, wort, ausfuehrlich) {
    const kopf = `Ø ${wort}fehler ${de(k.mittel_mm)} mm · größter ${de(k.groesster_mm)} mm (${k.groesster_gelenk})`;
    if (!ausfuehrlich) return kopf;
    const gruppen = Object.entries(k.je_gruppe_mm).map(([g, mm]) => `${g} ${de(mm)}`).join(' · ');
    return `${kopf} · unter ${de(k.schwelle_mm)} mm: ${de(k.unter_schwelle_prozent)} %\nJe Gruppe: ${gruppen} mm`;
}

/** Zusatz unter „Ausgabe des Netzes“: der Fehler des Rigs (Genesis-9-Knochen) dieser Zeile; leer, wenn die Antwort kein Rig trägt. */
function rigtext(teil) {
    const k = teil.rig?.kennzahlen;
    return k ? `\nRig: Ø ${de(k.mittel_mm)} mm über ${de(k.knochen)} Knochen · größter ${de(k.groesster_mm)} mm (${k.groesster_knochen})` : '';
}

/** Zusatz unter „Gewünschte Ausgabe“: welches Skelett die Zeile zeigt. */
function rigquelle(teil, zeile) {
    return teil.rig ? `Rig: ${de(teil.rig.kennzahlen.knochen)} Genesis-9-Knochen von Ursula1${zeile}` : '';
}

export class Meshgenesisbereiche {
    static KOERPERKAMERA = { position: [1.7, 1.5, 3.4], ziel: [0, 0.95, 0], boden: true };

    /** Der ganze Körper liegt in der Probe selbst; seine Beschreibung ist das Gerüst der Antwort. */
    static koerperDaten(antwort, probe) {
        return { beschreibung: { punkte: antwort.gelenke, fehler_rot_mm: 50 }, teil: probe };
    }

    /**
     * Datenzugriff der Zeilen unter dem ganzen Körper; `null`, wenn der Server die Zeile nicht liefert (ältere Antwort) — die Zeile sagt es dann selbst.
     * `mitKoerperEingabe`: die Eingabe der Zeile ist die des ganzen Körpers (Außenfläche mit Kleidern), nicht ein Ausschnitt.
     */
    static teilDaten(schluessel, mitKoerperEingabe = false) {
        return (antwort, probe) => {
            if (!antwort.teile?.[schluessel] || !probe.teile?.[schluessel]) return null;
            const d = { beschreibung: antwort.teile[schluessel], teil: probe.teile[schluessel] };
            return mitKoerperEingabe ? { ...d, eingabe: Meshgenesisbereiche.koerperDaten(antwort, probe) } : d;
        };
    }

    static LISTE = {
        koerper: {
            zeichner: new Meshgenesiskapselzeichner(),
            kamera: Meshgenesisbereiche.KOERPERKAMERA,
            rigMassstab: 1,
            daten: Meshgenesisbereiche.koerperDaten,
            texte: ({ probe, beschreibung, teil }) => ({
                eingabe: `${de(teil.eingabe.punkte)} Punkte auf der Außenfläche (Dummy: Punkte auf Kapseln um das Gerüst)`,
                soll: `Quelle: ${probe.quelle}\n${rigquelle(teil, ' mit Fingern, Zehen und Gesicht')} · Flächen: Dummy-Kapseln um ${beschreibung.punkte.length} Gelenke`,
                ausgabe: fehlertext(teil.kennzahlen, 'Gelenk', false) + rigtext(teil),
            }),
        },
        koerper_nackt: {
            zeichner: new Meshgenesiskapselzeichner(),
            kamera: Meshgenesisbereiche.KOERPERKAMERA,
            rigMassstab: 1,
            daten: Meshgenesisbereiche.teilDaten('koerper_nackt', true),
            texte: ({ beschreibung, teil }) => ({
                eingabe: `${de(teil.eingabe.punkte)} Punkte der Außenfläche MIT Kleidern — dieselbe Eingabe wie beim ganzen Körper`,
                soll: `Der Körper unter den Kleidern, nur Haut (Dummy-Kapseln um ${beschreibung.punkte.length} Gelenke)\n${rigquelle(teil, '')}`,
                ausgabe: fehlertext(teil.kennzahlen, 'Gelenk', true) + rigtext(teil),
            }),
        },
        gesicht: {
            zeichner: new Meshgenesisgesichtzeichner(),
            kamera: { position: [0.10, 0.05, 0.52], ziel: [0, 0, 0], boden: false },
            rigMassstab: 0.5,
            daten: Meshgenesisbereiche.teilDaten('gesicht'),
            texte: ({ beschreibung, teil }) => ({
                eingabe: `${de(teil.eingabe.punkte)} Punkte der Außenfläche um den Kopf (Dummy: Punkte auf einem Ellipsoid mit Nase)`,
                soll: `${beschreibung.punkte.length} Gesichtspunkte in der Kopfhaltung der Pose (Dummy: in jeder Probe dasselbe Gesicht)\n${rigquelle(teil, ' (Kopf, Augen, Lider, Brauen, Mund, Zunge, Zähne …)')}`,
                ausgabe: fehlertext(teil.kennzahlen, 'Punkt', true) + rigtext(teil),
            }),
        },
        haende: {
            zeichner: new Meshgenesiskapselzeichner({ punktradius: 0.0065, eingabegroesse: 0.006 }),
            kamera: { position: [0.35, 0.65, 1.2], ziel: [0, 0, 0], boden: false },
            rigMassstab: 0.8,
            daten: Meshgenesisbereiche.teilDaten('haende'),
            texte: ({ beschreibung, teil }) => ({
                eingabe: `${de(teil.eingabe.punkte)} Punkte der Außenfläche um Handgelenke und Knöchel — vier Ausschnitte nebeneinander (Dummy: Punkte auf Kapseln)`,
                soll: `${beschreibung.punkte.length} Gelenke von Fingern und Zehen, Hände oben, Füße unten (Dummy)\n${rigquelle(teil, ' von Händen und Füßen (Finger, Zehen)')}`,
                ausgabe: fehlertext(teil.kennzahlen, 'Punkt', true) + rigtext(teil),
            }),
        },
        kleider: {
            zeichner: new Meshgenesiskapselzeichner({ punktradius: 0.016, eingabegroesse: 0.014 }),
            kamera: Meshgenesisbereiche.KOERPERKAMERA,
            rigMassstab: 1,
            daten: Meshgenesisbereiche.teilDaten('kleider'),
            texte: ({ teil }) => ({
                eingabe: `${de(teil.eingabe.punkte)} Punkte der Außenfläche, die Stoff sind (Dummy: Punkte auf Kapseln)`,
                soll: `Oberteil, Ärmel, Hose, Schuhe (Dummy-Kapseln, keine Genesis-Kleider)\n${rigquelle(teil, ' unter dem Stoff (Rumpf, Arme, Beine, Füße)')}`,
                ausgabe: fehlertext(teil.kennzahlen, 'Punkt', true) + rigtext(teil),
            }),
        },
    };

    static fuer(schluessel) {
        const bereich = Meshgenesisbereiche.LISTE[schluessel];
        if (!bereich) throw new Error(`Unbekannte Zeile: ${schluessel}`);
        return bereich;
    }
}
