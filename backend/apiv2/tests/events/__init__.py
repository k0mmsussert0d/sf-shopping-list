import json
import os


with open(os.path.join(os.path.dirname(os.path.relpath(__file__)), 'api_gateway_v2_event.json')) as f:
    api_gateway_v2_event = json.load(f)
