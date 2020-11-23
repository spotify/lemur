from lemur.plugins.bases import DestinationPlugin

class GcpDestination(DestinationPlugin):
    title = 'Gcp Destination'
    slug = 'gcp_destination'
    description = 'Gcp Destination Plugin'

    author = 'Your Name'
    author_url = 'https://github.com/yourname/lemur_pluginname'

    options = [
        {
            'name': 'gcp-project',
            'type': 'str',
            'required': True,
        },
        {
            'name': 'target-proxy-name',
            'type': 'str',
            'required': True,
        },
    ]
    additional_options = []

    def __init__(self, *args, **kwargs):
        super(GcpDestination, self).__init__(*args, **kwargs)


    def upload(self, name, body, private_key, cert_chain, options, **kwargs):
        raise NotImplementedError