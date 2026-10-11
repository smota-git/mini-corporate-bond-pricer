# Corporate Bond Pricing and Risk Analytics

A compact Python project for exploring fixed-rate corporate bond pricing, implied yield, interest-rate sensitivity and credit-spread sensitivity.

The project extends a basic bond pricer with:

- optional interactive user input,
- model price / present value calculation,
- implied yield from a specified market price,
- Macaulay duration,
- modified duration,
- convexity,
- DV01,
- CS01,
- duration-plus-convexity approximation,
- scenario analysis,
- and four diagnostic plots.

The model is intentionally simplified so that the relationships between cash flows, yield, price and risk measures remain transparent.

## 1. Model inputs

The bond is defined by:

- **face value** `F`,
- **coupon rate** `c`,
- **maturity** `T`,
- **risk-free rate** `r_f`,
- **credit spread** `s`,
- **market price** `P_market`.

The annual coupon is:

$$C = cF$$

The simplified model yield is:

$$y = r_f + s$$

The script uses annual coupons and one flat yield for all cash flows.

## 2. Interactive input

At startup, the script asks:

```text
Use default parameters? [Y/n]:
```

Pressing Enter or entering `Y` keeps the default parameters.

Entering `n` allows the user to specify:

```text
Face value
Coupon rate
Maturity
Risk-free rate
Credit spread
Market price
```

Pressing Enter at an individual prompt keeps the displayed default value.

Default values are:

```text
Face value:       100
Coupon rate:        5 %
Maturity:            5 years
Risk-free rate:      3 %
Credit spread:       2 %
Market price:       95
```

## 3. Cash flows and model price

For a fixed-rate bond, the investor receives the coupon in every year and the face value at maturity.

For example, with:

```text
Face value = 100
Coupon rate = 5 %
Maturity = 5 years
```

the contractual cash flows are:

```text
5, 5, 5, 5, 105
```

The model price is the present value of these future cash flows:

$$P_{model} = \sum_{t=1}^{T} \frac{CF_t}{(1+y)^t}$$

In this project:

- **model price**,
- **calculated bond price**,
- and **present value (PV)**

refer to the same calculated quantity.

The **market price** is different: it is an externally supplied or hypothetical observed price used in the inverse pricing problem.

## 4. Implied yield

Given a market price, the script solves for the yield that makes the model price equal to that market price:

$$P_{model}(y) = P_{market}$$

Equivalently, it finds the root of:

$$P_{model}(y) - P_{market} = 0$$

The numerical solution is obtained with Brent's method using `scipy.optimize.brentq`.

This creates two opposite calculations:

```text
yield -> model price
market price -> implied yield
```

## 5. Macaulay duration

Macaulay duration is the present-value-weighted average time of the bond's cash flows:

$$D_{Mac} = \frac{\sum_{t=1}^{T} t \cdot PV(CF_t)}{P}$$

The weights are the individual present values divided by the total bond price.

It can be interpreted as the **time center of gravity of the discounted cash flows**.

This is not a replacement for the maturity itself. A 15-year coupon bond can have a Macaulay duration well below 15 years because part of its present value is received earlier through coupons.

For a zero-coupon bond, all value is received at maturity, so:

$$D_{Mac} = T$$

Macaulay duration is also the starting point for the bond's first-order yield sensitivity.

## 6. Modified duration

Modified duration converts Macaulay duration into a direct relative price sensitivity to yield:

$$D_{mod} = \frac{D_{Mac}}{1+y}$$

For annual compounding, this is equivalent to:

$$D_{mod} = -\frac{1}{P}\frac{dP}{dy}$$

Therefore, for a small yield change:

$$\frac{\Delta P}{P} \approx -D_{mod}\Delta y$$

Example interpretation:

```text
Modified duration = 8.8
Yield change       = +1.0 percentage point
```

gives approximately:

```text
Relative price change ≈ -8.8 %
```

for the first-order approximation.

## 7. DV01

DV01 measures the approximate absolute price change associated with a 1 basis point increase in yield.

One basis point is:

$$1\text{ bp} = 0.0001$$

Using modified duration:

$$DV01 \approx P \cdot D_{mod} \cdot 0.0001$$

The script reports DV01 as a **price-unit amount**, not as a percentage.

For a bond quoted around 100, a DV01 of `0.05` means that a +1 bp yield move changes the bond price by approximately `0.05` price units.

DV01 could also be computed directly by bumping the yield by 1 bp and repricing the bond. The duration formula is a local analytical approximation of the same sensitivity.

## 8. CS01

CS01 measures the price effect of a 1 bp widening of the credit spread.

The script calculates it directly by repricing:

$$CS01 = P(s) - P(s + 0.0001)$$

Like DV01, CS01 is reported in **price units**, not in percent.

In this simplified model:

$$y = r_f + s$$

so a +1 bp move in total yield and a +1 bp move in credit spread have almost the same pricing effect. Therefore DV01 and CS01 are usually very close in this version of the project.

In a more realistic credit model, interest-rate risk and credit-spread risk would not be identical.

## 9. Convexity

Duration captures the first derivative of price with respect to yield. Bond price, however, is not a linear function of yield.

Convexity measures the second-order curvature:

$$Convexity = \frac{1}{P}\frac{d^2P}{dy^2}$$

For annual discrete compounding, the script calculates:

$$Convexity = \frac{1}{P}\sum_{t=1}^{T}\frac{CF_t\,t(t+1)}{(1+y)^{t+2}}$$

The factor `t(t+1)` appears because convexity comes from the second derivative of the bond pricing function.

The combined duration-and-convexity approximation is:

$$\frac{\Delta P}{P} \approx -D_{mod}\Delta y + \frac{1}{2}Convexity(\Delta y)^2$$

This improves the linear duration approximation when yield changes are not extremely small.

## 10. Exact repricing vs duration + convexity

The script applies a +100 bp yield shock:

$$\Delta y = 0.01$$

It then compares:

- **Exact price change** — full repricing at the shocked yield,
- **Duration + convexity** — second-order approximation.

Example output:

```text
Exact price change:     -5.1148
Duration+convexity:     -5.0995
```

The comparison is not only mathematical decoration.

It illustrates the practical idea behind risk measures: instead of fully repricing an instrument for every small scenario, local sensitivities can provide a fast approximation.

For one simple bond, exact repricing is trivial. For larger portfolios and many scenarios, sensitivity-based approximations become more useful.

## 11. Scenario analysis

The script evaluates five scenarios:

```text
Base
Risk-free +100 bp
Spread +100 bp
Both +100 bp
Spread -50 bp
```

For each scenario it prints:

- risk-free rate,
- credit spread,
- resulting model price.

Because the current model uses:

$$y = r_f + s$$

the scenarios:

```text
Risk-free +100 bp
Spread +100 bp
```

produce the same bond price when all other inputs are unchanged.

This is a consequence of the simplified model, not a general property of real corporate bonds.

## 12. Console output

A typical run reports:

```text
--- Corporate Bond Pricing and Risk Analytics ---
Face value
Coupon rate
Maturity
Risk-free rate
Credit spread
Model yield
Model bond price
Observed market price
Implied market yield

--- Risk measures at model yield ---
Macaulay duration
Modified duration
Convexity
DV01
CS01

--- +100 bp yield shock ---
Exact price change
Duration+convexity

--- Scenario analysis ---
scenario rates and resulting prices
```

The distinction between **model bond price** and **observed market price** is important:

- `model bond price` is calculated from the assumed model yield,
- `observed market price` is supplied by the user,
- `implied market yield` is the yield required to reproduce that market price.

## 13. Figures

The script creates four plots.

### 13.1 Bond price vs credit spread

**x-axis:** credit spread  
**y-axis:** model bond price

The risk-free rate, coupon rate, face value and maturity are fixed.

Only the credit spread changes.

Since:

$$y = r_f + s$$

a wider credit spread increases the discount yield and lowers the present value of the bond.

### 13.2 Bond price vs maturity

**x-axis:** maturity  
**y-axis:** model bond price

The graph compares three coupon-rate scenarios:

```text
selected coupon rate - 1 percentage point
selected coupon rate
selected coupon rate + 1 percentage point
```

The model yield is fixed.

This graph shows **price as a function of maturity for three fixed coupon-rate scenarios**. It is not a yield curve.

### 13.3 Implied yield vs market price

**x-axis:** hypothetical market price  
**y-axis:** implied yield

Face value, coupon rate and maturity are fixed.

For every hypothetical market price, the script numerically solves:

$$P_{model}(y) = P_{market}$$

A higher price for the same contractual cash flows implies a lower yield.

The vertical dashed line marks the market price entered by the user.

### 13.4 DV01 vs maturity

**x-axis:** maturity  
**y-axis:** DV01

For maturities from 1 to 20 years, the script calculates DV01 using the selected face value, coupon rate and base yield.

The graph therefore shows how 1 bp yield sensitivity changes with maturity.

## 14. Important simplifications

The current version deliberately assumes:

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

## 15. Requirements

```text
numpy
matplotlib
scipy
```

Install with:

```bash
pip install numpy matplotlib scipy
```

## 16. Run

```bash
python corporate_bond_pricer_v2.py
```

## 17. Conceptual structure

The project connects the following chain:

```text
contractual cash flows
-> discounting
-> model yield
-> present value / model price
-> market price
-> implied yield
-> Macaulay duration
-> modified duration
-> DV01 / CS01
-> convexity
-> scenario analysis
```

The purpose is to make the relationships between bond valuation and local risk measures explicit while keeping the model simple enough to inspect and understand.
