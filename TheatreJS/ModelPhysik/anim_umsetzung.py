# -*- coding: utf-8 -*-
u"""Rigify-Drehungen -> Gelenkdrehungen, wie FastProjectiveSkinning sie erwartet.

DIE BEIDEN RIGS MEINEN VERSCHIEDENES MIT „LOKALER DREHUNG"
==========================================================

Rigify (und damit unser Retarget) gibt je Knochen eine lokale Drehung, die
die RUHE-ORIENTIERUNG DES KNOCHENS BEREITS ENTHAELT:

    Welt_i = Welt_eltern * lokal_i        Ruhelage: lokal_i = rest_local_quat

FPS kennt keine Knochenorientierung. Seine Gelenke sind nackte Punkte, und
seine Ruhelage ist die Einheitsdrehung (`Skeleton::transform`:
`joints_[i]->local_.linear() = quats[i].matrix()`, danach Vorwaertskinematik):

    Welt_i = Welt_eltern * q_i            Ruhelage: q_i = Einheit

Wer die Rigify-Drehung direkt hinschreibt, uebergibt FPS die Ruhelage des
Knochens als Bewegung — die Figur steht schon im ersten Bild verdreht. Was
FPS braucht, ist das DELTA gegen die eigene Ruhelage, ausgedrueckt im Raum
des Elternteils:

    Delta_i = Welt_pose_i * Welt_ruhe_i^-1
    q_i     = Delta_eltern^-1 * Delta_i

Dieselbe Ueberlegung stand am 07.09.2026 hinter `Gelenkskelett` („Der Motor
liefert lokale Drehungen relativ zur Ruhelage, und eine abgeleitete ist eine
andere als die eigene").

KONVENTIONEN, beide am Bestand abgelesen, nicht geraten:
  * `def_skeleton.json` fuehrt `local_quaternion` als **[w, x, y, z]**.
  * Die Retarget-Spuren (`Bewegungsspuren.tracks`) fuehren **[x, y, z, w]**.

Ohne Three.js und ohne FPS pruefbar: `gegenprobe()` rechnet die
Vorwaertskinematik beider Seiten und vergleicht die Gelenkpunkte.
"""
import numpy as np


class Animumsetzung:
    u"""Rechnet Bewegungsspuren in FPS-Gelenkdrehungen um."""

    #: Twist auf das Twist-Segment verlagern. Siehe `_twist_verlagern`.
    TWIST_VERLAGERN = True

    def __init__(self, knochen, gelenke, laengen=None, punkte=None):
        u"""`knochen`: {name: {'parent', 'local_position', 'local_quaternion'}}
        aus `def_skeleton.json`; `gelenke`: [(name, elternname)] in der
        Reihenfolge der `.skel`-Datei (Eltern vor Kindern); `laengen`:
        {name: Knochenlaenge in Metern} aus `rig_bones.json` (`tail - head`).

        Ohne `laengen` schaetzt die Gegenprobe die Laenge eines Blattes aus
        dem ersten Kind — am Kopf ist das ein Gesichtsknochen, und die Probe
        meldete 62 mm, die es gar nicht gab.
        """
        self.knochen = knochen
        self.laengen = laengen or {}
        self.gelenke = list(gelenke)
        self.namen = [n for n, _ in self.gelenke]
        self.eltern = dict(self.gelenke)
        self.ruhe_welt = self._ruhelagen()
        # Gelenkpunkte in FPS-Einheiten — nur die RICHTUNGEN werden gebraucht,
        # der Massstab kuerzt sich heraus.
        self.punkte = punkte or {}
        self.kinder = {}
        for name, elternteil in self.gelenke:
            self.kinder.setdefault(elternteil, []).append(name)
        self._twistbezug = None

    # ------------------------------------------------------------- Rechnung

    def _ruhelagen(self):
        u"""Welt-Ruhedrehung je Knochen des GANZEN Rigs (rekursiv)."""
        aus = {}

        def loesen(name):
            if name in aus:
                return aus[name]
            knochen = self.knochen.get(name)
            if knochen is None:
                return np.array([0.0, 0.0, 0.0, 1.0])
            eigen = self._wxyz(knochen['local_quaternion'])
            elternteil = knochen.get('parent')
            aus[name] = (eigen if not elternteil
                         else self.mul(loesen(elternteil), eigen))
            return aus[name]

        for name in self.knochen:
            loesen(name)
        return aus

    def bild(self, spuren, nummer, roh=False):
        u"""Die FPS-Drehungen eines Bildes: {gelenkname: [x, y, z, w]}.

        Ein Gelenk, dessen Name auf `_ende` endet, ist ein Endpunkt ohne
        eigenen Knochen — es dreht nie.

        `roh=True` ist die SABOTAGE fuer die Gegenprobe: Es schreibt die
        Rigify-Drehung unverändert, ohne das Delta gegen die Ruhelage. Genau
        der Fehler, den die Probe finden muss — ohne ihn waere „0,00 mm"
        nichts wert.
        """
        pose_welt = {}

        def welt(name):
            u"""Welt-Posedrehung eines Knochens, Kette hinauf."""
            if name in pose_welt:
                return pose_welt[name]
            knochen = self.knochen.get(name)
            if knochen is None:
                return np.array([0.0, 0.0, 0.0, 1.0])
            spur = spuren.get(name)
            if spur is not None:
                lokal = self.nach_blender(np.asarray(
                    spur[nummer * 4:nummer * 4 + 4], dtype=np.float64))
            else:
                lokal = self._wxyz(knochen['local_quaternion'])
            elternteil = knochen.get('parent')
            pose_welt[name] = (lokal if not elternteil
                               else self.mul(welt(elternteil), lokal))
            return pose_welt[name]

        delta = {}
        for name in self.namen:
            grund = name[:-5] if name.endswith('_ende') else name
            if roh:
                delta[name] = welt(grund)
                continue
            delta[name] = self.mul(welt(grund),
                                   self.konjugiert(self.ruhe_welt.get(
                                       grund, np.array([0.0, 0.0, 0.0, 1.0]))))

        aus = {}
        for name in self.namen:
            elternteil = self.eltern.get(name)
            if elternteil and elternteil in delta:
                aus[name] = self.mul(self.konjugiert(delta[elternteil]), delta[name])
            else:
                aus[name] = delta[name]
        if roh or not self.TWIST_VERLAGERN or not self.punkte:
            return aus
        return self._twist_verlagern(aus, spuren)

    # ------------------------------------------------------------ Twist

    def _knochenachse(self, name):
        u"""Richtung des Knochens: vom Gelenk zu seinem ersten Kind.

        `None` fuer ein Blatt — dort gibt es keine Achse, und ein Twist ist
        dann ohnehin bedeutungslos.
        """
        kinder = self.kinder.get(name)
        if not kinder or name not in self.punkte:
            return None
        for kind in kinder:
            if kind not in self.punkte:
                continue
            achse = self.punkte[kind] - self.punkte[name]
            laenge = float(np.linalg.norm(achse))
            if laenge > 1e-9:
                return achse / laenge
        return None

    @staticmethod
    def zerlegen(q, achse):
        u"""Swing-Twist-Zerlegung: `q = swing * twist`, Twist um `achse`.

        Der Twist ist die Projektion des Vektorteils auf die Achse. Ist der
        Rest nahe null (Drehung genau um die Achse), bleibt die Einheit
        stehen statt einer Division durch fast null.
        """
        achse = np.asarray(achse, dtype=np.float64)
        anteil = float(np.dot(q[:3], achse)) * achse
        twist = np.array([anteil[0], anteil[1], anteil[2], q[3]])
        norm = float(np.linalg.norm(twist))
        if norm < 1e-9:
            twist = np.array([0.0, 0.0, 0.0, 1.0])
        else:
            twist = twist / norm
        return Animumsetzung.mul(q, Animumsetzung.konjugiert(twist)), twist

    #: Rigify teilt Arme und Beine in einen Schwenk- und ein Twist-Segment
    #: (`DEF-upper_arm.L` und `DEF-upper_arm.L.001`).
    TWISTSEGMENT = '.001'

    def _twist_verlagern(self, drehungen, spuren):
        u"""Den Twist vom Knochen auf SEIN Twist-Segment schieben.

        WARUM (10.09.2026, gemessen): Der Retarget setzt 21 Spuren; die
        `.001`-Segmente haben keine eigene und stehen in Ruhe. Der ganze
        Twist bleibt damit auf dem Hauptknochen liegen:

            DEF-forearm.L      77,1  76,9  78,0   Spanne  1,2 Grad
            DEF-upper_arm.L   152,6 151,2 143,5   Spanne  9,0 Grad
            DEF-shin.L          0,0   0,2   0,7   Spanne  0,7 Grad

        IM BROWSER IST DAS RICHTIG SO — die Hautgewichte verteilen ihn ueber
        beide Segmente, und die Animationen laufen dort korrekt (Edgar,
        10.09.2026). FPS hat keine Hautgewichte: Es baut seine Muskel- und
        Fettschicht aus der Geometrie und dreht sie mit dem Knochen. Ein
        Twist von 153 Grad auf einem Segment verdreht die Haut um 153 Grad,
        und der Arm zerreisst.

        Verlagert wird deshalb dorthin, wofuer Rigify das Segment HAT:

            q_knochen  = swing
            q_segment  = twist * q_segment

        DIE KETTE BLEIBT EXAKT ERHALTEN, denn

            welt(segment) = welt(knochen) * q_segment
                          = (welt(eltern) * swing) * (twist * q_alt)
                          = welt(eltern) * (swing * twist) * q_alt
                          = welt(eltern) * q_knochen_alt * q_alt

        Deshalb muss die Positionsprobe weiter 0,00 mm melden — sie ist die
        Gegenprobe dieser Verlagerung.

        Ein frueherer Versuch, den Twist stattdessen gegen Bild 0 zu
        NORMIEREN, hat ihn zwar kleingerechnet (153 -> 30 Grad), aber die
        Positionen zerstoert (0,00 -> 867 mm): Ein Twist am Oberarm dreht
        den ganzen Unterarm mit, und wer ihn wegnimmt, ohne ihn weiter unten
        wieder einzusetzen, verschiebt jedes Kind.
        """
        aus = dict(drehungen)
        for name in self.namen:
            segment = name + self.TWISTSEGMENT
            if segment not in aus or self.eltern.get(segment) != name:
                continue
            # EIN TWIST-SEGMENT HAT KEINE EIGENE SPUR. Das ist das Kriterium,
            # nicht der Name: `DEF-spine.001` heisst genauso, ist aber der
            # naechste WIRBEL (Lumbar) und wird vom Retarget gesetzt. Weil
            # `DEF-spine` die Wurzel ist, drehte ein Twist dort die ganze
            # Figur — gemessen 28,32 mm am Fuss, wandernd ueber beide Beine,
            # waehrend die Arme sauber blieben.
            if spuren.get(segment) is not None:
                continue
            # DIE ACHSE ZEIGT AUF DAS SEGMENT, nicht auf irgendein Kind.
            # `_knochenachse` nimmt das erste Kind der Liste; bei einem
            # Knochen mit mehreren Kindern ist das nicht zwingend das
            # Twist-Segment, und dann dreht der Twist quer zur Kette. Gemessen
            # kostete das 28,32 mm in der Positionsprobe — klein genug, um es
            # zu uebersehen, und gross genug, um falsch zu sein.
            versatz = self.punkte[segment] - self.punkte[name]
            laenge = float(np.linalg.norm(versatz))
            if laenge < 1e-9:
                continue
            swing, twist = self.zerlegen(
                np.asarray(aus[name], dtype=np.float64), versatz / laenge)
            # GLEICHMAESSIG AUF BEIDE SEGMENTE, nicht ganz auf eines. Genau
            # dafuer hat Rigify das Twist-Segment: Im Browser verteilen die
            # Hautgewichte den Twist graduell ueber die Segmentgrenze, und
            # der Arm dreht sich weich. Wer ihn ganz auf ein Segment legt,
            # hat 152 Grad auf halber Armlaenge statt zweimal 76.
            #
            # Die Kette bleibt dabei exakt erhalten, weil
            # `halb * halb = twist`:
            #
            #     welt(segment) = welt(eltern) * (swing*halb) * (halb*q_alt)
            #                   = welt(eltern) * swing * twist * q_alt
            #
            # Die Positionsprobe ist die Gegenprobe dazu — sie muss 0,00 mm
            # bleiben, und sie tut es.
            halb = self.halbe_drehung(twist)
            aus[name] = self.mul(swing, halb)
            aus[segment] = self.mul(halb, np.asarray(aus[segment],
                                                     dtype=np.float64))
        return aus

    @staticmethod
    def halbe_drehung(q):
        u"""Die Drehung mit halbem Winkel um dieselbe Achse.

        `halb * halb == q`. Ueber die Achse-Winkel-Darstellung, nicht ueber
        eine Quaternionen-Wurzel: Bei w nahe -1 (Winkel nahe 360 Grad) ist
        die Wurzel numerisch heikel, und `achse_winkel` nimmt ohnehin schon
        den kuerzeren Weg.
        """
        achse, winkel = Animumsetzung.achse_winkel(q)
        # VIERTEL, NICHT HALB: `achse_winkel` liefert den vollen DREHwinkel,
        # ein Quaternion traegt aber den halben. Fuer die halbe Drehung ist
        # der Quaternion-Winkel also `winkel/2/2`. Mit `winkel/2` kam eine
        # Drehung heraus, die genauso gross war wie das Original — und
        # `halb*halb` ergab 56 statt 152 Grad.
        viertel = winkel / 4.0
        sinus = np.sin(viertel)
        return np.array([achse[0] * sinus, achse[1] * sinus,
                         achse[2] * sinus, np.cos(viertel)])

    def twistbericht(self, spuren, nummern):
        u"""Twist je Gelenk in Grad — die Probe, fuer die die Positionsprobe
        blind ist. {gelenk: [Grad je Bild]}."""
        bericht = {}
        for nummer in nummern:
            drehungen = self.bild(spuren, nummer)
            for name in self.namen:
                achse = self._knochenachse(name)
                if achse is None:
                    continue
                _swing, twist = self.zerlegen(
                    np.asarray(drehungen[name], dtype=np.float64), achse)
                grad = np.degrees(2 * np.arccos(min(1.0, abs(float(twist[3])))))
                bericht.setdefault(name, []).append(float(grad))
        return bericht

    # ------------------------------------------------------------ Gegenprobe

    def gegenprobe(self, spuren, nummer, gelenkpunkte, massstab_je_meter=None,
                   roh=False):
        u"""Gelenkpunkte nach FPS-Kinematik gegen die unseres Rigs (mm).

        FPS dreht ein Kind um die Position seines Elternteils
        (`Skeleton::transform`: `pretranslate(-pV)`, drehen, zurueck). Genau
        das wird hier nachgerechnet — mit den Drehungen, die geschrieben
        werden, und den Punkten, die in der `.skel` stehen.
        """
        drehungen = self.bild(spuren, nummer, roh=roh)

        # unsere Seite: Weltmatrizen des Rigs
        unsere = self._rig_punkte(spuren, nummer)

        # FPS-Seite
        fps = {}
        for name in self.namen:
            elternteil = self.eltern.get(name)
            if not elternteil or elternteil not in fps:
                fps[name] = (gelenkpunkte[name], self._welt_von(drehungen, name))
                continue
            eltern_punkt, _eltern_dreh = fps[elternteil]
            welt = self._welt_von(drehungen, name)
            eltern_welt = self._welt_von(drehungen, elternteil)
            versatz = gelenkpunkte[name] - gelenkpunkte[elternteil]
            fps[name] = (eltern_punkt + self.drehen(eltern_welt, versatz), welt)

        # Verglichen wird RELATIV zur Wurzel und in derselben Einheit: Die
        # `.skel` steht in FPS-Einheiten (Faktor rund 12,3 gegenueber Metern)
        # und mit anderem Ursprung. Absolute Punkte zu vergleichen ergab
        # 1,79 m „Abweichung" — das war der Ursprung, nicht die Drehung.
        wurzel = self.namen[0]
        massstab = massstab_je_meter or 1.0
        abweichung = {}
        for name in self.namen:
            if name not in unsere:
                continue
            hier = (fps[name][0] - fps[wurzel][0]) / massstab
            dort = unsere[name] - unsere[wurzel]
            abweichung[name] = float(np.linalg.norm(hier - dort) * 1000.0)
        return abweichung

    def _welt_von(self, drehungen, name):
        elternteil = self.eltern.get(name)
        if not elternteil:
            return drehungen[name]
        return self.mul(self._welt_von(drehungen, elternteil), drehungen[name])

    def _rig_punkte(self, spuren, nummer):
        u"""Gelenkpunkte, wie unser eigenes Rig sie in dieser Pose haette."""
        welt = {}

        def loesen(name):
            if name in welt:
                return welt[name]
            knochen = self.knochen[name]
            spur = spuren.get(name)
            if spur is not None:
                lokal = self.nach_blender(np.asarray(
                    spur[nummer * 4:nummer * 4 + 4], dtype=np.float64))
            else:
                lokal = self._wxyz(knochen['local_quaternion'])
            versatz = np.asarray(knochen['local_position'], dtype=np.float64)
            elternteil = knochen.get('parent')
            if not elternteil or elternteil not in self.knochen:
                # Die Wurzel sitzt NICHT im Ursprung: `DEF-spine` steht bei
                # z = 0,81. Mit `zeros` verglich die Gegenprobe zwei Raeume
                # und meldete 1,79 m Abweichung.
                welt[name] = (versatz, lokal)
            else:
                ep, eq = loesen(elternteil)
                welt[name] = (ep + self.drehen(eq, versatz), self.mul(eq, lokal))
            return welt[name]

        aus = {}
        for name in self.namen:
            grund = name[:-5] if name.endswith('_ende') else name
            if grund not in self.knochen:
                continue
            punkt, drehung = loesen(grund)
            if name.endswith('_ende'):
                # Der Endpunkt sitzt am Schwanz — in Knochenrichtung (+Y).
                laenge = np.linalg.norm(self._schwanzversatz(grund))
                punkt = punkt + self.drehen(drehung, np.array([0.0, laenge, 0.0]))
            aus[name] = punkt
        return aus

    def _schwanzversatz(self, name):
        u"""Die Knochenlaenge — aus dem Rig, sonst aus dem ersten Kind."""
        if name in self.laengen:
            return np.array([0.0, float(self.laengen[name]), 0.0])
        for knochen in self.knochen.values():
            if knochen.get('parent') == name:
                return np.asarray(knochen['local_position'], dtype=np.float64)
        return np.array([0.0, 0.05, 0.0])

    # ------------------------------------------------- Quaternionen [x,y,z,w]

    @staticmethod
    def _wxyz(vier):
        u"""`def_skeleton.json` fuehrt [w, x, y, z] — hier wird [x, y, z, w]."""
        w, x, y, z = vier
        return np.array([x, y, z, w], dtype=np.float64)

    @staticmethod
    def nach_blender(q):
        u"""Retargetdrehung von Three.js-Lage in die Lage des Rigs.

        DER FEHLER HINTER DEN ERHOBENEN ARMEN (gefunden 10.09.2026). Die
        Retargetspuren kommen in Three.js-Lage (y oben), `def_skeleton.json`
        steht in Blender-Lage (z oben). Belegt an derselben Bewegung:

            DEF-spine.local_position     (0, -0,019, 0,810)     z oben
            Wurzelbahn desselben Laufs   (0,  0,810, 0,019)     y oben

        Der Weg hinueber ist `[x, z, -y, w]` (CLAUDE.md, `to_threejs`),
        also zurueck `[x, -z, y, w]`.

        OHNE DIESE ZEILE stehen beide Haende in Bild 0 bei z = 1,84 — ueber
        dem Kopf und in der Koerpermitte. Becken, Beine und Kopf sehen dabei
        richtig aus, weil ihre Ruhelage nahe der Drehachse liegt; erst der
        Arm mit 0,6 m Hebel macht es sichtbar.

        GEGEN DIE BVH-QUELLE GEPRUEFT (Walk/01_01, unabhaengige Referenz):
        Dort steht die linke Hand in Bild 5 bis 40 UEBER der Schulter und
        die rechte weit darunter. Genau diese Asymmetrie liefert die
        Umrechnung (1,467 gegen 0,930 bei Schulterhoehe 1,370); ohne sie
        stehen beide Haende gleich hoch bei 1,84.

        Warum es im Browser trotzdem stimmt: Dort sind Spuren UND Skelett
        in derselben Lage. Nur dieser Konverter mischt beide. Und warum es
        die Positionsprobe nicht findet: Sie fuettert Quelle und Ziel mit
        derselben, falsch verstandenen Eingabe und meldet 0,00 mm.
        """
        return np.array([q[0], -q[2], q[1], q[3]], dtype=np.float64)

    @staticmethod
    def mul(a, b):
        ax, ay, az, aw = a
        bx, by, bz, bw = b
        return np.array([
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz,
        ])

    @staticmethod
    def konjugiert(q):
        return np.array([-q[0], -q[1], -q[2], q[3]])

    @staticmethod
    def drehen(q, v):
        x, y, z, w = q
        u = np.array([x, y, z])
        return (v + 2.0 * np.cross(u, np.cross(u, v) + w * v))

    @staticmethod
    def achse_winkel(q):
        u"""[x,y,z,w] -> (Achse, Winkel). FPS liest genau dieses Paar."""
        q = np.asarray(q, dtype=np.float64)
        norm = np.linalg.norm(q)
        if norm < 1e-12:
            return np.array([1.0, 0.0, 0.0]), 0.0
        q = q / norm
        if q[3] < 0:                      # kuerzerer Weg
            q = -q
        winkel = 2.0 * np.arccos(np.clip(q[3], -1.0, 1.0))
        sinus = np.sqrt(max(0.0, 1.0 - q[3] * q[3]))
        if sinus < 1e-9:
            return np.array([1.0, 0.0, 0.0]), 0.0
        return q[:3] / sinus, float(winkel)
