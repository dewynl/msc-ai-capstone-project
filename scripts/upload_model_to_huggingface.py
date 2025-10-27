#!/usr/bin/env python3
"""
Upload Fine-Tuned T5 Model to Hugging Face Hub

This script uploads the locally trained T5 model to Hugging Face Hub
for deployment on Streamlit Cloud.

Prerequisites:
1. Hugging Face account (free): https://huggingface.co/join
2. Hugging Face token with write access
3. Install: pip install huggingface_hub

Usage:
    export HF_TOKEN="your_token_here"
    python scripts/upload_model_to_huggingface.py
"""

import os
from pathlib import Path

from huggingface_hub import HfApi, create_repo


def upload_model_to_hub():
    """Upload fine-tuned T5 model to Hugging Face Hub."""

    print("🚀 Uploading Fine-Tuned T5 Model to Hugging Face Hub")
    print("=" * 70)

    # Check if model exists locally
    model_path = Path("models/t5-function-call-finetuned")
    if not model_path.exists():
        print(
            "❌ ERROR: Fine-tuned model not found at models/t5-function-call-finetuned"
        )
        print("   Please train the model first:")
        print("   python scripts/t5_function_call_trainer.py")
        return

    # Get Hugging Face token from environment
    token = os.getenv("HF_TOKEN")
    if not token:
        print("❌ ERROR: HF_TOKEN environment variable not set")
        print("\n📋 To get your token:")
        print("   1. Go to: https://huggingface.co/settings/tokens")
        print("   2. Create a new token with WRITE permission")
        print("   3. Run: export HF_TOKEN='your_token_here'")
        print("   4. Run this script again")
        return

    # Get username from user
    username = input("\n📝 Enter your Hugging Face username: ").strip()
    if not username:
        print("❌ Username cannot be empty")
        return

    # Model repository name
    repo_name = "educraft-t5-function-call"
    repo_id = f"{username}/{repo_name}"

    print(f"\n📦 Model will be uploaded to: https://huggingface.co/{repo_id}")
    print(f"   Local path: {model_path}")

    # Confirm upload
    confirm = input("\n⚠️  Proceed with upload? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Upload cancelled")
        return

    try:
        # Initialize Hugging Face API
        api = HfApi(token=token)

        # Create repository (if doesn't exist)
        print(f"\n🔧 Creating repository: {repo_id}")
        create_repo(
            repo_id=repo_id,
            token=token,
            private=False,  # Public repository
            exist_ok=True,  # Don't error if already exists
        )
        print("✅ Repository created/verified")

        # Upload all model files
        print(f"\n📤 Uploading model files from {model_path}...")
        api.upload_folder(
            folder_path=str(model_path),
            repo_id=repo_id,
            repo_type="model",
            token=token,
        )

        print("\n" + "=" * 70)
        print("✅ MODEL UPLOAD SUCCESSFUL!")
        print("=" * 70)
        print("\n🎉 Your model is now available at:")
        print(f"   https://huggingface.co/{repo_id}")
        print("\n📝 To use in your code:")
        print(f'   model = T5ForConditionalGeneration.from_pretrained("{repo_id}")')
        print(f'   tokenizer = T5Tokenizer.from_pretrained("{repo_id}")')
        print("\n🔑 Add to Streamlit Cloud secrets:")
        print(f'   HF_MODEL_ID = "{repo_id}"')
        print("=" * 70)

        return repo_id

    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Check your HF_TOKEN is valid and has WRITE permission")
        print("   - Verify your username is correct")
        print("   - Ensure you have internet connection")
        return None


if __name__ == "__main__":
    upload_model_to_hub()
