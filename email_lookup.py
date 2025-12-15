import time
import os
import difflib

# -------------------------------
# CONFIGURATION
# -------------------------------
REPORT_FOLDER = "/path/to/reports/"
REPORT_1 = "report_1.txt"  # or .csv or .json
REPORT_2 = "report_2.txt"
DIFF_OUTPUT = "difference_output.txt"

CHECK_INTERVAL = 10  # seconds to re-check for files


def wait_for_reports():
    """Wait until both report files exist."""
    print("Waiting for both reports to be generated...")

    while True:
        r1_exists = os.path.exists(os.path.join(REPORT_FOLDER, REPORT_1))
        r2_exists = os.path.exists(os.path.join(REPORT_FOLDER, REPORT_2))

        if r1_exists and r2_exists:
            print("Both reports detected!")
            return

        time.sleep(CHECK_INTERVAL)


def compare_reports():
    """Compare the two reports and generate a diff output file."""
    file1_path = os.path.join(REPORT_FOLDER, REPORT_1)
    file2_path = os.path.join(REPORT_FOLDER, REPORT_2)

    with open(file1_path, "r") as f1:
        f1_lines = f1.readlines()

    with open(file2_path, "r") as f2:
        f2_lines = f2.readlines()

    diff = difflib.unified_diff(
        f1_lines,
        f2_lines,
        fromfile=REPORT_1,
        tofile=REPORT_2,
        lineterm=""
    )

    output_path = os.path.join(REPORT_FOLDER, DIFF_OUTPUT)

    with open(output_path, "w") as out:
        for line in diff:
            out.write(line + "\n")

    print(f"Diff file generated: {output_path}")
    return output_path


def main():
    wait_for_reports()
    compare_reports()


if __name__ == "__main__":
    main()
