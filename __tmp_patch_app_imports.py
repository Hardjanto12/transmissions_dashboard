from pathlib import Path

path = Path('app.py')
text = path.read_text()
if 'import sys' not in text.splitlines()[0:20]:
    text = text.replace('from flask import Flask, render_template, request, jsonify, send_file\n', 'from flask import Flask, render_template, request, jsonify, send_file\nimport sys\n')
if 'from pathlib import Path' not in text.splitlines()[0:25]:
    text = text.replace('import tempfile\n\n', 'import tempfile\nfrom pathlib import Path\n\n')
path.write_text(text)
