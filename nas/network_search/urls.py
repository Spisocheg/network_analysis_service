from django.urls import path, include

from .views import IPHostToSubnetView, UpdateNetworksDBView, UpdatePhysicalDBView


updatedb_patterns = [
    path('logical/', UpdateNetworksDBView.as_view(), name='network_search_updatedb_logical'),
    path('physical/', UpdatePhysicalDBView.as_view(), name='network_search_updatedb_physical'),
]

urlpatterns = [
    path('', IPHostToSubnetView.as_view(), name='network_search'),
    path('updatedb/', include(updatedb_patterns)),
]
