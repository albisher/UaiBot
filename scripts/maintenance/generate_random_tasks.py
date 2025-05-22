import random

# List of verbs and actions that are not explicitly defined in UaiBot
verbs = [
    'summarize', 'visualize', 'archive', 'monitor', 'track', 'compare', 'forecast', 'simulate',
    'predict', 'schedule', 'annotate', 'highlight', 'extract', 'merge', 'split', 'convert',
    'translate', 'scan', 'audit', 'validate', 'synchronize', 'replicate', 'backup', 'restore',
    'deploy', 'provision', 'deprovision', 'clone', 'mount', 'unmount', 'encrypt', 'decrypt',
    'compress', 'decompress', 'index', 'tag', 'label', 'filter', 'sort', 'group', 'aggregate',
    'notify', 'alert', 'log', 'report', 'benchmark', 'profile', 'throttle', 'limit', 'prioritize',
    'archive', 'purge', 'sanitize', 'scrub', 'redact', 'mask', 'obfuscate', 'simulate', 'emulate',
    'inject', 'capture', 'record', 'replay', 'stream', 'broadcast', 'mirror', 'snapshot', 'diff',
    'patch', 'rollback', 'advance', 'rewind', 'freeze', 'thaw', 'lock', 'unlock', 'grant', 'revoke',
    'escalate', 'downgrade', 'ping', 'trace', 'map', 'visualize', 'render', 'plot', 'chart', 'graph',
    'export', 'import', 'sync', 'desync', 'archive', 'restore', 'simulate', 'emulate', 'test', 'probe'
]

# List of objects/entities
objects = [
    'system logs', 'network traffic', 'disk partitions', 'user sessions', 'API endpoints',
    'database schema', 'firewall rules', 'USB devices', 'Bluetooth connections', 'WiFi networks',
    'GPU usage', 'CPU affinity', 'memory pages', 'swap space', 'kernel modules', 'process tree',
    'file metadata', 'image files', 'audio streams', 'video files', 'container images',
    'virtual machines', 'cloud resources', 'IAM policies', 'SSL certificates', 'DNS records',
    'routing tables', 'cron jobs', 'scheduled tasks', 'environment variables', 'temp files',
    'orphaned files', 'zombie processes', 'background jobs', 'foreground tasks', 'clipboard history',
    'browser cache', 'session tokens', 'API keys', 'access logs', 'error reports', 'debug traces',
    'test results', 'build artifacts', 'deployment logs', 'release notes', 'audit trails',
    'security alerts', 'compliance reports', 'performance counters', 'resource quotas', 'usage stats'
]

# List of human-like variations
templates = [
    'Can you {verb} the {obj}?',
    'Please {verb} all {obj}.',
    'I want to {verb} my {obj}.',
    'Is it possible to {verb} the {obj}?',
    'How do I {verb} {obj}?',
    'Could you help me {verb} the {obj}?',
    'Try to {verb} {obj} now.',
    'Show me how to {verb} {obj}.',
    'What happens if I {verb} the {obj}?',
    'Attempt to {verb} {obj} for me.',
    'Go ahead and {verb} the {obj}.',
    'Would you {verb} {obj} in this environment?',
    'Is there a way to {verb} {obj}?',
    'Let\'s {verb} the {obj} together.',
    'Quickly {verb} {obj}.',
    'Safely {verb} the {obj}.',
    'Automatically {verb} {obj} every hour.',
    'Manually {verb} the {obj} now.',
    'What\'s the best way to {verb} {obj}?',
    'Give me a summary after you {verb} the {obj}.'
]

random.seed()
tasks = set()

while len(tasks) < 100:
    verb = random.choice(verbs)
    obj = random.choice(objects)
    template = random.choice(templates)
    task = template.format(verb=verb, obj=obj)
    tasks.add(task)

with open('random_tasks.txt', 'w') as f:
    for task in sorted(tasks):
        f.write(task + '\n') 