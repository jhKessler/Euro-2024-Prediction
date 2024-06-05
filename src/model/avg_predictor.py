import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pickle
import os
from loguru import logger


def linear_regression(years: list[int], verbose: bool = True):
    """Trains a linear regression model on the market value distance between two teams and the goals scored by the first team
    saves the model to data/models/linear_regression.pkl

    Args:
        years (list[int]): list of years to train the model on
        verbose (bool, optional): whether to plot the regression line. Defaults to True.
    """
    os.makedirs("data/models", exist_ok=True)
    data = None
    for year in years:
        if data is None:
            data = pd.read_csv(f"data/cleaned/{year}_train_games.csv", sep=";")
        else:
            data = pd.concat(
                [data, pd.read_csv(f"data/cleaned/{year}_train_games.csv", sep=";")]
            )
    data.drop(columns=["team2_goals"], inplace=True)

    X = data[["market_value_distance"]]
    y = data["team1_goals"]

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
        data["market_value_distance"],
        data["team1_goals"],
        color="blue",
        label="Actual goals",
    )
    plt.plot(
        data["market_value_distance"],
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
