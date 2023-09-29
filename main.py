import re, os, requests, threading, lzma, flet, fleter
from flet import colors, icons, Icon, Text, TextButton, TextField, Page
from threading import Thread
DOWNLOAD_URL = "https://bmclapi2.bangbang93.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json"
def app(p: Page):
    def upd(): p.update()
    def get(url):
        return requests.get(
            url = url.replace("piston-meta.mojang.com", "bmclapi2.bangbang93.com"),
            headers = {"user-agent": "Chrome/114.5.1.4"}
        )
    def change(e):
        folder.value = e.path or ""    
        upd()
    def show_banner(message):
        p.banner.content = Text(message)
        p.banner.open = True
        upd()
    def show_snack_bar(message, color = colors.GREEN):
        p.snack_bar.content = Text(message)
        p.snack_bar.bgcolor = color
        p.snack_bar.open = True
        upd()
    def close(_):
        p.banner.open = False
        upd()
    def download(_):
        def d(name, url, lz = False):
            try: buffer = get(url).content
            except: d(name, url, lz)
            else:  download.value += 1 / pool; upd()
            open(os.path.join(directory, name), 'wb').write(buffer if not lz else lzma.decompress(buffer))
        if not folder.value: show_banner("请选择保存目录")
        elif version.value is None: show_banner("请选择 JRE 版本")
        else:
            show_snack_bar(f"开始下载 {version.value}")
            download.visible = True; upd()
            tmp_ver = re.search(r'\((.*?)\)', version.value).group(1)
            for i in vers[tmp_ver]:
                if i['version']['name'] == version.value.replace(f"({tmp_ver})", ""):
                    download.value = None; upd()
                    try: manifest = get(i['manifest']['url']).json()['files']
                    except: exit(0)
                    directory, download.value = folder.value, 0; upd()
                    pool, threads = len(manifest), []
                    for f in manifest:
                        if manifest[f]['type'] == 'directory': os.makedirs(os.path.join(directory, f), exist_ok = True)
                        else:
                            k = manifest[f]['downloads']
                            t = Thread(target = d, args = (f, k[('lzma' if 'lzma' in k else 'raw')]['url'], ('lzma' in k)))
                            t.start(), threads.append(t)
                    for t in threads: t.join()
            show_snack_bar(f"{version.value} 下载完成！")
            download.value = 1
        upd()
    p.window_height = p.window_min_height = p.window_max_height = \
        p.window_width = p.window_min_width = p.window_max_width = 400
    TitleBar = fleter.HeaderBar(p, True, False, True, False, "LI JRE Helper", "left")
    TitleBar.controls.insert(1, fleter.SwitchThemeButton(p)), p.add(TitleBar)
    folder = TextField(
        label = "JRE 下载目录", hint_text = "保存 JRE 路径", read_only = True, 
        on_focus = lambda _: picker.get_directory_path(),
        border = flet.InputBorder.UNDERLINE, filled = True
    )
    p.add(folder)
    picker = flet.FilePicker(on_result = change); p.overlay.extend([picker])
    vers = get(DOWNLOAD_URL).json()["windows-x64"]
    version = flet.Dropdown(
        label = "版本", hint_text = "您需要配置的 JRE 版本？", filled = True,
        options = [flet.dropdown.Option(f"{v['version']['name']}({ver})") for ver in vers for v in vers[ver]] 
    )
    p.add(version)
    p.banner = flet.Banner(
        bgcolor = colors.AMBER_100, content = Text(""), actions = [TextButton("关闭", on_click = close)],
        leading = Icon(icons.WARNING_AMBER_ROUNDED, color = colors.AMBER, size = 40)
    )
    p.snack_bar = flet.SnackBar(content = Text(""))
    p.add(flet.FloatingActionButton(icon = icons.DOWNLOAD_SHARP, bgcolor = colors.BLUE_ACCENT, on_click = download))
    download = flet.ProgressBar(visible = False, value = 0); p.add(download)
flet.app(target = app)
