import torch
import torch.nn as nn
from nets.vgg import VGG16


class unetUp(nn.Module):
    """上采样单元   """
    def __init__(self, in_size, out_size):
        super(unetUp, self).__init__()
        self.conv1 = nn.Conv2d(in_size, out_size, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(out_size, out_size, kernel_size=3, padding=1)
        self.up = nn.UpsamplingBilinear2d(scale_factor=2)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, inputs1, inputs2):
        """前向传播"""
        outputs = torch.cat([inputs1, self.up(inputs2)], 1)
        outputs = self.conv1(outputs)
        outputs = self.relu(outputs)
        outputs = self.conv2(outputs)
        outputs = self.relu(outputs)
        return outputs

class Unet(nn.Module):
    """改进UNet全卷积神经网络"""
    def __init__(self, num_classes=21, in_channels=3, pretrained=False):
        """构造函数

        Args:
            num_classes (int, optional): 分类数. Defaults to 21.
            in_channels (int, optional): 通道数. Defaults to 3.
            pretrained (bool, optional): 是否载入预训练权重. Defaults to False.
        """
        super(Unet, self).__init__()
        self.vgg = VGG16(pretrained=pretrained,in_channels=in_channels)
        in_filters = [192, 384, 768, 1024]
        out_filters = [64, 128, 256, 512]
        # upsampling
        # 64,64,512
        self.up_concat4 = unetUp(in_filters[3], out_filters[3])
        # 128,128,256
        self.up_concat3 = unetUp(in_filters[2], out_filters[2])
        # 256,256,128
        self.up_concat2 = unetUp(in_filters[1], out_filters[1])
        # 512,512,64
        self.up_concat1 = unetUp(in_filters[0], out_filters[0])

        # final conv (without any concat)
        self.final = nn.Conv2d(out_filters[0], num_classes, 1)

    def forward(self, inputs):
        """前向传播

        Args:
            inputs (torch.tensor): 输入

        Returns:
            torch.tensor: 预测结果
        """ 
        feat1 = self.vgg.features[  :4 ](inputs)
        feat2 = self.vgg.features[4 :9 ](feat1)
        feat3 = self.vgg.features[9 :16](feat2)
        feat4 = self.vgg.features[16:23](feat3)
        feat5 = self.vgg.features[23:-1](feat4)

        up4 = self.up_concat4(feat4, feat5)
        up3 = self.up_concat3(feat3, up4)
        up2 = self.up_concat2(feat2, up3)
        up1 = self.up_concat1(feat1, up2)

        final = self.final(up1)
        
        return final

    def _initialize_weights(self, *stages):
        """初始化权重"""
        for modules in stages:
            for module in modules.modules():
                if isinstance(module, nn.Conv2d):
                    nn.init.kaiming_normal_(module.weight)
                    if module.bias is not None:
                        module.bias.data.zero_()
                elif isinstance(module, nn.BatchNorm2d):
                    module.weight.data.fill_(1)
                    module.bias.data.zero_()

