import torchvision.transforms as transforms 


transform = transforms.Compose([
    transforms.Resize((256, 256))
    transforms.ToTensor(),
    transforms.Normalize(mean = [.5, .5, .5], std = [.5, .5, .5])
])

# Hyperparameters
BATCH_SIZE = 8
LR = 2e-4
NUM_EPOCHS = 20 
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
LAMBDA_CYCLE = 10
LAMBDA_ID = 0
