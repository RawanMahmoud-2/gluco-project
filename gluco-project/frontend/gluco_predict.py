import torch
from gluco_model import CNN_GRU_Model
from gluco_preprocessing import preprocess_ppg


def glucose_predict(ppg):

    # 1. Check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # 2. Load checkpoint
    checkpoint = torch.load(
        r"/gluco-project/gluco-project/frontend/cnn_gru_model_full_enhanced_600Epochs.pth",
        map_location=device
    )

    # 3. Rebuild model and load weights
    loaded_model = CNN_GRU_Model().to(device)
    loaded_model.load_state_dict(checkpoint["model_state"])
    loaded_model.eval()   # set to inference mode

    # 4. Restore BG scaler
    bg_scaler = checkpoint["bg_scaler"]

    # Shape for model input
    ppg_signal = ppg[ppg['ppg'] > 0]
    sig_norm = preprocess_ppg(ppg_signal)
    new_ppg_tensor = torch.FloatTensor(sig_norm).reshape(1, -1, 1).to(device)

    with torch.no_grad():
        predicted_bg_n = loaded_model(new_ppg_tensor)
        predicted_bg_n = predicted_bg_n.detach().cpu().numpy().reshape(-1,1)

        # Inverse transform using the BG scaler saved in dataset
        predicted_bg_n = bg_scaler.inverse_transform(predicted_bg_n)

    return predicted_bg_n