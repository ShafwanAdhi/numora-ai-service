"""Atomic, explicit local export with verified retry; never overwrites another bundle."""
import json
import os
import shutil
import tempfile
from pathlib import Path

from store import StoreError
from tryout_media import digest,stable_questions


def _reparse(path):
    info=path.lstat()
    return path.is_symlink() or bool(getattr(info,'st_file_attributes',0)&0x400)


def _verify_existing(target,files):
    if _reparse(target) or not target.is_dir():raise StoreError('Output is not a regular bundle directory.')
    top=set()
    for path in target.iterdir():
        if _reparse(path):raise StoreError('Bundle must not contain symbolic links or junctions.')
        top.add(path.name)
    if top!={'questions.json','media-manifest.json','preview.html','images'}:
        raise StoreError('Output contains an incomplete or different bundle.')
    images=target/'images'
    if not images.is_dir():raise StoreError('Bundle images directory is missing.')
    actual=set(top)-{'images'}
    for path in images.iterdir():
        if _reparse(path) or not path.is_file():raise StoreError('Invalid bundle image path.')
        actual.add('images/'+path.name)
    if actual!=set(files):raise StoreError('Bundle file roster differs.')
    try:
        manifest=json.loads((target/'media-manifest.json').read_bytes())
        expected=json.loads(files['media-manifest.json'])
        questions=(target/'questions.json').read_bytes()
        if digest(questions)!=manifest['questions_sha256']:raise StoreError('Stored questions hash mismatch.')
        if stable_questions(json.loads(questions))!=stable_questions(json.loads(files['questions.json'])):
            raise StoreError('Output belongs to different question content.')
        manifest.pop('questions_sha256');expected.pop('questions_sha256')
        if manifest!=expected:raise StoreError('Output belongs to a different media bundle.')
        for name,data in files.items():
            if name not in ('questions.json','media-manifest.json') and (target/name).read_bytes()!=data:
                raise StoreError('Stored preview or image bytes were modified.')
    except (ValueError,KeyError,TypeError,OSError) as error:
        raise StoreError('Cannot verify the existing local bundle.') from error


def write_files(files,output):
    target=Path(output).expanduser().absolute()
    if not target.name or target==Path(target.anchor):raise StoreError('Output must name a bundle directory.')
    if target.exists():
        if _reparse(target) or not target.is_dir():raise StoreError('Output must be a regular directory.')
        if any(target.iterdir()):
            _verify_existing(target,files);return target.resolve()
    parent=target.parent.resolve();parent.mkdir(parents=True,exist_ok=True)
    target=parent/target.name
    stage=Path(tempfile.mkdtemp(prefix=f'.{target.name}-',dir=parent))
    try:
        (stage/'images').mkdir()
        for name,data in files.items():
            path=stage/name
            if not path.resolve().is_relative_to(stage.resolve()):raise StoreError('Bundle path escapes output root.')
            with path.open('xb') as f:
                f.write(data);f.flush();os.fsync(f.fileno())
        _verify_existing(stage,files)
        if target.exists():
            if _reparse(target):raise StoreError('Output changed to a symbolic link or junction.')
            if any(target.iterdir()):
                _verify_existing(target,files);return target.resolve()
            target.rmdir()  # Only a verified empty directory; never recursive user-data deletion.
        try:stage.rename(target)
        except FileExistsError:
            _verify_existing(target,files)
        return target.resolve()
    finally:
        if stage.exists():
            # Recursive cleanup is confined to this newly created staging directory.
            if stage.resolve().parent!=parent or _reparse(stage):
                raise StoreError('Refusing cleanup outside the owned staging directory.')
            shutil.rmtree(stage)
