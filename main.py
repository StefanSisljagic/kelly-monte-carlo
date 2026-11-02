import random
import math
import matplotlib.pyplot as plt


def simulate_bet(bankroll, bet_size, win_probability):
    if random.random() < win_probability:
        return bankroll + bet_size

    return bankroll - bet_size


def simulate_proportional_session(
    starting_bankroll,
    bet_fraction,
    win_probability,
    num_bets
):
    bankroll = starting_bankroll

    for _ in range(num_bets):
        bet_size = bankroll * bet_fraction

        bankroll = simulate_bet(
            bankroll,
            bet_size,
            win_probability
        )

    return bankroll


def simulate_session_with_drawdown(
    starting_bankroll,
    bet_fraction,
    win_probability,
    num_bets
):
    bankroll = starting_bankroll
    peak_bankroll = starting_bankroll
    max_drawdown = 0

    for _ in range(num_bets):
        bet_size = bankroll * bet_fraction

        bankroll = simulate_bet(
            bankroll,
            bet_size,
            win_probability
        )

        peak_bankroll = max(peak_bankroll, bankroll)

        drawdown = (
            peak_bankroll - bankroll
        ) / peak_bankroll

        max_drawdown = max(max_drawdown, drawdown)

    return bankroll, max_drawdown


def kelly_fraction(win_probability):
    return 2 * win_probability - 1


def fractional_kelly(estimated_probability, kelly_multiplier):
    return (
        kelly_fraction(estimated_probability)
        * kelly_multiplier
    )


def expected_log_growth(bet_fraction, win_probability):
    p = win_probability
    f = bet_fraction

    return (
        p * math.log(1 + f)
        + (1 - p) * math.log(1 - f)
    )


def break_even_probability(bet_fraction):
    numerator = -math.log(1 - bet_fraction)

    denominator = (
        math.log(1 + bet_fraction)
        - math.log(1 - bet_fraction)
    )

    return numerator / denominator


def estimate_proportional_results(
    starting_bankroll,
    bet_fraction,
    win_probability,
    num_bets,
    sessions
):
    final_bankrolls = []

    for _ in range(sessions):
        final_bankroll = simulate_proportional_session(
            starting_bankroll,
            bet_fraction,
            win_probability,
            num_bets
        )

        final_bankrolls.append(final_bankroll)

    mean_bankroll = sum(final_bankrolls) / sessions

    final_bankrolls.sort()
    median_bankroll = final_bankrolls[sessions // 2]

    return mean_bankroll, median_bankroll


def estimate_drawdown(
    starting_bankroll,
    bet_fraction,
    win_probability,
    num_bets,
    sessions
):
    final_bankrolls = []
    drawdowns = []

    for _ in range(sessions):
        final_bankroll, max_drawdown = simulate_session_with_drawdown(
            starting_bankroll,
            bet_fraction,
            win_probability,
            num_bets
        )

        final_bankrolls.append(final_bankroll)
        drawdowns.append(max_drawdown)

    final_bankrolls.sort()
    drawdowns.sort()

    median_final = final_bankrolls[sessions // 2]
    median_drawdown = drawdowns[sessions // 2]

    return median_final, median_drawdown


def estimation_error_experiment(
    starting_bankroll,
    estimated_probability,
    true_probabilities,
    num_bets,
    sessions,
    kelly_multipliers
):
    results = []

    for true_probability in true_probabilities:
        for multiplier in kelly_multipliers:

            bet_fraction = fractional_kelly(
                estimated_probability,
                multiplier
            )

            mean, median = estimate_proportional_results(
                starting_bankroll,
                bet_fraction,
                true_probability,
                num_bets,
                sessions
            )

            log_growth = expected_log_growth(
                bet_fraction,
                true_probability
            )

            results.append({
                "true_probability": true_probability,
                "kelly_multiplier": multiplier,
                "bet_fraction": bet_fraction,
                "mean": mean,
                "median": median,
                "log_growth": log_growth
            })

    return results


def plot_drawdown_comparison(results):
    strategies = []
    drawdowns = []

    for result in results:
        strategies.append(
            f"{result['multiplier']:.0%} Kelly"
        )

        drawdowns.append(
            result["median_drawdown"] * 100
        )

    plt.figure(figsize=(8, 5))

    plt.bar(
        strategies,
        drawdowns
    )

    plt.xlabel("Betting Strategy")
    plt.ylabel("Median Maximum Drawdown (%)")

    plt.title(
        "Risk Increases with Kelly Bet Sizing\n"
        "51% True Win Probability, 1,000 Bets"
    )

    plt.grid(
        axis="y",
        alpha=.25
    )

    plt.tight_layout()

    plt.savefig(
        "kelly_drawdown_comparison.png",
        dpi=300
    )

    plt.show()


def main():

    starting_bankroll = 1000
    win_probability = .51
    num_bets = 1000
    sessions = 5001

    kelly_multipliers = [
        .25,
        .50,
        1.00
    ]

    drawdown_results = []

    print("Fractional Kelly Risk Analysis")
    print("-" * 60)

    for multiplier in kelly_multipliers:

        bet_fraction = fractional_kelly(
            win_probability,
            multiplier
        )

        median_final, median_drawdown = estimate_drawdown(
            starting_bankroll,
            bet_fraction,
            win_probability,
            num_bets,
            sessions
        )

        drawdown_results.append({
            "multiplier": multiplier,
            "bet_fraction": bet_fraction,
            "median_final": median_final,
            "median_drawdown": median_drawdown
        })

        print(
            f"{multiplier:.0%} Kelly | "
            f"Bet: {bet_fraction:.2%} | "
            f"Median Final: ${median_final:.2f} | "
            f"Median Max Drawdown: {median_drawdown:.2%}"
        )

    plot_drawdown_comparison(
        drawdown_results
    )


if __name__ == "__main__":
    main()