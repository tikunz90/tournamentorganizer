# snippets/views.py
from rest_framework import generics, viewsets, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from beachhandball_app.models.Game import Game, GameAction
from beachhandball_app.api.serializers.game import GameSerializer, GameActionSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class  = GameSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        tourn = self.get_object()
        return Response(tourn)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class GameActionViewSet(viewsets.ModelViewSet):
    queryset = GameAction.objects.all()
    serializer_class  = GameActionSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        tourn = self.get_object()
        return Response(tourn)
