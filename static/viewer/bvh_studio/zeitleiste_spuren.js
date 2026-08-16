/**
 * Spurinhalte der Zeitleiste zeichnen: Hintergrund, Balken der
 * Schluesselbilder, Verbindungslinien, Clips, Ueberblendzonen.
 *
 * Aus zeitleiste_zeichnen.js herausgeloest (Umbau 16.08.2026): `renderTimeline`
 * war 330 Zeilen — Lineal, Gruppenkoepfe, fuenf verschiedene Spurdarstellungen
 * und der Abspielkopf in einer Funktion.
 */
import { state, TRACK_HEIGHT, HEADER_WIDTH } from './state.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';

export class Zeitleistenspuren {
    /** Hintergrund einer Spurzeile. */
    static hintergrund(ti, y, w) {
        Zeitleistenflaeche.ctx.fillStyle = ti === state.selectedTrackIdx ? 'rgba(124,92,191,0.1)' : 'rgba(0,0,0,0.2)';
        Zeitleistenflaeche.ctx.fillRect(HEADER_WIDTH, y, w - HEADER_WIDTH, TRACK_HEIGHT);
        Zeitleistenflaeche.ctx.strokeStyle = '#1e293b';
        Zeitleistenflaeche.ctx.beginPath();
        Zeitleistenflaeche.ctx.moveTo(HEADER_WIDTH, y + TRACK_HEIGHT);
        Zeitleistenflaeche.ctx.lineTo(w, y + TRACK_HEIGHT);
        Zeitleistenflaeche.ctx.stroke();
        
    }

    /** Balken zwischen den Schluesselbildern einer Kamera- oder Lichtspur. */
    static balken(track, y, pps, w) {
        // Balken für Kamera/Licht-Tracks. Semantik der KF-Arten:
        //   - 'upper'  = Schluss-KF eines Balkens (Bar endet HIER)
        //   - 'lower'  = Start-KF eines NEUEN Balkens (Offset wird getoggled)
        //   - regular  = schließt aktuellen Balken UND startet direkt den nächsten (gleicher Offset)
        // Dadurch bleibt auch nach Verschieben eines 'lower'-KFs die visuelle Trennung
        // stabil (Gap zwischen 'upper' und 'lower' bleibt sichtbar).
        if ((track.type === 'camera' || track.type === 'light') && track.clips.length >= 2) {
            const kfs = track.clips.filter(c => c.type === 'camera_kf' || c.type === 'light_kf');
            if (kfs.length >= 2) {
                const sorted = [...kfs].sort((a, b) => {
                    if (a.startFrame !== b.startFrame) return a.startFrame - b.startFrame;
                    return (a.data?.trackPosition === 'upper' ? 0 : 1) - (b.data?.trackPosition === 'upper' ? 0 : 1);
                });
                const halfH = (TRACK_HEIGHT - 8) / 2;
                const topY = y + 4;
                const botY = y + 4 + halfH;
                const segments = [];  // { from, to, offsetIdx }
                let barStart = null;
                let offsetIdx = 0;  // 0 = oben, 1 = unten
                for (const kf of sorted) {
                    const tp = kf.data?.trackPosition;
                    if (tp === 'upper') {
                        if (barStart != null && barStart !== kf.startFrame) {
                            segments.push({ from: barStart, to: kf.startFrame, offsetIdx });
                        }
                        barStart = null;
                    } else if (tp === 'lower') {
                        offsetIdx = 1 - offsetIdx;  // toggle bei jedem Paar-Übergang
                        barStart = kf.startFrame;
                    } else {
                        // Regular KF: beende laufenden Balken und starte direkt neuen mit gleichem Offset
                        if (barStart != null && barStart !== kf.startFrame) {
                            segments.push({ from: barStart, to: kf.startFrame, offsetIdx });
                        }
                        barStart = kf.startFrame;
                    }
                }
                Zeitleistenflaeche.ctx.fillStyle = track.color;
                Zeitleistenflaeche.ctx.globalAlpha = 0.28;
                for (const seg of segments) {
                    const ax = HEADER_WIDTH + (seg.from / state.project.fps) * pps - state.timelineScrollX;
                    const bx = HEADER_WIDTH + (seg.to   / state.project.fps) * pps - state.timelineScrollX;
                    const segX = Math.max(ax, HEADER_WIDTH);
                    const segW = Math.max(1, Math.min(bx, w) - segX);
                    const segY = seg.offsetIdx === 0 ? topY : botY;
                    if (segW > 0) Zeitleistenflaeche.ctx.fillRect(segX, segY, segW, halfH);
                }
                Zeitleistenflaeche.ctx.globalAlpha = 1.0;
                // Vertikale Trennstriche an jedem Pair-Frame (Same-Frame-Paare)
                Zeitleistenflaeche.ctx.strokeStyle = '#fff';
                Zeitleistenflaeche.ctx.lineWidth = 1;
                Zeitleistenflaeche.ctx.globalAlpha = 0.5;
                for (let i = 0; i < sorted.length - 1; i++) {
                    const a = sorted[i], b = sorted[i + 1];
                    if (a.startFrame !== b.startFrame) continue;
                    if (a.data?.trackPosition !== 'upper' || b.data?.trackPosition !== 'lower') continue;
                    const sx = HEADER_WIDTH + (a.startFrame / state.project.fps) * pps - state.timelineScrollX;
                    if (sx < HEADER_WIDTH || sx > w) continue;
                    Zeitleistenflaeche.ctx.beginPath();
                    Zeitleistenflaeche.ctx.moveTo(sx, topY);
                    Zeitleistenflaeche.ctx.lineTo(sx, botY + halfH);
                    Zeitleistenflaeche.ctx.stroke();
                }
                Zeitleistenflaeche.ctx.globalAlpha = 1.0;
            }
        }
    }

    /** Verbindungslinien ueber den Balken. */
    static linien(track, y, pps) {
        // Draw interpolation lines for camera/light keyframe tracks (über Balken gelegt)
        if ((track.type === 'camera' || track.type === 'light') && track.clips.length > 1) {
            Zeitleistenflaeche.ctx.strokeStyle = track.color;
            Zeitleistenflaeche.ctx.lineWidth = 1.5;
            Zeitleistenflaeche.ctx.globalAlpha = 0.6;
            Zeitleistenflaeche.ctx.beginPath();
            for (let ci = 0; ci < track.clips.length; ci++) {
                const cx = HEADER_WIDTH + (track.clips[ci].startFrame / state.project.fps) * pps - state.timelineScrollX;
                if (ci === 0) Zeitleistenflaeche.ctx.moveTo(cx, y + TRACK_HEIGHT / 2);
                else Zeitleistenflaeche.ctx.lineTo(cx, y + TRACK_HEIGHT / 2);
            }
            Zeitleistenflaeche.ctx.stroke();
            Zeitleistenflaeche.ctx.globalAlpha = 1.0;
        }
        
    }

    /**
     * Alle Clips einer Spur zeichnen.
     *
     * Umbau 17.08.2026: Die Methode hatte 104 Zeilen und zeichnete zwei ganz
     * verschiedene Dinge — Schluesselbild-Marker (Diamanten) und Clips
     * (Rechtecke mit Beschriftung). Jetzt drei Methoden, die je EINE Form
     * zeichnen; die Auswahl trifft `klips`.
     */
    static klips(track, ti, y, pps) {
        for (let ci = 0; ci < track.clips.length; ci++) {
            const clip = track.clips[ci];
            const x = HEADER_WIDTH
                + (clip.startFrame / state.project.fps) * pps
                - state.timelineScrollX;
            const gewaehlt = (ti === state.selectedTrackIdx
                              && ci === state.selectedClipIdx);
            if (clip.type === 'camera_kf' || clip.type === 'light_kf') {
                Zeitleistenspuren._marker(clip, track, x, y, gewaehlt);
            } else {
                Zeitleistenspuren._rechteck(clip, track, x, y, pps, gewaehlt);
            }
        }
    }

    /** Anteil der Spurhoehe, auf dem ein versetzter Marker sitzt. */
    static MARKER_OBEN = 0.28;
    static MARKER_UNTEN = 0.72;
    static MARKER_GROSS = 8;
    static MARKER_KLEIN = 6;

    /**
     * Schluesselbild als Diamant. Paare sitzen versetzt (`trackPosition`),
     * damit zwei Marker auf demselben Bild sichtbar bleiben.
     */
    static _marker(clip, track, x, y, gewaehlt) {
        const ctx = Zeitleistenflaeche.ctx;
        const lage = clip.data?.trackPosition;
        const my = lage === 'upper' ? y + TRACK_HEIGHT * Zeitleistenspuren.MARKER_OBEN
                 : lage === 'lower' ? y + TRACK_HEIGHT * Zeitleistenspuren.MARKER_UNTEN
                 : y + TRACK_HEIGHT / 2;
        const gr = gewaehlt ? Zeitleistenspuren.MARKER_GROSS
                            : Zeitleistenspuren.MARKER_KLEIN;
        ctx.fillStyle = track.color;
        ctx.globalAlpha = gewaehlt ? 1.0 : 0.8;
        Zeitleistenspuren._diamant(x, my, gr);
        ctx.fill();
        // Ohne Ueberblendung: innen aushoehlen — das zeigt den Sprung an.
        if (clip.data?.fade === false) {
            ctx.fillStyle = '#1a1a2e';
            Zeitleistenspuren._diamant(x, my, gr - 2);
            ctx.fill();
        }
        if (gewaehlt) {
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            Zeitleistenspuren._diamant(x, my, gr);
            ctx.stroke();
        }
        ctx.globalAlpha = 1.0;
        if (clip.name) {
            ctx.fillStyle = gewaehlt ? '#fff' : 'rgba(255,255,255,0.75)';
            ctx.font = '10px sans-serif';
            ctx.textBaseline = 'middle';
            ctx.fillText(clip.name, x + gr + 4, my);
        }
    }

    static _diamant(x, y, groesse) {
        const ctx = Zeitleistenflaeche.ctx;
        ctx.beginPath();
        ctx.moveTo(x, y - groesse);
        ctx.lineTo(x + groesse, y);
        ctx.lineTo(x, y + groesse);
        ctx.lineTo(x - groesse, y);
        ctx.closePath();
    }

    /** BVH-, Ton- und Modellclips als Rechteck. */
    static _rechteck(clip, track, x, y, pps, gewaehlt) {
        const ctx = Zeitleistenflaeche.ctx;
        const breite = Math.max(clip.duration * pps, 4);
        const oben = y + 4;
        const hoehe = TRACK_HEIGHT - 8;

        ctx.fillStyle = track.color;
        ctx.globalAlpha = gewaehlt ? 1.0 : 0.7;
        ctx.fillRect(x, oben, breite, hoehe);
        ctx.globalAlpha = 1.0;
        if (clip.type === 'audio') {
            Zeitleistenspuren._tonzacken(x, oben, breite, hoehe);
        }
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = gewaehlt ? 2 : 0.5;
        ctx.strokeRect(x, oben, breite, hoehe);
        Zeitleistenspuren._beschriftung(clip, x, oben, breite, hoehe);
    }

    /**
     * Andeutung einer Tonspur. Bewusst zufaellig: Die echten Pegel liegen im
     * Browser nicht vor, und eine gerade Linie saehe nach „kein Ton" aus.
     */
    static _tonzacken(x, oben, breite, hoehe) {
        const ctx = Zeitleistenflaeche.ctx;
        ctx.strokeStyle = 'rgba(255,255,255,0.3)';
        ctx.lineWidth = 1;
        for (let zx = x + 4; zx < x + breite - 2; zx += 6) {
            const zh = 3 + Math.random() * (hoehe - 8);
            ctx.beginPath();
            ctx.moveTo(zx, oben + hoehe / 2 - zh / 2);
            ctx.lineTo(zx, oben + hoehe / 2 + zh / 2);
            ctx.stroke();
        }
    }

    static _beschriftung(clip, x, oben, breite, hoehe) {
        const ctx = Zeitleistenflaeche.ctx;
        ctx.fillStyle = '#fff';
        ctx.font = '10px sans-serif';
        if (clip.type !== 'model' || !clip.data?.preset) {
            ctx.fillText(clip.name, x + 4, oben + hoehe / 2 + 3, breite - 8);
            return;
        }
        // Modellclip: Symbol plus Name der Vorgabe, gekuerzt auf die Breite.
        const name = clip.data.preset;
        const passt = Math.max(3, Math.floor((breite - 24) / 6));
        ctx.font = '12px sans-serif';
        ctx.fillText('\u{1F464}', x + 3, oben + hoehe / 2 + 4);
        ctx.font = 'bold 10px sans-serif';
        ctx.fillText(name.length > passt ? name.substring(0, passt) + '…' : name,
                     x + 18, oben + hoehe / 2 + 3, breite - 22);
    }

    /** Ueberblendzonen der Modellspuren — nach den Clips, damit sie obenauf liegen. */
    static ueberblendung(track, y, pps, w) {
        // Overlap-Zonen für Model-Tracks — Fade-Bereich mit Kreuz-Schraffur,
        // gerendert NACH den Clips damit die Schraffur on-top liegt.
        if (track.type === 'model' && track.clips.length > 1) {
            const sorted = [...track.clips].sort((a, b) => a.startFrame - b.startFrame);
            for (let i = 0; i < sorted.length - 1; i++) {
                const a = sorted[i], b = sorted[i + 1];
                const aEndFrame = a.startFrame + Math.ceil(a.duration * state.project.fps);
                if (b.startFrame >= aEndFrame) continue;
                const ox = HEADER_WIDTH + (b.startFrame / state.project.fps) * pps - state.timelineScrollX;
                const oEnd = HEADER_WIDTH + (aEndFrame / state.project.fps) * pps - state.timelineScrollX;
                const ow = Math.max(2, oEnd - ox);
                const oy = y + 4, oh = TRACK_HEIGHT - 8;
                if (ox + ow < HEADER_WIDTH || ox > w) continue;  // off-screen
                // Basis (orange-transparent) + Kreuz-Schraffur
                Zeitleistenflaeche.ctx.fillStyle = 'rgba(255, 152, 0, 0.45)';
                Zeitleistenflaeche.ctx.fillRect(ox, oy, ow, oh);
                Zeitleistenflaeche.ctx.save();
                Zeitleistenflaeche.ctx.beginPath();
                Zeitleistenflaeche.ctx.rect(ox, oy, ow, oh);
                Zeitleistenflaeche.ctx.clip();
                Zeitleistenflaeche.ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
                Zeitleistenflaeche.ctx.lineWidth = 1;
                const step = 7;
                for (let hx = ox - oh; hx < ox + ow + oh; hx += step) {
                    Zeitleistenflaeche.ctx.beginPath();
                    Zeitleistenflaeche.ctx.moveTo(hx, oy);
                    Zeitleistenflaeche.ctx.lineTo(hx + oh, oy + oh);
                    Zeitleistenflaeche.ctx.stroke();
                    Zeitleistenflaeche.ctx.beginPath();
                    Zeitleistenflaeche.ctx.moveTo(hx + oh, oy);
                    Zeitleistenflaeche.ctx.lineTo(hx, oy + oh);
                    Zeitleistenflaeche.ctx.stroke();
                }
                Zeitleistenflaeche.ctx.restore();
                Zeitleistenflaeche.ctx.strokeStyle = 'rgba(255, 120, 0, 1)';
                Zeitleistenflaeche.ctx.lineWidth = 1.5;
                Zeitleistenflaeche.ctx.strokeRect(ox, oy, ow, oh);
                if (ow > 50) {
                    Zeitleistenflaeche.ctx.fillStyle = '#fff';
                    Zeitleistenflaeche.ctx.font = 'bold 10px sans-serif';
                    Zeitleistenflaeche.ctx.textAlign = 'center';
                    Zeitleistenflaeche.ctx.textBaseline = 'middle';
                    Zeitleistenflaeche.ctx.fillText('✕ FADE', ox + ow / 2, oy + oh / 2);
                    Zeitleistenflaeche.ctx.textAlign = 'start';
                    Zeitleistenflaeche.ctx.textBaseline = 'alphabetic';
                }
            }
        }
    }
}
