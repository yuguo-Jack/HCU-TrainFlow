---
id: doc-ascend-mindspeed-6f37ecf75911f074b0b7
title: Ascend/MindSpeed / docs/en/features/async-log-allreduce.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/en/features/async-log-allreduce.md
raw_sha256: bc2b61a9a6d2593afe843b2c4c5aeba4e3845a9bfd9e4a2e0d31c4fa19d97bfe
sources: []
generated_body_sha256: 1868ba746a9f22fefdc28fbf66c38bafbc602c60fab9a14fb91f819f1fb83c0f
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/async-log-allreduce.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/async-log-allreduce.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Async Log Allreduce

## Background and Challenges

In distributed training, traditional synchronous log allreduce operations block the training pipeline, waiting for all processes to complete loss value computation and communication. This synchronous approach leads to the following issues:

1. Underutilization of computing resources due to idle waiting time
2. Training throughput is limited by the slowest process
3. Logging becomes a performance bottleneck, impacting overall training efficiency.

This is especially pronounced in large-scale distributed training, where the overhead of synchronous log allreduce becomes significant when using a large number of NPUs, potentially affecting the overall training speed.

## Solution

The Async Log Allreduce feature addresses the above challenges through the following approaches:

1. **Asynchronous communication**: Uses non-blocking allreduce operations, allowing the training process to continue without waiting for log communication to complete.
2. **Overlapped computation and communication**: Overlaps log-related all-reduce operations with subsequent training steps to improve hardware utilization.
3. **Deferred processing**: Synchronizes communication results only when logs need to be actually recorded, rather than waiting immediately.

This feature implements asynchronous communication through the `async_op=True` parameter of `torch.distributed.all_reduce`, and uses a special loss value handling mechanism to ensure data consistency.

## Use Scenario

This feature is particularly suitable for the following scenarios:

1. Large-scale distributed training (hundreds to thousands of NPUs)
2. Scenarios requiring frequent logging of training metrics
3. Scenarios where computation and communication need to be highly overlapped
4. Apps sensitive to training throughput

## Usage

1. Add the parameter `--async-log-allreduce` to the startup bash script
2. Replace the `loss_func` function in ``pretrain_gpt.py` as follows.

```python
def loss_func(loss_mask: torch.Tensor, output_tensor: torch.Tensor):
    """Loss function.

    Args:
        loss_mask (torch.Tensor): Used to mask out some portions of the loss
        output_tensor (torch.Tensor): The tensor with the losses

    Returns:
        the loss scalar for this micro-batch
        the number of non-padded tokens in this microbatch
        a dict containing reporting metrics on the loss and number of tokens across
            the data parallel ranks
    """
    args = get_args()

    losses = output_tensor.float()
    loss_mask = loss_mask.view(-1).float()
    total_tokens = loss_mask.sum()
    loss = torch.cat([torch.sum(losses.view(-1) * loss_mask).view(1), total_tokens.view(1)])

    if args.context_parallel_size > 1:
        torch.distributed.all_reduce(loss, group=mpu.get_context_parallel_group())

    # Check individual rank losses are not NaN prior to DP all-reduce.
    rerun_state_machine = get_rerun_state_machine()
    if args.check_for_nan_in_loss_and_grad:
        rerun_state_machine.validate_result(
            result=loss[0],
            rejection_func=torch.isnan,
            message="found NaN in local forward loss calculation",
            tolerance=0.0,        # forward pass calculations are deterministic
            fatal=True,
        )
        rerun_state_machine.validate_result(
            result=loss[0],
            rejection_func=torch.isinf,
            message="found Inf in local forward loss calculation",
            tolerance=0.0,        # forward pass calculations are deterministic
            fatal=True,
        )
    # Check for spiky loss
    if args.check_for_spiky_loss:
        rerun_state_machine.validate_result(
            result=loss[0],
            rejection_func=partial(
                rerun_state_machine.is_unexpectedly_large,
                threshold=SPIKY_LOSS_FACTOR,
                context="loss",
            ),
            message="Spiky loss",
            tolerance=0.0,        # forward pass calculations are deterministic
            fatal=False,
        )
    # Reduce loss for logging.
    reporting_loss = loss.clone().detach()
    allreduce_handle = torch.distributed.all_reduce(
        reporting_loss, group=mpu.get_data_parallel_group(), async_op=True
    )

    # loss[0] is a view of loss, so it has ._base not None, which triggers assert error
    # in core/pipeline_parallel/schedule.py::deallocate_output_tensor, calling .clone()
    # on loss[0] fixes this
    local_num_tokens = loss[1].clone().detach().to(torch.int)
    return (
        loss[0].clone(),
        local_num_tokens,
        ({'lm loss': (reporting_loss[0], reporting_loss[1])}, allreduce_handle),
    )

```

## Effects

Enabling the Async Log Allreduce feature brings the following improvements:

1. **Larger training throughput**
2. **Higher resource utilization**
