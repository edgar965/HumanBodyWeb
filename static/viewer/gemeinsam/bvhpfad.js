/**
 * Bvhpfad — der Pfad der BVH oben auf der Ergebnisseite: Ordner, Datei,
 * Bibliothekskopie, je ein Knopf für die Zwischenablage.
 *
 * WARUM (Edgar, 13.09.2026: „auf allen ergebnis seiten … sollte immer der
 * Pfad der BVH kommen, so dass ich das Verzeichnis kopieren kann"): Der
 * Pfad stand schon da, aber nur als eine Zeile mit der Datei — den Ordner
 * musste man von Hand herausschneiden. Hier wird der Ordner aus dem
 * Dateipfad genommen (`ordner`) und jeder Teil hat seinen Knopf.
 *
 * Vorlage: `_bvh_pfad.html` (`data-pfad` am Behälter, `data-kopie` an den
 * Knöpfen, `<code>`-Felder `bvhOrdner`, `bvhDatei`, `bvhKopie`). Ohne DOM
 * prüfbar: `ordner()` ist reine Textarbeit (`test_js_bvhpfad.py`).
 */
export class Bvhpfad {

    /** So lange zeigt der Knopf „kopiert" (ms). */
    static RUECKMELDUNG_MS = 1200;

    /** Der Ordner eines Pfads — Windows- oder POSIX-Trenner, ohne den Trenner am Ende. */
    static ordner(pfad) {
        const text = String(pfad || '');
        const schnitt = Math.max(text.lastIndexOf('\\'), text.lastIndexOf('/'));
        return schnitt > 0 ? text.slice(0, schnitt) : text;
    }

    /** Die drei Texte des Blocks, wie die Knöpfe sie kopieren. */
    static texte(behaelter) {
        const pfad = behaelter?.dataset?.pfad || '';
        return {
            ordner: Bvhpfad.ordner(pfad),
            datei: pfad,
            kopie: behaelter?.querySelector('#bvhKopie')?.textContent?.trim() || '',
        };
    }

    static verdrahten(behaelter) {
        if (!behaelter) return false;
        const texte = Bvhpfad.texte(behaelter);
        const ordnerFeld = behaelter.querySelector('#bvhOrdner');
        if (ordnerFeld) ordnerFeld.textContent = texte.ordner;
        for (const knopf of behaelter.querySelectorAll('.bvh-kopieren')) {
            knopf.addEventListener('click', () => Bvhpfad.kopieren(knopf, texte[knopf.dataset.kopie] || ''));
        }
        return true;
    }

    /** In die Zwischenablage — mit kurzer Rückmeldung am Knopf. */
    static async kopieren(knopf, text) {
        if (!text) return false;
        let gelungen = false;
        try {
            await navigator.clipboard.writeText(text);
            gelungen = true;
        } catch (fehler) {
            // Ohne Zwischenablage-Recht: den Text markieren und über den
            // alten Weg kopieren — Strg+C nähme die Markierung ebenso.
            const feld = knopf.parentElement?.querySelector('code');
            if (feld) window.getSelection()?.selectAllChildren(feld);
            try { gelungen = document.execCommand('copy'); } catch (e2) { gelungen = false; }
        }
        if (!gelungen) return false;
        const vorher = knopf.innerHTML;
        knopf.innerHTML = '<i class="fas fa-check"></i> kopiert';
        setTimeout(() => { knopf.innerHTML = vorher; }, Bvhpfad.RUECKMELDUNG_MS);
        return true;
    }
}
