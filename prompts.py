
TEST_CASE_PROMPT = """
You are an expert software testing engineer.

Analyze the software requirement carefully.

Generate:
1. Positive test cases
2. Negative test cases
3. Edge test cases

Rules:
- Do not invent application rules.
- Mention assumptions clearly.
- Include test steps, test data and expected results.
- Assign only High, Medium or Low priority.
- Return valid JSON only.
- Do not use Markdown code fences.

Required JSON format:

{{
  "feature": "Feature name",
  "assumptions": [],
  "test_cases": [
    {{
      "title": "Test case title",
      "scenario": "Positive",
      "preconditions": "Required conditions",
      "steps": ["Step 1", "Step 2"],
      "test_data": "Input data",
      "expected_result": "Expected result",
      "priority": "High"
    }}
  ]
}}

Software Requirement:
{requirement}
"""
