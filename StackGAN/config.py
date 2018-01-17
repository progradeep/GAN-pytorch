import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--training', type=int, required=True, help='1 for True for and 0 for False')
parser.add_argument('--stage', type=int, default=2, help='1 | 2')
parser.add_argument('--dataset', required=True, help='birds | flowers | coco')
parser.add_argument('--dataroot', required=True, help='path to dataset')
parser.add_argument('--embedding_type', default='cnn-rnn', help='text embedding type')
parser.add_argument('--workers', type=int, help='number of data loading workers', default=2)
parser.add_argument('--batch_size', type=int, default=40, help='input batch size')
parser.add_argument('--image_size', type=int, default=64, help='the height / width of the input image to network')
parser.add_argument('--text_dim', type=int, default=1024)
parser.add_argument('--nz', type=int, default=100, help='size of the latent z vector')
parser.add_argument('--nef', type=int, default=128)
parser.add_argument('--ngf', type=int, default=192)
parser.add_argument('--ndf', type=int, default=96)
parser.add_argument('--r_num', type=int, default=2)
parser.add_argument('--niter', type=int, default=120, help='number of epochs to train for')
parser.add_argument('--snapshot_interval', type=int, default=10, help='number of epochs to train for')
parser.add_argument('--vis_count', type=int, default=64)
parser.add_argument('--lrD', type=float, default=0.0002, help='learning rate, default=0.0002')
parser.add_argument('--lrG', type=float, default=0.0002, help='learning rate, default=0.0002')
parser.add_argument('--lr_decay_step', type=int, default=20)
parser.add_argument('--beta1', type=float, default=0.5, help='beta1 for adam. default=0.5')
parser.add_argument('--cuda', action='store_true', help='enables cuda')
parser.add_argument('--ngpu', type=int, default=1, help='number of GPUs to use')
parser.add_argument('--netG', default='', help="path to netG (to continue training)")
parser.add_argument('--stageI_G', default='', help="path to stageI_G (to continue training)")
parser.add_argument('--netD', default='', help="path to netD (to continue training)")
parser.add_argument('--outf', default=None, help='folder to output images and model checkpoints')
parser.add_argument('--coeff_KL', type=int, default=2.0, help='coefficient for KL divergence')


def get_config():
    return parser.parse_args()
