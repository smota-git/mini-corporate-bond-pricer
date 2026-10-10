import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq


# ============================================================
# Mini-project: Bond pricing, yield and sensitivities
#
# Cíl:
# - spočítat cenu fixně úročeného dluhopisu z jeho cash flows
# - ukázat vliv risk-free rate a credit spreadu na cenu
# - numericky dopočítat implied yield z tržní ceny
# - ukázat citlivost ceny na malou změnu yieldu
#
# Zjednodušení:
# - roční kupóny
# - konstantní risk-free rate
# - konstantní credit spread
# - yield = risk-free rate + credit spread
# - nepoužíváme plnou yield curve / term structure
# ============================================================


# ----------------------------
# Parametry dluhopisu
# ----------------------------

FACE_VALUE = 100.0          # jistina vyplacená při splatnosti
COUPON_RATE = 0.05          # roční kupón = 5 % z face value
MATURITY = 5                # splatnost v letech

RISK_FREE_RATE = 0.03
CREDIT_SPREAD = 0.02


# ----------------------------
# Model price (present value) from risk-free rate and credit spread
# ----------------------------
#
# Celkový požadovaný yield zjednodušeně modelujeme jako:
#
# yield = risk-free rate + credit spread
#
# Cena dluhopisu je současná hodnota:
# - všech budoucích kupónů
# - splacené jistiny při maturity
#

def bond_price(
    face_value,
    coupon_rate,
    maturity,
    risk_free_rate,
    credit_spread
):

    yield_rate = risk_free_rate + credit_spread
    coupon = face_value * coupon_rate
    price = 0.0

    for t in range(1, maturity + 1):

        cash_flow = coupon

        if t == maturity:
            cash_flow += face_value

        present_value = cash_flow / (1 + yield_rate) ** t
        price += present_value

    return price


# ----------------------------
# Model price (present value) directly from a specified yield
# ----------------------------
#
# Tato funkce je užitečná pro:
# - výpočet sensitivity
# - numerické hledání implied yieldu
#

def bond_price_from_yield(
    face_value,
    coupon_rate,
    maturity,
    yield_rate
):

    coupon = face_value * coupon_rate
    price = 0.0

    for t in range(1, maturity + 1):

        cash_flow = coupon

        if t == maturity:
            cash_flow += face_value

        price += cash_flow / (1 + yield_rate) ** t

    return price


# ----------------------------
# Implied yield z tržní ceny
# ----------------------------
#
# Známe market price a hledáme yield takový, aby:
#
# calculated bond price = market price
#
# Tedy hledáme kořen rovnice:
#
# bond_price(yield) - market_price = 0
#
# Použijeme Brentovu metodu.
#

def yield_from_price(
    market_price,
    face_value,
    coupon_rate,
    maturity
):

    def price_difference(yield_rate):

        return (
            bond_price_from_yield(
                face_value,
                coupon_rate,
                maturity,
                yield_rate
            )
            - market_price
        )

    yield_rate = brentq(
        price_difference,
        -0.9,
        1.0
    )

    return yield_rate


# ============================================================
# 1. Základní scénář
# ============================================================

price_base = bond_price(
    FACE_VALUE,
    COUPON_RATE,
    MATURITY,
    RISK_FREE_RATE,
    CREDIT_SPREAD
)

print("Base bond price:", price_base)


# ============================================================
# 2. Jednoduché scénáře
#
# Porovnáváme:
# - růst risk-free rate
# - růst credit spreadu
#
# V obou případech roste požadovaný yield,
# takže cena dluhopisu klesá.
# ============================================================

price_higher_rates = bond_price(
    FACE_VALUE,
    COUPON_RATE,
    MATURITY,
    0.04,
    CREDIT_SPREAD
)

price_higher_spread = bond_price(
    FACE_VALUE,
    COUPON_RATE,
    MATURITY,
    RISK_FREE_RATE,
    0.04
)

print("\nHigher risk-free rate:", price_higher_rates)
print("Higher credit spread:", price_higher_spread)


# ============================================================
# 3. Spread sensitivity
#
# Odhadujeme změnu ceny při zvýšení credit spreadu o 1 bp.
#
# 1 bp = 0.0001
#
# Finite difference:
#
# dP/dSpread ≈ [P(spread + h) - P(spread)] / h
# ============================================================

ONE_BP = 0.0001

price_spread_up = bond_price(
    FACE_VALUE,
    COUPON_RATE,
    MATURITY,
    RISK_FREE_RATE,
    CREDIT_SPREAD + ONE_BP
)

spread_sensitivity = (
    price_spread_up - price_base
) / ONE_BP

print("\nSpread sensitivity:")
print(spread_sensitivity)


# ============================================================
# 4. Model price (PV) vs credit spread
#
# Risk-free rate držíme konstantní.
# Vyšší credit spread -> vyšší yield -> nižší bond price.
# ============================================================

spreads = np.linspace(0.0, 0.08, 100)

prices = []

for spread in spreads:

    price = bond_price(
        FACE_VALUE,
        COUPON_RATE,
        MATURITY,
        RISK_FREE_RATE,
        spread
    )

    prices.append(price)


# ============================================================
# 5. Model price (PV) vs maturity
#
# POZOR:
# Tento graf předpokládá konstantní yield pro všechny maturity.
# Nejde tedy o reálnou yield curve.
#
# Při coupon rate = yield je bond přesně at par:
#
# price = face value
#
# pro každou maturity.
# ============================================================

maturities_long = range(1, 31)

mprices1 = []
mprices2 = []
mprices3 = []

for mat in maturities_long:

    price1 = bond_price(
        FACE_VALUE,
        0.04,
        mat,
        RISK_FREE_RATE,
        CREDIT_SPREAD
    )

    price2 = bond_price(
        FACE_VALUE,
        0.05,
        mat,
        RISK_FREE_RATE,
        CREDIT_SPREAD
    )

    price3 = bond_price(
        FACE_VALUE,
        0.06,
        mat,
        RISK_FREE_RATE,
        CREDIT_SPREAD
    )

    mprices1.append(price1)
    mprices2.append(price2)
    mprices3.append(price3)

# ============================================================
# 6. Implied yield z jedné zadané market price
# ============================================================

market_price = 95.0

market_yield = yield_from_price(
    market_price,
    FACE_VALUE,
    COUPON_RATE,
    MATURITY
)

print("\nMarket price:", market_price)
print("Implied yield:", market_yield)


# ============================================================
# 7. Numerická sensitivity ceny na yield
#
# Odhad:
#
# dP/dy ≈ [P(y + dy) - P(y)] / dy
#
# Jelikož vyšší yield snižuje cenu,
# očekáváme zápornou hodnotu.
# ============================================================

dy = 0.0001

price_y = bond_price_from_yield(
    FACE_VALUE,
    COUPON_RATE,
    MATURITY,
    market_yield
)

price_y_up = bond_price_from_yield(
    FACE_VALUE,
    COUPON_RATE,
    MATURITY,
    market_yield + dy
)

yield_sensitivity = (
    price_y_up - price_y
) / dy

print("\nPrice sensitivity to yield:")
print(yield_sensitivity)


# ============================================================
# 8. Implied yield vs hypothetical market price
#
# Pro různé market prices numericky dopočítáme yield.
#
# Vyšší market price -> nižší implied yield.
# ============================================================

market_prices = np.linspace(70, 130, 100)
implied_yields = []

for market_price in market_prices:

    y = yield_from_price(
        market_price,
        FACE_VALUE,
        COUPON_RATE,
        MATURITY
    )

    implied_yields.append(y)


# ============================================================
# 9. DV01 vs maturity
#
# Pro každou maturity spočítáme numericky dP/dy.
#
# Při delší maturity je cena obecně citlivější
# na změnu yieldu, protože vzdálenější cash flows
# jsou silněji ovlivněny diskontní sazbou.
#
# Opět předpokládáme konstantní yield,
# nikoli plnou term structure.
# ============================================================

maturities_sensitivity = range(1, 21)
yield_sensitivities = []

base_yield = RISK_FREE_RATE + CREDIT_SPREAD

for maturity in maturities_sensitivity:

    price_y = bond_price_from_yield(
        FACE_VALUE,
        COUPON_RATE,
        maturity,
        base_yield
    )

    price_y_up = bond_price_from_yield(
        FACE_VALUE,
        COUPON_RATE,
        maturity,
        base_yield + dy
    )

    sensitivity = (price_y_up - price_y) / dy

    dv01 = -sensitivity * 0.0001

    yield_sensitivities.append(dv01)


# ============================================================
# Grafy
# ============================================================

plt.figure(figsize=(10, 14))

# 1. Model price (PV) vs credit spread
plt.subplot(4, 1, 1)

plt.plot(
    spreads * 100,
    prices
)

plt.xlabel("Credit spread [%]")
plt.ylabel("Model price (PV)")
plt.title("Model price (PV) vs credit spread")
plt.grid()


# 2. Model price (PV) vs maturity
plt.subplot(4, 1, 2)

plt.plot(
    maturities_long,
    mprices1,
    label="Coupon 4%"
)

plt.plot(
    maturities_long,
    mprices2,
    label="Coupon 5%"
)

plt.plot(
    maturities_long,
    mprices3,
    label="Coupon 6%"
)

plt.xlabel("Maturity [years]")
plt.ylabel("Model price (PV)")
plt.title("Model price (PV) vs maturity")
plt.legend()
plt.grid()


# 3. Implied yield vs hypothetical market price
plt.subplot(4, 1, 3)

plt.plot(
    market_prices,
    np.array(implied_yields) * 100
)

plt.xlabel("Hypothetical market price")
plt.ylabel("Implied yield [%]")
plt.title("Implied yield vs hypothetical market price")
plt.grid()


# 4. DV01 vs maturity
plt.subplot(4, 1, 4)

plt.plot(
    maturities_sensitivity,
    yield_sensitivities
)

plt.xlabel("Maturity [years]")
plt.ylabel("DV01")
plt.title("DV01 vs maturity")
plt.grid()


plt.subplots_adjust(hspace=0.8)
plt.show()



