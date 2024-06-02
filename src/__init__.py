import os
from .lambda_function import lambda_handler
from .utils import get_flag_image_path

auth_key = os.environ['ESIM_GO_AUTH_KEY']
