import { state } from './state.js';
import { Exportleiste } from '../exportleiste/exportleiste.js';

/**
 * Studioexportquelle — die Figur des BVH Studios für die Exportleiste im Reiter „Rendern“ (20.11.2026, Edgar: „http://127.0.0.1:8081/studio/ … da drin möchte ich den Renderer
 * usw. haben“; Server `core/dienste/studioexportquelle.py`, Leiste `exportleiste/exportleiste.js`).
 *
 * Figur: die Genesis-9-Figur der gewählten Bewegungsspur (`Spurfigurarten.BAUER.genesis9`: `spur.modell`, Name `spur.preset`), ist keine solche gewählt, die erste im Projekt.
 * Der Render kann nur Genesis 9 — ohne Genesis-9-Figur startet die Leiste nicht, der Hinweis sagt warum. Höhe wie der Retarget des Studios (`Retargetziel.wahl(spur.modell,
 * spur.figurHoehe)`), damit Render und Studio dieselbe Bewegung tragen. Animation: der Clip dieser Spur unter dem Abspielkopf, sonst ihr erster (`Kategorie/Name`).
 * Wechselt die Figur, zieht die Leiste um (`adresse`, je Modell ein Arbeitsordner auf dem Server).
 */
export class Studioexportquelle {

    static TAKT_MS = 2000;

    static starten() {
        const wurzel = document.getElementById('exportleiste');
        const hinweis = document.getElementById('studio-rendern-hinweis');
        if (!wurzel) return null;
        const quelle = new Studioexportquelle();
        const warten = () => {
            if (quelle.spur()) {
                if (hinweis) hinweis.hidden = true;
                wurzel.hidden = false;
                wurzel.dataset.adresse = quelle.adresse();
                quelle.leiste = Exportleiste.starten(wurzel, quelle);
                return;
            }
            if (hinweis) hinweis.hidden = false;
            wurzel.hidden = true;
            setTimeout(warten, Studioexportquelle.TAKT_MS);
        };
        warten();
        return quelle;
    }

    /** Die Bewegungsspur mit Genesis-9-Figur: die gewählte, sonst die erste — oder null. */
    spur() {
        const spuren = state.project?.tracks || [];
        const passt = s => s?.type === 'bvh' && s.quelle === 'genesis9' && s.modell;
        const gewaehlt = spuren[state.selectedTrackIdx];
        return passt(gewaehlt) ? gewaehlt : spuren.find(passt) || null;
    }

    adresse() {
        const s = this.spur();
        return s ? `/api/exportleiste/studio/${encodeURIComponent(s.preset || s.modell.figur || 'basis')}/` : null;
    }

    /** `Kategorie/Name` des Clips unter dem Abspielkopf, sonst des ersten Clips der Spur. */
    bvh() {
        const clips = (this.spur()?.clips || []).filter(c => c.type === 'bvh' && c.category && c.name);
        const kopf = Number(state.playheadFrame) || 0;
        const clip = clips.find(c => c.startFrame <= kopf && kopf < c.endFrame) || clips[0];
        return clip ? `${clip.category}/${clip.name}` : null;
    }

    async modell() {
        const s = this.spur();
        if (!s) throw new Error('Im Projekt steht keine Genesis-9-Figur — der Render kann nur Genesis 9');
        const m = s.modell;
        return { inst: m, figur: m.figur, regler: m.regler || {}, hoehe_m: Number(s.figurHoehe) > 0 ? Number(s.figurHoehe) : (m.hoehe || 0) };
    }
}
