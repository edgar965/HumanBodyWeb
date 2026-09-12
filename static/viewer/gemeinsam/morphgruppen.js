/**
 * Morphgruppen — die 29 Morph-Kategorien des HumanBody-Netzes in drei
 * klappbare Bereiche: Gesicht, Körper, Fantasie.
 *
 * WARUM (Edgar, 12.09.2026: „Die Morphs mach auch auf- zuklappbar, auch
 * Gesicht, Körper" — und zum Format: „wie bei Augen/Wimpern … für alle"):
 * Die Liste stand als 29 Kategorien untereinander (`Morphliste`), jede für
 * sich klappbar, aber ohne Ordnung darüber. Jetzt liegt je Bereich ein
 * `panel-section` mit `h3` wie in den Vorlagen (`Klappbereiche`), darin die
 * Kategorien wie bisher.
 *
 * Die Zuordnung ist eine Tabelle, keine Heuristik: Der Hals gehört zum
 * Körper, `Face` (Ellipsoid, Dreieck …) zum Gesicht, `Fantasy` (Elfenohren,
 * Zwergenproportionen) für sich. Eine Kategorie, die hier nicht steht,
 * landet unter „Weitere" — sichtbar, nicht verschluckt.
 */
export class Morphgruppen {

    /** @type {Array<[string, string[]]>} Bereich → Kategorien (Namen aus `/api/character/morphs/`). */
    static OBER = [
        ['Gesicht', ['Cheeks', 'Chin', 'Ears', 'Eyebrows', 'Eyelids', 'Eyes', 'Face', 'Forehead',
                     'Head', 'Jaw', 'Mouth', 'Nose']],
        ['Körper', ['Abdomen', 'Armpit', 'Arms', 'Body', 'Chest', 'Elbows', 'Feet', 'Hands', 'Legs',
                    'Neck', 'Pelvis', 'Shoulders', 'Stomach', 'Torso', 'Waist', 'Wrists']],
        ['Fantasie', ['Fantasy']],
    ];
    static WEITERE = 'Weitere';

    /**
     * Kategorien auf die Bereiche verteilen — in der Reihenfolge von `OBER`,
     * innerhalb eines Bereichs in der Reihenfolge der Eingabe; leere Bereiche
     * fallen weg, Unbekanntes kommt zuletzt unter `WEITERE`.
     * @param {string[]} kategorien
     * @returns {Array<[string, string[]]>}
     */
    static aufteilen(kategorien) {
        const offen = new Set(kategorien || []);
        const aus = [];
        for (const [name, liste] of Morphgruppen.OBER) {
            const drin = (kategorien || []).filter(k => liste.includes(k));
            if (!drin.length) continue;
            for (const k of drin) offen.delete(k);
            aus.push([name, drin]);
        }
        if (offen.size) aus.push([Morphgruppen.WEITERE, [...offen]]);
        return aus;
    }

    /**
     * Ein klappbarer Bereich im Format der Vorlagen: `panel-section` mit `h3`
     * und Pfeil, Inhalt im `panel-body`. Der Klick hängt hier am Kopf, weil
     * `Klappbereiche.verdrahten` nur einmal beim Seitenaufbau läuft und
     * diesen Bereich dann noch nicht gab.
     * @returns {{block: HTMLElement, koerper: HTMLElement}}
     */
    static bereich(name, anzahl, offen = false) {
        const block = document.createElement('div');
        block.className = 'panel-section morph-bereich' + (offen ? '' : ' collapsed');
        const kopf = document.createElement('h3');
        kopf.append(`${name} (${anzahl})`);
        const pfeil = document.createElement('span');
        pfeil.className = 'chevron';
        pfeil.textContent = '▼';
        kopf.appendChild(pfeil);
        kopf.addEventListener('click', () => block.classList.toggle('collapsed'));
        const koerper = document.createElement('div');
        koerper.className = 'panel-body';
        block.append(kopf, koerper);
        return { block, koerper };
    }
}
