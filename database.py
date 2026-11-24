
import sqlite3
import json

DB_NAME = "test_cases.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requirement TEXT NOT NULL,
            feature TEXT,
            assumptions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            test_case_id TEXT,
            title TEXT,
            scenario TEXT,
            preconditions TEXT,
            steps TEXT,
            test_data TEXT,
            expected_result TEXT,
            priority TEXT,
            FOREIGN KEY(run_id) REFERENCES test_runs(id)
        )
    """)

    conn.commit()
    conn.close()


def save_test_run(requirement, feature, assumptions, test_cases):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO test_runs
        (requirement, feature, assumptions)
        VALUES (?, ?, ?)
    """, (
        requirement,
        feature,
        json.dumps(assumptions)
    ))

    run_id = cursor.lastrowid

    for case in test_cases:

        cursor.execute("""
            INSERT INTO test_cases (
                run_id,
                test_case_id,
                title,
                scenario,
                preconditions,
                steps,
                test_data,
                expected_result,
                priority
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            case["test_case_id"],
            case["title"],
            case["scenario"],
            case["preconditions"],
            json.dumps(case["steps"]),
            case["test_data"],
            case["expected_result"],
            case["priority"]
        ))

    conn.commit()
    conn.close()

    return run_id


def get_all_runs():

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT * FROM test_runs
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_test_cases_by_run(run_id):

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT * FROM test_cases
        WHERE run_id = ?
        ORDER BY id
    """, (run_id,)).fetchall()

    conn.close()

    results = []

    for row in rows:
        case = dict(row)

        try:
            case["steps"] = json.loads(case["steps"])
        except (json.JSONDecodeError, TypeError):
            case["steps"] = []

        results.append(case)

    return results


def update_test_case(case_id, case):

    conn = get_connection()

    conn.execute("""
        UPDATE test_cases
        SET title = ?,
            scenario = ?,
            preconditions = ?,
            steps = ?,
            test_data = ?,
            expected_result = ?,
            priority = ?
        WHERE id = ?
    """, (
        case["title"],
        case["scenario"],
        case["preconditions"],
        json.dumps(case["steps"]),
        case["test_data"],
        case["expected_result"],
        case["priority"],
        case_id
    ))

    conn.commit()
    conn.close()


def delete_test_case(case_id):

    conn = get_connection()

    conn.execute("""
        DELETE FROM test_cases WHERE id = ?
    """, (case_id,))

    conn.commit()
    conn.close()
