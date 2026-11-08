"""Explicit profile selection. A mismatching runtime must never rewrite reviewed pins."""
import json
import os
import platform
from pathlib import Path

WINDOWS='windows-amd64-cpython-3.11.3-pillow-12.1.0-v1'
LINUX='linux-amd64-cpython-3.11.14-pillow-12.1.0-v1'
BOOKWORM='linux-amd64-bookworm-cpython-3.11.14-pillow-12.1.0-v1'

def selected_profile():
    return os.environ.get('NUMORA_RENDERER_PROFILE',WINDOWS)

def reviewed_renderer(windows):
    profile=selected_profile()
    if profile==WINDOWS:return windows
    if profile not in (LINUX, BOOKWORM) or platform.system()!='Linux' or platform.machine() not in ('x86_64','AMD64'):
        raise ValueError('Unsupported explicitly pinned renderer profile')
    definition=json.loads((Path(__file__).parent/'renderer_runtime_profiles'/f'{profile}.json').read_text())
    if definition['profileId']!=profile:raise ValueError('Renderer profile identity mismatch')
    return definition['renderer']
