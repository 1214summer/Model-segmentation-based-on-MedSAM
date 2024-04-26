import numpy as np
import matplotlib.pyplot as plt
import os
from skimage import io, transform
import torch
import torch.nn.functional as F
import argparse
from PIL import Image
import imgviz
from segment_anything import sam_model_registry
join = os.path.join

class MedSAMInference:
    def __init__(self, checkpoint_path="work_dir/MedSAM/medsam_vit_b.pth", device="cpu"):
        self.device = device
        self.medsam_model = sam_model_registry["vit_b"](checkpoint=checkpoint_path)
        self.medsam_model = self.medsam_model.to(device)
        self.medsam_model.eval()

    @torch.no_grad()
    def medsam_inference(self, img_embed, box_1024, H, W):
        box_torch = torch.as_tensor(box_1024, dtype=torch.float, device=img_embed.device)
        if len(box_torch.shape) == 2:
            box_torch = box_torch[:, None, :]  # (B, 1, 4)


        sparse_embeddings, dense_embeddings = self.medsam_model.prompt_encoder(
            points=None,
            boxes=box_torch,
            masks=None,
        )
        low_res_logits, _ = self.medsam_model.mask_decoder(
            image_embeddings=img_embed,  # (B, 256, 64, 64)
            image_pe=self.medsam_model.prompt_encoder.get_dense_pe(),  # (1, 256, 64, 64)
            sparse_prompt_embeddings=sparse_embeddings,  # (B, 2, 256)
            dense_prompt_embeddings=dense_embeddings,  # (B, 256, 64, 64)
            multimask_output=False,
        )

        low_res_pred = torch.sigmoid(low_res_logits)  # (1, 1, 256, 256)

        low_res_pred = F.interpolate(
            low_res_pred,
            size=(H, W),
            mode="bilinear",
            align_corners=False,
        )
        low_res_pred = low_res_pred.squeeze().cpu().numpy()  # (256, 256)
        medsam_seg = (low_res_pred > 0.5).astype(np.uint8)
        return medsam_seg

    def preprocess_image(self, img_path):
        img_np = io.imread(img_path)
        if len(img_np.shape) == 2:
            img_3c = np.repeat(img_np[:, :, None], 3, axis=-1)
        else:
            img_3c = img_np
        H, W, _ = img_3c.shape

        img_1024 = transform.resize(
            img_3c, (1024, 1024), order=3, preserve_range=True, anti_aliasing=True
        ).astype(np.uint8)
        img_1024 = (img_1024 - img_1024.min()) / np.clip(
            img_1024.max() - img_1024.min(), a_min=1e-8, a_max=None
        )
        img_1024_tensor = (
            torch.tensor(img_1024).float().permute(2, 0, 1).unsqueeze(0).to(self.device)
        )
        return img_1024_tensor, (H, W)


    def run_inference(self, img_path, box_coords, output_path):
        img_tensor, (H, W) = self.preprocess_image(img_path)

        box_np = np.array([box_coords])
        box_1024 = box_np / np.array([W, H, W, H]) * 1024

        image_embedding = self.medsam_model.image_encoder(img_tensor)  # (1, 256, 64, 64)
        #跑分割结果
        medsam_seg = self.medsam_inference(image_embedding, box_1024, H, W)

        #保存彩色mask部分
        colored_mask_folder = os.path.join(output_path,"colored")
        os.makedirs(colored_mask_folder, exist_ok=True)  # 创建文件夹，如果不存在的话
        colored_mask_path = os.path.join(colored_mask_folder, "seg_" + os.path.basename(img_path))

        self.save_colored_mask(medsam_seg, colored_mask_path)

        #保存对比图片
        segmented_dir = os.path.join(output_path, "segmented")
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))
        img_3c = io.imread(img_path)
        ax[0].imshow(img_3c)
        self.show_box(box_np[0], ax[0])
        ax[0].set_title("Input Image and Bounding Box")
        ax[1].imshow(img_3c)
        self.show_mask(medsam_seg, ax[1])
        self.show_box(box_np[0], ax[1])
        ax[1].set_title("MedSAM Segmentation")
        plt.savefig(os.path.join(segmented_dir,  "seg_" + os.path.basename(img_path)))
        segmented_img_path = os.path.join(segmented_dir, "seg_" + os.path.basename(img_path))


        # 提取分割好的部分
        segmented_region = img_3c.copy()
        segmented_region[medsam_seg == 0] = 0  # 将分割掩码为0的部分置为0，即黑色
        mask_dir = os.path.join(output_path, "mask")
        # 保存分割好的部分
        mask_segmented_path = os.path.join(mask_dir, "segmented_" + os.path.basename(img_path))
        io.imsave(mask_segmented_path, segmented_region)

        return segmented_img_path, mask_segmented_path


    def show_box(self, box, ax):
        x0, y0 = box[0], box[1]
        w, h = box[2] - box[0], box[3] - box[1]
        ax.add_patch(
            plt.Rectangle((x0, y0), w, h, edgecolor="blue", facecolor=(0, 0, 0, 0), lw=2)
        )

    def show_mask(self, mask, ax, random_color=False):
        if random_color:
            color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
        else:
            color = np.array([251 / 255, 252 / 255, 30 / 255, 0.6])
        h, w = mask.shape[-2:]
        mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
        ax.imshow(mask_image)

    # 调整图像对比度
    def save_colored_mask(self, mask, colored_mask_path):
        lbl_pil = Image.fromarray(mask.astype(np.uint8), mode="P")
        colormap = imgviz.label_colormap()
        lbl_pil.putpalette(colormap.flatten())
        lbl_pil.save(colored_mask_path)