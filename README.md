# 宾杰的个人博客

面向机器人仿真与算法的个人网站，部署于 <https://abinjie.github.io>。

## 本地编辑与预览

不需要 npm 或 Hexo。使用 Python 3 标准库生成静态页面：

```sh
python3 tools/build.py
python3 -m http.server 8000 --bind 127.0.0.1
```

在浏览器访问 `http://127.0.0.1:8000`。改动后重新生成，再刷新页面。

- `content/profile.json`：个人简介、教育、实习经历、技能、竞赛。
- `content/projects.json`：项目摘要、工作内容、结果和说明。项目筛选类别来自这里。
- `content/end-to-end.html`：保留的原有文章正文。
- `templates/base.html`：公共导航、元数据、页脚。
- `tools/build.py`：首页、项目列表与详情、关于、笔记和旧路由的生成逻辑。
- `assets/`：现用样式、脚本、原创矢量示意图与图标。

生成后的 HTML 与源码一起提交，GitHub Pages 直接提供根目录中的静态文件。`.nojekyll` 关闭 Jekyll 处理；不要用旧 Hexo 产物覆盖这些页面。

## 内容约定

定位为「机器人工程师 · 仿真与算法」。项目描述以实际参与范围为准，性能数字需保留测试语境。概念图不应标成实验截图。

不添加个人头像照片，不复制原始简历 PDF、PPT 或私人素材；公开联系信息使用邮箱与 GitHub。原始简历文件无需加入仓库。

旧文章 URL 与归档路由继续可用。新增文章时同步修改生成逻辑中的文章列表、归档与分类，重新生成 sitemap。
