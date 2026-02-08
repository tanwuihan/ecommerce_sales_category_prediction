import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# ---------------- LOAD DATA ----------------
df = pd.read_csv("products_raw.csv")

# ---------------- CLEAN ----------------
df["rating"] = df["rating"].fillna(df["rating"].median())
df["rating_count"] = df["rating_count"].fillna(0)

# ---------------- FEATURES & TARGET ----------------
X = df[["price", "rating", "rating_count", "category"]]
y = df["sold_quantity"]

num_features = ["price", "rating", "rating_count"]
cat_features = ["category"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), num_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features)
])

# ---------------- TRAIN-TEST SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------- MODELS ----------------
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=200, learning_rate=0.1, random_state=42)
}

results = {}
trained_pipelines = {}

# ---------------- TRAIN & EVALUATE ----------------
for name, model in models.items():
    pipe = Pipeline([
        ("prep", preprocessor),
        ("model", model)
    ])

    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    rmse = np.sqrt(mse)

    results[name] = {"MAE": mae, "RMSE": rmse}
    trained_pipelines[name] = pipe

    print(f"\n{name} Performance:")
    print("MAE :", mae)
    print("RMSE:", rmse)

# ---------------- MODEL COMPARISON ----------------
results_df = pd.DataFrame(results).T
print("\nModel Comparison:")
print(results_df)

# Select best model (lowest RMSE)
best_model_name = results_df["RMSE"].idxmin()
best_model = trained_pipelines[best_model_name]

print(f"\n✅ Best Performing Model: {best_model_name}")

# ---------------- PREDICT SALES USING BEST MODEL ----------------
df["predicted_sales"] = best_model.predict(X)

# ---------------- CATEGORY-LEVEL ANALYSIS ----------------
predicted_by_category = (
    df.groupby("category")["predicted_sales"]
      .mean()
      .sort_values(ascending=False)
)

print("\n📊 Predicted Average Sales by Category:")
print(predicted_by_category.to_frame(name="Predicted_Average_Sales"))

best_category = predicted_by_category.idxmax()
print(f"\n🔥 Best Selling Category (Predicted): {best_category}")

# ---------------- VISUALIZATION ----------------
results_df.plot(kind="bar", figsize=(8,5), title="Model Performance Comparison")
plt.ylabel("Error")
plt.show()

predicted_by_category.plot(
    kind="bar",
    figsize=(8,5),
    title="Predicted Average Sales by Category"
)
plt.ylabel("Predicted Sales")
plt.show()
