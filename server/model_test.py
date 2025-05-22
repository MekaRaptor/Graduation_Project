import torch
import os
from torchvision.models.segmentation import deeplabv3_resnet50
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

def analyze_model_structure(model_path):
    """
    Model yapısını ve özelliklerini incele
    """
    print(f"Model dosyası inceleniyor: {model_path}")
    
    # Model dosyasının varlığını kontrol et
    if not os.path.exists(model_path):
        print(f"HATA: Model dosyası bulunamadı: {model_path}")
        return
    
    # Model yükleme
    try:
        state_dict = torch.load(model_path, map_location="cpu")
        print(f"Model yüklendi. Toplam parametre sayısı: {len(state_dict)}")
        
        # Çıkış katmanını ve diğer önemli parametreleri bul
        classifier_keys = [k for k in state_dict.keys() if 'classifier' in k]
        output_layer_keys = [k for k in state_dict.keys() if 'classifier' in k and 'weight' in k]
        
        if output_layer_keys:
            output_key = output_layer_keys[-1]
            output_layer = state_dict[output_key]
            
            # Çıkış sınıflarının sayısını belirle
            num_classes = output_layer.shape[0]
            print(f"\nÇıkış katmanı: {output_key}")
            print(f"Çıkış katmanı boyutları: {output_layer.shape}")
            print(f"Model çıkış sınıflarının sayısı: {num_classes}")
            
            # Classifier parametrelerini incele
            print("\nClassifier katmanları:")
            for key in classifier_keys:
                print(f"  - {key}: {state_dict[key].shape}")
                
        else:
            print("\nÇıkış katmanı bulunamadı!")
            
        # Model dosyası adını incele
        model_name = os.path.basename(model_path)
        print(f"\nModel dosya adı: {model_name}")
        
        # Bazı özel parametreleri arama
        if any('iou' in k.lower() for k in state_dict.keys()):
            print("\nIoU ile ilgili parametreler:")
            for k in [k for k in state_dict.keys() if 'iou' in k.lower()]:
                print(f"  - {k}: {state_dict[k].shape}")
                
        return state_dict
    
    except Exception as e:
        print(f"Model analiz edilirken hata oluştu: {e}")
        return None

def test_model_inference(model_path, num_classes, expected_iou=None):
    device = torch.device("cpu")
    model = deeplabv3_resnet50(pretrained=False)
    old_conv = model.backbone.conv1
    new_conv = torch.nn.Conv2d(4, 64, kernel_size=7, stride=2, padding=3, bias=False)
    new_conv.weight.data[:, :3, :, :] = old_conv.weight.data
    new_conv.weight.data[:, 3:, :, :] = 0
    model.backbone.conv1 = new_conv
    model.classifier[-1] = torch.nn.Conv2d(256, num_classes, kernel_size=1)
    if hasattr(model, "aux_classifier") and model.aux_classifier is not None:
        model.aux_classifier[-1] = torch.nn.Conv2d(256, num_classes, kernel_size=1)
    state_dict = torch.load(model_path, map_location=device)
    state_dict = {k: v for k, v in state_dict.items() if not k.startswith('aux_classifier') or v.shape[0] == num_classes}
    try:
        model.load_state_dict(state_dict, strict=False)
        print("\nModel yükleme: BAŞARILI (strict=False)")
    except Exception as e:
        print(f"\nModel yükleme hatası (strict=False): {e}")
    model.eval()
    dummy_input = torch.randn(1, 4, 512, 512)
    with torch.no_grad():
        try:
            outputs = model(dummy_input)
            print("\nÖrnek çıkarım: BAŞARILI")
            print(f"Çıkış boyutları: {outputs['out'].shape}")
            predictions = torch.softmax(outputs['out'], dim=1)[0]
            print(f"Tahmin boyutları: {predictions.shape}")
            class_probabilities = predictions.mean(dim=(1, 2)).numpy()
            print("\nSınıf olasılıkları:")
            for i, prob in enumerate(class_probabilities):
                print(f"Sınıf {i}: {prob:.6f}")
        except Exception as e:
            print(f"\nÇıkarım hatası: {e}")
            import traceback
            traceback.print_exc()

def test_model_with_expected_iou(model_path):
    state_dict = analyze_model_structure(model_path)
    if state_dict:
        output_layer_keys = [k for k in state_dict.keys() if 'classifier' in k and 'weight' in k]
        if output_layer_keys:
            output_key = output_layer_keys[-1]
            num_classes = state_dict[output_key].shape[0]
            print(f"\nModel ({num_classes} sınıf) ile test başlatılıyor.")
            test_model_inference(model_path, num_classes)
        else:
            print("Çıkış katmanı bulunamadığı için test yapılamıyor!")

if __name__ == "__main__":
    # Sadece yeni 10 sınıflı modeli test et
    script_dir = os.path.dirname(os.path.abspath(__file__))
    finalv2_model_path = os.path.join(script_dir, "app", "models", "deeplabv3_rgbnir_finalv2.pth")
    if os.path.exists(finalv2_model_path):
        test_model_with_expected_iou(finalv2_model_path)
    else:
        print(f"Model bulunamadı: {finalv2_model_path}") 