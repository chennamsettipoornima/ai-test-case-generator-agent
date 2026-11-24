
import pandas as pd


def export_to_csv(test_cases):

    if not test_cases:
        return b""

    export_data = []

    for case in test_cases:

        export_data.append({
            "Test Case ID": case.get("test_case_id", ""),
            "Title": case.get("title", ""),
            "Scenario": case.get("scenario", ""),
            "Preconditions": case.get("preconditions", ""),
            "Test Steps": "\n".join(case.get("steps", [])),
            "Test Data": case.get("test_data", ""),
            "Expected Result": case.get("expected_result", ""),
            "Priority": case.get("priority", "")
        })

    df = pd.DataFrame(export_data)

    return df.to_csv(index=False).encode("utf-8-sig")
