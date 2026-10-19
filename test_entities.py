import unittest

from entities import BaseEntity, ImageInfo, RecentFile, KeyValueStore


class EntityTests(unittest.TestCase):
    def test_image_info(self):
        first = ImageInfo("photo.bmp", 800, 600)
        second = ImageInfo("./photo.bmp", 100, 100)
        self.assertEqual(first, second)
        self.assertEqual(first.get_info(), "800 x 600")
        first.width = 1024
        self.assertEqual(first.width, 1024)
        self.assertIn("photo.bmp", str(first))
        self.assertIn("ImageInfo", repr(first))

    def test_recent_file(self):
        first = RecentFile("photo.bmp")
        second = RecentFile("./photo.bmp")
        self.assertEqual(first, second)
        first.path = "other.bmp"
        self.assertEqual(first.name, "other.bmp")
        self.assertIn("RecentFile", repr(first))

    def test_key_value_store(self):
        settings = KeyValueStore()
        settings.set("zoom", 100)
        settings.set("fit", True)
        self.assertEqual(settings.get("zoom"), 100)
        self.assertIn("fit", settings)
        self.assertEqual(len(settings), 2)
        self.assertTrue(settings.remove("fit"))
        self.assertNotIn("fit", settings)
        self.assertEqual(settings, KeyValueStore([("zoom", 100)]))

    def test_user_entities_inherit_abstract_base(self):
        self.assertTrue(issubclass(ImageInfo, BaseEntity))
        self.assertTrue(issubclass(RecentFile, BaseEntity))
        self.assertTrue(issubclass(KeyValueStore, BaseEntity))


if __name__ == "__main__":
    unittest.main()
