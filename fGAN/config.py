import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', required=True, help='cifar10 | lsun | imagenet | folder | lfw | fake')
parser.add_argument('--dataroot', default=os.path.split(os.getcwd())[0] + '/datasets', help='path to dataset')
parser.add_argument('--f_div', default='GAN', help='type of f_divergence')  # type of f_divergence
parser.add_argument('--workers', type=int, help='number of data loading workers', default=2)
parser.add_argument('--batch_size', type=int, default=100, help='input batch size')
parser.add_argument('--image_size', type=int, default=64, help='the height / width of the input image to network')
parser.add_argument('--nc', type=int, default=3, help='input image channels')
parser.add_argument('--nz', type=int, default=100, help='size of the latent z vector')
parser.add_argument('--ngf', type=int, default=64)
parser.add_argument('--ndf', type=int, default=64)
parser.add_argument('--niter', type=int, default=25, help='number of epochs to train for')
parser.add_argument('--lr', type=float, default=0.002, help='learning rate, default=0.002')
parser.add_argument('--beta1', type=float, default=0.5, help='beta1 for adam. default=0.5')
parser.add_argument('--cuda', action='store_true', help='enables cuda')
parser.add_argument('--ngpu', type=int, default=1, help='number of GPUs to use')
parser.add_argument('--netG', default='', help="path to netG (to continue training)")
parser.add_argument('--netD', default='', help="path to netD (to continue training)")
parser.add_argument('--outf', default=None, help='folder to output images and model checkpoints')


def get_config():
    return parser.parse_args()
