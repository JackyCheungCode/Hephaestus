# Hephaestus Lead Finder

多搜索 API 聚合的海外客户开发与线索挖掘工具。当前 Cloudflare Worker 版是可运行的 MVP：搜索工作台、六个 Provider 配置、连接测试、Mock 搜索、域名去重、解释性评分、线索状态/备注/标签、历史、成本统计、CSV 导出。

## 技术与部署

- Cloudflare Workers + D1（线上）
- 本地运行使用 Wrangler + 本地 D1 模拟数据库
- 六个 Provider：Tavily、Brave、Serper、Exa、Bocha、Perplexity Sonar
- API Key 后端 AES-256-GCM 加密，主密钥通过 Worker Secret 注入
- Mock 模式默认启用，Mock 搜索不会调用付费 API

## 10 分钟本地启动

需要 Node.js 20+。

1. 安装依赖：npm install
2. 初始化本地 D1 数据库：npm run d1:local
3. 启动：npm run dev:worker
4. 打开 http://localhost:8787。默认 Mock 模式即可试用，不需要 API Key。

本地若要保存真实 API Key，创建 .dev.vars（不要提交到 Git）：

    APP_ENCRYPTION_KEY="在终端生成的 base64 32 字节密钥"

生成密钥：openssl rand -base64 32

## Docker

    docker compose up --build

页面地址为 http://localhost:8787。Docker 使用 Wrangler 的本地 D1 状态目录，请保留 .wrangler 数据卷。

## Cloudflare 部署

Worker 名称为 hephaestus，D1 数据库为 hephaestus-leads。

    npx wrangler login
    npm run d1:remote
    npx wrangler secret put APP_ENCRYPTION_KEY
    npm run deploy:worker

线上入口：https://hephaestus.xg-y.workers.dev

生产环境请使用自己的 Cloudflare 账号和密钥管理流程。不要把 .dev.vars、.env 或 API Key 提交到 Git。

## Provider 配置

进入 Provider 设置，启用需要的 Provider，填写官方 API Key 和可选 Base URL，设置优先级、权重、结果数、超时、重试和估算单价，保存后使用测试连接。密钥保存后不会返回明文。Live 模式只调用已启用且已配置密钥的 Provider；Mock 模式只产生模拟数据。

默认 API 地址：
- Tavily: https://api.tavily.com/search
- Brave: https://api.search.brave.com/res/v1/web/search
- Serper: https://google.serper.dev/search
- Exa: https://api.exa.ai/search
- Bocha: https://api.bochaai.com/v1/web-search
- Perplexity Sonar: https://api.perplexity.ai/chat/completions

Provider 的 API 版本和账号权限可能变化，请在正式使用前核对供应商最新官方文档。Perplexity 结果会保存 answer 与 citations。

## MVP 范围与限制

已实现：Provider 设置/测试、Mock/真实搜索适配、按域名去重、RRF 风格融合排序、解释性评分、线索筛选/状态/备注/标签、删除、CSV、历史与估算成本。

尚未实现：落地页抓取与 Contact/About 发现、邮箱/电话/社交信息提取、真正的缓存 TTL、并发任务队列、Excel、CRM Webhook、用户认证/RBAC。

单任务预算目前会在界面预估提示，不能替代供应商账户层的硬性消费限额。不提供自动群发邮件。仅采集公开商业信息；使用者应遵守网站 robots.txt、服务条款及适用的 GDPR/CCPA 等法律。URL 规范化包含基础 SSRF 过滤，但本 MVP 未开放任意 URL 抓取端点。

## 数据

D1 中 provider_configs 保存加密后的密钥；leads、search_jobs、provider_runs 持久化线索与运行历史。CSV 导出包含线索摘要、评分、来源、状态与备注，不导出密钥。
