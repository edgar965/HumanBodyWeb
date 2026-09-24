import { fn } from '../gemeinsam/registrierung.js';
import { Mimikbasis } from './mimikbasis.js';
import { Mimikspur } from './mimikspur.js';
import { Mimikanwendung } from './mimikanwendung.js';
import { Mimikmischer } from './mimikmischer.js';

/**
 * Mimikdialog — „Pose setzen": zehn Gruppen links, Kacheln rechts, darunter
 * Stärke, Übergang und Haltezeit.
 *
 * Edgar, 13.09.2026: „die Pose im Popup-Dialog, unterteilt in 10
 * Obereinheiten". Beim Überfahren einer Kachel zeigt die Figur die Pose
 * live (`spur._vorschau`, siehe `Mimikanwendung.alle`); „Setzen" legt das
 * Schlüsselbild an (`Mimikspur.setzen`). Die zehnte Gruppe „Eigene" hat
 * statt Kacheln den Mischer (`Mimikmischer`): Regler je Einheit, „als Pose
 * speichern". Das HTML entsteht hier, der Rahmen ist der der Figurwahl
 * (`figurwahldialog.css`), der Rest `mimikdialog.css`.
 */
export class Mimikdialog {

    static KENNUNG = 'mimik-dialog';
    static spur = null;
    static frame = 0;
    static gruppe = null;
    static gewaehlt = null;

    static async oeffnen(spur, frame, clip = null) {
        await Mimikbasis.laden();
        Mimikdialog.spur = spur;
        Mimikdialog.frame = frame;
        Mimikdialog.gewaehlt = clip ? Mimikbasis.pose(clip.data?.pose) : null;
        Mimikdialog.gruppe = Mimikdialog.gewaehlt?.gruppe || Mimikbasis.gruppen[0]?.id;
        const huelle = Mimikdialog._huelle();
        huelle.querySelector('.scene-modal-body').innerHTML = Mimikdialog._koerper();
        Mimikdialog._werte(clip?.data);
        Mimikdialog._binden(huelle);
        huelle.classList.add('visible');
        Mimikdialog._gruppeZeigen(Mimikdialog.gruppe);
    }

    static schliessen() {
        const huelle = document.getElementById(Mimikdialog.KENNUNG);
        if (huelle) huelle.classList.remove('visible');
        if (Mimikdialog.spur) {
            Mimikdialog.spur._vorschau = null;
            fn.applyPlayhead();
        }
    }

    // ------------------------------------------------------------------ Aufbau
    static _huelle() {
        let huelle = document.getElementById(Mimikdialog.KENNUNG);
        if (huelle) return huelle;
        huelle = document.createElement('div');
        huelle.id = Mimikdialog.KENNUNG;
        huelle.className = 'scene-modal-overlay';
        huelle.innerHTML = `<div class="scene-modal mimik-dialog">
            <div class="scene-modal-header"><h4><i class="fas fa-smile"></i> Pose setzen</h4>
                <button class="scene-modal-close" data-rolle="schliessen">&times;</button></div>
            <div class="scene-modal-body"></div>
            <div class="scene-modal-footer">
                <div class="mimik-regler">
                    <label>Stärke <input type="range" id="mimik-staerke" min="0" max="100" step="5" value="100">
                        <span id="mimik-staerke-wert">100</span> %</label>
                    <label>Übergang <select id="mimik-uebergang">
                        <option value="weich">weich</option><option value="linear">linear</option></select></label>
                    <label>Halten <input type="number" id="mimik-halten" min="0" step="0.1" value="0"> s</label>
                </div>
                <button data-rolle="abbrechen">Abbrechen</button>
                <button class="primary" data-rolle="setzen"><i class="fas fa-check"></i> Setzen</button>
            </div></div>`;
        document.body.appendChild(huelle);
        return huelle;
    }

    static _koerper() {
        const gruppen = Mimikbasis.gruppen.map(g => {
            const anzahl = Mimikbasis.posen.filter(p => p.gruppe === g.id).length;
            return `<div class="mimik-gruppe" data-gruppe="${g.id}"><span>${g.name}</span>
                <span class="zaehler">${g.id === 'eigene' ? '' : anzahl}</span></div>`;
        }).join('');
        return `<div class="mimik-koerper"><div class="mimik-gruppen">${gruppen}</div>
            <div class="mimik-kacheln" id="mimik-kacheln"></div>
            <div class="mimik-mischen hb-versteckt" id="mimik-mischen"></div></div>`;
    }

    static _kacheln(gruppe) {
        return Mimikbasis.posen.filter(p => p.gruppe === gruppe).map(p => {
            const aktiv = Mimikdialog.gewaehlt?.id === p.id ? ' aktiv' : '';
            return `<div class="mimik-kachel${aktiv}" data-pose="${p.id}" title="${p.name}">
                <img src="${Mimikbasis.VORSCHAU}${p.id}.png" alt="" loading="lazy"
                     onerror="this.hidden = true; this.nextElementSibling.hidden = false;">
                <div class="ohne-bild" hidden><i class="fas fa-smile"></i></div>
                <span>${p.name}</span></div>`;
        }).join('') || '<div class="fussnote">Noch keine Posen in dieser Gruppe.</div>';
    }

    static _werte(daten) {
        const staerke = Math.round((daten?.staerke ?? 1) * 100);
        document.getElementById('mimik-staerke').value = staerke;
        document.getElementById('mimik-staerke-wert').textContent = String(staerke);
        document.getElementById('mimik-uebergang').value = daten?.uebergang || 'weich';
        document.getElementById('mimik-halten').value = daten?.halten ?? 0;
    }

    // ---------------------------------------------------------------- Bedienung
    static _binden(huelle) {
        huelle.querySelector('[data-rolle="schliessen"]').onclick = Mimikdialog.schliessen;
        huelle.querySelector('[data-rolle="abbrechen"]').onclick = Mimikdialog.schliessen;
        huelle.querySelector('[data-rolle="setzen"]').onclick = Mimikdialog._setzen;
        huelle.onclick = (e) => { if (e.target === huelle) Mimikdialog.schliessen(); };
        huelle.querySelectorAll('.mimik-gruppe').forEach(el => {
            el.onclick = () => Mimikdialog._gruppeZeigen(el.dataset.gruppe);
        });
        const staerke = document.getElementById('mimik-staerke');
        staerke.oninput = () => {
            document.getElementById('mimik-staerke-wert').textContent = staerke.value;
            Mimikdialog._vorschau(Mimikdialog.gewaehlt);
        };
    }

    static _gruppeZeigen(gruppe) {
        Mimikdialog.gruppe = gruppe;
        document.querySelectorAll('.mimik-gruppe').forEach(el => {
            el.classList.toggle('aktiv', el.dataset.gruppe === gruppe);
        });
        const kacheln = document.getElementById('mimik-kacheln');
        const mischen = document.getElementById('mimik-mischen');
        const eigene = gruppe === 'eigene';
        mischen.classList.toggle('hb-versteckt', !eigene);
        kacheln.classList.toggle('hb-versteckt', false);
        if (eigene) {
            // Nach „Als Pose speichern" die Kacheln der Gruppe neu — die neue Pose steht dann da.
            Mimikmischer.zeigen(mischen, Mimikdialog.gewaehlt, (pose, gespeichert) => {
                Mimikdialog.gewaehlt = pose;
                if (gespeichert) Mimikdialog._gruppeZeigen('eigene');
                else Mimikdialog._waehlen(pose);
            });
        }
        kacheln.innerHTML = Mimikdialog._kacheln(gruppe);
        kacheln.querySelectorAll('.mimik-kachel').forEach(el => {
            const pose = Mimikbasis.pose(el.dataset.pose);
            el.onmouseenter = () => Mimikdialog._vorschau(pose);
            el.onmouseleave = () => Mimikdialog._vorschau(Mimikdialog.gewaehlt);
            el.onclick = () => Mimikdialog._waehlen(pose);
            el.ondblclick = () => { Mimikdialog._waehlen(pose); Mimikdialog._setzen(); };
        });
    }

    static _waehlen(pose) {
        Mimikdialog.gewaehlt = pose;
        document.querySelectorAll('.mimik-kachel').forEach(el => {
            el.classList.toggle('aktiv', el.dataset.pose === pose?.id);
        });
        Mimikdialog._vorschau(pose);
    }

    /** Die Figur zeigt die Pose sofort — über `spur._vorschau`, das `Mimikanwendung.alle` vorzieht. */
    static _vorschau(pose) {
        const spur = Mimikdialog.spur;
        if (!spur) return;
        const staerke = Number(document.getElementById('mimik-staerke')?.value ?? 100) / 100;
        spur._vorschau = pose ? Mimikdialog._skaliert(pose.gewichte, staerke) : null;
        Mimikanwendung.anwenden(spur._modellIdx, spur._vorschau || {});
    }

    static _skaliert(gewichte, staerke) {
        /** @type {Object<string, number>} */
        const aus = {};
        for (const [e, g] of Object.entries(gewichte || {})) aus[e] = g * staerke;
        return aus;
    }

    static _setzen() {
        const pose = Mimikdialog.gewaehlt;
        if (!pose || !Mimikdialog.spur) return;
        Mimikspur.setzen(Mimikdialog.spur, Mimikdialog.frame, pose, {
            staerke: Number(document.getElementById('mimik-staerke').value) / 100,
            uebergang: document.getElementById('mimik-uebergang').value,
            halten: Number(document.getElementById('mimik-halten').value) || 0,
        });
        Mimikdialog.schliessen();
    }
}
