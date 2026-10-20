"""Third batch: ten source-preserving originals and configurations."""
from build_drill_6_10_level45_batch1 import main as build
from test_drill_6_10_level45_batch3 import SELECTION, DATA

def author(e):
    if e['indicator'] != 8:
        from author_drill_algebra_level45_batch3 import author as make
    elif e['level'] == 4:
        from author_drill_8_level4_batch3 import author as make
    else:
        from author_drill_8_level5_batch3 import author as make
    return make(e)

if __name__ == '__main__':
    build(SELECTION=SELECTION, DATA=DATA, author=author, expected_count=10,
          batch='2026-10-20-indicators6-10-level45-batch3')
