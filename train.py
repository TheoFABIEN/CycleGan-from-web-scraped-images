import torch 
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm 
import matplotlib.pyplot as plt 
from dataset_class import ImagesDataset
from model import Generator, Discriminator
from pathlib import Path
from config import *


# Instanciate dataset and dataloader
dataset = ImagesDataset(
        photos_path = 'D:\ML_Projects\CycleGan\Dataset\Photos',
        anime_path = 'D:\ML_Projects\CycleGan\Dataset\Anime',
        transforms = transform
)

dataloader = DataLoader(
    dataset,
    batch_size = BATCH_SIZE,
    shuffle = True
)


L1_loss = nn.L1Loss()
mse_loss = nn.MSELoss()

g_scaler = torch.cuda.amp.GradScaler()
d_scaler = torch.cuda.amp.GradScaler()

#Creating model instances
disc_photo = Discriminator(in_channels = 3).to(DEVICE)
disc_anime = Discriminator(in_channels = 3).to(DEVICE)
gen_anime = Generator(img_channels = 3, num_residuals = 9).to(DEVICE)
gen_photo = Generator(img_channels = 3, num_residuals = 9).to(DEVICE)

# Optimizers
opt_disc = optim.Adam(
        list(disc_anime.parameters()) + list(disc_photo.parameters()),
        lr = LR,
        betas = (.5, .999)
)
opt_gen = optim.Adam(
        list(gen_anime.parameters()) + list(gen_photo.parameters()),
        lr = LR,
        betas = (.5, .999)
)


for epoch in range(NUM_EPOCHS):

    running_disc_loss = 0.
    running_gen_loss = 0.

    for photo, anime in tqdm(dataloader, leave = True):

        photo = photo.to(DEVICE)
        anime = anime.to(DEVICE)

        fake_photo = gen_photo(anime)
        disc_photo_real = disc_photo(photo)
        disc_photo_fake = disc_photo(fake_photo.detach())
        disc_photo_real_loss = mse_loss(
                disc_photo_real,
                torch.ones_like(disc_photo_real)
        )
        disc_photo_fake_loss = mse_loss(
                disc_photo_fake,
                torch.zeros_like(disc_photo_fake)
        )
        disc_photo_loss = disc_photo_real_loss + disc_photo_fake_loss

        fake_anime = gen_anime(photo)
        disc_anime_real = disc_anime(anime)
        disc_anime_fake = disc_anime(fake_anime.detach())
        disc_anime_real_loss = mse_loss(
                disc_anime_real,
                torch.ones_like(disc_anime_real)
        )
        disc_anime_fake_loss = mse_loss(
                disc_anime_fake,
                torch.zeros_like(disc_anime_fake)
        )
        disc_anime_loss = disc_anime_real_loss + disc_anime_fake_loss
    
        # Get the total discriminator loss
        disc_loss = (disc_photo_loss + disc_anime_loss) / 2
        running_disc_loss += disc_loss / len(dataloader)

        # Update the weights
        opt_disc.zero_grad()
        d_scaler.scale(disc_loss).backward()
        d_scaler.step(opt_disc)
        d_scaler.update()


        #Train the generator now

        with torch.cuda.amp.autocast():

            # Adversarial loss
            disc_photo_fake = disc_photo(fake_photo)
            disc_anime_fake = disc_anime(fake_anime)
            loss_gen_anime = mse_loss(
                    disc_anime_fake,
                    torch.ones_like(disc_anime_fake)
            )
            loss_gen_photo = mse_loss(
                    disc_photo_fake,
                    torch.ones_like(disc_photo_fake)
            )

            # Cycle loss
            cycle_anime = gen_anime(fake_photo)
            cycle_photo = gen_photo(fake_anime)
            cycle_anime_loss = L1_loss(anime, cycle_anime)
            cycle_photo_loss = L1_loss(photo, cycle_photo)

            #Identity loss
            id_anime = gen_anime(anime)
            id_photo = gen_photo(photo)
            id_anime_loss = L1_loss(anime, id_anime)
            id_photo_loss = L1_loss(photo, id_photo)

            # All losses together
            gen_loss = (
                    loss_gen_anime + loss_gen_photo +
                    cycle_anime_loss * LAMBDA_CYCLE + cycle_photo_loss * LAMBDA_CYCLE + 
                    id_anime_loss * LAMBDA_ID + id_photo_loss * LAMBDA_ID
            )

            running_gen_loss += gen_loss / len(dataloader)

            opt_gen.zero_grad()
            g_scaler.scale(gen_loss).backward()
            g_scaler.step(opt_gen)
            g_scaler.update()

    print(
            f"Epoch {epoch + 1}. Generator loss by epoch: {running_gen_loss}, \
                    Discriminator loss by epoch: {running_disc_loss}."
    )


saved_models_path = Path('D:\ML_Projects\CycleGan\Saved_models')

torch.save(disc_photo.state_dict(), saved_models_path)
torch.save(disc_anime.state_dict(), saved_models_path)
torch.save(disc_anime.state_dict(), saved_models_path)
torch.save(gen_photo.state_dict(), saved_models_path)



        





