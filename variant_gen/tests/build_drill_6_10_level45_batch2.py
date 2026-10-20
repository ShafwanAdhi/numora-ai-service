"""Author the second set of twenty using the existing source-preserving importer."""
from build_drill_6_10_level45_batch1 import main as build
from test_drill_6_10_level45_batch2 import SELECTION, DATA

def author(e):
    if e['indicator'] <= 7:
        from author_drill_6_7_level45_batch2 import author as make
    elif e['indicator'] <= 9:
        from author_drill_8_9_level45_batch2 import author as make
    else:
        from author_drill_10_level45_batch2 import author as make
    return make(e)

if __name__ == '__main__':
    build(SELECTION=SELECTION, DATA=DATA, author=author,
          batch='2026-10-20-indicators6-10-level45-batch2')
