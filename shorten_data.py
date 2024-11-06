from pathlib import Path
import numpy as np
import pandas as pd
import logging
from typing import Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def downsample_frequencies(frequencies: np.ndarray, magnitude_matrix: np.ndarray, factor: int) -> Tuple[np.ndarray, np.ndarray]:
    """Downsample frequency data using maximum pooling to retain important features."""
    if factor <= 1:
        return frequencies, magnitude_matrix

    num_frequencies = len(frequencies)
    new_num_frequencies = num_frequencies // factor
    new_frequencies = []
    new_magnitude_matrix = np.zeros((magnitude_matrix.shape[0], new_num_frequencies))

    for i in range(new_num_frequencies):
        start = i * factor
        end = min(start + factor, num_frequencies)
        
        # Take mean of frequency band
        new_frequencies.append(np.mean(frequencies[start:end]))
        # Use max pooling for magnitude to preserve peaks
        new_magnitude_matrix[:,i] = np.max(magnitude_matrix[:,start:end], axis=1)

    return np.array(new_frequencies), new_magnitude_matrix

def process_and_save_shortened_data(viz_data_dir: Path, output_dir: Path, time_downsample_factor: int = 10, freq_downsample_factor: int = 2):
    """Process all fiber data and save shortened versions."""
    output_dir.mkdir(exist_ok=True, parents=True)
    
    for group in [1, 2]:
        for fiber in range(1, 6):
            fiber_name = f"fiber_{group}_{fiber}"
            logging.info(f"Processing {fiber_name}")
            
            try:
                # Load data
                timestamp_df = pd.read_parquet(viz_data_dir / f"{fiber_name}_timestamps.parquet")
                frequencies = np.load(viz_data_dir / f"{fiber_name}_frequencies.npy")
                magnitude_matrix = np.load(viz_data_dir / f"{fiber_name}_magnitude_matrix.npy")
                print(magnitude_matrix.shape)
                print(timestamp_df.shape)
                
                # Filter valid data
                valid_data = timestamp_df[timestamp_df['has_data']]
                valid_indices = valid_data.index
                valid_indices = valid_indices[valid_indices < magnitude_matrix.shape[0]]
                timestamps = pd.to_datetime(valid_data['timestamp']).values
                
                # Filter magnitude matrix
                magnitude_matrix = magnitude_matrix[valid_indices,:]
                
                # Apply time downsampling
                timestamps = timestamps[::time_downsample_factor]
                magnitude_matrix = magnitude_matrix[::time_downsample_factor, :]
                
                # Apply frequency downsampling
                frequencies, magnitude_matrix = downsample_frequencies(
                    frequencies, magnitude_matrix, freq_downsample_factor
                )
                
                # Save shortened data
                np.save(output_dir / f"{fiber_name}_frequencies_short.npy", frequencies)
                np.save(output_dir / f"{fiber_name}_magnitude_matrix_short.npy", magnitude_matrix)
                pd.DataFrame({'timestamp': timestamps, 'has_data': True}).to_parquet(
                    output_dir / f"{fiber_name}_timestamps_short.parquet"
                )
                
                logging.info(f"Saved shortened data for {fiber_name}")
                logging.info(f"Original shape: {len(valid_indices)}x{len(frequencies)}")
                logging.info(f"New shape: {len(timestamps)}x{len(frequencies)}")
                
            except Exception as e:
                logging.error(f"Error processing {fiber_name}: {str(e)}")

if __name__ == "__main__":
    project_dir = Path(__file__).parent.parent
    print(project_dir)
    viz_data_dir = project_dir / "primavera_app" / "prepared_data"
    output_dir = project_dir / "primavera_app" / "shortened_data"
    
    process_and_save_shortened_data(viz_data_dir, output_dir)
