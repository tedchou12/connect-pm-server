import os

class config :
    def __init__(self):
        self.params = {'mysql_host': os.getenv('mysql_host'),
                       'mysql_user': os.getenv('mysql_user'),
                       'mysql_pass': os.getenv('mysql_pass'),
                       'mysql_port': os.getenv('mysql_port'),
                       'mysql_db'  : os.getenv('mysql_db'),
                       #smtp setup
                       'smtp_from' : os.getenv('smtp_from'),
                       'smtp_user' : os.getenv('smtp_user'),
                       'smtp_pass' : os.getenv('smtp_pass'),
                       'smtp_port' : os.getenv('smtp_port'),
                       'smtp_host' : os.getenv('smtp_host'),
                       #sfdc setup
                       'sfdc_endpoint': os.getenv('sfdc_endpoint'),
                       'sfdc_client_id': os.getenv('sfdc_client_id'),
                       'sfdc_client_secret': os.getenv('sfdc_client_secret'),
                       'sfdc_username': os.getenv('sfdc_username'),
                       'sfdc_password': os.getenv('sfdc_password'),
                       #onegarden setup
                       'one_garden_api_key': os.getenv('one_garden_api_key'),
                       'one_garden_auth': os.getenv('one_garden_auth'),
                       #other params
                       'flask_secret': os.getenv('flask_secret'),
                       'private_assets_path': os.getenv('private_assets_path'),
                       'static_path': os.getenv('static_path'),
                       'templates_path': os.getenv('templates_path'),
                       'resources_path': os.getenv('resources_path'),
                       'app_name': os.getenv('app_name'),
                       'hostname': os.getenv('hostname'),
                       'hostpart': os.getenv('hostpart'),
                       #google oidc
                       'google_client_id': os.getenv('google_client_id'),
                       'google_client_secret': os.getenv('google_client_secret'),
                       'google_auth_endpoint': os.getenv('google_auth_endpoint'),
                       'google_token_endpoint': os.getenv('google_token_endpoint'),
                       #microsoft oidc
                       'microsoft_client_id': os.getenv('microsoft_client_id'),
                       'microsoft_client_secret': os.getenv('microsoft_client_secret'),
                       'microsoft_auth_endpoint': os.getenv('microsoft_auth_endpoint'),
                       'microsoft_token_endpoint': os.getenv('microsoft_token_endpoint'),
                       #hac oidc
                       'hac_client_id': os.getenv('hac_client_id'),
                       'hac_client_secret': os.getenv('hac_client_secret'),
                       'hac_auth_endpoint': os.getenv('hac_auth_endpoint'),
                       'hac_token_endpoint': os.getenv('hac_token_endpoint'),
                      }
        # load from env
        for key in self.params :
            if os.getenv(key) is not None :
                self.params[key] = os.getenv(key)
