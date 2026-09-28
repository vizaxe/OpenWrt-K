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
| 插件清单差异 | ✅ 有 | 新增 EasyTier 与 ddns-go 两组（UC-0001 / UC-0002）；tailscale、旧 DDNS、qBittorrent 链、passwall 家族与 OpenClash 由排除清单关闭（UC-0003 / UC-0004 / UC-0006） |
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
| UC-0002 | 2026-09-28 | 新增插件 | ddns-go（`[35]`）、luci-app-ddns-go（`[34]`） | `config/*/OpenWrt-K/extpackages.config`、`config/rpi4b/luci.config`、`config/rpi4b/network.config`、`build_helper/prepare.py`、`README.md` | 低 | 保留本地条目与 golang 引用修补逻辑 |
| UC-0003 | 2026-09-28 | 脚本改动 | 本地排除清单机制：`local.config` + `local_exclude.py` + `prepare.py` 钩子 | `config/{x86_64,rpi4b}/OpenWrt-K/local.config`（新增）、`build_helper/utils/local_exclude.py`（新增）、`build_helper/prepare.py` | 低 | 保留本地机制；上游若重写 `parse_configs()`，把出口处的排除循环接回 |
| UC-0004 | 2026-09-28 | 配置改动 | 排除清单内容：tailscale 组合、旧 DDNS 方案、qBittorrent 及 Qt6 / libtorrent / boost 链（9 个拓展包 + 31 个开关） | `config/{x86_64,rpi4b}/OpenWrt-K/local.config` | 低 | 保留；被排除项的上游声明保持原样，不做删除 |
| UC-0005 | 2026-09-28 | 脚本改动 | `prepare.py` 的 Makefile 引用修补扩展（`golang-package.mk`） | `build_helper/prepare.py` | 低 | 保留（纯新增 2 行） |
| UC-0006 | 2026-09-28 | 配置改动 | 排除清单新增：passwall / passwall2 / OpenClash 及其代理生态（4 个拓展包 + 49 个配置开关） | `config/{x86_64,rpi4b}/OpenWrt-K/local.config` | 低 | 保留；上游条目与开关保持原样 |
| UC-0007 | 2026-09-28 | 预置文件 | 本地 xray 透明代理方案：`kmod-nft-tproxy`、官方 feed 的 `xray-core`、nft 规则与启停脚本、xray 运行身份 | `config/{x86_64,rpi4b}/{kmod,network}.config`、`files/etc/nftables.d/`、`files/etc/init.d/xray`、`files/etc/uci-defaults/zzz-xray-user`、`files/etc/config/xray`、`files/usr/bin/{start,stop}-tproxy` | 中 | 保留本地文件与开关；上游无同名文件 |
| UC-0008 | 2026-09-28 | 配置改动 | x86_64 默认 LAN 地址对齐为 `192.168.2.1`（rpi4b 上游本就是 2.1）；工具脚本与 uci-defaults 占位行同步 | `config/x86_64/OpenWrt-K/openwrtext.config`、`config_build_tool.sh`、`files/etc/uci-defaults/zzz-chenmozhijin` | 低 | 保留本地值 |
| UC-0009 | 2026-09-28 | 配置改动 | AdGuardHome 工作目录与配置路径迁移到 `/etc/adguardhome`（缓存目录搬家 + 构建期下载路径同步） | `files/etc/uci-defaults/zzz-chenmozhijin`、`files/etc/adguardhome/data/`（自 `files/usr/bin/AdGuardHome/data/` 迁移）、`files/etc/adguardhome/AdGuardHome.yaml`（自 `files/etc/AdGuardHome.yaml` 迁移）、`build_helper/prepare.py` | 低 | 保留本地路径 |
| UC-0010 | 2026-09-28 | 预置文件 | AdGuardHome 主配置按使用环境调整（上游接 SmartDNS、启用缓存与 DoH、替换订阅源） | `files/etc/adguardhome/AdGuardHome.yaml` | 中 | 保留本地取值；上游改动该文件时人工比对 |
| UC-0011 | 2026-09-28 | 配置改动 | AdGuardHome 改用官方 openwrt 方案（官方 `luci-app-adguardhome` + `adguardhome` 守护进程包），放弃第三方实现 | `config/{x86_64,rpi4b}/{OpenWrt-K/local.config,network.config}`、`files/etc/uci-defaults/zzz-chenmozhijin`、`files/etc/adguardhome/adguardhome.yaml`、`build_helper/prepare.py` | 中 | 保留本地配置；上游若也切到官方实现，本条可撤销 |
| UC-0012 | 2026-09-28 | 预置文件 | 把 AdGuardHome 的 uci-defaults 逻辑从 `zzz-chenmozhijin` 拆成独立文件 | `files/etc/uci-defaults/zzz-adguardhome`（新增）、`files/etc/uci-defaults/zzz-chenmozhijin` | 低 | 保留拆分 |
| UC-0013 | 2026-09-28 | 配置改动 | DNS 分流器由 SmartDNS 换为 mosdns（不装 LuCI 界面、配置由使用者自备 YAML；SmartDNS 的上游行原样保留，关闭语义集中在 local.config） | `config/{x86_64,rpi4b}/network.config`（仅新增 mosdns 行）、`config/{x86_64,rpi4b}/OpenWrt-K/local.config`（关闭 SmartDNS 开关）、`files/etc/uci-defaults/zzz-chenmozhijin`、`files/etc/uci-defaults/zzz-adguardhome`、`files/etc/mosdns/config.yaml`（使用者提供）、`files/etc/uci-defaults/zzz-mosdns`、`build_helper/prepare.py`、`README.md`、`AGENTS.md` | 低 | 保留本地选择；上游若同样切换到 mosdns，本条可撤销 |

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
  - 仅 rpi4b 启用 `CONFIG_PACKAGE_ddns-go=y`、`CONFIG_PACKAGE_luci-app-ddns-go=y`、`CONFIG_PACKAGE_luci-i18n-ddns-go-zh-cn=y`；
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
- 本地行为：清单里排除以下内容（共 9 个拓展包 + 31 个配置符号）：
  - tailscale 组合：`tailscale`、`luci-app-tailscale-community`，以及它们的 4 个开关；
  - 旧 DDNS 方案：`ddns-scripts_aliyun`，以及 rpi4b 上的 `ddns-scripts`、`ddns-scripts-cloudflare`、`ddns-scripts-dnspod`、`ddns-scripts-services`、`luci-app-ddns` 与 3 个 `luci-i18n-ddns-*`；
  - qBittorrent 及其构建链：`luci-app-qbittorrent`、`qBittorrent-Enhanced-Edition`、`qt6base`、`qt6tools`、`libdouble-conversion`、`protobuf-compat`，以及界面开关、Qt6 运行时、`libtorrent-rasterbar` 与 boost 系列。
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
  - 分流器改为 **mosdns**（由 immortalwrt/packages 提供，经 feed 直接启用，**不新增扩展包声明**）；
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
