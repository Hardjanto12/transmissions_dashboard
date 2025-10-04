import pathlib
text = pathlib.Path('templates/dashboard.html').read_text(encoding='utf-8')
for i, line in enumerate(text.splitlines(), 1):
    if 'DataTable' in line:
        print(i, line)
