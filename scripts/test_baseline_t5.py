import torch

from src.models.baseline_t5 import BaselineT5


def test_baseline_t5():
    """Test the baseline T5 model"""
    model_name = "t5-base"
    model = BaselineT5(model_name)

    checkpoint = torch.load(
        "checkpoints/baseline_t5_epoch_3.pt", map_location="cpu", weights_only=False
    )
    model.model.load_state_dict(checkpoint["model_state_dict"])
    model.model.to(model.device)

    # Test with sample input
    test_context = {
        "course_title": "Introduction to Python Programming",
        "domain": "Computer Science",
        "level": "undergraduate",
        "course_description": "A beginner course covering Python fundamentals and programming concepts.",
    }

    # Generate syllabus
    generated_syllabus = model.generate_syllabus(test_context)

    print("Generated Syllabus:")
    print("=" * 50)
    print(generated_syllabus)


if __name__ == "__main__":
    test_baseline_t5()
