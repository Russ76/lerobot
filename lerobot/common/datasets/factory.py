import torch

from lerobot.common.datasets.pusht import PushtExperienceReplay
from lerobot.common.datasets.simxarm import SimxarmExperienceReplay
from rl.torchrl.data.replay_buffers.samplers import PrioritizedSliceSampler


def make_offline_buffer(cfg):

    num_traj_per_batch = cfg.batch_size  # // cfg.horizon
    # TODO(rcadene): Sampler outputs a batch_size <= cfg.batch_size.
    # We would need to add a transform to pad the tensordict to ensure batch_size == cfg.batch_size.
    sampler = PrioritizedSliceSampler(
        max_capacity=100_000,
        alpha=cfg.per_alpha,
        beta=cfg.per_beta,
        num_slices=num_traj_per_batch,
        strict_length=False,
    )

    if cfg.env == "simxarm":
        # TODO(rcadene): add PrioritizedSliceSampler inside Simxarm to not have to `sampler.extend(index)` here
        offline_buffer = SimxarmExperienceReplay(
            f"xarm_{cfg.task}_medium",
            # download="force",
            download=True,
            streaming=False,
            root="data",
            sampler=sampler,
        )
    elif cfg.env == "pusht":
        offline_buffer = PushtExperienceReplay(
            f"xarm_{cfg.task}_medium",
            # download="force",
            download=True,
            streaming=False,
            root="data",
            sampler=sampler,
        )
    else:
        raise ValueError(cfg.env)

    num_steps = len(offline_buffer)
    index = torch.arange(0, num_steps, 1)
    sampler.extend(index)

    return offline_buffer
