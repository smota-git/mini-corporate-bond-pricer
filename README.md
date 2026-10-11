# Mini Corporate Bond Pricer (Bond Pricing, Yield and Sensitivities)

A compact Python project illustrating the basic mechanics of fixed-income pricing and credit-risk-sensitive bond valuation.

The model uses a simple fixed-rate coupon bond and connects:

- contractual cash flows,
- present-value discounting,
- risk-free rate,
- credit spread,
- yield,
- market price,
- implied yield,
- numerical root finding,
- and DV01.

The project is intentionally simplified so that the relationships between these quantities remain transparent.

## Model setup

The bond is defined by:

- **face value** `$F$` — principal repaid at maturity,
- **coupon rate** `c`,
- **maturity** `T`,
- **risk-free rate** `r_f`,
- **credit spread** `s`.

The annual coupon is

$$C = cF.$$

In this simplified model, the discount yield is

$$y = r_f + s.$$

The bond's calculated model price is the present value of all contractual future cash flows:

$$P_{model} = \sum_{t=1}^{T-1} \frac{C}{(1+y)^t} + \frac{C+F}{(1+y)^T}.$$

The project assumes annual coupons, a constant risk-free rate, a constant credit spread and a flat yield across maturities. It therefore does **not** represent a full market yield curve or term structure.

## Terminology

The distinction between the following quantities is important.

### Face value

The **face value** (or par value) is the principal amount repaid by the issuer at maturity.

It is not the same thing as the bond's current price.

### Model price / present value

The **model price** is the present value of the bond's future contractual cash flows discounted at the selected yield.

In this project:

$$P_{model} = PV(\text{future cash flows}).$$

The terms **model price**, **calculated bond price** and **present value (PV)** therefore refer to the same quantity.

### Market price

The **market price** is treated as an externally observed or hypothetically specified price.

It is an input to the inverse pricing problem and does not have to equal the model price calculated from the initially assumed yield.

### Model yield

The model yield is defined here as

$$y = r_f + s.$$

This is a deliberate simplification.

### Implied yield

The **implied yield** is the yield that makes the present value of the contractual cash flows equal to a specified market price:

$$P_{model}(y) = P_{market}.$$

For a coupon bond, this yield is generally solved numerically. The script uses Brent's root-finding method.

## Main calculations

### Base bond price

The function `bond_price()` calculates the model price from:

- face value,
- coupon rate,
- maturity,
- risk-free rate,
- credit spread.

Because the model uses

$$y = r_f + s,$$

an increase in either the risk-free rate or the credit spread increases the required yield and reduces the present value of the same future cash flows.

### Implied yield from market price

The function `yield_from_price()` solves

$$P_{model}(y) - P_{market} = 0.$$

The numerical solution is obtained using `scipy.optimize.brentq`.

This is the inverse of the usual pricing problem:

- **pricing problem:** yield → price,
- **inverse pricing problem:** market price → implied yield.

### Yield sensitivity and DV01

The script estimates price sensitivity numerically using a small yield increase:

$$\frac{\partial P}{\partial y} \approx \frac{P(y+\Delta y)-P(y)}{\Delta y}.$$

For

$$\Delta y = 1\text{ bp} = 0.0001,$$

the script converts this sensitivity into DV01:

$$DV01 \approx - \frac{\partial P}{\partial y} \times 0.0001.$$

DV01 therefore represents the approximate **absolute change in bond price caused by a 1 basis point increase in yield**.

## Figures

The four figures deliberately show different relationships. In each case, it is useful to distinguish which quantity is varied, which quantity is calculated, and which quantities are held constant.

### 1. Model price (PV) vs credit spread

**x-axis:** credit spread  
**y-axis:** model price / present value

The risk-free rate, coupon rate, face value and maturity are held constant.

Only the credit spread changes.

Because

$$y = r_f + s,$$

a wider spread increases the discount yield and lowers the present value of the same contractual cash flows:

$$s \uparrow \Rightarrow y \uparrow \Rightarrow P_{model} \downarrow.$$

This figure therefore shows the sensitivity of the calculated bond value to credit-spread changes.

It is **not** a generic yield-vs-price plot, even though yield changes indirectly because spread is one component of the model yield.

### 2. Model price (PV) vs maturity

**x-axis:** maturity  
**y-axis:** model price / present value

The graph compares three separate coupon-rate scenarios:

- 4% coupon,
- 5% coupon,
- 6% coupon.

The model yield is held constant at

$$3\% + 2\% = 5\%.$$

This gives three characteristic cases:

- if coupon rate < yield, the bond trades below par,
- if coupon rate = yield, the bond is at par,
- if coupon rate > yield, the bond trades above par.

As maturity increases, the effect becomes more pronounced.

The graph therefore does **not** show coupon rate as a function of maturity. It shows **bond price as a function of maturity for three fixed coupon-rate scenarios**.

It also does not represent a real yield curve, because the same yield is assumed for all maturities.

### 3. Implied yield vs hypothetical market price

**x-axis:** hypothetical market price  
**y-axis:** implied yield

The bond itself is kept fixed:

- same face value,
- same coupon rate,
- same maturity.

The script then considers a range of hypothetical market prices and solves a separate inverse pricing problem for each price:

$$P_{model}(y) = P_{market}.$$

The resulting curve shows that a higher market price for the same contractual cash flows implies a lower yield.

This figure should therefore be read as

$$P_{market} \longrightarrow y_{implied},$$

not as a direct model of how market prices are formed.

### 4. DV01 vs maturity

**x-axis:** maturity  
**y-axis:** DV01

For each maturity from 1 to 20 years, the script creates a bond with the same face value, coupon rate and base yield and calculates its DV01.

The graph therefore shows

$$T \longrightarrow DV01.$$

Longer-maturity bonds are generally more sensitive to small yield changes because a larger share of their cash flows lies further in the future.

The figure is not the price change of one single bond over time. It compares the 1 bp yield sensitivity of otherwise similar bonds with different maturities.

## Interpretation of price, yield and risk

A lower bond price implies a higher yield **for the same contractual cash flows**.

In a real corporate-bond market, a lower price and higher yield may arise because:

- general risk-free interest rates have risen,
- the issuer's credit spread has widened,
- or both.

The current model keeps these effects simple and transparent by representing yield as the sum of a risk-free rate and a credit spread.

The model does **not** yet explicitly model:

- default probability,
- recovery rate,
- survival probabilities,
- a full yield curve,
- liquidity effects,
- stochastic interest rates.

These are natural extensions for a more advanced version of the project.

## Project structure

`bond.py` contains:

- bond pricing from discounted cash flows,
- scenario calculations,
- implied-yield estimation using Brent's method,
- finite-difference yield sensitivity,
- DV01 calculation,
- and four diagnostic plots.

## Requirements

```text
numpy
matplotlib
scipy
```

## How to run

```bash
pip install numpy matplotlib scipy
python bond.py
```

## Summary

The project connects the following concepts in one workflow:

$$\text{cash flows} \rightarrow \text{discounting} \rightarrow \text{model yield} \rightarrow \text{present value} \rightarrow \text{market price} \rightarrow \text{implied yield} \rightarrow \text{sensitivity / DV01}.$$

The main purpose is not to reproduce a production-grade fixed-income system, but to make the relationships between price, yield, spread and sensitivity explicit and numerically testable.
