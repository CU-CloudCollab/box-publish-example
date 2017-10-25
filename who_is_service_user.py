from cu_box import client

credentials_json = client.get_aws_ssm_parameter('box_integration_credentials')
box = client.get_box_client(credentials_json)

service_account = box.user().get()

print 'Acting as user:'
print 'Service Account name: {0}'.format(service_account.name)
print 'Service Account login: {0}'.format(service_account.login)
