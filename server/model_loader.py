import torch
import torchvision
from torchvision.models.segmentation import deeplabv3_resnet50
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import os

class_names_9 = [
    "background",
    "double_plant",
    "drydown",
    "endrow",
    "nutrient_deficiency",
    "planter_skip",
    "water",
    "waterway",
    "weed_cluster"
]

class_names_10 = [
    "background",        # 0
    "double_plant",     # 1
    "drydown",          # 2
    "endrow",           # 3
    "nutrient_deficiency", # 4
    "planter_skip",     # 5
    "water",            # 6
    "waterway",         # 7
    "weed_cluster"      # 8
]

class AnomalyDetector:
    def __init__(self, model_path, num_classes=9, class_names=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_names = class_names if class_names is not None else class_names_9
        self.model = self._load_model(model_path, num_classes=num_classes)
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Lambda(lambda x: torch.cat([x, torch.zeros(1, x.shape[1], x.shape[2])], dim=0)),
            transforms.Normalize(mean=[0.485, 0.456, 0.406, 0], std=[0.229, 0.224, 0.225, 1])
        ])

    def _load_model(self, model_path, num_classes):
        model = deeplabv3_resnet50(weights=None, aux_loss=False)
        old_conv = model.backbone.conv1
        new_conv = torch.nn.Conv2d(4, 64, kernel_size=7, stride=2, padding=3, bias=False)
        new_conv.weight.data[:, :3, :, :] = old_conv.weight.data
        new_conv.weight.data[:, 3:, :, :] = 0
        model.backbone.conv1 = new_conv
        model.classifier[-1] = torch.nn.Conv2d(256, num_classes, kernel_size=1)
        if model.aux_classifier is not None:
            model.aux_classifier[-1] = torch.nn.Conv2d(256, num_classes, kernel_size=1)
        model.load_state_dict(torch.load(model_path, map_location=self.device), strict=False)
        model.eval()
        model.to(self.device)
        return model

    def detect_anomaly(self, image, return_probs=False):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.model(input_tensor)['out']
            predictions = torch.softmax(output, dim=1)[0]
            class_probabilities = predictions.mean(dim=(1, 2)).cpu().numpy()
        max_prob_idx = int(np.argmax(class_probabilities))
        max_prob = float(class_probabilities[max_prob_idx])
        status = "anomaly" if max_prob_idx != 0 else "normal"
        threshold = 0.2
        detected_anomalies = []
        if max_prob_idx != 0 and class_probabilities[max_prob_idx] > threshold:
            detected_anomalies.append({
                "type": self.class_names[max_prob_idx],
                "probability": float(class_probabilities[max_prob_idx]),
                "severity": "yüksek" if class_probabilities[max_prob_idx] > 0.5 else "orta" if class_probabilities[max_prob_idx] > 0.3 else "düşük"
            })
        result = {
            "primary_class": {
                "name": self.class_names[max_prob_idx],
                "probability": max_prob
            },
            "is_anomaly": status == "anomaly" and len(detected_anomalies) > 0,
            "anomaly_score": float(sum(class_probabilities[1:])),
            "detected_anomalies": detected_anomalies,
            "status": status,
            "confidence_scores": {name: float(prob) for name, prob in zip(self.class_names, class_probabilities)}
        }
        if return_probs:
            result["probs"] = class_probabilities
        return result

# Sadece deeplabv3_rgnir_best.pth modelini yükle
script_dir = os.path.dirname(os.path.abspath(__file__))
v4_path = os.path.join(script_dir, "app", "models", "deeplabv3_rgbnir_finalv4.pth")
anomaly_detector = AnomalyDetector(v4_path, num_classes=9, class_names=class_names_9)
