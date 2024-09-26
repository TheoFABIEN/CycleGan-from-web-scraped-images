# Photo to Anime CycleGAN

A CycleGAN model trained from scratch using web-scraped images. 

### Motivation

CycleGAN (Cycle-Consistent Generative Adversarial Network) models are highly popular for image-to-image translation without the need for paired data. 
They have a wide range of applications, such as enhancing the resolution of images, colorize grayscale images and films or generate a realistic face from the drawing of a suspect.
These fascinating properties made me want to build my own CycleGAN project. 

Makoto Shinkai's animated movies have a unique an beautiful aesthetic. I was inspired to capture this beautiful style and apply it to real-world photos. 
At the intersection of technical applications and artistic expression, this project is was an opportunity experiment with visual content in the realm of Japanese animation. 

### Data acquisition 

The dataset was obtained from Google Images. It was cleaned manually to remove irrelevant elements.

### Results

I was able to obtain good results, especially after fine-tuning the LAMBDA_ID parameter, which controls the relative importance of identity loss. 
This is important because it prevents excessive modifications of the image. In my case, setting it to 0 at first led to poor color restitution. 

![general_plot](https://github.com/user-attachments/assets/b8e347c8-5643-4794-b736-9e02c500ed80)
