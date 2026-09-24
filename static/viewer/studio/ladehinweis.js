/**
 * Ladehinweis — Play, während die Animation noch lädt: ein Popup statt Stille.
 *
 * Edgar, 21.09.2026: „bei start auf Play der Animation tut sich nichts. Mach
 * einen Popup, falls die Animation noch lädt." Beim Öffnen des Studios holt
 * jede Bewegungsspur erst ihre Figur (`Spurfigur`) und dann je Clip den
 * Retarget (`Clipanimation.laden`, beim ersten Mal bis 43 s); bis dahin hat
 * der Clip kein `animClip`, der Mixer nichts zu spielen — Play setzte
 * `state.playing`, das Symbol sprang auf Pause, und die Figur stand.
 *
 * Jetzt: `offen(state)` nennt, was noch fehlt (Figur der Spur, Bewegung je
 * Clip; ein Clip mit `_loadError` zählt nicht — der kommt nie). Ist etwas
 * offen, zeigt `zeigen` das Popup mit der Liste, prüft alle 500 ms nach,
 * schließt sich, sobald alles da ist, und ruft `danach()` — das Abspielen,
 * das der Klick gemeint hat. „Abbrechen" lässt es bleiben.
 *
 * Ohne Import von `state.js` (das zieht Three.js nach): `state` kommt als
 * Parameter, damit `offen` in Node prüfbar ist (`test_js_ladehinweis.py`).
 */
export class Ladehinweis {

    static KENNUNG = 'lade-hinweis';
    static TAKT_MS = 500;
    static _zeitgeber = null;

    /** `[{spur, was}]` — was noch lädt; leer, wenn alles da ist. */
    static offen(state) {
        const aus = [];
        for (const spur of state.project?.tracks || []) {
            if (spur.type !== 'bvh') continue;
            const clips = spur.clips.filter(c => (c.type === 'bvh' || c.type === 'freeze') && !c._loadError);
            if (!clips.length) continue;
            if (!spur.mesh || spur._loadingPreset) {
                aus.push({ spur: spur.name, was: `Figur${spur._loadingPreset ? ` „${spur._loadingPreset}"` : ''}` });
            }
            for (const clip of clips) {
                if (!clip.animClip) aus.push({ spur: spur.name, was: `Bewegung „${clip.name}"` });
            }
        }
        return aus;
    }

    /**
     * Popup zeigen, bis nichts mehr offen ist — dann `danach()`.
     * @returns true, wenn das Popup gezeigt wurde (der Aufrufer wartet dann)
     */
    static zeigen(state, danach) {
        const offen = Ladehinweis.offen(state);
        if (!offen.length) return false;
        Ladehinweis._bauen();
        Ladehinweis._fuellen(offen);
        Ladehinweis._kasten().style.display = 'flex';
        clearInterval(Ladehinweis._zeitgeber);
        Ladehinweis._zeitgeber = setInterval(() => {
            const rest = Ladehinweis.offen(state);
            if (rest.length) { Ladehinweis._fuellen(rest); return; }
            Ladehinweis.schliessen();
            danach?.();
        }, Ladehinweis.TAKT_MS);
        return true;
    }

    static schliessen() {
        clearInterval(Ladehinweis._zeitgeber);
        Ladehinweis._zeitgeber = null;
        const kasten = Ladehinweis._kasten();
        if (kasten) kasten.style.display = 'none';
    }

    static _kasten() {
        return document.getElementById(Ladehinweis.KENNUNG);
    }

    /** Einmal ins DOM — dieselbe Hülle wie das Hilfefenster (`#help-modal`). */
    static _bauen() {
        if (Ladehinweis._kasten()) return;
        const huelle = document.createElement('div');
        huelle.id = Ladehinweis.KENNUNG;
        huelle.className = 'lade-hinweis';
        huelle.innerHTML = `
            <div class="studio-dialogkasten">
                <div class="hilfemodal-kopf">
                    <h2 class="hilfemodal-titel"><i class="fas fa-spinner fa-spin"></i> Animation lädt noch …</h2>
                </div>
                <div class="hilfemodal-text">
                    <p>Das Abspielen startet, sobald alles geladen ist. Noch offen:</p>
                    <ul class="lade-hinweis-liste"></ul>
                </div>
                <div class="lade-hinweis-knoepfe">
                    <button type="button" class="lade-hinweis-abbrechen">Abbrechen</button>
                </div>
            </div>`;
        huelle.querySelector('.lade-hinweis-abbrechen').addEventListener('click', () => Ladehinweis.schliessen());
        document.body.appendChild(huelle);
    }

    static _fuellen(offen) {
        const liste = Ladehinweis._kasten()?.querySelector('.lade-hinweis-liste');
        if (!liste) return;
        liste.innerHTML = '';
        for (const { spur, was } of offen) {
            const zeile = document.createElement('li');
            zeile.textContent = `${spur}: ${was}`;
            liste.appendChild(zeile);
        }
    }
}
