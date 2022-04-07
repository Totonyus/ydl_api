import unittest
import ydl_utils
import yt_dlp as youtube_dl

class Tests(unittest.TestCase):
    def test_ydl_version(self):
        print(f'youtube-dl installed version : {youtube_dl.version.__version__}')

    #Tests with no_playlist = True
    def test_must_be_checked_no_playlist(self):
        self.assertTrue(ydl_utils.can_be_checked('https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj', True) is False) #playlist only
        self.assertTrue(ydl_utils.can_be_checked('https://www.youtube.com/watch?v=Ax4uSTdkp04', True) is True) #video only
        self.assertTrue(ydl_utils.can_be_checked('https://www.youtube.com/watch?v=Ax4uSTdkp04&list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&index=10&t=0s', True) is True) #video in playlist
        self.assertTrue(ydl_utils.can_be_checked('https://twitter.com/Totonyus/status/1198152820232314885', True) is True) #not youtube

    #Tests with no_playlist = False
    def test_must_be_checked_with_playlist(self):
        self.assertTrue(ydl_utils.can_be_checked('https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj', False) is False) #playlist only
        self.assertTrue(ydl_utils.can_be_checked('https://www.youtube.com/watch?v=Ax4uSTdkp04', False) is True) #video only
        self.assertTrue(ydl_utils.can_be_checked('https://www.youtube.com/watch?v=Ax4uSTdkp04&list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&index=10&t=0s', False) is False) #video in playlist
        self.assertTrue(ydl_utils.can_be_checked('https://twitter.com/Totonyus/status/1198152820232314885', False) is True) #not youtube

    def test_check_download(self):
        self.assertTrue(ydl_utils.check_download_validity('https://www.youtube.com/watch?v=Ax4uSTdkp04', 'best')['errors'] is False)
        self.assertTrue(ydl_utils.check_download_validity('https://www.youtube.com/watch?v=Ax4uSTdkp04', 'b3st')['errors'] is True)
        self.assertTrue(ydl_utils.check_download_validity('https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj', 'b3st')['checked'] is False)

    def test_preset(self):
        self.assertEqual(len(ydl_utils.existing_presets(['best', 'audio'])), 2)
        self.assertEqual(len(ydl_utils.existing_presets(['b3st', 'audio'])), 1)
        self.assertEqual(len(ydl_utils.existing_presets(['b3st', 'aud1o'])), 1)
        self.assertEqual(len(ydl_utils.existing_presets(['b3st'])), 1)

    def test_find_associated_user(self):
        self.assertTrue(ydl_utils.find_associated_user('ydl_api_very_secret_token') is not None)
        self.assertTrue(ydl_utils.find_associated_user('ydl_api_wrong_very_secret_token') is None)

unittest.main()
