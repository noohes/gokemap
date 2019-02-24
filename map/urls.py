from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from . import views, skills

app_name = 'map'
urlpatterns = [
    # ex: /map/
    path('', views.IndexView.as_view(), name='index'),
    url(r'^raid_post/', skills.raid_post),
    url(r'^raid_board/', skills.raid_board),
    # path('posted/', views.raid_post, name='posted'),
    # path('party/', views.party_post, name='p_posted'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)