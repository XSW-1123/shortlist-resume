# Java 后端 / 校招参考档（内置样例，不是硬编码要求）

用途：目标岗位为 Java 后端实习 / 校招，或用户明确说「没有 JD，按基线」时，作为 Phase 1 的权重来源基线。**必须在 `report.md` 写明「本版采用内置 Java 后端基线，未经用户 JD 校准」**。其他岗位请用 `assets/role-profile.template.yaml` 现场生成，不要把本档的词表硬套。

本档内容来自 2026-11-14 的一轮面试官偏好专项检索与一份真实项目的逐行源码核验，仅作可追溯的参考，不保证适用于 2026 年之后的市场，也不代表任何官方口径。

## 1. 权重来源（E1–E10，完整 URL 便于复核）

| 编号 | 来源 | 关键结论 |
|---|---|---|
| E1 | `https://developer.cloud.tencent.com/article/2756490` | P0 地基约 45%：Java 集合 / 并发 / JVM、MySQL 索引与事务、Redis 数据结构与一致性、框架 IoC/AOP/事务失效；P1 约 30% 为项目深挖（选型理由、指标条件、真实故障）；明确「AI 面试官围绕简历细节自动生成追问链，写不实反而致命」 |
| E2 | `https://ac.nowcoder.com/discuss/1671711` | HashMap、线程池 7 参数 + 拒绝策略、ThreadLocal、JVM、@Transactional 失效场景、SpringBoot 自动配置、MySQL 索引原理 / MVCC / 慢 SQL、Redis 五结构与分布式锁 |
| E3 | `https://www.hqwc.cn/a/1585571.html` | 技能按岗位匹配度排序，投 Java 后端第一行必须是 Java、SpringBoot；不用「精通」，用「熟悉 X，了解其 Y 原理」划边界 |
| E4 | `https://geekdaxue.co/read/tiansejiangbian@flutter/bfy8gz` | 避免写人人会用的基础技能，不写一知半解的词，只重点写 1–2 个 |
| E5 | `http://mp.weixin.qq.com/s?__biz=MzIyNzY5ODY5Mg==&mid=2247484464&idx=1&sn=8dd2d897805b6a45bb75349c369de742` | 首轮只有 10–30 秒，扫关键词、数字、做过真东西的证据；功能清单等于告诉对方这是教程项目；改成「问题 → 定位 → 方案 → 结果」并留追问接口 |
| E6 | `https://www.mtrt.cn/news/30198` | 点餐 / 秒杀是同款流水线项目，雷同的是描述不是项目；差距来自一个具体失败现场、一次带取舍的判断、一个没解决干净的遗留问题 |
| E7 | `https://www.hqwc.cn/a/563651.html` | 有排名和奖项才能证明同层次拔尖；项目写法要覆盖高并发 / 限流 / 缓存等高频考点，每条预留 1–2 个深度考点；技能栏只贴合岗位删选 |
| E8 | `http://www.nxbn.cn/news/28906.html` | 简历是面试的剧本，每一行都要能演三分钟；项目要讲决策不是讲功能；面试官关心「为什么选它」 |
| E9 | `https://www.hqwc.cn/a/1445135.html` | 简历上每个词都是向面试官发出的战书；写「熟悉 Redis」就会被追问持久化、淘汰策略、分布式锁，答不上来比写「了解」更减分 |
| E10 | `https://ginlong.zhiye.com/campus/jobs` | 27 届 Java 校招 JD 任职要求顺序：Java 基础 → SpringBoot / MyBatis-Plus → MySQL → Redis → MQ → Git / Maven / Linux |

## 2. P0 词表（47 个，作为覆盖率参考而非堆词目标）

```
Java 21, 集合, 并发, ThreadLocal, 线程池, 拒绝策略, 事务失效, JVM, GC,
SpringBoot, SpringMVC, Spring Security, MyBatis-Plus, IoC, AOP, 自动装配,
MySQL, 索引, B+ 树, 最左前缀, EXPLAIN, 隔离级别, MVCC, 行锁, 唯一索引, 幂等,
Redis, Lua, Redisson, 分布式锁, 缓存一致性, 穿透, 击穿, 雪崩,
RESTful, JWT, 越权, 脱敏, 滑动窗口, 限流, 防重放,
Git, Maven, Linux, 可观测性, traceId, afterCommit
```

注意：词表用于检查「有没有漏掉该岗位的地基」，**不是优化目标**。为凑命中率堆词会触发 R10 难度闸门失败。校验器只在用户提供 `role-profile.yaml` 时才检查这一项。

## 3. 技能栏顺序与程度词

推荐 6 行，顺序对齐 E10 任职要求：Java 基础 → 后端框架 → 数据库 → 缓存中间件 → 接口与安全 → 工程化。程度词三级：`熟悉`（有源码落点）/ `理解`（知识层必考但项目无实现，如 MVCC、行锁、事务失效）/ `了解`（只划认知边界，如 JVM / GC）。全篇 0 个「精通」。

技能栏不得复述实现级细节（`ON DUPLICATE KEY UPDATE`、`ZSET + Lua`、`X-Nonce`、`SpringDoc`、`MDC traceId`、`afterCommit` 等），那些由项目 bullet 独占（R6）。

## 4. 非岗位技术词样例（项目板块命中须为 0）

```
Python, PyTorch, Vue, uni-app, YOLO, RT-DETR, AUC, mAP, 量化, 图谱, 配电, 绝缘, 论文, 科研
```

这份名单来自一位真实用户的跨方向经历，只作示例。每个岗位应由用户自己的经历重新生成名单。

## 5. 源码级证据的写法样例

以下是「为什么 / 边界 / 代价」直接取自源码注释的真实样例，展示 R7/R11 想要的粒度，不是可复制的经历：

| 出处 | 可写进 bullet 的决策理由 |
|---|---|
| `cache/CacheHelper.java:192-205` | 事务 `afterCommit` 后延迟双删 500ms，是为兜住并发读写下的旧值回填窗口 |
| `mapper/DishMapper.java:18` | `UPDATE ... WHERE stock >= n` 把「是否够扣」交给 DB 行锁内原子完成，消除先查后减的超卖窗口 |
| `concurrent/MdcTaskDecorator.java:11-27` | `@Async` 不传递 ThreadLocal，搬运 MDC 快照并在 `finally` 还原，避免线程复用串号 |
| `scheduler/OrderTimeoutProducer.java:25-26,78` | 仅事务提交后投递延迟队列；Redis 不可用时跳过投递，由定时扫描兜底漏投 |
| `ratelimit/SlidingWindowRateLimiter.java:34` | ZSET + Lua 滑动窗口在 Redis 故障时 fail-open，以可用性优先 |

## 6. 常见无证据词黑名单（按项目实况确认，不是固定表）

MQ、SpringCloud、Docker、虚拟线程、JVM 调优、压测 QPS、上线部署、AI / 大模型关键词。项目里没用 MQ 就不要写 MQ；把延迟队列的兜底原因写清，让面试官自然问「为什么不用 MQ」，并提前准备选型对比。

## 7. 匹配分口径提醒

`scripts/ats_match.py` 用 JD 的 Top 12 关键词加权，目标区间 65%–85% 只是趋势估算。删内容会让「前 1/3」权重区前移、分数虚高；把技能栏移到文末会让分数回落，但全文命中数不变。曾出现顿号改写把 JD 的 2-gram「与事务」拆开导致掉分的情况，属于脚本切词口径效应，改回原字即可，不得据此加词（R15）。
