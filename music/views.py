from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest
from django.db import transaction
from rest_framework import status
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from music.models import Song, Artist, Album
from music.serializers import SongSerializer, ArtistSerializer, AlbumSerializer


class SongViewSet(ReadOnlyModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    # filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # full tex search qoshilgani uchun commentga olindi
    # DjangoFilterBackend -> /api/products?category=clothing
    ordering_fields = ["listened", "-listened"]

    # http://127.0.0.1:8000/songs/?ordering=-listened
    # search_fields = ["title", "album__artist__name"]
    # full tex search qoshilgani uchun commentga olindi

    # http://127.0.0.1:8000/songs/?search=kmdir
    # (= intiger uchun)(^boshlanadigan soz)

    def get_queryset(self):
        queryset = Song.objects.all()
        query = self.request.query_params.get("search")
        if query is not None:
            queryset = Song.objects.annotate(
                similarity=Greatest(
                    TrigramSimilarity("title", query),
                    TrigramSimilarity("album__artist__name", query)
                )
            ).filter(similarity__gt=0.4).order_by("-similarity")
        return queryset

    @action(detail=True, methods=["POST"])
    def listen(self, request, *args, **kwargs):
        song = self.get_object()
        with transaction.atomic():
            song.listened += 1
            song.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"])
    def top(self, request, *args, **kwargs):
        songs = self.get_queryset()
        songs = songs.order_by('-listened')[:10]
        serializer = SongSerializer(songs, many=True)
        return Response(data=serializer.data)


class ArtistViewSet(ReadOnlyModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    pagination_class = LimitOffsetPagination

    @action(detail=True, methods=["GET"])
    def albums(self, request, *args, **kwargs):
        artist = self.get_object()
        serializer = AlbumSerializer(artist.album_set.all(), many=True)
        return Response(serializer.data)


class AlbumViewSet(ReadOnlyModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

# class SongAPIView(APIView):
#     def get(self, request):
#         songs = Song.objects.all()
#         serializer = SongSerializer(songs, many=True)
#         return Response(data=serializer.data)
#
#     def post(self, request):
#         serializer = SongSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         serializer.save()
#         return Response(data=serializer.data)
#     # def post(self, request):
#     #     name = request.data['name']
#     #     message = f"helle {name}"
#     #     return Response(data={"GETTING": message})
