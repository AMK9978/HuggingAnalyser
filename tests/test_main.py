import sys
import unittest
from unittest.mock import patch

from huggingface_hub import hf_api
from huggingface_hub.hf_api import SpaceInfo

from main import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestMainModule(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        csv_files = [
            "models-test_category-2.csv",
            "test_category.csv",
        ]
        for csv_file in csv_files:
            file_path = os.path.join(os.path.dirname(__file__), csv_file)
            if os.path.exists(file_path):
                os.remove(file_path)

    @patch("main.hf_api.list_spaces")
    @patch("main.requests.get")
    def test_crawl_models(self, mock_requests_get, mock_list_spaces):
        mock_requests_get.return_value.text = '[{"id": "model1"}, {"id": "model2"}]'
        mock_list_spaces.return_value = ["space1", "space2"]

        crawl_models("test_category", sort="downloads", number=2)

        expected_csv_content = "category,model,number_of_apps\ntest_category,model1,2\ntest_category,model2,2\n"

        with open(
            os.path.join(os.path.dirname(__file__), "models-test_category-2.csv"), "r"
        ) as f:
            actual_csv_content = f.read()

        self.assertEqual(expected_csv_content, actual_csv_content)

    @patch("main.requests.get")
    def test_crawl_spaces(self, mock_requests_get):
        model_id = "model1"

        # Create a mock response
        mock_response = [
            SpaceInfo(
                id="space1",
                author=None,
                sha=None,
                created_at=None,
                last_modified=None,
                private=False,
                gated=None,
                disabled=None,
                host=None,
                subdomain=None,
                likes=3,
                sdk="streamlit",
                tags=["streamlit"],
                siblings=None,
                card_data=None,
                runtime=None,
                models=[model_id],
                datasets=None,
            )
        ]

        # Patch the method to return the mock response
        with patch.object(hf_api, "list_spaces", return_value=mock_response):
            result = hf_api.list_spaces(models=model_id)
            print(result)
            crawl_spaces("test_category", number=2)

            expected_csv_content = (
                "category,model,space,size\ntest_category,model1,space1,0.0\n"
            )

            with open(
                os.path.join(os.path.dirname(__file__), "test_category.csv"), "r"
            ) as f:
                actual_csv_content = f.read()

            self.assertEqual(expected_csv_content, actual_csv_content)

    def test_is_dir(self):
        # Test with various titles
        self.assertTrue(is_dir("Some Directory"))
        self.assertTrue(is_dir("Directory with Spaces"))
        self.assertTrue(is_dir("AnotherDirectory"))

        # Test with size-related titles
        self.assertFalse(is_dir("500 MB"))
        self.assertFalse(is_dir("1.5 GB"))
        self.assertFalse(is_dir("1024 Bytes hello"))
        self.assertFalse(is_dir("10 kB"))

    def test_convert_size(self):
        # Test converting size from different formats
        self.assertEqual(convert_size("500 MB"), 500 * 1024 * 1024)
        self.assertEqual(convert_size("1.5 GB"), 1.5 * 1024 * 1024 * 1024)
        self.assertEqual(convert_size("1024 Bytes"), 1024)
        self.assertEqual(convert_size("10 kB"), 10 * 1024)

        # Test with unknown format
        self.assertEqual(convert_size("unknown"), 0)


if __name__ == "__main__":
    unittest.main()
