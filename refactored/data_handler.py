"""Data loading and processing functionality"""
from pathlib import Path
import logging
from typing import Tuple, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class DataLoader:
    """Handles loading and preprocessing of fiber data"""
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        logger.info(f"Initialized DataLoader with directory: {data_dir}")
        
    def load_timestamps(self, fiber_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load and validate timestamp data"""
        try:
            file_path = self.data_dir / f"{fiber_name}_timestamps.parquet"
            logger.debug(f"Loading timestamps from {file_path}")
            
            df = pd.read_parquet(file_path)
            valid_data = df[df['has_data']]
            
            if valid_data.empty:
                raise ValueError(f"No valid data points found for {fiber_name}")
                
            return pd.to_datetime(valid_data['timestamp']).values, valid_data.index
            
        except Exception as e:
            logger.error(f"Error loading timestamps for {fiber_name}: {str(e)}")
            raise

    def load_frequencies(self, fiber_name: str) -> np.ndarray:
        """Load frequency data"""
        try:
            file_path = self.data_dir / f"{fiber_name}_frequencies.npy"
            logger.debug(f"Loading frequencies from {file_path}")
            return np.load(file_path)
        except Exception as e:
            logger.error(f"Error loading frequencies for {fiber_name}: {str(e)}")
            raise

    def load_magnitude_matrix(self, fiber_name: str) -> np.ndarray:
        """Load magnitude matrix data"""
        try:
            file_path = self.data_dir / f"{fiber_name}_magnitude_matrix.npy"
            logger.debug(f"Loading magnitude matrix from {file_path}")
            return np.load(file_path)
        except Exception as e:
            logger.error(f"Error loading magnitude matrix for {fiber_name}: {str(e)}")
            raise

class FiberData:
    """Handles data processing for a single fiber"""
    def __init__(self, fiber_name: str, data_loader: DataLoader, 
                 time_downsample: int = 5, freq_downsample: int = 2):
        self.fiber_name = fiber_name
        self.data_loader = data_loader
        self.time_downsample = time_downsample
        self.freq_downsample = freq_downsample
        self.timestamps: Optional[np.ndarray] = None
        self.frequencies: Optional[np.ndarray] = None
        self.magnitude_matrix: Optional[np.ndarray] = None
        self.load_and_process_data()

    def load_and_process_data(self) -> None:
        """Load and process all fiber data"""
        try:
            # Load data
            self.timestamps, valid_indices = self.data_loader.load_timestamps(self.fiber_name)
            self.frequencies = self.data_loader.load_frequencies(self.fiber_name)
            magnitude_matrix = self.data_loader.load_magnitude_matrix(self.fiber_name)

            # Log shapes for debugging
            logger.debug(f"Loaded data shapes for {self.fiber_name}:")
            logger.debug(f"Timestamps: {self.timestamps.shape}")
            logger.debug(f"Frequencies: {self.frequencies.shape}")
            logger.debug(f"Magnitude matrix: {magnitude_matrix.shape}")

            # Process data
            self.process_magnitude_matrix(magnitude_matrix, valid_indices)
            self.apply_downsampling()
            
            logger.info(f"Successfully loaded and processed data for {self.fiber_name}")
            
        except Exception as e:
            logger.error(f"Error processing {self.fiber_name}: {str(e)}")
            raise

    def process_magnitude_matrix(self, matrix: np.ndarray, valid_indices: np.ndarray) -> None:
        """Process the magnitude matrix with validation"""
        valid_indices = valid_indices[valid_indices < matrix.shape[0]]
        self.magnitude_matrix = matrix[valid_indices, :]

    def apply_downsampling(self) -> None:
        """Apply time and frequency downsampling"""
        if self.timestamps is None or self.magnitude_matrix is None:
            raise ValueError("Data must be loaded before downsampling")
            
        # Time downsampling
        self.timestamps = self.timestamps[::self.time_downsample]
        self.magnitude_matrix = self.magnitude_matrix[::self.time_downsample, :]
        
        # Frequency downsampling
        if self.freq_downsample > 1 and self.frequencies is not None:
            self.frequencies, self.magnitude_matrix = self._downsample_frequencies()

    def _downsample_frequencies(self) -> Tuple[np.ndarray, np.ndarray]:
        """Downsample frequency data using maximum pooling"""
        if self.frequencies is None or self.magnitude_matrix is None:
            raise ValueError("Data must be loaded before downsampling")
            
        num_freqs = len(self.frequencies)
        new_num_freqs = num_freqs // self.freq_downsample
        
        # Calculate the actual size for reshaping
        time_points = self.magnitude_matrix.shape[0]
        remainder = num_freqs % self.freq_downsample
        
        if remainder != 0:
            # Adjust the frequencies array to be evenly divisible by freq_downsample
            new_size = new_num_freqs * self.freq_downsample
            self.frequencies = self.frequencies[:new_size]
            self.magnitude_matrix = self.magnitude_matrix[:, :new_size]
            num_freqs = new_size
        
        # Reshape for pooling
        try:
            reshaped_matrix = self.magnitude_matrix.reshape(
                time_points, new_num_freqs, self.freq_downsample)
            
            # Use numpy operations for better performance
            freq_ranges = np.array_split(self.frequencies, new_num_freqs)
            new_frequencies = np.array([freq.mean() for freq in freq_ranges])
            new_magnitude_matrix = np.max(reshaped_matrix, axis=2)
            
            logger.debug(f"Downsampled shapes for {self.fiber_name}:")
            logger.debug(f"New frequencies: {new_frequencies.shape}")
            logger.debug(f"New magnitude matrix: {new_magnitude_matrix.shape}")
            
            return new_frequencies, new_magnitude_matrix
            
        except Exception as e:
            logger.error(f"Error in downsampling for {self.fiber_name}: {str(e)}")
            logger.error(f"Matrix shape: {self.magnitude_matrix.shape}")
            logger.error(f"Attempted reshape: ({time_points}, {new_num_freqs}, {self.freq_downsample})")
            raise