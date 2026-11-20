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

## Raman / FTIR
- spectral_range
- wavenumber_unit
- intensity_or_transmittance_basis
- baseline_processing_visible
- peak_labels_visible
- laser_or_acquisition_conditions_visible (where applicable)

### Raman / FTIR cross-sample comparison (required when multiple samples or plotted series are present)
- spectrum_or_series_identity_and_sample_mapping
- technique_and_mode (Raman; FTIR; ATR; transmission; reflectance; other)
- spectral_range_and_wavenumber_calibration
- spectral_resolution_or_axis_tick_resolution
- laser_wavelength_power_and_acquisition_settings (Raman, where applicable)
- scan_count_or_accumulation_and_replicate_basis
- sample_state_and_preparation
- baseline_correction_and_smoothing
- normalization_method_and_reference_band
- vertical_offsets_or_independent_y_axis_scaling
- absorbance_transmittance_or_intensity_basis
- candidate_peak_positions_and_supported_uncertainty
- relative_peak_intensity_and_area_basis
- new_missing_split_merged_or_broadened_bands

For each comparison, record matched/mismatched/unknown dimensions before interpreting differences. Approximate visual peak positions may be reported only to the resolution supported by the original image and axis ticks. Compare apparent band area only when a defensible baseline/integration basis is available; otherwise report relative signal trends qualitatively. Distinguish band overlap or reduced visibility from true disappearance. Keep direct spectral observations, functional-group interpretations and mechanistic hypotheses separate.

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
