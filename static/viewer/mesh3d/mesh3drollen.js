/**
 * Mesh3drollen — die Karte „Netze und Rollen“ (Schritt „Lesen“): jedes Netz der Datei mit seiner Rolle, dazu die Prüfung des Körpers (11.10.2026).
 */
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3drollen {
    static ROLLEN = {
        koerper: 'Körper', kleid: 'Kleid', haar: 'Haar', auge: 'Auge', augenzubehoer: 'Augenzubehör', mund: 'Mund', gesichtshaar: 'Gesichtshaar',
    };

    constructor() {
        this.zahlen = document.getElementById('rollen-zahlen');
        this.tabelle = document.getElementById('rollen-tabelle');
        this._stand = '';
    }

    zeigen(z) {
        if (!Mesh3danzeige.geaendert(this, '_stand', z.rollen)) return;
        const r = z.rollen;
        if (!r) {
            Mesh3danzeige.zeilen(this.zahlen, []);
            Mesh3danzeige.leer(this.tabelle, 'Noch nicht gelesen — der Schritt „Lesen“ läuft zuerst.');
            return;
        }
        const k = r.koerper;
        Mesh3danzeige.zeilen(this.zahlen, [
            `${r.netze} Netze gelesen.`,
            k ? `Körper „${k.koerper}“: ${Mesh3danzeige.zahl(k.hoehe_koerper_m, 2)} m hoch, die Figur ${Mesh3danzeige.zahl(k.hoehe_figur_m, 2)} m — Deckung ${Mesh3danzeige.zahl((k.anteil || 0) * 100, 0)} %`
                + `${k.tiefstes ? ` (tiefstes Netz „${k.tiefstes}“, höchstes „${k.hoechstes}“)` : ''}.` : null,
        ]);
        Mesh3danzeige.tabelle(this.tabelle, [{ titel: 'Netz' }, { titel: 'Rolle' }, { titel: 'Art' }, { titel: 'Punkte', num: true }],
            r.zeilen.map(n => [n.name, { text: Mesh3drollen.ROLLEN[n.rolle] || n.rolle, klasse: n.rolle === 'koerper' ? 'mesh3d-gut' : '' }, n.art || '', n.punkte === undefined ? '—' : Mesh3danzeige.zahl(n.punkte, 0)]));
    }
}
