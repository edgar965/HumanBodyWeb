/**
 * Tabfelder — die Ankreuzfelder "Ausgeklappte Tabs" einer Einstellungsseite.
 *
 * Umbau 16.08.2026 (Anforderung 6): `buildPanelCheckboxes()` stand wortgleich
 * in settings_model.html und settings_scene.html. Unterschiedlich waren nur
 * die Tab-Liste und das Namenspraefix, also genau die Werte, die jetzt als
 * Argumente hereinkommen.
 *
 * Das Praefix landet im name-Attribut (`panel_config_morphs`); die Ansicht
 * sammelt daraus beim Speichern die angekreuzten Schluessel ein.
 */
export class Tabfelder {

    /**
     * @param {string} zielId       id des umgebenden <div>
     * @param {Array<[string,string]>} tabs  [schluessel, Beschriftung]
     * @param {string} praefix      z. B. 'panel_config_'
     * @param {string} offenJson    gespeicherter Stand als JSON-Liste
     */
    static bauen(zielId, tabs, praefix, offenJson) {
        const ziel = document.getElementById(zielId);
        if (!ziel) return null;
        let offen = [];
        try {
            offen = JSON.parse(offenJson || '[]');
        } catch (fehler) {
            // Kaputter Stand darf die Seite nicht kosten — dann eben alle zu.
            console.warn('Tab-Stand nicht lesbar:', fehler);
        }
        ziel.innerHTML = '';
        tabs.forEach(([schluessel, beschriftung]) => {
            ziel.appendChild(Tabfelder._feld(
                praefix + schluessel, beschriftung, offen.includes(schluessel)));
        });
        return ziel;
    }

    static _feld(name, beschriftung, angekreuzt) {
        const beschriftungElement = document.createElement('label');
        beschriftungElement.className = 'settings-checkbox tab-feld';
        const kasten = document.createElement('input');
        kasten.type = 'checkbox';
        kasten.name = name;
        kasten.checked = angekreuzt;
        beschriftungElement.appendChild(kasten);
        beschriftungElement.appendChild(document.createTextNode(' ' + beschriftung));
        return beschriftungElement;
    }
}
