/**
 * Mhkopfzeile — die eine Zeile über den MakeHuman-Eigenschaften.
 *
 * Sie steht in einem eigenen Modul, weil zwei Seiten sie auffrischen: der
 * Aufbau des Panels (`Mheigenschaften`) und jede Änderung an Netzteilen,
 * Glättung oder Größe (`Mhkoerperregler`). Ein gegenseitiger Import der beiden
 * wäre ein Ring — hier holen ihn beide von derselben Stelle.
 */
export class Mhkopfzeile {

    static KENNUNG = 'prop-mh-figur-kopf';

    /** Zentimeter mit Komma — `toFixed` schreibt einen Punkt. */
    static ZENTIMETER = new Intl.NumberFormat('de-DE',
        { minimumFractionDigits: 1, maximumFractionDigits: 1 });

    static angleichen(inst) {
        const zeile = document.getElementById(Mhkopfzeile.KENNUNG);
        if (!zeile || !inst) return;
        const stuecke = inst.getragen().length;
        zeile.textContent = [
            `${inst.punktzahl.toLocaleString('de-DE')} Punkte`,
            `${Mhkopfzeile.ZENTIMETER.format(inst.sichtbareHoehe() * 100)} cm`,
            inst.glatt ? 'geglättet' : 'Basisnetz',
            stuecke ? `${stuecke} Kleidungsstück${stuecke === 1 ? '' : 'e'}`
                    : 'unbekleidet',
        ].join(' · ');
    }
}
