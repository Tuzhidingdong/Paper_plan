# Instrument visual checklist

For each field record one state: FOUND, NOT_SHOWN, NOT_LEGIBLE, UNCERTAIN or NOT_APPLICABLE. Keep figure_status separate from report_status.

## XRD
- two_theta_range
- x_axis_unit
- y_axis_unit_or_intensity_basis
- reference_phase_or_pdf_card
- peak_labels_or_reference_lines
- background_or_smoothing_visible
- stacked_curve_offsets_visible
- sample_labels_visible

## XPS
- binding_energy_axis_and_unit
- charge_calibration_reference
- c1s_reference_position
- raw_data_points_visible
- fit_envelope_visible
- component_peaks_visible
- background_model_visible
- sample_labels_visible

## Raman / FTIR / DRIFTS
- spectral_range
- wavenumber_unit
- intensity_or_transmittance_basis (intensity, absorbance or transmittance)
- baseline_processing_visible
- normalization_or_scaling_basis_visible
- peak_labels_and_sample_or_series_labels_visible
- spectral_resolution_and_acquisition_conditions_visible (where applicable)
- temperature, atmosphere, pH, timepoint and specimen state where reported

## CV / LSV
- potential_axis_and_unit
- reference_electrode
- scan_rate
- electrolyte_or_test_medium
- ir_compensation
- current_normalization_basis
- sample_labels_visible

## EIS
- plot_type
- frequency_range
- frequency_markers
- equivalent_circuit_shown
- fit_residual_or_quality
- electrode_area_or_normalization_basis

## Battery cycling / rate performance
- current_density_or_rate
- capacity_normalization_basis
- voltage_window
- cycle_number
- coulombic_efficiency
- loading_or_mass_basis
- temperature_and_electrolyte (where applicable)

## Microscopy
- scale_bar_and_unit
- magnification_or_scale
- sample_identity
- number_of_fields_or_images
- image_processing_or_contrast_note

Checklist fields are prompts for inspection, not mandatory values. NOT_SHOWN means absent from the image only. Search the PDF text separately before claiming NOT_REPORTED.

## Cross-image comparability (required when a claim combines image-derived Result Units)

Record each dimension per compared entity, including explicit UNKNOWN values when metadata are absent:
- `imaging_modality` — instrument/mode and acquisition configuration
- `magnification_or_pixel_size` — nominal magnification, pixel size or calibrated spatial scale
- `scale_bar_or_spatial_calibration` — scale-bar value/unit, calibration source and whether embedded scale bars are trustworthy
- `specimen_state_and_preparation` — before/after/treatment state, coating, sectioning, drying and preparation
- `image_processing_and_contrast` — contrast, filtering, thresholding, cropping and other processing
- `field_selection_and_sampling` — field selection, number of fields, replicate specimens and sampling basis

Do not infer particle-size or morphology changes from images acquired at different scales or modalities unless a valid scale-normalized comparison is available. Record the permissible observation (e.g. each image shows a morphology) separately from any prohibited between-image inference.


## Cross-sample vibrational-spectrum comparison (required when at least two samples or series are available)

After independent original-resolution inspection, prepare one joint comparison task for spectra of the same modality. Keep Raman, FTIR and DRIFTS distinct unless a scientifically justified cross-technique comparison is explicitly planned. Compare all available sample/timepoint spectra rather than stopping at the first pair; where one panel contains multiple legend series, treat those series as separate comparison units.

For each comparison record:
- sample/series identity and source Region/Panel/page;
- spectral modality and acquisition mode;
- spectral range and x-axis unit;
- intensity / absorbance / transmittance basis;
- baseline correction and normalization;
- instrument, spectral resolution and acquisition conditions;
- sample state/preparation and treatment/timepoint;
- curve offsets, stacking, vertical scaling and display processing.

Required scientific observations:
- band/peak positions as approximate ranges when readable, direction and bounded shift estimate (never false-precision point values);
- relative intensity changes only when the plotted basis, normalization, baseline and acquisition make them defensible;
- relative band-area trends only as qualitative/semi-quantitative visual observations, never numerical integration from pixels;
- bands that emerge, disappear, broaden, narrow, split, merge or remain stable;
- plausible functional-group and bond assignments, confidence, alternatives and chemical meaning;
- alternative explanations and independent measurements that could corroborate or contradict each interpretation.

A comparison is COMPARABLE only when all decision-relevant dimensions match or are not applicable. Unknown dimensions must remain UNKNOWN and limit the inference. Keep direct visual observations separate from assignments and mechanistic hypotheses. A new band is not, by itself, proof of a unique species or reaction pathway.
