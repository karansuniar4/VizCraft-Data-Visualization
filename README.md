# VizCraft — Interactive Data Visualization Dashboard

**CodSoft Data Analytics Internship · Task 3**

VizCraft is a beginner-friendly Streamlit dashboard for exploring CSV data, building interactive charts, checking data quality, and exporting analysis results. It includes a reproducible demo dataset, so you can run it without downloading any external files.

## Features

- Upload your own CSV or use the built-in demo dataset.
- KPIs, data preview, column metadata, and statistical summaries.
- Interactive bar, line, scatter, histogram, box, and pie charts.
- Pearson correlation heatmap and a ranked view of numerical relationships.
- Missing-value and duplicate checks plus potential numerical outlier detection using the IQR rule.
- Category, numeric-range, and date-range filters when suitable columns are present.
- Download filtered data, an analysis summary, a KPI report, and a chart as interactive HTML.
- Helpful handling for empty files, parse errors, empty filtered results, and datasets with few/no numeric columns.

## Requirements

- Windows 10/11
- Python 3.10 or newer (Python 3.11 recommended)
- Internet connection for the first dependency installation

## Windows installation and run

1. Install Python from [python.org](https://www.python.org/downloads/windows/). During setup, enable **Add Python to PATH**.
2. Extract `VizCraft_Task3_Data_Visualization.zip` to a folder.
3. Open the extracted `VizCraft_Task3_Data_Visualization` folder.
4. Double-click `run_windows.bat`, or run these commands in Command Prompt from the project folder:

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   streamlit run app.py
   ```

5. Streamlit normally opens the dashboard in your browser. If not, copy the local URL printed in the terminal (usually `http://localhost:8501`).

## How to use

1. Pick **Built-in demo dataset** or **Upload a CSV** in the sidebar.
2. Set filters in the **Filters** expander. All tabs use the filtered rows.
3. Use **Data & columns** to inspect rows and column metadata.
4. In **Visualizations**, choose a chart type and select its axes/options.
5. Review missing values, duplicates, and IQR outlier flags in **Data quality**.
6. Download your filtered CSV, text summary, KPI report, or chart HTML from **Downloads**.

## Notes and limitations

- CSV files should have a header row. UTF-8 is recommended; common UTF-8 and Latin-1 encodings are attempted.
- Date filters are offered for columns already stored as datetimes or whose names suggest a date/time and whose values parse consistently.
- Scatter plots and correlation analysis need at least two numerical columns. Some charts may be less meaningful for IDs or free-text columns.
- Correlation indicates association, not causation.
- Outlier detection is a statistical flag for review, not a guarantee that a value is wrong.
- The dashboard does not modify the uploaded source file. Exported data is generated on demand.
- Downloaded reports are created in the browser session; the `reports/` and `visualizations/` directories are included as project organization folders.

## Project structure

```text
VizCraft_Task3_Data_Visualization/
├── app.py
├── requirements.txt
├── README.md
├── run_windows.bat
├── .gitignore
├── data/
│   └── README.txt
├── reports/
│   └── README.txt
└── visualizations/
    └── README.txt
```

## Internship submission checklist

- [ ] Run `run_windows.bat` and confirm the dashboard opens.
- [ ] Try the demo data and one of your own CSV files.
- [ ] Test filters, each chart type, quality checks, and downloads.
- [ ] Add screenshots of your running dashboard to your submission if required.
- [ ] Follow your internship provider's submission instructions.

## License

Created as an educational project starter for internship learning and demonstration.
