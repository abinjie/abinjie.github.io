# 宾杰的个人博客

机器人工程师，专注仿真与算法。

[访问博客](https://abinjie.github.io/) · [项目](https://abinjie.github.io/projects/) · [关于](https://abinjie.github.io/about/)

使用 `python3 tools/build.py` 生成静态页面，再用 `python3 -m http.server 8001 --bind 127.0.0.1` 本地预览。日常构建只依赖 Python 3 标准库。

`content/notes.json` 管理文章摘要、发布和更新日期、标签与相关项目；正文存放在 `content/`。生成后的 HTML 与源码一同提交。

分享封面位于 `assets/social/`。修改封面时，用安装了 Pillow 的 Python 运行 `tools/build_social_images.py`，再重新生成页面。脚本支持通过 `--sans-font`、`--serif-font`、`--mono-font` 指定字体文件；中文字体需覆盖卡片中的汉字。PNG 已加入仓库，普通构建无需 Pillow 或系统字体。
