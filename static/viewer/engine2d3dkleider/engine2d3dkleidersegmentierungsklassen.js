/**
 * Engine2d3dKleidersegmentierungsklassen — die 28 Klassen von Sapiens und was sie in „2D3D Kleider" werden (05.10.2026).
 *
 * Edgar: „was für andere Sapiens Klassen gibt es noch? Noch anderen Einstellungen, die du mir bisher verschwiegen hast? … zeige mir die Optionen in der Oberfläche." Die Tabelle steht aufklappbar in
 * der Karte „Segmentierung": je Klasse (links/rechts zusammengefasst), was sie bedeutet, WAS sie jetzt wird (nach den Optionen `schuhe`, `socken`, `zubehoer`; der Rest ist fest) und — nach einem
 * Lauf — wie viel gesehene Netzfläche sie nach der stärksten Stimme trägt (`kennzahlen.klassen`). Die Zuordnung selbst macht `Kleidung/sapienszuordnung.py`; diese Liste muss mit ihr
 * übereinstimmen (ein Test prüft die Klassennamen).
 */
export class Engine2d3dKleidersegmentierungsklassen {

    static ZIELE = { fuesse: 'Socken / Schuhe', zubehoer: 'Zubehör', oberteil: 'Oberteil', hose: 'Hose / Rock', haut: 'nicht Kleidung (Haut)', haar: 'Haar' };

    /** [Sapiens-Klassen, Bedeutung, Ziel (fest) oder {option}, Anmerkung] */
    static KLASSEN = [
        [['Background'], 'Hintergrund', 'keine Stimme', 'zählt nicht; Pixel im Hintergrund gelten als schlechte Einpassung'],
        [['Upper_Clothing'], 'Oberteil (Shirt, Hemd, Jacke)', 'oberteil', ''],
        [['Lower_Clothing'], 'Hose, Rock, Shorts', 'hose', ''],
        [['Apparel'], 'Sonstige Bekleidung', { option: 'zubehoer', vorgabe: 'zubehoer' }, 'Jacke, Mütze, Schal, Uhr …'],
        [['Left_Shoe', 'Right_Shoe'], 'Schuhe', { option: 'schuhe', vorgabe: 'fuesse' }, 'ein Fuß in schwarzer Socke kommt hier heraus (gemessen)'],
        [['Left_Sock', 'Right_Sock'], 'Socken', { option: 'socken', vorgabe: 'fuesse' }, 'oft nur ein schmaler Streifen am Knöchel'],
        [['Hair'], 'Haar', 'haar', 'nie Kleidung; die Haarmaske nimmt es bei Option „Haar aus der Segmentierung“'],
        [['Face_Neck'], 'Gesicht und Hals', 'haut', ''],
        [['Torso'], 'Rumpf (nackt)', 'haut', ''],
        [['Left_Upper_Arm', 'Right_Upper_Arm'], 'Oberarme', 'haut', ''],
        [['Left_Lower_Arm', 'Right_Lower_Arm'], 'Unterarme', 'haut', ''],
        [['Left_Hand', 'Right_Hand'], 'Hände', 'haut', ''],
        [['Left_Upper_Leg', 'Right_Upper_Leg'], 'Oberschenkel', 'haut', ''],
        [['Left_Lower_Leg', 'Right_Lower_Leg'], 'Unterschenkel', 'haut', ''],
        [['Left_Foot', 'Right_Foot'], 'Füße (nackt)', 'haut', ''],
        [['Lower_Lip', 'Upper_Lip', 'Lower_Teeth', 'Upper_Teeth', 'Tongue'], 'Lippen, Zähne, Zunge', 'haut', 'bisher ungenutzt (Mundöffnung wäre eine Anwendung)'],
    ];

    constructor(behaelter) {
        this.behaelter = behaelter;
        this._stand = null;
    }

    zeigen(optionen, kennzahlen) {
        const stand = JSON.stringify([optionen?.schuhe, optionen?.socken, optionen?.zubehoer, kennzahlen?.klassen]);
        if (stand === this._stand) return;
        this._stand = stand;
        const ziele = Engine2d3dKleidersegmentierungsklassen.ZIELE;
        const je = kennzahlen?.klassen || null;
        const details = document.createElement('details');
        const titel = document.createElement('summary');
        titel.textContent = 'Die 28 Klassen von Sapiens und was sie hier werden';
        titel.className = 'hb-hinweis';
        details.appendChild(titel);
        const tabelle = document.createElement('table');
        tabelle.className = 'table table-sm engine2d3dkleider-stuecketabelle';
        const kopf = tabelle.createTHead().insertRow();
        for (const text of ['Klasse', 'Bedeutung', 'wird', 'gesehen (cm²)', 'Anmerkung']) {
            const zelle = document.createElement('th');
            zelle.textContent = text;
            kopf.appendChild(zelle);
        }
        const koerper = tabelle.createTBody();
        for (const [namen, bedeutung, ziel, anmerkung] of Engine2d3dKleidersegmentierungsklassen.KLASSEN) {
            const wert = typeof ziel === 'object' ? (optionen?.[ziel.option] || ziel.vorgabe) : ziel;
            const zeile = koerper.insertRow();
            const cm2 = je ? namen.reduce((s, n) => s + (je[n]?.cm2 || 0), 0) : null;
            const zellen = [namen.join(' / '), bedeutung, ziele[wert] || wert, cm2 === null ? '—' : Math.round(cm2).toLocaleString('de-DE'), anmerkung];
            zellen.forEach((text, i) => {
                const zelle = zeile.insertCell();
                zelle.textContent = text;
                if (i === 2 && typeof ziel === 'object') zelle.title = `Einstellbar: Option „${ziel.option}“`;
                if (i === 3) zelle.style.textAlign = 'right';
            });
        }
        details.appendChild(tabelle);
        this.behaelter.replaceChildren(details);
    }
}
