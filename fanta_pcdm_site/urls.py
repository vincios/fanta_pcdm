from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("classifica-squadre/", views.squadre_leaderboard, name="classifica-squadre"),
    path("fragments/squadre-leaderboard/", views.fragment_squadre_leaderboard, name="fragment-leaderboard-squadre"),
    path("classifica-concorrenti/", views.concorrenti_leaderboard, name="classifica-concorrenti"),
    path("fragments/concorrenti-leaderboard/", views.fragment_concorrenti_leaderboard, name="fragment-leaderboard-concorrenti")
]
