
import streamlit as st
import pandas as pd

from agent import run_agent
from database import (
    create_database,
    save_test_run,
    get_all_runs,
    get_test_cases_by_run,
    update_test_case,
    delete_test_case
)
from export_utils import export_to_csv


# ---------------- DATABASE SETUP ----------------

create_database()


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AI Test Case Generator Agent",
    page_icon="🧪",
    layout="wide"
)


# ---------------- SESSION STATE ----------------

if "test_cases" not in st.session_state:
    st.session_state.test_cases = []

if "requirement" not in st.session_state:
    st.session_state.requirement = ""

if "feature" not in st.session_state:
    st.session_state.feature = ""

if "assumptions" not in st.session_state:
    st.session_state.assumptions = []

if "saved_run_id" not in st.session_state:
    st.session_state.saved_run_id = None


# ---------------- SIDEBAR ----------------

st.sidebar.title("🧪 Test Case Generator")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Saved History"]
)


# ---------------- HELPER FUNCTION ----------------

def display_test_cases(cases):

    if not cases:
        st.info("No test cases available.")
        return

    table_data = []

    for case in cases:
        table_data.append({
            "ID": case["test_case_id"],
            "Title": case["title"],
            "Scenario": case["scenario"],
            "Test Steps": " → ".join(case["steps"]),
            "Test Data": case["test_data"],
            "Expected Result": case["expected_result"],
            "Priority": case["priority"]
        })

    st.dataframe(
        pd.DataFrame(table_data),
        use_container_width=True,
        hide_index=True
    )


def load_run(run_id):

    runs = get_all_runs()

    selected_run = next(
        (run for run in runs if run["id"] == run_id),
        None
    )

    if selected_run is None:
        st.error("Selected history was not found.")
        return

    st.session_state.requirement = selected_run["requirement"]
    st.session_state.feature = selected_run["feature"] or "Unknown feature"

    import json

    try:
        st.session_state.assumptions = json.loads(
            selected_run["assumptions"] or "[]"
        )
    except (ValueError, TypeError):
        st.session_state.assumptions = []

    st.session_state.test_cases = get_test_cases_by_run(run_id)
    st.session_state.saved_run_id = run_id


# ---------------- HOME PAGE ----------------

if page == "Home":

    st.title("🧪 AI Test Case Generator Agent")

    st.write(
        "Generate positive, negative and edge test cases "
        "from simple software requirements using local AI."
    )

    st.divider()

    st.subheader("Enter Software Requirement")

    requirement = st.text_area(
        "Describe your software feature:",
        value=st.session_state.requirement,
        height=150,
        placeholder=(
            "Example: A user should be able to register "
            "using name, email and password."
        )
    )

    if st.button(
        "🚀 Generate Test Cases",
        type="primary",
        use_container_width=True
    ):

        if not requirement.strip():

            st.warning("Please enter a software requirement.")

        else:

            with st.spinner(
                "AI agent is analyzing the requirement..."
            ):

                try:

                    result = run_agent(requirement)

                    st.session_state.requirement = requirement
                    st.session_state.feature = result["feature"]
                    st.session_state.assumptions = result["assumptions"]
                    st.session_state.test_cases = result["test_cases"]
                    st.session_state.saved_run_id = None

                    st.success(
                        "Test cases generated successfully!"
                    )

                except Exception as error:

                    st.error(
                        f"Unable to generate test cases: {error}"
                    )

    # ---------------- GENERATED RESULTS ----------------

    if st.session_state.test_cases:

        st.divider()

        st.subheader("Requirement Analysis")

        st.write(
            f"**Identified Feature:** {st.session_state.feature}"
        )

        if st.session_state.assumptions:

            st.write("**Assumptions:**")

            for assumption in st.session_state.assumptions:
                st.write(f"- {assumption}")

        st.subheader("Generated Test Cases")

        display_test_cases(st.session_state.test_cases)

        st.divider()

        st.subheader("Edit Test Case")

        cases = st.session_state.test_cases

        selected_index = st.selectbox(
            "Select a test case to edit:",
            options=list(range(len(cases))),
            format_func=lambda i: (
                f"{cases[i]['test_case_id']} - {cases[i]['title']}"
            ),
            key="edit_case_selector"
        )

        selected_case = cases[selected_index]

        with st.form("edit_test_case_form"):

            title = st.text_input(
                "Test Case Title",
                value=selected_case["title"]
            )

            scenario = st.selectbox(
                "Scenario",
                ["Positive", "Negative", "Edge"],
                index=["Positive", "Negative", "Edge"].index(
                    selected_case["scenario"]
                )
            )

            preconditions = st.text_area(
                "Preconditions",
                value=selected_case["preconditions"]
            )

            steps = st.text_area(
                "Test Steps (one step per line)",
                value="\n".join(selected_case["steps"])
            )

            test_data = st.text_area(
                "Test Data",
                value=selected_case["test_data"]
            )

            expected_result = st.text_area(
                "Expected Result",
                value=selected_case["expected_result"]
            )

            priority = st.selectbox(
                "Priority",
                ["High", "Medium", "Low"],
                index=["High", "Medium", "Low"].index(
                    selected_case["priority"]
                )
            )

            update_button = st.form_submit_button(
                "💾 Update Test Case"
            )

            if update_button:

                if not title.strip() or not expected_result.strip():
                    st.error("Title and expected result are required.")

                elif not steps.strip():
                    st.error("Please enter at least one test step.")

                else:

                    updated_case = {
                        **selected_case,
                        "title": title.strip(),
                        "scenario": scenario,
                        "preconditions": preconditions.strip(),
                        "steps": [
                            step.strip()
                            for step in steps.splitlines()
                            if step.strip()
                        ],
                        "test_data": test_data.strip(),
                        "expected_result": expected_result.strip(),
                        "priority": priority
                    }

                    if updated_case.get("id") is not None:
                        update_test_case(
                            updated_case["id"],
                            updated_case
                        )

                    st.session_state.test_cases[
                        selected_index
                    ] = updated_case

                    st.success("Test case updated successfully!")
                    st.rerun()

        # ---------------- DELETE TEST CASE ----------------

        st.subheader("Delete Test Case")

        if st.button(
            "🗑️ Delete Selected Test Case",
            use_container_width=True
        ):

            case_to_delete = cases[selected_index]

            if case_to_delete.get("id") is not None:

                delete_test_case(case_to_delete["id"])

            st.session_state.test_cases.pop(selected_index)

            st.success("Test case deleted successfully!")
            st.rerun()

        st.divider()

        # ---------------- SAVE TO DATABASE ----------------

        st.subheader("Save and Export")

        if st.button(
            "💾 Save Test Cases to History",
            use_container_width=True
        ):

            if not st.session_state.test_cases:
                st.warning("No test cases to save.")

            elif st.session_state.saved_run_id is not None:

                st.info("These test cases are already saved.")

            else:

                run_id = save_test_run(
                    st.session_state.requirement,
                    st.session_state.feature,
                    st.session_state.assumptions,
                    st.session_state.test_cases
                )

                st.session_state.saved_run_id = run_id

                st.session_state.test_cases = (
                    get_test_cases_by_run(run_id)
                )

                st.success("Test cases saved successfully!")

                st.rerun()

        csv_data = export_to_csv(
            st.session_state.test_cases
        )

        st.download_button(
            label="⬇️ Download Test Cases as CSV",
            data=csv_data,
            file_name="generated_test_cases.csv",
            mime="text/csv",
            use_container_width=True
        )


# ---------------- SAVED HISTORY PAGE ----------------

elif page == "Saved History":

    st.title("📚 Saved Test Case History")

    runs = get_all_runs()

    if not runs:

        st.info("No saved test case history available.")

    else:

        st.write(
            "Select a previously saved requirement "
            "to view its test cases."
        )

        selected_run_id = st.selectbox(
            "Saved Requirements",
            options=[run["id"] for run in runs],
            format_func=lambda run_id: next(
                (
                    f"Run {run['id']} - {run['requirement'][:65]}"
                    for run in runs
                    if run["id"] == run_id
                ),
                f"Run {run_id}"
            )
        )

        if st.button(
            "📂 Load Selected History",
            use_container_width=True
        ):

            load_run(selected_run_id)
            st.success("Previous test cases loaded successfully!")
            st.rerun()

        selected_run = next(
            run for run in runs
            if run["id"] == selected_run_id
        )

        st.divider()

        st.write(
            f"**Requirement:** {selected_run['requirement']}"
        )

        history_cases = get_test_cases_by_run(selected_run_id)

        display_test_cases(history_cases)

        st.download_button(
            "⬇️ Download History as CSV",
            data=export_to_csv(history_cases),
            file_name=f"test_cases_run_{selected_run_id}.csv",
            mime="text/csv"
        )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "AI Test Case Generator Agent | "
    "Powered by Ollama, LangChain, Python, SQLite and Pandas"
)
