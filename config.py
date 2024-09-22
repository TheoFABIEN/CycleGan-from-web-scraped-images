import torchvision.transforms as transforms 


transform = transforms.Compose([
    transforms.Resize((256, 256))
    transforms.ToTensor(),
    transforms.Normalize(mean = [.5, .5, .5], std = [.5, .5, .5])
])
