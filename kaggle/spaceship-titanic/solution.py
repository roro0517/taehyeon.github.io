# Spaceship Titanic - Kaggle competition solution
# Copy-paste this whole file into a Kaggle notebook cell (or split at the "# %%" markers
# into separate cells) and run. It reads train.csv/test.csv from /kaggle/input/,
# engineers features, trains a gradient boosting model, and writes submission.csv.

# %%
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold

INPUT_DIR = "/kaggle/input/spaceship-titanic"

train = pd.read_csv(f"{INPUT_DIR}/train.csv")
test = pd.read_csv(f"{INPUT_DIR}/test.csv")

test_passenger_ids = test["PassengerId"].copy()

# %%
# Feature engineering: apply the same transformations to train and test together
# so encodings line up, then split back out at the end.

SPEND_COLS = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]


def engineer_features(df):
    df = df.copy()

    # PassengerId format is gggg_pp -> group id and position within group.
    df["Group"] = df["PassengerId"].str.split("_").str[0]
    group_sizes = df.groupby("Group")["PassengerId"].transform("count")
    df["GroupSize"] = group_sizes

    # Cabin format is deck/num/side.
    cabin_parts = df["Cabin"].str.split("/", expand=True)
    df["Deck"] = cabin_parts[0]
    df["CabinNum"] = pd.to_numeric(cabin_parts[1], errors="coerce")
    df["Side"] = cabin_parts[2]

    # Family name, used only to compute family size (people sharing a group
    # are often family, but last name catches families split across groups).
    df["LastName"] = df["Name"].str.split(" ").str[-1]
    family_sizes = df.groupby("LastName")["PassengerId"].transform("count")
    df["FamilySize"] = family_sizes.where(df["LastName"].notna(), df["GroupSize"])

    # Spending: missing amenity spend most likely means 0, especially for
    # passengers in CryoSleep (they can't spend anything).
    for col in SPEND_COLS:
        df[col] = df[col].fillna(0)
    df["TotalSpend"] = df[SPEND_COLS].sum(axis=1)
    df["HasSpent"] = (df["TotalSpend"] > 0).astype(int)

    # CryoSleep passengers can't spend money, so if it's missing but they
    # spent something, they weren't asleep; if they spent nothing, assume True.
    cryo_missing = df["CryoSleep"].isna()
    df.loc[cryo_missing & (df["TotalSpend"] > 0), "CryoSleep"] = False
    df.loc[cryo_missing & (df["TotalSpend"] == 0), "CryoSleep"] = True

    df["Age"] = df["Age"].fillna(df["Age"].median())
    df["VIP"] = df["VIP"].fillna(False)

    df["CryoSleep"] = df["CryoSleep"].astype(bool)
    df["VIP"] = df["VIP"].astype(bool)

    drop_cols = ["PassengerId", "Cabin", "Name", "LastName", "Group"]
    df = df.drop(columns=drop_cols)

    return df


train_fe = engineer_features(train)
test_fe = engineer_features(test)

y = train_fe["Transported"].astype(int)
X = train_fe.drop(columns=["Transported"])
X_test = test_fe

# %%
# One-hot encode categoricals, keeping train/test columns aligned.
CATEGORICAL_COLS = ["HomePlanet", "CryoSleep", "Destination", "VIP", "Deck", "Side"]

X = pd.get_dummies(X, columns=CATEGORICAL_COLS, dummy_na=True)
X_test = pd.get_dummies(X_test, columns=CATEGORICAL_COLS, dummy_na=True)
X, X_test = X.align(X_test, join="left", axis=1, fill_value=0)

# %%
model = HistGradientBoostingClassifier(
    max_iter=400,
    learning_rate=0.05,
    max_depth=6,
    l2_regularization=1.0,
    random_state=42,
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
print(f"CV accuracy: {scores.mean():.4f} +/- {scores.std():.4f}")

model.fit(X, y)

# %%
predictions = model.predict(X_test).astype(bool)

submission = pd.DataFrame({
    "PassengerId": test_passenger_ids,
    "Transported": predictions,
})
submission.to_csv("submission.csv", index=False)
print(submission.head())
print("Saved submission.csv")
