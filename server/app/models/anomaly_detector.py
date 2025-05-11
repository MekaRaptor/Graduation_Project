import torch
import torchvision
from torchvision.models.segmentation import deeplabv3_resnet50
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import os

class AnomalyDetector:
    # Sınıf isimleri
    class_names = [
        "normal",           # 0
        "hastalik",        # 1
        "zararli",         # 2
        "su_stresi",       # 3
        "besin_eksikligi", # 4
        "yabanci_ot",      # 5
        "hasar",           # 6
        "olgunlasma",      # 7
        "diger"            # 8
    ]

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_path = os.path.join(os.path.dirname(__file__), "deeplabv3_rgbnir_best.pth")
        self.model = self._load_model(model_path)
        
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Lambda(lambda x: torch.cat([x, torch.zeros(1, x.shape[1], x.shape[2])], dim=0)),
            transforms.Normalize(mean=[0.485, 0.456, 0.406, 0], 
                              std=[0.229, 0.224, 0.225, 1])
        ])

    def _load_model(self, model_path):
        # Özel model mimarisi oluştur
        model = deeplabv3_resnet50(pretrained=False, aux_loss=True)
        
        # Giriş katmanını 4 kanala çıkar (RGB + NIR)
        old_conv = model.backbone.conv1
        new_conv = torch.nn.Conv2d(4, 64, kernel_size=7, stride=2, padding=3, bias=False)
        new_conv.weight.data[:, :3, :, :] = old_conv.weight.data
        new_conv.weight.data[:, 3:, :, :] = 0
        model.backbone.conv1 = new_conv
        
        # Çıkış katmanını 9 sınıfa ayarla
        old_classifier = model.classifier[-1]
        in_channels = old_classifier.in_channels
        model.classifier[-1] = torch.nn.Conv2d(in_channels, len(self.class_names), kernel_size=1)
        
        # Model ağırlıklarını yükle
        state_dict = torch.load(model_path, map_location=self.device)
        
        # Auxiliary classifier ağırlıklarını kaldır
        state_dict = {k: v for k, v in state_dict.items() if not k.startswith('aux_classifier')}
        
        model.load_state_dict(state_dict, strict=False)
        model.eval()
        model.to(self.device)
        return model

    def detect_anomaly(self, image):
        """
        Detect anomalies in the given image
        Args:
            image: PIL Image or numpy array
        Returns:
            dict: Contains detailed anomaly analysis
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Görüntüyü ön işleme
        input_tensor = self.transform(image).unsqueeze(0)
        input_tensor = input_tensor.to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)['out']
            predictions = torch.softmax(output, dim=1)[0]  # Softmax uygula
            
            # Her sınıf için olasılıkları hesapla
            class_probabilities = predictions.mean(dim=(1, 2)).cpu().numpy()
            
            # En yüksek olasılıklı sınıfı bul
            max_prob_idx = int(np.argmax(class_probabilities))  # numpy.int64'ü int'e çevir
            max_prob = float(class_probabilities[max_prob_idx])  # numpy.float32'yi float'a çevir
            
            # Tüm anomali sınıfları için toplam olasılık
            anomaly_prob = float(sum(class_probabilities[1:]))  # numpy.float32'yi float'a çevir
            
            # Tespit edilen anomalileri listele (threshold üstündekiler)
            threshold = 0.1  # Minimum olasılık eşiği
            detected_anomalies = [
                {
                    "type": self.class_names[i],
                    "probability": float(class_probabilities[i]),  # numpy.float32'yi float'a çevir
                    "severity": "yüksek" if class_probabilities[i] > 0.5 else "orta" if class_probabilities[i] > 0.3 else "düşük"
                }
                for i in range(1, len(self.class_names))  # normal sınıfı hariç
                if class_probabilities[i] > threshold
            ]

        return {
            "filename": getattr(image, 'filename', 'unknown'),
            "primary_class": {
                "name": self.class_names[max_prob_idx],
                "probability": max_prob
            },
            "is_anomaly": bool(max_prob_idx != 0),  # numpy.bool_'u bool'a çevir
            "anomaly_score": anomaly_prob,
            "detected_anomalies": detected_anomalies,
            "status": "anomaly" if max_prob_idx != 0 else "normal",
            "confidence_scores": {
                name: float(prob)  # numpy.float32'yi float'a çevir
                for name, prob in zip(self.class_names, class_probabilities)
            }
        } 