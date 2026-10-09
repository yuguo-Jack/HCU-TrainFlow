# 缩减模型与验收范围

优先仅缩层跑通或提前筛机。资源确实受限且用户明确允许时，也可缩减指定维度；把授权、完整配置、实际配置、逐项差异和未覆盖机制保存在私有任务中。不能根据“模型太大”自行改变 hidden size、专家数、head 数或精度。

`proxy-check FULL.json CANDIDATE.json` 默认只允许正整数 `num_layers` 减小。允许维度缩减的任务额外提供：

```json
{
  "authority": "用户明确允许本任务缩减指定维度，原指令保存在任务记录",
  "reason": "在有限设备上验证模型机制与工作流",
  "allowed_dimension_reductions": ["hidden_size", "ffn_hidden_size"]
}
```

运行 `proxy-check FULL.json CANDIDATE.json --authorization AUTHORIZATION.json`。这个授权文件记录既有授权，不是每次运行都要求用户再次批准。程序检查字段范围和正整数缩减；它不验证授权身份，也不能证明架构约束、反向传播或 loss 正确。新增、删除字段、改变 dtype、未列出的字段或增大维度仍拒绝。

## 适配时还要检查

- 保留有代表性的层型、分支、路由、共享专家、归一化、位置编码、前后向和残差边界。若缩层遗漏某种机制，单独增加覆盖用例并明确范围。
- 区分模型配置的 decoder 层数和引擎的 attention/MLP entry 数；不能仅比较两个同名 `num_layers`。保存从模型定义到 launcher 参数的映射。
- 检查 head/hidden/group 的整除、head dimension、latent projection、TP/EP/CP 分片、专家容量和序列长度限制。显式保留或说明被缩减的维度。
- 新模型不能用架构相似的已支持模型替代。逐项区分源码存在、可以 import、forward、backward、训练循环及扩容已验证状态。
- 初始数值基线按实际选定配置冻结，不能拿不同模型的 loss 做候选精度比较。已挂接 flow 且仍在同一比较范围内的源码或优化参数候选，用新 `candidate.snapshot` 固定实现并重新取得受影响证据；不为每次优化重置整个任务。环境、模型、数据、初始基线或验证契约改变时才按 [上下文契约](contracts.md) 更新 `task-context` 并重新验收。未挂接 flow 的旧式任务仍按该文档的旧式候选规则处理。

## 扩容和交付

完整模型目标仍须恢复完整参数后建立可运行布局，再扩 DP 域。若用户明确将缩减配置作为本轮验证对象，可以扩该配置的 DP，但须写成“缩减模型 DP 验证”；不能证明完整模型容量、数值收敛、性能或规模效率。完整模型未验证的项目继续列为缺口。
