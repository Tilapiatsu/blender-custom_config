# CODE BY
# https://github.com/xinntao/ESRGAN
# I modified the code to work with Blender.

import os
import bpy
import glob
import functools
import numpy as np
from ..pidgeon_tool_bag.PTB_Functions import bcolors

try:
    import cv2
except Exception:
    pass

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except Exception:
    pass

def make_layer(block, n_layers):
    layers = []
    for _ in range(n_layers):
        layers.append(block())
    return nn.Sequential(*layers)

def upscale_image():
    settings = bpy.context.scene.siu_settings
    model_primary_path = os.path.join(os.path.dirname(__file__), "esrgan", "models", settings.model_primary)
    model_secondary_path = os.path.join(os.path.dirname(__file__), "esrgan", "models", settings.model_secondary)
    device = torch.device(settings.device)
    test_img_folder = os.path.join(bpy.path.abspath(settings.input_folder),'*')

    print(bcolors.OKBLUE + "Loading models..." + bcolors.ENDC)
    
    def initialize_model(model_path, device):
        model = RRDBNet(3, 3, 64, 23, gc=32)
        model.load_state_dict(torch.load(model_path), strict=True)
        model.eval()
        return model.to(device)

    # Primary
    if settings.model_blend != 1.0:
        model_primary = initialize_model(model_primary_path, device)

    # Secondary
    if settings.model_blend != 0.0:
        model_secondary = initialize_model(model_secondary_path, device)


    print(bcolors.OKBLUE + "Models loaded successfully." + bcolors.ENDC)

    print(bcolors.OKBLUE + "Upscaling images..." + bcolors.ENDC)
    idx = 0
    totalx = len(glob.glob(test_img_folder))
    for path in glob.glob(test_img_folder):
        idx += 1
        base = os.path.splitext(os.path.basename(path))[0]
        print(bcolors.OKCYAN + f"Working on image: {base} - {idx} of {totalx}" + bcolors.ENDC)

        img = cv2.imread(path, cv2.IMREAD_COLOR)
        img = img * 1.0 / 255
        img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img_LR = img.unsqueeze(0)
        img_LR = img_LR.to(device)

        def process_output(model, img_LR):
            with torch.no_grad():
                output = model(img_LR).data.squeeze().float().cpu().clamp_(0, 1).numpy()
            output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
            return (output * 255.0).round()

        if settings.model_blend == 0.0:
            output = process_output(model_primary, img_LR)
        elif settings.model_blend == 1.0:
            output = process_output(model_secondary, img_LR)
        else:
            output_primary = process_output(model_primary, img_LR)
            output_secondary = process_output(model_secondary, img_LR)
            output = (output_primary * (1 - settings.model_blend)) + (output_secondary * settings.model_blend)

        cv2.imwrite(os.path.join(bpy.path.abspath(settings.output_folder), f"{settings.output_prefix}{base}{settings.output_suffix}.{settings.output_format}").format(base), output)

    print(bcolors.SUCCESS + "Finished upscaling images."+ bcolors.ENDC, "\n")


class ResidualDenseBlock_5C(nn.Module):
    def __init__(self, nf=64, gc=32, bias=True):
        super(ResidualDenseBlock_5C, self).__init__()
        # gc: growth channel, i.e. intermediate channels
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1, bias=bias)
        self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1, bias=bias)
        self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1, bias=bias)
        self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1, bias=bias)
        self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1, bias=bias)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

        # initialization
        # mutil.initialize_weights([self.conv1, self.conv2, self.conv3, self.conv4, self.conv5], 0.1)

    def forward(self, x):
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x


class RRDB(nn.Module):
    '''Residual in Residual Dense Block'''

    def __init__(self, nf, gc=32):
        super(RRDB, self).__init__()
        self.RDB1 = ResidualDenseBlock_5C(nf, gc)
        self.RDB2 = ResidualDenseBlock_5C(nf, gc)
        self.RDB3 = ResidualDenseBlock_5C(nf, gc)

    def forward(self, x):
        out = self.RDB1(x)
        out = self.RDB2(out)
        out = self.RDB3(out)
        return out * 0.2 + x


class RRDBNet(nn.Module):
    def __init__(self, in_nc, out_nc, nf, nb, gc=32):
        super(RRDBNet, self).__init__()
        RRDB_block_f = functools.partial(RRDB, nf=nf, gc=gc)

        self.conv_first = nn.Conv2d(in_nc, nf, 3, 1, 1, bias=True)
        self.RRDB_trunk = make_layer(RRDB_block_f, nb)
        self.trunk_conv = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
        #### upsampling
        self.upconv1 = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
        self.upconv2 = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
        self.HRconv = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
        self.conv_last = nn.Conv2d(nf, out_nc, 3, 1, 1, bias=True)

        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x):
        settings = bpy.context.scene.siu_settings
        fea = self.conv_first(x)
        trunk = self.trunk_conv(self.RRDB_trunk(fea))
        fea = fea + trunk

        # string to float
        scale = float(settings.scale_factor)
        fea = self.lrelu(self.upconv1(F.interpolate(fea, scale_factor=scale, mode=settings.mode_type)))
        fea = self.lrelu(self.upconv2(F.interpolate(fea, scale_factor=scale, mode=settings.mode_type)))
        out = self.conv_last(self.lrelu(self.HRconv(fea)))

        return out
