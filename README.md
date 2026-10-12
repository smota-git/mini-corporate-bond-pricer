# Corporate Bond Pricing and Risk Analytics

A compact Python project for exploring fixed-rate corporate bond pricing, implied yield, interest-rate sensitivity and credit-spread sensitivity.

The model connects contractual cash flows, present-value discounting, risk-free rate and credit spread, market price and implied yield, DV01, modified duration, convexity, Macaulay duration and scenario analysis.

The model is intentionally simplified so that these relationships remain transparent.

## 1. Model and inputs

The bond is described by:

- **face value** `F`,
- **coupon rate** `c`,
- **maturity** `T`,
- **risk-free rate** `r_f`,
- **credit spread** `s`,
- **market price** `P_market`.

The annual coupon is:

$$C = c \cdot F$$

The simplified model yield is:

$$y = r_f + s$$

The model assumes annual coupons and one flat yield for all cash flows.

At startup, the user can either keep the default parameters or enter custom values. Pressing Enter at an individual prompt keeps the displayed default.

Default values:

```text
Face value:       100
Coupon rate:        5 %
Maturity:            5 years
Risk-free rate:      3 %
Credit spread:       2 %
Market price:       95
```

## 2. Pricing, present value and implied yield

For a fixed-rate bond, the investor receives a coupon in every year and the face value at maturity.

For example:

```text
Face value = 100
Coupon rate = 5 %
Maturity = 5 years
```

produces the contractual cash flows:

```text
5, 5, 5, 5, 105
```

The **model price** is the present value of these cash flows:

$$P_{model} = \sum_{t=1}^{T} \frac{CF_t}{(1+y)^t}$$

In this project, **model price**, **calculated bond price** and **present value (PV)** refer to the same calculated quantity.

The **market price** is different: it is an externally supplied or hypothetical observed price.

The model can therefore be used in two directions:

```text
yield -> model price
market price -> implied yield
```

The implied yield is the yield that satisfies:

$$P_{model}(y) = P_{market}$$

or equivalently:

$$P_{model}(y) - P_{market} = 0$$

The script solves this numerically using Brent's method from `scipy.optimize.brentq`.

## 3. Risk measures: practical hierarchy and meaning

The risk measures in the script are related, but they do not have equal practical importance.

A useful hierarchy is:

1. **DV01** — direct absolute price sensitivity to a 1 bp yield move.
2. **Modified duration** — relative first-order sensitivity of price to yield.
3. **Convexity** — second-order correction describing curvature of the price-yield relationship.
4. **Macaulay duration** — present-value-weighted timing of cash flows; historically the original duration concept and the basis from which modified duration is obtained.

### DV01

DV01 measures the approximate absolute price change caused by a 1 basis point increase in yield.

One basis point is:

$$1\text{ bp} = 0.0001$$

Using modified duration:

$$DV01 \approx P \cdot D_{mod} \cdot 0.0001$$

The script reports DV01 in **price units**, not in percent.

For a bond priced around 100, a DV01 of `0.05` means that a +1 bp increase in yield changes the price by approximately `0.05` price units.

DV01 could also be obtained directly by bumping the yield by 1 bp and repricing the bond. The duration formula is a local analytical approximation of the same sensitivity.

### Modified duration

Modified duration is the relative first-order sensitivity of price to yield:

$$D_{mod} = -\frac{1}{P}\frac{dP}{dy}$$

For annual compounding it is related to Macaulay duration by:

$$D_{mod} = \frac{D_{Mac}}{1+y}$$

For a small yield move:

$$\frac{\Delta P}{P} \approx -D_{mod}\Delta y$$

So modified duration is best read as a **percentage price-sensitivity measure**, not as an intuitive time measure.

Example:

```text
Modified duration = 8.8
Yield change       = +1.0 percentage point
```

gives approximately:

```text
Relative price change ≈ -8.8 %
```

### Convexity

Duration gives only the local slope of the price-yield curve. Bond price is not linear in yield, so larger yield moves require a curvature correction.

Convexity measures the second-order curvature:

$$Convexity = \frac{1}{P}\frac{d^2P}{dy^2}$$

For annual discrete compounding:

$$Convexity = \frac{1}{P}\sum_{t=1}^{T}\frac{CF_t \cdot t(t+1)}{(1+y)^{t+2}}$$

The duration-plus-convexity approximation is:

$$\frac{\Delta P}{P} \approx -D_{mod}\Delta y + \frac{1}{2}Convexity(\Delta y)^2$$

This improves the linear duration approximation when the yield move is not extremely small.

### Macaulay duration

Macaulay duration is:

$$D_{Mac} = \frac{\sum_{t=1}^{T} t \cdot PV(CF_t)}{P}$$

It is the **present-value-weighted average time of the bond's cash flows** — effectively a time center of gravity of the discounted payments.

Historically, this was the original duration concept: a better description of the economic "length" of a coupon bond than maturity alone.

A coupon bond with maturity 15 years can therefore have Macaulay duration well below 15 years because part of its present value is received earlier through coupons.

For a zero-coupon bond:

$$D_{Mac} = T$$

In this project, Macaulay duration is mainly important for two reasons:

- it explains the timing structure behind interest-rate sensitivity,
- and it provides the starting point for modified duration.

It is less direct as a practical risk measure than DV01 or modified duration, but it remains useful conceptually and in applications such as duration matching / immunization.

## 4. Credit-spread sensitivity: CS01

CS01 measures the price effect of a 1 bp widening of the credit spread.

The script calculates it by direct repricing:

$$CS01 = P(s) - P(s + 0.0001)$$

Like DV01, CS01 is expressed in **price units**, not in percent.

Because this simplified model assumes:

$$y = r_f + s$$

a +1 bp move in total yield and a +1 bp move in credit spread have almost the same effect on price. Therefore DV01 and CS01 are very close in this version.

This is a feature of the simplified model, not a general property of real corporate bonds.

## 5. Exact repricing, approximation and scenario analysis

The script compares a full +100 bp repricing with the second-order duration-plus-convexity approximation.

For example:

```text
Exact price change:     -5.1148
Duration+convexity:     -5.0995
```

For one simple bond, exact repricing is trivial. The approximation is useful because the same idea scales to larger portfolios and many risk scenarios, where repeated full repricing can become more expensive.

The script also evaluates:

```text
Base
Risk-free +100 bp
Spread +100 bp
Both +100 bp
Spread -50 bp
```

and prints the resulting model price for each scenario.

Because the current model uses:

$$y = r_f + s$$

the scenarios `Risk-free +100 bp` and `Spread +100 bp` produce the same model price when everything else is unchanged.

## 6. Figures

The script creates four diagnostic plots.

### Model price vs credit spread

**x-axis:** credit spread  
**y-axis:** model bond price

The risk-free rate, coupon rate, face value and maturity are fixed.

A wider spread increases the model yield and lowers present value:

$$s \uparrow \Rightarrow y \uparrow \Rightarrow P_{model} \downarrow$$

### Model price vs maturity

**x-axis:** maturity  
**y-axis:** model bond price

The graph compares three coupon-rate scenarios:

```text
selected coupon rate - 1 percentage point
selected coupon rate
selected coupon rate + 1 percentage point
```

The model yield is held fixed.

This graph shows **price as a function of maturity for three fixed coupon-rate scenarios**. It is not a yield curve.

### Implied yield vs hypothetical market price

**x-axis:** hypothetical market price  
**y-axis:** implied yield

Face value, coupon rate and maturity are fixed.

For each hypothetical market price, the script solves:

$$P_{model}(y) = P_{market}$$

A higher market price for the same contractual cash flows implies a lower yield.

The vertical dashed line marks the market price entered by the user.

### DV01 vs maturity

**x-axis:** maturity  
**y-axis:** DV01

For maturities from 1 to 20 years, the script calculates DV01 using the selected face value, coupon rate and base yield.

The graph shows how 1 bp yield sensitivity changes with maturity.

## 7. Assumptions and limitations

The model deliberately assumes:

- annual coupons,
- constant risk-free rate,
- constant credit spread,
- one flat yield for all maturities,
- no explicit yield curve,
- no default probability,
- no recovery rate,
- no survival probabilities,
- no liquidity premium,
- no stochastic interest-rate model.

The credit spread therefore acts only as an additive component of the discount yield.

A natural next extension would be an explicit default/recovery model based on survival probabilities or hazard rates.

## 8. Requirements and run

Requirements:

```text
numpy
matplotlib
scipy
```

Install with:

```bash
pip install numpy matplotlib scipy
```

Run:

```bash
python corporate_bond_pricer_v2.py
```

The conceptual flow is:

```text
contractual cash flows
-> model yield
-> present value / model price
-> market price
-> implied yield
-> DV01 / modified duration
-> convexity
-> Macaulay duration
-> CS01
-> scenario analysis
```

The main goal is to make the relationship between bond valuation and local risk measures explicit while keeping the model simple enough to inspect and understand.
