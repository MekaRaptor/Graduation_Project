import torch
import torchvision
from torchvision.models.segmentation import deeplabv3_resnet50
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

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
            prediction = torch.sigmoid(output)
            
        # Anomali skoru hesaplama (örnek bir yaklaşım)
        anomaly_score = float(prediction.mean().cpu().numpy())
        is_anomaly = anomaly_score > 0.5

        return {
            "anomaly_score": anomaly_score,
            "is_anomaly": is_anomaly,
            "status": "anomaly" if is_anomaly else "normal"
        } 