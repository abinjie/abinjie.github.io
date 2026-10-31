#!/usr/bin/env python3
"""Build the static GitHub Pages site. Python 3, standard library only."""
import html
import hashlib
import json
import re
from pathlib import Path
from string import Template
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://abinjie.github.io"
PROFILE = json.loads((ROOT / "content/profile.json").read_text())
PROJECTS = json.loads((ROOT / "content/projects.json").read_text())
TEMPLATE = Template((ROOT / "templates/base.html").read_text())
ASSET_VERSION = hashlib.sha256((ROOT / 'assets/site.css').read_bytes() + (ROOT / 'assets/site.js').read_bytes()).hexdigest()[:12]
ARTICLE_PATH = "/2025/02/22/端到端模型/"
ARTICLE_TITLE = "端到端模型与传统算法：对比与实现"
GENERATED = []


def esc(value):
    return html.escape(str(value), quote=True)


def tags(items):
    return '<div class="tags">' + ''.join(f'<span class="tag">{esc(t)}</span>' for t in items) + '</div>'


def eyebrow(text):
    return f'<div class="eyebrow">{esc(text)}</div>'


def write_page(path, title, description, body, active="", og_type="website", canonical=None):
    nav_items = [("/", "首页", "home"), ("/projects/", "项目", "projects"), ("/list/", "笔记", "notes"), ("/about/", "关于", "about")]
    nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if key == active else '') + f'>{label}</a>' for url, label, key in nav_items)
    canonical = canonical or path
    output = TEMPLATE.substitute(
        title=esc(title + " · 宾杰" if title != "宾杰 · 机器人工程师，仿真与算法" else title),
        description=esc(description), canonical=BASE_URL + quote(canonical, safe="/"),
        body=body, navigation=nav, main_class="wrap", og_type=og_type, asset_version=ASSET_VERSION,
    )
    target = ROOT / (path.lstrip('/') + 'index.html' if path.endswith('/') else path.lstrip('/'))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(output)
    GENERATED.append(path)


def mini_diagram(project):
    if project.get('cover'):
        return f'<div class="mini-diagram project-preview" aria-hidden="true"><img src="{esc(project["cover"])}" alt="" width="480" height="270" loading="lazy"></div>'
    pairs = {
        "sim2sim": ("MuJoCo", "Isaac Sim", "POLICY → EVALUATE → COMPARE"),
        "mpm": ("PARTICLES", "GRID", "NEWTON MPM / TERRAIN CONTACT"),
        "roboarena": ("PHYSICS", "3DGS + VLA", "STATE → RENDER → ACTION"),
        "synthetic-data": ("SCENE", "SENSORS", "RGB / DEPTH / POINT CLOUD"),
        "g1": ("PERCEPTION", "CONTROL", "NAVIGATE → GRASP → DELIVER"),
    }
    left, right, caption = pairs[project['slug']]
    return f'<div class="mini-diagram" aria-hidden="true"><div class="diagram-line"><span class="diagram-node">{left}</span><span class="diagram-arrow">⇄</span><span class="diagram-node solid">{right}</span></div><div class="diagram-caption">{caption}</div></div>'


def project_row(project):
    return f'''<a class="project-row" href="/projects/{project['slug']}/" data-project-category="{esc(project['category'])}">
      <span class="project-number">{project['number']}</span>
      <div><div class="project-subtitle">{esc(project['subtitle'])}</div><h3 class="project-title">{esc(project['title'])}</h3><p>{esc(project['summary'])}</p>{tags(project['tags'])}</div>
      {mini_diagram(project)}<span class="project-arrow" aria-hidden="true">↗</span></a>'''


def project_media(project):
    if not project.get('media'):
        return ''
    groups = []
    for group in project['media']:
        figures = []
        for item in group['items']:
            caption = f'<figcaption><strong>{esc(item["title"])}</strong><span>{esc(item["caption"])}</span></figcaption>'
            if item['type'] == 'video':
                asset = f'''<div class="video-player" data-video-player><video controls muted playsinline preload="none" poster="{esc(item['poster'])}" width="{item['width']}" height="{item['height']}" aria-label="{esc(item['title'])}"><source src="{esc(item['src'])}" type="video/mp4"><a href="{esc(item['src'])}">打开视频：{esc(item['title'])}</a></video><button class="video-launch" type="button" hidden aria-label="播放：{esc(item['title'])}"><img src="{esc(item['poster'])}" alt="" width="{item['width']}" height="{item['height']}" loading="lazy"><span class="video-play" aria-hidden="true">▶ <span>播放演示</span></span></button><p class="video-status" role="status" hidden>视频暂时无法播放，请重试或<a href="{esc(item['src'])}">直接打开视频</a>。</p></div>'''
            else:
                asset = f'<a class="media-image-link" href="{esc(item["src"])}" target="_blank" rel="noopener" aria-label="查看大图：{esc(item["title"])}"><img src="{esc(item["src"])}" alt="{esc(item["alt"])}" width="{item["width"]}" height="{item["height"]}" loading="lazy"></a>'
            figures.append(f'<figure class="project-media">{asset}{caption}</figure>')
        groups.append(f'<div class="media-group media-{esc(group["layout"])}">{"".join(figures)}</div>')
    return '<section class="project-demos" id="demo"><h2>演示与记录</h2>' + ''.join(groups) + '</section>'


def experience():
    return ''.join(f'''<div class="experience-row"><div class="experience-time">{esc(item['period'])}</div><div><h3>{esc(item['company'])}</h3><p class="experience-team">{esc(item['team'])}</p><p>{esc(item['summary'])}</p>{tags(item['tags'])}</div></div>''' for item in PROFILE['experience'])


def note_row():
    return f'''<a class="note-row" href="{ARTICLE_PATH}"><span class="note-date">2025.02.22 / 学习笔记</span><div><h3 class="note-title">{ARTICLE_TITLE}</h3><p>从控制与建模的视角，整理端到端模型和传统算法的基本思路、适用条件与实现流程。</p>{tags(['机器人', '控制算法'])}</div><span aria-hidden="true">↗</span></a>'''


def section_heading(label, title, url='', link=''):
    action = f'<a class="text-link" href="{url}">{link} <span aria-hidden="true">↗</span></a>' if url else ''
    return f'<div class="section-heading"><div>{eyebrow(label)}<h2>{title}</h2></div>{action}</div>'


def contact():
    return '''<section class="contact-block" aria-labelledby="contact-title"><div><div class="eyebrow">LET’S CONNECT</div><h2 id="contact-title">聊聊机器人与仿真。</h2><p>欢迎交流仿真算法、策略评测与机器人系统的工程实践。</p></div><a href="mailto:binjie6707@gmail.com">binjie6707@gmail.com <span aria-hidden="true">↗</span></a></section>'''


def home():
    body = f'''<section class="hero" aria-labelledby="hero-title">
      <div><div class="eyebrow">ROBOTICS ENGINEER / SIMULATION & ALGORITHMS</div>
        <h1 id="hero-title">你好，我是宾杰。<br>在仿真中，<br><em>走向真实世界。</em></h1>
        <p class="hero-role">机器人工程师 · 仿真与算法</p>
        <p class="hero-description">围绕机器人仿真、策略评测与合成数据，构建从物理引擎到真实机器人的验证闭环。关注 Isaac Sim / MuJoCo、Sim2Real 与物理仿真的工程实现。</p>
        <div class="hero-actions"><a class="button" href="/projects/">查看项目 <span aria-hidden="true">↗</span></a><a class="text-link" href="/about/">了解我的经历 <span aria-hidden="true">→</span></a></div>
        <div class="hero-meta"><span>WUXI UNIVERSITY / AI</span><span>2027 届本科</span></div>
      </div>
      <figure class="hero-figure"><div class="hero-image-meta"><span>NEWTON MPM</span><span>01 / TERRAIN CONTACT</span></div><a class="hero-media" href="/projects/mpm/#demo" aria-label="观看轮腿机器狗沙地仿真演示"><img src="/assets/media/robot-sand-hero.webp" alt="白色轮腿机器狗在沙地中行走，足部周围形成颗粒扰动" width="1000" height="1000" fetchpriority="high"><span class="hero-play" aria-hidden="true">▶</span></a><figcaption><span>轮腿机器狗 · 沙地接触</span><a href="/projects/mpm/#demo">观看演示 ↗</a></figcaption></figure>
    </section>
    <section class="focus-strip" aria-label="主要方向">
      <div class="focus-item"><span class="focus-number">01</span><div><h2>物理仿真</h2><p>Isaac Sim · MuJoCo · Newton MPM</p></div></div>
      <div class="focus-item"><span class="focus-number">02</span><div><h2>策略评测与迁移</h2><p>Sim2Sim · Sim2Real · VLA / RL</p></div></div>
      <div class="focus-item"><span class="focus-number">03</span><div><h2>感知与合成数据</h2><p>3D Gaussian Splatting · 多传感器仿真</p></div></div>
    </section>
    <section class="section" aria-labelledby="selected-projects">{section_heading('SELECTED WORK / 01', '<span id="selected-projects">精选项目</span>', '/projects/', '全部项目')}<div>{''.join(project_row(p) for p in PROJECTS[:3])}</div></section>
    <section class="section" aria-labelledby="experience-title">{section_heading('EXPERIENCE / 02', '<span id="experience-title">从仿真到实机的实践</span>', '/about/#experience', '完整经历')}{experience()}</section>
    <section class="section" aria-labelledby="notes-title">{section_heading('FIELD NOTES / 03', '<span id="notes-title">学习与记录</span>', '/list/', '全部笔记')}{note_row()}</section>
    {contact()}'''
    desc = "宾杰，机器人工程师，专注仿真与算法。分享 Isaac Sim、MuJoCo、Sim2Sim / Sim2Real、MPM 物理仿真与合成数据的项目实践。"
    write_page('/', '宾杰 · 机器人工程师，仿真与算法', desc, body, 'home')
    write_page('/index/', '宾杰 · 机器人工程师，仿真与算法', desc, body, 'home', canonical='/')


def project_pages():
    categories = ['全部'] + list(dict.fromkeys(p['category'] for p in PROJECTS))
    filters = ''.join(f'<button class="filter" type="button" data-project-filter="{esc(cat)}" aria-pressed="{str(cat == "全部").lower()}" hidden>{cat}</button>' for cat in categories)
    body = f'''<div class="page-heading">{eyebrow('PROJECTS / ENGINEERING PRACTICE')}<h1>让算法在环境中接受检验。</h1><p>从物理求解、跨引擎评测到真实机器人闭环，记录我参与构建的系统与解决的工程问题。</p></div><div class="page-content projects-list"><div class="filters" role="group" aria-label="按项目方向筛选">{filters}</div><p class="filter-status" data-filter-status role="status" aria-live="polite">显示 {len(PROJECTS)} 个项目</p>{''.join(project_row(p) for p in PROJECTS)}</div>'''
    write_page('/projects/', '项目 · 仿真与算法实践', '宾杰的机器人项目：Sim2Sim 评测、Newton MPM 沙地仿真、RoboArena、多传感器数据生成与 G1 自主任务系统。', body, 'projects')
    for i, p in enumerate(PROJECTS):
        work = ''.join(f'<h3>{esc(w["title"])}</h3><p>{esc(w["text"])}</p>' for w in p['work'])
        flow = ''.join(f'<div class="flow-step"><span>0{n + 1}</span>{esc(step)}</div>' for n, step in enumerate(p['flow']))
        metrics = '<div class="metrics">' + ''.join(f'<div class="metric"><strong>{esc(m["value"])}</strong><span>{esc(m["label"])}</span></div>' for m in p['metrics']) + '</div>' if p.get('metrics') else ''
        note = f'<div class="callout">{esc(p["note"])}</div>' if p.get('note') else ''
        next_project = PROJECTS[(i + 1) % len(PROJECTS)]
        body = f'''<div class="page-heading"><a class="crumb" href="/projects/">← 全部项目</a>{eyebrow('PROJECT ' + p['number'] + ' / ' + p['category'])}<h1>{esc(p['title'])}</h1><p>{esc(p['summary'])}</p><div class="page-kicker">{esc(p['period'])}</div></div>
        <div class="detail-layout"><article class="prose"><h2>项目背景</h2><p>{esc(p['context'])}</p>{project_media(p)}<h2>我的工作</h2>{work}<h2>链路概览</h2><div class="flow">{flow}</div><h2>项目结果</h2>{metrics}<p>{esc(p['result'])}</p>{note}</article>
        <aside class="detail-aside" aria-label="项目信息"><h2>FOCUS</h2><p>{esc(p['category'])}</p><h2>STACK</h2>{tags(p['tags'])}<h2>MORE</h2>{'<a href="#demo">演示与记录 ↓</a>' if p.get('media') else ''}<a href="/about/#experience">相关实习经历 ↗</a><a href="mailto:{PROFILE['email']}">交流这个项目 ↗</a></aside></div>
        <div class="project-next"><a href="/projects/">← 返回全部项目</a><a href="/projects/{next_project['slug']}/">下一个：{esc(next_project['title'])} →</a></div>'''
        write_page(f'/projects/{p["slug"]}/', p['title'], p['summary'], body, 'projects')


def about():
    education = PROFILE['education']
    skills = ''.join(f'<div class="skill-row"><h3>{esc(s["title"])}</h3><p>{esc(s["items"])}</p></div>' for s in PROFILE['skills'])
    awards = ''.join(f'<li>{esc(a)}</li>' for a in PROFILE['awards'])
    body = f'''<div class="page-heading">{eyebrow('ABOUT / BINJIE')}<h1>机器人工程师，<br>专注仿真与算法。</h1><p>用工程实践连接物理仿真、算法评测与真实机器人。</p></div>
    <div class="page-content"><div class="about-grid"><div><div class="about-intro"><p>我关注机器人从仿真到实机的验证过程：对齐环境、定位差异，并验证任务表现。</p></div>
    <p class="section-intro">我是宾杰，无锡学院人工智能专业本科生。三段机器人相关实习让我逐步聚焦于仿真与算法：从 MuJoCo 与 3DGS 仿真环境，到 Isaac Sim 模型测评，再到颗粒物理仿真、跨引擎策略验证和多传感器数据生产。</p>
    <p class="section-intro">我的项目覆盖四足、人形与机械臂平台。希望持续深入物理仿真、Sim2Real 与自动化评测，把可复现的实验和可定位的系统作为算法迭代的基础。</p>
    <section class="about-section" id="experience"><h2>实习经历</h2>{experience()}</section>
    <section class="about-section" id="skills"><h2>技术能力</h2>{skills}<p class="section-intro">接触过的机器人平台：Unitree G1 / Go2、Franka Panda / FR3、UR5e、AgileX Piper、AIRBOT、OpenArm 与 ALOHA。</p></section>
    <section class="about-section"><h2>教育背景</h2><div class="education-school">{education['school']}</div><div class="education-meta">{education['department']} · {education['major']}</div><div class="education-meta">{education['period']}</div></section>
    <section class="about-section"><h2>竞赛与研究记录</h2><ul class="award-list">{awards}</ul><div class="prose"><h3>论文与专利</h3><p>《基于改进 YOLOv5s 的交通标志检测算法》，2024 年 6 月公开。<br>专利：一种基于改进 YOLOv5s 模型的交通标识检测方法。<br>申请号：202410462556.6 · 公布号：CN118298404A。</p></div></section>
    <section class="about-section"><h2>相关公开项目</h2><p class="section-intro">实习经历涉及的公开平台与项目。以下链接用于了解项目背景，个人参与范围见上方经历。</p><div class="link-list"><a href="https://github.com/TATP-233/DISCOVERSE" target="_blank" rel="noopener noreferrer">DISCOVERSE ↗</a><a href="https://robochallenge.ai/" target="_blank" rel="noopener noreferrer">RoboChallenge ↗</a><a href="https://dexbotic.com/" target="_blank" rel="noopener noreferrer">Dexbotic ↗</a></div></section></div>
    <aside class="about-sidebar" aria-label="联系与个人方向"><h2>CONTACT</h2><a href="mailto:{PROFILE['email']}">{PROFILE['email']} ↗</a><a href="{PROFILE['github']}" target="_blank" rel="noopener noreferrer">github.com/abinjie ↗</a><p>欢迎机器人仿真、算法评测相关的技术交流与工程合作。</p><h2>FOCUS</h2><p>物理仿真<br>Sim2Sim / Sim2Real<br>模型评测与合成数据</p></aside></div></div>'''
    write_page('/about/', '关于宾杰', '宾杰的教育、三段机器人实习、技术能力与项目经历。职业方向：机器人工程师，偏仿真与算法。', body, 'about')


def article():
    source = (ROOT / 'content/end-to-end.html').read_text()
    # Horizontal scrolling is confined to tables on narrow screens.
    source = source.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', source)
    toc = ''.join(f'<a href="#{esc(anchor)}">{re.sub("<[^>]+>", "", title)}</a>' for anchor, title in headings)
    body = f'''<div class="page-heading"><a class="crumb" href="/list/">← 全部笔记</a>{eyebrow('FIELD NOTES / LEARNING')}<h1>{ARTICLE_TITLE}</h1><p>梳理数据驱动与基于模型的控制思路，记录早期学习中的基本概念。</p><div class="article-date">发布于 2025-02-22 · 原文更新于 2025-03-05</div>{tags(['机器人', '控制算法'])}</div>
    <div class="detail-layout article-layout"><article class="prose"><div class="callout">这是一篇早期学习笔记。文中的优缺点与对比表是概括性整理；实际精度、实时性、计算成本与泛化能力取决于任务、数据、控制器及软硬件实现，不能仅由“端到端”或“传统算法”的分类判断。</div>{source}<div class="related-note">继续阅读：<a href="/projects/sim2sim/">跨仿真引擎的策略评测</a></div></article><aside class="detail-aside"><h2>CONTENTS</h2><nav class="article-toc" aria-label="文章目录">{toc}</nav></aside></div>'''
    write_page(ARTICLE_PATH, ARTICLE_TITLE, '端到端模型与传统算法的早期学习笔记，整理基本概念、实现过程和控制方法的差异。', body, 'notes', 'article')


def note_indexes():
    for path, title, label, intro in [
        ('/list/', '学习与记录', 'FIELD NOTES', '记录机器人控制与算法学习中的思考。项目架构、个人工作与结果另见项目页。'),
        ('/archives/', '笔记归档', 'ARCHIVE', '按时间回看学习记录。'),
        ('/archives/2025/', '2025 年笔记', 'ARCHIVE / 2025', '这一年的机器人与算法学习记录。'),
        ('/archives/2025/02/', '2025 年 2 月', 'ARCHIVE / 2025.02', '机器人控制与算法的基础整理。'),
        ('/tags/机器人/', '机器人', 'TAG / ROBOTICS', '机器人控制与算法相关笔记。'),
        ('/categories/技术/', '技术笔记', 'CATEGORY / ENGINEERING', '机器人与算法的技术学习记录。'),
    ]:
        body = f'<div class="page-heading">{eyebrow(label)}<h1>{title}</h1><p>{intro}</p></div><div class="page-content"><p class="archive-heading">2025 / 01 篇</p>{note_row()}<div class="link-list"><a href="/projects/">查看项目实践 ↗</a><a href="/archives/">按时间归档 ↗</a><a href="/tags/">标签 ↗</a></div></div>'
        write_page(path, title, intro, body, 'notes')
    for path, title, label, links in [
        ('/tags/', '标签', 'TAGS', [('机器人', '/tags/机器人/', '1 篇')]),
        ('/categories/', '分类', 'CATEGORIES', [('技术笔记', '/categories/技术/', '1 篇')]),
    ]:
        rows = ''.join(f'<a class="note-row" href="{url}"><span class="note-date">{count}</span><h2 class="note-title">{name}</h2><span aria-hidden="true">→</span></a>' for name, url, count in links)
        write_page(path, title, '浏览机器人工程学习笔记。', f'<div class="page-heading">{eyebrow(label)}<h1>{title}</h1><p>从主题出发，浏览学习记录。</p></div><div class="page-content">{rows}<div class="link-list"><a href="/list/">全部笔记 ↗</a><a href="/projects/">项目实践 ↗</a></div></div>', 'notes')
    write_page('/tags/求之实习/', '求之实习', 'DISCOVER Robotics 实习经历与仿真平台开发。', f'<div class="page-heading">{eyebrow("EXPERIENCE / DISCOVER ROBOTICS")}<h1>求之科技实习</h1><p>参与 MuJoCo、3DGS 与 ROS 2 仿真平台开发的经历。</p></div><div class="page-content"><p class="section-intro">相关经历已整理到关于页，项目实践可在项目列表中浏览。</p><div class="link-list"><a href="/about/#experience">查看实习经历 ↗</a><a href="/projects/">全部项目 ↗</a></div></div>', 'about')
    body = f'<div class="page-heading">{eyebrow("RECENT UPDATES")}<h1>最近更新</h1><p>项目与学习记录的最近整理。</p></div><div class="page-content"><p class="archive-heading">2026.10.31 / 项目与个人经历整理</p>{"".join(project_row(p) for p in PROJECTS)}<p class="archive-heading" style="margin-top:40px">2025 / 学习笔记</p>{note_row()}</div>'
    write_page('/recent-updates/', '最近更新', '近期整理的机器人仿真与算法项目。', body)


def main():
    home()
    project_pages()
    about()
    article()
    note_indexes()
    write_page('/404.html', '页面未找到', '这个页面不存在，请返回首页或浏览项目与笔记。', '<section class="empty-page">' + eyebrow('PAGE NOT FOUND') + '<h1>404</h1><p>这个页面没有找到。去看看项目，或回到首页重新出发。</p><div class="hero-actions"><a class="button" href="/">返回首页 →</a><a class="text-link" href="/projects/">浏览项目 ↗</a></div></section>')
    (ROOT / '.nojekyll').touch()
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n')
    urls = [p for p in GENERATED if p not in ('/404.html', '/index/')]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{BASE_URL}{quote(p, safe="/")}</loc></url>\n' for p in urls) + '</urlset>\n'
    (ROOT / 'sitemap.xml').write_text(sitemap)
    print(f'Built {len(GENERATED)} pages, sitemap.xml and robots.txt.')


if __name__ == '__main__':
    main()
