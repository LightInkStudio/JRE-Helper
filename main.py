import flet, fleter, lzma, os, re, requests, threading
def build(page: flet.Page):
    # 窗口大小
    page.window_height = \
        page.window_min_height = \
            page.window_max_height = 400
    page.window_width = \
        page.window_min_width = \
            page.window_max_width = 400
    
    # 标题栏
    TitleBar = fleter.HeaderBar(
        page, 
        True, 
        False, 
        True, 
        False, 
        "JRE Helper", 
        "left"
    )
    TitleBar.controls.insert(1, fleter.SwitchThemeButton(page))
    page.add(TitleBar)
    
    # 选择路径        
    folder = flet.TextField(
        label = "JRE 下载目录", 
        hint_text = "保存 JRE 路径", 
        read_only = True, 
        on_focus = lambda _: picker.get_directory_path(),
        border = flet.InputBorder.UNDERLINE,
        filled = True,
    )
    page.add(folder)
    def change(e):
        folder.value = e.path if e.path else ""    
        page.update()
    picker = flet.FilePicker(on_result = change)
    page.overlay.extend([picker])
    
    # 版本
    vers = requests.get(
        "https://bmclapi2.bangbang93.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json",
        headers = {
            "user-agent": "Chrome/114.5.1.4"
        }
    ).json()["windows-x64"]
    version = flet.Dropdown(
        label = "版本",
        hint_text = "您需要配置的 JRE 版本？",
        options = [],
        filled = True
    )
    for ver in vers:
        for v in vers[ver]:
            version.options.append(flet.dropdown.Option(v['version']['name'] + '(' + ver + ')'))
    page.add(version)
    
    # 警告栏
    def close(_):
        page.banner.open = False
        page.update()
    page.banner = flet.Banner(
        bgcolor = flet.colors.AMBER_100,
        leading = flet.Icon(flet.icons.WARNING_AMBER_ROUNDED, color = flet.colors.AMBER, size = 40),
        content = flet.Text("您还未选择下载文件夹或 JRE 版本。"),
        actions = [
            flet.TextButton("关闭", on_click = close),
        ],
    )
    page.snack_bar = flet.SnackBar(content = flet.Text(""))
    
    # 下载按钮
    def download(_):
        if folder.value == '':
            page.banner.content = flet.Text("请选择保存目录")
            page.banner.open = True
        elif version.value == None :
            page.banner.content = flet.Text("请选择 JRE 版本")
            page.banner.open = True
        else:
            page.snack_bar.content = flet.Text(f"开始下载 {version.value}")
            page.snack_bar.bgcolor = flet.colors.GREEN
            page.snack_bar.open = True
            page.update()
            # 开始下载
            tmp_ver = re.search(r'\((.*?)\)', version.value).group(1)
            download.visible = True
            page.update()
            for i in vers[tmp_ver]:
                if i['version']['name'] == version.value.replace(tmp_ver, "").replace("()", ""):
                    # 开始操作，就下这个
                    download.value = None
                    page.update()
                    try: 
                        manifest = requests.get(
                            i['manifest']['url'].replace(
                                "piston-meta.mojang.com",
                                "bmclapi2.bangbang93.com"
                            ),
                            headers = {
                                "user-agent": "Chrome/114.5.1.4"
                            }
                        ).json()['files']
                    except: exit(0)
                    directory = folder.value
                    download.value = 0
                    page.update()
                    pool = len(manifest)
                    threads = []
                    def down(name, url, lz = False):
                        try:
                            buffer = requests.get(
								url.replace(
									"piston-meta.mojang.com",
									"bmclapi2.bangbang93.com"
								),
								headers = {
									"user-agent": "Chrome/114.5.1.4"
								}
							).content
                        except: down(name, url, lz)
                        else: 
                            download.value += 1 / pool
                            page.update()
                        open(os.path.join(directory, name), 'wb').write(buffer if not lz else lzma.decompress(buffer))
                    for f in manifest:
                        if manifest[f]['type'] == 'directory':
                            try: os.mkdir(os.path.join(directory, f))
                            except: pass
                        else:
                            try: lz = manifest[f]['downloads']['lzma']
                            except:
                                thr = threading.Thread(
                                    target = down,
                                    args = (f, manifest[f]['downloads']['raw']['url'], False)
								)
                            else:
                                thr = threading.Thread(
                                    target = down,
                                    args = (f, manifest[f]['downloads']['lzma']['url'], True)
                                )
                            thr.start()
                            threads.append(thr)
                    for t in threads:
                        t.join()
            page.snack_bar.content = flet.Text(f"{version.value} 下载完成！")
            page.snack_bar.bgcolor = flet.colors.GREEN
            page.snack_bar.open = True
            download.value = 1
        page.update()
        
    page.add(flet.FloatingActionButton(
        icon = flet.icons.DOWNLOAD_SHARP,
        bgcolor = flet.colors.BLUE_ACCENT,
        on_click = download
    ))
    
    # 下载进度条
    download = flet.ProgressBar(visible = False, value = 0)
    page.add(download)
    
    page.update()
flet.app(target = build)
