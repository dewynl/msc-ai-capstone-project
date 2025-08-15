import json
from typing import Any, Dict

from torch.utils.data import Dataset
from transformers import PreTrainedTokenizerBase


class SyllabusDataset(Dataset[Dict[str, Any]]):
    """Dataset for loading syllabus data for T5 training"""

    def __init__(
        self,
        data_path: str,
        tokenizer: PreTrainedTokenizerBase,
        max_input_length: int = 512,
        max_target_length: int = 1024,
    ) -> None:
        self.tokenizer = tokenizer
        self.max_input_length = max_input_length
        self.max_target_length = max_target_length

        # Load data
        with open(data_path) as f:
            self.data = json.load(f)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = self.data[idx]
        context = item["context"]
        syllabus_content = item["syllabus_content"]

        # Create input prompt
        input_text = f"Generate syllabus: Title: {context['course_title']} "
        input_text += f"Domain: {context['domain']} Level: {context['level']} "
        input_text += f"Description: {context['course_description']}"

        # Tokenize input
        input_encoding = self.tokenizer(
            input_text,
            max_length=self.max_input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        target_encoding = self.tokenizer(
            syllabus_content,
            max_length=self.max_target_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return {
            "input_ids": input_encoding["input_ids"].flatten(),
            "attention_mask": input_encoding["attention_mask"].flatten(),
            "labels": target_encoding["input_ids"].flatten(),
        }
