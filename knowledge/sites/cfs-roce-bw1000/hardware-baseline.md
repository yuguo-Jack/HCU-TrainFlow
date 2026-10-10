---
id: sites/cfs-roce-bw1000/hardware-baseline
title: CFS gfx936 硬件参数与 Roofline 参考边界
engine: cross-engine
kind: site-knowledge
stages: [adapt, optimize, fault-tolerance]
visibility: public
review_level: source-and-measurement-review
runtime_validated: false
observed_at: '2026-10-10T09:57:59.816648+00:00'
---

# 硬件参数与算子建模参考

本页保存可跨训练任务复用的硬件观测和既有基础实测。它不包含模型中间候选，也不替代新任务的设备健康、占用和性能验收。原件随仓保留，见 [证据清单](manifest.json)。

## 设备身份与资源

2026-10-10 对 `10.32.4.64`、`10.32.4.76` 各8卡做驱动只读属性和管理工具查询，没有运行GPU负载、修改时钟或功耗。旧 Torch/runtime 产品标签为 **BW1000_H**；此次 hy-smi 的 `Card Series` 为 **BW3000**。产品命名映射尚未确认，故不以某个SKU的外部规格表直接定义本站理论峰值；目录名继续保留历史标识以维持已有链接。

|参数|原始观测|如何使用|
|---|---|---|
|架构与身份|KFD `gfx_target_version=90306`；冻结 runtime `gfx936`；PCI vendor/device `1d94:6320`|保留每卡PCI、KFD node、render minor及管理工具ID；不同工具卡序需另外核对映射|
|计算资源|每卡320 SIMD、每CU4 SIMD，即80个有效CU；wave64；max_waves_per_simd=10|不能把8组×11名义槽位算成88个启用CU；实际occupancy还受寄存器、LDS和网格限制|
|显存|每卡65520 MiB，即63.984375 GiB|这是可见总量，不是训练时可用余量|
|LDS|`lds_size_in_kb=64`|每CU64 KiB；实际kernel静态/动态使用量另查编译产物和profiler|
|内存与缓存字段|每卡memory bank `width=4096`、`mem_clk_max=1800`；共享L2 entry `size=8192`|保留原始字段，单位/有效数据率与共享范围须用匹配驱动/API资料核对，不能据字段名计算未经核实的理论带宽；共享缓存不能按CU重复相加|
|时钟|sclk支持300–1600 MHz，此次空闲为600 MHz；mclk1800 MHz|支持上限、空闲快照、负载持续频率不同；没有负载时钟证据时明确缺口|
|功耗与PCIe|功耗上限800 W，auto策略；PCIe32.0 GT/s ×16|不是持续耗电或实测通信带宽；各卡瞬时功耗/温度在原件|

原始驱动/KFD与首次管理工具输出：[node64](evidence/2026-10-10-hardware/10.32.4.64-passive.json.gz)、[node76](evidence/2026-10-10-hardware/10.32.4.76-passive.json.gz)。有效JSON管理输出：[node64](evidence/2026-10-10-hardware/10.32.4.64-smi-json.json)、[node76](evidence/2026-10-10-hardware/10.32.4.76-smi-json.json)。gzip解压后字节哈希同样登记在清单。

一次 `--showclkfrq` 与 `--json` 合用时，工具退出0却把频率文本混入JSON。去掉该选项后重新查询得到有效JSON，频率表另以驱动属性核对。这是该安装版本的已观测行为；后续版本应重新查接口，不能依赖成功退出码自动接受不完整结构，也不应以正则随意修复原件。

## 既有本站 GEMM 与 copy 实测

以下来自 **2026-10-09 11:05 UTC** 的8卡逐卡顺序测量。原任务将其归属为node67；这份诊断自身没有hostname或容器ID，随仓原件未保留将该诊断哈希与执行节点/容器直接绑定的回执，因此该节点归属不能仅凭本页原件独立核验，更不能算作上述64/76的当前测量。Torch2.11、DTK26.10、HIP7.2.26365；精确包版本、设备UUID及每组时间见 [原始诊断](evidence/2026-10-10-hardware/torch-diagnostic-20261009T110522Z.json)，方法见 [固定测试脚本](evidence/2026-10-10-hardware/probe_torch_device.py)。每卡预热10次、每组30次调用、重复3组，以device events计时；速率由各组平均调用时间的中位数换算。

|项目|8卡测得范围|计数与适用边界|
|---|---:|---|
|BF16 GEMM 4096³|354.512–354.907 TFLOP/s|2MNK，FMA计2；Torch mm，不是矩阵指令理论峰值|
|BF16 GEMM 8192³|316.698–325.875 TFLOP/s|不同shape本就可能不同；原件未固定BLAS具体算法，不推定所有矩阵能达同值|
|FP32 device copy|1358.654–1359.763 GB/s|源/目标各512 MiB，读+写1 GiB；十进制GB/s，不能当作规约、随机访问或多数组融合的匹配上限|

正确性仅覆盖测试脚本的64³整数输入BF16 GEMM和copy相等性，不是对全部大矩阵精度的验收。8卡按顺序执行，不等于同时满载或集群持续稳定性通过。当次未固定实际BLAS算法与负载时钟，且存在上述执行身份回执缺口；仅用作带限制的参考。后续新测试同时保存节点/容器、命令、源码与结果哈希的绑定回执，不追溯补造旧回执。

## 建模与失效条件

1. 对实际算子分别选择矩阵/VALU/特殊指令和HBM/缓存/通信路径；按真实dtype、累加精度、shape、别名和必要读写计算工作量。
2. 上表可用于条件化筛查，不能当严格物理屋顶。尤其不可把BF16 GEMM速率用于FP32逐元素、sqrt/div，或把逻辑字节一律当作实测HBM流量。
3. 精确SKU的分精度理论算力、特殊函数吞吐和负载持续时钟仍未完成确认。缺口保留；不引用相近硬件的数值填表，不因此否定已成立的实际测量。
4. 换设备、驱动、镜像、库、时钟/功耗策略或测量协议后重新判断受影响项；扩容时核对新增设备同质性。重新阅读本页不刷新测量日期。

环境到算子负责人的完整交接要求见 [通用环境发现](../../../docs/environment-discovery.md#建立硬件基线并交给算子建模)。本站通信另见 [通信配方与实测](communication.md)。
