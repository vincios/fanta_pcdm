from typing import List

from ninja import NinjaAPI, Router
from django.conf import settings

from fanta_pcdm_api.data import classifica_squadre, classifica_concorrenti, get_client
from fanta_pcdm_api.data.loaders import get_squadre, get_puntate, get_concorrenti_full
import fanta_pcdm_api.schema as schema

squadre_router = Router()
concorrenti_router = Router()

api = NinjaAPI()


@squadre_router.get('/leaderboard', response=List[schema.PunteggioSquadra])
def get_squadre_leaderboard(request):
    client = get_client(settings.GOOGLE_APPLICATION_CREDENTIALS_1)
    squadre = get_squadre(client)
    puntate = get_puntate(client)

    return classifica_squadre(squadre, puntate)


@concorrenti_router.get('/leaderboard', response=List[schema.Concorrente])
def get_concorrenti_leaderboard(request):
    client = get_client(settings.GOOGLE_APPLICATION_CREDENTIALS_1)
    concorrenti = get_concorrenti_full(client)
    puntate = get_puntate(client)

    return classifica_concorrenti(concorrenti, puntate)


api.add_router("/squadre/", squadre_router)
api.add_router("/concorrenti/", concorrenti_router)
