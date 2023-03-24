from ninja import Schema

from fanta_pcdm_api import models


class BonusMalus(Schema):
    id: int
    descrizione: str
    is_malus: bool
    punti: int
    quantita: int

    @classmethod
    def from_model(cls, bm: models.BonusMalus):
        return cls(id=bm.id, descrizione=bm.descrizione, is_malus=bm.is_malus, punti=bm.punti, quantita=bm.quantita)


class ConcorrentePuntata(Schema):
    numero_puntata: int
    is_finale: bool
    is_eliminato: bool
    is_sospeso: bool
    bonus_malus: list[BonusMalus]
    totale: int

    @classmethod
    def from_model(cls, cp: models.ConcorrentePuntata):
        return cls(
            numero_puntata=cp.numero_puntata,
            is_finale=cp.is_finale,
            is_eliminato=cp.is_eliminato,
            is_sospeso=cp.is_sospeso,
            bonus_malus=[BonusMalus.from_model(bm) for bm in cp.bonus_malus],
            totale=cp.totale
        )


class Concorrente(Schema):
    id: str
    nome: str
    image_url: str
    puntate: list[ConcorrentePuntata]
    punteggio: int

    @classmethod
    def from_model(cls, c: models.Concorrente):
        return cls(
            id=c.id,
            nome=c.nome,
            image_url=c.image_url,
            puntate=[ConcorrentePuntata.from_model(cp) for cp in c.puntate],
            punteggio=c.punteggio
        )


class Squadra(Schema):
    id: str
    nome: str
    propretario: str
    da_episodio: int
    concorrenti: list[Concorrente]
    sostituti: list[Concorrente]

    @classmethod
    def from_model(cls, s: models.Squadra):
        return cls(
            id=s.id,
            nome=s.nome,
            propretario=s.propretario,
            da_episodio=s.da_episodio,
            concorrenti=[Concorrente.from_model(c) for c in s.concorrenti],
            sostituti=[Concorrente.from_model(c) for c in s.sostituti]
        )


# Schemas for the score sheets
class PunteggioPuntata(Schema):
    numero: int
    is_finale: bool
    team_puntata: list[Concorrente]
    panchina: list[Concorrente]
    sostituzioni: list[dict[str, Concorrente]]
    team_bm: list[BonusMalus]
    totale: int

    @classmethod
    def from_model(cls, pp: models.PunteggioPuntata):
        return cls(
            numero=pp.numero,
            is_finale=pp.is_finale,
            team_puntata=[Concorrente.from_model(c) for c in pp.team_puntata],
            panchina=[Concorrente.from_model(c) for c in pp.panchina],
            sostituzioni=pp.sostituzioni,
            team_bm=[BonusMalus.from_model(bm) for bm in pp.team_bm],
            totale=pp.totale
        )


class PunteggioSquadra(Schema):
    squadra: Squadra
    puntate: list[PunteggioPuntata]
    totale: int

    @classmethod
    def from_model(cls, ps: models.PunteggioSquadra):
        return cls(
            squadra=Squadra.from_model(ps.squadra),
            puntate=[PunteggioPuntata.from_model(pp) for pp in ps.puntate],
            totale=ps.totale
        )
