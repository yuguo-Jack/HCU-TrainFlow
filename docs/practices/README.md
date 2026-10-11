# 可复用工程实践

这里保存工作流的通用方法说明，供 Skill 与用户按需阅读，不进入共享 Wiki 检索。方法是否适用由当前源码和现场条件决定；可跨项目借鉴的环境经验在 `knowledge/sites/` 保存，完整任务档案留在 workspace。

- [全参容量预估与多实例并行优化](capacity-and-parallel-experiments.md)：HCU Train Sim 的适用边界、全参优先、缩模依据、独立 DP 实例和 Agent 交流。
- [通信现场配方、RoCE 与 RCCL 差距排查](communication-recipe.md)：发现完整启动链、核对变量/库与实际路径、复现实测、区分多变量收益与单变量因果。
- [HCU 算子、通信与底层依赖联动](hcu-library-routing.md)：Primus Turbo、UCCL、UltraEP、MoonEP 等的选择边界，重编制品、集成与PR。
- [执行基线、候选验证与主仓交付顺序](execution-baseline.md)：保持实验连续性、复用已有资格、差异回归。
- [性能方法与参考来源](performance-methods.md)：证据刷新、热点/重叠/融合分析、条件上限、组合验证，以及 Hyperloom、GEAK、BBuf 方法的采用边界。

工具证据如何衔接这些方法，见 [TraceLens 分析与验证](../tracelens-analysis.md)和[性能分析流程细图](../workflow-map.md#36-tracelens-证据怎样进入优化闭环)。

实际站点入口见 [站点知识](../../knowledge/sites/README.md)，归属与维护规则见 [知识架构](../knowledge-architecture.md)。`wiki-search` 搜索筛选后的工程 Wiki；本目录属于工作流使用文档，任务原始经验另用 `experience-search`。没有现场记录时保持缺口，不从模板捏造配置或数值。
