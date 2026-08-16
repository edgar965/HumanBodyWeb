/**
 * Knochengruppen — welche Knochen des DEF-Skeletts sichtbar sind.
 *
 * Aus model_generator.js herausgeloest (Umbau 15.08.2026). Dort standen fuenf
 * Konstanten, eine Schleife auf Modulebene (die FINGER_BONES fuellte) und zwei
 * Klassifikationsfunktionen zwischen den Geometriebauern. Die Schleife war
 * Modul-Initialisierung: Sie lief beim Laden, und ihr Ergebnis liess sich nicht
 * pruefen, ohne das ganze Modul zu importieren.
 */

export class Knochengruppen {
    /** Hauptknochen des Koerpers — im Modell sichtbar (rund 25). */
    static KOERPER = [
        'DEF-spine', 'DEF-spine.001', 'DEF-spine.002', 'DEF-spine.003',
        'DEF-spine.004', 'DEF-spine.005', 'DEF-spine.006',
        'DEF-thigh.L', 'DEF-thigh.L.001',
        'DEF-thigh.R', 'DEF-thigh.R.001',
        'DEF-shin.L', 'DEF-shin.L.001',
        'DEF-shin.R', 'DEF-shin.R.001',
        'DEF-foot.L', 'DEF-foot.R',
        'DEF-shoulder.L', 'DEF-shoulder.R',
        'DEF-upper_arm.L', 'DEF-upper_arm.L.001',
        'DEF-upper_arm.R', 'DEF-upper_arm.R.001',
        'DEF-forearm.L', 'DEF-forearm.L.001',
        'DEF-forearm.R', 'DEF-forearm.R.001',
        'DEF-hand.L', 'DEF-hand.R',
    ];

    /** Fingerglieder — im Modell zunaechst verborgen. */
    static FINGER = Knochengruppen_finger();

    /** Gesichtsknochen — werden aus den Skelettdaten ergaenzt. */
    static GESICHT = [];

    /** Mechanikknochen, die nie gezeigt werden. */
    static NIE_ZEIGEN = ['MCH-', 'ORG-'];

    /** Endknochen mit fester Anzeigelaenge (Meter). */
    static ENDLAENGEN = {
        'DEF-hand.L': 0.05, 'DEF-hand.R': 0.05,
        'DEF-toe.L': 0.03, 'DEF-toe.R': 0.03,
        'DEF-foot.L': 0.06, 'DEF-foot.R': 0.06,
    };

    static _koerperMenge = null;
    static _fingerMenge = null;

    static istKoerper(name) {
        if (!this._koerperMenge) this._koerperMenge = new Set(this.KOERPER);
        return this._koerperMenge.has(name);
    }

    static istFinger(name) {
        if (!this._fingerMenge) this._fingerMenge = new Set(this.FINGER);
        return this._fingerMenge.has(name);
    }

    static istMechanik(name) {
        return this.NIE_ZEIGEN.some((p) => name.startsWith(p));
    }

    /**
     * DEF-Knochen eines Skeletts einteilen: Koerper, Finger, Gesicht.
     * Rueckgabe: { body: string[], finger: string[], face: string[] }
     *
     * Wortgleich zum bisherigen `classifyBones`: Mechanikknochen und alles ohne
     * DEF-Praefix fallen heraus, der Rest landet im Gesicht.
     */
    static einteilen(skelData) {
        const body = [], finger = [], face = [];
        for (const b of (skelData && skelData.bones) || []) {
            const name = b.name;
            if (this.istMechanik(name)) continue;
            if (!name.startsWith('DEF-')) continue;
            if (this.istKoerper(name)) body.push(name);
            else if (this.istFinger(name)) finger.push(name);
            else face.push(name);
        }
        return { body, finger, face };
    }

    /**
     * Rig-Knochen nach Praefix einteilen — das ist eine ANDERE Frage als bei
     * `einteilen`: Hier geht es um die vier Ebenen eines Rigify-Rigs.
     * Rueckgabe: { def, mch, org, control }
     */
    static einteilenRig(rigData) {
        const def = [], mch = [], org = [], control = [];
        for (const b of (rigData && rigData.bones) || []) {
            const name = b.name;
            if (name.startsWith('DEF-')) def.push(name);
            else if (name.startsWith('MCH-')) mch.push(name);
            else if (name.startsWith('ORG-')) org.push(name);
            else control.push(name);
        }
        return { def, mch, org, control };
    }
}

/** Fingernamen mal Glieder mal Seiten — einmal beim Laden erzeugt. */
function Knochengruppen_finger() {
    const namen = ['thumb', 'f_index', 'f_middle', 'f_ring', 'f_pinky'];
    const glieder = ['.01', '.02', '.03'];
    const raus = [];
    for (const n of namen) {
        for (const g of glieder) {
            raus.push(`DEF-${n}${g}.L`);
            raus.push(`DEF-${n}${g}.R`);
        }
    }
    return raus;
}
