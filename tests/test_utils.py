import unittest
from unittest.mock import patch

from src.utils import get_flag_image_path


class TestUtils(unittest.TestCase):

    @patch('src.utils.boto3.client')
    def test_get_flag_image_path_success(self, mock_boto3_client):
        # Mock S3 client response
        mock_s3_client = mock_boto3_client.return_value
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [{'Key': 'flags/flag_test_iso.png'}]
        }

        # Call the get_flag_image_path function
        flag_image_path = get_flag_image_path('bundle_test_iso_test')

        # Validate the response
        self.assertEqual(
            flag_image_path, 'https://country-to-flag.s3.eu-west-2.amazonaws.com/flags/flag_test_iso.png')

    @patch('src.utils.boto3.client')
    def test_get_flag_image_path_no_flag(self, mock_boto3_client):
        # Mock S3 client response with no matching flag
        mock_s3_client = mock_boto3_client.return_value
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [{'Key': 'flags/flag_non_matching.png'}]
        }

        # Call the get_flag_image_path function
        flag_image_path = get_flag_image_path('bundle_test_iso_test')

        # Validate the response
        self.assertIsNone(flag_image_path)


if __name__ == '__main__':
    unittest.main()
