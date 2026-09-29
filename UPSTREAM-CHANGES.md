# UPSTREAM-CHANGES.md — 相对上游差异登记簿

> 配套文档：[AGENTS.md](AGENTS.md)
> 维护铁律：任何插件的**新增 / 更新 / 删除**，以及任何会改变插件集合的脚本改动，
> 都必须在同一批次内登记到本文件，并同步更新 `AGENTS.md` 第 4 节。详见 [AGENTS.md](AGENTS.md) 第 8 节。

---

## 一、这份文档解决什么问题

本仓库是上游的 fork，长期会被改造（换插件、改版本、加预置文件）。
一旦上游继续演进，就必须能回答三个问题：

1. **从哪一点开始偏离了上游？** —— 由第三节"同步基准"回答。
2. **哪些文件被改过、为什么改？** —— 由第五、六节回答。
3. **合并上游时遇到冲突，该保留谁？** —— 由第六节的"变更原因"与"同步动作"回答。

一句话：**这份文档是冲突时的裁判依据，不是装饰**。

本 fork 的改造遵循一条原则：**能"新增"就不"修改"，能"开关"就不"删除"**。
因此这里登记的绝大多数改动都是"纯新增"（新增文件、文件末尾追加），冲突风险普遍为低。

---

## 二、上游与分叉关系

| 角色 | 地址 | 说明 |
| --- | --- | --- |
| upstream（上游） | <https://github.com/chenmozhijin/OpenWrt-K> | 差异比较的基准，只读参考 |
| origin（本仓库） | <https://github.com/vizaxe/OpenWrt-K> | 实际推送目标 |
| 本地 main | —— | 当前与上游同一提交，本地改动尚未提交 |

上游分支情况：`main`（主线）、`v25.12.0`（版本特性分支）。

---

## 三、同步基准（Baseline）

| 项目 | 值 |
| --- | --- |
| 上游 main 提交 | `67e01a23777cd486afb8b5c38e1fe0ab15367806` |
| 基准记录日期 | 2026-09-28 |
| 本地 main 提交 | `67e01a23777cd486afb8b5c38e1fe0ab15367806`（与上游一致，尚无本地独有提交） |
| 编译基准 OpenWrt 版本 | `v25.12.5`（x86_64 与 rpi4b 一致） |
| `config/OpenWrt.config` 启用目标 | `x86_64` |
| 拓展包清单 | `config/{default-,x86_64/,rpi4b/}…extpackages.config`（三份逐字节一致，各 37 项 = 上游 33 项 + 本地新增 4 项） |
| 本地排除清单 | `config/{x86_64,rpi4b}/OpenWrt-K/local.config`（本地新增文件，两份内容一致；当前排除 13 个拓展包与 80 个配置开关） |

> **每完成一次上游合并，必须刷新本节的"上游 main 提交"与"基准记录日期"。**
> 本节是判断"从哪一点开始偏离"的唯一依据，过期就等于账簿失效。

---

## 四、当前差异总览

| 层面 | 是否有差异 | 说明 |
| --- | --- | --- |
| 提交历史 | ❌ 无 | 本地 main 与上游 main 指向同一提交 `67e01a2` |
| 已提交的本地改动 | ❌ 无 | 尚无本地独有提交 |
| 工作区未提交改动 | ⚠️ 有 | 改动：`config/**`、`build_helper/prepare.py`、`README.md`、`.gitignore`；新增未跟踪：`AGENTS.md`、`UPSTREAM-CHANGES.md`、`config/{x86_64,rpi4b}/OpenWrt-K/local.config`、`build_helper/utils/local_exclude.py` |
| 插件清单差异 | ✅ 有 | 新增 EasyTier 与 ddns-go 两组（UC-0001 / UC-0002）；tailscale、旧 DDNS、qBittorrent 链、passwall 家族与 OpenClash 由排除清单关闭（UC-0003 / UC-0004 / UC-0006）；UC-0016 恢复了被 `netdata` 依赖的 `protobuf-compat`；UC-0017 补入 mosdns（`[38]`）并把 ddns-go 的启用开关补齐到 x86_64 |
| 预置文件 / 补丁差异 | ✅ 有 | `files/` 新增本地透明代理相关文件（nft 规则、启停脚本、xray 运行身份与 uci 配置），并删除 passwall / OpenClash 专属预置；`patches/` 仍为上游原样 |

**结论**：插件集合相对上游已定制，但**没有删除任何上游内容**——
所有差异都是"新增文件 + 文件内追加"，因此合并上游时冲突面最小。
需要注意的反而是：上游若在 `extpackages.config` 末尾继续追加条目，可能有行级冲突；
若上游动了 `prepare.py::parse_configs()` 的出口，需要把排除清单的钩子重新接上。

---

## 五、差异索引表

| 编号 | 日期 | 类型 | 对象 | 涉及文件 | 冲突风险 | 同步动作 |
| --- | --- | --- | --- | --- | --- | --- |
| UC-0001 | 2026-09-28 | 新增插件 | easytier（`[36]`）、luci-app-easytier（`[37]`） | `config/*/OpenWrt-K/extpackages.config`、`config/{x86_64,rpi4b}/luci.config`、`config/{x86_64,rpi4b}/network.config`、`build_helper/prepare.py`、`README.md` | 低 | 保留本地条目与 `version.mk` 复制逻辑 |
| UC-0002 | 2026-09-28 | 新增插件 | ddns-go（`[35]`）、luci-app-ddns-go（`[34]`）（x86_64 的启用开关由 UC-0017 补齐） | `config/*/OpenWrt-K/extpackages.config`、`config/rpi4b/luci.config`、`config/rpi4b/network.config`、`build_helper/prepare.py`、`README.md` | 低 | 保留本地条目与 golang 引用修补逻辑 |
| UC-0003 | 2026-09-28 | 脚本改动 | 本地排除清单机制：`local.config` + `local_exclude.py` + `prepare.py` 钩子 | `config/{x86_64,rpi4b}/OpenWrt-K/local.config`（新增）、`build_helper/utils/local_exclude.py`（新增）、`build_helper/prepare.py` | 低 | 保留本地机制；上游若重写 `parse_configs()`，把出口处的排除循环接回 |
| UC-0004 | 2026-09-28 | 配置改动 | 排除清单内容：tailscale 组合、旧 DDNS 方案、qBittorrent 及 Qt6 / libtorrent / boost 链（9 个拓展包 + 31 个开关；其中 `protobuf-compat` 已于 UC-0016 恢复） | `config/{x86_64,rpi4b}/OpenWrt-K/local.config` | 低 | 保留；被排除项的上游声明保持原样，不做删除 |
| UC-0005 | 2026-09-28 | 脚本改动 | `prepare.py` 的 Makefile 引用修补扩展（`golang-package.mk`） | `build_helper/prepare.py` | 低 | 保留（纯新增 2 行） |
| UC-0006 | 2026-09-28 | 配置改动 | 排除清单新增：passwall / passwall2 / OpenClash 及其代理生态（4 个拓展包 + 49 个配置开关） | `config/{x86_64,rpi4b}/OpenWrt-K/local.config` | 低 | 保留；上游条目与开关保持原样 |
| UC-0007 | 2026-09-28 | 预置文件 | 本地 xray 透明代理方案：`kmod-nft-tproxy`、官方 feed 的 `xray-core`、nft 规则与启停脚本、xray 运行身份 | `config/{x86_64,rpi4b}/{kmod,network}.config`、`files/etc/nftables.d/`、`files/etc/init.d/xray`、`files/etc/uci-defaults/zzz-xray-user`、`files/etc/config/xray`、`files/usr/bin/{start,stop}-tproxy` | 中 | 保留本地文件与开关；上游无同名文件 |
| UC-0008 | 2026-09-28 | 配置改动 | x86_64 默认 LAN 地址对齐为 `192.168.2.1`（rpi4b 上游本就是 2.1）；工具脚本与 uci-defaults 占位行同步 | `config/x86_64/OpenWrt-K/openwrtext.config`、`config_build_tool.sh`、`files/etc/uci-defaults/zzz-chenmozhijin` | 低 | 保留本地值 |
| UC-0009 | 2026-09-28 | 配置改动 | AdGuardHome 工作目录与配置路径迁移到 `/etc/adguardhome`（缓存目录搬家 + 构建期下载路径同步） | `files/etc/uci-defaults/zzz-chenmozhijin`、`files/etc/adguardhome/data/`（自 `files/usr/bin/AdGuardHome/data/` 迁移）、`files/etc/adguardhome/AdGuardHome.yaml`（自 `files/etc/AdGuardHome.yaml` 迁移）、`build_helper/prepare.py` | 低 | 保留本地路径 |
| UC-0010 | 2026-09-28 | 预置文件 | AdGuardHome 主配置按使用环境调整（上游接 SmartDNS、启用缓存与 DoH、替换订阅源） | `files/etc/adguardhome/AdGuardHome.yaml` | 中 | 保留本地取值；上游改动该文件时人工比对 |
| UC-0011 | 2026-09-28 | 配置改动 | AdGuardHome 改用官方 openwrt 方案（官方 `luci-app-adguardhome` + `adguardhome` 守护进程包），放弃第三方实现 | `config/{x86_64,rpi4b}/{OpenWrt-K/local.config,network.config}`、`files/etc/uci-defaults/zzz-chenmozhijin`、`files/etc/adguardhome/adguardhome.yaml`、`build_helper/prepare.py` | 中 | 保留本地配置；上游若也切到官方实现，本条可撤销 |
| UC-0012 | 2026-09-28 | 预置文件 | 把 AdGuardHome 的 uci-defaults 逻辑从 `zzz-chenmozhijin` 拆成独立文件 | `files/etc/uci-defaults/zzz-adguardhome`（新增）、`files/etc/uci-defaults/zzz-chenmozhijin` | 低 | 保留拆分 |
| UC-0013 | 2026-09-28 | 配置改动 | DNS 分流器由 SmartDNS 换为 mosdns（不装 LuCI 界面、配置由使用者自备 YAML；SmartDNS 的上游行原样保留，关闭语义集中在 local.config）。⚠️ 当时误以为官方 feed 自带 mosdns，实际没有 —— 包源由 UC-0017 补齐 | `config/{x86_64,rpi4b}/network.config`（仅新增 mosdns 行）、`config/{x86_64,rpi4b}/OpenWrt-K/local.config`（关闭 SmartDNS 开关）、`files/etc/uci-defaults/zzz-chenmozhijin`、`files/etc/uci-defaults/zzz-adguardhome`、`files/etc/mosdns/config.yaml`（使用者提供）、`files/etc/uci-defaults/zzz-mosdns`、`build_helper/prepare.py`、`README.md`、`AGENTS.md` | 低 | 保留本地选择；上游若同样切换到 mosdns，本条可撤销 |
| UC-0014 | 2026-09-29 | 配置改动 | 加入 nginx（自管配置，仅用于自定义端口反向代理内网服务；不接管 LuCI、不占 80/443） | `config/{x86_64,rpi4b}/network.config`（仅新增 3 行）、`files/etc/nginx/nginx.conf`、`files/etc/uci-defaults/zzz-nginx`、`AGENTS.md` | 低 | 保留本地选择 |
| UC-0015 | 2026-09-29 | 配置改动 | 升级 Go 工具链分支 25.x → 26.x，适配官方 `adguardhome` 包 `go.mod` 的 `go >= 1.26.3` 要求 | `config/{x86_64,rpi4b}/OpenWrt-K/openwrtext.config` | 低 | 保留本地取值；上游若同步升级可撤销 |
| UC-0016 | 2026-09-29 | 配置改动 | 恢复 `protobuf-compat`：immortalwrt 版 `netdata` 硬依赖它，排除后 `make package/install` 失败 | `config/{x86_64,rpi4b}/OpenWrt-K/local.config`、`AGENTS.md` | 低 | 保留；被排除项的上游声明仍未改动 |
| UC-0017 | 2026-09-29 | 新增插件 | mosdns（`[38]`，取自 immortalwrt/packages `net/mosdns`）；并把 ddns-go 的启用开关补到 x86_64 | `config/{x86_64,rpi4b}/OpenWrt-K/extpackages.config`、`config/default-extpackages.config`、`config/x86_64/network.config`、`config/x86_64/luci.config`、`README.md`、`AGENTS.md` | 低 | 保留本地条目与开关 |
| UC-0018 | 2026-09-29 | 预置文件 | 修复 xray 透明代理自环：`xray_output` 补 `meta mark 0xff` 让路、`mark` 移到 `tproxy` 之后、DIVERT 链限定 TCP、删除永不命中的 `myip` / `vps` 空集合、日志降级；并补登 `files/etc/xray/config.json` | `files/etc/nftables.d/xray.nft`、`files/etc/xray/config.json`、`files/etc/config/xray`、`AGENTS.md` | 中 | 保留本地修复；上游无同名文件，`xray-core` 与其 init 的改动须人工比对 |
| UC-0019 | 2026-09-29 | 预置文件 | 构建期下载 xray geodata（Loyalsoldier 数据集：`geoip.dat` + `geosite.dat`）到 `/usr/share/xray/`，补齐 UC-0018 遗留的"分流数据缺失"缺口；URL 用 `releases/latest/download`（跟随最新，不加锁版本） | `build_helper/prepare.py`、`AGENTS.md` | 低 | 保留本地下载任务；上游若自带 geodata 下载逻辑，需人工比对其数据源与目标路径 |

> 编号规则：`UC-####` 起顺序递增，**永不复用、永不重排**；撤销的条目保留行并标注"已撤销 + 日期 + 原因"。

### 列含义

| 列 | 填写要求 |
| --- | --- |
| 编号 | `UC-####`，顺序递增 |
| 日期 | 改动落地日期，格式 `YYYY-MM-DD` |
| 类型 | 新增插件 / 更新插件 / 删除插件 / 脚本改动 / 配置改动 / 预置文件 / 补丁 |
| 对象 | 具体插件名、包名或机制名 |
| 涉及文件 | 仓库相对路径，多个用 `、` 分隔 |
| 冲突风险 | 低 / 中 / 高，分级标准见 [AGENTS.md](AGENTS.md) 第 9 节 |
| 同步动作 | 合并上游时该怎么做 |

---

## 六、条目详情

### UC-0001 · 新增插件 · easytier、luci-app-easytier

- 日期：2026-09-28
- 变更类型：新增插件
- 涉及文件：
  - config/x86_64/OpenWrt-K/extpackages.config
  - config/rpi4b/OpenWrt-K/extpackages.config
  - config/default-extpackages.config
  - config/x86_64/luci.config、config/rpi4b/luci.config
  - config/x86_64/network.config、config/rpi4b/network.config
  - build_helper/prepare.py
  - README.md
- 上游对照：上游无此条目，也没有对应开关
- 本地行为：
  - 在 `extpackages.config` **末尾追加** `[36]="easytier"`（路径 `easytier`）与 `[37]="luci-app-easytier"`（路径 `luci-app-easytier`），来源均为 `https://github.com/EasyTier/luci-app-easytier` 默认分支；
  - 两个目标启用 `CONFIG_PACKAGE_easytier=y`、`CONFIG_PACKAGE_luci-app-easytier=y`、`CONFIG_PACKAGE_luci-i18n-easytier-zh-cn=y`；
  - `prepare.py` 追加（新增 9 行）：遇到该仓库时把仓库根的 `version.mk` 复制到 `package/cmzj_packages/version.mk`；
  - README 内置功能列表加入 `luci-app-easytier`。
- 变更原因：
  - 原组网方案（tailscale 组合）需要替换，改用 EasyTier；
  - `luci-app-easytier` 的 `LUCI_DEPENDS` 只含 `kmod-tun` 与 `luci-compat`，**不含本体**，因此 `easytier` 必须显式声明，否则 LuCI 界面缺少 `/usr/bin/easytier` 无法工作；
  - 两个包的 Makefile 都用 `-include ../version.mk` 取版本号，复制到 `package/cmzj_packages/<包名>/` 后该文件不在，会静默回退到 Makefile 内置版本（形成两处版本来源），故补一份到 `cmzj_packages/` 根。
- 冲突风险：低 —— 条目追加在 `extpackages.config` 末尾，开关插在上游行的相邻位置
- 上游同步动作：保留本地条目与 `version.mk` 复制逻辑
- 文档同步：AGENTS.md 第 3.2、3.3、4.1 节已更新 ☑
- 相关提交：——

### UC-0002 · 新增插件 · ddns-go、luci-app-ddns-go

- 日期：2026-09-28
- 变更类型：新增插件
- 涉及文件：
  - config/x86_64/OpenWrt-K/extpackages.config
  - config/rpi4b/OpenWrt-K/extpackages.config
  - config/default-extpackages.config
  - config/rpi4b/luci.config
  - config/rpi4b/network.config
  - build_helper/prepare.py
  - README.md
- 上游对照：上游无此两个包；OpenWrt 官方 `openwrt/packages`、`openwrt/luci` 亦均无，只有 immortalwrt 提供
- 本地行为：
  - 在 `extpackages.config` **末尾追加** `[34]="luci-app-ddns-go"`（immortalwrt/luci，`applications/luci-app-ddns-go`）与 `[35]="ddns-go"`（immortalwrt/packages，`net/ddns-go`）；
  - 仅 rpi4b 启用 `CONFIG_PACKAGE_ddns-go=y`、`CONFIG_PACKAGE_luci-app-ddns-go=y`、`CONFIG_PACKAGE_luci-i18n-ddns-go-zh-cn=y`（x86_64 当时漏配，已于 UC-0017 补齐同一组开关）；
  - README 内置功能列表加入 `luci-app-ddns-go`。
- 变更原因：
  - 取代旧的 ddns-scripts 方案（见 UC-0004）；
  - `ddns-go` 的 Makefile 用 `include ../../lang/golang/golang-package.mk` 引用 feed 内的 golang 构建脚本，包被复制到 `package/cmzj_packages/` 后该相对路径失效，必须改写为 `$(TOPDIR)` 路径（见 UC-0005）。
- 冲突风险：低 —— 纯末尾追加 + 相邻插入
- 上游同步动作：保留本地条目与 golang 引用修补逻辑
- 文档同步：AGENTS.md 第 3.1、4.1 节已更新 ☑
- 相关提交：——

### UC-0003 · 脚本改动 · 本地排除清单机制

- 日期：2026-09-28
- 变更类型：脚本改动
- 涉及文件：
  - config/x86_64/OpenWrt-K/local.config（新增）
  - config/rpi4b/OpenWrt-K/local.config（新增）
  - build_helper/utils/local_exclude.py（新增）
  - build_helper/prepare.py（新增 8 行：1 行导入 + `parse_configs()` 出口 7 行过滤逻辑，**0 删除**）
  - AGENTS.md
- 上游对照：上游无 `local.config`、无 `local_exclude.py`，`parse_configs()` 出口处没有排除步骤
- 本地行为：
  - 在 `parse_configs()` 出口读取可选的 `local.config`；
  - `extpackages_exclude`：按 `NAME` 精确匹配，命中者从拓展包字典中剔除 —— 既不克隆、也不复制源码，自然不进固件；
  - `configs_exclude`：按配置符号名匹配（支持 fnmatch 通配），命中者从拼接后的配置文本中整行剔除，兼容 `CONFIG_X=y` 与 `# CONFIG_X is not set`；
  - 清单支持单行多值、同名键累加、行尾注释三种写法；
  - 文件缺失 / 键缺失 / 键留空都视为"不排除任何内容"，行为与上游完全一致。
- 变更原因：此前若要下线某个上游插件，必须删除上游条目与开关，每次合并上游都会在同一区域冲突。
  把"要排除什么"收进一个**上游不存在的文件**并按清单过滤后，本地差异收敛为"新增文件 + 纯新增行"。
- 冲突风险：低 —— `prepare.py` 只新增，不删除；两个新增文件上游不存在
- 上游同步动作：保留本地机制；若上游重写 `parse_configs()`，把出口处的排除循环接回去即可
- 文档同步：AGENTS.md 第 1、2、3.3、7、10 节已更新 ☑
- 相关提交：——

### UC-0004 · 配置改动 · 排除清单的内容

- 日期：2026-09-28
- 变更类型：配置改动
- 涉及文件：
  - config/x86_64/OpenWrt-K/local.config
  - config/rpi4b/OpenWrt-K/local.config
- 上游对照：这些包与开关在上游 `extpackages.config`、各目标 `*.config` 中**全部保持原样**，本地一个都没有删除
- 本地行为：清单里排除以下内容（共 9 个拓展包 + 31 个配置符号；其中 `protobuf-compat` 已于 UC-0016 恢复，理由见该条）：
  - tailscale 组合：`tailscale`、`luci-app-tailscale-community`，以及它们的 4 个开关；
  - 旧 DDNS 方案：`ddns-scripts_aliyun`，以及 rpi4b 上的 `ddns-scripts`、`ddns-scripts-cloudflare`、`ddns-scripts-dnspod`、`ddns-scripts-services`、`luci-app-ddns` 与 3 个 `luci-i18n-ddns-*`；
  - qBittorrent 及其构建链：`luci-app-qbittorrent`、`qBittorrent-Enhanced-Edition`、`qt6base`、`qt6tools`、`libdouble-conversion`，以及界面开关、Qt6 运行时、`libtorrent-rasterbar` 与 boost 系列。~~`protobuf-compat`~~ 已于 UC-0016 恢复（它其实由 `netdata` 依赖，不属于本条要下线的 qt6 链）。
  - 注意：`configs_exclude` 刻意**逐条精确列出**，不使用 `luci-i18n-ddns-*` 这类通配，以免误伤本地新增的 `luci-i18n-ddns-go-zh-cn`。
- 变更原因：这三组是本次定制的对象 —— tailscale / ddns-scripts 被新方案取代，qBittorrent 链整体下线。用清单表达可使上游文件保持原样。
- 冲突风险：低 —— 只改本地新增文件
- 上游同步动作：保留；若上游新增了这些包的依赖项，把新符号补进 `configs_exclude`
- 文档同步：AGENTS.md 第 4.1 节（`✗` 图例与状态列）已更新 ☑
- 相关提交：——

### UC-0005 · 脚本改动 · `prepare.py` 的 Makefile 引用修补扩展

- 日期：2026-09-28
- 变更类型：脚本改动
- 涉及文件：
  - build_helper/prepare.py（新增 3 行：2 行注释 + 1 行 `replace`，**0 删除**）
- 上游对照：上游此处只改写 `../../luci.mk`，没有处理 golang 构建脚本的引用
- 本地行为：在处理拓展包源码时，额外把 `../../lang/golang/golang-package.mk` 改写为 `$(TOPDIR)/feeds/packages/lang/golang/golang-package.mk`
- 变更原因：`ddns-go`（UC-0002）的 Makefile 用相对路径引用 feed 内的 golang 构建脚本，包被复制到 `package/cmzj_packages/ddns-go/` 后该路径指向不存在的位置，编译阶段会直接报找不到文件
- 冲突风险：低 —— 上游原注释、原日志行保持原样，本地只是在同一循环里多追加一次 `replace`
- 上游同步动作：保留；若上游重写了这段循环，把新增的 `replace` 行补回即可
- 文档同步：AGENTS.md 第 3.1 节已更新 ☑
- 相关提交：——


### UC-0006 · 配置改动 · 排除 passwall / passwall2 / OpenClash 生态

- 日期：2026-09-28
- 变更类型：配置改动
- 涉及文件：
  - config/x86_64/OpenWrt-K/local.config
  - config/rpi4b/OpenWrt-K/local.config
- 上游对照：这些包与开关在上游 `extpackages.config`、各目标 `*.config` 中**全部保持原样**，本地一个都没有删除
- 本地行为：清单新增 4 条 `extpackages_exclude`（`luci-app-passwall`、`openwrt-passwall-packages`、`passwall2`、`luci-app-openclash`）与 49 条 `configs_exclude`：
  - 三个界面及其全部子选项、两个语言包；
  - 代理核心与工具：`sing-box`、`hysteria`、`naiveproxy`、`brook`、`microsocks`、`simple-obfs`、`shadowsocks-libev-*`、`shadowsocks-rust-*`、`shadowsocksr-libev-*`、`trojan-go`、`trojan-plus`、`tuic-client`、`v2ray-plugin`、`xray-plugin`、`v2ray-geoip`、`v2ray-geosite`、`dns2socks`、`dns2tcp`、`ipt2socks`、`chinadns-ng`、`haproxy`；
  - OpenClash 专属运行时：`ruby` 与 `ruby-*`、`libruby`、`CONFIG_RUBY_ENABLE_YJIT`、`bash`、`unzip`；
  - 仅代理使用过的内核模块：`kmod-inet-diag`、`kmod-ipt-*` 系列、`kmod-nf-ipt` / `kmod-nf-ipt6`、`ipset`、`libipset`；
  - iptables 用户态：`iptables-nft`、`iptables-mod-ipopt`（防火墙走 `firewall4` + nftables 原生语法；`kmod-nft-compat` 作为内核兼容层保留）。
  - **例外**：`CONFIG_PACKAGE_xray-core` 明确不在排除之列（见 UC-0007）。
- 变更原因：代理方案改为「官方 `xray-core` + 自写 nft 片段 + tproxy」，不再需要 passwall / OpenClash 生成规则；这些包与开关留着会编进固件（部分在官方 feed 里）或产生未知符号告警。
- 冲突风险：低 —— 只改本地新增文件
- 上游同步动作：保留；若上游给这些包新增依赖，把新符号补进 `configs_exclude`
- 文档同步：AGENTS.md 第 3.4、4.1 节已更新 ☑
- 相关提交：——

### UC-0007 · 预置文件 · 本地 xray 透明代理方案

- 日期：2026-09-28
- 变更类型：预置文件
- 涉及文件：
  - config/x86_64/kmod.config、config/rpi4b/kmod.config（各 +1 行：`kmod-nft-tproxy=y`）
  - config/x86_64/network.config、config/rpi4b/network.config（各 +1 行：`xray-core=y`，取自官方 feed）
  - files/etc/nftables.d/xray.nft、cn_ipv4.conf、cn_ipv6.conf（本地 nft 规则片段）
  - files/usr/bin/start-tproxy、stop-tproxy（启停脚本）
  - files/etc/init.d/xray（覆盖官方 init）
  - files/etc/uci-defaults/zzz-xray-user（创建运行身份）
  - files/etc/config/xray（uci 配置：enabled=1 + confdir）
  - 同时删除：files/etc/uci-defaults/zzz-chenmozhijin-passwall、files/usr/share/passwall/、files/etc/openclash/
- 上游对照：上游既没有这些文件，也没有对应的 kmod 开关；`xray-core` 上游本就从官方 feed 提供
- 本地行为：
  - `kmod.config` 补 `CONFIG_PACKAGE_kmod-nft-tproxy=y` —— 自写规则的 `tproxy` 表达式需要它，而清掉 passwall / OpenClash 后已无人拉取（`firewall4` 只拉 core/fib/offload/nat）；`kmod-nft-socket` 早已显式启用，对应规则里的 `socket transparent`；
  - `xray-core` 改从**官方 openwrt/packages** 启用（版本与 passwall-packages 同为 26.9.9 一系，且自带 `/etc/init.d/xray` 与 `/etc/config/xray`）；
  - nft 规则放在 `files/etc/nftables.d/`，由 `firewall4` 自动 include 进 `table inet fw4`；
  - xray 运行身份为 uid 0 / gid 966：`zzz-xray-user` 首次开机创建，覆盖版 `init.d/xray` 用 `procd_set_param user/group` 切过去，使规则里的 `meta skgid 966` 生效（放过 xray 自身出站，避免与 tproxy 规则互相抓取）；
  - 启停脚本配置 `fwmark 0x11` 与本地路由表 100（v4）/106（v6），依赖 `ip-full`（已显式启用）。
- 变更原因：替代 passwall / OpenClash 的规则生成，实现"自写 nft + 官方 xray 核心"的透明代理；同时保证清理代理生态后 `/etc/nftables.d` 的规则仍能加载。
- 冲突风险：中 —— 覆盖了官方的 `/etc/init.d/xray`（上游若改该脚本，需人工比对合并）
- 上游同步动作：保留 `files/` 全部本地文件与两处开关；若上游 `xray-core` 的 init 或 uci 配置结构变化，重新对齐覆盖版脚本
- 文档同步：AGENTS.md 第 3.4、4.2、10 节已更新 ☑
- 相关提交：——


### UC-0008 · 配置改动 · x86_64 默认 LAN 地址对齐为 192.168.2.1

- 日期：2026-09-28
- 变更类型：配置改动
- 涉及文件：
  - config/x86_64/OpenWrt-K/openwrtext.config
  - config_build_tool.sh
  - files/etc/uci-defaults/zzz-chenmozhijin（占位行同步）
- 上游对照：上游两个目标的默认地址本来就不一致 —— `rpi4b/openwrtext.config` 是 `192.168.2.1`，`x86_64/openwrtext.config` 是 `192.168.1.1`。本地把 x86_64 对齐到 2.1
- 本地行为：
  - `config/x86_64/OpenWrt-K/openwrtext.config` 的 `ipaddr` 改为 `192.168.2.1`（`rpi4b` 已是该值，无需改动）；
  - `config_build_tool.sh` 三处同步：下载配置缺少 `ipaddr` 键时的兜底值、菜单「恢复默认配置」写入的值、以及「修改IP地址」输入框的提示文案；
  - `files/etc/uci-defaults/zzz-chenmozhijin` 里的 `uci set network.lan.ipaddr=...` 也同步为 `192.168.2.1`。该行本是占位符 —— `prepare.py` 在构建时会用配置里的 `ipaddr` 覆写它（见 `prepare.py` 中匹配 `uci set network.lan.ipaddr=` 的分支），功能上不改也正确；本地仍改，是作为"覆写失效"时的兜底：该覆写依赖 `startswith` 精确匹配，一旦上游改变这一行的写法就会静默失效。
- 变更原因：两个编译目标的默认地址不一致会让人误判；且 `192.168.1.1` 常与光猫管理地址冲突。
- 冲突风险：低 —— 配置键单行改动；工具脚本处均为字面量
- 上游同步动作：保留本地值；若上游把两个目标统一，按上游取值即可
- 文档同步：本条即登记 ☑（AGENTS.md 未记载默认 IP，无需变动）
- 相关提交：——


### UC-0009 · 配置改动 · AdGuardHome 工作目录与配置路径迁移到 /etc/adguardhome

- 日期：2026-09-28
- 变更类型：配置改动
- 涉及文件：
  - files/etc/uci-defaults/zzz-chenmozhijin（新增 workdir / backupwdpath 两项）
  - files/etc/adguardhome/data/（自 files/usr/bin/AdGuardHome/data/ 整体迁移，20 个订阅缓存文件）
  - files/etc/adguardhome/AdGuardHome.yaml（自 files/etc/AdGuardHome.yaml 迁移，内容为使用者已调整的版本，见 UC-0010）
  - build_helper/prepare.py（下载目标路径调整 + 二进制目录补建）
  - AGENTS.md（第 4.2 节预置表）
- 上游对照：插件的 `workdir` 默认是 `/usr/bin/AdGuardHome`（`luci-app-adguardhome` 的 init 脚本里 `config_get workdir $CONFIGURATION workdir "/usr/bin/AdGuardHome"`），上游未做改动
- 本地行为：
  - `uci-defaults` 的 AdGuardHome 段新增 `workdir='/etc/adguardhome'`、`configpath='/etc/adguardhome/AdGuardHome.yaml'` 与 `backupwdpath='/etc/adguardhome'`（后两者与工作目录同值，等同上游"工作目录与备份目录同值"的默认模式）；
  - 订阅缓存目录随之从 `files/usr/bin/AdGuardHome/data/` 迁到 `files/etc/adguardhome/data/`，用 `git mv` 保留文件历史；
  - `prepare.py` 的 `adg_filters_path` 同步改为 `files/etc/adguardhome/data/filters`；
  - `prepare.py` 在写入 AdGuardHome 二进制前补了一句 `os.makedirs(..., exist_ok=True)`：原 `data` 是 `/usr/bin/AdGuardHome/` 下唯一的子目录，迁走后该目录不再存在于仓库，而二进制仍要写到这里；
  - **未改动**：`binpath` 仍为 `/usr/bin/AdGuardHome/AdGuardHome` —— 该选项必须是二进制**文件**路径（init 中有 `[ ! -f "$binpath" ]` 判定与 `procd_set_param command $binpath`），指向目录会导致服务无法启动；`files/etc/AdGuardHome-dnslist(by cmzj).yaml` 仍留在 `/etc/`（当前主配置已清空对它的引用）。
- 变更原因：按使用者要求把 AdGuardHome 的运行数据集中到 `/etc/adguardhome`。
- 冲突风险：低 —— `uci-defaults` 与 `files/` 均为本地预置文件；`prepare.py` 仅改一行路径、新增一行建目录
- 上游同步动作：保留本地路径；若上游调整 `luci-app-adguardhome` 的目录语义（例如新增其它目录选项），重新对齐
- 后续变更：**已被 UC-0011 取代** —— AdGuardHome 改用官方方案，本条的工作目录 / 配置路径定制与二进制下载路径同步不再适用（作为历史保留）
- 注意事项：插件的"跨系统升级保留"由 `upprotect` 选项写进 `/lib/upgrade/keep.d/luci-app-adguardhome` 控制；本地**未设置**该选项，因此 `/etc/adguardhome` 不会随 sysupgrade 自动保留。需要保留时设置 `AdGuardHome.AdGuardHome.upprotect='/etc/adguardhome'` 即可。
- 文档同步：AGENTS.md 第 4.2 节已更新 ☑
- 相关提交：——


### UC-0010 · 预置文件 · AdGuardHome 主配置按使用环境调整

- 日期：2026-09-28
- 变更类型：预置文件
- 涉及文件：
  - files/etc/adguardhome/AdGuardHome.yaml（原 files/etc/AdGuardHome.yaml，随 UC-0009 一并迁移）
- 上游对照：相对上游在 HEAD 中的预置版本（244 行），当前版本为 249 行，差异为 +92 / -87 行
- 本地行为（相对上游预置内容）：
  - DNS 上游改接 SmartDNS：`upstream_dns` 由 `223.5.5.5` 改为 `tcp://127.0.0.1:5335`；`upstream_mode` 由 `parallel` 改为 `load_balance`；`fallback_dns` 补入 `223.5.5.5`；
  - 清空 `upstream_dns_file`（上游预置值指向 `/etc/AdGuardHome-dnslist(by cmzj).yaml`）；
  - 启用 DNS 缓存：新增 `cache_enabled`、`cache_size: 4194304`、`cache_ttl_min: 600`、`cache_optimistic` 及乐观缓存参数（上游预置中 `cache_size` 与 `cache_ttl_min` 为 0）；
  - 新增 DoH 配置段（`doh.routes`、`insecure_enabled`），并开启 `allow_unencrypted_doh`；
  - `refuse_any` 由 `false` 改为 `true`；`session_ttl` 由 `720h` 改为 `30d`；
  - 过滤器订阅列表整体替换（一批新的 URL 与 id）；
  - 规则更新间隔由 `168h` / `2160h` 统一为 `90d`，`ignored_enabled: false`。
- 变更原因：按使用者的实际部署调整（上游接 SmartDNS、启用缓存与 DoH、更换订阅来源）。
- 冲突风险：中 —— 该文件是本地预置内容，且改动面较大；上游若更新同一文件，冲突时以上游结构为准，再按上述清单重新套用本地取值
- 上游同步动作：保留本地取值；上游改动该文件时逐项比对
- 关联说明：由于订阅列表被替换，`files/etc/adguardhome/data/filters/` 下的 20 个预置缓存（7.7 MB）与当前 yaml 中的 filter id 已不对应，AdGuardHome 会重新下载所需的过滤器；这批缓存是否继续保留由使用者决定（`prepare.py` 当前仍在维护它们）。
- 文档同步：AGENTS.md 第 4.2 节已同步路径 ☑
- 后续变更：**已被 UC-0011 取代**（改用官方包后，主配置文件名与选项体系随官方方案变化；yaml 内容本身仍沿用）
- 链路变化：`upstream_dns` 的 `tcp://127.0.0.1:5335` 保持不变，但该端口上的服务已由 SmartDNS 换为 **mosdns**（见 UC-0013）
- 相关提交：——


### UC-0011 · 配置改动 · AdGuardHome 改用官方 openwrt 方案

- 日期：2026-09-28
- 变更类型：配置改动
- 涉及文件：
  - config/x86_64/OpenWrt-K/local.config、config/rpi4b/OpenWrt-K/local.config（排除扩展包 `luci-app-adguardhome`）
  - config/x86_64/network.config、config/rpi4b/network.config（新增 `CONFIG_PACKAGE_adguardhome=y`）
  - files/etc/uci-defaults/zzz-chenmozhijin（AdGuardHome 段按官方 uci 重写；删除第三方版专有的 chmod 行）
  - files/etc/adguardhome/AdGuardHome.yaml → adguardhome.yaml（改名）
  - build_helper/prepare.py（删除自下载二进制与解压逻辑，并清理失去用途的 `adg_arch` 变量）
  - AGENTS.md（第 4.1、4.2 节与验证清单）
- 上游对照：上游把 `luci-app-adguardhome` 作为**扩展包**引入（来源 `chenmozhijin/luci-app-adguardhome`）；OpenWrt 官方另有配套实现 —— `openwrt/packages` 的 `adguardhome`（守护进程，源码 Go 编译）+ `openwrt/luci` 的 `luci-app-adguardhome`（界面）。本地改为后者
- 本地行为：
  - `extpackages.config` 条目保持原样（仍为 [17]），仅在 `local.config` 中排除 → OpenWrt 的 feed 覆盖机制（`include/scan.awk`：本地包与 feed 同名时登记为 override、feed 那份不参与扫描）随之让**官方版**生效；
  - 新增 `CONFIG_PACKAGE_adguardhome=y`；界面与中文包开关沿用原有的 `luci-app-adguardhome` / `luci-i18n-adguardhome-zh-cn`；
  - `uci-defaults` 的 AdGuardHome 段按官方选项重写：`config_file=/etc/adguardhome/adguardhome.yaml`、`work_dir=/etc/adguardhome`、`user`/`group=adguardhome`、`verbose=0`，并补 `/etc/init.d/adguardhome enable`；
  - 官方版**没有**第三方版的 `redirect`（自动把 dnsmasq 上游指向 AdGuardHome），因此显式补上 `dhcp.@dnsmasq[0]` 的 `server=127.0.0.1#1745` + `noresolv=1`，维持原有链路 dnsmasq → AdGuardHome(1745) → SmartDNS(5335)；
  - 主配置按官方命名改为全小写 `adguardhome.yaml`（内容仍为使用者调整过的版本，见 UC-0010）；
  - `prepare.py` 删除 AdGuardHome 二进制下载与解压逻辑（改由包编译提供），并清理因此失去用途的 `adg_arch` 变量（13 处架构赋值）。
- 变更原因：改用官方维护的实现 —— 以 `adguardhome` 用户（853）运行、`capabilities` 限制（CAP_NET_BIND_SERVICE / CAP_NET_RAW）、procd jail、随包附带 sysctl 调优，安全性更好，且随官方 feed 演进。
- 与前序条目的关系：**取代 UC-0009 / UC-0010 的定制方案**（第三方版的 `workdir` / `configpath` 选项与自建二进制布局不再适用）。那两条作为历史保留。
- 冲突风险：中 —— `uci-defaults` 与两份目标配置均为本地改动；官方包若变更 uci 选项名需要跟进
- 上游同步动作：保留本地配置；若上游也切换到官方实现，本条可撤销
- 注意事项：
  - 官方默认 `work_dir` 是 `/var/lib/adguardhome`，本地按使用者意愿设为 `/etc/adguardhome`；若要与官方默认一致，改 `work_dir` 即可；
  - 官方方案**不支持在线更新核心**（init 带 `--no-check-update`），核心版本随 feed（当前锁定 commit 中为 0.107.76）；
  - `files/usr/share/cmzj/openwrt-k_tool.sh` 中"更新 AdGuardHome 上游 DNS 分流规则"仍指向 `/etc/AdGuardHome-dnslist(by cmzj).yaml`；官方版在 jail 内默认看不到该路径，如需使用要加 `jail_mount`（当前主配置已清空 `upstream_dns_file`，不受影响）。
- 文档同步：AGENTS.md 第 4.1、4.2 节已更新 ☑
- 相关提交：——


### UC-0012 · 预置文件 · uci-defaults 拆分出 zzz-adguardhome

- 日期：2026-09-28
- 变更类型：预置文件
- 涉及文件：
  - files/etc/uci-defaults/zzz-adguardhome（新增，43 行）
  - files/etc/uci-defaults/zzz-chenmozhijin（移除 AdGuardHome 段，342 → 323 行）
- 上游对照：上游只有 `zzz-chenmozhijin` 一个文件，AdGuardHome 段内含其中
- 本地行为：
  - 把 AdGuardHome 的首次开机配置（官方 uci 选项、服务 `enable`、dnsmasq 上游指向）拆到 `zzz-adguardhome`；
  - 新文件**自带** `has_package()` 定义与"等待包数据库就绪"的循环，不依赖 `zzz-chenmozhijin`，可独立存在与删除；
  - `zzz-chenmozhijin` 相应删除该段，其余内容（LAN 地址、SmartDNS、dnsmasq 缓存、aria2、OpenClash 等）不变。
- 变更原因：`zzz-chenmozhijin` 已混合 SmartDNS、aria2、OpenClash、dnsmasq 等多摊配置，不利于维护；拆分后 AdGuardHome 相关逻辑独立成文件，将来不用时整文件删除即可。
- 冲突风险：低 —— 新增独立文件；`zzz-chenmozhijin` 一侧只是"删除一段"
- 上游同步动作：保留拆分；若上游重写 `zzz-chenmozhijin`，注意不要把 AdGuardHome 段又混回去
- 附带核对：`zzz-chenmozhijin` 的 dnsmasq 段只设置 `cachesize=0`（不碰 `server` / `noresolv`），且 `uci commit dhcp` 是合并式提交，因此与 `zzz-adguardhome` 设置的 dnsmasq 上游互不覆盖，两个文件的执行先后无影响（uci-defaults 按文件名排序，`zzz-adguardhome` 恰好排在 `zzz-chenmozhijin` 之前）。
- 文档同步：AGENTS.md 第 4.2 节已更新 ☑
- 相关提交：——


### UC-0013 · 配置改动 · DNS 分流器由 SmartDNS 换为 mosdns

- 日期：2026-09-28
- 变更类型：配置改动
- 涉及文件：
  - config/x86_64/network.config、config/rpi4b/network.config（**仅新增** `CONFIG_PACKAGE_mosdns=y`；上游的 `CONFIG_PACKAGE_smartdns=y` 原样保留）
  - config/x86_64/OpenWrt-K/local.config、config/rpi4b/OpenWrt-K/local.config（**新增 5 行 `configs_exclude`**，关闭 SmartDNS 本体、界面与语言包）
  - config/x86_64/luci.config、config/rpi4b/luci.config（**无改动**；上游的 `luci-app-smartdns` 与语言包行原样保留）
  - files/etc/uci-defaults/zzz-chenmozhijin（删除 SmartDNS 配置段，205 行）
  - files/etc/uci-defaults/zzz-adguardhome（链路注释 SmartDNS → mosdns）
  - files/etc/mosdns/config.yaml（**新增**，使用者提供的配置：UDP/TCP 监听 `:5335`、`http_server` 监听 `:8443`，含 hosts / 缓存 / 双栈 ECS / 域名分流 / DoT 上游）
  - files/etc/mosdns/domain_set/、files/etc/mosdns/ip_set/（**新增**，分流规则文本，共约 4 MB）
  - files/etc/uci-defaults/zzz-mosdns（**新增**，负责 `enable` + `restart`；mosdns 包的 postinst 会 stop + disable）
  - build_helper/prepare.py（删除 pymumu 源码克隆、feed 覆盖与 hash 跳过逻辑）
  - README.md、AGENTS.md
- 上游对照：上游自带 SmartDNS（`smartdns` + `luci-app-smartdns`），并在 `prepare.py` 中用 pymumu 上游 `master` 覆盖 feed、跳过下载 hash 校验；uci-defaults 中预置了一整套 SmartDNS 参数（含 20 个上游 DNS 服务器）
- 本地行为：
  - 上游配置文件**零修改**：`CONFIG_PACKAGE_smartdns=y`、`CONFIG_PACKAGE_luci-app-smartdns=y` 与语言包行全部保留在 `*.config` 中，关闭动作只由 `local.config` 的 `configs_exclude` 表达（与 tailscale 组合同一处理方式），两个目标配置文件相对上游**只有新增行、没有删除行**；
  - 分流器改为 **mosdns**；⚠️ 当时误认为"官方 feed 自带该包、经 feed 直接启用即可"，实际 `openwrt/packages` 的 `openwrt-25.12` 与 `master` 都没有 `net/mosdns`，于是 `CONFIG_PACKAGE_mosdns=y` 成了**未知符号**，被 `make defconfig` 悄悄丢弃 —— 编译成功、固件里却没有 mosdns。该缺陷已由 **UC-0017** 修复（补上扩展包声明，取自 immortalwrt/packages）；此处保留原记录以说明来龙去脉；
  - **不安装** `luci-app-mosdns`（使用者不需要界面，配置以 YAML 形式提供）；
  - 配置随固件落地：`files/etc/mosdns/config.yaml` 在构建期由 `files/` 覆盖包自带的默认配置（`prepare_rootfs` 先装包、后复制 `files/`），并由 `zzz-mosdns` 显式 `enable` + `restart`（否则包 postinst 的 disable 会让服务不自启）；
  - 删除 `zzz-chenmozhijin` 中的 SmartDNS 配置段（205 行），并删除 `prepare.py` 中 `pymumu/openwrt-smartdns`、`pymumu/luci-app-smartdns` 的克隆、feed 覆盖与 `disable_smartdns_hash_check` 函数；
  - `zzz-adguardhome` 的链路注释更新为 `dnsmasq → AdGuardHome(1745) → mosdns(5335)`。
- 变更原因：使用者在设备上已自备并在用 mosdns 的 YAML 配置，改为与之一致；同时精简仓库内不再需要的 SmartDNS 定制（pymumu 源码替换与 hash 跳过）。
- 冲突风险：低 —— 上游配置文件相对上游只新增行、无删除；关闭语义集中在本地新增的 `local.config`；`prepare.py` 一侧的删除属独立区域
- 上游同步动作：保留本地选择；若上游也切换到 mosdns，本条可撤销
- 注意事项：
  - mosdns 使用 YAML 配置（`/etc/mosdns/config.yaml`、`/etc/init.d/mosdns`，由包提供）；本仓库**已预置**使用者提供的配置与配套规则（`files/etc/mosdns/{config.yaml,domain_set/,ip_set/}`）；
  - 该配置**只使用官方 mosdns 插件**：原配置中的 `dual_stack_ecs_handler` 与 `network_interface` 属使用者自维护的 fork（`vizaxe/mosdns`）专属。前者的"按查询类型分别写 IPv4/IPv6 ECS"语义，已改用官方的 `ecs_handler` × 2 + `sequence` 按 `qtype` 分派实现（官方 `ecs_handler` 的 preset 仅接受单个 IP，且按 preset 族别而非查询类型决定 ECS family，其源码 `QuickSetupOldECS` 明确标注 dual-stack 写法已废弃）；后者随 `ddns_sq` 段一并删除。因此本仓库**无需引入 fork 版 mosdns**；
  - 规则数据以**文本文件**形式随配置落地（`domain_set/*.txt` 约 4 MB），**不依赖** `v2ray-geodata` 的 `/usr/share/v2ray/*.dat`，故无需把该包从排除清单中移出；
  - 链路依赖 mosdns 监听 **5335**；若改用其它端口，需同步修改 `files/etc/adguardhome/adguardhome.yaml` 的 `upstream_dns` 与 `zzz-adguardhome` 中的 dnsmasq 上游；
  - `files/usr/share/cmzj/openwrt-k_tool.sh` 中"更新 AdGuardHome 上游 DNS 分流规则"仍以 `has_package smartdns` 为条件，换用 mosdns 后该条件恒假、功能自动跳过（输出"未检测到…"），且该段内的 `/etc/init.d/AdGuardHome restart` 属旧服务名 —— 如需清理可另行删除该功能段；
  - 如需恢复 SmartDNS：删掉 `local.config` 中的那 5 行即可重新启用 feed 版；若要恢复成 pymumu 上游版本（并跳过下载 hash 校验），还需在 `prepare.py` 中恢复对应的克隆与替换逻辑（已随本条删除）；
  - 顺手清掉一处悬空配置：原 SmartDNS 段中的 `when_chnroute_default_dns='chinadns_ng'` 指向已被排除的 `chinadns-ng`（UC-0006），随本段删除一并消失。
- 文档同步：AGENTS.md 第 3.2 / 4.2 / 5 / 7 / 10 节已更新 ☑
- 相关提交：——


### UC-0014 · 配置改动 · 加入 nginx（自管配置，仅用于自定义端口反代）

- 日期：2026-09-29
- 变更类型：配置改动
- 涉及文件：
  - config/x86_64/network.config、config/rpi4b/network.config（**仅新增** `nginx-ssl`、`nginx-ssl-util`、`nginx-mod-stream` 三个开关）
  - files/etc/nginx/nginx.conf（**新增**，本地自管配置）
  - files/etc/uci-defaults/zzz-nginx（**新增**，关闭 uci 管理、清理残留、启用服务）
  - AGENTS.md
- 上游对照：上游不含 nginx（LuCI 由 uhttpd 承载），本仓库此前亦无
- 本地行为：
  - 启用 `nginx-ssl`（默认变体；反代所需编译期模块默认即为 y —— `NGINX_HTTP_PROXY`、`NGINX_HTTP_REWRITE`（并 `select NGINX_PCRE`）、`NGINX_HTTP_CACHE`、`NGINX_HTTP_V2`、`NGINX_HTTP_UPSTREAM_*` 等）、`nginx-ssl-util`（TLS 辅助工具）与 `nginx-mod-stream`（TCP/UDP 反代模块）；
  - **不接管 LuCI**：不启用 `luci-nginx` 与 `nginx-mod-luci`，`uhttpd` 保持原样；亦未启用 `nginx-mod-ubus`（它服务于 LuCI 集成，本用途不需要）；
  - **关闭 uci 管理**（`nginx.global.uci_enable=false`），使随固件预置的 `/etc/nginx/nginx.conf` 接管。依据：init 的 `nginx_init()` 按「`/etc/nginx/uci.conf` 存在则优先用它，否则用 `/etc/nginx/nginx.conf`」选择配置，而 `nginx-util` 的 `init_lan()` 仅在 `uci_enable=true` 时才生成 `/var/lib/nginx/uci.conf`（实测其源码：`if (config_enabled) { init_uci(...) }`）；
  - **不占用 80/443**：包自带的 UCI 默认值会生成 `server '_redirect2ssl'`（`listen 80`）与 `server '_lan'`（`listen 443 ssl default_server`），关闭 uci 管理后这两个 server 不再生成，避免与 `uhttpd` 争抢 80；
  - `zzz-nginx` 额外清理可能残留的 `/var/lib/nginx/uci.conf` 与 `/etc/nginx/uci.conf`（设备曾以 uci 模式运行过时的兜底，避免旧的 uci.conf 被优先选用）。
- 变更原因：使用者需要在自定义端口上反向代理内网服务（含 TCP/UDP），且明确不占用 80/443、不接管 LuCI。
- 冲突风险：低 —— 上游配置文件只新增行；`files/` 下均为独立新文件
- 上游同步动作：保留本地选择
- 注意事项：
  - 模块加载依赖自管配置里的 `include module.d/*.module;`（由 `nginx-mod-*` 包安装，例如 `stream.module` 内含 `load_module .../ngx_stream_module.so`）；缺少它会让 `stream {}` 报 unknown directive，**勿删**；
  - `pid /var/run/nginx.pid;` 必须与 init 脚本的 reload 判定保持一致（该脚本读取 `/var/run/nginx.pid`），**勿删**；
  - HTTP(S) 的 server 块放 `/etc/nginx/conf.d/*.conf`；TCP/UDP（stream）的 server 块放 `/etc/nginx/stream.d/*.conf`（该目录需自建；`stream` 只能位于顶层，不能写进 `http {}` 内）；
  - 自管模式不再有 UCI 的 `uci_manage_ssl='self-signed'` 自签逻辑，需要 HTTPS 反代时用 `nginx-ssl-util` 生成证书或自备证书；
  - nginx 包自带配置监听 80/443 属"包默认值"，本方案通过关闭 uci 管理使其失效；若日后重新打开 uci_enable，需自行改 `listen` 或删除那两个 server 段。
- 文档同步：AGENTS.md 第 4.2 节已更新 ☑
- 相关提交：——


### UC-0015 · 配置改动 · 升级 Go 工具链至 26.x（修复 adguardhome 构建失败）

- 日期：2026-09-29
- 变更类型：配置改动
- 涉及文件：
  - config/x86_64/OpenWrt-K/openwrtext.config（`golang_version=25.x` → `26.x`）
  - config/rpi4b/OpenWrt-K/openwrtext.config（同上）
- 上游对照：上游该键为 `25.x`
- 本地行为：`prepare.py` 用 `sbwml/packages_lang_golang` 的对应分支整体替换 `feeds/packages/lang/golang`；分支 `26.x` 提供 **Go 1.26.8**（该分支 `golang/Makefile` 中 `GO_VERSION_MAJOR_MINOR:=1.26`、`GO_VERSION_PATCH:=8`）。
- 变更原因：UC-0011 改用官方 `adguardhome` 包（**源码 Go 编译**）后，其 v0.107.76 的 `go.mod` 声明 `go 1.26.3`，而 `25.x` 分支提供的是 Go 1.25.14，导致 CI 构建失败：
  `go: ../../go.mod requires go >= 1.26.3 (running go 1.25.14; GOTOOLCHAIN=local)` →
  `package/feeds/packages/adguardhome failed to build`（`GOTOOLCHAIN=local` 禁止自动下载更高工具链）。抬到 26.x（Go 1.26.8）后满足要求。
- 冲突风险：低 —— 仅改一处版本号
- 上游同步动作：保留本地取值；若上游也升级到 26.x，本条可撤销
- 注意事项：
  - Go 1.x 保持向后兼容，仓库内其它 Go 包（`xray-core` / `mosdns` / `ddns-go` / `easytier` 等）不受影响；代价是构建时间增加（Go 工具链自身需重新编译）；
  - `sbwml/packages_lang_golang` 的分支命名形如 `NN.x`（`19.x` … `27.x`），**不是** `1.26` 这种写法；
  - 日后 AdGuardHome 上游若继续抬高 `go.mod` 要求，需同步把本键调到对应分支（`27.x` 等）；
  - 若 26.x 工具链本身构建异常，退路是放弃"源码编译官方包"、改回构建期下载 AdGuardHome 官方预编译二进制（UC-0009 的做法）；
  - `config_build_tool.sh` 内有两处 `22.x` 与该键相关（生成/重置配置时的默认值），不是当前生效值，未改动。
- 文档同步：AGENTS.md 无需改动（4.1 插件表与 3.2 特殊处理表均未变）☑
- 相关提交：——

### UC-0016 · 配置改动 · 恢复 `protobuf-compat`（修复 netdata 依赖缺失导致的构建失败）

- 日期：2026-09-29
- 变更类型：配置改动
- 涉及文件：
  - config/x86_64/OpenWrt-K/local.config（删掉 `extpackages_exclude=protobuf-compat` 一行，补上为什么不能排除的注释）
  - config/rpi4b/OpenWrt-K/local.config（同上）
  - AGENTS.md（第 4.1 节表格 `[33]` 状态列 + 已知情况说明）
- 上游对照：`extpackages.config` 中该条目（上游 `[33]`）自始至终**原样保留**，本地这次只是"不再排除"，不是新增声明
- 本地行为：`protobuf-compat` 重新参与克隆与复制，并由 `defconfig` 依据 `netdata` 的依赖**自动选中**；任何 `*.config` 里都没有也不需要写 `CONFIG_PACKAGE_protobuf-compat`
- 变更原因：UC-0004 把它与 qBittorrent 链一起排除后，CI 在 `make package/install` 阶段失败：
  `ERROR: unable to select packages: protobuf-compat (no such package): required by: netdata-1.38.1-r5[protobuf-compat]`。
  根因有两层：
  - `prepare.py::prepare_cfg()` 用 immortalwrt/packages 的 `admin/netdata` **覆盖**官方 feed 的同名包，而这一版（1.38.1-r5）的 Makefile 把 `+protobuf-compat` 与 `PKG_BUILD_DEPENDS:=protobuf-compat/host` 写成**必需依赖**（官方 25.12 的 netdata 1.33.1 并不需要 protobuf）；
  - 排除清单只能拦"扩展包要不要克隆"，拦不住依赖解析：`defconfig` 阶段仅打印
    `WARNING: Makefile 'package/feeds/packages/netdata/Makefile' has a dependency on 'protobuf-compat', which does not exist`（非致命，构建继续），
    直到安装软件包时 apk 才报 `no such package` 并终止。日志里同时出现的 `WARNING: your configuration is out of sync.` 是同一根因的伴生现象，不是第二个问题。
- 冲突风险：低 —— 只改本地新增文件与文档
- 上游同步动作：保留。它自身只依赖 `zlib` / `libatomic` / `libstdcpp` / `protobuf-compat-lite`，与 qt6 链无关，**不会**把已下线的 qBittorrent 相关包拉回来；若日后 `netdata` 覆盖逻辑被移除、或上游 feed 换掉这份依赖，可再把它写回排除清单
- 注意事项：
  - 代价是 host 与 target 各编译一次 protobuf 3.17.3（该包自带 `HostBuild`），固件体积约 +1.5 MB（`libprotobuf` / `libprotoc` / `libprotobuf-lite`）；
  - 安装段把兼容库从 `/usr/protobuf-compat/lib` 拷到 `/usr/lib`，与其他 protobuf 实现的库文件同名；当前配置没有选中会与之冲突的包，**不要**再额外选中同名的 protobuf 库包；
  - 它的语义是"依赖驱动"进入 `.config`，所以 AGENTS.md 第 4.1 节状态列记 `·`（未显式启用）而不是 `✔`。
- 文档同步：AGENTS.md 第 4.1 节已更新 ☑
- 相关提交：——

### UC-0017 · 新增插件 · mosdns（`[38]`）与 x86_64 的 ddns-go 开关

- 日期：2026-09-29
- 变更类型：新增插件 + 配置改动
- 涉及文件：
  - config/x86_64/OpenWrt-K/extpackages.config、config/rpi4b/OpenWrt-K/extpackages.config、config/default-extpackages.config（末尾追加 `[38]`）
  - config/x86_64/network.config（新增 `CONFIG_PACKAGE_ddns-go=y`）
  - config/x86_64/luci.config（新增 `CONFIG_PACKAGE_luci-app-ddns-go=y`、`CONFIG_PACKAGE_luci-i18n-ddns-go-zh-cn=y`）
  - README.md、AGENTS.md
- 上游对照：上游没有 `[38]` 条目；x86_64 的 `*.config` 上游不含 ddns-go 的三个开关（rpi4b 的那组由 UC-0002 已加）
- 本地行为：
  - `extpackages.config` 末尾追加 `EXT_PACKAGES_NAME[38]="mosdns"`，仓库 `https://github.com/immortalwrt/packages`、路径 `net/mosdns`、分支留空；UC-0013 写的 `CONFIG_PACKAGE_mosdns=y`（两个目标都有）由此才真正生效；
  - x86_64 补齐 ddns-go 的三个开关，与 rpi4b 对齐（分别插在字母序位置：`network.config` 的 IP Addresses and Names 段、`luci.config` 的 Applications 段与语言包段）。
- 变更原因（现象：编译成功，进入系统后发现 mosdns 与 ddns-go 都没装）：
  - **mosdns**：`openwrt/packages` 的 `openwrt-25.12`（本次编译的 `v25.12.5` 所属分支）与 `master` **都没有** `net/mosdns`（raw 请求 404，GitHub contents API 也确认 net 目录下无此包），只有 immortalwrt/packages 提供。于是 `CONFIG_PACKAGE_mosdns=y` 成了**未知符号**，`make defconfig` 只打印一句 WARNING 就把它丢掉，编译照常成功 —— 典型的静默失败；
  - **ddns-go**：x86_64 从来没有任何 ddns-go 开关（UC-0002 当时只加了 rpi4b），所以它不是"装丢了"，而是"没被要求装"。本次按使用者要求补上本体 + LuCI 界面 + 中文语言包。
- 冲突风险：低 —— 三个 `extpackages.config` 均为末尾追加；x86_64 的 `*.config` 为字母序相邻插入
- 上游同步动作：保留。若日后官方 feed 收录 `net/mosdns`，可改回"官方 feed 直接启用"，并把 `[38]` 条目写进排除清单
- 注意事项：
  - mosdns 的 Makefile 用 `include ../../lang/golang/golang-package.mk`，复制到 `package/cmzj_packages/mosdns/` 后由 `prepare.py` 的**通用改写**（UC-0005）修正为 `$(TOPDIR)` 路径，无需额外脚本；它声明 `PKG_BUILD_DEPENDS:=golang/host`，走 UC-0015 的 Go 26.x 工具链；
  - 官方 feed 没有同名 `mosdns` 包，因此**不需要**在 `prepare.py` 里先 `rmtree` feed 同名目录；
  - 包自带 `/etc/mosdns/config.yaml`，构建期由 `files/etc/mosdns/config.yaml` 覆盖（`prepare_rootfs` 先装包、后复制 `files/`），与 UC-0013 一致；
  - 版本为 immortalwrt 的 `mosdns 5.3.3`（默认分支，未钉版本）；日后上游配置语法变动时，需要同步核对本地 `config.yaml`；
  - 该包 postinst 会 `stop` + `disable`，服务自启仍依赖 `files/etc/uci-defaults/zzz-mosdns`（UC-0013）。
- 文档同步：AGENTS.md 第 3.1、4.1、4.2 节与 README.md 已更新 ☑
- 相关提交：——

### UC-0018 · 预置文件 · 修复 xray 透明代理自环（mark 时序 / 0xff 让路 / DIVERT 收窄 / 清理空集合）

- 日期：2026-09-29
- 变更类型：预置文件（含配置改动）
- 涉及文件：
  - files/etc/nftables.d/xray.nft（**核心修复**）
  - files/etc/xray/config.json（日志降级 `debug` → `warning`、`dnsLog: false`）
  - files/etc/config/xray（注释订正：主配置已随固件预置，端口 65535 与 nft 强耦合）
  - AGENTS.md
- 上游对照：上游没有这些文件（UC-0007 引入），因此本条只修本地实现，不涉及上游内容
- 现象（设备实测）：部分流量"出不去"——不是丢包，而是**在 nftables 链与内核路由之间循环**，始终无法出站；随后 xray 进程内存从几十 MB 一路涨到接近 2 GB，整机网络明显变差
- 根因（两处缺陷叠加，均已在源码层面证实）：
  - **让路缺了一处**：xray 出站套接字带 `SO_MARK 255`（`config.json` 各出站 `sockopt.mark`），本应被 `xray_prerouting` 首条的 `meta mark 0xff accept` 与 `xray_output` 的 `meta skgid 966 accept` 放过。但 `xray_output` **没有** `meta mark 0xff` 这一条，一旦 skgid 失配（`/etc/init.d/xray` 不在包 conffiles 里，运行时升级 / 重装 `xray-core` 会被官方 init 覆盖，而官方 init 完全没有 `procd_set_param user/group`，xray 便以 gid/fsgid 0 运行），包会一路落到链尾的 `mark set 0x11`，**把 255 改写成 0x11** → 命中 `ip rule fwmark 0x11 table 100` 的 `local default dev lo` → 经 `lo` 回到 prerouting → 被 `tproxy` 当成新连接投递给 xray 自己 → xray 再开出站 → 无限自环（每轮回一圈多一套连接 / 协程 / 套接字，内存随之涨到 GB 级）；
  - **mark 写在了 `tproxy` 之前**：内核 `nft_tproxy_eval` 找不到透明套接字时置 `NFT_BREAK`（后续语句含 `counter`/`accept` 全部跳过），但**已写入的 mark 不回滚**。于是任何 tproxy 未命中的包仍带 `fwmark 0x11` 进 `table 100`，被 `local dev lo` 送到本地却没有套接字接收 —— 静默黑洞（入站端口不一致、未监听该协议族时最典型）。
- 本地行为（本次改动）：
  - `xray_output` 链首新增 `meta mark 0xff counter accept comment "Xray出站(SO_MARK 255)"`，排在 `meta skgid 966` **之前** —— 让防自环不再依赖 gid；`skgid 966` 保留为兜底；
  - `xray_prerouting` 的两条规则改为 `tproxy ip/ip6 to :65535 meta mark set 0x11 counter accept`，**mark 移到 `tproxy` 之后**（与官方 TProxy 教程 `tproxy … meta mark set 1` 的写法一致）：tproxy 成功才打标，失败包保留原标记、按正常路由转发（**由"静默黑洞"变为"直连放行"**，可用性提高但该流量不再经过代理，属有意的取向选择）；
  - `xray_divert` 链首新增 `meta mark 0xff counter accept`（该链优先级 `mangle -10` = -160，早于 `xray_prerouting`，而 nftables 的 `accept` 只结束当前基链、不阻止同钩子的其它基链 —— 不先让过 0xff 就会把主保护悄悄抹掉）；规则收窄为 `meta l4proto tcp socket transparent 1 …`，与官方 `-p tcp -m socket` 的 DIVERT 语义对齐：UDP 侧 xray 会为每个目标地址建一个绑在目标地址上的 FakeUDP 透明套接字，`socket transparent` 会对它自己发出的包命中，是回路的放大器；
  - 删除 `myip` / `myip6` / `vps` / `vps6` 四个空集合及配套 4 条 `ip daddr @… accept` 规则：仓库内**没有任何地方填充它们**（构建期、开机脚本、hotplug 均无），永远为空的集合让这几条直连规则永不命中，只在排障时误导人以为"VPS 已放行"。xray 出站的放行已由 `SO_MARK 255` 全链路承担，比按 IP 放行更可靠（IP 与解析结果都会变）。文件内保留注释与运行时 `nft add element` 的恢复示例；
  - `config.json` 日志降级：`loglevel: debug` + `dnsLog: true` 在自环时会变成日志放大器（procd 经管道转发 logd），改回 `warning` / `false`；
  - `files/etc/config/xray` 注释订正：主配置**已随固件预置**（原注释写"需自备"），并写明入站 65535 与 nft 里 `tproxy … to :65535` 的强耦合关系。
- 变更原因：修复设备上真实发生的自环与黑洞；同时把三处让路、mark 时序、端口耦合这些"静默失效"知识固化进文件注释与 AGENTS.md，避免下次靠猜。
- 冲突风险：中 —— 全部为本地文件，上游不会碰到；风险来自语义：`xray_output` 的规则顺序与 `tproxy` 语句顺序都是**功能性约束**，不可"顺手重排"；`/etc/init.d/xray` 与官方包同名，上游或包更新该文件时需人工比对
- 上游同步动作：保留本地修复。若上游日后也提供 tproxy 预置，需人工比对 `xray.nft` 的三条链与 `config.json` 的端口 / mark 取值
- 注意事项：
  - **排障顺序**：怀疑自环时先跑 `/usr/bin/stop-tproxy`（移除 `ip rule` 与本地路由，回路立刻断；代价是暂时全走直连），**不要只停 xray** —— 路由表还在时，未命中的包会按本文档的缺陷静默黑洞；
  - **v6 无需额外入站**：`listen: "0.0.0.0"` 在 Go 里是通配地址，`favoriteAddrFamily()` 会建成 **AF_INET6 双栈**套接字（`IPv4zero` 在 `ipToSockaddrInet6()` 中被换成 `IPv6zero`），v4 与 v6 的透明套接字查找都能命中它；改成 `"::"` 会变 v6-only 并打断 v4，**不要改**；
  - **确认 xray 真实身份**：`grep Gid /proc/$(pidof xray)/status` 的第 4 个字段即 fsgid，不是 966 就说明本地覆盖版 init 已失效（`meta skgid` 取的是套接字 `file->f_cred->fsgid`；`setgid()` 会同步 fsgid，所以覆盖版 init 在场时本应等于 966）；
  - 遗留未处理（本次未纳入范围）：`config/<目标>/OpenWrt-K/local.config` 排除了 `v2ray-geosite` / `v2ray-geoip`，而官方 `xray-core` 包**并不依赖**它们（`DEPENDS:=$(GO_ARCH_DEPENDS) +ca-bundle`），但 `files/etc/xray/config.json` 的路由规则大量使用 `geosite:*` / `geoip:*`。若固件内没有这两份数据，规则会整体失效、gfw 域名单掉到末条 `direct` 直连 —— 需单独确认与决断。
- 文档同步：AGENTS.md 第 3.4 / 4.2 节已更新 ☑
- 相关提交：——

### UC-0019 · 预置文件 · 构建期下载 xray geodata（Loyalsoldier 数据集）

- 日期：2026-09-29
- 变更类型：预置文件（`prepare.py` 新增下载任务）
- 涉及文件：
  - build_helper/prepare.py（在 AdGuardHome 下载任务之后追加两个 `dl2` 任务）
  - AGENTS.md
- 上游对照：上游在 `prepare()` 的下载段落里没有该任务，也没有"必须使用 Loyalsoldier 数据集"这一约定
- 本地行为：
  - 在 `prepare()` 的下载段落中新增 `xray_asset_path = workdir/files/usr/share/xray`，从 `https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/` 下载 `geoip.dat`（约 15.9 MiB）与 `geosite.dat`（约 10.5 MiB）；
  - 产物先落入 `workdir/files/`，随后由既有逻辑（`prepare_cfg()` 的 `copytree(global_files_path, openwrt/files)`）并入各目标 rootfs，固件内路径为 `/usr/share/xray/`；
  - 目录与文件名由 xray 侧约定：`/etc/config/xray` 的 `datadir` 与覆盖版 init 的 `XRAY_LOCATION_ASSET` 都指向 `/usr/share/xray`，xray 只认该目录下的 `geoip.dat` / `geosite.dat`，因此**未改动任何 xray 配置**；
  - 版本策略：URL 使用 `releases/latest/download`，由 GitHub 重定向到最新 tag —— **有意不锁版本**，每次编译取最新数据（同一提交的两次编译产物可能不同）；
  - 与排除清单保持互斥：`CONFIG_PACKAGE_v2ray-geoip` / `v2ray-geosite` 仍留在 `local.config` 的排除项中，避免"包安装的文件"与"预置文件"争同一路径。
- 变更原因：
  - UC-0018 已记录遗留缺口：`v2ray-geoip` / `v2ray-geosite` 被排除，而 `files/etc/xray/config.json` 依赖 `geosite:category-ads-all` / `gfw` / `github` / `google` 与 `geoip:facebook` / `google` / `netflix` / `telegram` / `twitter`，数据缺失时这些规则整体落空、gfw 域名只剩链尾 `direct` 直连；
  - 官方 `xray-core`（openwrt-25.12 分支，版本 26.3.27）只安装二进制、`/etc/xray/config.json.example`、`/etc/config/xray` 与 init，**不提供任何 geodata**，缺口只能由外部数据补齐；
  - 选 Loyalsoldier 而非官方 feed 的 `v2ray-geodata`：后者数据源为 v2fly，实测（解包 geoip.dat / dlc.dat 读取类别表）其 geoip 仅含国家代码与 `PRIVATE` / `TEST` / `ZZ`（**没有** `facebook` / `google` / `netflix` / `telegram` / `twitter`），geosite 也没有 `gfw` 类别（对应物是 `greatfire`），直接换上会让本仓库的上述规则全部失效；Loyalsoldier 版这些类别齐全，`config.json` 一行都不用改，体积 15.86 + 10.46 = 26.3 MiB，也小于 v2fly 组合（22.25 + 2.19 = 24.4 MiB 中真正可用的部分）。
- 冲突风险：低 —— 仅在上游 `prepare()` 下载段落末尾追加，`files/usr/share/xray/` 也是上游没有的目录
- 上游同步动作：保留本地下载任务；若上游日后自带 geodata 下载逻辑，需人工比对其数据源（v2fly / Loyalsoldier）与目标路径后再决定是否拆除本地任务
- 注意事项：
  - 下载失败会让 `wait_dl_tasks()` 抛错、**整个 prepare 阶段失败**（fail-fast，与 AdGuardHome 段保持一致）；
  - 这两个文件不在任何包的 conffiles 中，opkg / apk 不感知、也不参与包升级，sysupgrade 时随新固件覆盖；
  - `.gitignore` 未忽略 `workdir/`，本地执行 prepare 后工作区会出现约 26 MiB 未跟踪文件（本次未处理，需要时再补忽略规则）；
  - 固件体积：x86_64 与 rpi4b 均增加约 26.3 MiB。
- 文档同步：AGENTS.md 第 3.4 / 4.2 节已更新 ☑
- 相关提交：——

### 新增条目模板

```markdown
### UC-000X · <类型> · <对象>

- 日期：
- 变更类型：
- 涉及文件：
  -
- 上游对照：
- 本地行为：
- 变更原因：
- 冲突风险：<低/中/高> —— <理由>
- 上游同步动作：
- 文档同步：AGENTS.md 第 <章节> 已更新 ☐
- 相关提交：——
```

---

## 七、上游同步操作流程

> ⚠️ 涉及远程仓库与分支的操作（`remote add`、`fetch`、`merge`、`rebase`、`push`）
> 均属于**需要用户确认**的操作，不得自行执行。

1. **清点本地**
   `git status` 确认没有未提交的临时改动；若有，先妥善处理。
2. **通读账簿**
   打开本文件第五节，明确"我方动过哪些文件"。
3. **确认上游远程**
   `git remote -v` 检查是否已配置 `upstream`；
   若无：`git remote add upstream https://github.com/chenmozhijin/OpenWrt-K.git`。
4. **拉取**
   `git fetch upstream`
5. **预览差异**
   `git log --oneline HEAD..upstream/main`
   `git diff HEAD upstream/main --stat`
6. **合并**
   `git merge upstream/main`（使用 merge 还是 rebase 由用户决定）。
7. **处理冲突**
   - 凡在第五节登记过的文件，冲突时**默认保留本地意图**；
   - 再逐条评估上游改动是否值得吸收（尤其是上游对 `prepare.py`、`extpackages.config` 的整段重写）；
   - 拿不准时回到第六节读"变更原因"，不要凭直觉删掉本地改动。
8. **合并后复核清单**

   | 检查项 | 为什么 |
   | --- | --- |
   | `config/*/OpenWrt-K/extpackages.config` | 容易被上游整段替换，本地末尾追加的 4 个条目会静默丢失 |
   | `config/*/OpenWrt-K/local.config` | 上游不会有此文件，出现即说明被误删或误建 |
   | `config/*/luci.config` 等目标配置 | 上游会持续增删开关 |
   | `build_helper/prepare.py` | 添加的排除钩子、Makefile 引用修补、`version.mk` 复制都在此，冲突风险最高 |
   | `build_helper/utils/local_exclude.py` | 本地新增文件，上游不会有 |
   | `files/` 预置文件 | 上游可能删除或改写同名文件 |
   | `patches/` | 上游可能已内置等价修复 |

9. **刷新账簿**
   更新第三节的"上游 main 提交"与"日期"；在第五节逐条标注本次同步动作的结果。
10. **触发验证**
    推送后由 CI 验证。注意触发路径只含 `.github/**`、`files/**`、`build_helper/**`、`config/**`，
    纯文档改动不会触发构建，需要时用 `workflow_dispatch` 手动跑。

---

## 八、维护规则

| 时机 | 必须做的事 |
| --- | --- |
| 新增 / 更新 / 删除插件 | 第五节加行 + 第六节加详情 + `AGENTS.md` 第 4 节同步 |
| 改 `local.config` 的排除内容 | 同上，并在 `AGENTS.md` 第 4.1 节更新状态列 |
| 改 `prepare.py` 的特殊处理 | 同上，并在"变更原因"里写清失败现象 |
| 改 `files/` 预置或 `patches/` | 同上 |
| 完成一次上游合并 | 刷新第三节基准 + 更新第五节"同步动作"结果 |
| 撤销某条本地改动 | 该条目保留，行尾标注"已撤销 + 日期 + 原因"，**不得删行** |

编号永不复用，顺序永不重排 —— 因为提交历史里的引用会指向编号。

---

## 九、类型速查

| 类型 | 何时使用 | 典型冲突风险 |
| --- | --- | --- |
| 新增插件 | 引入上游没有的包 | 低 |
| 更新插件 | 换仓库 / 路径 / 分支 / 名称 | 低～中 |
| 删除插件 | 从 `extpackages.config` 中移除条目（注意：多数情况应改用 `local.config` 排除） | 低～中 |
| 脚本改动 | 改 `build_helper/` 下的逻辑 | 中～高 |
| 配置改动 | 改目标 `*.config`、`compile.config`、`local.config` | 中（改 `local.config` 为低） |
| 预置文件 | 改 `files/` 下内容 | 中 |
| 补丁 | 改 `patches/` 或补丁调用逻辑 | 中～高 |
