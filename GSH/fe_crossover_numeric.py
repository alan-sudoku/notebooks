import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Fe/Al τ* Crossover — OQ-GSH.8 Numeric Instance

    Populates check 7's crossover formula with real supply-chain data for the
    Fe (incumbent) vs. Al geometric substitute comparison.

    **Source mapping:**
    - `Σ_cap_s` = extraction exergy of Fe + deferred Axiom II recovery cost
    - `Σ_cap_g` = extraction exergy of Al geometric substitute
    - `r_s` = ongoing entropy rate of Fe supply chain (corrosion-dominated)
    - `r_g` = ongoing maintenance entropy rate of Al substitute (≈ 0, self-passivating)

    **Data sources:** Szargut (1988) standard chemical exergies · NIST WebBook · ISO 9223
    """)
    return


@app.cell
def _():
    T0 = 298.15          # K  — standard dead-state reference temperature
    R  = 8.314           # J/(mol·K)

    SZARGUT_B_CH = {
        "Fe": 376_400,
        "Al": 888_400,
        "C":  410_260,
        "Si": 854_600,
        "H":   236_100,
        "O":    3_970,
    }

    M = {
        "Fe": 55.845,
        "Al": 26.982,
        "C":  12.011,
        "O":  15.999,
    }

    DG_OXIDATION_FE = -742_200
    DG_OXIDATION_FE_PER_MOL = DG_OXIDATION_FE / 2
    DG_REDUCTION_FE2O3 = +742_200
    DG_REDUCTION_FE_PER_MOL = DG_REDUCTION_FE2O3 / 2

    RHO_FE = 7_874.0
    RHO_AL = 2_700.0
    SECONDS_PER_YEAR = 365.25 * 24 * 3600
    return (
        DG_OXIDATION_FE_PER_MOL,
        DG_REDUCTION_FE_PER_MOL,
        M,
        RHO_AL,
        RHO_FE,
        SECONDS_PER_YEAR,
        SZARGUT_B_CH,
        T0,
    )


@app.cell
def _(mo):
    mo.md("""
    ## Parameters
    """)
    return


@app.cell
def _(mo):
    fe_mass_slider = mo.ui.slider(100, 10_000, step=100, value=1_000, label="Fe structure mass (kg)")
    area_slider    = mo.ui.slider(1, 200, step=1, value=10, label="Exposed surface area (m²)")
    corr_slider    = mo.ui.slider(1, 200, step=1, value=25, label="Corrosion rate (μm/yr)")
    equal_vol      = mo.ui.checkbox(value=True, label="Equal-volume substitution (uncheck for equal-mass)")
    mo.vstack([fe_mass_slider, area_slider, corr_slider, equal_vol])
    return area_slider, corr_slider, equal_vol, fe_mass_slider


@app.cell
def _(
    DG_OXIDATION_FE_PER_MOL,
    DG_REDUCTION_FE_PER_MOL,
    M,
    RHO_AL,
    RHO_FE,
    SECONDS_PER_YEAR,
    SZARGUT_B_CH,
    T0,
    area_slider,
    corr_slider,
    equal_vol,
    fe_mass_slider,
):
    fe_mass_kg     = fe_mass_slider.value
    surface_area   = area_slider.value
    corr_um_yr     = corr_slider.value
    al_mass_kg     = fe_mass_kg * (RHO_AL / RHO_FE) if equal_vol.value else fe_mass_kg

    def sigma_cap_per_kg(element):
        return (SZARGUT_B_CH[element] / (M[element] / 1000)) / T0

    def sigma_rec_fe_per_kg():
        return (abs(DG_REDUCTION_FE_PER_MOL) / (M["Fe"] / 1000)) / T0

    def r_corr_to_entropy_rate(corr_rate_m_per_s, surface_area_m2):
        molar_flux     = (corr_rate_m_per_s * RHO_FE * 1000) / M["Fe"]
        power_per_area = molar_flux * abs(DG_OXIDATION_FE_PER_MOL)
        return (power_per_area * surface_area_m2) / T0

    corr_m_s      = (corr_um_yr * 1e-6) / SECONDS_PER_YEAR
    sigma_cap_fe  = sigma_cap_per_kg("Fe") * fe_mass_kg
    sigma_rec_fe  = sigma_rec_fe_per_kg()  * fe_mass_kg
    sigma_cap_s   = sigma_cap_fe + sigma_rec_fe
    sigma_cap_g   = sigma_cap_per_kg("Al") * al_mass_kg
    r_s           = r_corr_to_entropy_rate(corr_m_s, surface_area)
    r_g           = 0.0

    numerator     = sigma_cap_g - sigma_cap_s
    denominator   = r_s - r_g
    tau_star_s    = numerator / denominator if abs(denominator) > 1e-30 else float("inf")
    tau_star_yr   = tau_star_s / SECONDS_PER_YEAR

    regime = (
        "Favourable substitution at τ > τ*" if tau_star_yr > 0 else
        "Geometry unconditionally cheaper — no crossover needed" if (tau_star_yr < 0 and numerator < 0) else
        "Geometry unconditionally more expensive — no crossover exists"
    )
    return (
        al_mass_kg,
        fe_mass_kg,
        numerator,
        r_g,
        r_s,
        regime,
        sigma_cap_fe,
        sigma_cap_g,
        sigma_cap_s,
        sigma_rec_fe,
        tau_star_yr,
    )


@app.cell
def _(
    al_mass_kg,
    fe_mass_kg,
    mo,
    r_g,
    r_s,
    regime,
    sigma_cap_fe,
    sigma_cap_g,
    sigma_cap_s,
    sigma_rec_fe,
    tau_star_yr,
):
    mo.md(f"""
    ## Results

    | Parameter | Value |
    |---|---|
    | Fe structure mass | {fe_mass_kg:.0f} kg |
    | Al substitute mass | {al_mass_kg:.0f} kg |
    | Σ_cap_s (Fe extraction) | {sigma_cap_fe:.1f} J/K |
    | Σ_cap_s (Fe recycling) | {sigma_rec_fe:.1f} J/K |
    | **Σ_cap_s total** | **{sigma_cap_s:.1f} J/K** |
    | **Σ_cap_g (Al extraction)** | **{sigma_cap_g:.1f} J/K** |
    | r_s (Fe corrosion entropy rate) | {r_s:.4e} W/K |
    | r_g (Al maintenance) | {r_g:.4e} W/K |
    | **τ*** | **{tau_star_yr:.1f} years** |
    | Regime | {regime} |
    """)
    return


@app.cell
def _(mo, numerator, r_g, r_s, sigma_cap_g, sigma_cap_s, tau_star_yr):
    import matplotlib.pyplot as plt
    import numpy as np

    tau_max = max(tau_star_yr * 2.5, 200) if tau_star_yr > 0 else 500
    tau = np.linspace(0, tau_max, 500)

    SECONDS_PER_YEAR_plot = 365.25 * 24 * 3600
    sigma_s = sigma_cap_s + r_s * tau * SECONDS_PER_YEAR_plot
    sigma_g = sigma_cap_g + r_g * tau * SECONDS_PER_YEAR_plot

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(tau, sigma_s, label="Σ_s — Fe supply chain", color="#c0392b")
    ax.plot(tau, sigma_g, label="Σ_g — Al geometric substitute", color="#2980b9")

    if tau_star_yr > 0:
        crossover_y = sigma_cap_s + r_s * tau_star_yr * SECONDS_PER_YEAR_plot
        ax.axvline(tau_star_yr, color="#7f8c8d", linestyle="--", linewidth=1)
        ax.plot(tau_star_yr, crossover_y, "o", color="#7f8c8d", markersize=6)
        ax.annotate(
            f"τ* = {tau_star_yr:.0f} yr",
            xy=(tau_star_yr, crossover_y),
            xytext=(tau_star_yr + tau_max * 0.04, crossover_y),
            fontsize=9, color="#7f8c8d",
            va="center",
        )
        # shade regions
        ax.axvspan(0, tau_star_yr, alpha=0.05, color="#c0392b", label="Fe cheaper")
        ax.axvspan(tau_star_yr, tau_max, alpha=0.05, color="#2980b9", label="Al cheaper")
    elif tau_star_yr < 0 and numerator < 0:
        ax.text(
            0.5, 0.92, "Al substitute unconditionally cheaper — no crossover",
            transform=ax.transAxes, ha="center", fontsize=9,
            color="#2980b9", style="italic",
        )
    else:
        ax.text(
            0.5, 0.92, "Fe unconditionally cheaper — no crossover exists",
            transform=ax.transAxes, ha="center", fontsize=9,
            color="#c0392b", style="italic",
        )

    ax.set_xlabel("Deployment lifetime τ (years)")
    ax.set_ylabel("Cumulative entropy (J/K)")
    ax.set_title("Fe vs. Al geometric substitute — entropy crossover")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    mo.mpl.interactive(fig)
    return


if __name__ == "__main__":
    app.run()
