import json
import boto3
import urllib3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from src.utils import get_flag_image_path


def lambda_handler(event, context):
    try:

        request = json.loads(event['body'])
        print(request)
        customer_id_to_match = request['customer_id']
        dynamodb = boto3.resource('dynamodb')
        customer_table = dynamodb.Table('customer')
        esim_table = dynamodb.Table('esim_details')

        response = customer_table.query(
            IndexName='source_customer_id-index',
            KeyConditionExpression=Key(
                'source_customer_id').eq(customer_id_to_match)
        )
        customer_data = response['Items']
        retrieved_items = []

        for items in customer_data:
            order_ids = items['orders'][::-1]
            for order_id in order_ids:
                response = esim_table.scan(
                    FilterExpression=Attr("order_table_ref_id").eq(order_id)
                )

                # Check if an item was found for the given order ID
                if 'Items' in response:
                    item = response['Items']
                    if (len(item) > 0):
                        retrieved_items.append(item[0])
                else:
                    print(f"No item found for order ID: {order_id}")

        esim_details = []
        if len(retrieved_items) > 0:
            for item in retrieved_items:
                print(retrieved_items)
                if (len(item['esim_details']) > 0):
                    for esim in item['esim_details']:
                        print(esim)

                        iccid = esim['iccid']
                        flag_image_url = get_flag_image_path(esim['bundle'])
                        if flag_image_url:
                            esim['flag_image_url'] = flag_image_url
                        print(esim['iccid'])
                        url = "https://api.esim-go.com/v2.3/esims/"+iccid+"/bundles"
                        payload = {}
                        headers = {"X-API-Key": auth_key}

                        try:
                            http = urllib3.PoolManager()
                            r = http.request(
                                'GET', url, fields=payload, headers=headers)

                            if (r.status == 200):
                                data = json.loads(r.data.decode('utf-8'))
                                print("ddd")
                                print(data)
                                # Check if the 'bundles' list is empty
                                if 'bundles' in data and len(data['bundles']) > 0:
                                    esim_data = data['bundles'][0]
                                    esim_data['qr_code'] = 'https://esim-qrcode.s3.eu-west-2.amazonaws.com/'+iccid+'.png'
                                    esim_data['esim_details'] = esim
                                    esim_details.append(esim_data)
                                    print(esim_details)
                                else:
                                    print("No bundles found for ICCID: " + iccid)
                                    # Continue to the next item in the loop
                                    continue
                            else:
                                print(f"HTTP Error: {r.status}")
                        except urllib3.exceptions.HTTPError as e:
                            print(
                                f"HTTP Error occurred while making the API request: {str(e)}")
                        except urllib3.exceptions.RequestError as e:
                            print(
                                f"Request Error occurred while making the API request: {str(e)}")

        # Return the response as a dictionary
        response_body = json.dumps({"data": esim_details})
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": response_body
        }

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        error_response_body = json.dumps({"error": str(e)})
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": error_response_body
        }
