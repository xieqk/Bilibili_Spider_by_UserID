# Bilibili_Spider_by_UserID

Python 爬取B站（bilibili.com）UP主的所有视频链接及详细信息

博客：[https://blog.xieqiaokang.com/posts/36033.html](https://blog.xieqiaokang.com/posts/36033.html)

# 环境准备

- selenium
- bs4

### 安装

这里使用 conda 安装，也可使用 pip

```bash
conda install selenium bs4
```

selenium是一个操作浏览器的 Python 库，**需要安装相应的浏览器驱动**，如 firefox：

```bash
conda install gtk3 firefox -c conda-forge
```

此外还需要 `geckodriver` ，可前往 github 下载，并放置于 `/usr/local/bin/`：

- mozilla/geckodriver：[https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases)

> - 也可以放置在自定义路径下（但须为环境变量能够找到的地方），如非管理员用户可放置于自己 home 目录下的 `~/bin` 目录下，并将该路径添加进环境变量：
>
> ```bash
> export PATH=~/bin${PATH:+:${PATH}}
> ```
>
> 如果需要永久将 `~/bin` 路径添加进环境变量，则将上述语句添加进 `~/.bashrc` 文件末尾即可（重启命令行生效，或手动输入`source ~/.bashrc` 在当前命令行激活）。
>
> - Windows 需下载对应 windows 版本并放置于环境变量能够找到的地方，或手动将 `geckodriver` 所在路径加入 `PATH` 中，并重启。



# 快速使用

### 1. 安装依赖

见上一节环境准备部分，安装对应依赖环境。

### 2. Clone 代码

```python
# Github (国内访问网速不佳者可使用 Gitee)
git clone https://github.com/xieqk/Bilibili_Spider_by_UserID.git
# Gitee
git clone https://gitee.com/xieqk/Bilibili_Spider_by_UserID.git
```

### 3. 查看 B 站用户  uid

如下图所示，进入该用户主页，地址栏后面红框中的数字即为该用户的 `uid`。

![产看用户uid](https://cdn.jsdelivr.net/gh/xieqk/blog-cdn@master/imgs/image-20201118162506657.png#pic_center)

### 4. 爬取用户视频数据

进入代码目录中，直接执行 `main.py`，传入 `uid` 参数即可：

```bash
python main.py --uid 362548791
```

爬取结果将保存于当前目录下的 `json` 目录，以 `json` 格式保存，为一个列表，内容如下：

```json
[
    {
        "user_name": "歪西歪小哥哥",	// UP主名字
        "bv": "BV1Wa4y1e7yy",	// BV号
        "url": "https://www.bilibili.com/video/BV1Wa4y1e7yy",	// 视频链接
        "title": "【新冠肺炎:全球各国+中美各省/州】累计确诊人数 & 累计死亡人数数据可视化：俄罗斯情况不容乐观",	// 标题
        "play": "3888",		// 播放量
        "duration": 796,	// 总时长
        "pub_date": "2020-05-16",	// 发布日期
        "now": "2020-11-18 15:47:28"	// 当前日期
    },
    ...
]
```

### 5. 其它参数

- **--save_dir**：保存 json 结果的目录，默认为 `json`。
- **--save_by_page**：按页保存用户视频信息，默认为 `False`（B站用户视频页一页一般为30个视频）。
- **--time**：爬取时，浏览器获取页面的等待时间，默认为 `2`（秒）。网络状况不佳时等待时间过短可能会导致爬取的数据不完全。
- **--detailed**：进一步爬取每一个链接的详细信息（弹幕数、是否为播放列表、发布日期及时刻、，默认为 `False`。

当加入 `--detailed` 参数后每个 url 的爬取结果为：

```json
[
    {
        "user_name": "歪西歪小哥哥",
        "bv": "BV1Wa4y1e7yy",
        "url": "https://www.bilibili.com/video/BV1Wa4y1e7yy",
        "title": "【新冠肺炎:全球各国+中美各省/州】累计确诊人数 & 累计死亡人数数据可视化：俄罗斯情况不容乐观",
        "play": "3888",
        "duration": 796,
        "pub_date": "2020-05-16 02:17:16",	// 发布日期精确到时分秒
        "now": "2020-11-18 15:47:28",
        "danmu": "85",
        "type": "playlist",		// 链接类型：'video'代表单个视频，'playlist'代表播放列表
        "num": 4	// 分P数，如果为'video'则为1，'playlist'则为播放列表的视频集数
    },
    ...
]
```
