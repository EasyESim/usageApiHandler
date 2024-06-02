import boto3

# Add the get_flag_image_url function here


def get_flag_image_path(sku):
    bucket_name = 'country-to-flag'
    s3 = boto3.client('s3')
    folder_prefix = 'flags/'

    try:
        iso_code = sku.split('_')[-2].lower()
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        # Check if objects were found
        if 'Contents' in response:
            for obj in response['Contents']:
                object_key = obj['Key']
                # Check if the ISO code is part of the object key
                if iso_code in object_key:
                    # Return the S3 path for the matching flag image
                    s3_path = f"https://country-to-flag.s3.eu-west-2.amazonaws.com/{object_key}"
                    return s3_path

        # If no matching flag image was found
        return None

    except Exception as e:
        print(f"An error occurred while searching for flag images: {str(e)}")
        return None
