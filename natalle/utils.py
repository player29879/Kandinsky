import math
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import importlib
from .model.utils import get_named_beta_schedule, _extract_into_tensor


def prepare_image(pil_image):
    w, h = pil_image.size
    pil_image = pil_image.resize((512, 512), resample=Image.BICUBIC, reducing_gap=1)
    arr = np.array(pil_image.convert("RGB"))
    arr = arr.astype(np.float32) / 127.5 - 1
    arr = np.transpose(arr, [2, 0, 1])
    image = torch.from_numpy(arr).unsqueeze(0)
    return image



def q_sample(x_start, t, schedule_name='linear', num_steps=1000, noise=None):
    betas = get_named_beta_schedule(schedule_name, num_steps)
    alphas = 1.0 - betas
    alphas_cumprod = np.cumprod(alphas, axis=0)
    sqrt_alphas_cumprod = np.sqrt(alphas_cumprod)
    sqrt_one_minus_alphas_cumprod = np.sqrt(1.0 - alphas_cumprod)
    if noise is None:
        noise = torch.randn_like(x_start)
    assert noise.shape == x_start.shape
    return (
            _extract_into_tensor(sqrt_alphas_cumprod, t, x_start.shape) * x_start
            + _extract_into_tensor(sqrt_one_minus_alphas_cumprod, t, x_start.shape)
            * noise
    )


def process_images(batch):
    scaled = ((batch + 1) * 127.5).round().clamp(0, 255).to(torch.uint8).to('cpu').permute(0, 2, 3, 1).numpy()
    images = []
    for i in range(scaled.shape[0]):
        images.append(Image.fromarray(scaled[i]))
    return images