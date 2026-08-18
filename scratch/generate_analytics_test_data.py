import os
import pandas as pd
import numpy as np

def generate_test_datasets():
    os.makedirs("scratch", exist_ok=True)
    np.random.seed(42)

    departments = ["Engineering", "Product", "Data Platform", "Security", "Operations"]
    cities = ["Bangalore", "Mumbai", "Pune", "Delhi", "Hyderabad"]
    genders = ["Male", "Female", "Non-Binary"]

    data = []
    for i in range(1, 101):
        dept = np.random.choice(departments, p=[0.3, 0.2, 0.2, 0.15, 0.15])
        city = np.random.choice(cities, p=[0.35, 0.25, 0.15, 0.15, 0.1])
        gender = np.random.choice(genders, p=[0.48, 0.48, 0.04])
        
        # Base salary depends somewhat on dept & experience for realistic distribution
        exp = int(np.random.randint(1, 21))
        base_sal = 50000 + (exp * 4000) + np.random.randint(-5000, 10000)
        if dept == "Engineering":
            base_sal += 15000
        elif dept == "Data Platform":
            base_sal += 10000

        age = int(22 + exp + np.random.randint(0, 3))
        joining_year = int(2026 - exp)
        score = round(float(np.random.uniform(2.5, 5.0)), 1)

        data.append({
            "EmployeeID": i,
            "Name": f"Employee_{i}",
            "Age": age,
            "Gender": gender,
            "City": city,
            "Department": dept,
            "Salary": base_sal,
            "Experience": exp,
            "JoiningYear": joining_year,
            "PerformanceScore": score
        })

    df = pd.DataFrame(data)

    # Introduce deliberately controlled missing values
    df.loc[5, "Age"] = np.nan
    df.loc[15, "Salary"] = np.nan
    df.loc[25, "City"] = np.nan

    # Add 2 duplicate rows at the end
    dup_row1 = df.iloc[0].copy()
    dup_row2 = df.iloc[1].copy()
    df = pd.concat([df, pd.DataFrame([dup_row1, dup_row2])], ignore_index=True)

    csv_path = "scratch/employee_analytics_dataset_2026.csv"
    xlsx_path = "scratch/employee_analytics_dataset_2026.xlsx"

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    print(f"Generated CSV dataset: {csv_path} ({len(df)} total rows)")
    print(f"Generated XLSX dataset: {xlsx_path} ({len(df)} total rows)")
    return csv_path, xlsx_path

if __name__ == "__main__":
    generate_test_datasets()
