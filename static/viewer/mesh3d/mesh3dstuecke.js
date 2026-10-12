/**
 * Mesh3dstuecke — die Karte „Kleider, Haar und Augen“ (Schritt „Kleider und Haar“) der Jobseite „Mesh-3D“ (11.10.2026).
 *
 * Eine Zeile je Genesis-Stück: Rolle im Original, Name in der Garderobe, Kategorie, Punkte, Abstand zur Haut (Median) und größte Abweichung der Rückrechnung
 * in die Ruhelage (`Kleidungsentposen`, Abnahme von `Blendimportpruefung`); darunter, was scheiterte oder entfiel, und der Kontaktbogen aller Stücke.
 */
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3dstuecke {

    constructor() {
        this.zahlen = document.getElementById('stuecke-zahlen');
        this.tabelle = document.getElementById('stuecke-tabelle');
        this.bilder = document.getElementById('stuecke-bilder');
        this._stand = '';
    }

    zeigen(z) {
        if (!Mesh3danzeige.geaendert(this, '_stand', z.stuecke)) return;
        const s = z.stuecke;
        if (!s) {
            Mesh3danzeige.zeilen(this.zahlen, []);
            Mesh3danzeige.leer(this.tabelle, 'Noch keine Stücke — der Schritt „Kleider und Haar“ läuft nach „Figur“ und „Finger“.');
            Mesh3danzeige.bilder(this.bilder, []);
            return;
        }
        Mesh3danzeige.zeilen(this.zahlen, [
            s.aus ? { text: 'Einstellung „Kleider und Haar“ steht auf „Nur die Figur“ — es wurden keine Stücke gebaut.', klasse: 'mesh3d-warnung' } : `${s.zeilen.length} Stücke in der Garderobe.`,
            ...s.gescheitert.map(g => ({ text: `Gescheitert: ${g.schluessel} — ${g.fehler}`, klasse: 'mesh3d-schlecht' })),
            ...s.ohne.map(g => `Entfallen: ${g.schluessel} — ${g.grund}`),
        ]);
        Mesh3danzeige.tabelle(this.tabelle,
            [{ titel: 'Original' }, { titel: 'Stück' }, { titel: 'Kategorie' }, { titel: 'Punkte', num: true }, { titel: 'Haut Ø mm', num: true }, { titel: 'Rest max mm', num: true }, { titel: 'Hinweise' }],
            s.zeilen.map(r => [r.schluessel, r.name, r.kategorie || '', r.punkte === undefined ? '—' : Mesh3danzeige.zahl(r.punkte, 0), Mesh3danzeige.zahl(r.haut_median_mm, 1), Mesh3danzeige.zahl(r.rest_max_mm, 1),
                { text: r.warnungen.length ? r.warnungen.join(' · ') : '', klasse: r.warnungen.length ? 'mesh3d-warnung' : '' }]),
            'Keine Stücke.');
        Mesh3danzeige.bilder(this.bilder, [{ adresse: s.bogen, titel: 'Kontaktbogen: jedes Stück am Original, in der Haltung des Originals', gross: true }]);
    }
}
