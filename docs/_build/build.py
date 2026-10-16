#!/usr/bin/env python3
"""Generate static Pages files. Python 3, standard library only.
Usage: python3 docs/_build/build.py /path/to/data.js
Changed 2026-10-16 by Codex: task H rebuild from the 927-entry candidate.
"""
import argparse
import json
import re
from collections import Counter
from html import escape
from pathlib import Path

BASE = 'https://wutuobangai.github.io/happy-ai-opus55-video-prompts/'
MAIN = 'https://wutuobangai.top/opus55-video-prompts.html?utm_source=ghpages&utm_medium=referral&utm_campaign=opus55-repo'
REPO = 'https://github.com/wutuobangai/happy-ai-opus55-video-prompts'
EN = dict(showreel='Motion design & showreels', launch='Product launches & ads', explainer='Explainers & education', history='History & documentaries', music='Music videos & lyric animation', story='Stories, illustration & stop motion', self='Opus on itself', worlds='3D, shaders & worlds', remix='Remixes & recreations', interactive='Interactive websites')
INTRO = dict(showreel='从单个形状的动效循环到完整作品集，浏览转场、节奏、排版与视觉风格的提示词。', launch='寻找产品发布短片、品牌广告与演示视频灵感，观察提示词如何描述产品、镜头和卖点。', explainer='用动画讲清概念：浏览科学、技术与知识讲解案例，参考内容组织和画面表达。', history='用时间线、地图和叙事组织历史题材，查看纪录式视频的主题、风格与场景描述。', music='探索音乐、歌词与画面节奏的结合，参考 MV、歌词动画及多工具制作流程。', story='浏览故事、手绘、像素与定格风格，参考角色、场景、动作和连续叙事的写法。', self='浏览让 Opus 表达自身形象与视角的案例，观察抽象概念怎样转化为视觉创意。', worlds='从三维场景到着色器视觉，寻找空间、材质、光线与镜头运动的描述方式。', remix='观察已有作品如何被重新演绎，参考风格迁移、视觉复刻与创意改编的提示词。', interactive='浏览可互动的网页与视觉体验，参考空间探索、用户操作和动态反馈的描述。')

def e(value):
    return escape(str(value), quote=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Existing opus55-video-prompts/data.js')
    args = parser.parse_args()
    raw = args.source.read_text(encoding='utf-8')
    data = json.loads(raw.split('window.OPUS55=', 1)[1].strip().rstrip(';'))
    rows, cats = data['rows'], data['meta']['cats']
    counts = Counter(r['c'] for r in rows)
    if len(rows) != 927 or len(cats) != 10 or len({r['i'] for r in rows}) != 927:
        raise ValueError('Expected 927 distinct entries and 10 categories; review source before rebuilding.')
    if set(counts) != {c['slug'] for c in cats}:
        raise ValueError('Unrecognized category')
    out = Path(__file__).resolve().parent.parent
    names = {c['slug']: c['name'] for c in cats}
    cover = next(r['img'] for r in rows if r.get('img', '').startswith('https://cdn.wutuobangai.com/') and not r['img'].lower().endswith('.gif'))
    def card(r):
        lines = [line.strip() for line in r.get('z', '').splitlines() if line.strip()][:2]
        excerpt = '\n'.join(lines) or '本条暂无中文提示词摘录，请到主站查看案例详情。'
        img = r.get('img', '')
        image = f'<img src="{e(img)}" alt="{e(r["t"])} · 案例封面" loading="lazy" decoding="async" width="640" height="360">' if img.startswith('https://cdn.wutuobangai.com/') and not img.lower().endswith('.gif') else '<div class="no-cover">文字案例 / PROMPT NOTE</div>'
        return f'''<article class="card" id="p-{e(r['i'])}">{image}<div class="card-body"><a class="category" href="{e(r['c'])}.html">{e(names[r['c']])}</a><h3>{e(r['t'])}</h3><p class="author">作者 / Author <a href="{e(r['u'])}" rel="noopener noreferrer">@{e(r['a'])}</a></p><p class="excerpt">{e(excerpt)}</p><a class="watch" href="{e(MAIN+'#p-'+r['i'])}">看视频 → 主站条目 <span lang="en">Watch / details ↗</span></a></div></article>'''
    def page(subset, slug=None):
        filename = slug + '.html' if slug else 'index.html'
        canonical = BASE + (filename if slug else '')
        title = f'{names[slug]} · {EN[slug]} | Opus 5.5 视频提示词' if slug else 'Opus 5.5 Video Prompts · Opus 5.5 视频提示词 | 927 条案例 · Happy AI'
        desc = f'{names[slug]}：{len(subset)} 条 Opus 5.5 视频提示词案例，含作者、中文摘录与主站视频入口。{EN[slug]} prompts and examples.' if slug else '探索 927 条 Opus 5.5 视频提示词，涵盖动效、广告、科普、MV、3D 等 10 类。中文摘录、原作者与视频链接。Explore 927 Opus 5.5 video prompts across 10 categories.'
        ld = {'@context':'https://schema.org','@type':'ItemList','name':title,'url':canonical,'numberOfItems':len(subset),'itemListElement':[{'@type':'ListItem','position':i,'name':r['t'],'url':canonical+'#p-'+r['i']} for i,r in enumerate(subset,1)]}
        nav = '<a '+('aria-current="page" ' if not slug else '')+'href="index.html">全部 All <b>927</b></a>' + ''.join(f'<a {"aria-current=\"page\" " if slug==c["slug"] else ""}href="{c["slug"]}.html">{e(c["name"])} <b>{counts[c["slug"]]}</b></a>' for c in cats)
        heading = names[slug] if slug else 'Opus 5.5 视频提示词'
        enheading = EN[slug] if slug else 'Opus 5.5 Video Prompts'
        intro = INTRO[slug] if slug else '先看效果，再找到你想做的那一种。动效、产品广告、科普、音乐与 3D 世界，从这里开始。'
        return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title>
<meta name="description" content="{e(desc)}"><meta name="keywords" content="opus 5.5 video prompts,Opus 5.5 视频提示词,Claude video prompts,AI 视频,中文提示词"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{e(cover)}"><meta property="og:image:alt" content="Opus 5.5 视频案例封面"><meta property="og:locale" content="zh_CN"><meta property="og:locale:alternate" content="en_US"><meta property="og:site_name" content="Happy AI"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="style.css">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False,separators=(',',':')).replace('<',r'\u003c')}</script></head>
<body><a class="skip" href="#library">跳到案例 / Skip to prompts</a><header class="top"><a class="brand" href="index.html"><span class="brand-icon">H</span> HAPPY AI <span class="brand-sub">/ PROMPT LIBRARY</span></a><a href="{REPO}">GitHub ↗</a></header>
<main><section class="hero"><div class="eyebrow">THE CREATIVE INDEX · 中文精选</div><h1>{e(heading)}<span lang="en">{e(enheading)}</span></h1><p class="intro">{e(intro)}</p><p class="english" lang="en">Browse real examples. Find a direction. Watch the result and read the full prompt on Happy AI.</p><a class="primary" href="{e(MAIN)}">去主站看视频与完整提示词 <span lang="en">Explore Happy AI ↗</span></a><div class="stats"><span><b>{len(subset)}</b> 条案例 / examples</span><span><b>{1 if slug else 10}</b> 个分类 / categories</span><span>免费浏览 · Free to explore</span></div></section>
<section class="catalog" id="library"><div class="section-heading"><h2>{'分类案例 / Category collection' if slug else '全部灵感 / The full collection'}</h2><span>{len(subset)} entries</span></div><nav class="filters" aria-label="案例分类 / Categories">{nav}</nav><p class="note">以下为中文提示词前两个非空行；完整内容与视频在主站。部分条目为片段或描述，互动类可查看网页效果。<span lang="en"> Chinese prompt excerpts below; full prompts and available previews on the main site.</span></p><div class="grid">{''.join(card(r) for r in subset)}</div></section></main>
<footer><strong>HAPPY AI · 灵感有出处，创作有起点。</strong><p>数据快照：{e(data['meta']['built'])} · 部分中文翻译来自 Li-Evan，其余由 Happy AI 补译；站内有删减合并，本页展示摘录。</p><p>来源：<a href="https://github.com/yihui-dev/awesome-opus5-5-videos">yihui-dev · MIT</a> / <a href="https://github.com/Li-Evan/awesome-opus-5.5-video-prompts">Li-Evan · CC BY 4.0</a> · <a href="{REPO}/blob/main/LICENSE.md">许可说明</a> · <a href="{REPO}/blob/main/CREDITS.md">完整署名</a></p><p>原作者的提示词、视频与封面归原作者所有。资料免费，生成作品可能需模型订阅或其他工具；案例不代表每次都能一键复现。</p><a href="#top" onclick="window.scrollTo(0,0);return false">回到顶部 ↑</a></footer></body></html>'''
    for slug in [None] + [c['slug'] for c in cats]:
        (out/(slug+'.html' if slug else 'index.html')).write_text(page([r for r in rows if r['c']==slug] if slug else rows,slug),encoding='utf-8')
    urls = [BASE] + [BASE+c['slug']+'.html' for c in cats]
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc></url>' for u in urls)+'</urlset>\n',encoding='utf-8')
    (out/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /happy-ai-opus55-video-prompts/_build/\nSitemap: '+BASE+'sitemap.xml\n',encoding='utf-8')
    size = sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    if size > 8_000_000:
        raise ValueError(f'docs exceeds 8 MB: {size}')
    print(json.dumps({'entries':len(rows),'categories':dict(counts),'html_pages':11,'docs_bytes':size},ensure_ascii=False))

if __name__ == '__main__':
    main()
