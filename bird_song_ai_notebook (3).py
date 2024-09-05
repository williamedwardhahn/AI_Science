# -*- coding: utf-8 -*-
"""Bird Song AI Notebook.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-dIw9gzpbeU8s-zrKzJFAVahLd2phNoT
"""

# Import necessary libraries
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import requests

# Function to download and save the audio file
def download_audio(url, file_name):
    response = requests.get(url)
    with open(file_name, 'wb') as file:
        file.write(response.content)

# Function to plot the spectrogram
def plot_spectrogram(y, sr, title):
    # Compute the short-time Fourier transform (STFT) of the audio
    D = np.abs(librosa.stft(y))

    # Convert the STFT into a log-scaled spectrogram
    S_db = librosa.amplitude_to_db(D, ref=np.max)

    # Plot the spectrogram
    plt.figure(figsize=(10, 6))
    librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title(title)
    plt.show()

# Function to load and plot the audio waveform and spectrogram
def load_and_plot_audio(file_path):
    # Load the audio file
    y, sr = librosa.load(file_path)

    # Plot the waveform
    plt.figure(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.show()

    # Plot the spectrogram
    plot_spectrogram(y, sr, 'Spectrogram')

# Download the audio file from the provided URL
audio_url = 'https://soundcamp.org/sounds/382/birdsong_in_woodland_DGc.wav'
audio_file = 'birdsong_in_woodland.wav'
download_audio(audio_url, audio_file)

# Load and plot the audio
load_and_plot_audio(audio_file)









/content/drive/MyDrive/birdsong_archive/songs/songs/xc101371.flac

"""# Dataset"""

import pandas as pd
import torch
import os
import librosa
from sklearn.preprocessing import LabelEncoder
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Path to the metadata and audio files in Google Drive
metadata_path = '/content/drive/MyDrive/birdsong_archive/birdsong_metadata.csv'
files_directory = '/content/drive/MyDrive/birdsong_archive/songs/songs/'

# Load the metadata
metadata = pd.read_csv(metadata_path)

# Initialize label encoder
label_encoder = LabelEncoder()

# Encode the bird names (english_cname) to numerical labels
metadata['encoded_label'] = label_encoder.fit_transform(metadata['english_cname'])

# List to hold data and labels
data_list = []
label_list = []

# Function to load a single audio file
def load_file(file_path, duration=10):
    # Use librosa to load only the first 'duration' seconds of the audio file
    audio_data, _ = librosa.load(file_path, sr=None, duration=duration)  # Adjust duration if needed
    return torch.tensor(audio_data)

# Loop through file IDs and load the corresponding files
for i, row in metadata.iterrows():
    file_id = row['file_id']
    file_path = os.path.join(files_directory, f"xc{file_id}.flac")  # Construct the file path
    if os.path.exists(file_path):
        print(f"Processing: {file_path}")
        try:
            file_data = load_file(file_path)
            data_list.append(file_data)
            label_list.append(row['encoded_label'])  # Use the encoded label
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    else:
        print(f"File {file_path} not found!")

# Check if any data was loaded
if data_list:
    # Convert lists to tensors
    data_tensor = torch.nn.utils.rnn.pad_sequence(data_list, batch_first=True)  # Padding for varying lengths
    label_tensor = torch.tensor(label_list)

    # Save tensors back to Google Drive
    torch.save(data_tensor, '/content/drive/MyDrive/birdsong_archive/birdsong_data_tensor.pt')
    torch.save(label_tensor, '/content/drive/MyDrive/birdsong_archive/birdsong_labels_tensor.pt')

    print("Tensors saved successfully.")
else:
    print("No data was processed.")





import torch
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Load the tensors from Google Drive
data_tensor = torch.load('/content/drive/MyDrive/birdsong_archive/birdsong_data_tensor.pt')
label_tensor = torch.load('/content/drive/MyDrive/birdsong_archive/birdsong_labels_tensor.pt')

# Load the metadata to map the encoded labels back to the bird names
metadata_path = '/content/drive/MyDrive/birdsong_archive/birdsong_metadata.csv'
metadata = pd.read_csv(metadata_path)

# Initialize label encoder to match the one used earlier
label_encoder = LabelEncoder()
metadata['encoded_label'] = label_encoder.fit_transform(metadata['english_cname'])

# Create a dictionary to map encoded labels back to the original bird names
label_decoder = dict(zip(metadata['encoded_label'], metadata['english_cname']))

# Function to create and display a spectrogram from tensor data
def create_spectrogram_from_tensor(audio_tensor, sr, ax, label):
    # Convert tensor to numpy array and generate a mel spectrogram
    audio_data = audio_tensor.numpy()
    S = librosa.feature.melspectrogram(y=audio_data, sr=sr, n_mels=128, fmax=8000)
    S_db = librosa.power_to_db(S, ref=np.max)

    # Display the spectrogram
    librosa.display.specshow(S_db, sr=sr, ax=ax, x_axis='time', y_axis='mel')
    ax.set_title(label, fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])

# Parameters
num_samples = 3  # Number of samples per label to display
unique_labels = torch.unique(label_tensor).tolist()  # Get unique labels

# Sample rate assumption (adjust based on your data)
sample_rate = 22050  # Assuming standard sample rate, modify if needed

# Loop through each unique label and create a separate montage
for encoded_label in unique_labels:
    # Get the indices of the samples with this label
    indices = (label_tensor == encoded_label).nonzero(as_tuple=True)[0]

    # Create a new figure for each label
    bird_name = label_decoder[encoded_label]  # Decode the label
    num_plots = min(len(indices), num_samples)  # Limit the number of plots per label

    # Create a figure for the current bird species
    fig, axs = plt.subplots(1, num_plots, figsize=(15, 3))  # 1 row, num_plots columns
    fig.suptitle(f"Spectrograms for {bird_name}", fontsize=16)

    # Plot the spectrograms for this label
    for j in range(num_plots):
        idx = indices[j].item()
        audio_tensor = data_tensor[idx]
        ax = axs[j] if num_plots > 1 else axs  # Handle single column case
        create_spectrogram_from_tensor(audio_tensor, sample_rate, ax, bird_name)

    # Adjust layout and show the figure
    plt.tight_layout()
    plt.show()

