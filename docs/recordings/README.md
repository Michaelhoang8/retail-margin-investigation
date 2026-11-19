# Power BI walkthrough

[Watch or download the MP4](walkthrough.mp4)

This is a **step walkthrough assembled from actual native Power BI screenshots**, captured on 2026-11-19. It is not a continuous screen recording or footage of a person manually authoring the report. Each original screenshot is held for six seconds with a caption. No chart values, UI states or cursor movements are fabricated. The screenshots show the final programmatically generated project loaded, refreshed and inspected in Power BI Desktop.

| Time | View | What it demonstrates |
|---|---|---|
| 00–06s | Overview | All 12,000 orders; contribution margin is a ratio of sums. |
| 06–12s | 2025 filter | 6,002 orders; 26.3% contribution margin. Compare with SQL 01. |
| 12–18s | Discount diagnosis | Inspect category/tier differences and the order-volume denominators. |
| 18–24s | Relationships | Products and customers filter the orders fact through many-to-one relationships. |
| 24–30s | Loaded orders | 12,000 clean order rows loaded in Power BI Desktop. |

The unmodified PNGs are in [screenshots](../screenshots). [Capture manifest](captures.json) records their SHA-256 hashes and descriptions. Rebuild the video using `python scripts/build_walkthrough.py` from the repository root, with FFmpeg on PATH. The video is silent; captions identify each step. GitHub may require downloading the MP4 to play it.
