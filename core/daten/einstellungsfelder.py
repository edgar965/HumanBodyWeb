# -*- coding: utf-8 -*-
"""Einstellungsfelder — das Register aller erklärten Einstellungen.

Die eine Quelle für Titel, Erklärung und Grenzen; das Model holt seinen
`help_text` hier, die Vorlagen ihre Zeile. Begründung und Vorgeschichte
stehen in `einstellungsfeld.py`.

WAS SICH DABEI GEÄNDERT HAT (30.08.2026), damit es niemand für einen
Fehler hält:

- `mp_min_detection_confidence` und `mp_min_tracking_confidence` heissen
  jetzt auf BEIDEN Seiten gleich. Vorher stand auf der 2D-Seite
  „Detection Confidence" mit der Erklärung „Mindest-Konfidenz damit ein
  Pose-Ergebnis als erkannt gilt", auf der 3D-Seite „MediaPipe Detection
  Confidence" mit „Mindest-Konfidenz für die Pose-Erkennung" — dasselbe
  Feld, dieselbe Datenbankspalte.
- `progress_update_interval` erklärt sich auf Deutsch wie alle anderen.
- Die drei Rig-Felder sagen, welche Seite sie meinen. Sie standen mit
  wortgleicher Beschriftung untereinander; erkennbar waren sie nur an der
  Gruppenüberschrift darüber.
"""

from .einstellungsfeld import Einstellungsfeld as F


class Einstellungsfelder:
    """Nachschlagewerk: Feldname → `Einstellungsfeld`."""

    #: Feldname wie in `AppSettings` — die Vorlagen greifen mit diesem Namen zu.
    REGISTER = {
        # ----------------------------------------------------- Modelle/Prozess
        'progress_update_interval': F(
            'Fortschritt',
            'Nach wie vielen Bildern der Balken weiterrückt. '
            'Kleinere Werte melden häufiger und kosten etwas Rechenzeit',
            min=1,
            max=10000,
            schritt=1,
        ),
        'show_rig_config': F(
            '', 'Rig auf der Konfigurationsseite von Anfang an einblenden', zusatz='Rig beim Start anzeigen'
        ),
        'show_rig_animations': F(
            '', 'Rig auf der Animationsseite von Anfang an einblenden', zusatz='Rig beim Start anzeigen'
        ),
        'show_rig_scene': F(
            '', 'Rig auf der Szenenseite von Anfang an einblenden', zusatz='Rig beim Start anzeigen'
        ),
        'smpl_default_wireframe': F(
            'Wireframe', 'Body als Drahtgitter anzeigen', zusatz='Wireframe aktivieren'
        ),
        # ------------------------------------------ Standard-Modelle (21.09.2026)
        # Sieben Seiten, ein Baustein: `{% modell %}` mit dem Figurwahl-Dialog
        # (Edgar: „bei Modellauswahl standard bitte den neuen Modellauswahl-
        # dialog von /settings/scene/. Korrigiere das auch bei den anderen").
        'default_model_scene': F(
            'Standard-Modell',
            'Modell, das beim Öffnen der Szene-Seite geladen wird — jede Figurart '
            '(HumanBody, SMPL-X, MakeHuman, UMA, UMA Python, Genesis 9)',
        ),
        'default_model_config': F(
            'Konfiguration', 'HumanBody-Modell, das beim Öffnen der Konfigurationsseite geladen wird'
        ),
        'default_model_animations': F(
            'Animationen', 'HumanBody-Modell, das beim Öffnen der Animationen-Seite geladen wird'
        ),
        'default_model_result': F(
            'Standard-Modell', 'HumanBody-Modell, das beim Öffnen der Ergebnisseite geladen wird'
        ),
        'theatre_default_model': F(
            'Standard-Modell', 'HumanBody-Modell, das beim Laden der Theatre-Seite angezeigt wird'
        ),
        'effekte_default_model': F(
            'Standard-Modell',
            'HumanBody-Modell (Pipeline „HumanBody-Figur"), das die Effekte-Seite beim Laden '
            'vorwählt. Ein Modell, das es nicht mehr gibt, bleibt unbesetzt',
        ),
        'smpl_default_humanbody_preset': F(
            'HumanBody-Modell', 'HumanBody-Modell neben dem SMPL-Körper auf der SMPL-Seite'
        ),
        # ------------------------------------------ Standard-Animationen
        # Fuenfmal dasselbe Feld fuer fuenf Seiten. Vier davon hatten gar
        # keinen Titel und liefen unter der Vorgabe „Default Animation" —
        # englisch, mitten unter deutschen Zeilen.
        'default_anim_config': F(
            'Standard-Animation', 'Welche Animation die Konfigurationsseite von sich aus lädt'
        ),
        'default_anim_animations': F(
            'Standard-Animation', 'Welche Animation die Animationsseite von sich aus lädt'
        ),
        'default_anim_scene': F('Standard-Animation', 'Welche Animation die Szenenseite von sich aus lädt'),
        'default_anim_result': F(
            'Standard-Animation', 'Welche Animation die Ergebnisseite von sich aus lädt'
        ),
        'theatre_default_animation': F(
            'Standard-Animation', 'Welche Animation beim Laden der Theatre-Seite abgespielt wird'
        ),
        # ------------------------------------------------- Effekte (12.09.2026)
        # Edgar: „erstelle eine Seite Einstellungen - Effekte wo man das
        # Standard Modell auswählen kann … standard: Female2 sowie andere
        # settings". Die Zahlen sind die Startwerte der Regler auf der
        # Effekte-Seite; die Grenzen sind die der `Figurparameter`-Felder.
        'effekte_default_animation': F(
            'Standard-Animation',
            'Welche Animation die Effekte-Seite beim Laden vorwählt; ohne '
            'Angabe die neueste passende aus „Process Videos"',
        ),
        'effekte_video_fps': F(
            'Bildrate',
            'Bilder je Sekunde des Videos; bei 60-fps-BVHs gibt 30 den Schritt 1, 24 gäbe Zeitlupe',
            min=10,
            max=60,
            schritt=1,
        ),
        'effekte_video_width': F(
            'Breite (px)',
            'Videobreite — Vorgabe des Reglers auf der Effekte-Seite',
            min=320,
            max=3840,
            schritt=1,
        ),
        'effekte_video_height': F(
            'Höhe (px)', 'Videohöhe — Vorgabe des Reglers auf der Effekte-Seite', min=240, max=2160, schritt=1
        ),
        'effekte_wind': F(
            'Wind (m/s)',
            'Windstärke der Stoffdynamik (HumanBody-Figur); 0 = kein Wind',
            min=0,
            max=30,
            schritt=0.1,
        ),
        # ------------------------------------------ Netzqualitaet (17.09.2026)
        'unterteilung_browser': F(
            'Unterteilung im Browser',
            'Catmull-Clark-Stufen der HumanBody-Figur auf Szene, Modell- und '
            'Ergebnisseite (je Stufe viermal so viele Flächen). MB-Lab zeigt '
            '2; 1 ist schneller, 3 sehr schwer',
            min=1,
            max=3,
            schritt=1,
        ),
        'unterteilung_film': F(
            'Unterteilung im Film',
            'Catmull-Clark-Stufen beim Rendern des Figurvideos (pyrender). MB-Lab rendert 3',
            min=1,
            max=3,
            schritt=1,
        ),
        'haut_verschiebung': F(
            '',
            'Hautverschiebung wie MB-Labs Displace-Modifier: Poren, '
            'Falten (Alter), Muskeln (Tonus), Fett (Masse) aus der '
            'Displacement-Textur, ±5 mm entlang der Normale',
            zusatz='Hautverschiebung (Displacement) anwenden',
        ),
        # --------------------------------------------- MediaPipe (2D UND 3D)
        'mp_min_detection_confidence': F(
            'MediaPipe Detection Confidence',
            'Mindest-Konfidenz, damit eine Pose als erkannt gilt',
            min='0.0',
            max='1.0',
            schritt='0.05',
        ),
        'mp_min_tracking_confidence': F(
            'MediaPipe Tracking Confidence',
            'Mindest-Konfidenz für das Pose-Tracking zwischen Bildern. Niedrig = seltener neu erkennen',
            min='0.0',
            max='1.0',
            schritt='0.05',
        ),
        # ------------------------------------------------------- MocapNET v4
        'v4_hcd_iterations': F(
            'HCD Iterations',
            'IK-Gradient-Descent-Iterationen pro Bild. Mehr = genauer, aber langsamer',
            min=1,
            max=100,
            schritt=1,
        ),
        'v4_hcd_epochs': F(
            'HCD Epochs',
            'IK-Epochen pro Bild. Mehr Epochen verbessern die Pose-Qualität',
            min=1,
            max=200,
            schritt=1,
        ),
        'v4_hcd_learning_rate': F(
            'HCD Learning Rate',
            'Lernrate für den IK-Gradient-Descent-Solver',
            min='0.0001',
            max='0.1',
            schritt='0.0001',
        ),
        'v4_smoothing_cutoff': F(
            'Smoothing Cutoff (Hz)',
            'Butterworth-Tiefpass-Grenzfrequenz. Niedrigere Werte = glattere Animation',
            min='0.5',
            max='15.0',
            schritt='0.5',
        ),
        'v4_smoothing_sampling': F(
            'Smoothing Sampling (Hz)',
            'Abtastfrequenz für den Butterworth-Filter. Sollte zur Bildrate des Videos passen',
            min='10.0',
            max='120.0',
            schritt='1.0',
        ),
        # -------------------------------------------------------------- GVHMR
        'gvhmr_static_cam': F(
            'Static Camera',
            'Statische Kamera annehmen (kein DPVO). Empfohlen für eine feste Kameraperspektive',
        ),
        'gvhmr_focal_length_mm': F(
            'Focal Length (mm)',
            'Brennweite der Kamera in mm. 0 = automatisch schätzen (empfohlen)',
            min=0,
            max=200,
            schritt='0.5',
        ),
        'gvhmr_smooth_sigma': F(
            'Temporal Smoothing',
            'Gaußsche Glättung der Gelenkwinkel im BVH (0 = aus, 2 = Standard, '
            '4 und mehr = stark). Vorgabe für die Karte auf der Uploadseite; '
            'gilt auch für den Körper-Durchlauf des Hybrid-Laufs',
            min=0,
            max=10,
            schritt='0.5',
        ),
        'gvhmr_joint_limits': F(
            'Joint Limits',
            'Anatomische Grenzen für Knie, Ellbogen und Hüfte im BVH anwenden. '
            'Vorgabe für die Karte auf der Uploadseite',
        ),
        'gvhmr_use_dpvo': F(
            'DPVO',
            'Kamerabahn mit DPVO statt SimpleVO schätzen (genauer, langsamer, '
            'mehr VRAM). Wirkt nur ohne statische Kamera. Vorgabe für die Karte',
        ),
        'gvhmr_verbose': F(
            'Verbose',
            'Debug-Videos der Vorstufen ausgeben (Personenkästen, ViTPose-'
            'Skelett) — liest das Video dafür komplett in den Speicher. '
            'Vorgabe für die Karte',
        ),
        'gvhmr_render': F(
            'Demo-Videos rendern',
            'Kamera-, Welt- und Vergleichsvideo erzeugen (pytorch3d). Bei '
            '7.538 Bildern die Hälfte der Laufzeit; ohne sie bleibt das BVH. '
            'Die Videos kopiert „3D Video Output" in den Ausgabeordner',
        ),
        # --------------------------------------------------------------- WHAM
        'wham_estimate_local_only': F(
            'Estimate Local Only', 'Nur die lokale Körperbewegung schätzen, keine globale Bahn'
        ),
        'wham_run_smplify': F('Run SMPLify', 'SMPLify-Verfeinerung ausführen. Langsamer, aber genauer'),
        # ---------------------------------------------------------- PromptHMR
        'prompthmr_static_camera': F(
            'Static Camera', 'Statische Kamera annehmen. Empfohlen für die meisten Videos'
        ),
        # ----------------------------------------------------------- GEM-SMPL
        'gem_static_cam': F(
            'Static Camera',
            'Statische Kamera annehmen. Das Video-Demo von GEM verfolgt die '
            'Kamera ohnehin nicht; der Schalter setzt nur die Kamera-Maske '
            'des Modells',
        ),
        'gem_smooth_sigma': F(
            'Temporal Smoothing',
            'Gaußsche Glättung der Gelenkwinkel im BVH (0 = aus, 2 = Standard, '
            '4 und mehr = stark). Vorgabe für die Karte auf der Uploadseite',
            min=0,
            max=10,
            schritt='0.5',
        ),
        'gem_joint_limits': F(
            'Joint Limits',
            'Anatomische Grenzen für Knie, Ellbogen und Hüfte im BVH anwenden. '
            'Vorgabe für die Karte auf der Uploadseite',
        ),
        'gem_render': F(
            'Demo-Videos rendern',
            'Kamera-, Welt- und Vergleichsvideo mit Open3D erzeugen (dauert '
            'länger, liest das Video komplett in den Speicher). Vorgabe für '
            'die Karte',
        ),
        # -------------------------------------------------------------- DuoMo
        'duomo_static_cam': F(
            'Static Camera',
            'Statische Kamera annehmen. DuoMo liefert ohne Kamerabahn ohnehin '
            'eine feste Kamera; der Schalter ist die Vorgabe der Karte',
        ),
        'duomo_smooth_sigma': F(
            'Temporal Smoothing',
            'Gaußsche Glättung der Gelenkwinkel im BVH (0 = aus, 2 = Standard, '
            '4 und mehr = stark). Vorgabe für die Karte auf der Uploadseite',
            min=0,
            max=10,
            schritt='0.5',
        ),
        'duomo_joint_limits': F(
            'Joint Limits',
            'Anatomische Grenzen für Knie, Ellbogen und Hüfte im BVH anwenden. '
            'Vorgabe für die Karte auf der Uploadseite',
        ),
        # -------------------------------------------------------------- GEM-X
        'gemx_static_cam': F(
            'Static Camera',
            'Statische Kamera annehmen — wie bei GEM-SMPL nur die Kamera-Maske '
            'des Modells. Vorgabe für die Karte auf der Uploadseite',
        ),
        'gemx_smooth_sigma': F(
            'Temporal Smoothing',
            'Gaußsche Glättung der Gelenkwinkel im BVH (0 = aus, 4 = Standard seit '
            '12.09.2026: gemessen halbiert sie das Körperzittern von GEM-X bei '
            'gleicher Deckung; 2 = weniger). Gelenkgrenzen gibt es für GEM-X nicht: SOMA '
            'hat 77 Gelenke, die Grenzen sind SMPL-Indizes',
            min=0,
            max=10,
            schritt='0.5',
        ),
    }

    @classmethod
    def feld(cls, kennung):
        """Das `Einstellungsfeld` zu einem Feldnamen.

        WIRFT, wenn es den Namen nicht gibt. Ein stiller Rückfall auf einen
        leeren Datensatz gäbe eine Einstellungszeile ohne Titel und ohne
        Grenzen — sie sähe fertig aus und liesse jeden Wert durch.
        """
        try:
            return cls.REGISTER[kennung]
        except KeyError:
            raise KeyError(
                'Kein Einstellungsfeld "%s". Bekannt sind: %s' % (kennung, ', '.join(sorted(cls.REGISTER)))
            )

    @classmethod
    def hilfetext(cls, kennung):
        """Der `help_text` fürs Model — dieselbe Erklärung wie auf der Seite."""
        return cls.feld(kennung).hilfetext
