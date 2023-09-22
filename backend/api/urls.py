from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers

from api.views import TagViewSet, RecipeViewSet, UserViewSet, IngredientViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('token/login/', TokenCreateView.as_view(), name='login'),
    path('token/logout/', TokenDestroyView.as_view(), name='logout'),
]
