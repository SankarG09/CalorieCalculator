"""Build a deterministic deployment archive with build metadata and checksum."""
import argparse, hashlib, json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
def build(destination,commit,build_id):
    root=Path(__file__).resolve().parents[1]; dest=Path(destination); dest.mkdir(parents=True,exist_ok=True)
    files=[root/'app.py',root/'catalog.py',root/'requirements.txt']
    for folder in ('static','templates'): files.extend(p for p in (root/folder).rglob('*') if p.is_file())
    metadata=json.dumps({'commit':commit,'build_id':build_id},sort_keys=True).encode(); archive=dest/'app.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED) as z:
        for path in sorted(files):
            info=ZipInfo(path.relative_to(root).as_posix(),date_time=(2020,1,1,0,0,0)); info.compress_type=ZIP_DEFLATED; z.writestr(info,path.read_bytes())
        info=ZipInfo('static/build.json',date_time=(2020,1,1,0,0,0)); info.compress_type=ZIP_DEFLATED; z.writestr(info,metadata)
    (dest/'build.json').write_bytes(metadata); (dest/'app.zip.sha256').write_text(f'{hashlib.sha256(archive.read_bytes()).hexdigest()}  app.zip\n',encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('destination'); p.add_argument('--commit',required=True); p.add_argument('--build',required=True); a=p.parse_args(); build(a.destination,a.commit,a.build)
