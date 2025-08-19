HARDWARE_CONFIG = {
    # CPU training optimization
    "device": "cpu",
    "max_batch_size": 8,  # Conservative for CPU
    "gradient_accumulation": 4,  # Effective batch size: 32
    "max_sequence_length": 1024,  # Full T5 sequence length
    "mixed_precision": None,  # CPU doesn't support mixed precision
    # CPU optimization for Ryzen 7 7700X (8-core/16-thread)
    "dataloader_workers": 14,  # Use most threads for data loading
    "pin_memory": False,  # Not needed for CPU training
    "persistent_workers": True,  # Keep workers alive between epochs
    # Memory management for 64GB DDR5
    "prefetch_factor": 8,  # More aggressive prefetching with abundant RAM
    "dataset_cache": True,  # Cache entire dataset in RAM (you have 64GB)
}
