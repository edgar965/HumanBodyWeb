/**
 * Genesis9teilregler — welche Formregler zu einem Teil gehören (Brauen, Wimpern, Augen, Nägel), für den Block „Form"
 * im Popup hinter dem Zahnrad (`genesis9materialdialog.js`).
 *
 * WARUM (Edgar, 09.10.2026: „Gibt es nicht mehr Einstellungen zu den Augenbrauen usw.?"): Daz bringt für die Brauen neun
 * Formregler mit (Höhe, Dicke, Abstand, Tiefe, innen/Mitte/außen, Breite), dazu vier Asymmetrie-Regler und sechs
 * HB-Morphs; die Wimpern haben 28 (Länge, Krümmung, Locke, Wurzel), die Nägel fünf, die Augen Größe und Pupille. Sie standen
 * schon im Plan, aber verstreut in einer Liste mit 386 Reglern des Bereichs „Kopf" — gefunden hat sie so keiner (gemessen am
 * laufenden Server: `GET /api/character/genesis9-figur/regler/`). Hier werden sie nur AUSGEWÄHLT, nicht neu erfunden: dieselben
 * Regler, derselbe Weg (`Genesis9eigenschaften._zeile` → `inst.reglerSetzen`), nur ein zweites Mal am Zahnrad des Teils.
 *
 * Die Mimik (`facs_*`: Brow Up, Eye Blink …) gehört nicht dazu — das sind Ausdrücke, keine Form; nur beim Teil, der es
 * ausdrücklich verlangt (`mimik: true`), kommt ein Mimik-Regler mit (Pupille weiten).
 * Mund und Zähne haben 177 Regler über drei Bereiche und bleiben draußen (kein sinnvoller Ausschnitt ohne Rückfrage).
 */
export class Genesis9teilregler {

    /** Teil → Titel des Blocks und Muster auf Anzeigename und Kanalname; `mimik` nimmt auch Regler des Bereichs Mimik mit. */
    static TEILE = {
        brauen: { titel: 'Form der Brauen', muster: /brow/i },
        wimpern: { titel: 'Form der Wimpern', muster: /lash/i },
        augen: { titel: 'Augen: Größe und Pupille', muster: /^(200\+ )?Eyes Scale$|Pupils/i, mimik: true },
        naegel: { titel: 'Form der Nägel', muster: /nail/i },
    };

    /** Die Regler des Plans, die zu einem Teil gehören (Reihenfolge des Plans, jeder Kanal einmal). */
    static reglerFuer(plan, teil) {
        const art = Genesis9teilregler.TEILE[teil];
        if (!art) return [];
        const gesehen = new Set();
        const aus = [];
        for (const bereich of plan?.bereiche || []) {
            if (bereich.schluessel === 'mimik' && !art.mimik) continue;
            for (const regler of bereich.regler || []) {
                if (gesehen.has(regler.name)) continue;
                if (!art.muster.test(regler.anzeige || '') && !art.muster.test(regler.name)) continue;
                gesehen.add(regler.name);
                aus.push(regler);
            }
        }
        return aus;
    }

    /** Der Block „Form": Überschrift und je Regler eine Zeile (`zeileBauen(regler)` liefert sie) — leer, wenn der Teil keine hat. */
    static block(plan, teil, zeileBauen) {
        const regler = Genesis9teilregler.reglerFuer(plan, teil);
        if (!regler.length) return null;
        const block = document.createElement('div');
        block.className = 'hb-formblock';
        const kopf = document.createElement('div');
        kopf.className = 'hb-formkopf';
        kopf.textContent = `${Genesis9teilregler.TEILE[teil].titel} (${regler.length})`;
        block.appendChild(kopf);
        for (const r of regler) block.appendChild(zeileBauen(r));
        return block;
    }
}
