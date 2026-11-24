
from test_case_generator import generate_test_cases


def identify_task(requirement):

    if not requirement or not requirement.strip():
        return "unclear"

    return "generate_test_cases"


def run_agent(requirement):

    action = identify_task(requirement)

    if action == "unclear":
        raise ValueError("Please enter a clear requirement.")

    result = generate_test_cases(requirement)

    return {
        "action": action,
        "feature": result["feature"],
        "assumptions": result["assumptions"],
        "test_cases": result["test_cases"]
    }
