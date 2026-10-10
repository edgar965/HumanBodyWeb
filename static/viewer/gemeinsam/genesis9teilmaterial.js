/**
 * Genesis9teilmaterial — Glanz, Rauheit, Relief, Deckkraft und Feuchte je Teil einer Genesis-9-Figur.
 *
 * WARUM (Edgar, 09.10.2026, mit Bild der Augen: „glasig / grau" — dann „mach mir Einstellungen, wo ich
 * Glanz, Rauheit usw. ändern kann, auch bei Augenbrauen usw."): Die Daz-Presets bringen Glanz und
 * Rauheit mit (Amala, Ursula, Olesia: Glanz 1, Rauheit 0,6; Damiras eigene Augen: 0 und 0). Bei Glanz 1 und
 * Rauheit 0,6 liegt ein milchiger Schleier über Iris und Pupille — gemessen im Chrome an Ursulas grünen
 * Augen, gleiche Karte, gleiche Lichter: Pupille grau, Iris blass; mit Glanz 0 schwarze Pupille und
 * kräftige Iris. Die Augen haben darum einen eigenen Standard (`TEILE.augen`: Rauheit 0,1, Glanz 0,25), und jeder
 * Teil lässt sich im Popup hinter dem Zahnrad neben seiner Auswahl (`genesis9materialdialog.js`) verstellen.
 *
 * ZWEITER BEFUND (Edgar mit Bild von „Damira · Eyes Blue" und Damiras eigener Haut, „funktioniert nicht!!!"): (1) die Glasschichten
 * `EyeMoisture`/`Tear` waren weiß mit 12 % Deckkraft und lagen, wie eine milchige Fläche beleuchtet, als Schleier über Iris und
 * Pupille (Pupille grau statt schwarz) — jetzt klar (Farbe schwarz, additiv, `Genesis9netz.material`), Deckkraft = Stärke der
 * Spiegelung (`feuchte`, `traene`); (2) die weißen Streifen unter den Augen und an der Nase sind Haut-Glanzlichter (Rauheitskarte
 * des Kopfes) — nicht Augen, nicht Tränen: gemessen mit klaren Schichten und ohne Tränenlinie, die Streifen bleiben; mit Glanz
 * 0,3 oder Rauheit ×1,5 sind sie stark gedämpft, mit beiden fast weg (Chrome, Damira · Eyes Blue, Haut „Wie im Katalog");
 * (3) die Haut war ein `MeshStandardMaterial` ohne `specularIntensity` — das Glanz-Feld wäre wirkungslos geblieben, darum
 * Physical für Augen UND Haut (`Genesis9netz.EINSTELLBAR`). Die Rauheit von Haut, Nägeln und Mund ist ein Faktor (bis 2) auf den
 * Ausgangswert jedes Materials: Kopf (Karte, 1) und Körper (0,6) behalten ihren Abstand.
 *
 * WIE: Die Werte liegen je Figur in `inst.teilmaterial = {teil: {feld: wert}}` (geht mit „Modell speichern"
 * mit) und werden NACH JEDEM Neubau auf die frischen Materialien gelegt (`Genesis9Modell.koerperAufbauen`)
 * — Materialien entstehen bei jedem Reglerzug neu. Ein Wert, den ein spät geladenes Bild überschreibt
 * (Rauheitskarte: `material.roughness = 1`, `Genesis9netz.texturen`), kommt über den Haken
 * `material.userData.teilnach` zurück (`Genesis9texturen.holen` ruft ihn nach jedem Bild).
 * Ohne eigenen Wert gilt der Standard des Felds, sonst bleibt das Material, wie das Preset es lieferte;
 * „auf Standard" nimmt den vor dem ersten Eingriff gemerkten Wert zurück (`userData.teilStandard`).
 *
 * Nicht erfasst: Kleidung und Haar (eigene Werte je Stück, `stueckstoff.js`), Ersatz-Augen aus einer .blend.
 */
export class Genesis9teilmaterial {

    /** Die Felder: Eigenschaft am Material und Bereich des Schiebers. */
    static FELDER = {
        glanz: { titel: 'Glanz', eig: 'specularIntensity', min: 0, max: 1, schritt: 0.05,
                 hilfe: 'Stärke der Spiegelung. 0 = matt; hoch bei rauer Fläche wirkt wie ein milchiger Schleier.' },
        rauheit: { titel: 'Rauheit', eig: 'roughness', min: 0, max: 2, schritt: 0.05,
                   hilfe: 'Klein = scharfe Glanzpunkte, groß = breites, mattes Licht. Mit Rauheitskarte (Haut): Faktor darauf — '
                       + 'über 1 verschwinden die weißen Glanzstreifen unter den Augen und an der Nase.' },
        relief: { titel: 'Relief', eig: 'normalScale', min: 0, max: 2, schritt: 0.05,
                  hilfe: 'Stärke der Normalenkarte (Poren, Härchen, Irisstruktur).' },
        deckkraft: { titel: 'Deckkraft', eig: 'opacity', min: 0, max: 1, schritt: 0.05,
                     hilfe: 'Wie dicht Härchen und Wimpern stehen (1 = wie geliefert).' },
        feuchte: { titel: 'Feuchte', eig: 'opacity', min: 0, max: 1, schritt: 0.05,
                   hilfe: 'Spiegelung der Hornhaut (Glanzschicht EyeMoisture, nur Licht, keine Farbe): das Lichtpünktchen im Auge.' },
        traene: { titel: 'Tränenfilm', eig: 'opacity', min: 0, max: 1, schritt: 0.05,
                  hilfe: 'Spiegelung des Tränenfilms am unteren Lid (Tear). 0 = aus.' },
    };

    static _AUGE = /^Eye (Left|Right)$/;

    /**
     * Die Teile. `gruppe` = Name der Materialgruppe (`material.userData.gruppe`, vom Server), `felder` =
     * die Felder des Teils; ein Feld kann eine eigene `gruppe` und einen `standard` tragen (Zahl).
     * Eine Gruppe gehört zu genau einem Teil — gesucht wird nur am Körper und an den Anhängen.
     */
    static TEILE = {
        haut: { titel: 'Haut', gruppe: /^(Head|Body|Arms|Legs)$/, felder: { glanz: {}, rauheit: { relativ: true }, relief: {} } },
        augen: { titel: 'Augen', gruppe: Genesis9teilmaterial._AUGE, felder: {
            glanz: { standard: 0.25 }, rauheit: { standard: 0.1 }, relief: {},
            feuchte: { gruppe: /^EyeMoisture/, standard: 1 }, traene: { gruppe: /^Tear/, standard: 0.4 },
        } },
        // `anhang`: ALLE Materialien des Brauennetzes (`inst.anhangNetze.brauen`), egal wie die Gruppe heißt — Karten und Fasern heißen `Eyebrows_…`, aber
        // „MB Olesia Brows Apply" `hairPhysicalShader1SG` und Kins Brauen `Layer1`/`Layer2` (Edgar, 10.10.2026: Deckkraft und Glanz wirkten dort nicht).
        brauen: { titel: 'Augenbrauen', gruppe: /^Eyebrows/, anhang: 'brauen', felder: { deckkraft: {}, glanz: {}, rauheit: {} } },
        wimpern: { titel: 'Wimpern', gruppe: /^Eyelashes/, felder: { deckkraft: {}, glanz: {}, rauheit: {} } },
        naegel: { titel: 'Nägel', gruppe: /^(Fingernails|Toenails)$/, felder: { glanz: {}, rauheit: { relativ: true }, relief: {} } },
        mund: { titel: 'Mund und Zähne', gruppe: /^(Mouth|Teeth|Mouth Cavity)$/,
                felder: { glanz: {}, rauheit: { relativ: true }, relief: {} } },
    };

    /** Alle Materialien, an denen die Teile liegen: Körper und Anhänge (nicht die Kleidung). Die Materialien eines Anhangs
     *  tragen seinen Schlüssel (`userData.anhang`: augen, mund, wimpern, traene, brauen) — daran erkennt `_passt` ein Teil, das nicht an Gruppennamen hängt. */
    static materialien(inst) {
        const aus = [];
        for (const [schluessel, netz] of [['', inst?.bodyMesh], ...Object.entries(inst?.anhangNetze || {})]) {
            if (!netz) continue;
            for (const material of [].concat(netz.material).filter(Boolean)) {
                if (schluessel) (material.userData ??= {}).anhang = schluessel;
                aus.push(material);
            }
        }
        return aus;
    }

    /** Das Feld eines Teils (Teil + Feld + Standard) für dieses Material — oder null, wenn es nicht dazugehört. */
    static _passt(material, teil, feld) {
        const def = Genesis9teilmaterial.TEILE[teil];
        const f = def?.felder[feld];
        if (!f) return null;
        if (def.anhang && material.userData?.anhang === def.anhang && !f.gruppe) return f;
        const name = material.userData?.gruppe || '';
        return (f.gruppe || def.gruppe).test(name) ? f : null;
    }

    static _kann(material, feld) {
        const eig = Genesis9teilmaterial.FELDER[feld].eig;
        return eig === 'normalScale' ? !!material.normalScale : eig in material;
    }

    static _lesen(material, feld) {
        const eig = Genesis9teilmaterial.FELDER[feld].eig;
        return eig === 'normalScale' ? material.normalScale.x : material[eig];
    }

    static _setzen(material, feld, wert) {
        const eig = Genesis9teilmaterial.FELDER[feld].eig;
        // Die Normalenkarte von DirectX hat Y verkehrt (`normalScale.y < 0`): das Vorzeichen bleibt.
        if (eig === 'normalScale') material.normalScale.set(wert, wert * (Math.sign(material.normalScale.y) || 1));
        else material[eig] = wert;
        material.needsUpdate = true;
    }

    /** Der Ausgangswert dieses Materials: vor dem ersten Eingriff gemerkt; Rauheit mit Karte ist ein Faktor und steht auf 1. */
    static _basis(material, feld) {
        if (feld === 'rauheit' && material.userData.gehoertKarte) return 1;   // `Genesis9netz.texturen`, auch wenn die Karte noch lädt
        return material.userData.teilStandard?.[feld];
    }

    /** Der Wert, auf den „Standard" zurückführt: der des Felds, sonst der Ausgangswert des Materials. */
    static _standard(material, feld, def) {
        return typeof def.standard === 'number' ? def.standard : Genesis9teilmaterial._basis(material, feld);
    }

    /**
     * Der Wert für dieses Material. Ein `relativ`es Feld (Rauheit von Haut, Nägeln, Mund) ist ein FAKTOR auf den Ausgangswert
     * des Materials: Kopf (Karte, 1) und Körper (ohne Karte, 0,6) behalten ihren Abstand, 1 = wie geliefert.
     */
    static _soll(material, feld, def, eigen) {
        if (def.relativ) {
            const basis = Genesis9teilmaterial._basis(material, feld);
            return typeof basis === 'number' ? basis * (typeof eigen === 'number' ? eigen : 1) : undefined;
        }
        return typeof eigen === 'number' ? eigen : Genesis9teilmaterial._standard(material, feld, def);
    }

    /** Alle Felder, die zu diesem Material passen, auf den Stand der Figur legen. */
    static auflegen(inst, material) {
        const daten = material.userData;
        daten.teilStandard ??= {};
        for (const teil of Object.keys(Genesis9teilmaterial.TEILE)) {
            for (const feld of Object.keys(Genesis9teilmaterial.TEILE[teil].felder)) {
                const def = Genesis9teilmaterial._passt(material, teil, feld);
                if (!def || !Genesis9teilmaterial._kann(material, feld)) continue;
                if (!(feld in daten.teilStandard)) daten.teilStandard[feld] = Genesis9teilmaterial._lesen(material, feld);
                if (material.roughnessMap) daten.gehoertKarte = true;
                const soll = Genesis9teilmaterial._soll(material, feld, def, inst.teilmaterial?.[teil]?.[feld]);
                if (typeof soll === 'number' && Math.abs(Genesis9teilmaterial._lesen(material, feld) - soll) > 1e-9) {
                    Genesis9teilmaterial._setzen(material, feld, soll);
                }
            }
        }
        // Nach einem spät geladenen Bild (Rauheitskarte setzt `roughness = 1`) wieder auflegen.
        daten.teilnach = () => Genesis9teilmaterial.auflegen(inst, material);
    }

    /** Nach jedem Neubau von Körper und Anhängen: die Werte der Figur auf die frischen Materialien. */
    static anwenden(inst) {
        for (const material of Genesis9teilmaterial.materialien(inst)) Genesis9teilmaterial.auflegen(inst, material);
    }

    /** Einen Wert stellen und sofort anwenden; `wert` null/undefiniert = zurück auf den Standard. */
    static setzen(inst, teil, feld, wert) {
        inst.teilmaterial ??= {};
        const bisher = { ...(inst.teilmaterial[teil] || {}) };   // neues Objekt: die gespeicherte Figur hält eine flache Kopie
        if (typeof wert === 'number' && Number.isFinite(wert)) bisher[feld] = wert; else delete bisher[feld];
        if (Object.keys(bisher).length) inst.teilmaterial[teil] = bisher; else delete inst.teilmaterial[teil];
        Genesis9teilmaterial._zurueck(inst, teil, feld, typeof bisher[feld] !== 'number');
        Genesis9teilmaterial.anwenden(inst);
    }

    /** Ein Feld oder (feld = null) alle Felder eines Teils auf Standard. */
    static zuruecksetzen(inst, teil, feld = null) {
        const felder = feld ? [feld] : Object.keys(Genesis9teilmaterial.TEILE[teil].felder);
        for (const f of felder) Genesis9teilmaterial.setzen(inst, teil, f, null);
    }

    /** Ohne eigenen Wert und ohne festen Standard: das Material auf den gemerkten Ausgangswert stellen. */
    static _zurueck(inst, teil, feld, ohneEigenen) {
        if (!ohneEigenen) return;
        for (const m of Genesis9teilmaterial.materialien(inst)) {
            const def = Genesis9teilmaterial._passt(m, teil, feld);
            if (!def || !Genesis9teilmaterial._kann(m, feld)) continue;
            const wert = Genesis9teilmaterial._soll(m, feld, def, undefined);
            if (typeof wert === 'number') Genesis9teilmaterial._setzen(m, feld, wert);
        }
    }

    /**
     * Die Bedienzeilen eines Teils: `{feld, titel, hilfe, min, max, schritt, wert, standard, eigen, verfuegbar}`.
     * `verfuegbar` = mindestens ein Material des Teils kennt die Eigenschaft (ein Standard-Material hat keinen Glanz).
     */
    static felder(inst, teil) {
        const aus = [];
        const alle = Genesis9teilmaterial.materialien(inst);
        for (const [feld, def] of Object.entries(Genesis9teilmaterial.TEILE[teil].felder)) {
            const treffer = alle.filter(m => Genesis9teilmaterial._passt(m, teil, feld) && Genesis9teilmaterial._kann(m, feld));
            const erstes = treffer[0];
            // Ein Faktor-Feld zeigt 1 als Standard; sonst der Standard des Felds oder der Ausgangswert des ersten Materials.
            const standard = def.relativ ? 1 : (erstes ? Genesis9teilmaterial._standard(erstes, feld, def) : undefined);
            const eigen = inst.teilmaterial?.[teil]?.[feld];
            const gelesen = erstes ? Genesis9teilmaterial._lesen(erstes, feld) : 0;
            const wert = typeof eigen === 'number' ? eigen : (typeof standard === 'number' ? standard : gelesen);
            aus.push({ feld, ...Genesis9teilmaterial.FELDER[feld], wert, standard, eigen: typeof eigen === 'number',
                       relativ: !!def.relativ, verfuegbar: treffer.length > 0 });
        }
        return aus;
    }
}
