from dataclasses import dataclass


@dataclass
class EducationalT5Config:
    """Configuration for Educational T5 model"""

    # Base T5 configuration
    model_name: str = "t5-base"
    d_model: int = 512
    num_layers: int = 12
    num_heads: int = 8

    # Educational enhancements
    num_domains: int = 50  # STEM, Business, Arts, etc.
    num_levels: int = 5  # K-12, undergraduate, graduate, professional, executive
    num_templates: int = 4  # university, corporate, certification, professional_dev

    # Bloom's taxonomy configuration
    bloom_levels: int = 6
    bloom_integration_layers: list[
        int
    ] | None = None  # Which layers get Bloom's attention

    # Pedagogical structure
    max_weeks: int = 16
    max_sections_per_week: int = 8
    hierarchical_encoding: bool = True

    def __post_init__(self) -> None:
        if self.bloom_integration_layers is None:
            # Integrate Bloom's attention every 3rd layer
            self.bloom_integration_layers = list(range(0, self.num_layers, 3))
