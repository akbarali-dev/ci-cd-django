from django.test import TestCase, Client

from music.models import Artist, Album, Song


class TestSongView(TestCase):
    def setUp(self) -> None:
        self.artist = Artist.objects.create(name="Example Artist")
        self.album = Album.objects.create(artist=self.artist, title="Test album")
        self.song = Song.objects.create(album=self.album, title="Test song")
        self.client = Client()

    def test_search(self):
        response = self.client.get("/songs/?search=Test")
        data = response.data

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["title"], "Test song")


class TestArtistViewSet(TestCase):
    def setUp(self) -> None:
        self.artist = Artist.objects.create(name="Test Artist")
        self.client = Client()

    def test_get_all_albums(self):
        response = self.client.get("/artist/")
        data = response.data
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data), 1)
        self.assertIsNotNone(data[0]['id'])
        self.assertEquals(data[0]["name"], "Test Artist")
