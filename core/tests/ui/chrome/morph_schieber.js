/* UI-Testfälle für die Morph-Schieber der Szene (Chrome, 17.10.2026) — wird im Szenen-Tab `/Charakter/` ausgeführt (Chrome-MCP `javascript_tool`), nicht von `manage.py test`.
 *
 * WARUM (Edgar, 17.10.2026: „Teste alle Morphs, mach dir UI testcases, ob die funktionieren"): Der Server-Test (`longrunner/test_genesis9_alter_semantik.py`) prüft die Ablagen und die Formung;
 * ob ein Schieber im Browser das Netz verändert, prüft nur der Schieber selbst. Dieses Skript bewegt ihn wie ein Mensch (Wert setzen, `input`-/`change`-Ereignis) und misst am Netz der Haut.
 *
 * ABLAUF (jeder Aufruf höchstens 45 s, sonst bricht das Werkzeug ab — lange Läufe als Promise starten und nur den Stand abfragen)
 *   (0, eval)(text dieser Datei)                    // legt window.__morphTest an
 *   await __morphTest.start();                      // Referenz: Lebensalter und Alter auf 0, Netz kopieren. VORHER: kein anderer Schieber verstellt!
 *   await __morphTest.fall('lebensalter');          // benannte Fälle: lebensalter | alter | makros
 *   window.__morphLauf = 'laeuft'; __morphTest.alle().then(r => { window.__morphLauf = r; });   // jeder Schieber der Familien hb/mh/sx/uma auf seinen Anschlag, im Hintergrund des Tabs
 *   __morphTest.bericht();                          // Stand und Ergebnis als kurzer Text (während des Laufs jederzeit abfragbar)
 *   __morphTest.abbruch = true;                     // hält den Lauf an; danach `zurueck()`
 *   await __morphTest.zurueck();                    // alle angefassten Schieber auf ihren Ausgangswert
 *
 * MESSGRÖSSEN (Haut, `inst.bodyMesh.geometry`): Höhe (Meter), Bauchtiefe vorn (Mittelebene, Band 55–62 % der Höhe), größte Verschiebung gegen die Referenz (Millimeter).
 *
 * FALLEN, an denen der erste Lauf scheiterte (17.10.2026):
 *   1. Das Netz kommt in Stufen. Wer nach der ersten Änderung sofort den nächsten Schieber setzt, wird von der UI überrollt: der Schieber springt auf 1 zurück, der Reset wirkt nie, und alle
 *      folgenden Messungen laufen gegen ein verstelltes Netz (bewegt_mm 644,47 bei jedem Regler — ein konstanter Wert ist ein Warnzeichen, kein Befund). Deshalb wartet `setze`/`alle` bis das Netz
 *      `still` Millisekunden unverändert ist, und `alle` prüft nach jedem Schritt, dass die Schieber wirklich stehen (`steht`).
 *   2. `alle` stellt den VORHERIGEN Schieber und den neuen in EINEM Zug (zwei Ereignisse hintereinander, ein Aufbau): halbiert die Zeit; gegengeprobt — Abdomen_Mass → 0 und Abdomen_Tone → 1 gab
 *      4,05 mm, dieselbe Wirkung wie Abdomen_Tone allein.
 *   3. `javascript_tool` blockt Ausgaben, die wie `name=wert` aussehen — Ergebnisse mit Leerzeichen formatieren.
 *   4. Der Tab muss sichtbar sein (`document.visibilityState`), sonst drosselt Chrome die Zeitgeber.
 *   5. Zwei Ereignisse in einem Zug sind zwei Aufbauten hintereinander (gemessen: Body_Size → 0 und Arms_ForearmLength → 1: Netz bewegt sich nach 1,6 s um 606 mm — der Reset —, der zweite Schieber
 *      springt dabei auf 0 zurück, nach 3,2 s kommt +54,9 mm und der Schieber steht wieder auf 1). Wer nach der ersten Änderung nur Ruhe abwartet, hört in der Pause von 1,6 s auf und misst gegen
 *      ein halbes Ergebnis. `alle` wartet deshalb zusätzlich auf den Sollzustand beider Schieber.
 * Ein Schieber gilt als OHNE WIRKUNG, wenn das Netz sich binnen `ende` ms nicht ändert und der Abstand zur Referenz unter 0,1 mm bleibt.
 */
(() => {
    const WARTE_MS = 20000;
    const inst = () => [...window.__characters.values()][0];
    const regler = (name) => document.querySelector(`input[data-regler="${name}"]`);
    const schlafen = (ms) => new Promise((r) => setTimeout(r, ms));
    const ereignisse = (el) => {
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    };
    const setzen = (name, wert) => {
        const el = regler(name);
        if (!el) throw new Error('Schieber fehlt: ' + name);
        el.value = String(wert);
        ereignisse(el);
    };

    const T = {
        ergebnisse: [], angefasst: new Map(), ref: null, stand: 0, letzter: null, abbruch: false, probleme: [],

        netz() {
            const g = inst().bodyMesh.geometry;
            return { g, p: g.attributes.position.array, n: g.attributes.position.count };
        },
        kopie() { return Float32Array.from(T.netz().p); },
        hoehe(p) {
            let lo = 1e9, hi = -1e9;
            for (let i = 1; i < p.length; i += 3) { if (p[i] < lo) lo = p[i]; if (p[i] > hi) hi = p[i]; }
            return hi - lo;
        },
        bauch(p) {
            let lo = 1e9, hi = -1e9;
            for (let i = 1; i < p.length; i += 3) { if (p[i] < lo) lo = p[i]; if (p[i] > hi) hi = p[i]; }
            let vorn = -1e9;
            for (let i = 0; i < p.length; i += 3) {
                const rel = (p[i + 1] - lo) / (hi - lo);
                if (Math.abs(p[i]) < 0.06 && rel > 0.55 && rel < 0.62 && p[i + 2] > vorn) vorn = p[i + 2];
            }
            return vorn;
        },
        verschiebung(a, b) {
            let m = 0;
            for (let i = 0; i < a.length; i += 3) {
                const d = Math.hypot(a[i] - b[i], a[i + 1] - b[i + 1], a[i + 2] - b[i + 2]);
                if (d > m) m = d;
            }
            return m * 1000;
        },

        /** Schieber setzen wie ein Mensch; wartet auf die erste Änderung des Netzes und dann, bis es `still` ms ruhig ist. */
        async setze(name, wert, warte = WARTE_MS, still = 1300) {
            const el0 = regler(name);
            if (!el0) throw new Error('Schieber fehlt: ' + name);
            if (!T.angefasst.has(name)) T.angefasst.set(name, el0.value);
            if (+el0.value === +wert) return { ms: 0, netz: T.kopie(), geaendert: false, steht: true };
            const t0 = performance.now();
            let geaendert = false;
            for (let versuch = 0; versuch < 3 && !geaendert; versuch++) {
                const vorher = T.kopie();
                setzen(name, wert);
                const t1 = performance.now();
                while (performance.now() - t1 < (versuch ? 6000 : warte)) {
                    await schlafen(120);
                    const jetzt = T.netz().p;
                    if (jetzt.length !== vorher.length || T.verschiebung(vorher, jetzt) > 1e-3) { geaendert = true; break; }
                }
                if (!geaendert && warte < 3000) break;
            }
            let ruhe = performance.now(), letzt = T.kopie();
            while (geaendert && performance.now() - ruhe < still && performance.now() - t0 < warte + 8000) {
                await schlafen(150);
                const jetzt = T.netz().p;
                if (jetzt.length !== letzt.length || T.verschiebung(letzt, jetzt) > 1e-3) { ruhe = performance.now(); letzt = Float32Array.from(jetzt); }
            }
            return { ms: Math.round(performance.now() - t0), netz: T.kopie(), geaendert, steht: +regler(name).value === +wert };
        },

        async start() {
            T.ergebnisse = []; T.stand = 0; T.letzter = null; T.probleme = []; T.abbruch = false;
            await T.setze('alter:jahre', 0);
            await T.setze('alter:gesamt', 0);
            T.ref = T.kopie();
            return 'Referenz: ' + T.netz().n + ' Punkte, Höhe ' + T.hoehe(T.ref).toFixed(3) + ' m, Bauch vorn ' + T.bauch(T.ref).toFixed(3) + ' m';
        },

        async zurueck() {
            for (const [name, alt] of T.angefasst) { await T.setze(name, alt); }
            T.angefasst.clear();
            return 'zurückgesetzt, Abweichung zur Referenz ' + T.verschiebung(T.ref, T.netz().p).toFixed(2) + ' mm';
        },

        async fall(name) {
            const f = T.faelle[name];
            if (!f) throw new Error('Fall unbekannt: ' + name);
            const aus = [];
            const h0 = T.hoehe(T.ref), b0 = T.bauch(T.ref);
            for (const [regl, wert, erwartet] of f) {
                const r = await T.setze(regl, wert);
                const h = T.hoehe(r.netz), b = T.bauch(r.netz);
                const zeile = { regler: regl, wert, ms: r.ms, hoehe_prozent: +(h / h0 * 100).toFixed(1), bauch_mm: +((b - b0) * 1000).toFixed(0), bewegt_mm: +T.verschiebung(T.ref, r.netz).toFixed(1) };
                zeile.ok = erwartet(zeile);
                aus.push(zeile);
                await T.setze(regl, 0, r.geaendert ? WARTE_MS : 1500);
            }
            T.ergebnisse.push(...aus.map((z) => ({ fall: name, ...z })));
            return JSON.stringify(aus.map((z) => [z.regler, z.wert, z.ms + 'ms', z.hoehe_prozent + '%', z.bauch_mm + 'mm', z.bewegt_mm + 'mm', z.ok ? 'ok' : 'FALSCH']));
        },

        /** Jeder Schieber der Familien auf seinen Anschlag; der vorherige geht im selben Zug auf 0 (siehe Falle 2). */
        async alle({ familien = ['hb', 'mh', 'sx', 'uma'], maxSekunden = 100000, still = 1000, ende = 14000 } = {}) {
            const t0 = performance.now();
            const namen = [...document.querySelectorAll('input[data-regler]')].map((e) => e.dataset.regler).filter((n) => familien.some((f) => n.startsWith(f + ':')));
            let i = T.stand;
            for (; i < namen.length && !T.abbruch && (performance.now() - t0) / 1000 < maxSekunden; i++) {
                const name = namen[i], el = regler(name);
                const anschlag = Math.abs(+el.max) >= Math.abs(+el.min) ? +el.max : +el.min;
                // Sollzustand: der neue Schieber steht auf dem Anschlag, der vorherige auf 0 (Falle 5: die UI beantwortet zwei Ereignisse nacheinander und setzt den zweiten Schieber dazwischen zurück).
                const soll = () => +regler(name).value === anschlag && (!T.letzter || T.letzter === name || +regler(T.letzter).value === 0);
                const vorher = T.kopie();
                if (T.letzter && T.letzter !== name) setzen(T.letzter, 0);
                setzen(name, anschlag);
                const t1 = performance.now();
                let geaendert = false, ruhe = performance.now(), letzt = vorher;
                while (performance.now() - t1 < ende) {
                    await schlafen(120);
                    const j = T.netz().p;
                    if (j.length !== letzt.length || T.verschiebung(letzt, j) > 1e-3) { geaendert = true; ruhe = performance.now(); letzt = Float32Array.from(j); }
                    else if (geaendert && soll() && performance.now() - ruhe >= still) break;
                }
                const bewegt = T.verschiebung(T.ref, T.netz().p);
                const steht = soll();
                T.ergebnisse.push({ fall: 'alle', regler: name, wert: anschlag, ms: Math.round(performance.now() - t1), bewegt_mm: +bewegt.toFixed(2), ok: bewegt >= 0.1 && steht, steht });
                if (!steht) T.probleme.push(name);
                T.angefasst.set(name, T.angefasst.get(name) ?? '0');
                T.letzter = name;
                T.stand = i + 1;
            }
            return 'Stand ' + T.stand + ' von ' + namen.length + (T.stand >= namen.length ? ' - fertig' : ' - angehalten');
        },

        bericht() {
            const alle = T.ergebnisse;
            const schlecht = alle.filter((z) => !z.ok);
            return 'Lauf ' + window.__morphLauf + ' | Ergebnisse ' + alle.length + ', ohne Wirkung/falsch ' + schlecht.length + ', Schieber nicht gestanden ' + T.probleme.length + ': '
                + schlecht.slice(0, 40).map((z) => z.regler + ' (' + (z.bewegt_mm ?? '') + ' mm, ' + z.ms + ' ms)').join(', ');
        },
    };

    /* Erwartungen der benannten Fälle: [Schieber, Wert, Prüfung der Zeile]. Quellen der Zahlen: test_genesis9_alter_semantik.py (Ursula, 17.10.2026). */
    T.faelle = {
        // Seit 18.10.2026 ab 18 Jahren (Anschlag −0,29; Kinder: Genesis 1) — Ursula am Server 90,3 % bei 18, 95,0 % bei 21 Jahren (`alter_ab18.py`).
        lebensalter: [
            ['alter:jahre', -0.29, (z) => z.hoehe_prozent > 86 && z.hoehe_prozent < 95],
            ['alter:jahre', -0.15, (z) => z.hoehe_prozent > 92 && z.hoehe_prozent < 98],
            ['alter:jahre', 0.5, (z) => z.hoehe_prozent > 96 && z.hoehe_prozent < 100.5 && z.bauch_mm < 35],
            ['alter:jahre', 1.0, (z) => z.hoehe_prozent > 96 && z.hoehe_prozent < 100.5 && z.bauch_mm < 35],
        ],
        // „Wirkt älter / jünger“ ändert nur das Aussehen, nie die Größe (Vorschlag A, 17.10.2026): vorher −1 = 85–95 % der Höhe (Kind × 0,5). Unter dem Ausgangsgesicht gibt es nichts
        // (HumanBody kennt nur 18–100 Jahre): auf einem 25-Jährigen tut „jünger“ nichts (Netz unverändert).
        alter: [
            ['alter:gesamt', -1.0, (z) => z.hoehe_prozent > 99.9 && z.hoehe_prozent < 100.1 && z.bewegt_mm < 0.1],
            ['alter:gesamt', 1.0, (z) => z.hoehe_prozent > 96 && z.hoehe_prozent < 102 && z.bauch_mm < 25 && z.bewegt_mm > 1],
        ],
        makros: [
            ['mh:macro_Groesse', 1.0, (z) => z.hoehe_prozent > 115],
            ['mh:macro_Groesse', -1.0, (z) => z.hoehe_prozent < 90],
            ['mh:macro_Gewicht', 1.0, (z) => z.bewegt_mm > 5],
            ['mh:macro_Gewicht', -1.0, (z) => z.bewegt_mm > 5],
            ['mh:macro_Geschlecht', 1.0, (z) => z.hoehe_prozent > 104],
        ],
    };
    window.__morphTest = T;
    return 'morphTest bereit';
})();
