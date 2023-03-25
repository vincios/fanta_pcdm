from django.conf import settings
from django.shortcuts import render

from fanta_pcdm_api.data import get_client, classifica_squadre, classifica_concorrenti, clear_caches
from fanta_pcdm_api.data.loaders import get_squadre, get_puntate, get_concorrenti_full
from fanta_pcdm_api.utils import str2bool
from fanta_pcdm_site.constants import COLORS_CONCORRENTI


# Create your views here.

def index(request):
    return render(request, "fanta_pcdm_site/index.html")


def squadre_leaderboard(request):
    return render(request, "fanta_pcdm_site/classifica_squadre.html")


def concorrenti_leaderboard(request):
    return render(request, "fanta_pcdm_site/classifica_concorrenti.html")


def fragment_squadre_leaderboard(request):
    if str2bool(request.GET.get("renew", "false")):
        clear_caches()

    client = get_client(settings.GOOGLE_APPLICATION_CREDENTIALS_1)
    squadre = get_squadre(client)
    puntate = get_puntate(client)
    leaderboard = classifica_squadre(squadre, puntate)

    return render(request, "fanta_pcdm_site/fragment_squadre_leaderboard.html", context={"leaderboard": leaderboard,
                                                                                         "colors": COLORS_CONCORRENTI})


def fragment_concorrenti_leaderboard(request):
    if str2bool(request.GET.get("renew", "false")):
        clear_caches()

    client = get_client(settings.GOOGLE_APPLICATION_CREDENTIALS_1)
    concorrenti = get_concorrenti_full(client)
    puntate = get_puntate(client)
    leaderboard = classifica_concorrenti(concorrenti, puntate)

    return render(request, "fanta_pcdm_site/fragment_concorrenti_leaderboard.html", context={"leaderboard": leaderboard,
                                                                                             "colors": COLORS_CONCORRENTI})
