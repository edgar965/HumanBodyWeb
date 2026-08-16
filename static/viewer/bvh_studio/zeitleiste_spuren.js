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

    /** Alle Clips einer Spur. */
    static klips(track, ti, y, pps) {
        for (let ci = 0; ci < track.clips.length; ci++) {
            const clip = track.clips[ci];
            const cx = HEADER_WIDTH + (clip.startFrame / state.project.fps) * pps - state.timelineScrollX;
            const isSelected = (ti === state.selectedTrackIdx && ci === state.selectedClipIdx);
        
            if (clip.type === 'camera_kf' || clip.type === 'light_kf') {
                // Keyframe marker: Diamant (einheitlich für Kamera + Licht)
                // Pair-KFs versetzt: 'upper' oben, 'lower' unten; Standard zentriert
                const pos = clip.data?.trackPosition;
                const my = pos === 'upper' ? y + TRACK_HEIGHT * 0.28
                         : pos === 'lower' ? y + TRACK_HEIGHT * 0.72
                         : y + TRACK_HEIGHT / 2;
                const sz = isSelected ? 8 : 6;
                Zeitleistenflaeche.ctx.fillStyle = track.color;
                Zeitleistenflaeche.ctx.globalAlpha = isSelected ? 1.0 : 0.8;
                // Diamant
                Zeitleistenflaeche.ctx.beginPath();
                Zeitleistenflaeche.ctx.moveTo(cx, my - sz);
                Zeitleistenflaeche.ctx.lineTo(cx + sz, my);
                Zeitleistenflaeche.ctx.lineTo(cx, my + sz);
                Zeitleistenflaeche.ctx.lineTo(cx - sz, my);
                Zeitleistenflaeche.ctx.closePath();
                Zeitleistenflaeche.ctx.fill();
                // Wenn Fade aus → hollow (nur Umriss, weiß) für "Sprung"-Anzeige
                if (clip.data?.fade === false) {
                    Zeitleistenflaeche.ctx.fillStyle = '#1a1a2e';
                    Zeitleistenflaeche.ctx.beginPath();
                    Zeitleistenflaeche.ctx.moveTo(cx, my - sz + 2);
                    Zeitleistenflaeche.ctx.lineTo(cx + sz - 2, my);
                    Zeitleistenflaeche.ctx.lineTo(cx, my + sz - 2);
                    Zeitleistenflaeche.ctx.lineTo(cx - sz + 2, my);
                    Zeitleistenflaeche.ctx.closePath();
                    Zeitleistenflaeche.ctx.fill();
                }
                if (isSelected) {
                    Zeitleistenflaeche.ctx.strokeStyle = '#fff';
                    Zeitleistenflaeche.ctx.lineWidth = 2;
                    Zeitleistenflaeche.ctx.beginPath();
                    Zeitleistenflaeche.ctx.moveTo(cx, my - sz);
                    Zeitleistenflaeche.ctx.lineTo(cx + sz, my);
                    Zeitleistenflaeche.ctx.lineTo(cx, my + sz);
                    Zeitleistenflaeche.ctx.lineTo(cx - sz, my);
                    Zeitleistenflaeche.ctx.closePath();
                    Zeitleistenflaeche.ctx.stroke();
                }
                Zeitleistenflaeche.ctx.globalAlpha = 1.0;
                // Label rechts neben dem Marker (Name z.B. "Kameraposition 1")
                if (clip.name) {
                    Zeitleistenflaeche.ctx.fillStyle = isSelected ? '#fff' : 'rgba(255,255,255,0.75)';
                    Zeitleistenflaeche.ctx.font = '10px sans-serif';
                    Zeitleistenflaeche.ctx.textBaseline = 'middle';
                    Zeitleistenflaeche.ctx.fillText(clip.name, cx + sz + 4, my);
                }
            } else {
                // Rectangle clips (BVH, Audio)
                const cw = Math.max(clip.duration * pps, 4);
                const cy = y + 4;
                const ch = TRACK_HEIGHT - 8;
        
                Zeitleistenflaeche.ctx.fillStyle = track.color;
                Zeitleistenflaeche.ctx.globalAlpha = isSelected ? 1.0 : 0.7;
                Zeitleistenflaeche.ctx.fillRect(cx, cy, cw, ch);
                Zeitleistenflaeche.ctx.globalAlpha = 1.0;
        
                // Audio waveform indicator
                if (clip.type === 'audio') {
                    Zeitleistenflaeche.ctx.strokeStyle = 'rgba(255,255,255,0.3)';
                    Zeitleistenflaeche.ctx.lineWidth = 1;
                    for (let wx = cx + 4; wx < cx + cw - 2; wx += 6) {
                        const wh = 3 + Math.random() * (ch - 8);
                        Zeitleistenflaeche.ctx.beginPath();
                        Zeitleistenflaeche.ctx.moveTo(wx, cy + ch / 2 - wh / 2);
                        Zeitleistenflaeche.ctx.lineTo(wx, cy + ch / 2 + wh / 2);
                        Zeitleistenflaeche.ctx.stroke();
                    }
                }
        
                // Clip border
                Zeitleistenflaeche.ctx.strokeStyle = '#fff';
                Zeitleistenflaeche.ctx.lineWidth = isSelected ? 2 : 0.5;
                Zeitleistenflaeche.ctx.strokeRect(cx, cy, cw, ch);
        
                // Clip label
                Zeitleistenflaeche.ctx.fillStyle = '#fff';
                Zeitleistenflaeche.ctx.font = '10px sans-serif';
                if (clip.type === 'model' && clip.data?.preset) {
                    // Model clip: show person icon + preset name
                    const presetName = clip.data.preset;
                    const maxLen = Math.max(3, Math.floor((cw - 24) / 6));
                    const label = presetName.length > maxLen ? presetName.substring(0, maxLen) + '…' : presetName;
                    // Person icon (Unicode)
                    Zeitleistenflaeche.ctx.font = '12px sans-serif';
                    Zeitleistenflaeche.ctx.fillText('👤', cx + 3, cy + ch / 2 + 4);
                    // Preset name
                    Zeitleistenflaeche.ctx.font = 'bold 10px sans-serif';
                    Zeitleistenflaeche.ctx.fillText(label, cx + 18, cy + ch / 2 + 3, cw - 22);
                } else {
                    Zeitleistenflaeche.ctx.fillText(clip.name, cx + 4, cy + ch / 2 + 3, cw - 8);
                }
            }
        }
        
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
