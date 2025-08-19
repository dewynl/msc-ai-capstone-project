import torch
import torch.optim as optim
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset
from transformers import T5Tokenizer

from src.data.syllabus_dataset import SyllabusDataset
from src.models.baseline_t5 import BaselineT5


class T5Trainer:
    """Basic trainer for T5 model"""

    def __init__(self, model_name: str = "t5-base"):
        self.device = torch.device("cpu")
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)

        # Initialize model
        self.baseline_model = BaselineT5(model_name)
        self.model = self.baseline_model.model

        # Optimizer
        self.optimizer = optim.AdamW(self.model.parameters(), lr=3e-4)

    def train(self, data_path: str, epochs: int = 3) -> None:
        """Train the baseline T5 model with automatic data splitting"""

        # Create full dataset
        full_dataset = SyllabusDataset(data_path, self.tokenizer)

        # Split dataset (70% train, 30% validation)
        train_size = int(0.7 * len(full_dataset))

        indices = list(range(len(full_dataset)))
        train_indices, val_indices = train_test_split(
            indices, train_size=train_size, random_state=42
        )

        train_dataset = Subset(full_dataset, train_indices)
        val_dataset = Subset(full_dataset, val_indices)

        # Create dataloaders
        train_loader = DataLoader(
            train_dataset, batch_size=4, shuffle=True, num_workers=0
        )
        val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False, num_workers=0)

        print(f"Total dataset: {len(full_dataset)} syllabi")
        print(f"Training on {len(train_dataset)} samples")
        print(f"Validation on {len(val_dataset)} samples")

        # Training loop
        for epoch in range(epochs):
            self.model.train()
            total_train_loss = 0

            for batch_idx, batch in enumerate(train_loader):
                # Move data to device
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)

                # Zero gradients
                self.optimizer.zero_grad()

                # Forward pass
                outputs = self.model(
                    input_ids=input_ids, attention_mask=attention_mask, labels=labels
                )

                loss = outputs.loss
                total_train_loss += loss.item()

                # Backward pass
                loss.backward()
                self.optimizer.step()

                if batch_idx % 10 == 0:
                    print(
                        f"Epoch {epoch+1}/{epochs}, Batch {batch_idx}/{len(train_loader)}, Loss: {loss.item():.4f}"
                    )

            # Validation phase
            avg_train_loss = total_train_loss / len(train_loader)
            val_loss = self.validate(val_loader)
            print(
                f"Epoch {epoch+1}/{epochs}: Train Loss: {avg_train_loss:.4f}, Val Loss: {val_loss:.4f}"
            )

            # Save checkpoint
            self.save_checkpoint(f"baseline_t5_epoch_{epoch+1}.pt")

    def validate(self, val_loader: DataLoader) -> float:
        """Validate the model"""
        self.model.eval()
        total_val_loss = 0

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)

                outputs = self.model(
                    input_ids=input_ids, attention_mask=attention_mask, labels=labels
                )

                total_val_loss += outputs.loss.item()

        avg_val_loss = total_val_loss / len(val_loader)
        return avg_val_loss

    def save_checkpoint(self, filename: str) -> None:
        """Save model checkpoint"""

        import os

        os.makedirs("checkpoints", exist_ok=True)

        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "tokenizer": self.tokenizer,
            },
            f"checkpoints/{filename}",
        )

        print(f"Checkpoint saved: checkpoints/{filename}")


if __name__ == "__main__":
    print("Starting T5 Syllabus Generation Training")
    print("=" * 50)

    trainer = T5Trainer()
    trainer.train(
        data_path="data/assembled_syllabi/syllabi_dataset.json",
        epochs=3,
    )
