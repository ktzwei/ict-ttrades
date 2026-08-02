#!/usr/bin/env python3
"""确定 ict-ttrades 下一集该做哪一集。输出下一序号 + 视频ID + 标题。"""
import os, re, subprocess, json

ROOT = '/Users/maomao/code/web3/ict-ttrades'
LESSONS = os.path.join(ROOT, 'lessons')
PLIST = os.path.join(ROOT, 'playlist_ids.txt')

def get_next_index():
    # 扫描已发布集数
    done = set()
    if os.path.isdir(LESSONS):
        for f in os.listdir(LESSONS):
            m = re.match(r'(\d+)-', f)
            if m:
                done.add(int(m.group(1)))
    n = 1
    while n in done:
        n += 1
    return n

def main():
    n = get_next_index()
    # 从播放列表文件找对应序号的视频ID
    vid = None
    with open(PLIST) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            idx, id_ = line.split('|')
            if int(idx) == n:
                vid = id_
                break
    if not vid:
        print(f"第{n}集未在播放列表中找到（可能已全部完成或列表不完整）")
        return
    # 获取标题
    try:
        title = subprocess.run(
            ['yt-dlp','--skip-download','--print','%(title)s', f'https://www.youtube.com/watch?v={vid}'],
            capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        title = 'ICT Lesson'
    print(json.dumps({'index': n, 'video_id': vid, 'title': title}))

if __name__ == '__main__':
    main()
