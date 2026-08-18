import asyncio
import io
import os
import json
import sys
import httpx
import pandas as pd
import numpy as np

BASE_URL = "http://localhost:8005/api/v1"

async def run_csv_excel_audit():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🧪 NEURODESK AI — ISOLATED CSV & EXCEL ANALYTICS ACCEPTANCE AUDIT")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # PHASE 1: Load dataset & compute ground truth using Pandas
    # -------------------------------------------------------------------------
    csv_path = "scratch/employee_analytics_dataset_2026.csv"
    xlsx_path = "scratch/employee_analytics_dataset_2026.xlsx"

    df_ground = pd.read_csv(csv_path)

    # Independent Ground Truth Calculations
    total_rows = len(df_ground)
    avg_age = df_ground["Age"].mean()
    avg_sal = df_ground["Salary"].mean()
    median_sal = df_ground["Salary"].median()
    max_sal = df_ground["Salary"].max()
    min_sal = df_ground["Salary"].min()
    missing_vals = int(df_ground.isnull().sum().sum())
    dup_rows = int(df_ground.duplicated().sum())

    dept_counts = df_ground["Department"].value_counts().to_dict()
    city_counts = df_ground["City"].value_counts().to_dict()
    bangalore_count = city_counts.get("Bangalore", 0)

    top_dept = df_ground.groupby("Department")["Salary"].mean().idxmax()
    top_dept_sal = df_ground.groupby("Department")["Salary"].mean().max()
    eng_avg_sal = df_ground[df_ground["Department"] == "Engineering"]["Salary"].mean()

    top5_sals = sorted(df_ground["Salary"].dropna().unique(), reverse=True)[:5]
    bottom5_sals = sorted(df_ground["Salary"].dropna().unique())[:5]

    joined_after_2022 = len(df_ground[df_ground["JoiningYear"] > 2022])
    top_city = df_ground["City"].mode()[0]
    avg_exp = df_ground["Experience"].mean()
    sal_gt_80k = len(df_ground[df_ground["Salary"] > 80000])

    print("\n--- INDEPENDENT PANDAS GROUND TRUTH ---")
    print(f"Total Rows: {total_rows}")
    print(f"Average Age: {avg_age:.2f}")
    print(f"Average Salary: ${avg_sal:,.2f}")
    print(f"Median Salary: ${median_sal:,.2f}")
    print(f"Highest Salary: ${max_sal:,.2f}")
    print(f"Lowest Salary: ${min_sal:,.2f}")
    print(f"Missing Values: {missing_vals}")
    print(f"Duplicate Rows: {dup_rows}")
    print(f"Department Counts: {dept_counts}")
    print(f"City Counts: {city_counts}")
    print(f"Bangalore Count: {bangalore_count}")
    print(f"Top Dept by Salary: {top_dept} (${top_dept_sal:,.2f})")
    print(f"Engineering Avg Salary: ${eng_avg_sal:,.2f}")
    print(f"Joined After 2022: {joined_after_2022}")
    print(f"Top City: {top_city}")
    print(f"Average Experience: {avg_exp:.2f}")
    print(f"Salary > 80k Count: {sal_gt_80k}")
    print("---------------------------------------\n")

    results = {}
    details = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # Register and login test user
        email = "csv_excel_audit_isolated_2026@neurodesk.ai"
        pw = "AuditPass2026!"
        await client.post("/auth/register", json={"email": email, "full_name": "CSV Excel Auditor", "password": pw})
        login_res = await client.post("/auth/login", json={"email": email, "password": pw})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Upload Main CSV & XLSX Assets
        with open(csv_path, "rb") as f:
            up_csv = await client.post("/assets/upload", headers=headers, files={"file": ("employee_analytics_dataset_2026.csv", f, "text/csv")})
        csv_id = up_csv.json()["id"]

        with open(xlsx_path, "rb") as f:
            up_xlsx = await client.post("/assets/upload", headers=headers, files={"file": ("employee_analytics_dataset_2026.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
        xlsx_id = up_xlsx.json()["id"]

        async def ask_chat(prompt: str, asset_ids: list, c_id: str):
            res = await client.post("/chat/stream", headers=headers, json={"conversation_id": c_id, "prompt": prompt, "attached_assets": asset_ids})
            raw_text = res.text
            full_content = []
            for line in raw_text.split("\n"):
                line = line.strip()
                if line.startswith("data:"):
                    json_str = line[5:].strip()
                    if json_str:
                        try:
                            data = json.loads(json_str)
                            if "content" in data and data["content"]:
                                full_content.append(data["content"])
                        except Exception:
                            pass
            return "".join(full_content) if full_content else raw_text

        # =========================================================================
        # PHASE 2: CSV ACCEPTANCE QUERIES (20 QUERIES)
        # =========================================================================
        print("▶ PHASE 2: CSV Acceptance Queries (20 queries)...")
        c2 = await client.post("/chat/conversations", headers=headers, json={"title": "CSV Phase 2 Conv"})
        cid2 = c2.json()["id"]

        r1 = await ask_chat("How many employees are there?", [csv_id], cid2)
        results["P2_Q01_employee_count"] = str(total_rows) in r1
        details["P2_Q01_employee_count"] = f"Expected {total_rows} | Got: {r1[:120]}"

        r2 = await ask_chat("How many rows are there?", [csv_id], cid2)
        results["P2_Q02_row_count"] = str(total_rows) in r2
        details["P2_Q02_row_count"] = f"Expected {total_rows} | Got: {r2[:120]}"

        r3 = await ask_chat("What is the average age?", [csv_id], cid2)
        results["P2_Q03_avg_age"] = f"{avg_age:.2f}" in r3 or f"{round(avg_age, 1)}" in r3
        details["P2_Q03_avg_age"] = f"Expected {avg_age:.2f} | Got: {r3[:120]}"

        r4 = await ask_chat("What is the average salary?", [csv_id], cid2)
        sal_str = f"{avg_sal:,.2f}".split(".")[0]
        results["P2_Q04_avg_salary"] = sal_str in r4 or f"{int(avg_sal)}" in r4
        details["P2_Q04_avg_salary"] = f"Expected {sal_str} | Got: {r4[:120]}"

        r5 = await ask_chat("What is the median salary?", [csv_id], cid2)
        med_str = f"{median_sal:,.2f}".split(".")[0]
        results["P2_Q05_median_salary"] = med_str in r5 or f"{int(median_sal)}" in r5
        details["P2_Q05_median_salary"] = f"Expected {med_str} | Got: {r5[:120]}"

        r6 = await ask_chat("What is the highest salary?", [csv_id], cid2)
        max_str = f"{max_sal:,.2f}".split(".")[0]
        results["P2_Q06_highest_salary"] = max_str in r6 or f"{int(max_sal)}" in r6
        details["P2_Q06_highest_salary"] = f"Expected {max_str} | Got: {r6[:120]}"

        r7 = await ask_chat("What is the lowest salary?", [csv_id], cid2)
        min_str = f"{min_sal:,.2f}".split(".")[0]
        results["P2_Q07_lowest_salary"] = min_str in r7 or f"{int(min_sal)}" in r7
        details["P2_Q07_lowest_salary"] = f"Expected {min_str} | Got: {r7[:120]}"

        r8 = await ask_chat("How many missing values are there?", [csv_id], cid2)
        results["P2_Q08_missing_values"] = str(missing_vals) in r8
        details["P2_Q08_missing_values"] = f"Expected {missing_vals} | Got: {r8[:120]}"

        r9 = await ask_chat("How many duplicate rows are there?", [csv_id], cid2)
        results["P2_Q09_duplicate_rows"] = str(dup_rows) in r9
        details["P2_Q09_duplicate_rows"] = f"Expected {dup_rows} | Got: {r9[:120]}"

        r10 = await ask_chat("Show department distribution.", [csv_id], cid2)
        results["P2_Q10_dept_distribution"] = "Engineering" in r10 and "Product" in r10
        details["P2_Q10_dept_distribution"] = f"Expected depts | Got: {r10[:120]}"

        r11 = await ask_chat("Show city distribution.", [csv_id], cid2)
        results["P2_Q11_city_distribution"] = "Bangalore" in r11 and "Mumbai" in r11
        details["P2_Q11_city_distribution"] = f"Expected cities | Got: {r11[:120]}"

        r12 = await ask_chat("How many employees are in Bangalore?", [csv_id], cid2)
        results["P2_Q12_bangalore_count"] = str(bangalore_count) in r12
        details["P2_Q12_bangalore_count"] = f"Expected {bangalore_count} | Got: {r12[:120]}"

        r13 = await ask_chat("Which department has the highest average salary?", [csv_id], cid2)
        results["P2_Q13_top_dept_salary"] = top_dept in r13
        details["P2_Q13_top_dept_salary"] = f"Expected {top_dept} | Got: {r13[:120]}"

        r14 = await ask_chat("What are the top 5 highest salaries?", [csv_id], cid2)
        results["P2_Q14_top5_salaries"] = any(f"{int(s):,}" in r14 or str(int(s)) in r14 for s in top5_sals[:2])
        details["P2_Q14_top5_salaries"] = f"Expected top5 | Got: {r14[:120]}"

        r15 = await ask_chat("What are the bottom 5 salaries?", [csv_id], cid2)
        results["P2_Q15_bottom5_salaries"] = any(f"{int(s):,}" in r15 or str(int(s)) in r15 for s in bottom5_sals[:2])
        details["P2_Q15_bottom5_salaries"] = f"Expected bottom5 | Got: {r15[:120]}"

        r16 = await ask_chat("What is the average salary of Engineering employees?", [csv_id], cid2)
        eng_sal_str = f"{eng_avg_sal:,.2f}".split(".")[0]
        results["P2_Q16_eng_avg_salary"] = eng_sal_str in r16 or f"{int(eng_avg_sal)}" in r16
        details["P2_Q16_eng_avg_salary"] = f"Expected {eng_sal_str} | Got: {r16[:120]}"

        r17 = await ask_chat("How many employees joined after 2022?", [csv_id], cid2)
        results["P2_Q17_joined_after_2022"] = str(joined_after_2022) in r17
        details["P2_Q17_joined_after_2022"] = f"Expected {joined_after_2022} | Got: {r17[:120]}"

        r18 = await ask_chat("Which city has the most employees?", [csv_id], cid2)
        results["P2_Q18_top_city"] = top_city in r18
        details["P2_Q18_top_city"] = f"Expected {top_city} | Got: {r18[:120]}"

        r19 = await ask_chat("What is the average experience?", [csv_id], cid2)
        results["P2_Q19_avg_experience"] = f"{avg_exp:.2f}" in r19 or f"{round(avg_exp, 1)}" in r19
        details["P2_Q19_avg_experience"] = f"Expected {avg_exp:.2f} | Got: {r19[:120]}"

        r20 = await ask_chat("Show employees with salary greater than 80000.", [csv_id], cid2)
        results["P2_Q20_salary_gt_80k"] = str(sal_gt_80k) in r20
        details["P2_Q20_salary_gt_80k"] = f"Expected {sal_gt_80k} | Got: {r20[:120]}"

        # =========================================================================
        # PHASE 3: EXCEL ACCEPTANCE QUERIES (10 QUERIES)
        # =========================================================================
        print("▶ PHASE 3: Excel Acceptance Queries (10 queries)...")
        c3 = await client.post("/chat/conversations", headers=headers, json={"title": "Excel Phase 3 Conv"})
        cid3 = c3.json()["id"]

        xr1 = await ask_chat("How many employees are there?", [xlsx_id], cid3)
        xr2 = await ask_chat("What is the average age?", [xlsx_id], cid3)
        xr3 = await ask_chat("What is the average salary?", [xlsx_id], cid3)
        xr4 = await ask_chat("What is the highest salary?", [xlsx_id], cid3)
        xr5 = await ask_chat("Show department distribution.", [xlsx_id], cid3)
        xr6 = await ask_chat("Show city distribution.", [xlsx_id], cid3)
        xr7 = await ask_chat("How many missing values are there?", [xlsx_id], cid3)
        xr8 = await ask_chat("How many duplicate rows are there?", [xlsx_id], cid3)
        xr9 = await ask_chat("Which department has the highest average salary?", [xlsx_id], cid3)
        xr10 = await ask_chat("Show employees with salary greater than 80000.", [xlsx_id], cid3)

        results["P3_XLSX_01_employee_count"] = str(total_rows) in xr1
        results["P3_XLSX_02_avg_age"] = f"{avg_age:.2f}" in xr2 or f"{round(avg_age, 1)}" in xr2
        results["P3_XLSX_03_avg_salary"] = sal_str in xr3 or f"{int(avg_sal)}" in xr3
        results["P3_XLSX_04_highest_salary"] = max_str in xr4 or f"{int(max_sal)}" in xr4
        results["P3_XLSX_05_dept_distribution"] = "Engineering" in xr5 and "Product" in xr5
        results["P3_XLSX_06_city_distribution"] = "Bangalore" in xr6 and "Mumbai" in xr6
        results["P3_XLSX_07_missing_values"] = str(missing_vals) in xr7
        results["P3_XLSX_08_duplicate_rows"] = str(dup_rows) in xr8
        results["P3_XLSX_09_top_dept_salary"] = top_dept in xr9
        results["P3_XLSX_10_salary_gt_80k"] = str(sal_gt_80k) in xr10

        # =========================================================================
        # PHASE 4: NATURAL LANGUAGE VARIATIONS & INTENT ROUTING
        # =========================================================================
        print("▶ PHASE 4: Natural Language Variations...")
        c4 = await client.post("/chat/conversations", headers=headers, json={"title": "NL Phase 4 Conv"})
        cid4 = c4.json()["id"]

        nl1 = await ask_chat("How many people work here?", [csv_id], cid4)
        nl2 = await ask_chat("What's the mean employee age?", [csv_id], cid4)
        nl3 = await ask_chat("Who earns the most?", [csv_id], cid4)
        nl4 = await ask_chat("Give me salary stats.", [csv_id], cid4)
        nl5 = await ask_chat("Break employees down by department.", [csv_id], cid4)
        nl6 = await ask_chat("How many people are based in Bangalore?", [csv_id], cid4)
        nl7 = await ask_chat("Find employees earning above 80k.", [csv_id], cid4)

        results["P4_NL1_people_work_here"] = str(total_rows) in nl1
        results["P4_NL2_mean_employee_age"] = f"{avg_age:.2f}" in nl2 or f"{round(avg_age, 1)}" in nl2
        results["P4_NL3_who_earns_the_most"] = max_str in nl3 or f"{int(max_sal)}" in nl3
        results["P4_NL4_salary_stats"] = sal_str in nl4 or f"{int(avg_sal)}" in nl4
        results["P4_NL5_break_by_dept"] = "Engineering" in nl5 and "Product" in nl5
        results["P4_NL6_people_in_bangalore"] = str(bangalore_count) in nl6
        results["P4_NL7_earning_above_80k"] = str(sal_gt_80k) in nl7
        results["P4_NO_COLUMN_HALLUCINATION"] = "PaymentTier" not in r4 and "PaymentTier" not in r6

        # =========================================================================
        # PHASE 5: MULTI-DATASET ISOLATION
        # =========================================================================
        print("▶ PHASE 5: Multi-Dataset Isolation...")
        c5a = await client.post("/chat/conversations", headers=headers, json={"title": "ISO A Conv"})
        c5b = await client.post("/chat/conversations", headers=headers, json={"title": "ISO B Conv"})
        cid5a = c5a.json()["id"]
        cid5b = c5b.json()["id"]

        ds_a_csv = b"EmployeeID,Name,Salary\n1,Alice,50000\n2,Bob,60000\n"
        ds_b_csv = b"EmployeeID,Name,Salary\n101,Xavier,150000\n102,Yvonne,170000\n"

        up_a = await client.post("/assets/upload", headers=headers, files={"file": ("Employee_A.csv", io.BytesIO(ds_a_csv), "text/csv")})
        up_b = await client.post("/assets/upload", headers=headers, files={"file": ("Employee_B.csv", io.BytesIO(ds_b_csv), "text/csv")})
        id_a = up_a.json()["id"]
        id_b = up_b.json()["id"]

        r_a = await ask_chat("What is the average salary?", [id_a], cid5a)
        r_b = await ask_chat("What is the average salary?", [id_b], cid5b)

        p_iso = ("55,000" in r_a or "55000" in r_a) and ("160,000" in r_b or "160000" in r_b)
        results["P5_MULTI_DATASET_ISOLATION"] = p_iso
        details["P5_MULTI_DATASET_ISOLATION"] = f"DS A: {r_a[:90]} | DS B: {r_b[:90]}"

        # =========================================================================
        # PHASE 6: FOLLOW-UP QUESTIONS
        # =========================================================================
        print("▶ PHASE 6: Follow-up Questions...")
        c6 = await client.post("/chat/conversations", headers=headers, json={"title": "Followup Conv"})
        cid6 = c6.json()["id"]

        fu1 = await ask_chat("What is the average salary?", [csv_id], cid6)
        fu2 = await ask_chat("What about Engineering?", [csv_id], cid6)
        fu3 = await ask_chat("And Bangalore?", [csv_id], cid6)

        p_fu1 = sal_str in fu1 or f"{int(avg_sal)}" in fu1
        p_fu2 = eng_sal_str in fu2 or f"{int(eng_avg_sal)}" in fu2
        p_fu3 = str(bangalore_count) in fu3 or "Bangalore" in fu3

        results["P6_FOLLOWUP_CONTEXT_RESOLVED"] = p_fu1 and p_fu2 and p_fu3
        details["P6_FOLLOWUP_CONTEXT_RESOLVED"] = f"FU1: {fu1[:60]} | FU2: {fu2[:60]} | FU3: {fu3[:60]}"

        # =========================================================================
        # PHASE 7: FAILURE CASES
        # =========================================================================
        print("▶ PHASE 7: Failure Cases...")
        c7_1 = await client.post("/chat/conversations", headers=headers, json={"title": "Fail 1 Conv"})
        c7_2 = await client.post("/chat/conversations", headers=headers, json={"title": "Fail 2 Conv"})
        c7_3 = await client.post("/chat/conversations", headers=headers, json={"title": "Fail 3 Conv"})

        no_age_csv = b"EmployeeID,Name,Salary\n1,Alice,70000\n"
        up_no_age = await client.post("/assets/upload", headers=headers, files={"file": ("no_age.csv", io.BytesIO(no_age_csv), "text/csv")})
        id_no_age = up_no_age.json()["id"]
        r_no_age = await ask_chat("What is the average age?", [id_no_age], c7_1.json()["id"])
        p_no_age = "does not contain an Age column" in r_no_age

        no_sal_csv = b"EmployeeID,Name,Age\n1,Alice,30\n"
        up_no_sal = await client.post("/assets/upload", headers=headers, files={"file": ("no_salary.csv", io.BytesIO(no_sal_csv), "text/csv")})
        id_no_sal = up_no_sal.json()["id"]
        r_no_sal = await ask_chat("What is the average salary?", [id_no_sal], c7_2.json()["id"])
        p_no_sal = "does not contain a Salary column" in r_no_sal

        str_num_csv = b"EmployeeID,Name,Age,Salary\n1,Alice,30,85000\n2,Bob,40,95000\n"
        up_str_num = await client.post("/assets/upload", headers=headers, files={"file": ("str_num.csv", io.BytesIO(str_num_csv), "text/csv")})
        id_str_num = up_str_num.json()["id"]
        r_str_num = await ask_chat("What is the average salary?", [id_str_num], c7_3.json()["id"])
        p_str_num = "90,000" in r_str_num or "90000" in r_str_num

        results["P7_FAILURE_NO_AGE_COLUMN"] = p_no_age
        results["P7_FAILURE_NO_SALARY_COLUMN"] = p_no_sal
        results["P7_FAILURE_NUMERIC_STRINGS"] = p_str_num

    print("\n" + "=" * 80)
    print("📊 ISOLATED ACCEPTANCE AUDIT RESULTS SUMMARY:")
    all_ok = True
    for test_key, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            all_ok = False
        print(f"  {status} - {test_key}")
        if not passed and test_key in details:
            print(f"     -> {details[test_key]}")

    print("=" * 80)
    print(f"OVERALL AUDIT RESULT: {'✅ ALL TESTS PASSED' if all_ok else '❌ DEFECTS DISCOVERED'}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_csv_excel_audit())
