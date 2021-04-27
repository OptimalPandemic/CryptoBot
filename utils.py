import argparse
import yaml
import json
from jinja2 import Environment, FileSystemLoader

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.yml', help='YAML file for configuration information')
args = parser.parse_args()

with open(args.config) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

data = {}
data['auth0_domain'] = config['auth0_domain']
data['auth0_frontend_id'] = config['auth0_frontend_id']

with open('web/frontend/auth_config.json', 'w') as file:
    json.dump(data, file)

template_env = Environment(loader=FileSystemLoader('./'))
template = template_env.get_template('web/nginx.conf')
out = template.render(port=config['frontend_port'])
with open("web/nginx.conf", "w") as f:
    f.write(out)