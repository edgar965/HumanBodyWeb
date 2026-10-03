# -*- coding: utf-8 -*-
"""Werkzeuggarmentcode — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: GarmentCode-Katalog als Genesis-Stücke.

Reine Daten (Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`.
Jede Zeile ist gegen den Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum.
"""

__all__ = ['Werkzeuggarmentcode']


class Werkzeuggarmentcode:
    G = 'Genesis9/'
    A = 'HumanBodyWeb/core/api/'
    C = 'Assets/GarmentCode/'

    KENNUNG = 'garmentcode'
    TITEL = 'GarmentCode-Katalog: Schnitt bauen, drapieren, als Genesis-Stück ablegen'
    EINLEITUNG = (
        'GarmentCode konstruiert Kleidung aus einem Schnitt (Baukasten), statt ein fertiges Netz anzupassen. Der Katalog '
        '(Assets/GarmentCode/katalog.py) kennt acht Stücke mit Formen: oberteil, hose, shorts, rock, kleid, anzug, '
        'unterwaesche, schuh. Auf Genesis 9 wird ein Schnitt auf den Maßen der Figur gebaut, auf der Figur drapiert und als '
        'gewöhnliches Garderobenstück „GC <Titel>“ (Kennung gc_…) abgelegt; danach zieht man es wie jedes Daz-Stück an '
        '(Gruppe „Kleider anziehen und einstellen“). Reihenfolge: 1. Vorlage und Form wählen (Katalog.liste, '
        'Formpresets.fuer), 2. bauen (kleid_schnitt im Rezept, G9gceigenes.bauen in Python oder der Reiter GarmentCode), '
        '3. anziehen mit der Kennung aus der Bilanz (bilanz["stueck"]). Ein Bau kostet rund 25–60 s auf der GPU und '
        'schreibt in die eigene Bibliothek: nicht nebenbei neben Edgars Arbeit starten.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Neues Stück aus einem GarmentCode-Schnitt (Rezept)',
         'Baut ein NEUES Stück aus dem Katalog, drapiert es auf der Grundfigur, legt es als Genesis-Stück ab und zieht es an.',
         'rezept',
         "m.kleid_schnitt('oberteil', titel='Test Shirt', form='form_t_shirt_anliegend', regler={'sleeve.length': 0.5}, "
         "farbe='#336699', anteil=1.0)",
         [(G + 'modellform.py', 'ModellFormMixin'), (C + 'formpresets.py', 'Formpresets'), (G + 'gceigenes.py', 'G9gceigenes'),
          (G + 'gcstuecke.py', 'G9gcstuecke')],
         'vorlage ∈ oberteil|hose|shorts|rock|kleid|anzug|unterwaesche|schuh; form = Schlüssel eines Formpresets der Vorlage '
         '(Formpresets.fuer(vorlage)), unbekannt wirft ValueError „form … gibt es für … nicht“; regler = {pfad: wert} wie im '
         'Reiter (etwa sleeve.length, pants.length, bau.anliegen_mm); farbe #rrggbb; anteil wie kleid_anteil. Dauer ≈ 25 s '
         '(Docstring), die Probe auf der Genesis-Figur 25–60 s (Docstring Gcgenesisapi). Ohne titel heißt das Stück '
         '„<vorlage> <form>“; ein zweiter Bau mit gleichem Titel bekommt „…_2“, außer das erste kam aus dem Reiter. '
         'kleid_schnitt zieht das Stück selbst an (kleid_anteil mit bilanz["stueck"]); die Kennung steht danach als '
         'sorte.<kennung> in m.kleidung. Quelle: Genesis9/modellform.py, gceigenes.py (25.09.2026).'),

        ('Katalog und Formen lesen',
         'Liefert die Katalogstücke, ihre Formen (Kästchen) und die alten Namen (Aliase).',
         'python',
         "import sys\n"
         "sys.path[:0] = ['A:/3DTools', 'A:/3DTools/Assets']\n"
         "from GarmentCode.katalog import Katalog\n"
         "from GarmentCode.formpresets import Formpresets\n"
         "Katalog.liste()               # [{'name': 'oberteil', 'titel': 'Oberteil'}, … acht Stücke]\n"
         "Formpresets.fuer('oberteil')  # [{'schluessel': 'form_t_shirt', 'titel', 'werte', 'zurueck', 'gehakt', 'kern'}, …]\n"
         "Katalog.aliase()              # {'t-shirt': ('oberteil', 'form_t_shirt'), …}",
         [(C + 'katalog.py', 'Katalog'), (C + 'formpresets.py', 'Formpresets')],
         'Gelesen und mit Python 3.14 ausgeführt am 03.10.2026 (reines Lesen): Formen — oberteil: form_t_shirt, '
         'form_t_shirt_anliegend, form_hemd, form_traegertop; kleid: form_kleid, form_sommerkleid, form_abendkleid; anzug: '
         'form_jumpsuit; unterwaesche: form_bh, form_hoeschen, form_body; rock: form_bleistiftrock, form_kreisrock, '
         'form_stufenrock, form_godetrock, form_faltenrock, form_asymmetrischer_rock; schuh: form_ballerina, form_slipper, '
         'form_pumps, form_plateauschuh, form_stiefelette, form_stiefel, form_socke; hose und shorts haben keine Form. 24 '
         'Aliase (t-shirt, bleistiftrock, pumps …) leben in gespeicherten Szenen, vorbilder.json und der Schnittdeutung '
         'weiter. Die Vorbilder (aus der MakeHuman-Bibliothek gemessene Voreinstellungen) liegen in '
         'Assets/GarmentCode/vorbilder.json. Seit 11.09.2026 ist ein Rock EIN Katalogstück mit Formen, kein Eintrag je Art '
         '(garmentcode-katalog.md).'),

        ('Schnitt als Genesis-Stück speichern (Server)',
         'Baut Schnitt und Drapierung auf der Genesis-Figur des Reiters (sonst der Grundfigur), schreibt das Stück in die '
         'eigene Bibliothek und lässt die Garderobe neu lesen.',
         'api',
         'POST /api/garmentcode/genesis/speichern/\n'
         'Formularfelder: vorlage, regler (JSON), bau (JSON, z. B. {"anliegen_mm": 2}), titel, material (JSON: farbe, rauheit, '
         'metall, gewebe), quelle, regler_figur (JSON, die Daz-Regler der Figur)\n'
         '→ {stueck, kennung, name, stoff, sekunden, haut_median_mm, figurbau, angepasst}',
         [(A + 'gcgenesis.py', 'Gcgenesisapi'), (C + 'katalog.py', 'Katalog'), (G + 'gceigenes.py', 'G9gceigenes'),
          (G + 'gcstuecke.py', 'G9gcstuecke')],
         '400 bei unbekannter Vorlage (Katalog.kennt) oder wenn Schnitt/Drapierung scheitern (EntwurfFehler, DrapierFehler), '
         '500 bei unerwartetem Fehler. Dauer wie „Bauen 2D + 3D“, rund 25–60 s (Docstring). Metall und Gewebe hat der '
         'Schreiber nicht: der Browser legt sie auf (Stoffwerte) und sie gehen mit der Herkunft zurück. Die Antwort nennt '
         'stueck = Kennung in der Garderobe. Frontend: HumanBodyWeb/static/viewer/charakter/garmentcode_alsgenesis.js '
         '(Knopf #gc-als-genesis). Geprüft im Chrome nur: Knopf da, Modul geladen, Herkunft kommt; der ganze Ablauf mit '
         'Figur und 30-s-Bau ist nicht im Browser gelaufen (genesis9-garderobe.md, 25.09.2026).'),

        ('Herkunft eines GarmentCode-Stücks lesen',
         'Liefert Vorlage, Quelle, Werte, Farbe und Stoff eines gebackenen gc_-Stücks — damit der Reiter es wieder öffnen kann.',
         'api',
         'GET /api/garmentcode/genesis/<stueck>/   → {vorlage, quelle, werte, farbe, stoff, name, …}',
         [(A + 'gcgenesis.py', 'Gcgenesisapi'), (G + 'gceigenes.py', 'G9gceigenes')],
         'stueck muss ^gc_[a-z0-9_]{1,120}$ passen (sonst 400), unbekannt → 404 „Herkunft unbekannt“. Frontend: '
         'static/viewer/charakter/genesis9/gcherkunft.js öffnet am gewählten gc_-Stück den Reiter, klickt ihn (Reiterwechsel '
         'aus Code muss KLICKEN) und stellt Vorlage, Vorbild und die Werte DES STÜCKS. Quelle: genesis9-garderobe.md '
         '(25.09.2026, „Weg 2“).'),

        ('Schnitt und Stück in Python bauen (ohne HTTP)',
         'Baut ein Stück aus Vorlage und Reglerwerten direkt: Schnitt, Drapierung, Schreiben.',
         'python',
         "from Genesis9.gceigenes import G9gceigenes\n"
         "bilanz = G9gceigenes.bauen('rock', {'meta.bottom': 'SkirtCircle'}, 'Test Kreisrock', material={'farbe': '#336699'}, "
         "quelle='probe')\n"
         "bilanz['stueck']      # Kennung in der Garderobe; bilanz['haut_median_mm'], bilanz['sekunden']",
         [(G + 'gceigenes.py', 'G9gceigenes'), (G + 'gcstuecke.py', 'G9gcstuecke'), (G + 'gcdrapierung.py', 'G9gcdrapierung'),
          (G + 'gcstueckmaterial.py', 'G9gcstueckmaterial'), (G + 'eigenstueck.py', 'G9eigenstueck')],
         'Läuft im Django-Prozess oder einem Skript mit TOOLS_ROOT, Assets und HumanBody im Pfad; GarmentCodes Drapierung '
         'braucht python10_Garment und eine GPU (CLAUDE.md, Umgebungen). Der Auftrag trägt vorlage, werte, titel, material '
         '(farbe, roughness), quelle, regler_figur; auf einer Figur gebaut (regler_figur nicht leer) wird die Ruhelage '
         'zurückgerechnet (G9gcfigurbau). Nicht ausprobiert (nur gelesen); die Werte im Beispiel sind ein Muster, die gültigen '
         'Pfade liefert Formpresets/Regler. Nach dem Bau ruft G9gceigenes G9mbstuecke.vergessen().'),

        ('Alle Katalogformen und Vorbilder als Genesis-Stücke (Stapel)',
         'Baut für jede Form (ohne Form: das Stück selbst) und jedes Vorbild je ein Genesis-9-Stück auf den Maßen der '
         'Grundfigur.',
         'cli',
         'cd A:/3DTools/HumanBodyWeb && ../python14/Scripts/python.exe manage.py gcstuecke --liste\n'
         'manage.py gcstuecke [--nur <teilwort>] [--neu]',
         [(G + 'gcstuecke.py', 'G9gcstuecke'), (G + 'gcdrapierung.py', 'G9gcdrapierung'), (G + 'eigenstueck.py', 'G9eigenstueck'),
          (G + 'gcstueckmaterial.py', 'G9gcstueckmaterial'), (G + 'mbstuecke.py', 'G9mbstuecke')],
         '--liste zeigt nur, was gebaut würde (vorlage, kennung, quelle, „(aktuell)“) und rechnet nichts; ohne Argumente '
         'baut er alles, was fehlt oder veraltet ist, --nur filtert nach Teilwort in Kennung oder Vorlage, --neu baut auch '
         'Aktuelles neu. Stand 25.09.2026: 171 von 171 Aufträgen gebaut, ~25 s je Stück; der Command nennt 20–45 s je '
         'Stück GPU-Drapierung und „der ganze Stapel dauert Stunden und gehört nicht neben Edgars Arbeit“ — nur auf '
         'Ansage. Ablage 3DObjects/Genesis9/gc_stuecke/<Kennung>/ mit Fingerabdruck (Vorlage, Werte, Material, FASSUNG): ein '
         'zweiter Lauf baut nur Fehlendes. GarmentCodes Nacharbeit nur für Hose, Shorts, Anzug, Schuh '
         '(G9gcdrapierung.NACHARBEIT); Strümpfe mit Anlegen 2 mm (STRUMPFWERTE, Median 34 → 6 mm). Ungenähte breite Stiefel '
         '(StitchingError im Netzbau) baut G9gcdrapierung mit anderer Auflösung und schrittweise schmalerer Sohle; was '
         'geändert wurde, steht als angepasst in der Bilanz. Danach die Garderobe neu lesen lassen '
         '(G9mbstuecke.vergessen, Gruppe „Garderobe“).'),

        ('Passform-Regler der GC-Stücke als Morphe backen',
         'Backt je Passform-Regler zwei Kanäle (minus/plus) als Daz-Morph an ein GC-Stück, damit sie mit Daz-Reglern '
         'stellbar sind.',
         'cli',
         'cd A:/3DTools/HumanBodyWeb && ../python14/Scripts/python.exe manage.py gcmorphe --liste\n'
         'manage.py gcmorphe [--nur <teilwort>] [--neu] [--teil i/n]',
         [(G + 'gcmorphe.py', 'G9gcmorphe'), (G + 'gcstuecke.py', 'G9gcstuecke'), (G + 'gcmorphuebertrag.py', 'G9gcmorphuebertrag')],
         'Je Regler zwei Drapierungen (Minimum, Maximum), ~30 s je Fassung auf der GPU (Docstring des Befehls; rund 35 s '
         'in genesis9-garderobe.md, 25.09.2026); 1.231 Regler über alle Stücke, bis zu 2.462 Fassungen. --teil i/n teilt '
         'den Stapel auf parallele Läufe. Gegenprobe: ein Stück auf sich selbst 0,0 mm; T-Shirt Länge/Ärmel trifft p99 '
         '5,7–6,8 mm. Verworfen werden Regler mit < 5 mm Weg, Deckung p99 > 25 mm oder > 15 % gekippt. Ablage '
         'gc_stuecke/<Kennung>/morphe/, Morphe als Morphs/*.dsf neben dem Netz, Gruppe /GarmentCode/<Teil>. Nur auf '
         'Ansage, belegt die GPU für Stunden.'),

        ('GarmentCode-Reiter in der Szene (Schnitt, Drapierung, Genesis-Figur)',
         'Die Oberfläche für Schnitt, 2D-Vorschau, 3D-Drapierung und Anziehen; auf Genesis 9 schickt sie statt Bauart und '
         'Morphs die Daz-Regler der Figur.',
         'api',
         'POST /api/garmentcode/erzeugen/     vorlage, figurart=genesis9, regler_figur (JSON), regler (JSON), meta (JSON) → Schnitt\n'
         'POST /api/garmentcode/drapieren/    spezifikation, vorlage, … → Drapierung (3D-Netz)\n'
         'GET  /api/garmentcode/zustand/      → {Vorlagen, drapierbereit}',
         [(A + 'garmentcode.py', 'Garmentcode'), (A + 'garmentanfrage.py', 'Garmentanfrage'),
          (C + 'dienst.py', 'GarmentcodeDienst'), (C + 'genesis9drapierung.py', 'Genesis9drapierung')],
         'Szene /Charakter/ → Reiter GarmentCode (Frontend HumanBodyWeb/static/viewer/charakter/garmentcode*.js, über 30 '
         'Module). Felder lesen Garmentanfrage; figurart gilt nur genesis9 (FIGURARTEN). Gemessen 08.09.2026 '
         '(garmentcode.md): Schnitt 225 ms statt 866, Drapierung 24,5 s (run_sim 15,7 s, 439 Bilder × 10), Vorschau am '
         'Regler 8,4 ms je Zug über WebSocket ws/stoff/. Dev-Server-Neustart während einer Drapierung → „Failed to '
         'fetch“, nichts im Fehlerlog (garmentcode.md). Ein Bau ohne Morphs überschreibt den Ergebnisordner. Die '
         'Genesis-Figur des Reiters baut G9gcfigurbau (Ruhelage zurückrechnen). Der Rest der Reiter-Schnittstelle '
         '(vorbilder, regler, simulationsregler, gemeinsam, schnittnetz, antwort, abbrechen) steht in urls.py.'),

        ('Regel: GarmentCode-Grundsätze',
         'Hält fest, was für jeden GarmentCode-Bau gilt, damit Messungen und Ergebnisse stimmen.',
         'regel',
         'Der Stoff fällt auf den Figurkörper, nie auf mean_all; Schubrichtung = KÖRPERnormale; Durchstich je STOFFpunkt '
         'messen; Hautabstand (hautabstand_mm) belegt „liegt an“.',
         [(G + 'gcdrapierung.py', 'G9gcdrapierung'), (C + 'dienst.py', 'GarmentcodeDienst')],
         'Aus garmentcode.md (12.09.2026): Drapierung(koerper=None) heißt GarmentCodes Durchschnittskörper — Körpernetz '
         'figur_<12 Hex>.obj in koerper/<geschlecht>/ nehmen; Figur 13,2 mm Hautabstand gegen mean_all 27,4, über 40 mm '
         'heißt „sitzt nicht“; Wickelrichtung prüfen (signiertes Volumen), die Stoffnormale hängt an der Dreiecksorientierung '
         '(aus 20 mm Einsinken wurden 35); Durchstich: vier Messerfassungen waren falsch (Punkt-zu-Punkt am Saum 35 %, '
         'Stoffnormale 96–99 %, körperseitig am Fuß 19,6 %), Gegenprobe: 200 um 15 mm eingedrückte Punkte müssen gemeldet '
         'werden. Zwei Bauten mit verschiedenen Reglern taugen nicht als Vorher/Nachher. Auf Genesis: keine Portierung für '
         'BH und String (BH = ärmelloses Kurzoberteil, String = Boxershorts — so baut GarmentCode sie selbst, '
         'genesis9-garderobe.md 25.09.2026); Dreiecksnetze der GC-Stücke werden nicht unterteilt (G9dsonschreiber.netzart).'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('ModellFormMixin', 'ruft', 'Formpresets', 'Formpresets.fuer(vorlage): prüft form (kleid_schnitt)'),
        ('ModellFormMixin', 'ruft', 'G9gceigenes', 'G9gceigenes.bauen(vorlage, werte, titel, material, quelle): Schnitt → Stück'),
        ('Gcgenesisapi', 'ruft', 'Katalog', 'Katalog.kennt(vorlage): 400 bei unbekannter Vorlage'),
        ('Gcgenesisapi', 'ruft', 'G9gceigenes', 'G9gceigenes.bauen() für POST speichern; herkunft(stueck) für GET'),
        ('G9gceigenes', 'ruft', 'G9gcstuecke', 'G9gcstuecke.bauen(auftrag) und _ablegen(): die Rechnung; auftrag(): eindeutige Kennung'),
        ('G9gcstuecke', 'ruft', 'G9gcdrapierung', 'G9gcdrapierung.lauf(auftrag), punkte(), figur(): Schnitt und Drapierung'),
        ('G9gcstuecke', 'ruft', 'G9gcstueckmaterial', 'G9gcstueckmaterial.material(), vorschau(): Farbe und Vorschaubild'),
        ('G9gcstuecke', 'ruft', 'G9eigenstueck', 'G9eigenstueck.schreiben(): heben, Gewichte, DSON schreiben (Hersteller GC)'),
        ('G9gcstuecke', 'ruft', 'G9mbstuecke', 'G9mbstuecke.vergessen(): alle() lässt die Garderobe neu lesen'),
        ('G9gcdrapierung', 'ruft', 'GarmentcodeDienst', 'GarmentcodeDienst.erzeugen(): der Schnitt'),
        ('G9gcdrapierung', 'ruft', 'Genesis9drapierung', 'Genesis9drapierung.lauf(spez, figur, fein, …): Drapierung auf der Genesis-Figur'),
        ('G9gcmorphe', 'ruft', 'G9gcstuecke', 'G9gcstuecke.auftraege() und arbeitsordner(): welche Stücke, wohin'),
        ('G9gcmorphe', 'ruft', 'G9gcdrapierung', 'G9gcdrapierung.punkte(): Punkte der Drapierung je Fassung'),
        ('G9gcmorphe', 'ruft', 'G9gcmorphuebertrag', 'G9gcmorphuebertrag.netz(): legt die gebackenen Kanäle auf die Stückpunkte'),
        ('Garmentcode', 'ruft', 'Garmentanfrage', 'Garmentanfrage.lesen(request): die Felder von Schnitt und Drapierung'),
        ('Garmentcode', 'ruft', 'GarmentcodeDienst', 'GarmentcodeDienst.erzeugen(), drapieren(), zustand(): der Reiter-Weg'),
        ('GarmentcodeDienst', 'ruft', 'Genesis9drapierung', 'Genesis9drapierung.masse(regler_figur): Maße der Genesis-Figur'),
    ]
