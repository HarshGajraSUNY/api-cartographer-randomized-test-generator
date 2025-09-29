
import requests
import json
import os
import copy


class TestExecutor:
    def __init__(self, base_url, api_config):
        self.base_url = base_url
        self.api_config = api_config
        self.session = requests.Session()

    def _load_test_data(self, data_key, data_type='valid'):
        """Loads test data from a JSON file."""
        file_path = os.path.join('test_data', data_type, f'{data_key}.json')
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Data file not found at {file_path}")
            return {}

    def run_test_path(self, path, use_invalid_data=False):
        """Executes a sequence of API calls defined in a path."""
        print(f"--- EXECUTING PATH: {' -> '.join(path)} (Invalid Data: {use_invalid_data}) ---")
        context = {}  # Stores variables like user_id, account_id
        results = []

        for step_name in path:
            step_config = self.api_config[step_name]
            url = self.base_url + step_config['path']

            # Prepare data payload
            data_type = 'invalid' if use_invalid_data else 'valid'
            payload = copy.deepcopy(self._load_test_data(step_config['data_key'], data_type))

            # Inject required variables from context
            is_missing_dependency = False
            for req in step_config.get('requires', []):
                if req not in context:
                    print(f"FAILED: Missing dependency '{req}' for step '{step_name}'")
                    is_missing_dependency = True
                    break
                payload[req] = context[req]

            if is_missing_dependency:
                return {"status": "FAILED", "reason": f"Missing dependency for {step_name}"}

            # Execute request
            try:
                response = self.session.request(step_config['method'], url, json=payload)
                result = {
                    "step": step_name,
                    "status_code": response.status_code,
                    "payload": payload,
                    "response": response.json() if response.content else {}
                }
                results.append(result)

                if response.status_code >= 400:
                    print(f"Step '{step_name}' FAILED with status {response.status_code}")
                    return {"status": "FAILED", "reason": f"API call to {step_name} failed.", "details": results}

                print(f"Step '{step_name}' SUCCEEDED with status {response.status_code}")

                # Capture provided variable for the next step
                provided_var = step_config.get('provides')
                if provided_var:
                    context[provided_var] = response.json().get(provided_var)

            except requests.RequestException as e:
                print(f"FAILED: RequestException for step '{step_name}': {e}")
                return {"status": "FAILED", "reason": str(e), "details": results}

        return {"status": "PASSED", "details": results}
