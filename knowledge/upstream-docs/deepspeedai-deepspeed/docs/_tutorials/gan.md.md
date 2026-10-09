---
id: doc-deepspeedai-deepspeed-5ae8ae7b045162930d3b
title: deepspeedai/DeepSpeed / docs/_tutorials/gan.md
engine: deepspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: deepspeedai/DeepSpeed
commit: bc1ad320a9afb516797577924a9983c6d7cd6793
path: docs/_tutorials/gan.md
raw_sha256: 3e1303da890fee3a9a425fbcd318f919841a3f4328ff5f7fe59f3e3c92a2a90f
sources: []
generated_body_sha256: ddca3cf041c4c9554b5accb0623a03c9eaba544739bfae8bbc9265abedcd5b62
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/_tutorials/gan.md

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/_tutorials/gan.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "DCGAN Tutorial"
excerpt: "Train your first GAN model with DeepSpeed!"
tags: getting-started training
---

If you haven't already, we advise you to first read through the [Getting Started](/getting-started/) guide before stepping through this
tutorial.

In this tutorial, we will port the DCGAN model to DeepSpeed using custom (user-defined) optimizers and a multi-engine setup!

## Running Original DCGAN

Please go through the [original tutorial](https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html) for the Celebrities dataset first using the [original code](https://github.com/pytorch/examples/blob/master/dcgan/main.py). Then run `bash gan_baseline_run.sh`.


## Enabling DeepSpeed

The codes may be obtained [here](https://github.com/deepspeedai/DeepSpeedExamples/tree/master/gan).

### Argument Parsing

The first step to apply DeepSpeed is adding configuration arguments to DCGAN model, using the `deepspeed.add_config_arguments()` function as below.

```python
import deepspeed

def main():
    parser = get_argument_parser()
    parser = deepspeed.add_config_arguments(parser)
    args = parser.parse_args()
    train(args)
```



### Initialization

We use `deepspeed.initialize` to create two model engines (one for the discriminator network and one for the generator network along with their respective optimizers) as follows:

```python
    model_engineD, optimizerD, _, _ = deepspeed.initialize(args=args, model=netD, model_parameters=netD.parameters(), optimizer=optimizerD)
    model_engineG, optimizerG, _, _ = deepspeed.initialize(args=args, model=netG, model_parameters=netG.parameters(), optimizer=optimizerG)

```

Note that DeepSpeed automatically takes care of the distributed training aspect, so we set ngpu=0 to disable the default data parallel mode of pytorch.

### Discriminator Training

We modify the backward for discriminator as follows:

```python
model_engineD.backward(errD_real)
model_engineD.backward(errD_fake)
```

which leads to the inclusion of the gradients due to both real and fake mini-batches in the optimizer update.

### Generator Training

We modify the backward for generator as follows:

```python
model_engineG.backward(errG)
```

**Note:** In the case where we use gradient accumulation, backward on the generator would result in accumulation of gradients on the discriminator, due to the tensor dependencies as a result of `errG` being computed from a forward pass through the discriminator; so please set `requires_grad=False` for the `netD` parameters before doing the generator backward.

### Configuration

The next step to use DeepSpeed is to create a configuration JSON file (gan_deepspeed_config.json). This file provides DeepSpeed specific parameters defined by the user, e.g., batch size, optimizer, scheduler and other parameters.

```json
{
  "train_batch_size" : 64,
  "optimizer": {
    "type": "Adam",
    "params": {
      "lr": 0.0002,
      "betas": [
        0.5,
        0.999
      ],
      "eps": 1e-8
    }
  },
  "steps_per_print" : 10
}
```



### Run DCGAN Model with DeepSpeed Enabled

To start training the DCGAN model with DeepSpeed, we execute the following command which will use all detected GPUs by default.

```bash
deepspeed gan_deepspeed_train.py --dataset celeba --cuda --deepspeed_config gan_deepspeed_config.json --tensorboard_path './runs/deepspeed'
```

## Performance Comparison

We use a total batch size of 64 and perform the training on 16 GPUs for 1 epoch on a DGX-2 node which leads to 3x speed-up. The summary of the results is given below:

- Baseline total wall clock time for 1 epochs is 393 secs

- Deepspeed total wall clock time for 1 epochs is 128 secs


###