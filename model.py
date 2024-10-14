import torch 
import torch.nn as nn
from config import *



class ConvBlock(nn.Module):
    """
    Convolutional block used in both the generator and the discriminator.

    Parameters:
        in_channels (int): Number of input channels.
        out_channels(int): Number of output channels.
        down (bool, optional): If True (default), applies standard convolution. 
                               If False, applies transpose convolution.
        use_act (bool, optional): If True (default), adds ReLU activation.
                                  If False, skips activation.
        **kwargs: additional arguments to pass to the convolution layer.
    """

    def __init__(self, in_channels, out_channels, down = True, use_act = True, **kwargs):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, padding_mode = 'reflect', **kwargs)
            if down
            else nn.ConvTranspose2d(in_channels, out_channels, **kwargs),
            nn.InstanceNorm2d(out_channels),
            nn.ReLU(inplace = True) if use_act else nn.Identity()
        )
    def forward(self, x):
        return self.conv(x)

    
class ResidualBlock(nn.Module):
    """
    Residual block that adds the output of two convolutional layers to the 
    original input.

    Parameters:
        channels (int): Number of input and output channels.
    """

    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            ConvBlock(channels, channels, kernel_size = 3, padding = 1),
            ConvBlock(channels, channels, use_act = False, kernel_size = 3, padding = 1)
        )
        
    def forward(self, x):
        return x + self.block(x)

    
class Generator(nn.Module):
    """
    Generator architecture use in the CycleGAN.

    Parameters:
        img_channels (int, optional): Number of input channels (defaults to 3).
        num_features (int, optional): Number of features in the convolutional
                                      layer (defaults to  64).
        num_residuals (int, optional): Number of residual blocks to use in the 
                                       network (default to 9).
    """

    def __init__(self, img_channels = 3, num_features = 64, num_residuals = 9):
        super().__init__()
        self.initial = nn.Sequential(
            nn.Conv2d(
                img_channels, 64, kernel_size = 7, stride = 1, 
                padding = 3, padding_mode = 'reflect'
            ),
            nn.ReLU(inplace = True) 
        )
        self.down_blocks = nn.ModuleList(
            [
                ConvBlock(
                    num_features, num_features*2, kernel_size = 3, stride = 2, padding = 1
                ),
                ConvBlock(
                    num_features*2, num_features*4, kernel_size = 3, stride = 2, padding = 1
                ),
            ]
        )
        
        self.residual_blocks = nn.Sequential(
            *[ResidualBlock(num_features*4) for _ in range(num_residuals)]
        )
        self.up_blocks = nn.ModuleList(
            [
                ConvBlock(
                    num_features*4, num_features*2, down = False, kernel_size = 3, stride = 2,
                    adding = 1, output_padding = 1
                ),
                ConvBlock(
                    num_features*2, num_features, down = False, kernel_size = 3, stride = 2,
                    padding = 1, output_padding = 1
                ),
            ]   
        )
        self.last = nn.Conv2d(
            num_features, img_channels, kernel_size = 7, stride = 1, 
            padding = 3, padding_mode = 'reflect'
        )
        
    def forward(self, x):
        x = self.initial(x)
        for layer in self.down_blocks:
            x = layer(x)
        x = self.residual_blocks(x)
        for layer in self.up_blocks:
            x = layer(x)
        return torch.tanh(self.last(x))




class Block(nn.Module):
    """
    Convolutional block used in the discriminator model.

    Parameters:
        in_channels (int): Number of input channels.
        out_channels (int): Number of ouptut channels.
        stride (int): Stride parameter for the convolution.
    """

    def __init__(self, in_channels, out_channels, stride):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(
                in_channels, out_channels, 4, stride, 1, bias = True, 
                padding_mode = 'reflect'
            ),
            nn.InstanceNorm2d(out_channels),
            nn.LeakyReLU(.2)
        )
        
    def forward(self, x):
        return self.conv(x)

    
class Discriminator(nn.Module):
    """
    Discriminator architecture used in the CycleGAN.

    Parameters:
        in_channels (int, optional): Number of input channels (defaults to 3).
        features (list of int, optional): List of feature dimensions for each 
                                          convolutional block (default is 
                                          [64, 128, 256, 512]).
    """

    def __init__(self, in_channels = 3, features = [64, 128, 256, 512]):
        super().__init__()
        self.initial = nn.Sequential(
            nn.Conv2d(
                in_channels, features[0], kernel_size = 4, stride = 2, 
                padding = 1, padding_mode = 'reflect'
            ),
            nn.LeakyReLU(.2)
        )
        
        layers = []
        in_channels = features[0]
        for feature in features[1:]:
            layers.append(
                Block(in_channels, feature, stride = 1 if feature == features[-1] else 2)
            )
            in_channels = feature
        layers.append(
            nn.Conv2d(
                in_channels, 1, kernel_size = 4, stride = 1, 
                padding = 1, padding_mode = 'reflect'
            )
        )
        self.model = nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.initial(x)
        return torch.sigmoid(self.model(x))


