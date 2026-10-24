"""Allowlisted diagnostics: never log stderr, prompts, credentials, or model text."""
import re
import subprocess


def classify(stderr, stdout=''):
    text = (stderr or '') + '\n' + (stdout or '')
    tests = (
        ('CLI_ARGUMENT_REJECTED', r'unrecognized arguments|no such option|unknown option'),
        ('CREDENTIAL_NOT_FOUND', r'no api key|missing api key|api.key.*(?:not set|not found|not configured)'),
        ('AUTHENTICATION_FAILED', r'authenticationerror|invalid.api.key|unauthorized|authentication failed|status.code.?401'),
        ('PROVIDER_NOT_CONFIGURED', r'provider.*not configured|no provider'),
        ('MODEL_NOT_AVAILABLE', r'model.*(?:not found|does not exist|not available)'),
        ('RATE_LIMITED', r'ratelimiterror|rate limit|status.code.?429'),
        ('PROFILE_NOT_FOUND', r'profile.*(?:not found|does not exist)'),
        ('FILESYSTEM_PERMISSION', r'permission denied|permissionerror'),
        ('RUNTIME_DEPENDENCY_MISSING', r'modulenotfounderror|importerror|command not found'),
        ('CONNECTION_FAILED', r'connectionerror|connection refused|name resolution'),
    )
    for code, pattern in tests:
        if re.search(pattern, text, re.I):
            return code
    # Exception class names contain no arbitrary error message or supplied data.
    known = {'RuntimeError', 'ValueError', 'TypeError', 'KeyError', 'FileNotFoundError',
             'TimeoutError', 'APIError', 'BadRequestError', 'NotFoundError',
             'APIConnectionError', 'APITimeoutError', 'OSError'}
    classes = [name for name in re.findall(r'\b([A-Za-z]{1,50}(?:Error|Exception))\b', text) if name in known]
    return 'RUNTIME_' + classes[-1] if classes else 'UNCLASSIFIED_RUNTIME_FAILURE'


def stage_runner(argv):
    from support.nmprp_stages import StageError
    p = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, timeout=900)
    if p.returncode and '-z' in argv:
        raise StageError('HERMES_EXIT_%d:%s;PENDING_REQUIRES_RECONCILIATION' %
                         (p.returncode, classify(p.stderr, p.stdout)))
    return p.returncode, p.stdout
