#!/usr/bin/env python3
"""
Comprehensive Tests for Markdown Syllabus Parser

Tests edge cases, malformed input, and robustness.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from markdown_syllabus_parser import MarkdownSyllabusParser


def create_mock_context():
    """Create mock RAG context for testing."""
    return {
        "available_modules": [
            {"id": "mod-0", "title": "Module 0"},
            {"id": "mod-1", "title": "Module 1"},
            {"id": "mod-2", "title": "Module 2"},
        ],
        "available_activities": [
            {"id": "act-0", "title": "Activity 0"},
            {"id": "act-1", "title": "Activity 1"},
        ],
        "available_assessments": [
            {"id": "ass-0", "title": "Assessment 0"},
        ],
    }


def test_normal_case():
    """Test normal, well-formatted markdown."""
    markdown = """# Course: Test Course

**Domain:** computer_science
**Level:** beginner
**Duration:** semester

## Learning Objectives
- Objective 1
- Objective 2

## Selected Modules
[0], [1]

## Selected Activities
[0]

## Selected Assessments
[0]
"""

    parser = MarkdownSyllabusParser()
    result = parser.parse(markdown, create_mock_context())

    assert result.success, f"Expected success, got errors: {result.errors}"
    assert len(result.syllabus["modules"]) == 2
    assert result.syllabus["modules"] == ["mod-0", "mod-1"]
    assert len(result.syllabus["activities"]) == 1
    assert len(result.errors) == 0

    print("✅ Test 1: Normal case - PASSED")


def test_indices_different_formats():
    """Test various index formatting styles."""
    test_cases = [
        ("[0], [1], [2]", [0, 1, 2]),  # Comma-separated
        ("[0] [1] [2]", [0, 1, 2]),  # Space-separated
        ("[0]\n[1]\n[2]", [0, 1, 2]),  # Newline-separated
        ("[0],[1],[2]", [0, 1, 2]),  # No spaces
    ]

    parser = MarkdownSyllabusParser()

    for format_str, expected_indices in test_cases:
        markdown = f"""# Course: Test

**Domain:** test
**Level:** beginner
**Duration:** semester

## Learning Objectives
- Test objective

## Selected Modules
{format_str}
"""

        result = parser.parse(markdown, create_mock_context())
        assert result.success, f"Failed on format: {format_str}"
        assert len(result.syllabus["modules"]) == len(expected_indices)

    print("✅ Test 2: Different index formats - PASSED")


def test_invalid_indices():
    """Test that invalid indices are caught and warned."""
    markdown = """# Course: Test

**Domain:** test
**Level:** beginner
**Duration:** semester

## Learning Objectives
- Objective

## Selected Modules
[0], [999]

## Selected Activities
[100]
"""

    parser = MarkdownSyllabusParser()
    result = parser.parse(markdown, create_mock_context())

    # Should still succeed but with warnings
    assert result.success
    assert len(result.warnings) >= 2  # Invalid module 999 and activity 100
    assert result.syllabus["modules"] == ["mod-0"]  # Only valid index kept
    assert len(result.syllabus["activities"]) == 0  # Invalid skipped

    print("✅ Test 3: Invalid indices handled - PASSED")


def test_missing_sections():
    """Test markdown with missing sections."""
    markdown = """# Course: Minimal Course

**Domain:** test
**Level:** beginner

## Learning Objectives
- Only objective
"""

    parser = MarkdownSyllabusParser()
    result = parser.parse(markdown, create_mock_context())

    assert result.success
    assert len(result.warnings) >= 1  # Warning about no modules/activities
    assert len(result.syllabus["modules"]) == 0
    assert len(result.syllabus["activities"]) == 0

    print("✅ Test 4: Missing sections handled - PASSED")


def test_no_objectives():
    """Test markdown without objectives."""
    markdown = """# Course: No Objectives Course

**Domain:** test
**Level:** beginner
**Duration:** semester

## Selected Modules
[0]
"""

    parser = MarkdownSyllabusParser()
    result = parser.parse(markdown, create_mock_context())

    assert result.success
    assert "No learning objectives" in str(result.warnings)
    assert len(result.syllabus["learning_objectives"]) == 0
    assert len(result.syllabus["modules"]) == 1

    print("✅ Test 5: No objectives handled - PASSED")


def test_empty_sections():
    """Test sections that exist but are empty."""
    markdown = """# Course: Empty Sections

**Domain:** test
**Level:** beginner
**Duration:** semester

## Learning Objectives

## Selected Modules

## Selected Activities
"""

    parser = MarkdownSyllabusParser()
    result = parser.parse(markdown, create_mock_context())

    assert result.success
    assert len(result.syllabus["learning_objectives"]) == 0
    assert len(result.syllabus["modules"]) == 0

    print("✅ Test 6: Empty sections handled - PASSED")


def test_malformed_markdown():
    """Test resilience to markdown syntax errors."""
    markdown = """# Course: Malformed

**Domain: test
**Level:** beginner

## Learning Objectives
- Objective without proper formatting

## Selected Modules
[0] [1 [2]
"""  # Mismatched brackets

    parser = MarkdownSyllabusParser()
    result = parser.parse(markdown, create_mock_context())

    # Should still extract what it can
    assert result.success or len(result.errors) == 0
    # Should get indices 0 and 2 (1 is malformed)
    assert "mod-0" in result.syllabus["modules"]

    print("✅ Test 7: Malformed markdown resilient - PASSED")


def test_duplicate_indices():
    """Test that duplicate indices are handled."""
    markdown = """# Course: Duplicates

**Domain:** test
**Level:** beginner
**Duration:** semester

## Learning Objectives
- Objective

## Selected Modules
[0], [0], [1], [0]
"""

    parser = MarkdownSyllabusParser()
    result = parser.parse(markdown, create_mock_context())

    assert result.success
    # Should have duplicates (parser doesn't dedupe - that's intentional)
    assert len(result.syllabus["modules"]) == 4

    print("✅ Test 8: Duplicate indices preserved - PASSED")


def test_case_sensitivity():
    """Test that section headers are case-sensitive."""
    markdown = """# Course: Case Test

**Domain:** test
**Level:** beginner
**Duration:** semester

## Learning Objectives
- Objective

## SELECTED MODULES
[0]

## selected modules
[1]
"""

    parser = MarkdownSyllabusParser()
    result = parser.parse(markdown, create_mock_context())

    # Should NOT match uppercase "SELECTED MODULES"
    assert len(result.syllabus["modules"]) == 0

    print("✅ Test 9: Case sensitivity correct - PASSED")


def test_unicode_content():
    """Test unicode characters in objectives."""
    markdown = """# Course: Unicode Test

**Domain:** test
**Level:** beginner
**Duration:** semester

## Learning Objectives
- Understand λ-calculus and ∀ quantifiers
- Master café management 🎓

## Selected Modules
[0]
"""

    parser = MarkdownSyllabusParser()
    result = parser.parse(markdown, create_mock_context())

    assert result.success
    assert len(result.syllabus["learning_objectives"]) == 2
    assert "λ-calculus" in result.syllabus["learning_objectives"][0]

    print("✅ Test 10: Unicode handled - PASSED")


def run_all_tests():
    """Run all test cases."""
    print("=" * 80)
    print("MARKDOWN PARSER TESTS")
    print("=" * 80)
    print()

    tests = [
        test_normal_case,
        test_indices_different_formats,
        test_invalid_indices,
        test_missing_sections,
        test_no_objectives,
        test_empty_sections,
        test_malformed_markdown,
        test_duplicate_indices,
        test_case_sensitivity,
        test_unicode_content,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__} - FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} - ERROR: {e}")
            failed += 1

    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print()

    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
