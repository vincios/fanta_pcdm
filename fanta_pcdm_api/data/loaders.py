# data loaders
from functools import lru_cache

import gspread
from cachetools import cached
from cachetools.keys import hashkey
from gspread.utils import numericise_all

from fanta_pcdm_api.data.gsheet_utils import WorksheetLoader
from fanta_pcdm_api.models import Concorrente, ConcorrentePuntata, Puntata, BonusMalus, Squadra
from fanta_pcdm_api.utils import str2bool

SHEET_KEY = "1wt-PvS1Br0bE79-eQuZyJNa-RUo3SHdyMvzrekJQ7X4"

# WORKSHEET NAMES
SHEET_CONCORRENTI = "Concorrenti"
SHEET_SQUADRE = "Squadre"
SHEET_PUNTATE = "Puntate"
SHEET_BONUS_MALUS = "Bonus / Malus"


def SHEET_CONCORRENTE(concorrente: Concorrente):
    return f"{concorrente.id}. {concorrente.nome}"


# SHEETS CONFIGURATION
# Bonus/Malus sheet
RANGE_BONUS_PUNTATA = "A3:C16"
RANGE_BONUS_FINALE = "D5:F7"
RANGE_MAULS_RANGE = "A18:C30"

# Puntata sheet
PUNTATA_ROWS_OFFSET = 22  # number of rows for each puntata

ROW_PUNTATA_ELIMINATO = 2  # Row number of the cell in Puntata 1
COLUMN_PUNTATA_ELIMINATO = "B"
ROW_PUNTATA_SOSPESO = 3  # Row number of the cell in Puntata 1
COLUMN_PUNTATA_SOSPESO = "B"
RANGE_START_ROW_PUNTATA_BONUS_MALUS = 2  # Row number of the range start in Puntata 1
RANGE_START_COLUMN_PUNTATA_BONUS_MALUS = "D"
RANGE_END_ROW_PUNTATA_BONUS_MALUS = 20  # Row number of the range start in Puntata 1
RANGE_END_COLUMN_PUNTATA_BONUS_MALUS = "H"


def ADDRESS_PUNTATA_ELIMINATO(puntata: int) -> str:
    puntata_multiplier = puntata - 1
    row_number = (puntata_multiplier * PUNTATA_ROWS_OFFSET) + ROW_PUNTATA_ELIMINATO
    return f"{COLUMN_PUNTATA_ELIMINATO}{row_number}"


def ADDRESS_PUNTATA_SOSPESO(puntata: int):
    puntata_multiplier = puntata - 1
    row_number = (puntata_multiplier * PUNTATA_ROWS_OFFSET) + ROW_PUNTATA_SOSPESO
    return f"{COLUMN_PUNTATA_SOSPESO}{row_number}"


def RANGE_PUNTATA_BONUS_MALUS(puntata: int):
    puntata_multiplier = puntata - 1
    start_row_number = (puntata_multiplier * PUNTATA_ROWS_OFFSET) + RANGE_START_ROW_PUNTATA_BONUS_MALUS
    end_row_number = (puntata_multiplier * PUNTATA_ROWS_OFFSET) + RANGE_END_ROW_PUNTATA_BONUS_MALUS

    return f"{RANGE_START_COLUMN_PUNTATA_BONUS_MALUS}{start_row_number}:{RANGE_END_COLUMN_PUNTATA_BONUS_MALUS}{end_row_number}"


def _worksheet_loader(client: gspread.Client, worksheet_title: str, table_mode: bool = False) -> WorksheetLoader:
    wl = WorksheetLoader(client, SHEET_KEY)
    wl.load_worksheet(worksheet_title, table_mode)

    return wl


@cached(cache={}, key=lambda client: hashkey())
def get_puntate(client: gspread.Client) -> list[Puntata]:
    wl = _worksheet_loader(client, SHEET_PUNTATE, table_mode=True)
    puntate_records = wl.as_records()

    return [Puntata.from_sheet(record) for record in puntate_records]


@cached(cache={}, key=lambda client, number: hashkey(number))
def get_puntata(client: gspread.Client, number: int) -> Puntata:
    puntate = get_puntate(client)
    puntate_filtered = [puntata for puntata in puntate if puntata.numero == number]

    return puntate_filtered.pop() if len(puntate_filtered) == 1 else None


@cached(cache={}, key=lambda client, concorrente, puntata, wl_concorrente: hashkey(concorrente, puntata))
def get_puntata_concorrente(client: gspread.Client, concorrente: Concorrente, puntata: int | Puntata,
                            wl_concorrente: WorksheetLoader = None) -> ConcorrentePuntata:
    """
    Load a ConcorrentePuntata object, given a concorrente and a puntata number
    :param client:
    :param concorrente:
    :param puntata:
    :param wl_concorrente: [OPTIONAL] an already loaded concorrente worksheet to reuse instead of
     make a new connection to the Google APIs
    :return:
    """
    puntata_instance = puntata if isinstance(puntata, Puntata) else get_puntata(client, puntata)
    puntata_number = puntata.numero if isinstance(puntata, Puntata) else puntata
    wl = wl_concorrente if wl_concorrente else _worksheet_loader(client, SHEET_CONCORRENTE(concorrente))

    is_eliminato = str2bool(wl.get_value(ADDRESS_PUNTATA_ELIMINATO(puntata_number)))
    is_sospeso = str2bool(wl.get_value(ADDRESS_PUNTATA_SOSPESO(puntata_number)))

    # load bonus and malus
    bm_values = wl.get_values(RANGE_PUNTATA_BONUS_MALUS(puntata_number), by_row=True)
    headers = bm_values[0]
    headers[0] = "ID"  # in the worksheet the first column (id) column doesn't have the header
    bm_rows = bm_values[1:]
    bm_list = [BonusMalus.from_sheet(dict(zip(headers, numericise_all(row)))) for row in bm_rows if not row[0] == ""]

    return ConcorrentePuntata(puntata_number, puntata_instance.is_finale, is_eliminato, is_sospeso, bm_list)


@cached(cache={}, key=lambda client, concorrente: hashkey(concorrente))
def get_puntate_concorrente(client: gspread.Client, concorrente: Concorrente) -> list[ConcorrentePuntata]:
    """
    Load all puntate objects for a given concorrente
    :param client:
    :param concorrente:
    :return:
    """
    puntate = get_puntate(client)

    wl_concorrente = _worksheet_loader(client, SHEET_CONCORRENTE(concorrente))
    return [get_puntata_concorrente(client, concorrente, puntata, wl_concorrente) for puntata in puntate if puntata.is_trasmessa]


@cached(cache={}, key=lambda client: hashkey())
def get_concorrenti_without_puntate(client: gspread.Client) -> list[Concorrente]:
    """
    Get list of concorrenti, with concorrente.puntate = None
    :param client:
    :return:
    """
    wl = _worksheet_loader(client, SHEET_CONCORRENTI, table_mode=True)
    concorrenti_records = wl.as_records()
    return [Concorrente.from_sheet(crecord) for crecord in concorrenti_records]


@cached(cache={}, key=lambda client: hashkey())
def get_concorrenti_full(client: gspread.Client) -> list[Concorrente]:
    """
    Get list of concorrenti
    :param client:
    :return:
    """
    concorrenti = get_concorrenti_without_puntate(client)

    for concorrente in concorrenti:
        concorrente.puntate = get_puntate_concorrente(client, concorrente)

    return concorrenti


@cached(cache={}, key=lambda client, name: hashkey(name))
def get_concorrente_full_by_name(client: gspread.Client, name: str) -> Concorrente | None:
    """
    Get a concorrente from its name
    :param client:
    :param name:
    :return:
    """
    concorrenti = get_concorrenti_full(client)
    return next((c for c in concorrenti if c.nome.strip().lower() == name.strip().lower()), None)


@cached(cache={}, key=lambda client: hashkey())
def get_squadre(client) -> list[Squadra]:
    """
    Get list of squadre
    :param client:
    :return:
    """
    squadre_wl = _worksheet_loader(client, "Squadre", table_mode=True)
    squadre_record = squadre_wl.as_records()

    squadre = []

    for record in squadre_record:
        sid = record["id"]
        owner = record["owner"]
        name = record["name"]
        team = [get_concorrente_full_by_name(client, cname.strip()) for cname in record["team"].split(",")]
        first_sub = get_concorrente_full_by_name(client, record["first_sub"])
        second_sub = get_concorrente_full_by_name(client, record["second_sub"])
        from_episode = record["from_episode"]

        squadre.append(Squadra(sid, name, owner, from_episode, team, first_sub, second_sub))

    return squadre


@cached(cache={}, key=lambda client, name: hashkey(name))
def get_squadra_by_name(client: gspread.Client, name: str):
    squadre = get_squadre(client)

    return next((s for s in squadre if s.nome.strip().lower() == name.strip().lower()), None)


if __name__ == "__main__":
    sheet_id = "1wt-PvS1Br0bE79-eQuZyJNa-RUo3SHdyMvzrekJQ7X4"
    gc = gspread.service_account(filename="../../google_credentials.json")
    cc = get_concorrenti_full(gc)
