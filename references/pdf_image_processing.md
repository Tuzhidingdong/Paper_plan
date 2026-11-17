# PDF and image processing

Use PyMuPDF to inventory pages, extract text/image blocks and render requested PDF-coordinate regions. Preserve the source PDF unchanged.

Automatic extraction covers embedded raster image blocks. Vector-only plots may be drawing primitives rather than images; flag them for manual/agent region definition.

Store raw PDF-coordinate and normalized BBoxes. Reject malformed, zero-area and out-of-page boxes. Record page rotation and coordinate convention.

First-pass visual payload contains only the figure/panel crop. External captions and narrative are withheld. Image-internal ticks, labels and legends remain visible.

Contact sheets are thumbnails for triage only. They are not suitable for peak positions, exact values, subtle line discrimination or quantitative measurements.

Use source PDF SHA-256, page, normalized BBox, pixel SHA-256 and extractor version to create an anchor. Perceptual hashes are similarity hints only.
