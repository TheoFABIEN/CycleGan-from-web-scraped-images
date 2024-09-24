import torch 
import os
import matplotlib.pyplot as plt
from torch.utils.data import Dataset
from PIL import Image 
from glob import glob
from pathlib import Path
import glob



class ImagesDataset(Dataset):

    def __init__(self, photos_path, anime_path, transforms):
        self.photos_path = Path(photos_path)
        self.anime_path = Path(anime_path)
        self.transform = transforms
        self.photos = os.listdir(photos_path)
        self.anime = os.listdir(anime_path)
        self.l_photos = len(self.photos)
        self.l_anime = len(self.anime)

    def __len__(self):
        return max(self.l_photos, self.l_anime)

    def __getitem__(self, idx):
        photo = Image.open(
            (self.photos_path).joinpath(self.photos[idx % self.l_photos])
        ).convert('RGB')
        anime = Image.open(
                (self.anime_path).joinpath(self.anime[idx % self.l_anime])
        ).convert('RGB')
        photo = self.transform(photo)
        anime = self.transform(anime)
        return photo, anime



