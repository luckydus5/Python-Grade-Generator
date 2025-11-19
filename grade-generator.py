#!/usr/bin/env python3

import csv
import sys

def input_nonempty(prompt):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Input cannot be empty. Try again.")

def input_category(prompt):
    while True:
        val = input(prompt).strip().upper()
        if val in ("FA", "SA"):
            return val
        print("Category must be 'FA' or 'SA' (case-insensitive).")

def input_float(prompt, min_value=None, must_positive=False):
    while True:
        val = input(prompt).strip()
        try:
            num = float(val)
        except ValueError:
            print("Please enter a valid number.")
            continue
        if must_positive and num <= 0:
            print("Value must be a positive number.")
            continue
        if (min_value is not None) and (num < min_value):
            print(f"Value must be at least {min_value}.")
            continue
        return num

def collect_assignments():
    assignments = []
    while True:
        print("\nEnter assignment details:")
        name = input_nonempty("  Assignment name: ")
        category = input_category("  Category (FA/SA): ")
        grade = input_float("  Grade obtained (0-100): ", min_value=0)
        # ensure grade <=100
        while grade > 100:
            print("Grade must be between 0 and 100.")
            grade = input_float("  Grade obtained (0-100): ", min_value=0)
        weight = input_float("  Weight (positive number, e.g., 30): ", must_positive=True)

        assignments.append({
            "Assignment": name,
            "Category": category,
            "Grade": grade,
            "Weight": weight
        })

        another = input("Add another assignment? (y/n): ").strip().lower()
        if another not in ("y", "yes"):
            break
    return assignments

def compute_results(assignments):
    # For each assignment compute weighted = (grade / 100) * weight
    for a in assignments:
        a["Weighted"] = (a["Grade"] / 100.0) * a["Weight"]

    # Totals
    total_fa_weighted = sum(a["Weighted"] for a in assignments if a["Category"] == "FA")
    total_sa_weighted = sum(a["Weighted"] for a in assignments if a["Category"] == "SA")
    total_grade = total_fa_weighted + total_sa_weighted

    # Also need the sum of weights per category (to check pass/fail)
    sum_fa_weights = sum(a["Weight"] for a in assignments if a["Category"] == "FA")
    sum_sa_weights = sum(a["Weight"] for a in assignments if a["Category"] == "SA")

    # GPA
    gpa = (total_grade / 100.0) * 5.0

    # Pass/Fail: must be >= 50% of category weight in both categories that exist.
    def category_pass(obtained, sum_weights):
        if sum_weights == 0:
            # If no assignments in the category, treat as pass (or decide policy).
            # We'll treat missing category as pass but note it. We could also treat
            # missing as fail if teacher requires both categories; adjust as needed.
            return True
        return obtained >= (0.5 * sum_weights)

    fa_pass = category_pass(total_fa_weighted, sum_fa_weights)
    sa_pass = category_pass(total_sa_weighted, sum_sa_weights)
    overall_pass = fa_pass and sa_pass

    return {
        "assignments": assignments,
        "total_fa_weighted": total_fa_weighted,
        "total_sa_weighted": total_sa_weighted,
        "sum_fa_weights": sum_fa_weights,
        "sum_sa_weights": sum_sa_weights,
        "total_grade": total_grade,
        "gpa": gpa,
        "fa_pass": fa_pass,
        "sa_pass": sa_pass,
        "overall_pass": overall_pass
    }

def print_summary(results):
    assignments = results["assignments"]
    print("\n" + "="*60)
    print("GRADE SUMMARY")
    print("="*60)
    # Print table header
    print(f"{'Assignment':30} {'Cat':3} {'Grade':6} {'Weight':6} {'Weighted':8}")
    print("-"*60)
    for a in assignments:
        name = (a["Assignment"][:27] + '...') if len(a["Assignment"]) > 30 else a["Assignment"]
        print(f"{name:30} {a['Category']:3} {a['Grade']:6.2f} {a['Weight']:6.2f} {a['Weighted']:8.2f}")

    print("-"*60)
    print(f"{'Total Formative (FA)':30} {'':3} {'':6} {results['sum_fa_weights']:6.2f} {results['total_fa_weighted']:8.2f}")
    print(f"{'Total Summative (SA)':30} {'':3} {'':6} {results['sum_sa_weights']:6.2f} {results['total_sa_weighted']:8.2f}")
    print("-"*60)
    print(f"{'Final Grade (out of 100)':30} {'':3} {'':6} {'':6} {results['total_grade']:8.2f}")
    print(f"{'GPA (scaled to 5.0)':30} {'':3} {'':6} {'':6} {results['gpa']:8.2f}")
    print("-"*60)
    # Pass/Fail details
    def pf_text(cat, obtained, sum_weights, passed):
        if sum_weights == 0:
            return f"{cat}: no items entered (treated as pass)"
        required = 0.5 * sum_weights
        return f"{cat}: {obtained:.2f} / {sum_weights:.2f}  (required >= {required:.2f}) -> {'PASS' if passed else 'FAIL'}"

    print(pf_text("Formative (FA)", results["total_fa_weighted"], results["sum_fa_weights"], results["fa_pass"]))
    print(pf_text("Summative (SA)", results["total_sa_weighted"], results["sum_sa_weights"], results["sa_pass"]))
    print(f"\nOVERALL RESULT: {'PASS' if results['overall_pass'] else 'FAIL'}")
    print("="*60 + "\n")

def write_csv(assignments, filename="grades.csv"):
    header = ["Assignment","Category","Grade","Weight"]
    try:
        with open(filename, mode="w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for a in assignments:
                writer.writerow([a["Assignment"], a["Category"], f"{a['Grade']:.2f}", f"{a['Weight']:.2f}"])
    except Exception as e:
        print(f"Error writing CSV file: {e}")
        return False
    return True

def main():
    print("Grade Generator - enter assignment details. Press Enter when prompted.")
    assignments = collect_assignments()
    if not assignments:
        print("No assignments entered. Exiting.")
        sys.exit(0)

    results = compute_results(assignments)
    print_summary(results)

    success = write_csv(assignments, filename="grades.csv")
    if success:
        print("Saved assignments to grades.csv")
    else:
        print("Failed to save grades.csv")

if __name__ == "__main__":
    main()
