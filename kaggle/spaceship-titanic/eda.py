# Spaceship Titanic - Exploratory Data Analysis
# Copy-paste this whole file into a Kaggle notebook cell (or split at the "# %%"
# markers into separate cells) and run.
#
# Column classification used below (the raw data has no explicit type labels,
# so these are assigned based on each column's meaning):
#   Binary   (exactly 2 categories, unordered): CryoSleep, VIP, Side
#   Nominal  (>2 categories, unordered):        HomePlanet, Destination
#   Ordinal  (>2 categories, natural order):     Deck (A is highest, T is lowest)
#   Target:                                      Transported
# Side and Deck are engineered from Cabin ("deck/num/side").

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

sns.set_theme(style="whitegrid")

INPUT_DIR = "/kaggle/input/spaceship-titanic"
train = pd.read_csv(f"{INPUT_DIR}/train.csv")

cabin_parts = train["Cabin"].str.split("/", expand=True)
train["Deck"] = cabin_parts[0]
train["Side"] = cabin_parts[2]

BINARY_COLS = ["CryoSleep", "VIP", "Side"]
NOMINAL_COLS = ["HomePlanet", "Destination"]
ORDINAL_COLS = ["Deck"]
TARGET_COL = "Transported"

# %%
# ---- Summary table: # missing, # original values, first/second/third value ----


def summarize_column(df, col, type_label):
    uniques = df[col].dropna().unique()
    first_three = list(uniques[:3]) + [np.nan] * max(0, 3 - len(uniques))
    return {
        "Column": col,
        "Type": type_label,
        "# Missing Value": df[col].isna().sum(),
        "# Original Value": len(uniques),
        "1st Original Value": first_three[0],
        "2nd Original Value": first_three[1],
        "3rd Original Value": first_three[2],
    }


summary_rows = (
    [summarize_column(train, c, "Binary") for c in BINARY_COLS]
    + [summarize_column(train, c, "Nominal") for c in NOMINAL_COLS]
    + [summarize_column(train, c, "Ordinal") for c in ORDINAL_COLS]
)
summary_table = pd.DataFrame(summary_rows)
display(summary_table)

# %%
# ---- Ordinal data: show every original value ----

for col in ORDINAL_COLS:
    values = sorted(train[col].dropna().unique())
    print(f"{col} ({len(values)} values): {values}")

# %%
# ---- Target distribution: Transported as 0/1 countplot ----

train["Transported_int"] = train[TARGET_COL].astype(int)

plt.figure(figsize=(5, 4))
ax = sns.countplot(x="Transported_int", data=train)
total = len(train)
for p in ax.patches:
    height = p.get_height()
    pct = height / total * 100
    ax.annotate(
        f"{height}\n({pct:.1f}%)",
        (p.get_x() + p.get_width() / 2, height),
        ha="center",
        va="bottom",
    )
ax.set_xlabel("Transported (0 = False, 1 = True)")
ax.set_ylabel("Count")
ax.set_title("Target Distribution")
plt.tight_layout()
plt.show()

# %%
# ---- Binary data: distribution by target, percentage on every bar ----
# Each subplot holds one binary column x Transported (2 x 2 = 4 bars).
# The percentage on each bar is the share of that bar's x-category
# (e.g. "of passengers with CryoSleep=True, X% were transported").

fig, axes = plt.subplots(1, len(BINARY_COLS), figsize=(5 * len(BINARY_COLS), 4))
if len(BINARY_COLS) == 1:
    axes = [axes]

for ax, col in zip(axes, BINARY_COLS):
    order = sorted(train[col].dropna().unique(), key=str)
    hue_order = [False, True]

    sns.countplot(x=col, hue=TARGET_COL, data=train, order=order, hue_order=hue_order, ax=ax)

    # totals per x-category, to turn each bar's height into a within-category %
    category_totals = train.groupby(col)[TARGET_COL].count().reindex(order)

    # each container is one hue level; its bars line up with `order`
    for container in ax.containers:
        for bar, category in zip(container, order):
            height = bar.get_height()
            if height == 0:
                continue
            pct = height / category_totals.loc[category] * 100
            ax.annotate(
                f"{int(height)}\n({pct:.1f}%)",
                (bar.get_x() + bar.get_width() / 2, height),
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_title(f"{col} by {TARGET_COL}")
    ax.set_ylabel("Count")

plt.tight_layout()
plt.show()
