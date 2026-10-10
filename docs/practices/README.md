# 可复用工程实践

这里保存工作流的通用方法说明，供 Skill 与用户按需阅读，不进入共享 Wiki 检索。方法是否适用由当前源码和现场条件决定；可跨项目借鉴的环境经验在 `knowledge/sites/` 保存，完整任务档案留在 workspace。

- [全参容量预估与多实例并行优化](capacity-and-parallel-experiments.md)：HCU Train Sim 的适用边界、全参优先、缩模依据、独立 DP 实例和 Agent 交流。
- [通信现场配方、RoCE 与 RCCL 差距排查](communication-recipe.md)：发现完整启动链、核对变量/库与实际路径、复现实测、区分多变量收益与单变量因果。
- [HCU 算子、通信与底层依赖联动](hcu-library-routing.md)：Primus Turbo、UCCL、UltraEP、MoonEP 等的选择边界，重编制品、集成与PR。
- [执行基线、候选验证与主仓交付顺序](execution-baseline.md)：保持实验连续性、复用已有资格、差异回归。

实际站点入口见 [站点知识](../../knowledge/sites/README.md)，归属与维护规则见 [知识架构](../knowledge-architecture.md)。`wiki-search` 搜索筛选后的工程 Wiki；本目录属于工作流使用文档，任务原始经验另用 `experience-search`。没有现场记录时保持缺口，不从模板捏造配置或数值。
