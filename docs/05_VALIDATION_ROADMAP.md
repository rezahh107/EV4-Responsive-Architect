# 05 — Validation Roadmap

## Validation Principle

LLM-generated payloads are not considered structurally valid until a programmatic validator confirms required fields, enums, schema versions, duplicate IDs, forbidden fields, and payload identity.

## E2E-001 — Textual Fixture Contract Validation

```yaml
status_goal: contract_validation_only
requires:
  - sample_valid_payload
  - sample_invalid_payload
  - schema_validator_result
not_sufficient_for:
  - real_screenshot_validation
  - live_elementor_rendering
  - export_json_validation
  - production_readiness
```

## E2E-002 — Real Builder Responsive Test

```yaml
requires:
  - completed_main_EV4_handoff
  - desktop_baseline_frontend_screenshot
  - breakpoint_inventory_lock
  - tablet_frontend_screenshot
  - mobile_frontend_screenshot
  - builder_feedback_after_repair
  - responsive_final_audit
optional_recommended:
  - Elementor_export_JSON
  - Playwright_screenshot_set
  - visual_diff_report
```

## E2E-003 — Export / Import / JSON Roundtrip

```yaml
requires:
  - Build_Tree_Payload
  - generated_Elementor_JSON_skeleton
  - import_test_result
  - exported_Elementor_JSON_after_import
  - roundtrip_comparison
  - live_render_screenshot
  - Playwright_screenshot_set
```

## Release Boundary

No `production_ready`, `release_ready`, `live_render_validated`, `export_validated`, or `pixel_perfect` claim is allowed without matching evidence.
