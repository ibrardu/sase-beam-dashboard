"""
Synthetic SASE X-ray beam diagnostic data generator.

Mimics the structure of European XFEL pulse-resolved diagnostics:
- XGM (X-ray Gas Monitor): per-pulse intensity
- Spectrometer: per-pulse photon energy spectrum (spiky SASE lineshape)

Organized as trains, each containing multiple pulses, matching the
train/pulse indexing scheme used at EuXFEL.
"""

import json
import numpy as np

rng = np.random.default_rng(42)

N_TRAINS = 60
PULSES_PER_TRAIN = 30
N_ENERGY_BINS = 200

# Nominal beam parameters (soft X-ray SASE3-like regime)
E0 = 1200.0          # central photon energy, eV
NOMINAL_BW_FWHM = 6.0  # eV, typical SASE relative bandwidth ~0.5%
GAIN_LENGTH_JITTER = 0.15  # fractional shot-to-shot energy jitter
N_SPIKES_MEAN = 6     # average number of SASE spectral spikes


def generate_pulse_spectrum(energy_axis, centroid, bandwidth, n_spikes):
    """Generate one stochastic SASE spectrum as a sum of narrow spikes
    under a broad Gaussian envelope, mimicking the self-amplified
    spontaneous emission process."""
    envelope = np.exp(-0.5 * ((energy_axis - centroid) / (bandwidth / 2.355)) ** 2)

    spectrum = np.zeros_like(energy_axis)
    spike_positions = rng.normal(centroid, bandwidth / 2.0, size=n_spikes)
    spike_widths = rng.uniform(0.15, 0.4, size=n_spikes)
    spike_heights = rng.exponential(1.0, size=n_spikes)

    for pos, width, height in zip(spike_positions, spike_widths, spike_heights):
        spectrum += height * np.exp(-0.5 * ((energy_axis - pos) / width) ** 2)

    spectrum *= envelope
    spectrum += rng.normal(0, 0.01, size=energy_axis.shape).clip(min=0)

    peak = spectrum.max()
    if peak > 0:
        spectrum /= peak
    return spectrum


def spectral_moments(energy_axis, spectrum):
    """Compute centroid and FWHM-equivalent bandwidth from a spectrum."""
    weights = spectrum / spectrum.sum()
    centroid = np.sum(energy_axis * weights)
    variance = np.sum(weights * (energy_axis - centroid) ** 2)
    sigma = np.sqrt(variance)
    fwhm = 2.355 * sigma
    return float(centroid), float(fwhm)


def main():
    energy_axis = np.linspace(E0 - 15, E0 + 15, N_ENERGY_BINS)

    trains = []
    for train_id in range(N_TRAINS):
        electron_charge_pc = float(rng.normal(250, 8))
        electron_energy_gev = float(rng.normal(14.0, 0.02))

        pulses = []
        for pulse_id in range(PULSES_PER_TRAIN):
            centroid_jitter = rng.normal(0, NOMINAL_BW_FWHM * GAIN_LENGTH_JITTER)
            centroid = E0 + centroid_jitter
            bandwidth = max(1.0, rng.normal(NOMINAL_BW_FWHM, 1.2))
            n_spikes = max(1, int(rng.poisson(N_SPIKES_MEAN)))

            spectrum = generate_pulse_spectrum(energy_axis, centroid, bandwidth, n_spikes)
            meas_centroid, meas_fwhm = spectral_moments(energy_axis, spectrum)

            xgm_intensity_uj = float(
                np.clip(rng.gamma(shape=6.0, scale=40.0), 5, None)
            )

            pulses.append({
                "pulse_id": pulse_id,
                "xgm_intensity_uj": round(xgm_intensity_uj, 2),
                "centroid_ev": round(meas_centroid, 3),
                "bandwidth_fwhm_ev": round(meas_fwhm, 3),
                "n_spikes": n_spikes,
                "spectrum": [round(v, 4) for v in spectrum],
            })

        trains.append({
            "train_id": train_id,
            "electron_charge_pc": round(electron_charge_pc, 2),
            "electron_energy_gev": round(electron_energy_gev, 4),
            "pulses": pulses,
        })

    dataset = {
        "meta": {
            "facility": "Synthetic (European XFEL-like)",
            "beamline": "SASE3 (soft X-ray, simulated)",
            "n_trains": N_TRAINS,
            "pulses_per_train": PULSES_PER_TRAIN,
            "energy_axis_ev": [round(v, 3) for v in energy_axis],
            "nominal_centroid_ev": E0,
            "nominal_bandwidth_fwhm_ev": NOMINAL_BW_FWHM,
        },
        "trains": trains,
    }

    with open("data/sase_data.json", "w") as f:
        json.dump(dataset, f)

    print(f"Generated {N_TRAINS} trains x {PULSES_PER_TRAIN} pulses = "
          f"{N_TRAINS * PULSES_PER_TRAIN} total pulses")


if __name__ == "__main__":
    main()