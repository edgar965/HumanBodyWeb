/**
 * Mesh3dsegmentierung — die Karte „Segmentierung“ der Jobseite „Mesh-3D“, nur beim Weg „netz“ (11.10.2026).
 *
 * Edgar am Zauberer: „Womit machst du die Kleiderabschätzung, Sapiens hat doch schon mal besser funktioniert für Kleider und Haare??“ — der Schritt `segmentierung` (`Blendimportsegmentierung`) rendert das
 * verschmolzene Netz aus vier Ansichten, Sapiens2 etikettiert sie (Haut, Oberteil, Hose, Füße, Zubehör, Haar), die Etiketten gehen auf die Flächen des Netzes. Die Karte zeigt je Ansicht das Rendering und
 * die Überlagerung, Flächen und cm² je Stück — und, was „Mesh to 3D“ daraus gemacht hat: woher der Hautton kam und ob die Kleidungsmaske den Etiketten folgte (`z.figur.hautmodell`, `z.figur.kleidung`).
 * „Segmentierung rechnen“ startet den Lauf ab diesem Schritt (Pose, Figur und alles danach rechnen mit).
 */
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3dsegmentierung {
    static ANSICHT = { vorne: 'von vorn', hinten: 'von hinten', rechts: 'von rechts', links: 'von links' };
    static STUECKE = ['nicht Kleidung', 'Oberteil', 'Hose / Rock', 'Socken / Schuhe', 'Zubehör', 'Haar'];

    constructor(seite) {
        this.seite = seite;
        this.karte = document.getElementById('segmentierung-karte');
        this.zahlen = document.getElementById('segmentierung-zahlen');
        this.zeile = document.getElementById('segmentierung-zeile');
        this.bilder = document.getElementById('segmentierung-bilder');
        this._stand = '';
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.id = 'segmentierung-starten';
        this.knopf.className = 'btn btn-primary btn-sm';
        this.knopf.innerHTML = '<i class="fas fa-vector-square"></i> <span>Segmentierung rechnen</span>';
        this.knopf.title = 'Rechnet ab dem Schritt „Segmentierung“ (Sapiens2 an vier Ansichten des Netzes), danach Pose, Figur und alles Weitere — wie „Neu berechnen“ ab „Segmentierung“.';
        this.zeile.appendChild(this.knopf);
        this.knopf.addEventListener('click', () => seite.lauf.neu('segmentierung', this.knopf));
    }

    zeigen(z) {
        const netz = z.weg === 'netz';
        this.karte.hidden = !netz;
        if (!netz) return;
        this.knopf.disabled = z.status === 'laeuft' || !z.koerper || !z.moegliche.some(s => s.schluessel === 'segmentierung');
        this.knopf.querySelector('span').textContent = z.status === 'laeuft' && z.schritt === 'segmentierung' ? 'Berechnet …' : 'Segmentierung rechnen';
        if (!Mesh3danzeige.geaendert(this, '_stand', [z.segmentierung, z.figur?.hautmodell, z.figur?.kleidung, z.status])) return;
        const s = z.segmentierung;
        if (!s) {
            Mesh3danzeige.leer(this.zahlen, 'Noch nicht gerechnet — der Schritt läuft nach „Körpernetz“ und vor „Pose“ und „Figur“.');
            Mesh3danzeige.bilder(this.bilder, []);
            return;
        }
        Mesh3danzeige.zeilen(this.zahlen, [...this._sapiens(s), ...this._figur(z.figur)]);
        Mesh3danzeige.bilder(this.bilder, s.ansichten.flatMap(a => [
            { adresse: a.rendering, titel: `Rendering ${Mesh3dsegmentierung.ANSICHT[a.rolle] || a.rolle}` },
            { adresse: a.ueberlagerung, titel: `Sapiens ${Mesh3dsegmentierung.ANSICHT[a.rolle] || a.rolle} — grün Haut, rot Oberteil, orange Hose, blau Füße, magenta Zubehör, braun Haar` },
        ]));
    }

    _sapiens(s) {
        const k = s.kennzahlen || {};
        const o = s.optionen || {};
        const stuecke = Object.entries(k.stuecke || {}).filter(([, v]) => v.flaechen > 0).map(([n, v]) => `${n} ${Mesh3danzeige.zahl(v.cm2, 0)} cm²`).join(' · ');
        return [
            `Sapiens (${o.modell || '—'}), Haarmaske: ${o.haar === 'beide' ? 'Farbe oder Sapiens' : o.haar}: ${Mesh3danzeige.zahl(k.flaechen_gesehen, 0)} von ${Mesh3danzeige.zahl(k.flaechen_gesamt, 0)} Flächen gesehen `
                + `(${Mesh3danzeige.zahl(k.cm2_gesehen, 0)} von ${Mesh3danzeige.zahl(k.cm2_gesamt, 0)} cm²)${k.sekunden ? `, ${Mesh3danzeige.zahl(k.sekunden.gesamt, 1)} s` : ''}.`,
            stuecke ? `Gesehen je Stück: ${stuecke}.` : null,
            ...s.ansichten.map(a => `${Mesh3dsegmentierung.ANSICHT[a.rolle] || a.rolle}: Silhouetten-IoU Netz ↔ Rendering ${Mesh3danzeige.zahl(a.iou, 3)}, ${Mesh3danzeige.zahl(a.sichtbar, 0)} Flächen sichtbar.`),
        ];
    }

    /** Was „Mesh to 3D“ übernommen hat — erst, wenn der Schritt „Figur“ gelaufen ist. */
    _figur(f) {
        if (!f) return [{ text: '„Mesh to 3D“: noch nicht gerechnet.', klasse: 'mesh3d-leer' }];
        const h = f.hautmodell;
        const k = f.kleidung || {};
        const sapiens = k.sapiens;
        return [
            h ? `Hautton ${h.hautton ? `(${h.hautton.join(', ')})` : ''} aus: ${h.quelle || '—'}${h.haut_anteil !== undefined ? `, ${Mesh3danzeige.zahl(h.haut_anteil * 100, 0)} % der Proben gelten als Haut` : ''}.`
                : { text: 'Hautton: kein Hautmodell — es gilt die alte Regel (Rumpf und Oberschenkel, bei Kleidung also der Stoff).', klasse: 'mesh3d-warnung' },
            k.fehler ? { text: `Kleidung: ${k.fehler}`, klasse: 'mesh3d-warnung' }
                : sapiens?.verwendet ? `Kleidungsmaske folgt Sapiens: ${Mesh3danzeige.zahl(sapiens.flaechen_geaendert, 0)} Flächen anders als nach Farbe und Lage.`
                    : { text: `Kleidungsmaske: Sapiens nicht benutzt${sapiens?.grund ? ` — ${sapiens.grund}` : ''}.`, klasse: 'mesh3d-warnung' },
        ];
    }
}
