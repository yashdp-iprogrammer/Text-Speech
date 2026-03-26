# import numpy as np
# import soundfile as sf

# duration_seconds = 5
# sample_rate = 22050
# frequency = 440  # A4 note (audible)

# t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), endpoint=False)

# dummy = 0.5 * np.sin(2 * np.pi * frequency * t)

# sf.write("test.wav", dummy, sample_rate)

import torch
if torch.cuda.is_available():
    print('GPU AVAilable')
else:
    print("No GPU")