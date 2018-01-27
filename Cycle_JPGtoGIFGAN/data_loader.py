import os
from glob import glob
from PIL import Image
import torch.utils.data
import torchvision.datasets as dset
import torchvision.transforms as transforms

class Dataset(torch.utils.data.Dataset):
    def __init__(self, root, image_size, domain):
        self.root = root
        self.domain = domain
        if not os.path.exists(self.root):
            raise Exception("[!] {} not exists.".format(self.root))

        self.paths = glob(os.path.join(self.root, '*.' + self.domain))
        if len(self.paths) == 0:
            raise Exception("No images are found in {}".format(self.root))

        #self.shape = list(Image.open(self.paths[0]).size) + [3]
        self.transform = transforms.Compose([
            transforms.Resize(image_size), 
            transforms.CenterCrop(image_size), 
            transforms.ToTensor(), 
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])

    def __getitem__(self, index):
        if self.domain == 'gif':
            outImgs = []
            inGif = Image.open(self.paths[index])
            nframes = 0
            while inGif:
                outImgs.append(self.transform(inGif.convert("RGB")))
                nframes += 1
                try:
                    inGif.seek(nframes)
                except EOFError:
                    break
            return outImgs
        else:
            inJpg = Image.open(self.paths[index]).convert("RGB")
            return self.transform(inJpg)

    def __len__(self):
        return len(self.paths)

def get_loader(dataroot, batch_size, image_size, num_workers, shuffle=True):
    A_dataset = Dataset(dataroot, image_size, domain="jpg")
    B_dataset = Dataset(dataroot, image_size, domain="gif")
    A_dataloader = torch.utils.data.DataLoader(A_dataset, batch_size=batch_size
                                             ,shuffle=True, num_workers=num_workers)
    B_dataloader = torch.utils.data.DataLoader(B_dataset, batch_size=batch_size
                                             ,shuffle=True, num_workers=num_workers)

    return A_dataloader, B_dataloader, A_dataloader, B_dataloader
