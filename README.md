# 🏏 IPL Cricket Analytics & Match Prediction

## 📌 Project Overview

This project focuses on analyzing IPL cricket data and predicting match outcomes using Machine Learning. The solution is built using Databricks for data processing and Power BI for visualization.

---

## 🎯 Problem Statement

Predict which team will win a cricket match based on historical match data, team performance, and match conditions.

---

## 💼 Business Value

* Helps analysts understand key winning factors
* Useful for commentators and teams
* Can be extended for betting analytics and fan engagement

---

## 🏗️ Architecture

![Architecture](images/ipl_architecture_diagram.png)

---

## ⚙️ Tech Stack

* Databricks (PySpark)
* Python (Machine Learning)
* MLflow (Model Tracking)
* Power BI (Dashboard)
* GitHub (Version Control)

---

## 🔄 Data Pipeline

* Bronze Layer → Raw Data Ingestion
* Silver Layer → Data Cleaning
* Gold Layer → Feature Engineering
* ML Model → Random Forest Classifier

---

## 🤖 Machine Learning

* Model: Random Forest
* Task: Binary Classification
* Output: Win Probability (%)
* Accuracy: ~56%

---

## 📊 Power BI Dashboard

Dashboard provides:

* Team performance analysis
* Top teams & venues
* Toss impact
* Match outcome prediction

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

1. Upload dataset to Databricks
2. Run notebook for data processing
3. Train ML model
4. Export results
5. Open Power BI dashboard

---

## 👤 Author

Shrimant Moghe
