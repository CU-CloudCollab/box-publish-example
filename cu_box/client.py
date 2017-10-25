import boto3
import json
import logging
import os
import tempfile

from boxsdk import Client, JWTAuth
from boxsdk.exception import BoxAPIException

LOG_STREAM = 'CU-BOX-CLIENT'
LOGGER = logging.getLogger(LOG_STREAM)


def get_aws_ssm_parameter(parameter_name, decrypt=True, aws_region='us-east-1'):
    """
    Given a parameter name, retreive from AWS SSM service

    Args:
        parameter_name (str): Name of parameter in SSM
        decrypt (bool): Should paramter be decrypted on retrieval (default: True)
        aws_region (str): Region where parameter lives (default: us-east-1)

    Returns:
        str - value of parameter
    """

    # Get credentials from SSM
    LOGGER.info('Getting credentials from SSM')
    boto3.setup_default_session(region_name=aws_region)
    ssm = boto3.client('ssm')

    response = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=decrypt
    )

    return response['Parameter']['Value']


def get_box_client(credential_json):
    """
    Given the SSM parameter name for credentials - authenticate + return client

    Args:
        credential_json (str): JSON blob as provided by the Box App Management tool

    Returns:
        boxsdk.client.Client (https://github.com/box/box-python-sdk)
    """

    box_credentials = json.loads(credential_json)

    # Write out PK to tempfile - box python SDK requires that this be a file
    LOGGER.info('Writing out temorary keyfile')
    new_file, key_file_path = tempfile.mkstemp()
    os.write(new_file, box_credentials['boxAppSettings']['appAuth']['privateKey'])
    os.close(new_file)

    # Get BOX client
    LOGGER.info('Authenticating client with Box service')
    auth = JWTAuth(
        client_id=box_credentials['boxAppSettings']['clientID'],
        client_secret=box_credentials['boxAppSettings']['clientSecret'],
        enterprise_id=box_credentials['enterpriseID'],
        jwt_key_id=box_credentials['boxAppSettings']['appAuth']['publicKeyID'],
        rsa_private_key_file_sys_path=key_file_path,
        rsa_private_key_passphrase=box_credentials['boxAppSettings']['appAuth']['passphrase'].encode('ascii')
    )

    # Authenticate our client + get instance
    auth.authenticate_instance()
    client = Client(auth)

    # Cleanup tempfile
    LOGGER.info('Removing temporary keyfile')
    os.remove(key_file_path)

    return client


def write_file_to_box(box_client, file_to_write, box_folder_id):
    """
    Write specified file to specified box folder - if it exists, write a new version

    Args:
        box_client (boxsdk.client.Client)
        file_to_write (str): Path to file that should be written
        box_folder_id (str): ID of box folder where file should be written
    """

    LOGGER.info('Lookup up target folder')
    target_folder = box_client.folder(folder_id=box_folder_id)

    try:
        LOGGER.info('Attempting to upload new file')
        target_folder.upload(file_path=file_to_write)

    except BoxAPIException as err:

        if err.code == 'item_name_in_use':
            LOGGER.info('Filename already exists - writing new version')
            file_context = err.context_info
            existing_file = box_client.file(file_id=file_context['conflicts']['id'])
            existing_file.update_contents(file_path=file_to_write)

        else:
            raise err
