from __future__ import print_function
import os
import tqdm
import pickle
import numpy as np
import torch.utils.data
from torchvision.datasets import ImageFolder
from torchvision import transforms
from torch.utils.data import DataLoader
from PIL import Image
import functools


class VideoFolderDataset(torch.utils.data.Dataset):
    def __init__(self, folder, min_len=10):
        dataset = ImageFolder(folder)
        self.total_frames = 0
        self.lengths = []
        self.images = []

        for idx, (im, categ) in enumerate(
                tqdm.tqdm(dataset, desc="Counting total number of frames")):
            img_path, _ = dataset.imgs[idx]
            shorter, longer = min(im.width, im.height), max(im.width, im.height)
            length = longer // shorter
            if length >= min_len:
                self.images.append((img_path, categ))
                self.lengths.append(length)


        self.cumsum = np.cumsum([0] + self.lengths)
        print ("Total number of frames {}".format(np.sum(self.lengths)))

    def __getitem__(self, item):
        path, label = self.images[item]
        im = Image.open(path)
        return im, label

    def __len__(self):
        return len(self.images)


class ImageDataset(torch.utils.data.Dataset):
    def __init__(self, dataset, transform=None):
        self.dataset = dataset

        self.transforms = transform if transform is not None else lambda x: x

    def __getitem__(self, item):
        if item != 0:
            video_id = np.searchsorted(self.dataset.cumsum, item) - 1
            frame_num = item - self.dataset.cumsum[video_id] - 1
        else:
            video_id = 0
            frame_num = 0

        video, target = self.dataset[video_id]
        video = np.array(video)

        horizontal = video.shape[1] > video.shape[0]

        if horizontal:
            i_from, i_to = video.shape[0] * frame_num, video.shape[0] * (frame_num + 1)
            frame = video[:, i_from: i_to, ::]
        else:
            i_from, i_to = video.shape[1] * frame_num, video.shape[1] * (frame_num + 1)
            frame = video[i_from: i_to, :, ::]

        if frame.shape[0] == 0:
            print ("video {}. From {} to {}. num {}".format(video.shape, i_from, i_to, item))
        return {"images": self.transforms(frame), "categories": target}

    def __len__(self):
        return self.dataset.cumsum[-1]


class VideoDataset(torch.utils.data.Dataset):
    def __init__(self, dataset, video_length, every_nth=1, transform=None):
        self.dataset = dataset
        self.video_length = video_length
        self.every_nth = every_nth
        self.transforms = transform if transform is not None else lambda x: x

    def __getitem__(self, item):
        video, target = self.dataset[item]
        video = np.array(video)
        # video. 96 x 96 * 16 x 3

        horizontal = video.shape[1] > video.shape[0]
        shorter, longer = min(video.shape[0], video.shape[1]), max(video.shape[0], video.shape[1])
        video_len = longer // shorter

        # videos can be of various length, we randomly sample sub-sequences
        if video_len > self.video_length * self.every_nth:
            needed = self.every_nth * (self.video_length - 1)
            gap = video_len - needed
            start = 0 if gap == 0 else np.random.randint(0, gap, 1)[0]
            subsequence_idx = np.linspace(start, start + needed, self.video_length, endpoint=True, dtype=np.int32)

        elif video_len >= self.video_length:
            subsequence_idx = np.linspace(0, video_len-1, self.video_length, dtype=np.int32)
        else:
            raise Exception("Length is too short id - {}, len - {}").format(self.dataset[item], video_len)

        # video. 96 x 96 * 16 x 3
        frames = np.split(video, video_len, axis=1 if horizontal else 0)
        # frames. 16 x 96 x 96 x 3
        selected = np.array([frames[s_id] for s_id in subsequence_idx])
        # selected. 10 x 96 x 96 x 3

        return {"images": self.transforms(selected), "categories": target}

    def __len__(self):
        return len(self.dataset)


class ImageSampler(torch.utils.data.Dataset):
    def __init__(self, dataset, transform=None):
        self.dataset = dataset
        self.transforms = transform

    def __getitem__(self, index):
        result = {}
        for k in self.dataset.keys:
            result[k] = np.take(self.dataset.get_data()[k], index, axis=0)

        if self.transforms is not None:
            for k, transform in self.transforms.iteritems():
                result[k] = transform(result[k])

        return result

    def __len__(self):
        return self.dataset.get_data()[self.dataset.keys[0]].shape[0]


class VideoSampler(torch.utils.data.Dataset):
    def __init__(self, dataset, video_length, every_nth=1, transform=None):
        self.dataset = dataset
        self.video_length = video_length
        self.unique_ids = np.unique(self.dataset.get_data()['video_ids'])
        self.every_nth = every_nth
        self.transforms = transform

    def __getitem__(self, item):
        result = {}
        ids = self.dataset.get_data()['video_ids'] == self.unique_ids[item]
        ids = np.squeeze(np.squeeze(np.argwhere(ids)))
        for k in self.dataset.keys:
            result[k] = np.take(self.dataset.get_data()[k], ids, axis=0)

        subsequence_idx = None
        print (result[k].shape[0])

        # videos can be of various length, we randomly sample sub-sequences
        if result[k].shape[0] > self.video_length:
            needed = self.every_nth * (self.video_length - 1)
            gap = result[k].shape[0] - needed
            start = 0 if gap == 0 else np.random.randint(0, gap, 1)[0]
            subsequence_idx = np.linspace(start, start + needed, self.video_length, endpoint=True, dtype=np.int32)
        elif result[k].shape[0] == self.video_length:
            subsequence_idx = np.arange(0, self.video_length)
        else:
            print ("Length is too short id - {}, len - {}".format(self.unique_ids[item], result[k].shape[0]))

        if subsequence_idx:
            for k in self.dataset.keys:
                result[k] = np.take(result[k], subsequence_idx, axis=0)
        else:
            print (result[self.dataset.keys[0]].shape)

        if self.transforms is not None:
            for k, transform in self.transforms.iteritems():
                result[k] = transform(result[k])

        return result

    def __len__(self):
        return len(self.unique_ids)

def video_transform(video, image_transform):
    # apply image transform to every frame in a video
    vid = []
    for im in video:
        vid.append(image_transform(im))

    vid = torch.stack(vid)
    # vid. 10, 3, 64, 64
    vid = vid.permute(1, 0, 2, 3)
    # vid. 3, 10, 64, 64
    return vid

def get_loader(dataroot, image_size, n_channels, image_batch, video_batch, video_length):

    image_transforms = transforms.Compose([
        Image.fromarray,
        transforms.Scale(image_size),
        transforms.ToTensor(),
        # lambda x: x[:n_channels, ::],
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    video_transforms = functools.partial(video_transform, image_transform=image_transforms)

    dataset = VideoFolderDataset(dataroot)
    
    image_dataset = ImageDataset(dataset, image_transforms)
    video_dataset = VideoDataset(dataset, video_length, 2, video_transforms)

    image_loader = DataLoader(image_dataset, batch_size=image_batch, drop_last=True, shuffle=True)
    video_loader = DataLoader(video_dataset, batch_size=video_batch, drop_last=True, shuffle=True)

    return image_loader, video_loader
