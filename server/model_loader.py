import torch
import torchvision
from torchvision.models.segmentation import deeplabv3_resnet50
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
<<<<<<< Updated upstream
=======
import os

class_names_9 = [
    "background (Arka Plan)",
    "double_plant (Çift Tohum)",
    "drydown (Kuruma)",
    "endrow (Tarla Kenarı)",
    "nutrient_deficiency (Besin Eksikliği)",
    "planter_skip (Atlanan Alan)",
    "water (Su Birikintisi)",
    "waterway (Doğal Su Yolu)",
    "weed_cluster (Yabani Ot Kümeleri)"
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
>>>>>>> Stashed changes

class AnomalyDetector:
    def __init__(self, model_path="models/deep_labv3/deeplabv3_resnet_best.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path)
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                              std=[0.229, 0.224, 0.225])
        ])

    def _load_model(self, model_path):
        model = deeplabv3_resnet50(pretrained=False)
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.eval()
        model.to(self.device)
        return model

    def detect_anomaly(self, image):
        """
        Detect anomalies in the given image
        Args:
            image: PIL Image or numpy array
        Returns:
            dict: Contains anomaly score and binary decision
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        input_tensor = self.transform(image).unsqueeze(0)
        input_tensor = input_tensor.to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)['out']
<<<<<<< Updated upstream
            prediction = torch.sigmoid(output)
            
        # Anomali skoru hesaplama (örnek bir yaklaşım)
        anomaly_score = float(prediction.mean().cpu().numpy())
        is_anomaly = anomaly_score > 0.5
=======
            predictions = torch.softmax(output, dim=1)[0]
            class_probabilities = predictions.mean(dim=(1, 2)).cpu().numpy()
        max_prob_idx = int(np.argmax(class_probabilities))
        max_prob = float(class_probabilities[max_prob_idx])
        anomaly_score = float(sum(class_probabilities[1:]))
        max_non_bg = float(max(class_probabilities[1:]))
        is_anomaly = max_non_bg > 0.2  # background dışı herhangi bir sınıf %20'den büyükse
        status = "anomaly" if is_anomaly else "normal"
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
            "is_anomaly": is_anomaly,
            "anomaly_score": anomaly_score,
            "detected_anomalies": detected_anomalies,
            "status": status,
            "confidence_scores": {name: float(prob) for name, prob in zip(self.class_names, class_probabilities)}
        }
        if return_probs:
            result["probs"] = class_probabilities
        print("anomaly_score:", anomaly_score, "max_non_bg:", max_non_bg, "is_anomaly:", is_anomaly, "status:", status)
        return result
>>>>>>> Stashed changes

        return {
            "anomaly_score": anomaly_score,
            "is_anomaly": is_anomaly,
            "status": "anomaly" if is_anomaly else "normal"
        } 