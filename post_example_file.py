from cu_box import client

EXAMPLE_FOLDER_ID = '40977453470'
EXAMPLE_FILE = './example_file.txt'

credentials_json = client.get_aws_ssm_parameter('box_integration_credentials')
box = client.get_box_client(credentials_json)

client.write_file_to_box(box, EXAMPLE_FILE, EXAMPLE_FOLDER_ID)
