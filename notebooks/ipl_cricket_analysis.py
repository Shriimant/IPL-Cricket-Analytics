# Databricks notebook source
# MAGIC %md
# MAGIC ###Import Required Libraries

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ###Read Dataset From Volume

# COMMAND ----------

matches_df = spark.read.format("csv") \
.option("header","true") \
.option("inferSchema","true") \
.load("/Volumes/workspace/default/ipl_data/matches.csv")

display(matches_df)

# COMMAND ----------

deliveries_df = spark.read.format("csv") \
.option("header","true") \
.option("inferSchema","true") \
.load("/Volumes/workspace/default/ipl_data/deliveries.csv")

display(deliveries_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Create BRONZE Layer Tables

# COMMAND ----------

matches_df.write.format("delta") \
.mode("overwrite") \
.saveAsTable("bronze_matches")

# COMMAND ----------

deliveries_df.write.format("delta") \
.mode("overwrite") \
.saveAsTable("bronze_deliveries")

# COMMAND ----------

spark.sql("SELECT * FROM bronze_matches").show(5)

# COMMAND ----------

spark.sql("SELECT * FROM bronze_deliveries").show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Create Silver Matches Table (Clean Data)

# COMMAND ----------

silver_matches = spark.sql("""
SELECT
id AS match_id,
season,
team1,
team2,
toss_winner,
toss_decision,
venue,
winner
FROM bronze_matches
WHERE winner IS NOT NULL
""")

display(silver_matches)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Save Silver Matches Table

# COMMAND ----------

silver_matches.write.format("delta") \
.mode("overwrite") \
.saveAsTable("silver_matches")

# COMMAND ----------

# MAGIC %md
# MAGIC ###Clean Deliveries Data

# COMMAND ----------

silver_deliveries = spark.sql("""
SELECT
match_id,
inning,
batting_team,
bowling_team,
over,
ball,
batsman,
bowler,
total_runs,
player_dismissed
FROM bronze_deliveries
""")

display(silver_deliveries)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Save Silver Deliveries Table

# COMMAND ----------

silver_deliveries.write.format("delta") \
.mode("overwrite") \
.saveAsTable("silver_deliveries")

# COMMAND ----------

# MAGIC %md
# MAGIC ###Verify Silver Tables

# COMMAND ----------

spark.sql("SELECT * FROM silver_matches LIMIT 5").show()

# COMMAND ----------

spark.sql("SELECT * FROM silver_deliveries LIMIT 5").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ###Create ML Feature Dataset

# COMMAND ----------

gold_match_features = spark.sql("""

SELECT
match_id,
team1,
team2,
toss_winner,
venue,
CASE
    WHEN winner = team1 THEN 1
    ELSE 0
END AS team1_win

FROM silver_matches

""")

display(gold_match_features)


# COMMAND ----------

# MAGIC %md
# MAGIC ###Save Gold Feature Table

# COMMAND ----------

gold_match_features.write.format("delta") \
.mode("overwrite") \
.saveAsTable("gold_match_features")

# COMMAND ----------

# MAGIC %md
# MAGIC ###Verify Gold Table

# COMMAND ----------

spark.sql("SELECT * FROM gold_match_features LIMIT 5").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ###Convert Spark Data to Pandas

# COMMAND ----------

ml_df = spark.sql("SELECT * FROM gold_match_features")

pandas_df = ml_df.toPandas()

pandas_df.head()

# COMMAND ----------

# MAGIC %md
# MAGIC ###Encode Categorical Columns

# COMMAND ----------

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()

pandas_df['team1'] = le.fit_transform(pandas_df['team1'])
pandas_df['team2'] = le.fit_transform(pandas_df['team2'])
pandas_df['toss_winner'] = le.fit_transform(pandas_df['toss_winner'])
pandas_df['venue'] = le.fit_transform(pandas_df['venue'])

# COMMAND ----------

# MAGIC %md
# MAGIC ###Split Dataset for Training

# COMMAND ----------

from sklearn.model_selection import train_test_split

X = pandas_df[['team1','team2','toss_winner','venue']]
y = pandas_df['team1_win']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Train Machine Learning Model

# COMMAND ----------

from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier()

model.fit(X_train, y_train)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Predict Results

# COMMAND ----------

predictions = model.predict(X_test)

predictions[:10]

# COMMAND ----------

# MAGIC %md
# MAGIC ###Evaluate Model Accuracy

# COMMAND ----------

from sklearn.metrics import accuracy_score

accuracy = accuracy_score(y_test, predictions)

print("Model Accuracy:", accuracy)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Calculate Team Win Count

# COMMAND ----------

team_wins = spark.sql("""

SELECT
winner AS team,
COUNT(*) AS total_wins
FROM silver_matches
GROUP BY winner

""")

display(team_wins)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Calculate Total Matches Played

# COMMAND ----------

team_matches = spark.sql("""

SELECT team, COUNT(*) AS matches_played
FROM (
    SELECT team1 AS team FROM silver_matches
    UNION ALL
    SELECT team2 AS team FROM silver_matches
)
GROUP BY team

""")

display(team_matches)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Create Team Win Percentage

# COMMAND ----------

team_stats = team_matches.join(
    team_wins,
    team_matches.team == team_wins.team,
    "left"
).select(
    team_matches.team,
    col("matches_played"),
    col("total_wins")
)

team_stats = team_stats.fillna(0)

team_stats = team_stats.withColumn(
    "win_percentage",
    col("total_wins") / col("matches_played")
)

display(team_stats)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Join Team Stats With Matches

# COMMAND ----------

team1_stats = team_stats.withColumnRenamed("team","team1") \
.withColumnRenamed("win_percentage","team1_win_pct")

team2_stats = team_stats.withColumnRenamed("team","team2") \
.withColumnRenamed("win_percentage","team2_win_pct")

# COMMAND ----------

# MAGIC %md
# MAGIC ###Build Improved ML Dataset

# COMMAND ----------

enhanced_features = gold_match_features \
.join(team1_stats, "team1", "left") \
.join(team2_stats, "team2", "left")

display(enhanced_features)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Convert to Pandas Again

# COMMAND ----------

enhanced_pd = enhanced_features.toPandas()

enhanced_pd.head()

# COMMAND ----------

# MAGIC %md
# MAGIC ###Encode Categorical Columns

# COMMAND ----------

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()

enhanced_pd['team1'] = le.fit_transform(enhanced_pd['team1'])
enhanced_pd['team2'] = le.fit_transform(enhanced_pd['team2'])
enhanced_pd['toss_winner'] = le.fit_transform(enhanced_pd['toss_winner'])
enhanced_pd['venue'] = le.fit_transform(enhanced_pd['venue'])

# COMMAND ----------

# MAGIC %md
# MAGIC ###Train Model Again

# COMMAND ----------

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

X = enhanced_pd[['team1','team2','toss_winner','venue','team1_win_pct','team2_win_pct']]
y = enhanced_pd['team1_win']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier()

model.fit(X_train, y_train)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Predict

# COMMAND ----------

pred = model.predict(X_test)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Check Accuracy Again

# COMMAND ----------

from sklearn.metrics import accuracy_score

accuracy = accuracy_score(y_test, pred)

print("Improved Model Accuracy:", accuracy)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Predict Win Probability

# COMMAND ----------

probabilities = model.predict_proba(X_test)

probabilities[:5]

# COMMAND ----------

# MAGIC %md
# MAGIC ###Convert to Percentage

# COMMAND ----------

import pandas as pd

results = pd.DataFrame({
    "Team1_Win_Probability": probabilities[:,1],
    "Actual_Result": y_test.values
})

results.head()

# COMMAND ----------

# MAGIC %md
# MAGIC ###Show Percentage

# COMMAND ----------

results["Team1_Win_%"] = results["Team1_Win_Probability"] * 100

results.head()

# COMMAND ----------

# MAGIC %md
# MAGIC ###Import MLflow

# COMMAND ----------

import mlflow
import mlflow.sklearn

# COMMAND ----------

# MAGIC %md
# MAGIC ###Start MLflow Experiment

# COMMAND ----------

mlflow.start_run()

# COMMAND ----------

# MAGIC %md
# MAGIC ###Log Model Metrics

# COMMAND ----------

mlflow.log_metric("accuracy", accuracy)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Log the Model

# COMMAND ----------

mlflow.sklearn.log_model(
    model,
    "ipl_match_prediction_model",
    input_example=X_train.iloc[:5]
)

mlflow.end_run()

# COMMAND ----------

# MAGIC %md
# MAGIC ###SQL Analytics

# COMMAND ----------

# MAGIC %md
# MAGIC ####Top IPL Teams by Wins

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC winner AS team,
# MAGIC COUNT(*) AS total_wins
# MAGIC FROM silver_matches
# MAGIC GROUP BY winner
# MAGIC ORDER BY total_wins DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ####Toss Impact on Match Result

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC toss_winner,
# MAGIC COUNT(*) AS matches_won
# MAGIC FROM silver_matches
# MAGIC WHERE toss_winner = winner
# MAGIC GROUP BY toss_winner
# MAGIC ORDER BY matches_won DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ####Venue Advantage

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC venue,
# MAGIC COUNT(*) AS matches_played
# MAGIC FROM silver_matches
# MAGIC GROUP BY venue
# MAGIC ORDER BY matches_played DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ####Most Successful Teams

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC team,
# MAGIC win_percentage
# MAGIC FROM (
# MAGIC     SELECT
# MAGIC     winner AS team,
# MAGIC     COUNT(*) AS wins,
# MAGIC     COUNT(*) * 1.0 /
# MAGIC     (SELECT COUNT(*) FROM silver_matches) AS win_percentage
# MAGIC     FROM silver_matches
# MAGIC     GROUP BY winner
# MAGIC )
# MAGIC ORDER BY win_percentage DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ####Average Runs per Match

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC match_id,
# MAGIC SUM(total_runs) AS total_runs
# MAGIC FROM silver_deliveries
# MAGIC GROUP BY match_id
# MAGIC ORDER BY total_runs DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ####Best Batting Teams

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC batting_team,
# MAGIC SUM(total_runs) AS total_runs
# MAGIC FROM silver_deliveries
# MAGIC GROUP BY batting_team
# MAGIC ORDER BY total_runs DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ####Most Successful Teams by Venue

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC venue,
# MAGIC winner,
# MAGIC COUNT(*) AS wins
# MAGIC FROM silver_matches
# MAGIC GROUP BY venue, winner
# MAGIC ORDER BY wins DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ####Toss Decision Impact

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC toss_decision,
# MAGIC COUNT(*) AS matches
# MAGIC FROM silver_matches
# MAGIC GROUP BY toss_decision

# COMMAND ----------

# MAGIC %md
# MAGIC ####Average Runs by Team

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC batting_team,
# MAGIC AVG(total_runs) AS avg_runs
# MAGIC FROM silver_deliveries
# MAGIC GROUP BY batting_team
# MAGIC ORDER BY avg_runs DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ####Top Wicket Taking Bowlers

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC bowler,
# MAGIC COUNT(player_dismissed) AS wickets
# MAGIC FROM silver_deliveries
# MAGIC WHERE player_dismissed IS NOT NULL
# MAGIC GROUP BY bowler
# MAGIC ORDER BY wickets DESC

# COMMAND ----------

spark.sql("SELECT * FROM silver_matches") \
.toPandas() \
.to_csv("/Volumes/workspace/default/ipl_data/silver_matches.csv", index=False)

# COMMAND ----------

spark.sql("SELECT * FROM silver_deliveries") \
.toPandas() \
.to_csv("/Volumes/workspace/default/ipl_data/silver_deliveries.csv", index=False)