
import json
import re

from langchain_ollama import ChatOllama
from prompts import TEST_CASE_PROMPT


def get_llm():
    return ChatOllama(
        model="llama3.2",
        temperature=0.2
    )


def extract_json(response_text):

    response_text = response_text.strip()

    response_text = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        response_text,
        flags=re.IGNORECASE
    )

    start = response_text.find("{")
    end = response_text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("AI did not return valid JSON.")

    return json.loads(response_text[start:end + 1])


def validate_test_cases(data):

    if not isinstance(data, dict):
        raise ValueError("Invalid AI response format.")

    cases = data.get("test_cases", [])

    if not isinstance(cases, list) or not cases:
        raise ValueError("No test cases were generated.")

    if len(cases) > 20:
        raise ValueError("Too many test cases generated.")

    valid_scenarios = ["Positive", "Negative", "Edge"]
    valid_priorities = ["High", "Medium", "Low"]

    validated = []

    for index, case in enumerate(cases, start=1):

        if not isinstance(case, dict):
            raise ValueError(f"Invalid test case {index}.")

        title = str(case.get("title", "")).strip()

        if not title:
            raise ValueError(f"Missing title in test case {index}.")

        scenario = str(
            case.get("scenario", "Positive")
        ).strip().capitalize()

        if scenario not in valid_scenarios:
            scenario = "Positive"

        priority = str(
            case.get("priority", "Medium")
        ).strip().capitalize()

        if priority not in valid_priorities:
            priority = "Medium"

        steps = case.get("steps", [])

        if isinstance(steps, str):
            steps = [steps]

        if not isinstance(steps, list):
            steps = []

        steps = [
            str(step).strip()
            for step in steps
            if str(step).strip()
        ]

        if not steps:
            steps = ["Perform the required test action."]

        expected_result = str(
            case.get("expected_result", "")
        ).strip()

        if not expected_result:
            raise ValueError(
                f"Missing expected result in test case {index}."
            )

        validated.append({
            "test_case_id": f"TC-{index:02d}",
            "title": title,
            "scenario": scenario,
            "preconditions": str(
                case.get("preconditions", "Not specified")
            ).strip(),
            "steps": steps,
            "test_data": str(
                case.get("test_data", "Not specified")
            ).strip(),
            "expected_result": expected_result,
            "priority": priority
        })

    return validated


def generate_test_cases(requirement):

    if not requirement or not requirement.strip():
        raise ValueError("Please enter a software requirement.")

    try:

        llm = get_llm()

        prompt = TEST_CASE_PROMPT.format(
            requirement=requirement.strip()
        )

        response = llm.invoke(prompt)

        result = extract_json(str(response.content))

        test_cases = validate_test_cases(result)

        return {
            "feature": str(
                result.get("feature", "Unknown feature")
            ),
            "assumptions": result.get("assumptions", []),
            "test_cases": test_cases
        }

    except json.JSONDecodeError:
        raise ValueError(
            "AI returned invalid JSON. Please try again."
        )

    except Exception as error:

        if isinstance(error, ValueError):
            raise

        raise RuntimeError(
            "Ollama error. Check whether the model is running. "
            f"Details: {error}"
        )
