from django.db import models

from fanta_pcdm_api.utils import str2bool


# Create your models here.
class Puntata:
    """
    Service class: for internal use and not exposed in external schema
    """
    @classmethod
    def from_sheet(cls, record):
        return cls(record["Puntata"], record["Data"], str2bool(record["Trasmessa"]), str2bool(record["Finale"]))

    def __init__(self, numero: int, data: str, is_trasmessa: bool, is_finale: bool):
        self.numero = numero
        self.data = data
        self.is_trasmessa = is_trasmessa
        self.is_finale = is_finale


class BonusMalus:
    @property
    def is_malus(self) -> bool:
        return self.punti < 0

    @property
    def totale(self) -> int:
        return self.punti * self.quantita

    @classmethod
    def from_sheet(cls, record):
        return cls(record["ID"], record["BONUS/MALUS"], record["PUNTI"], record["QUANTITA'"])

    def __init__(self, bmid: int, descrizione: str, punti: int, quantita: int):
        self.id = bmid
        self.descrizione = descrizione
        self.punti = punti
        self.quantita = quantita

    def __repr__(self):
        return f"{self.id} {self.descrizione} {self.punti} {self.quantita}"


class ConcorrentePuntata:
    @property
    def totale(self):
        return sum([bm.totale for bm in self.bonus_malus]) if self.bonus_malus else 0

    def __init__(self, puntata: int, is_finale: bool, is_eliminato: bool, is_sospeso: bool,
                 bonus_mauls: list[BonusMalus] = None):
        self.numero_puntata = puntata
        self.is_finale = is_finale
        self.is_eliminato = is_eliminato
        self.is_sospeso = is_sospeso
        self.bonus_malus = bonus_mauls


class Concorrente:
    @classmethod
    def from_sheet(cls, record):
        return cls(record['id'], record['name'], record['image_url'])

    @property
    def punteggio(self) -> int:
        return sum([cp.totale for cp in self.puntate])

    def __init__(self, cid, name, image_url: str = None, puntate: list[ConcorrentePuntata] = None):
        self.id = cid
        self.nome = name
        self.image_url = image_url
        self.puntate = puntate

    def __repr__(self):
        return f"{self.id}. {self.nome}"


class Squadra:
    id: str
    nome: str
    propretario: str
    da_episodio: int
    concorrenti: list[Concorrente]
    sostituti: list[Concorrente]

    def __init__(self, sid: str, name: str, owner: str, from_episode: int, concorrenti: list[Concorrente],
                 first_sub: Concorrente, second_sub: Concorrente):
        self.id = sid
        self.nome = name
        self.propretario = owner
        self.da_episodio = from_episode
        self.concorrenti = concorrenti
        self.sostituti = [first_sub, second_sub]

    def __repr__(self):
        return f"{self.id} {self.nome} ({self.propretario})"


# Models for the score sheets
class PunteggioPuntata:
    @property
    def team_puntata(self) -> list[Concorrente]:
        return self._team_puntata

    @team_puntata.setter
    def team_puntata(self, tp: list[Concorrente]):
        self._team_puntata = []
        for concorrente in tp:
            self._team_puntata.append(Concorrente(
                cid=concorrente.id,
                name=concorrente.nome,
                image_url=concorrente.image_url,
                puntate=[cp for cp in concorrente.puntate if cp.numero_puntata == self.numero]
            ))

    @property
    def panchina(self) -> list[Concorrente]:
        return self._panchina

    @panchina.setter
    def panchina(self, p: list[Concorrente]):
        self._panchina = [
            Concorrente(
                cid=c.id,
                name=c.nome,
                image_url=c.image_url,
                puntate=[cp for cp in c.puntate if cp.numero_puntata == self.numero]
            ) for c in p
        ]

    @property
    def totale(self) -> int:
        return sum([bm.punti for concorrente in self.team_puntata for puntata in
                    concorrente.puntate for bm in puntata.bonus_malus]) \
            + sum([bm.punti for bm in self.team_bm])

    def __init__(self, numero: int, is_finale: bool, team_puntata: list[Concorrente], panchina: list[Concorrente],
                 sostituzioni: list[dict[str, Concorrente]], team_bm: list[BonusMalus]):
        self.numero = numero
        self.is_finale = is_finale
        self.team_bm = team_bm  # additional bonus/malus added to the Squadra
        self.team_puntata = team_puntata
        self.panchina = panchina
        self.sostituzioni = sostituzioni


class PunteggioSquadra:
    @property
    def totale(self):
        return sum([p.totale for p in self.puntate])

    def __init__(self, squadra: Squadra, punteggio_puntate: list[PunteggioPuntata]):
        self.squadra = squadra
        self.puntate = punteggio_puntate
