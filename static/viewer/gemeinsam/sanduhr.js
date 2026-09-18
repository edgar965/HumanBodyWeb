/**
 * Sanduhr — zeigt, dass eine Änderung noch gerechnet wird.
 *
 * Edgar (18.09.2026): „mach eine Sanduhr wenn ich eine Property ändere,
 * damit ich weiss, wann die Property geändert wird". Ein Reglerzug an einer
 * Genesis-9-Figur läuft über den Server (Käfig 0,3 s, Stufe 2 mit Kleid
 * 2–3 s); solange stand die Figur unverändert da, ohne Hinweis.
 *
 * `an(text)` zählt hoch und zeigt das Abzeichen (fest unten links, neben dem
 * Netzstufen-Abzeichen rechts), `aus()` zählt herunter — verschachtelte Läufe
 * halten es, bis der letzte fertig ist. Dazu bekommt `<html>` die Klasse
 * `hb-sanduhr` (Mauszeiger `progress`, `stilhelfer.css`). `um(text, aufruf)`
 * umschließt ein Versprechen, auch bei Fehler wieder aus.
 */
export class Sanduhr {

    static ID = 'hb-sanduhr';
    static KLASSE = 'hb-sanduhr';
    static _offen = 0;

    static an(text = 'Rechnet …') {
        Sanduhr._offen += 1;
        let feld = document.getElementById(Sanduhr.ID);
        if (!feld) {
            feld = document.createElement('div');
            feld.id = Sanduhr.ID;
            Object.assign(feld.style, {
                position: 'fixed', left: '12px', bottom: '12px', zIndex: '9000',
                padding: '6px 10px', borderRadius: '6px', font: '12px/1.4 sans-serif',
                background: 'rgba(80, 140, 255, 0.92)', color: '#fff',
                pointerEvents: 'none', boxShadow: '0 2px 8px rgba(0,0,0,.4)',
            });
            document.body.appendChild(feld);
        }
        feld.textContent = `⏳ ${text}`;
        document.documentElement.classList.add(Sanduhr.KLASSE);
        return feld;
    }

    static aus() {
        Sanduhr._offen = Math.max(0, Sanduhr._offen - 1);
        if (Sanduhr._offen) return;
        document.getElementById(Sanduhr.ID)?.remove();
        document.documentElement.classList.remove(Sanduhr.KLASSE);
    }

    /** Ein Versprechen mit Sanduhr — aus, sobald es erfüllt oder gescheitert ist. */
    static async um(text, aufruf) {
        Sanduhr.an(text);
        try {
            return await aufruf();
        } finally {
            Sanduhr.aus();
        }
    }

    static laeuft() {
        return Sanduhr._offen > 0;
    }
}
