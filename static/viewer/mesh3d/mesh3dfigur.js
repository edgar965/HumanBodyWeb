/**
 * Mesh3dfigur — die Karte „Genesis-Figur“ (Schritte „Körpernetz“, „Figur“, „Finger“): was „Mesh to 3D“ aus dem Körper gemacht hat (11.10.2026).
 *
 * Kennzahlen (Regler, Eigenmorph, Körpernetz, Finger) und die Vorschaubilder des Auftrags „Mesh to 3D“ — dessen eigene Seite zeigt Erkennung, Runden und Vergleich.
 */
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3dfigur {

    constructor() {
        this.zahlen = document.getElementById('figur-zahlen');
        this.bilder = document.getElementById('figur-bilder');
        this._stand = '';
    }

    zeigen(z) {
        if (!Mesh3danzeige.geaendert(this, '_stand', [z.koerper, z.figur, z.finger, z.status === 'laeuft' ? z.fortschritt : null])) return;
        const k = z.koerper, f = z.figur, fi = z.finger;
        const zeilen = [];
        if (k?.weg === 'netz') {
            zeilen.push(`Verschmolzenes Netz für „Mesh to 3D“: ${Mesh3danzeige.zahl(k.punkte, 0)} Punkte, ${Mesh3danzeige.zahl(k.dreiecke, 0)} Dreiecke, ${Mesh3danzeige.zahl(k.groesse_mb, 1)} MB.`);
            zeilen.push(k.faktor !== 1
                ? `Höhe ${Mesh3danzeige.zahl(k.hoehe_m_original, 3)} m (ohne Maßstab) auf ${Mesh3danzeige.zahl(k.hoehe_m, 2)} m gestreckt, Faktor ${Mesh3danzeige.zahl(k.faktor, 3)} — die Höhe des ganzen Netzes samt Hut und Stab ist eine Setzung.`
                : `Höhe ${Mesh3danzeige.zahl(k.hoehe_m, 3)} m — unverändert.`);
        } else {
            zeilen.push(k ? `Körpernetz für „Mesh to 3D“: ${Mesh3danzeige.zahl(k.punkte, 0)} Punkte, ${Mesh3danzeige.zahl(k.dreiecke, 0)} Dreiecke, ${k.augen} Augen, Atlas ${(k.atlas || []).join(' × ')} px`
                + `${k.ergaenzt ? ` — Körper unter der Kleidung ergänzt (${Mesh3danzeige.zahl(k.ergaenzt.punkte, 0)} Punkte aus „${[].concat(k.ergaenzt.kleider).join(', ')}“)` : ''}.` : 'Körpernetz: noch nicht geschrieben.');
        }
        if (f) {
            const lauf = f.lauf ? ` — rechnet: ${f.lauf.schritt || ''} ${f.lauf.prozent ?? ''} %` : '';
            zeilen.push(`Figur: ${f.regler ?? '—'} Regler${f.rest ? `, Eigenmorph „${f.rest}“` : ''}${lauf}.`);
            const mess = f.schammessung;
            if (mess) zeilen.push(`Scham-Messung der Figur: ${mess.urteil ?? JSON.stringify(mess.abweichungen ?? mess)}.`);
        } else {
            zeilen.push('Figur: noch nicht angepasst.');
        }
        zeilen.push(fi ? (fi.aus ? { text: `Finger: aus${fi.fehler ? ` — ${fi.fehler}` : ''}.`, klasse: fi.fehler ? 'mesh3d-warnung' : '' } : 'Finger: an die Hände des Originals angepasst.') : null);
        Mesh3danzeige.zeilen(this.zahlen, zeilen);
        if (f) {
            const zeile = document.createElement('div');
            zeile.className = 'hb-hinweis';
            const verweis = document.createElement('a');
            verweis.href = `/modell-aus-dateien/meshfigur/${f.kennung}/`;
            verweis.target = '_blank';
            verweis.textContent = `Auftrag „Mesh to 3D“ ${f.kennung} öffnen: Erkennung, Runden, Vergleich`;
            zeile.appendChild(verweis);
            this.zahlen.appendChild(zeile);
        }
        Mesh3danzeige.bilder(this.bilder, (f?.bilder || []).map(b => ({ adresse: b.adresse, titel: b.titel })));
    }
}
