#!/usr/bin/env python3
"""一次性脚本：把已发布 lessons/*.html 里的 base64 内嵌图转换成 R2 图床 URL。
base64 图先从 assets/ 匹配到原文件名，再上传 R2 的 ict/{集号}/{文件名}，最后替换 HTML。
用法：python3 convert_to_r2.py
"""
import os, re, base64, glob, sys, subprocess
from urllib.parse import quote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT    = os.path.dirname(os.path.abspath(__file__))
ASSETS  = os.path.join(ROOT, 'assets')
LESSONS = os.path.join(ROOT, 'lessons')

def fast_upload(local_path, remote_path):
    """直接 copyto 上传（不做存在性检查，快）。"""
    subprocess.run(['rclone', 'copyto', local_path,
                    f'r2:yeyi-ai-image/{remote_path}'],
                   check=True, capture_output=True, timeout=180)
    return f'https://img.ktzwei.top/{quote(remote_path)}'

# base64 -> 原文件名 映射
assets = {}
for f in glob.glob(os.path.join(ASSETS, '*.png')):
    b64 = base64.b64encode(open(f, 'rb').read()).decode()
    assets[b64] = os.path.basename(f)

def convert(html_path):
    num = os.path.basename(html_path).split('-')[0]
    content = open(html_path, encoding='utf-8').read()
    total = len(re.findall(r'data:image/(png|jpg|jpeg|webp);base64,', content))
    converted = [0]
    def repl(m):
        b64 = m.group(1)
        fname = assets.get(b64)
        if not fname:
            return m.group(0)  # 匹配不到就保持原样
        url = fast_upload(os.path.join(ASSETS, fname), f'ict/{num}/{fname}')
        converted[0] += 1
        return url
    new = re.sub(r'data:image/(?:png|jpg|jpeg|webp);base64,([A-Za-z0-9+/=]+)', repl, content)
    open(html_path, 'w', encoding='utf-8').write(new)
    print(f'{os.path.basename(html_path)}: 转换 {converted[0]} 张, 共 {total} 张')

for html in sorted(glob.glob(os.path.join(LESSONS, '*.html'))):
    convert(html)
print('完成')
