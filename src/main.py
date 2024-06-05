from argparse import ArgumentParser
from gather import gather_tournament_data
from clean import format_training_data
from model import avg_predictor


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--years", type=int, nargs="+", help="Years of the tournaments to gather or format data for (must be valid euro year, e.g. 2020, 2024, etc.)"
    )
    parser.add_argument(
        "--gather", action='store_true', help="Gather data from wikipedia and transfermarkt"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Number of seconds to wait between requests, use at own caution to avoid overloading the transfermarkt servers, I like to fly under the radar with a very slow rate since I don't do many requests, but you can probably go faster if you want to get the data faster, but be careful not to get banned.",
    )
    parser.add_argument(
        "--continue-previous",
        action="store_true",
        help="Continue gathering data for a year that was previously started",
    )
    parser.add_argument(
        "--clean", action='store_true', help="Format gathered data into the format used by the model"
    )
    parser.add_argument(
        "--train", action='store_true', help="Train the model on the formatted data"
    )

    args = parser.parse_args()

    if args.gather:
        for year in args.years:
            gather_tournament_data(year, args.timeout, args.continue_previous)

    if args.clean:
        for year in args.years:
            format_training_data(year)

    if args.train:
        # train linear regression model
        avg_predictor.linear_regression(args.years)
    
    args = parser.parse_args()