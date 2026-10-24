import importlib.util
import json
import pathlib
import subprocess
import unittest
from unittest.mock import patch

from support.nmprp_runtime_diagnostics import classify, stage_runner
from support.nmprp_stages import StageError


class DiagnosticTests(unittest.TestCase):
    def test_errors_are_classified_without_echoing_credentials_or_prompts(self):
        secret = 'sk-secret-must-not-be-logged'
        cases = [('AuthenticationError: invalid api key ' + secret, 'AUTHENTICATION_FAILED'),
                 ('No API key found: ' + secret, 'CREDENTIAL_NOT_FOUND'),
                 ('unrecognized arguments: --bad ' + secret, 'CLI_ARGUMENT_REJECTED'),
                 ('PermissionError: ' + secret, 'FILESYSTEM_PERMISSION'),
                 ('patient text ' + secret, 'UNCLASSIFIED_RUNTIME_FAILURE')]
        for text, expected in cases:
            result = classify(text)
            self.assertEqual(result, expected)
            self.assertNotIn(secret, result)
        self.assertEqual(classify('PrivatePatientSecretError'), 'UNCLASSIFIED_RUNTIME_FAILURE')

    def test_stage_exit_keeps_rc_and_safe_cause_only(self):
        p = subprocess.CompletedProcess([], 1, 'sensitive model text', 'AuthenticationError: invalid api key sk-secret')
        with patch('support.nmprp_runtime_diagnostics.subprocess.run', return_value=p):
            with self.assertRaises(StageError) as exc:
                stage_runner(['docker', '-z', 'private source'])
        self.assertIn('HERMES_EXIT_1:AUTHENTICATION_FAILED', str(exc.exception))
        self.assertNotIn('sk-secret', str(exc.exception))
        self.assertNotIn('sensitive', str(exc.exception))

    def test_readonly_probe_does_not_invoke_model_or_dump_environment(self):
        path = pathlib.Path(__file__).parents[1] / 'scripts/nmprp-profile-diagnostics.py'
        spec = importlib.util.spec_from_file_location('probe', path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        compile(module.PROBE, '<profile probe>', 'exec')
        self.assertNotIn("'-z'", module.PROBE)
        self.assertNotIn('print(os.environ', module.PROBE)
        with patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '{"profiles":{}}', '')) as call:
            with patch('sys.argv', ['probe']), patch('builtins.print') as output:
                self.assertEqual(module.main(), 0)
                self.assertEqual(json.loads(output.call_args.args[0]), {'profiles': {}})
            self.assertEqual(call.call_args.args[0][:6], ['docker', 'exec', '-i', '-u', 'hermes', 'hermes-platform-agent'])
