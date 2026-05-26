import numpy as np
from scipy.signal import butter, filtfilt
import pywt
from sklearn.preprocessing import  MinMaxScaler


def wavelet_denoise(x, wavelet='db4', level=4):
    """Apply wavelet denoising"""
    if isinstance(x, torch.Tensor):
        x = x.detach().cpu().numpy()
    coeffs = pywt.wavedec(x, wavelet, level)
    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], value=0.4*np.std(coeffs[i]), mode='soft')
    x_denoised = pywt.waverec(coeffs, wavelet)
    return torch.tensor(x_denoised, dtype=torch.float32)


def preprocess_ppg(ppg_signal, fs=100):
    # 1. Flatten and cast
    x = np.array(ppg_signal, dtype=np.float32).ravel()
    
    # 2. Wavelet denoising
    x = wavelet_denoise(x)

    # 3. Bandpass filter
    band = (0.5, 7.0)
    b, a = butter(4, band, btype="band", fs=fs)
    x = filtfilt(b, a, x)

    # 4. Robust normalization (z-score)
    scaler = MinMaxScaler()
    x = scaler.fit_transform(x.reshape(-1,1)).ravel()

    return x