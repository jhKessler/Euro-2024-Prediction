import pickle
from loguru import logger
from matplotlib import pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression


def train_linear_regression(years: list[int], verbose: bool = True):
    data = None
    for year in years:
        logger.info(f"Loading data for year {year}")
        if data is None:
            data = pd.read_csv(f"data/cleaned/{year}_games.csv", sep=";")
        else:
            data = pd.concat([data, pd.read_csv(f"data/cleaned/{year}_games.csv", sep=";")])

    X = data[["team1_market_value_distance"]].values
    y = data["team1_goals"].values

    model = LinearRegression()
    model.fit(X, y)

    with open("data/models/linear_regression.pkl", "wb") as f:
        pickle.dump(model, f)

    logger.info("Model saved to data/models/linear_regression.pkl")

    if not verbose:
        logger.info("Skipping plotting as verbose is set to False")
        return

    logger.info("Plotting regression line")
    data["predicted_goals"] = model.predict(X)

    # Plotting
    plt.figure(figsize=(8, 4))
    plt.scatter(
        data["team1_market_value_distance"],
        data["team1_goals"],
        color="blue",
        label="Actual goals",
    )
    plt.plot(
        data["team1_market_value_distance"],
        data["predicted_goals"],
        color="red",
        label="Regression Line",
    )
    plt.xlabel("Market Value Distance")
    plt.ylabel("Goals Scored")
    plt.title("Linear Regression on Team Goals vs. Market Value Distance")
    plt.legend()
    plt.grid(True)
    plt.show()
