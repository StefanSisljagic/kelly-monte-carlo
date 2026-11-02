import random
import math
import os
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


def plot_kelly_growth_curve(win_probability):
    bet_fractions = [
        i / 1000
        for i in range(1, 101)
    ]

    log_growth_values = [
        expected_log_growth(
            fraction,
            win_probability
        )
        for fraction in bet_fractions
    ]

    optimal_fraction = kelly_fraction(
        win_probability
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        [f * 100 for f in bet_fractions],
        log_growth_values
    )

    plt.axhline(
        0,
        linestyle="--",
        alpha=.5
    )

    plt.axvline(
        optimal_fraction * 100,
        linestyle="--",
        alpha=.5,
        label=f"Kelly Fraction = {optimal_fraction:.1%}"
    )

    plt.xlabel("Bet Fraction (%)")
    plt.ylabel("Expected Log Growth per Bet")

    plt.title(
        "Expected Log Growth vs. Bet Size\n"
        f"{win_probability:.0%} Win Probability"
    )

    plt.legend()
    plt.grid(alpha=.25)
    plt.tight_layout()

    plt.savefig(
        "figures/kelly_growth_curve.png",
        dpi=300
    )

    plt.close()


def plot_estimation_error(results, estimated_probability):
    multipliers = sorted(
        set(
            result["kelly_multiplier"]
            for result in results
        )
    )

    plt.figure(figsize=(8, 5))

    for multiplier in multipliers:
        strategy_results = [
            result
            for result in results
            if result["kelly_multiplier"] == multiplier
        ]

        strategy_results.sort(
            key=lambda result: result["true_probability"]
        )

        probabilities = [
            result["true_probability"] * 100
            for result in strategy_results
        ]

        growth_values = [
            result["log_growth"]
            for result in strategy_results
        ]

        plt.plot(
            probabilities,
            growth_values,
            marker="o",
            label=f"{multiplier:.0%} Kelly"
        )

    plt.axhline(
        0,
        linestyle="--",
        alpha=.5
    )

    plt.axvline(
        estimated_probability * 100,
        linestyle="--",
        alpha=.5
    )

    plt.xlabel("True Win Probability (%)")
    plt.ylabel("Expected Log Growth per Bet")

    plt.title(
        "Kelly Betting Under Probability Estimation Error\n"
        f"Estimated Win Probability = {estimated_probability:.0%}"
    )

    plt.legend()
    plt.grid(alpha=.25)
    plt.tight_layout()

    plt.savefig(
        "figures/kelly_estimation_error.png",
        dpi=300
    )

    plt.close()


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
        "figures/kelly_drawdown_comparison.png",
        dpi=300
    )

    plt.close()


def main():
    random.seed(42)

    os.makedirs(
        "figures",
        exist_ok=True
    )

    starting_bankroll = 1000
    win_probability = .51
    estimated_probability = .51
    num_bets = 1000
    sessions = 5001

    kelly_multipliers = [
        .25,
        .50,
        1.00
    ]

    true_probabilities = [
        .49,
        .495,
        .50,
        .505,
        .51,
        .515,
        .52,
        .525,
        .53
    ]

    print("Kelly Criterion Analysis")
    print("-" * 60)

    full_kelly = kelly_fraction(
        win_probability
    )

    print(
        f"Win Probability: {win_probability:.2%}"
    )

    print(
        f"Full Kelly Fraction: {full_kelly:.2%}"
    )

    print()

    plot_kelly_growth_curve(
        win_probability
    )

    estimation_results = estimation_error_experiment(
        starting_bankroll,
        estimated_probability,
        true_probabilities,
        num_bets,
        sessions,
        kelly_multipliers
    )

    plot_estimation_error(
        estimation_results,
        estimated_probability
    )

    print("Probability Estimation Error")
    print("-" * 60)

    for multiplier in kelly_multipliers:
        bet_fraction = fractional_kelly(
            estimated_probability,
            multiplier
        )

        break_even = break_even_probability(
            bet_fraction
        )

        print(
            f"{multiplier:.0%} Kelly | "
            f"Bet: {bet_fraction:.2%} | "
            f"Break-Even True Probability: {break_even:.4%}"
        )

    print()
    print("Fractional Kelly Risk Analysis")
    print("-" * 60)

    drawdown_results = []

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

    print()
    print("Figures saved to figures/")


if __name__ == "__main__":
    main()