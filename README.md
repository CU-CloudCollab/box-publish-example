# box-publish-example
Example app to publish files to Cornell Box

## Introduction
This is example code associated with a blog post available here:

https://medium.com/cuc4/publish-files-to-cornell-box-from-your-application-dc7cc84bc80e

## Installing Dependencies
The included requirements.txt includes all necessary dependencies - to install:
``` 
pip install -r requirements.txt
```

## Using the examples:

The two example scripts (who_is_service_user.py and post_example_file.py) both have configuration variables to specify the SSM parameter
that should be retrieved for Cornell Box credentials.  Edit those and specify your parameter name or otherwise pipe in your application's JSON blob.

post_example_file.py also includes a setting for the folder that the example file should be posted to.  You'll want to change this to a folder that your app
has been granted access to.
