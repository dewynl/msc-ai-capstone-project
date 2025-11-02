#!/usr/bin/env python3
"""
Check feedback collection progress.
Shows how many ratings collected and how many more needed for fine-tuning.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.supabase_client import get_supabase_manager


def main():
    """Display current feedback statistics."""
    print("=" * 80)
    print("FEEDBACK COLLECTION PROGRESS")
    print("=" * 80)

    try:
        db = get_supabase_manager()
        stats = db.get_feedback_stats()

        total = stats["total_feedback"]
        avg_score = stats["avg_score"]
        high_quality = stats["high_quality_count"]

        # Progress bar
        target = 50
        progress = min(total / target * 100, 100)
        filled = int(progress / 2)
        bar = "█" * filled + "░" * (50 - filled)

        print("\n📊 Current Statistics:")
        print(f"   Total ratings: {total}")
        print(f"   Average score: {avg_score:.2f}/10")
        print(f"   High quality (≥7/10): {high_quality}")

        print("\n📈 Progress to Fine-Tuning:")
        print(f"   [{bar}] {progress:.1f}%")
        print(f"   {total}/{target} ratings collected")

        if total < target:
            remaining = target - total
            print(f"\n⏳ Need {remaining} more ratings to reach fine-tuning threshold")
            print(
                f"   Estimated time remaining: {remaining * 2} minutes (~2 min per syllabus)"
            )
        else:
            print("\n✅ READY FOR FINE-TUNING!")
            print(f"   You have {total} ratings (≥{target} required)")
            print("\n🚀 Next step: Run fine-tuning script")
            print("   python scripts/feedback/fine_tune_from_feedback.py")

        print("\n📉 Score Distribution:")
        if total > 0:
            # Get all feedback
            all_feedback = (
                db.client.table("syllabus_feedback").select("quality_score").execute()
            )
            if all_feedback.data:
                scores = [f["quality_score"] for f in all_feedback.data]

                # Count by range
                low = len([s for s in scores if s <= 3])
                medium = len([s for s in scores if 4 <= s <= 6])
                high = len([s for s in scores if 7 <= s <= 8])
                excellent = len([s for s in scores if s >= 9])

                print(f"   Poor (1-3): {low} ratings")
                print(f"   Fair (4-6): {medium} ratings")
                print(f"   Good (7-8): {high} ratings")
                print(f"   Excellent (9-10): {excellent} ratings")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("   1. Supabase credentials are configured in .env")
        print("   2. The syllabus_feedback table exists")
        print("   3. You've submitted at least one rating")


if __name__ == "__main__":
    main()
