# tournament/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'courts', views.CourtViewSet)
router.register(r'timeslots', views.TimeSlotViewSet)
router.register(r'categories', views.CategoryViewSet)
#router.register(r'structures', views.StructureViewSet)
router.register(r'phases', views.PhaseViewSet)
router.register(r'transitions', views.TransitionViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('cup_manager/<int:event_id>/', views.cup_manager, name='cup_manager'),
    path('basic_setup/<int:event_id>/', views.basic_setup, name='cup_basic_setup'),
    path('editor/<int:event_id>/', views.structure_editor, name='structure_editor'),
    path('api/structure-template/', views.save_structure_template, name='save_structure_template'),
    path("api/phases/<int:phase_id>/generate_matches/", views.generate_matches_view, name="generate_matches"),

]