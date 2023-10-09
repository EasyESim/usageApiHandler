import json
import boto3
import requests
import os
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    try:
        auth_key = os.environ['ESIM_GO_AUTH_KEY']
        request = event['detail']['payload']
        customer_id_to_match = request['customer_id']
        dynamodb = boto3.resource('dynamodb')
        customer_table = dynamodb.Table('customer')
        esim_table = dynamodb.Table('esim_details')
        print("source_customer_id " + str(customer_id_to_match))
        
        response = customer_table.query(
            IndexName='source_customer_id-index',
            KeyConditionExpression=Key('source_customer_id').eq(customer_id_to_match)
        )
        print(response)
        customer_data = response['Items']
        retrieved_items = []

        for items in customer_data:
            order_ids = items['orders']
            print(order_ids)
            
            for order_id in order_ids:
                response = esim_table.scan(
                    FilterExpression=Attr("order_table_ref_id").eq(order_id)
                )
                
                # Check if an item was found for the given order ID
                if 'Items' in response:
                    item = response['Items']
                    if(len(item) > 0):
                        retrieved_items.append(item[0])
                else:
                    print(f"No item found for order ID: {order_id}")
        
        esim_details = []
        if len(retrieved_items) > 0:
            for item in retrieved_items:
                if(len(item['esim_details']) > 0):
                    for esim in item['esim_details']:
                        iccid = esim['iccid']
                        print(esim['iccid'])
                        url = "https://api.esim-go.com/v2.2/esims/"+iccid+"/bundles"
                        payload = {}
                        headers = {"X-API-Key": auth_key}
                        
                        try:
                            r = requests.get(url, data=payload, headers=headers)
                            r.raise_for_status()  # Raise an exception for HTTP errors
                            
                            if(r.status_code == 200):
                                data = json.loads(r.text)
                                esim_data = data['bundles'][0]
                                esim_data['qr_code'] = 'https://esim-qrcode.s3.eu-west-2.amazonaws.com/'+iccid+'.png'
                                esim_details.append(esim_data)
                                print(esim_details)
                        except requests.exceptions.RequestException as e:
                            print(f"An error occurred while making the API request: {str(e)}")

        return esim_details

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"error": str(e)}
