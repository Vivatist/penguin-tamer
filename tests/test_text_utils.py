"""Tests for text_utils module."""

import pytest
from penguin_tamer.text_utils import extract_labeled_code_blocks, format_api_key_display


class TestExtractLabeledCodeBlocks:
    """Tests for extract_labeled_code_blocks function."""

    def test_single_code_block_with_code_label(self):
        """Test extraction of single code block with [Code #1] label."""
        text = """
Some text before
[Code #1]
```bash
echo "Hello, World!"
```
Some text after
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 1
        assert result[0] == 'echo "Hello, World!"'

    def test_multiple_code_blocks(self):
        """Test extraction of multiple code blocks with different labels."""
        text = """
[Code #1]
```python
print("First")
```

Some explanation

[Code #2]
```python
print("Second")
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 2
        assert result[0] == 'print("First")'
        assert result[1] == 'print("Second")'

    def test_code_block_with_custom_label(self):
        """Test extraction with custom labels like [Example], [Test], etc."""
        text = """
[Example]
```javascript
console.log("test");
```

[Test]
```python
assert True
```

[Пример]
```bash
ls -la
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 3
        assert result[0] == 'console.log("test");'
        assert result[1] == 'assert True'
        assert result[2] == 'ls -la'

    def test_code_block_with_language_specifier(self):
        """Test extraction with different language specifiers."""
        text = """
[Code #1]
```python
def hello():
    return "world"
```

[Code #2]
```bash
#!/bin/bash
echo "test"
```

[Code #3]
```javascript
const x = 42;
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 3
        assert 'def hello():' in result[0]
        assert '#!/bin/bash' in result[1]
        assert 'const x = 42;' in result[2]

    def test_multiline_code_block(self):
        """Test extraction of multiline code blocks."""
        text = """
[Code #1]
```python
def calculate(x, y):
    result = x + y
    return result

value = calculate(10, 20)
print(value)
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 1
        assert 'def calculate(x, y):' in result[0]
        assert 'result = x + y' in result[0]
        assert 'print(value)' in result[0]

    def test_no_labeled_blocks(self):
        """Test with no labeled code blocks (only unlabeled)."""
        text = """
```python
print("No label")
```

Some text

```bash
echo "Also no label"
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 0

    def test_empty_text(self):
        """Test with empty text."""
        result = extract_labeled_code_blocks("")
        assert result == []

    def test_label_with_spaces(self):
        """Test labels with various spacing."""
        text = """
[Code #1]
```python
print("no space after label")
```

[Code #2]
```python
print("spaces after label")
```

[Code #3]


```python
print("newlines after label")
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 3
        assert 'no space after label' in result[0]
        assert 'spaces after label' in result[1]
        assert 'newlines after label' in result[2]

    def test_code_block_with_special_characters(self):
        """Test code blocks containing special characters."""
        text = """
[Code #1]
```bash
echo "Test with 'quotes' and \\"escapes\\""
grep -E "pattern.*" file.txt
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 1
        assert 'quotes' in result[0]
        assert 'grep -E' in result[0]

    def test_code_block_without_language_specifier(self):
        """Test code blocks without language specifier (plain ```)."""
        text = """
[Code #1]
```
plain code block
no language specified
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 1
        assert 'plain code block' in result[0]
        assert 'no language specified' in result[0]

    def test_nested_code_markers(self):
        """Test code blocks that contain ``` in their content."""
        text = """
[Code #1]
```markdown
Here's how to write code:
```python
print("hello")
```
End of markdown
```
"""
        # This is a tricky case - regex should match first closing ```
        result = extract_labeled_code_blocks(text)
        # Should extract the outer block content
        assert len(result) == 1

    def test_cyrillic_labels(self):
        """Test with Cyrillic (Russian) labels."""
        text = """
[Код #1]
```python
print("Привет")
```

[Пример #2]
```bash
ls -la
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 2
        assert 'Привет' in result[0]
        assert 'ls -la' in result[1]

    def test_label_with_numbers_and_symbols(self):
        """Test labels with various numbers and symbols."""
        text = """
[#1]
```python
test1()
```

[Code 2]
```python
test2()
```

[Step #3.1]
```python
test3()
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 3

    def test_strip_whitespace(self):
        """Test that extracted code is stripped of leading/trailing whitespace."""
        text = """
[Code #1]
```python

    print("test")

```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 1
        # Should be stripped
        assert result[0] == 'print("test")'

    def test_empty_code_block(self):
        """Test extraction of empty code blocks."""
        text = """
[Code #1]
```python
```
"""
        result = extract_labeled_code_blocks(text)
        assert len(result) == 1
        assert result[0] == ''


class TestFormatApiKeyDisplay:
    """Tests for format_api_key_display function."""

    def test_empty_key(self):
        """Test with empty API key."""
        result = format_api_key_display("")
        assert result == "(not set)"

    def test_none_key(self):
        """Test with None API key."""
        result = format_api_key_display(None)
        assert result == "(not set)"

    def test_short_key(self):
        """Test with short key (10 chars or less)."""
        result = format_api_key_display("short")
        assert result == "short"

        result = format_api_key_display("1234567890")
        assert result == "1234567890"

    def test_long_key(self):
        """Test with long key (more than 10 chars)."""
        key = "sk-1234567890abcdefghijklmnop"
        result = format_api_key_display(key)
        assert result.startswith("sk-12")
        assert result.endswith("mnop")
        assert "..." in result
        assert len(result) == 13  # 5 + 3 + 5

    def test_very_long_key(self):
        """Test with very long key."""
        key = "sk-proj-" + "x" * 100 + "abcde"
        result = format_api_key_display(key)
        assert result.startswith("sk-pr")
        assert result.endswith("abcde")
        assert "..." in result

    def test_exactly_11_chars(self):
        """Test with exactly 11 characters."""
        key = "12345678901"
        result = format_api_key_display(key)
        assert result == "12345...78901"

    def test_special_characters_in_key(self):
        """Test with special characters in key."""
        key = "sk-abc_def-ghi_jkl_mno_pqr"
        result = format_api_key_display(key)
        assert result.startswith("sk-ab")
        assert "_pqr" in result
        assert "..." in result


@pytest.mark.parametrize("text,expected_count", [
    # Test various scenarios with parameters
    ("No code blocks here", 0),
    ("[Code #1]\n```bash\necho test\n```", 1),
    ("[A]\n```\n1\n```\n[B]\n```\n2\n```", 2),
    ("```\nUnlabeled\n```", 0),
])
def test_extract_labeled_code_blocks_parametrized(text, expected_count):
    """Parametrized test for various scenarios."""
    result = extract_labeled_code_blocks(text)
    assert len(result) == expected_count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
