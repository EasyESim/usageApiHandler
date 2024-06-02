import unittest
from unittest.mock import patch, MagicMock
import json
import os

from src.lambda_function import lambda_handler
from src.utils import get_flag_image_path


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {'ESIM_GO_AUTH_KEY': 'test_auth_key'})
    @patch('my_lambda_module.boto3.resource')
    @patch('my_lambda_module.boto3.client')
    @patch('my_lambda_module.urllib3.PoolManager')
    def test_lambda_handler_success(self, mock_pool_manager, mock_boto3_client, mock_boto3_resource):
        # Mocking DynamoDB table responses
        mock_dynamo_table = MagicMock()
        mock_dynamo_table.query.return_value = {
            'Items': [{'orders': ['order1', 'order2']}]
        }
        mock_dynamo_table.scan.return_value = {
            'Items': [{'esim_details': [{'iccid': '12345', 'bundle': 'bundle_test'}]}]
        }

        # Mocking boto3 resource
        mock_boto3_resource.return_value.Table.side_effect = [
            mock_dynamo_table, mock_dynamo_table]

        # Mocking urllib3 request
        mock_http = mock_pool_manager.return_value
        mock_http.request.return_value.status = 200
        mock_http.request.return_value.data = json.dumps(
            {'bundles': [{}]}).encode('utf-8')

        # Mock event
        event = {
            'body': json.dumps({'customer_id': 'test_customer_id'})
        }
        context = {}

        # Call the lambda handler
        response = lambda_handler(event, context)

        # Validate the response
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('data', json.loads(response['body']))

    @patch.dict(os.environ, {'ESIM_GO_AUTH_KEY': 'test_auth_key'})
    @patch('my_lambda_module.boto3.resource')
    @patch('my_lambda_module.boto3.client')
    @patch('my_lambda_module.urllib3.PoolManager')
    def test_lambda_handler_http_error(self, mock_pool_manager, mock_boto3_client, mock_boto3_resource):
        # Mocking DynamoDB table responses
        mock_dynamo_table = MagicMock()
        mock_dynamo_table.query.return_value = {
            'Items': [{'orders': ['order1', 'order2']}]
        }
        mock_dynamo_table.scan.return_value = {
            'Items': [{'esim_details': [{'iccid': '12345', 'bundle': 'bundle_test'}]}]
        }

        # Mocking boto3 resource
        mock_boto3_resource.return_value.Table.side_effect = [
            mock_dynamo_table, mock_dynamo_table]

        # Mocking urllib3 request with HTTP error
        mock_http = mock_pool_manager.return_value
        mock_http.request.return_value.status = 500

        # Mock event
        event = {
            'body': json.dumps({'customer_id': 'test_customer_id'})
        }
        context = {}

        # Call the lambda handler
        response = lambda_handler(event, context)

        # Validate the response
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('data', json.loads(response['body']))

    @patch.dict(os.environ, {'ESIM_GO_AUTH_KEY': 'test_auth_key'})
    @patch('my_lambda_module.boto3.client')
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

    @patch.dict(os.environ, {'ESIM_GO_AUTH_KEY': 'test_auth_key'})
    @patch('my_lambda_module.boto3.client')
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
