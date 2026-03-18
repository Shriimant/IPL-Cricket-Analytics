# 🏏 IPL Cricket Analytics & Match Prediction


## 🔥 Key Highlights

- End to End Data Pipeline using Databricks (Bronze → Silver → Gold)
- Machine Learning Model for Match Prediction.
- Interactive Power BI Dashboard.
- MLflow Experiment Tracking.

---

## 📌 Project Overview

This project focuses on analyzing IPL cricket data and predicting match outcomes using Machine Learning. The solution is built using Databricks for data processing and Power BI for visualization.

---

## 🎯 Problem Statement

Predict which team will win a cricket match based on historical match data, team performance and match conditions.

---

## 💼 Business Value

* Helps analysts understand key winning factors.
* Useful for commentators and teams.
* Can be extended for betting analytics and fan engagement.

---

## 🏗️ Architecture

![Pipeline DAG](https://github.com/Shriimant/IPL-Cricket-Analytics/blob/main/images/IPL_Architecture_Diagram.png)

---

## ⚙️ Tech Stack

* Databricks (PySpark)
* Python (Machine Learning)
* MLflow (Model Tracking)
* Power BI (Dashboard)
* GitHub (Version Control)

---

## 🔍 Data Understanding & Feature Engineering

- Dataset includes match-level and ball-by-ball data
- Key features used:
  - Venue (home advantage impact)
  - Toss decision (bat/field influence)
  - Teams (historical performance)
- Data cleaning handled missing and inconsistent values
- Created structured dataset for ML model

---

## 🗄️ Delta Lake Implementation

- Implemented Delta tables using Databricks Unity Catalog
- Converted Silver layer data into Delta format using PySpark
- Ensures reliable storage with ACID properties
- Enables scalable and efficient data processing

Example:

df.write.format("delta").mode("overwrite").saveAsTable("silver_matches_delta")

---

## ⚡ Delta Optimization

- Delta format improves query performance
- Supports scalable data pipelines in Databricks

---

## 🔄 Data Pipeline

* Bronze Layer → Raw Data Ingestion
* Silver Layer → Data Cleaning
* Gold Layer → Feature Engineering
* ML Model → Random Forest Classifier
* Silver layer data stored as Delta table for downstream ML and analytics.

---

## 🤖 Model Selection & Technical Reasoning

- Problem Type: Classification
- Model Used: Random Forest Classifier
- Reason:
  - Handles non-linear relationships
  - Works well with structured data
  - Robust against overfitting

---


## 📊 Model Evaluation

- Train-Test Split: 80-20
- Metric Used: Accuracy
- Model Accuracy: ~56%
- Insight: Model performance can improve with better features and tuning

---

## 🔗 Pipeline Integration

- Data processed through Bronze → Silver → Gold layers
- Gold layer used for model training
- Predictions generated and visualized in Power BI dashboard

---

## 📊 Power BI Dashboard

Dashboard provides:

* Team performance analysis
* Top teams & venues
* Toss impact
* Match outcome prediction

---

## 📊 Dashboard Preview

![Page 1](images/page1.png)
![Page 2](images/page2.png)
![Page 3](images/page3.png)

---


## 📁 Project Structure

```
IPL-Cricket-Analytics/
│
├── data/
├── notebooks/
├── powerbi/
├── images/
├── docs/
├── README.md
```

---

## 🚀 How to Run

1. Upload dataset to Databricks (DBFS)
2. Run notebook for Bronze → Silver → Gold transformation
3. Train Machine Learning model.
4. Export processed data as CSV.
5. Open Power BI dashboard (.pbix file)

---

## 👤 Author

Shrimant Moghe
