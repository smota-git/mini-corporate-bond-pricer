from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq


# ============================================================
# Corporate Bond Pricing and Risk Analytics
#
# Features:
# - fixed-rate bond pricing from cash flows
# - optional interactive input with sensible defaults
# - risk-free rate + credit spread decomposition
# - implied yield from market price
# - Macaulay duration
# - modified duration
# - convexity
# - DV01 and CS01
# - scenario analysis and diagnostic plots
#
# Simplifications:
# - annual coupons
# - constant risk-free rate
# - constant credit spread
# - yield = risk-free rate + credit spread
# - flat yield curve / no term structure
# - no explicit default/recovery model yet
# ============================================================


@dataclass
class BondParams:
    face_value: float = 100.0
    coupon_rate: float = 0.05
    maturity: int = 5
    risk_free_rate: float = 0.03
    credit_spread: float = 0.02
    market_price: float = 95.0


# ============================================================
# Input helpers
# ============================================================

def _read_float(prompt: str, default: float) -> float:
    raw = input(f"{prompt} [{default}]: ").strip()
    if raw == "":
        return default
    return float(raw)


def _read_percent(prompt: str, default_decimal: float) -> float:
    default_percent = 100.0 * default_decimal
    raw = input(f"{prompt} [%] [{default_percent:g}]: ").strip()
    if raw == "":
        return default_decimal
    return float(raw) / 100.0


def _read_int(prompt: str, default: int) -> int:
    raw = input(f"{prompt} [{default}]: ").strip()
    if raw == "":
        return default
    value = int(raw)
    if value <= 0:
        raise ValueError("Maturity must be a positive integer.")
    return value


def get_user_inputs(defaults: BondParams | None = None) -> BondParams:
    """Ask whether to use defaults; blank entries keep displayed defaults."""
    p = defaults or BondParams()

    use_defaults = input("Use default parameters? [Y/n]: ").strip().lower()
    if use_defaults in ("", "y", "yes"):
        return p

    print("\nPress Enter at any prompt to keep the value shown in brackets.\n")

    return BondParams(
        face_value=_read_float("Face value", p.face_value),
        coupon_rate=_read_percent("Coupon rate", p.coupon_rate),
        maturity=_read_int("Maturity [years]", p.maturity),
        risk_free_rate=_read_percent("Risk-free rate", p.risk_free_rate),
        credit_spread=_read_percent("Credit spread", p.credit_spread),
        market_price=_read_float("Market price", p.market_price),
    )


# ============================================================
# Core pricing functions
# ============================================================

def cash_flows(face_value: float, coupon_rate: float, maturity: int) -> np.ndarray:
    """Return annual contractual cash flows."""
    coupon = face_value * coupon_rate
    flows = np.full(maturity, coupon, dtype=float)
    flows[-1] += face_value
    return flows


def bond_price_from_yield(
    face_value: float,
    coupon_rate: float,
    maturity: int,
    yield_rate: float,
) -> float:
    """Present value of all contractual cash flows at one flat yield."""
    flows = cash_flows(face_value, coupon_rate, maturity)
    times = np.arange(1, maturity + 1, dtype=float)
    discount = (1.0 + yield_rate) ** times
    return float(np.sum(flows / discount))


def bond_price(
    face_value: float,
    coupon_rate: float,
    maturity: int,
    risk_free_rate: float,
    credit_spread: float,
) -> float:
    """Simplified corporate bond price with yield = risk-free + credit spread."""
    yield_rate = risk_free_rate + credit_spread
    return bond_price_from_yield(face_value, coupon_rate, maturity, yield_rate)


def yield_from_price(
    market_price: float,
    face_value: float,
    coupon_rate: float,
    maturity: int,
) -> float:
    """Solve for the yield that reproduces the observed market price."""

    def price_difference(yield_rate: float) -> float:
        return (
            bond_price_from_yield(face_value, coupon_rate, maturity, yield_rate)
            - market_price
        )

    return float(brentq(price_difference, -0.90, 5.0))


# ============================================================
# Interest-rate and spread risk analytics
# ============================================================

def macaulay_duration(
    face_value: float,
    coupon_rate: float,
    maturity: int,
    yield_rate: float,
) -> float:
    """Weighted average time to receive discounted cash flows."""
    flows = cash_flows(face_value, coupon_rate, maturity)
    times = np.arange(1, maturity + 1, dtype=float)
    pv = flows / (1.0 + yield_rate) ** times
    price = np.sum(pv)
    return float(np.sum(times * pv) / price)


def modified_duration(
    face_value: float,
    coupon_rate: float,
    maturity: int,
    yield_rate: float,
) -> float:
    """Approximate percentage price sensitivity to a small yield change."""
    mac = macaulay_duration(face_value, coupon_rate, maturity, yield_rate)
    return mac / (1.0 + yield_rate)


def convexity(
    face_value: float,
    coupon_rate: float,
    maturity: int,
    yield_rate: float,
) -> float:
    """Annual-pay bond convexity under discrete compounding."""
    flows = cash_flows(face_value, coupon_rate, maturity)
    times = np.arange(1, maturity + 1, dtype=float)
    price = bond_price_from_yield(face_value, coupon_rate, maturity, yield_rate)

    numerator = np.sum(
        flows * times * (times + 1.0)
        / (1.0 + yield_rate) ** (times + 2.0)
    )
    return float(numerator / price)


def dv01(
    face_value: float,
    coupon_rate: float,
    maturity: int,
    yield_rate: float,
) -> float:
    """Approximate price loss for a +1 bp parallel yield increase."""
    price = bond_price_from_yield(face_value, coupon_rate, maturity, yield_rate)
    mod_dur = modified_duration(face_value, coupon_rate, maturity, yield_rate)
    return float(price * mod_dur * 0.0001)


def cs01(
    face_value: float,
    coupon_rate: float,
    maturity: int,
    risk_free_rate: float,
    credit_spread: float,
) -> float:
    """Price loss for a +1 bp widening of credit spread."""
    h = 0.0001
    p0 = bond_price(
        face_value, coupon_rate, maturity, risk_free_rate, credit_spread
    )
    p1 = bond_price(
        face_value, coupon_rate, maturity, risk_free_rate, credit_spread + h
    )
    return float(p0 - p1)


def duration_convexity_price_change(
    price: float,
    modified_duration_value: float,
    convexity_value: float,
    delta_yield: float,
) -> float:
    """Approximate absolute price change using duration + convexity."""
    relative_change = (
        -modified_duration_value * delta_yield
        + 0.5 * convexity_value * delta_yield**2
    )
    return float(price * relative_change)


# ============================================================
# Scenario analysis
# ============================================================

def scenario_table(p: BondParams) -> list[tuple[str, float, float, float]]:
    """Return scenario name, risk-free rate, spread and resulting price."""
    scenarios = [
        ("Base", p.risk_free_rate, p.credit_spread),
        ("Risk-free +100 bp", p.risk_free_rate + 0.01, p.credit_spread),
        ("Spread +100 bp", p.risk_free_rate, p.credit_spread + 0.01),
        ("Both +100 bp", p.risk_free_rate + 0.01, p.credit_spread + 0.01),
        ("Spread -50 bp", p.risk_free_rate, max(0.0, p.credit_spread - 0.005)),
    ]

    result = []
    for name, rf, spread in scenarios:
        price = bond_price(
            p.face_value,
            p.coupon_rate,
            p.maturity,
            rf,
            spread,
        )
        result.append((name, rf, spread, price))

    return result


# ============================================================
# Plots
# ============================================================

def plot_results(p: BondParams) -> None:
    base_yield = p.risk_free_rate + p.credit_spread

    spreads = np.linspace(0.0, 0.08, 100)
    prices = [
        bond_price(
            p.face_value,
            p.coupon_rate,
            p.maturity,
            p.risk_free_rate,
            spread,
        )
        for spread in spreads
    ]

    maturities_long = range(1, 31)
    coupon_rates = [
        max(0.0, p.coupon_rate - 0.01),
        p.coupon_rate,
        p.coupon_rate + 0.01,
    ]

    maturity_prices = []
    for coupon_rate in coupon_rates:
        maturity_prices.append([
            bond_price(
                p.face_value,
                coupon_rate,
                mat,
                p.risk_free_rate,
                p.credit_spread,
            )
            for mat in maturities_long
        ])

    market_prices = np.linspace(
        max(1.0, 0.70 * p.face_value),
        1.30 * p.face_value,
        100,
    )
    implied_yields = [
        yield_from_price(
            market_price,
            p.face_value,
            p.coupon_rate,
            p.maturity,
        )
        for market_price in market_prices
    ]

    maturities_sensitivity = range(1, 21)
    dv01_values = [
        dv01(
            p.face_value,
            p.coupon_rate,
            maturity,
            base_yield,
        )
        for maturity in maturities_sensitivity
    ]

    plt.figure(figsize=(10, 14))

    plt.subplot(4, 1, 1)
    plt.plot(spreads * 100, prices)
    plt.xlabel("Credit spread [%]")
    plt.ylabel("Bond price")
    plt.title("Bond price vs credit spread")
    plt.grid()

    plt.subplot(4, 1, 2)
    for coupon_rate, values in zip(coupon_rates, maturity_prices):
        plt.plot(
            maturities_long,
            values,
            label=f"Coupon {100 * coupon_rate:.1f}%",
        )
    plt.xlabel("Maturity [years]")
    plt.ylabel("Bond price")
    plt.title("Bond price vs maturity")
    plt.legend()
    plt.grid()

    plt.subplot(4, 1, 3)
    plt.plot(market_prices, np.array(implied_yields) * 100)
    plt.axvline(p.market_price, linestyle="--", linewidth=1)
    plt.xlabel("Market price")
    plt.ylabel("Implied yield [%]")
    plt.title("Implied yield vs market price")
    plt.grid()

    plt.subplot(4, 1, 4)
    plt.plot(maturities_sensitivity, dv01_values)
    plt.xlabel("Maturity [years]")
    plt.ylabel("DV01")
    plt.title("DV01 vs maturity")
    plt.grid()

    plt.subplots_adjust(hspace=0.8)
    plt.show()


# ============================================================
# Main
# ============================================================

def main() -> None:
    p = get_user_inputs()

    base_yield = p.risk_free_rate + p.credit_spread
    model_price = bond_price(
        p.face_value,
        p.coupon_rate,
        p.maturity,
        p.risk_free_rate,
        p.credit_spread,
    )

    implied_yield = yield_from_price(
        p.market_price,
        p.face_value,
        p.coupon_rate,
        p.maturity,
    )

    mac_dur = macaulay_duration(
        p.face_value, p.coupon_rate, p.maturity, base_yield
    )
    mod_dur = modified_duration(
        p.face_value, p.coupon_rate, p.maturity, base_yield
    )
    conv = convexity(
        p.face_value, p.coupon_rate, p.maturity, base_yield
    )
    dv01_value = dv01(
        p.face_value, p.coupon_rate, p.maturity, base_yield
    )
    cs01_value = cs01(
        p.face_value,
        p.coupon_rate,
        p.maturity,
        p.risk_free_rate,
        p.credit_spread,
    )

    delta_y = 0.01
    exact_up_100 = bond_price_from_yield(
        p.face_value,
        p.coupon_rate,
        p.maturity,
        base_yield + delta_y,
    )
    exact_change = exact_up_100 - model_price
    approx_change = duration_convexity_price_change(
        model_price,
        mod_dur,
        conv,
        delta_y,
    )

    print("\n--- Corporate Bond Pricing and Risk Analytics ---")
    print(f"Face value:             {p.face_value:.2f}")
    print(f"Coupon rate:            {100 * p.coupon_rate:.2f} %")
    print(f"Maturity:               {p.maturity} years")
    print(f"Risk-free rate:         {100 * p.risk_free_rate:.2f} %")
    print(f"Credit spread:          {100 * p.credit_spread:.2f} %")
    print(f"Model yield:            {100 * base_yield:.2f} %")
    print(f"Model bond price:       {model_price:.4f}")
    print(f"Observed market price:  {p.market_price:.4f}")
    print(f"Implied market yield:   {100 * implied_yield:.4f} %")

    print("\n--- Risk measures at model yield ---")
    print(f"Macaulay duration:      {mac_dur:.4f} years")
    print(f"Modified duration:      {mod_dur:.4f}")
    print(f"Convexity:              {conv:.4f}")
    print(f"DV01:                   {dv01_value:.6f}")
    print(f"CS01:                   {cs01_value:.6f}")

    print("\n--- +100 bp yield shock ---")
    print(f"Exact price change:     {exact_change:.4f}")
    print(f"Duration+convexity:     {approx_change:.4f}")

    print("\n--- Scenario analysis ---")
    print(f"{'Scenario':<22}{'Risk-free':>12}{'Spread':>12}{'Price':>12}")
    for name, rf, spread, price in scenario_table(p):
        print(
            f"{name:<22}"
            f"{100 * rf:>11.2f}%"
            f"{100 * spread:>11.2f}%"
            f"{price:>12.4f}"
        )

    plot_results(p)


if __name__ == "__main__":
    main()
