# TRS Engine Core 🚀

**Talent Recruitment System - Emotional Inference Engine**

An intelligent recruitment matching system that evaluates candidate-job compatibility while considering emotional states and personalized communication.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Data Analysis & Visualization](#data-analysis--visualization)
- [Extensions & Tools](#extensions--tools)
- [Contributing](#contributing)

---

## 🎯 Overview

The TRS Engine Core is a data science project that matches job candidates with vacancies using:

- **Technology Stack Matching**: Calculates overlap between candidate skills and job requirements
- **Penalty System**: Applies deductions for modality, zone, and urgency mismatches
- **Emotional Intelligence**: Generates personalized messages based on candidate emotional state
- **Comprehensive Logging**: Outputs results in Markdown and CSV formats with timestamps

---

## ✨ Features

- ✅ **Automated Matching**: Evaluates all candidate-vacancy combinations
- ✅ **Emotional Messaging**: Tailored communication for Positive, Neutral, and Negative states
- ✅ **Dual Output Formats**: 
  - Markdown reports for human review
  - CSV files for data analysis
- ✅ **Timestamp Tracking**: All outputs include date-time stamps
- ✅ **Data Visualization**: Built-in analyzer with charts and insights
- ✅ **Best Practices**: Type hints, docstrings, and clean code structure

---

## 📂 Project Structure

```
TRS_Engine_Core/
├── Data/
│   ├── profiles.json                  # Candidate profiles (SOURCE DATA)
│   ├── Vacancy.json                   # Job vacancies (SOURCE DATA)
│   ├── recruiters.json                # Recruiter database (SOURCE DATA)
│   └── candidate_consent_log.json     # Generated from emotional_log (optional)
├── Modules/
│   ├── emotional_inference_engine.py  # Main inference engine (Step 1)
│   ├── chat_simulator.py              # Interview simulation (Step 2)
│   ├── emotional_closure.py           # Interview closure & consent (integrated)
│   ├── candidate_filter.py            # Candidate filtering logic (Step 3)
│   ├── report_generator.py            # Report generation MD/CSV (Step 4)
│   ├── response_evaluator.py          # Response quality analysis
│   ├── timezone_compatibility.py      # Timezone matching
│   ├── recruiter_assignment.py        # Dynamic recruiter assignment
│   ├── questions_bank.py              # Technical questions database
│   ├── process_candidates.py          # Main processing pipeline (orchestrator)
│   │
│   ├── consent_simulator.py           # Consent generator from emotional_log (optional)
│   ├── data_visualizer.py             # Data analysis & visualization (optional)
│   └── profile_simulator.py           # Profile generator (testing)
├── Logs/
│   ├── inference_results_*.md         # Markdown reports
│   ├── emotional_log_*.csv            # CSV data
│   ├── reports/                       # RRHH reports
│   │   ├── rrhh_registry.md           # Main candidate report
│   │   ├── rrhh_registry.csv          # CSV export
│   │   ├── accepted_candidates.md     # Accepted candidates
│   │   ├── rejected_candidates.md     # Rejected candidates
│   │   ├── talent_pool.csv            # Talent pool database
│   │   └── feedback/                  # Individual feedback files
│   ├── Plots/                         # Generated charts
│   └── insights.txt                   # Analysis summary
├── Docs/
│   ├── trs_architecture.md            # System architecture
│   └── emotional_closure_integration.md  # Closure integration guide
├── .vscode/
│   └── settings.json                  # VS Code configuration
├── requirements.txt                   # Python dependencies
├── install_extensions.ps1             # Extension installer
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd TRS_Engine_Core
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `pandas` - Data manipulation
- `matplotlib` - Plotting
- `seaborn` - Statistical visualizations

### 3. Install Recommended Extensions (Optional)

**Windows (PowerShell):**
```powershell
.\install_extensions.ps1
```

**Manual Installation:**
Open Extensions panel (`Ctrl+Shift+X`) and install:
- Python + Pylance
- Jupyter
- Data Wrangler
- Rainbow CSV
- GitLens
- Error Lens

---

## 🚀 Usage

### Run Inference Engine

```bash
python Modules/emotional_inference_engine.py
```

**Output:**
```
Logs/inference_results_2025-11-03_12-30-45.md
Logs/emotional_log_2025-11-03_12-30-45.csv
```

### Analyze Results

```bash
python Modules/data_visualizer.py
```

**Generates:**
- Score distribution charts
- Emotional state analysis
- Candidate-vacancy heatmap
- Correlation matrix
- Insights summary (`insights.txt`)

**Output Location:**
```
Logs/visualizations/
├── score_distributions.png
├── emotional_analysis.png
├── candidate_heatmap.png
└── correlation_matrix.png
```

---

## 📊 Data Analysis & Visualization

### Quick Analysis with Pandas

```python
import pandas as pd

# Load latest CSV
df = pd.read_csv('Logs/emotional_log_2025-11-03_12-30-45.csv')

# Top matches
df.nlargest(5, 'adjusted_score')

# Average by emotional state
df.groupby('emotional_state')['adjusted_score'].mean()

# Filter negative candidates
df[df['emotional_state'] == 'Negative']
```

### Visualization Examples

The `data_visualizer.py` script provides:

1. **Score Distributions**: Histograms of match scores, penalties, and adjusted scores
2. **Emotional Analysis**: Box plots and violin plots by emotional state
3. **Heatmap**: Visual matrix of candidate-vacancy matches
4. **Correlation Matrix**: Relationship between numerical features

---

## 🛠️ Extensions & Tools

### Essential Extensions

| Extension | Purpose |
|-----------|---------|
| **Python + Pylance** | IntelliSense, type checking |
| **Jupyter** | Interactive notebooks |
| **Data Wrangler** | Visual CSV analysis |
| **Rainbow CSV** | Color-coded CSV columns |
| **GitLens** | Git blame & history |
| **Error Lens** | Inline error display |

### Settings Configured

- ✅ Auto-format on save
- ✅ 4-space indentation for Python
- ✅ 2-space indentation for JSON
- ✅ Auto-organize imports
- ✅ Type checking enabled
- ✅ Hidden `__pycache__` folders

---

## 📈 Data Format

### Input: `profiles.json`

```json
{
  "name": "Luis",
  "stack": ["Docker", "C#", "Node.js"],
  "experience_years": 3,
  "emotional_state": "Neutral",
  "preferred_modality": "Hybrid",
  "zone": "Central"
}
```

### Input: `Vacancy.json`

```json
{
  "title": "Backend Node + RoR Developer",
  "company": "FullStack Labs",
  "modality": "Remote",
  "zone": "Global",
  "level": "Senior",
  "stack": ["Node.js", "Ruby on Rails", "PostgreSQL", "Docker"],
  "urgency": "high"
}
```

### Output: `emotional_log_*.csv`

```csv
name,vacancy,match_score,penalty,adjusted_score,emotional_state,message
Luis,Backend Node + RoR Developer,0.5,0.5,0.0,Neutral,"Hello Luis, thanks..."
```

---

## 🧪 Testing

Run the inference engine with sample data:

```bash
python Modules/emotional_inference_engine.py
```

Expected output:
- 10 profiles × 3 vacancies = 30 match records
- Markdown report with analysis
- CSV file for visualization

---

## 📝 Logging

All logs are timestamped and stored in `Logs/`:

```
inference_results_YYYY-MM-DD_HH-MM-SS.md
emotional_log_YYYY-MM-DD_HH-MM-SS.csv
```

**Markdown Report Includes:**
- Executive summary
- Detailed candidate results
- Emotional state distribution
- Top 5 best matches
- Recommendations

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is part of an AI/Data Science portfolio.

---

## 👤 Author

**TRS Engine Core Development Team**

---

## 🙏 Acknowledgments

- Emotional Intelligence in Recruitment Research
- Python Data Science Community
- Open Source Visualization Libraries

---

## 📞 Support

For issues or questions, please open an issue in the repository.

---

**Version:** 1.0  
**Last Updated:** 2025-11-03

