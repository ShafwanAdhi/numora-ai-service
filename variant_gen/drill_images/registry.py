"""Reviewed v1 allowlist. Changes require explicit template/renderer review.

Pins refer to exact UTF-8 template bytes and the approved rendering build, not
to hashes supplied by a template itself. Never auto-refresh at runtime.
"""
REVIEWED_TEMPLATES = {'pg-16-4-1': 'abfe35e7f1b5baeb07863afe61df5aed7f8103577678a6bfcc8298cced1641ae', 'pg-16-4-3': 'b17f6460e32495981c01c2f3938f19cf0bb00c9687f3feb91d50802aec815360', 'pg-16-4-4': '7d591f497cdee2e18e551708434be2d9665a199c8329dde2698e80b68c29ec52', 'pg-16-5-3': '4087f27670d9425a06e2e1f53f8470280a1e0da3e77c408f2c131fb5b5bf427f', 'pg-16-5-5': 'fc7da29172dc519b719d1e1b28e3044aee28d4e513f55ceb875d19ffa120fec6'}

REVIEWED_RENDERER = {'version': 'tryout-images-v2', 'code_sha256': '9f449c56eb93f58a96bdc5c004ed7d77c2352e4d747eb1822db4be189b665710', 'formatter_sha256': 'ac7f28c74124f5c191416c452233d16ff76c65836c6ba3f7f85a50e5ebc0d99f', 'pillow': '12.1.0', 'freetype': '2.14.1', 'zlib': '1.3.1.zlib-ng', 'pillow_core_sha256': '495f7b8cf1ec6c8894e7ff174be06622351f2c2edc8fa0b8ed03cd39c932a578', 'pillow_font_core_sha256': '02048ba09982e437fb56c35104c33b4ecca9b2166dc05486a9bbee41bd4c7831', 'python': '3.11.3', 'layout_engine': 'BASIC', 'scale': 2, 'resampling': 'LANCZOS', 'png_compress_level': 9}
