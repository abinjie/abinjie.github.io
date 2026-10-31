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
SHOW_QUADRUPED_MEDIA = PROFILE.get('show_quadruped_media', True)
PROJECTS = json.loads((ROOT / "content/projects.json").read_text())
EXPERIENCES = json.loads((ROOT / "content/experience.json").read_text())
TEMPLATE = Template((ROOT / "templates/base.html").read_text())
ASSET_VERSION = hashlib.sha256((ROOT / 'assets/site.css').read_bytes() + (ROOT / 'assets/site.js').read_bytes()).hexdigest()[:12]
ARTICLE_PATH = "/2025/02/22/端到端模型/"
NOTES = json.loads((ROOT / 'content/notes.json').read_text())
GENERATED = []


def esc(value):
    return html.escape(str(value), quote=True)


def tags(items):
    return '<div class="tags">' + ''.join(f'<span class="tag">{esc(t)}</span>' for t in items) + '</div>'


def eyebrow(text):
    return f'<div class="eyebrow">{esc(text)}</div>'


def write_page(path, title, description, body, active="", og_type="website", canonical=None, social_key="home"):
    nav_items = [("/", "首页", "home"), ("/projects/", "项目", "projects"), ("/list/", "笔记", "notes"), ("/about/", "关于", "about")]
    nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if key == active else '') + f'>{label}</a>' for url, label, key in nav_items)
    canonical = canonical or path
    social_alt = {
        'home': '宾杰的机器人仿真与算法博客：在仿真中，走向真实世界，配以协作机械臂概念插画。',
        'roboarena': 'RoboArena 机器人模型测评平台：本地物理仿真、云端 3DGS 渲染、VLA 推理与控制执行。',
    }[social_key]
    social_path = f'/assets/social/{social_key}.png'
    social_version = hashlib.sha256((ROOT / social_path.lstrip('/')).read_bytes()).hexdigest()[:12]
    output = TEMPLATE.substitute(
        title=esc(title + " · 宾杰" if title != "宾杰 · 机器人工程师，仿真与算法" else title),
        description=esc(description), canonical=BASE_URL + quote(canonical, safe="/"),
        body=body, navigation=nav, main_class="wrap", og_type=og_type, asset_version=ASSET_VERSION,
        social_image=BASE_URL + social_path + '?v=' + social_version, social_alt=esc(social_alt),
    )
    target = ROOT / (path.lstrip('/') + 'index.html' if path.endswith('/') else path.lstrip('/'))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(output)
    GENERATED.append(path)


def media_enabled(project):
    return SHOW_QUADRUPED_MEDIA or project['slug'] not in ('sim2sim', 'mpm')


def mini_diagram(project):
    if project.get('cover') and media_enabled(project):
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
    if not project.get('media') or not media_enabled(project):
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


def experience(compact=False):
    if compact:
        focus = {
            'huazhijian': '物理仿真优化 · 跨引擎策略验证 · 数据采集',
            'dexforce-megvii': '操作任务仿真 · 场景渲染 · 模型测评',
            'discover': 'MuJoCo / 3DGS 仿真平台 · ROS 2 系统联调',
        }
        return '<div class="experience-summary">' + ''.join(f'''<a class="experience-brief" href="/experience/{item['slug']}/"><span class="experience-time">{esc(item['period'])}</span><div><h3>{esc(item['company'])}</h3><p>{esc(focus[item['slug']])}</p></div><span class="brief-arrow" aria-hidden="true">↗</span></a>''' for item in PROFILE['experience']) + '</div>'
    return ''.join(f'''<a class="experience-row experience-link" href="/experience/{item['slug']}/"><div class="experience-time">{esc(item['period'])}</div><div><h3><span>{esc(item['company'])}</span><span class="experience-arrow" aria-hidden="true">↗</span></h3><p class="experience-team">{esc(item['team'])}</p><p>{esc(item['summary'])}</p><div class="experience-row-bottom">{tags(item['tags'])}<span class="experience-read">查看经历 →</span></div></div></a>''' for item in PROFILE['experience'])


def experience_pages():
    intro = '三段机器人仿真与具身智能实习，覆盖物理仿真、场景与数据生成、模型评测和真实机器人验证。'
    body = f'''<div class="page-heading">{eyebrow('EXPERIENCE / ROBOTICS ENGINEERING')}<h1>仿真与算法的工程实践</h1><p>{intro}</p></div><div class="page-content experience-index">{experience()}</div>'''
    write_page('/experience/', '实习经历', intro, body, 'about')
    profiles = {item['slug']: item for item in PROFILE['experience']}
    projects = {item['slug']: item for item in PROJECTS}
    for i, detail in enumerate(EXPERIENCES):
        item = profiles[detail['slug']]
        work = ''.join(f'<section class="experience-work"><div class="work-number">0{n + 1}</div><div><h3>{esc(part["title"])}</h3><p>{esc(part["text"])}</p></div></section>' for n, part in enumerate(detail['work']))
        related = ''.join(f'<a class="experience-project" href="/projects/{slug}/"><div><span>{esc(projects[slug]["subtitle"])}</span><strong>{esc(projects[slug]["title"])}</strong></div><span aria-hidden="true">↗</span></a>' for slug in detail['projects'])
        related = f'<section id="related"><h2>相关项目</h2>{related}</section>' if related else ''
        links = ''.join(f'<a href="{esc(link["url"])}" target="_blank" rel="noopener noreferrer">{esc(link["label"])} ↗</a>' for link in detail['links'])
        links = f'<h2>相关公开项目</h2><div class="link-list">{links}</div>' if links else ''
        next_item = profiles[EXPERIENCES[(i + 1) % len(EXPERIENCES)]['slug']]
        company_heading = ' <span class="employer-join">×</span> '.join(f'<span class="employer-name">{esc(name)}</span>' for name in item['company'].split(' × ')) if ' × ' in item['company'] else esc(item['company'])
        body = f'''<div class="page-heading experience-page-heading"><a class="crumb" href="/experience/">← 全部经历</a>{eyebrow('EXPERIENCE / ' + detail['location'])}<h1>{company_heading}</h1><p>{esc(item['team'])}</p><div class="page-kicker">{esc(item['period'])} · {esc(detail['location'])}</div></div>
        <div class="detail-layout"><article class="prose"><h2>工作背景</h2><p>{esc(detail['context'])}</p><section id="work"><h2>主要工作</h2>{work}</section>{related}{links}</article>
        <aside class="detail-aside"><h2>PERIOD</h2><p>{esc(item['period'])}<br>{esc(detail['location'])}</p><h2>FOCUS</h2>{tags(item['tags'])}<h2>ON THIS PAGE</h2><a href="#work">主要工作 ↓</a>{'<a href="#related">相关项目 ↓</a>' if detail['projects'] else ''}<a href="/experience/">全部经历 ↗</a><a href="mailto:{PROFILE['email']}">联系我 ↗</a></aside></div>
        <div class="project-next"><a href="/experience/">← 返回全部经历</a><a href="/experience/{next_item['slug']}/">下一段：{esc(next_item['company'])} →</a></div>'''
        write_page(f'/experience/{detail["slug"]}/', item['company'] + ' · 实习经历', item['summary'], body, 'about')


def note_row(note):
    return f'''<a class="note-row" href="{esc(note['path'])}"><span class="note-date">{esc(note['date'].replace('-', '.'))}<span class="note-kind">{esc(note['kind'])}</span></span><div><h3 class="note-title">{esc(note['title'])}</h3><p>{esc(note['summary'])}</p>{tags(note['tags'])}</div><span aria-hidden="true">↗</span></a>'''


def architecture(compact=False):
    steps = [
        ('LOCAL / 01', '物理仿真', 'Isaac Sim · Franka / UR5', '维护机器人动力学与环境状态'),
        ('CLOUD / 02', '视觉渲染', '3D Gaussian Splatting', '将仿真状态转为视觉观测'),
        ('CLOUD / 03', '模型推理', 'VLA', '基于视觉结果预测动作序列'),
        ('LOCAL / 04', '控制执行', 'Robot controller', '执行动作并回传更新后的状态'),
    ]
    nodes = ''.join(f'<li><span class="architecture-location">{location}</span><strong>{title}</strong><span class="architecture-stack">{stack}</span>' + ('' if compact else f'<p>{description}</p>') + '</li>' for location, title, stack, description in steps)
    return f'''<figure class="architecture{' architecture-compact' if compact else ''}"><div class="architecture-heading"><span>ROBOARENA</span><span>LOCAL ↔ CLOUD</span></div><ol aria-label="RoboArena 闭环的四个步骤">{nodes}</ol><div class="architecture-feedback"><span aria-hidden="true">↺</span> 状态回传，进入下一轮仿真与决策</div><figcaption>系统链路示意 · 按 01 → 04 顺序执行</figcaption></figure>'''


def featured_project():
    project = next(p for p in PROJECTS if p['slug'] == 'roboarena')
    return f'''<div class="featured-project"><div class="featured-copy"><div class="project-subtitle">FEATURED / 模型评测</div><h3>{esc(project['title'])}</h3><p>{esc(project['summary'])}</p>{tags(project['tags'])}<dl class="project-facts"><div><dt>平台</dt><dd>Franka / UR5</dd></div><div><dt>架构</dt><dd>本地仿真 + 云端渲染与推理</dd></div></dl><a class="text-link" href="/projects/roboarena/">查看架构与我的工作 <span aria-hidden="true">↗</span></a></div><a class="featured-visual" href="/projects/roboarena/" aria-label="查看 RoboArena 模型测评平台详情">{architecture(True)}</a></div>'''


def roboarena_case():
    return f'''<section id="architecture"><h2>系统架构</h2><p>这条链路将物理仿真、视觉渲染和模型推理分配到不同服务，再通过控制执行与状态回传连接成闭环。</p>{architecture()}</section>
    <section id="decisions"><h2>拆分后的职责与接口</h2><div class="table-wrap"><table><thead><tr><th scope="col">模块</th><th scope="col">职责</th><th scope="col">传递到下一步的内容</th></tr></thead><tbody><tr><th scope="row">本地仿真</th><td>维护物理环境与机器人动力学</td><td>供渲染使用的仿真状态</td></tr><tr><th scope="row">云端渲染</th><td>通过 3DGS 生成视觉观测</td><td>供模型推理使用的视觉结果</td></tr><tr><th scope="row">云端推理</th><td>基于视觉输入预测动作</td><td>机器人待执行的动作序列</td></tr><tr><th scope="row">控制执行</th><td>执行动作并更新环境</td><td>供后续交互使用的新状态</td></tr></tbody></table></div>
    <h3>为什么拆开物理、渲染与推理？</h3><p>项目通过云端推理与渲染解耦本地仿真计算负载。在描述这套架构时，可以分别观察物理执行、视觉生成和动作预测三个环节，也更容易说明不同模型如何接入同一条交互链路。</p>
    <h3>闭环如何形成？</h3><p>一次动作预测只是其中一步。控制器执行动作后，新的仿真状态继续进入渲染与推理，形成多轮交互。这是该平台支持任务执行与策略评估的基础。</p></section>'''


def section_heading(label, title, url='', link=''):
    action = f'<a class="text-link" href="{url}">{link} <span aria-hidden="true">↗</span></a>' if url else ''
    return f'<div class="section-heading"><div>{eyebrow(label)}<h2>{title}</h2></div>{action}</div>'


def contact():
    return '''<section class="contact-block" aria-labelledby="contact-title"><div><div class="eyebrow">LET’S CONNECT</div><h2 id="contact-title">聊聊机器人与仿真。</h2><p>欢迎交流仿真算法、策略评测与机器人系统的工程实践。</p></div><a href="mailto:binjie6707@gmail.com">binjie6707@gmail.com <span aria-hidden="true">↗</span></a></section>'''


def home():
    hero_figure = '''<figure class="hero-figure robotics-hero"><div class="hero-scene"><div class="scene-orbit" aria-hidden="true"></div><div class="scene-grid" aria-hidden="true"></div><span class="scene-coordinate" aria-hidden="true">x / y / z</span><img src="/assets/media/robotics-manipulator-cutout.webp" alt="墨绿与象牙白的协作机械臂夹起方块" width="1200" height="1200" fetchpriority="high"><span class="scene-label" aria-hidden="true"><i></i> SIMULATION → REALITY</span></div><figcaption><span>物理仿真 · 策略评测 · 真实验证</span><span>概念插画</span></figcaption></figure>'''
    body = f'''<section class="hero" aria-labelledby="hero-title">
      <div><div class="eyebrow">ROBOTICS ENGINEER / SIMULATION & ALGORITHMS</div>
        <h1 id="hero-title">你好，我是宾杰。<br>在仿真中，<br><em>走向真实世界。</em></h1>
        <p class="hero-role">机器人工程师 · 仿真与算法</p>
        <p class="hero-description">我做机器人仿真、策略评测与合成数据。用 Isaac Sim / MuJoCo 构建环境，对齐策略与传感器，让实验中的差异可以记录、比较和定位。</p>
        <div class="hero-actions"><a class="button" href="#selected-projects">查看精选项目 <span aria-hidden="true">↓</span></a><a class="text-link" href="/about/">认识我 <span aria-hidden="true">→</span></a></div>
        <div class="hero-meta"><span>WUXI UNIVERSITY / AI</span><span>2027 届本科</span></div>
      </div>
{hero_figure}
    </section>
    <section class="section selected-work" aria-labelledby="selected-projects">{section_heading('SELECTED WORK / 01', '<span id="selected-projects">精选项目</span>', '/projects/', '全部项目')}{featured_project()}<div class="supporting-projects">{''.join(project_row(p) for p in PROJECTS[:2])}</div></section>
    <section class="section" aria-labelledby="experience-title">{section_heading('EXPERIENCE / 02', '<span id="experience-title"><a class="section-title-link" href="/experience/">从仿真到实机的实践 <span aria-hidden="true">↗</span></a></span>', '/experience/', '全部经历')}{experience(True)}</section>
    <section class="section" aria-labelledby="notes-title">{section_heading('FIELD NOTES / 03', '<span id="notes-title">学习与记录</span>', '/list/', '全部笔记')}{''.join(note_row(note) for note in NOTES[:2])}</section>
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
        employer = {'sim2sim': 'huazhijian', 'mpm': 'huazhijian', 'synthetic-data': 'huazhijian', 'roboarena': 'dexforce-megvii'}.get(p['slug'])
        experience_url = f'/experience/{employer}/' if employer else '/experience/'
        is_roboarena = p['slug'] == 'roboarena'
        case = roboarena_case() if is_roboarena else ''
        overview = '' if is_roboarena else f'<section id="flow"><h2>链路概览</h2><div class="flow">{flow}</div></section>'
        related_note = '<div class="related-note">工程笔记：<a href="/2026/10/31/roboarena-loop/">从仿真状态到机器人动作：RoboArena 的闭环链路 →</a></div>' if is_roboarena else ''
        toc = '<a href="#background">项目背景 ↓</a>' + ('<a href="#architecture">系统架构 ↓</a><a href="#decisions">模块职责 ↓</a>' if is_roboarena else '') + '<a href="#contribution">我的工作 ↓</a><a href="#results">项目结果 ↓</a>'
        body = f'''<div class="page-heading"><a class="crumb" href="/projects/">← 全部项目</a>{eyebrow('PROJECT ' + p['number'] + ' / ' + p['category'])}<h1>{esc(p['title'])}</h1><p>{esc(p['summary'])}</p><div class="page-kicker">{esc(p['period'])}</div></div>
        <div class="detail-layout"><article class="prose"><section id="background"><h2>项目背景</h2><p>{esc(p['context'])}</p></section>{project_media(p)}{case}<section id="contribution"><h2>我的工作</h2>{work}</section>{overview}<section id="results"><h2>项目结果</h2>{metrics}<p>{esc(p['result'])}</p>{note}</section>{related_note}</article>
        <aside class="detail-aside" aria-label="项目信息"><h2>FOCUS</h2><p>{esc(p['category'])}</p><h2>STACK</h2>{tags(p['tags'])}<h2>ON THIS PAGE</h2>{toc}<h2 class="aside-more">MORE</h2>{'<a href="#demo">演示与记录 ↓</a>' if p.get('media') and media_enabled(p) else ''}<a href="{experience_url}">{'相关实习经历' if employer else '我的实习经历'} ↗</a><a href="mailto:{PROFILE['email']}">交流这个项目 ↗</a></aside></div>
        <div class="project-next"><a href="/projects/">← 返回全部项目</a><a href="/projects/{next_project['slug']}/">下一个：{esc(next_project['title'])} →</a></div>'''
        write_page(f'/projects/{p["slug"]}/', p['title'], p['summary'], body, 'projects', social_key='roboarena' if is_roboarena else 'home')


def about():
    education = PROFILE['education']
    skills = ''.join(f'<div class="skill-row"><h3>{esc(s["title"])}</h3><p>{esc(s["items"])}</p></div>' for s in PROFILE['skills'])
    awards = ''.join(f'<li>{esc(a)}</li>' for a in PROFILE['awards'])
    body = f'''<div class="page-heading">{eyebrow('ABOUT / BINJIE')}<h1>机器人工程师，<br>专注仿真与算法。</h1><p>用工程实践连接物理仿真、算法评测与真实机器人。</p></div>
    <div class="page-content"><div class="about-grid"><div><div class="about-intro"><p>我关注机器人从仿真到实机的验证过程：对齐环境、定位差异，并验证任务表现。</p></div>
    <p class="section-intro">我是宾杰，无锡学院人工智能专业本科生。三段机器人相关实习让我逐步聚焦于仿真与算法：从 MuJoCo 与 3DGS 仿真环境，到 Isaac Sim 模型测评，再到颗粒物理仿真、跨引擎策略验证和多传感器数据生产。</p>
    <p class="section-intro">我的项目覆盖四足、人形与机械臂平台。希望持续深入物理仿真、Sim2Real 与自动化评测，把可复现的实验和可定位的系统作为算法迭代的基础。</p>
    <section class="about-section" id="experience"><h2>实习经历</h2>{experience(True)}</section>
    <section class="about-section" id="skills"><h2>技术能力</h2>{skills}<p class="section-intro">接触过的机器人平台：Unitree G1 / Go2、Franka Panda / FR3、UR5e、AgileX Piper、AIRBOT、OpenArm 与 ALOHA。</p></section>
    <section class="about-section"><h2>教育背景</h2><div class="education-school">{education['school']}</div><div class="education-meta">{education['department']} · {education['major']}</div><div class="education-meta">{education['period']}</div></section>
    <section class="about-section"><h2>竞赛与研究记录</h2><ul class="award-list">{awards}</ul><div class="prose"><h3>论文与专利</h3><p>《基于改进 YOLOv5s 的交通标志检测算法》，2024 年 6 月公开。<br>专利：一种基于改进 YOLOv5s 模型的交通标识检测方法。<br>申请号：202410462556.6 · 公布号：CN118298404A。</p></div></section>
    <section class="about-section"><h2>相关公开项目</h2><p class="section-intro">实习经历涉及的公开平台与项目。以下链接用于了解项目背景，个人参与范围见上方经历。</p><div class="link-list"><a href="https://github.com/TATP-233/DISCOVERSE" target="_blank" rel="noopener noreferrer">DISCOVERSE ↗</a><a href="https://robochallenge.ai/" target="_blank" rel="noopener noreferrer">RoboChallenge ↗</a><a href="https://dexbotic.com/" target="_blank" rel="noopener noreferrer">Dexbotic ↗</a></div></section></div>
    <aside class="about-sidebar" aria-label="联系与个人方向"><h2>CONTACT</h2><a href="mailto:{PROFILE['email']}">{PROFILE['email']} ↗</a><a href="{PROFILE['github']}" target="_blank" rel="noopener noreferrer">github.com/abinjie ↗</a><p>欢迎机器人仿真、算法评测相关的技术交流与工程合作。</p><h2>FOCUS</h2><p>物理仿真<br>Sim2Sim / Sim2Real<br>模型评测与合成数据</p></aside></div></div>'''
    write_page('/about/', '关于宾杰', '宾杰的教育、三段机器人实习、技术能力与项目经历。职业方向：机器人工程师，偏仿真与算法。', body, 'about')


def article():
    for note in NOTES:
        source = (ROOT / 'content' / note['source']).read_text()
        # Keep wide tables scrollable without widening the article or the page.
        source = source.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
        headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', source)
        toc = ''.join(f'<a href="#{esc(anchor)}">{esc(re.sub("<[^>]+>", "", title))}</a>' for anchor, title in headings)
        directory = f'<aside class="detail-aside article-aside" aria-label="阅读导航"><details class="article-directory" data-article-directory open><summary>文章目录 <span>{len(headings)} 节</span></summary><nav class="article-toc" aria-label="文章目录">{toc}</nav></details></aside>'
        published, updated = esc(note['date']), esc(note.get('updated', note['date']))
        dates = f'发布于 <time datetime="{published}">{published}</time> <span>更新于 <time datetime="{updated}">{updated}</time></span>'
        project = next(p for p in PROJECTS if p['slug'] == note['related_project'])
        related = f'<div class="related-note">相关项目：<a href="/projects/{esc(project["slug"])}/">{esc(project["title"])} →</a></div>'
        early_note = '<div class="callout">这是一篇早期学习笔记。文中的优缺点与对比表是概括性整理；实际精度、实时性、计算成本与泛化能力取决于任务、数据、控制器及软硬件实现，不能仅由“端到端”或“传统算法”的分类判断。</div>' if note['path'] == ARTICLE_PATH else ''
        label = 'FIELD NOTES / ENGINEERING' if note['kind'] == '工程笔记' else 'FIELD NOTES / LEARNING'
        body = f'''<div class="page-heading"><a class="crumb" href="/list/">← 全部笔记</a>{eyebrow(label)}<h1>{esc(note['title'])}</h1><p>{esc(note['summary'])}</p><div class="article-date">{dates}</div>{tags(note['tags'])}</div>
        <div class="detail-layout article-layout"><article class="prose">{early_note}{source}{related}</article>{directory}</div>'''
        write_page(note['path'], note['title'], note['summary'], body, 'notes', 'article', social_key='roboarena' if note['related_project'] == 'roboarena' else 'home')


def note_indexes():
    indexes = [
        ('/list/', '学习与记录', 'FIELD NOTES', '沿着项目中的状态、数据与动作，记录系统架构与机器人算法的学习。', NOTES),
        ('/archives/', '笔记归档', 'ARCHIVE', '按时间回看工程与学习记录。', NOTES),
        ('/categories/技术/', '技术笔记', 'CATEGORY / ENGINEERING', '机器人与算法的工程、学习记录。', NOTES),
    ]
    for year in sorted({note['date'][:4] for note in NOTES}, reverse=True):
        year_notes = [note for note in NOTES if note['date'].startswith(year)]
        indexes.append((f'/archives/{year}/', f'{year} 年笔记', f'ARCHIVE / {year}', '这一年的机器人与算法记录。', year_notes))
    for month in sorted({note['date'][:7] for note in NOTES}, reverse=True):
        indexes.append((f'/archives/{month.replace("-", "/")}/', f'{month[:4]} 年 {int(month[5:])} 月', 'ARCHIVE / ' + month.replace('-', '.'), '这个月的工程与学习记录。', [note for note in NOTES if note['date'].startswith(month)]))
    all_tags = list(dict.fromkeys(tag for note in NOTES for tag in note['tags']))
    for tag in all_tags:
        indexes.append((f'/tags/{tag}/', tag, 'TAG / ' + tag, f'与{tag}相关的工程与学习记录。', [note for note in NOTES if tag in note['tags']]))
    for path, title, label, intro, notes in indexes:
        groups = []
        for year in sorted({note['date'][:4] for note in notes}, reverse=True):
            group = [note for note in notes if note['date'].startswith(year)]
            groups.append(f'<section class="note-year"><h2 class="archive-heading">{year} / {len(group)} 篇</h2>{"".join(note_row(note) for note in group)}</section>')
        body = f'<div class="page-heading">{eyebrow(label)}<h1>{esc(title)}</h1><p>{esc(intro)}</p></div><div class="page-content">{"".join(groups)}<div class="link-list"><a href="/projects/">查看项目实践 ↗</a><a href="/archives/">按时间归档 ↗</a><a href="/tags/">标签 ↗</a></div></div>'
        write_page(path, title, intro, body, 'notes')
    for path, title, label, links in [
        ('/tags/', '标签', 'TAGS', [(tag, f'/tags/{tag}/', str(sum(tag in note['tags'] for note in NOTES)) + ' 篇') for tag in all_tags]),
        ('/categories/', '分类', 'CATEGORIES', [('技术笔记', '/categories/技术/', f'{len(NOTES)} 篇')]),
    ]:
        rows = ''.join(f'<a class="note-row" href="{url}"><span class="note-date">{count}</span><h2 class="note-title">{name}</h2><span aria-hidden="true">→</span></a>' for name, url, count in links)
        write_page(path, title, '浏览机器人工程学习笔记。', f'<div class="page-heading">{eyebrow(label)}<h1>{title}</h1><p>从主题出发，浏览学习记录。</p></div><div class="page-content">{rows}<div class="link-list"><a href="/list/">全部笔记 ↗</a><a href="/projects/">项目实践 ↗</a></div></div>', 'notes')
    write_page('/tags/求之实习/', '求之实习', 'DISCOVER Robotics 实习经历与仿真平台开发。', f'<div class="page-heading">{eyebrow("EXPERIENCE / DISCOVER ROBOTICS")}<h1>求之科技实习</h1><p>参与 MuJoCo、3DGS 与 ROS 2 仿真平台开发的经历。</p></div><div class="page-content"><p class="section-intro">工作内容与公开项目入口已整理到独立的实习经历页。</p><div class="link-list"><a href="/experience/discover/">查看实习经历 ↗</a><a href="/projects/">全部项目 ↗</a></div></div>', 'about')
    body = f'<div class="page-heading">{eyebrow("RECENT UPDATES")}<h1>最近更新</h1><p>项目与学习记录的最近整理。</p></div><div class="page-content"><p class="archive-heading">工程与学习笔记</p>{"".join(note_row(note) for note in NOTES)}<p class="archive-heading updates-projects">2026.10.31 / 项目与个人经历整理</p>{"".join(project_row(p) for p in PROJECTS)}</div>'
    write_page('/recent-updates/', '最近更新', '近期整理的机器人仿真与算法项目。', body)


def main():
    home()
    experience_pages()
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
