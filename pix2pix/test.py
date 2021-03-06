from __future__ import print_function
import argparse
import os

import torch
from torch.autograd import Variable
import torchvision.transforms as transforms

from data_loader import is_image_file, load_img, save_img
from models import pix2pix

# Testing settings
parser = argparse.ArgumentParser(description='pix2pix-PyTorch-implementation')

parser.add_argument('--model', type=str, default='samples/netG_epoch_199.pth', help='model file to use')
parser.add_argument('--cuda', action='store_true', help='use cuda')
opt = parser.parse_args()


netG = pix2pix.define_G(3, 3, 64, 'batch', False, [])
netG.load_state_dict(torch.load(opt.model))

image_dir = "facades/test/a/"
image_filenames = [x for x in os.listdir(image_dir) if is_image_file(x)]

transform_list = [transforms.ToTensor(),
                  transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]

transform = transforms.Compose(transform_list)

for image_name in image_filenames:
    img = load_img(image_dir + image_name)
    img = transform(img)
    input = Variable(img, volatile=True).view(1, -1, 256, 256)

    if opt.cuda:
        netG = netG.cuda()
        input = input.cuda()

    out = netG(input)
    out = out.cpu()
    out_img = out.data[0]
    if not os.path.exists("facades/result"):
        os.mkdir("facades/result")
    save_img(out_img, "facades/result/{}".format(image_name))
