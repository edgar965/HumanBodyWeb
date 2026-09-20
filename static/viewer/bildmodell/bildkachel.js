/**
 * Bildkachel — eine Kachel je Ausschnitt: Bild mit Rig, Befundzeile, Steller.
 *
 * Aus `Bilderansicht` herausgelöst (19.09.2026, als die Steller drei Boxen
 * und zwei Knöpfe bekamen). Der Rahmen bekommt das Seitenverhältnis des
 * Bildes, damit das Rig-SVG (viewBox 0 0 1 1, `Rigzeichnung`) Punkt für Punkt
 * darauf liegt; welches Rig gezeichnet wird, sagt `rigWahl` (auto = MediaPipe,
 * sonst ViTPose, YOLO, openpifpaf).
 */
import { Rigzeichnung } from './rigzeichnung.js';

export class Bildkachel {

    static ANSICHT = { vorne: 'von vorn', seite: 'von der Seite', hinten: 'von hinten',
                       dreiviertel: 'dreiviertel', drehung: 'Drehvideo' };
    static TEILE = { haende: 'Hände', gesicht: 'Gesicht', oberkoerper: 'Oberkörper', ruecken: 'Rücken',
                     becken: 'Hüfte/Gesäß', arme: 'Arme', beine: 'Beine', fuesse: 'Füße' };

    constructor(auftrag, steller) {
        this.auftrag = auftrag;
        this.steller = steller;
    }

    element(b, rigWahl = 'auto') {
        const k = document.createElement('figure');
        k.className = 'bildmodell-kachel';
        k.dataset.datei = b.datei;
        const rahmen = document.createElement('div');
        rahmen.className = 'bildmodell-bildrahmen';
        if (b.breite && b.hoehe) rahmen.style.aspectRatio = `${b.breite} / ${b.hoehe}`;
        const bild = document.createElement('img');
        bild.src = this.auftrag.dateiAdresse('zuschnitt', b.datei);
        bild.alt = b.datei;
        bild.loading = 'lazy';
        rahmen.appendChild(bild);
        const rig = Bildkachel.rigFuer(b, rigWahl);
        if (rig.art === 'mediapipe') {
            rahmen.appendChild(Rigzeichnung.svg(b.landmarken, b.gesicht, (b.breite || 3) / (b.hoehe || 4), b.haende_punkte));
        } else if (rig.punkte) {
            rahmen.appendChild(Rigzeichnung.cocoSvg(rig.punkte, (b.breite || 3) / (b.hoehe || 4)));
        }
        k.appendChild(rahmen);
        k.appendChild(this.befund(b, rig));
        k.appendChild(this.steller.feld(b));
        return k;
    }

    /** Die Befundzeile: Quelle, Ansicht/Haltung/Teil, Sichtbarkeit, Rig-Teile, Schätzer, Silhouette. */
    befund(b, rig) {
        const text = document.createElement('figcaption');
        const teile = [];
        if (b.ansicht && b.kategorie !== 'neben') teile.push(Bildkachel.ANSICHT[b.ansicht] || b.ansicht);
        if (b.kategorie === 'neben' && b.teil) teile.push(Bildkachel.TEILE[b.teil] || b.teil);
        if (b.video) teile.push(`${b.bilder || '?'} Bilder` + (b.fps ? ` bei ${b.fps} fps` : ''));
        else if (b.haltung && b.kategorie !== 'neben') teile.push(b.haltung === 'neutral' ? 'neutrale Haltung' : 'posiert');
        if (b.koerper_sichtbar) teile.push(`${Math.round(b.koerper_sichtbar * 100)} % Körper`);
        if (b.gesicht && b.gesicht.hoehe) teile.push(`Gesicht ${Math.round(b.gesicht.hoehe * 100)} %`);
        if (b.punkte) teile.push(`${b.punkte} YOLO-Punkte`);
        if (rig.art && rig.art !== 'mediapipe' && rig.teile.length) teile.push(`${rig.art}: ${rig.teile.join(', ')}`);
        if (b.haende_punkte && b.haende_punkte.length) {
            teile.push(b.haende_punkte.map(h => `${h.seite === 'Left' ? 'linke' : 'rechte'} Hand ${Math.round(h.guete * 100)} %`).join(', '));
        }
        const s = b.schaetzung;
        if (s && s.fehler) teile.push(`Schätzer: ${s.fehler}`);
        else if (s && s.ausgelassen) teile.push(`${s.backend}: nicht verwendet`);
        else if (s && s.frames) teile.push(`${s.backend}: eine Form aus ${s.frames} Bildern`);
        else if (s) teile.push(`${s.backend}: ${Math.round((s.confidence || 0) * 100)} %`);
        if (s && s.silhouette && s.silhouette.iou_nachher != null) {
            teile.push(`Silhouette ${Math.round(s.silhouette.iou_vorher * 100)} → ${Math.round(s.silhouette.iou_nachher * 100)} %`);
        } else if (s && s.silhouette && s.silhouette.fehler) teile.push(`Silhouette: ${s.silhouette.fehler}`);
        // SMPL-X mit GVHMR für dieses Bild (Knopf an der Kachel, 20.09.2026).
        const g = b.gvhmr;
        if (g && g.fehler) teile.push(`GVHMR: ${g.fehler}`);
        else if (g && g.netz) teile.push(`GVHMR: SMPL-X${g.hoehe_m ? ' ' + g.hoehe_m.toFixed(2) + ' m' : ''} in ${g.dauer_s ?? '?'} s`);
        if (b.fehler) teile.push(b.fehler);
        text.innerHTML = `<span class="bildmodell-quelle" title="${b.quelle || ''}">${(b.quelle || b.datei)}</span>`
            + `<span class="bildmodell-befund">${teile.join(' · ')}</span>`;
        return text;
    }

    /** Das Rig, das die Wahl für dieses Bild ergibt: `{art, punkte, teile}`. */
    static rigFuer(b, wahl = 'auto') {
        const rigs = b.rigs || {};
        const hatMp = !!(b.landmarken || b.gesicht || (b.haende_punkte && b.haende_punkte.length));
        const reihe = wahl === 'auto' ? ['mediapipe', 'vitpose', 'yolo', 'openpifpaf'] : [wahl];
        for (const art of reihe) {
            if (art === 'mediapipe' && hatMp) return { art, punkte: b.landmarken, teile: [] };
            const r = rigs[art];
            if (art !== 'mediapipe' && r && r.punkte) return { art, punkte: r.punkte, teile: r.teile || [] };
        }
        return { art: null, punkte: null, teile: [] };
    }
}
