# -*- coding: utf-8 -*-
"""Auftragmodell — „Als Modell speichern“ eines Auftrags mit fertiger Figur (Mesh to 3D, BlenderModel, 2D3D Kleider): EIN Code für die Auftragsseite (`Auftragsfamilie.modell`) und die
Exportleiste (`Engine2d3dKleiderexportquelle.modell_speichern`, 23.11.2026, Edgar: „eine einzige Speicherart!“). Geschrieben wird sofort (`<Speichern>.fuer(job).modell_speichern`).

    antwort, status = Auftragmodell.speichern(job, Engine2d3dKleiderspeichern, 'Name')   # {'ok', 'modell', 'stand'} / {'error'}
"""

__all__ = ['Auftragmodell']


class Auftragmodell:

    @staticmethod
    def speichern(job, speichern, name):
        """(Antwort, HTTP-Status); `name` None = Vorgabename des Auftrags (`<Name> Mesh`)."""
        if job.laeuft or not job.stellung():
            return {'error': 'Erst wenn die Figur fertig ist'}, 409
        try:
            name = speichern.fuer(job).modell_speichern(name)
        except ValueError as fehler:
            return {'error': str(fehler)}, 400
        return {'ok': True, 'modell': name, 'stand': Auftragmodell.stand(job)}, 200

    @staticmethod
    def stand(job):
        """Stand wie `Exportleistequelle.modell_stand`: `fertig` mit dem zuletzt gespeicherten Modell des Auftrags, sonst `nie`."""
        if job.modell:
            return {'status': 'fertig', 'name': job.modell, 'meldung': 'Modell „%s“ gespeichert' % job.modell}
        return {'status': 'nie'}
