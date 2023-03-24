from typing import Any

from fanta_pcdm_api.models import Squadra, Concorrente, PunteggioPuntata, Puntata, BonusMalus, PunteggioSquadra


def get_team_for_puntata(squadra: Squadra, puntata: Puntata) -> tuple[list[Concorrente], list[dict[str, Concorrente]]]:
    """
    Returns the actual team for a puntata, making the substitutions.

    A substitution happens in two situations:
        - a concorrente is eliminato
        - a concorrente will be eliminato because of "non si prensta in puntata"
    :param squadra:
    :param puntata:
    :return: two values: the first is the list of concorrenti of the actual team. The second is a list of substitutions
    (where a substitution is a dict with two keys: "dentro" and "fuori")
    """
    actual_team = squadra.concorrenti.copy()
    substitutes = squadra.sostituti.copy()

    substitutions = []

    def should_substitute(concorrente: Concorrente) -> bool:
        cpuntata = next((p for p in concorrente.puntate if p.numero_puntata == puntata.numero), None)
        if cpuntata is not None:
            cpuntata_bms = [bm.id for bm in cpuntata.bonus_malus]
            # 24 is the id of the "Non si presenta in puntata" malus
            # TODO: if the substitutions must be done only if the concorrente will be eliminato because of
            #       "Non si prensenta in puntata" malus, add also "and 18 in cpuntata_bms"
            return cpuntata.is_eliminato or (24 in cpuntata_bms)

        return False

    # we iterate on the actual teams until some concorrente in actual team should be substituted
    while any([should_substitute(c) for c in actual_team]):
        for i, concorrente in enumerate(actual_team):
            if should_substitute(concorrente):
                concorrente_in = None
                if len(substitutes) > 0:
                    # make the substitution
                    concorrente_in = substitutes.pop(0)
                    actual_team[i] = concorrente_in
                else:
                    # no more sobstitutes
                    actual_team.remove(concorrente)

                # Update the substitutions dictionary
                is_new = True
                new_sub = {
                    "fuori": concorrente,
                    "dentro": concorrente_in
                }

                # for s in substitutions:
                #     # if the substituted concorrente (new_sub["fuori"]) was already
                #     # a substitute entered for some other concorrente (s["dentro"]), we update the substitution...
                #     if s["dentro"] == new_sub["fuori"]:
                #         s["dentro"] = new_sub["dentro"]
                #         is_new = False
                #
                # if is_new:
                #     # ... else new_sub["dentro"] is a new substitute, and we add the substitution into the dictionary
                #     substitutions.append(new_sub)
                substitutions.append(new_sub)

    return actual_team, substitutions


def punteggio_puntata(squadra: Squadra, puntata: Puntata) -> PunteggioPuntata:
    team_full = squadra.concorrenti + squadra.sostituti

    actual_team, substitutions = get_team_for_puntata(squadra, puntata)
    # bench_team = team_full - actual_team
    bench_team = [concorrente for concorrente in team_full if concorrente not in actual_team]

    # calculate the Squadra's bonus/malus
    team_bm = []

    # 1. if a concorrente was substituted because it has the "non si presenta in puntata" malus, we add the malus
    #    to the squadra
    for sub in substitutions:
        cout_puntata = next((p for p in sub["fuori"].puntate if p.numero_puntata == puntata.numero), None)
        # 24 is the id of the "Non si presenta in puntata" malus
        bm24 = next((bm for bm in cout_puntata.bonus_malus if bm.id == 24), None)
        if bm24:
            team_bm.append(
                BonusMalus(
                    bmid=bm24.id,
                    descrizione=f"{bm24.descrizione} ({sub['fuori'].nome})",
                    punti=bm24.punti,
                    quantita=bm24.quantita
                )
            )

    return PunteggioPuntata(puntata.numero, puntata.is_finale, actual_team, bench_team, substitutions, team_bm)


def punteggio_squadra(squadra: Squadra, puntate: list[Puntata]) -> PunteggioSquadra:
    """
    Calculate the squadra punteggio for the given puntate
    :param squadra:
    :param puntate:
    :return:
    """
    return PunteggioSquadra(
        squadra=squadra,
        punteggio_puntate=[punteggio_puntata(squadra, puntata) for puntata in puntate if puntata.is_trasmessa]
    )


def classifica_squadre(squadre: list[Squadra], puntate: list[Puntata]) -> list[PunteggioSquadra]:
    """
    Get the squadre leaderboard, for the given squadre and the given puntate
    :param squadre:
    :param puntate:
    :return:
    """

    return list(reversed(sorted([punteggio_squadra(squadra, puntate) for squadra in squadre], key=lambda ps: ps.totale)))


def classifica_concorrenti(concorrenti: list[Concorrente], puntate: list[Puntata]) -> list[Concorrente]:
    """
    Get the concorrenti leaderboard, for the given concorrenti and the given puntate
    :param concorrenti:
    :param puntate:
    :return:
    """
    puntate_nums = [p.numero for p in puntate]

    # for each concorrente, we made a copy of it with its puntate filtered by the given puntate list
    concorrenti_filtered = [
        Concorrente(
            cid=c.id,
            name=c.nome,
            image_url=c.image_url,
            puntate=[p for p in c.puntate if p.numero_puntata in puntate_nums]
        ) for c in concorrenti
    ]

    return list(reversed(sorted(concorrenti_filtered, key=lambda c: c.punteggio)))
