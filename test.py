import os
from pathlib import Path
import torch 
from model import Generator
import torchvision.transforms as transforms
from config import DEVICE, transform
import matplotlib.pyplot as plt
import random
from PIL import Image

# Create model instance 
gen_anime = Generator(img_channels = 3, num_residuals = 9).to(DEVICE)
gen_anime.load_state_dict(
        torch.load(
            "D:\ML_Projects\CycleGan\Saved_models\gen_anime.pth",
            weights_only = True
        )
)

# Predict on test images 

images_dir = "D:\ML_Projects\CycleGan\Dataset\Test_photos"

predictions_dir = "D:\ML_Projects\CycleGan\Predictions"

images_list = [
        os.path.join(images_dir, img)
        for img in random.sample(os.listdir(images_dir), 5)
]


fig, ax = plt.subplots(5, 2, figsize = (6, 12))
fig.tight_layout()

for i in range(5):

    original_image = Image.open(images_list[i]).convert('RGB')
    # Apply transformations
    original_image = transform(original_image)
    # Predict with the trained model
    predicted_image = None
    with torch.no_grad():
        predicted_image = gen_anime(original_image.unsqueeze(0).to(DEVICE))

    # Save the predictions 
    predicted_image = predicted_image.squeeze(0).permute(1, 2, 0).cpu() * .5 + .5
    output_path = os.path.join(predictions_dir, f"{i}.jpg")
    output_image = transforms.ToPILImage(mode = 'RGB')(predicted_image.permute(2, 0, 1))
    output_image.save(output_path)

    # Plot and save

    ax[i, 0].imshow(original_image.permute(1, 2, 0) * .5 + .5)
    ax[i, 1].imshow(predicted_image)

    ax[0, 0].set_title("Photo")
    ax[0, 1].set_title("Fake anime")
    
    ax[i, 0].axis("off")
    ax[i, 1].axis("off") 

plt.subplots_adjust(wspace = -0.2, hspace = 0.05, top = 0.95)
plt.savefig(os.path.join(predictions_dir, "general_plot.jpg"))
plt.show()


