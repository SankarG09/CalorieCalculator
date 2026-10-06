"""Create a consistent SQLite snapshot."""
import argparse, sqlite3
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('source'); p.add_argument('destination'); a=p.parse_args()
if not Path(a.source).is_file(): p.error('Source database does not exist')
if Path(a.destination).exists(): p.error('Destination exists; choose a new backup filename')
Path(a.destination).parent.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(f'{Path(a.source).resolve().as_uri()}?mode=ro',uri=True) as src, sqlite3.connect(a.destination) as dst: src.backup(dst)
print(f'Backup created: {a.destination}')
