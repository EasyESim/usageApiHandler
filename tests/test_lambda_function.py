import unittest
from unittest.mock import patch, MagicMock
import json
import os

from src.lambda_function import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {'ESIM_GO_AUTH_KEY': 'test_auth_key'})
    @patch('src.lambda_function.boto3.resource')
    @patch('src.lambda_function.boto3.client')
    @patch('src.lambda_function.urllib3.PoolManager')
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
    @patch('src.lambda_function.boto3.resource')
    @patch('src.lambda_function.boto3.client')
    @patch('src.lambda_function.urllib3.PoolManager')
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


if __name__ == '__main__':
    unittest.main()
