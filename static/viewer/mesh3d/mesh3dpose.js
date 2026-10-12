/**
 * Mesh3dpose — die Karte „Haltung und Pose“ der Jobseite „Mesh-3D“ (11.10.2026).
 *
 * Zwei Wege zur Haltung des Modells, wenn es nicht in A-Haltung steht (Edgar, 11.10.2026: „wenn das Modell in einer anderen Pose als A-Pose ist,
 * bitte berücksichtige das, mit SAM 3D“):
 *   Umposen   mit dem Rig der Datei (Auto-Rig Pro) — Schritt „Umposen“, Ergebnis `z.umposen`;
 *   Pose      SAM 3D Body findet die Gelenke an einem Rendering des Körpers — Schritt „Pose“ (`Blendimportpose`), Ergebnis `z.pose`, Einstellung „Pose bestimmen“.
 * Die Karte zeigt, was gelaufen ist, die gemessene Haltung (Winkel gegen die Körperachse, zum Vergleich mit der A-Haltung) und die vier Drehungen mit den Gelenken;
 * „Pose rechnen“ startet nur den Lauf ab dem Schritt „Pose“ — die Figur und alles danach rechnet er mit (der Import hat kein „bis“).
 */
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3dpose {
    static DREHUNGEN = [0, 90, 180, 270];

    constructor(seite) {
        this.seite = seite;
        this.zahlen = document.getElementById('pose-zahlen');
        this.zeile = document.getElementById('pose-zeile');
        this.bilder = document.getElementById('pose-bilder');
        this._stand = '';
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.id = 'pose-starten';
        this.knopf.className = 'btn btn-primary btn-sm';
        this.knopf.innerHTML = '<i class="fas fa-person"></i> <span>Pose rechnen</span>';
        this.knopf.title = 'Rechnet ab dem Schritt „Pose“ (SAM 3D Body am Rendering des Körpers), danach Figur, Finger, Stücke, Haut und Modell — wie „Neu berechnen“ ab „Pose“. Die Einstellung „Pose bestimmen“ muss auf „SAM 3D Body“ stehen.';
        this.hinweis = document.createElement('span');
        this.hinweis.className = 'hb-hinweis';
        this.zeile.append(this.knopf, this.hinweis);
        this.knopf.addEventListener('click', () => seite.lauf.neu('pose', this.knopf));
    }

    zeigen(z) {
        const an = z.einstellungen?.pose === 'sam';
        const hat = z.moegliche.some(s => s.schluessel === 'pose');
        const gelesen = z.weg === 'netz' ? !!z.koerper : !!z.rollen;
        this.knopf.disabled = z.status === 'laeuft' || !hat || !gelesen || !an;
        this.knopf.querySelector('span').textContent = z.status === 'laeuft' && z.schritt === 'pose' ? 'Berechnet …' : 'Pose rechnen';
        this.hinweis.textContent = !gelesen ? (z.weg === 'netz' ? 'Erst „Körpernetz“.' : 'Erst „Lesen“.') : (!an ? 'Einstellung „Pose bestimmen“ steht auf „Aus“ (oben unter „Einstellungen“).' : '');
        if (!Mesh3danzeige.geaendert(this, '_stand', [z.umposen, z.pose, z.einstellungen?.pose, z.einstellungen?.pose_drehung, z.weg])) return;
        const u = z.umposen, p = z.pose;
        Mesh3danzeige.zeilen(this.zahlen, [
            u ? (u.aus ? { text: `Umposen: aus${u.grund ? ` — ${u.grund}` : ''}. Die Haltung der Datei gilt.`, klasse: u.grund ? 'mesh3d-warnung' : '' }
                : `Umposen: ${u.gedreht} von ${u.segmente} Segmenten mit dem Rig in die Genesis-Haltung gedreht.`) : (z.weg === 'netz' ? null : 'Umposen: noch nicht gerechnet.'),
            ...this._pose(p, an),
        ]);
        Mesh3danzeige.bilder(this.bilder, p && !p.aus ? [
            ...Mesh3dpose.DREHUNGEN.map(g => ({ adresse: p.bilder?.[`skelett_${g}`], titel: `SAM 3D Body, Rendering ${g}° gedreht${g === p.drehung ? ' — gewählt' : ''}` })),
            { adresse: p.bilder?.netz, titel: 'Körpernetz von vorn und von der Seite mit den Landmarken (grün: im Netz, orange: auf das Netz gezogen)', gross: true },
        ] : []);
    }

    _pose(p, an) {
        if (!p) return [an ? 'Pose (SAM 3D Body): noch nicht gerechnet.' : 'Pose (SAM 3D Body): aus — „Mesh to 3D“ findet die Haltung selbst.'];
        if (p.aus) return [{ text: `Pose (SAM 3D Body): aus${p.grund ? ` — ${p.grund}` : ''}.`, klasse: p.grund ? 'mesh3d-warnung' : '' }];
        const g = p.gelenke || {};
        const a = p.abbildung || {};
        const h = p.haltung;
        return [
            `Pose (SAM 3D Body, Drehung ${p.drehung}°): ${g.gesetzt ?? '—'} Gelenke im Körpernetz (davon ${g.haupt_gesetzt ?? '—'} der 12 Hauptgelenke)`
                + `${g.ausserhalb?.length ? `, ${g.ausserhalb.length} auf das Netz gezogen` : ''}${a.iou !== undefined ? ` · Silhouetten-IoU Netz ↔ Rendering ${Mesh3danzeige.zahl(a.iou, 3)}` : ''}.`,
            h ? `Haltung (Winkel zur Körperachse, in der Bildebene): Oberarme ${Mesh3danzeige.zahl(h.oberarm_links_grad, 0)}° / ${Mesh3danzeige.zahl(h.oberarm_rechts_grad, 0)}° (A-Haltung: etwa ${Mesh3danzeige.zahl(h.a_haltung_oberarm_grad, 0)}°), `
                + `Oberschenkel ${Mesh3danzeige.zahl(h.oberschenkel_links_grad, 0)}° / ${Mesh3danzeige.zahl(h.oberschenkel_rechts_grad, 0)}° (stehend: nahe 0°), Rumpfneigung gegen die Senkrechte ${Mesh3danzeige.zahl(h.rumpf_neigung_grad, 0)}°.` : null,
            p.dauer_sam_s ? `SAM 3D Body ${p.sam_neu_gerechnet ? `gerechnet: ${Mesh3danzeige.zahl(p.dauer_sam_s, 1)} s` : 'aus der Ablage (Rendering unverändert)'}.` : null,
        ];
    }
}
