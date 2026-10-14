/**
 * Mesh3dnetzfarbwahl — die Zahlen der Auswahl nach Farbe in der Leiste „Netz bearbeiten“: Umkreis in Zentimetern und Farbabstand ΔE (13.10.2026), dazu der Regler „Granularität“ des Hover-Modus (14.10.2026).
 *
 * Edgar: „dieser kleine weisse Flügel am Arm ist nicht als extra Objekt erkannt, das möchte ich auch löschen“ — der Flügel hängt nur lose an Arm und Riemen; ein Rahmen träfe den Arm mit, eine Auswahl über Kanten riss ab.
 * Am Server gemessen (Spiralballerina, Netz `2026.10.13.19.00.52`): Umkreis 18 cm und ΔE 14 trafen den Flügel und sonst nichts Weißes.
 * Der Umkreis gilt in Zentimetern der ANGEZEIGTEN Figur; die Auswahl rechnet in den Einheiten der Szene der Datei, daher die Umrechnung über den Maßstab der Wurzel.
 *
 * Der Regler „Granularität“ (Hover) und das Zahlenfeld „Farbabstand ΔE“ sind EIN Wert: wer an einem dreht, stellt das andere mit (`bei` meldet jede Änderung, damit der Hover neu rechnet).
 */
export class Mesh3dnetzfarbwahl {
    static RADIUS_CM = { vorgabe: 18, min: 1, max: 200 };
    static TOLERANZ = { vorgabe: 14, min: 1, max: 80 };
    /** Der Regler läuft nur bis hier: darüber ist „gleiche Farbfamilie“ längst überschritten und die Auswahl nicht mehr fein. */
    static REGLER_MAX = 60;

    constructor() {
        this.radius = document.getElementById('netz-wz-farbradius');
        this.toleranz = document.getElementById('netz-wz-farbtoleranz');
        this.regler = document.getElementById('netz-wz-granularitaet');
        this.reglerWert = document.getElementById('netz-wz-granularitaet-wert');
        this._bei = null;
        for (const [feld, g] of [[this.radius, Mesh3dnetzfarbwahl.RADIUS_CM], [this.toleranz, Mesh3dnetzfarbwahl.TOLERANZ]]) {
            if (feld && !feld.value) feld.value = g.vorgabe;
        }
        this._binden();
    }

    /** Der Umkreis in Einheiten der Szene der Datei (`wurzel` ist deren Szene). */
    radiusSzene(wurzel) {
        wurzel.updateWorldMatrix(true, false);
        const massstab = wurzel.matrixWorld.getMaxScaleOnAxis() || 1;
        return this._zahl(this.radius, Mesh3dnetzfarbwahl.RADIUS_CM) / 100 / massstab;
    }

    farbabstand() {
        return this._zahl(this.toleranz, Mesh3dnetzfarbwahl.TOLERANZ);
    }

    /** Ein Rückruf, der nach jeder Änderung von Umkreis oder Farbabstand (Zahlenfeld oder Regler) läuft. */
    bei(rueckruf) {
        this._bei = rueckruf;
    }

    // ------------------------------------------------------------------ Innenleben

    _binden() {
        const hoeren = (feld, ereignis, tat) => { if (feld && typeof feld.addEventListener === 'function') feld.addEventListener(ereignis, tat); };
        hoeren(this.regler, 'input', () => {
            if (this.toleranz) this.toleranz.value = this._zahl(this.regler, Mesh3dnetzfarbwahl.TOLERANZ);
            this._reglerZeigen();
            this._melden();
        });
        hoeren(this.toleranz, 'input', () => { this._reglerZeigen(); this._melden(); });
        hoeren(this.toleranz, 'change', () => { this._reglerZeigen(); this._melden(); });
        hoeren(this.radius, 'input', () => this._melden());
        hoeren(this.radius, 'change', () => this._melden());
        this._reglerZeigen();
    }

    /** Regler und Anzeige auf den Wert des Zahlenfelds stellen (der Regler endet bei `REGLER_MAX`, das Feld darf bis 80). */
    _reglerZeigen() {
        const abstand = this.farbabstand();
        if (this.regler) {
            this.regler.max = String(Mesh3dnetzfarbwahl.REGLER_MAX);
            this.regler.value = String(Math.min(abstand, Mesh3dnetzfarbwahl.REGLER_MAX));
        }
        if (this.reglerWert) this.reglerWert.textContent = `ΔE ${Math.round(abstand)}`;
    }

    _melden() {
        if (this._bei) this._bei();
    }

    /** Eine Zahl aus dem Feld, auf die Grenzen geklemmt; leer oder Unsinn gibt die Vorgabe. */
    _zahl(feld, g) {
        const z = Number.parseFloat(String(feld?.value ?? '').replace(',', '.'));
        return Number.isFinite(z) ? Math.min(g.max, Math.max(g.min, z)) : g.vorgabe;
    }
}
