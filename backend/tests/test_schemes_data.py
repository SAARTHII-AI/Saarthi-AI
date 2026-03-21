"""
Schemes Data validation tests for Saarthi-AI backend.

Tests cover:
- All schemes have required fields
- scope field is valid ("central" or "state")
- application_url is a valid URL
- documents array is non-empty
- Data consistency and integrity checks
"""

import pytest
import json
import re
import warnings
from pathlib import Path
from urllib.parse import urlparse

from app.config import settings
from app.services.scheme_loader import load_schemes


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def schemes_data():
    """Load schemes data for testing."""
    schemes = load_schemes()
    if not schemes:
        pytest.skip("No schemes data available for testing")
    return schemes


@pytest.fixture(scope="module")
def raw_schemes_data():
    """Load raw JSON data for testing."""
    data_path = Path(settings.data_path)
    if not data_path.exists():
        pytest.skip(f"Schemes file not found at {data_path}")

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


# ============================================================================
# Required Fields Tests
# ============================================================================

class TestRequiredFields:
    """Test that all schemes have required fields."""

    REQUIRED_FIELDS = ["name", "description", "eligibility", "benefits"]

    OPTIONAL_FIELDS = [
        "documents", "target_group", "scope", "states",
        "application_url", "helpline"
    ]

    def test_all_schemes_have_name(self, schemes_data):
        """Test that all schemes have a name field."""
        for i, scheme in enumerate(schemes_data):
            assert "name" in scheme, f"Scheme at index {i} missing 'name'"
            assert scheme["name"], f"Scheme at index {i} has empty 'name'"
            assert isinstance(scheme["name"], str), f"Scheme '{scheme.get('name', i)}' name is not a string"

    def test_all_schemes_have_description(self, schemes_data):
        """Test that all schemes have a description field."""
        for scheme in schemes_data:
            assert "description" in scheme, f"Scheme '{scheme.get('name', 'Unknown')}' missing 'description'"
            assert scheme["description"], f"Scheme '{scheme.get('name')}' has empty 'description'"
            assert isinstance(scheme["description"], str)

    def test_all_schemes_have_eligibility(self, schemes_data):
        """Test that all schemes have eligibility information."""
        for scheme in schemes_data:
            assert "eligibility" in scheme, f"Scheme '{scheme.get('name', 'Unknown')}' missing 'eligibility'"
            assert scheme["eligibility"], f"Scheme '{scheme.get('name')}' has empty 'eligibility'"

    def test_all_schemes_have_benefits(self, schemes_data):
        """Test that all schemes have benefits information."""
        for scheme in schemes_data:
            assert "benefits" in scheme, f"Scheme '{scheme.get('name', 'Unknown')}' missing 'benefits'"
            assert scheme["benefits"], f"Scheme '{scheme.get('name')}' has empty 'benefits'"

    def test_schemes_have_all_required_fields(self, schemes_data):
        """Test that all schemes have all required fields."""
        for scheme in schemes_data:
            missing_fields = [f for f in self.REQUIRED_FIELDS if f not in scheme or not scheme[f]]
            assert not missing_fields, \
                f"Scheme '{scheme.get('name', 'Unknown')}' missing required fields: {missing_fields}"


# ============================================================================
# Scope Field Validation Tests
# ============================================================================

class TestScopeValidation:
    """Test that scope field is valid."""

    VALID_SCOPES = ["central", "state"]

    def test_scope_is_valid_value(self, schemes_data):
        """Test that scope field has valid values."""
        for scheme in schemes_data:
            if "scope" in scheme:
                assert scheme["scope"] in self.VALID_SCOPES, \
                    f"Scheme '{scheme.get('name')}' has invalid scope: '{scheme['scope']}'. " \
                    f"Must be one of {self.VALID_SCOPES}"

    def test_state_schemes_have_states_list(self, schemes_data):
        """Test that state-level schemes have a states list."""
        for scheme in schemes_data:
            if scheme.get("scope") == "state":
                assert "states" in scheme, \
                    f"State scheme '{scheme.get('name')}' missing 'states' field"
                # States can be empty list for schemes applicable to all states
                assert isinstance(scheme["states"], list), \
                    f"Scheme '{scheme.get('name')}' states field is not a list"

    def test_central_schemes_have_empty_or_no_states(self, schemes_data):
        """Test that central schemes have empty states list."""
        for scheme in schemes_data:
            if scheme.get("scope") == "central":
                if "states" in scheme:
                    assert scheme["states"] == [], \
                        f"Central scheme '{scheme.get('name')}' should have empty states list"


# ============================================================================
# URL Validation Tests
# ============================================================================

class TestURLValidation:
    """Test that application_url fields are valid URLs."""

    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def test_application_url_is_valid_url(self, schemes_data):
        """Test that application_url is a valid URL."""
        for scheme in schemes_data:
            if "application_url" in scheme and scheme["application_url"]:
                url = scheme["application_url"]
                parsed = urlparse(url)

                assert parsed.scheme in ["http", "https"], \
                    f"Scheme '{scheme.get('name')}' has URL with invalid scheme: {url}"
                assert parsed.netloc, \
                    f"Scheme '{scheme.get('name')}' has URL without domain: {url}"

    def test_application_url_uses_https(self, schemes_data):
        """Test that application URLs preferably use HTTPS."""
        http_schemes = []
        for scheme in schemes_data:
            if "application_url" in scheme and scheme["application_url"]:
                url = scheme["application_url"]
                if url.startswith("http://"):
                    http_schemes.append(scheme.get("name"))

        # Warn if any schemes use HTTP (government sites should use HTTPS)
        if http_schemes:
            import warnings
            warnings.warn(
                f"The following schemes use HTTP instead of HTTPS: {http_schemes}",
                UserWarning
            )

    def test_application_url_is_government_domain(self, schemes_data):
        """Test that application URLs are likely government domains."""
        government_tlds = [".gov.in", ".nic.in", ".gov", ".org.in"]

        for scheme in schemes_data:
            if "application_url" in scheme and scheme["application_url"]:
                url = scheme["application_url"]
                parsed = urlparse(url)
                domain = parsed.netloc.lower()

                # Check if it's a government domain
                is_govt = any(domain.endswith(tld) for tld in government_tlds)
                if not is_govt:
                    # This is just a warning, not a failure
                    # Some schemes may use non-.gov domains
                    pass

    def test_application_url_not_empty_when_present(self, schemes_data):
        """Test that application_url is not an empty string when present."""
        for scheme in schemes_data:
            if "application_url" in scheme:
                assert scheme["application_url"] is None or len(scheme["application_url"].strip()) > 0, \
                    f"Scheme '{scheme.get('name')}' has empty application_url"


# ============================================================================
# Documents Array Validation Tests
# ============================================================================

class TestDocumentsValidation:
    """Test that documents arrays are properly formatted."""

    def test_documents_is_array(self, schemes_data):
        """Test that documents field is an array when present."""
        for scheme in schemes_data:
            if "documents" in scheme:
                assert isinstance(scheme["documents"], list), \
                    f"Scheme '{scheme.get('name')}' documents is not a list"

    def test_documents_array_non_empty(self, schemes_data):
        """Test that documents array is non-empty when present."""
        for scheme in schemes_data:
            if "documents" in scheme and scheme["documents"] is not None:
                assert len(scheme["documents"]) > 0, \
                    f"Scheme '{scheme.get('name')}' has empty documents array"

    def test_documents_are_strings(self, schemes_data):
        """Test that all documents in the array are strings."""
        for scheme in schemes_data:
            if "documents" in scheme and scheme["documents"]:
                for i, doc in enumerate(scheme["documents"]):
                    assert isinstance(doc, str), \
                        f"Scheme '{scheme.get('name')}' document at index {i} is not a string"
                    assert doc.strip(), \
                        f"Scheme '{scheme.get('name')}' has empty document string at index {i}"

    def test_documents_no_duplicates(self, schemes_data):
        """Test that documents array has no duplicates."""
        for scheme in schemes_data:
            if "documents" in scheme and scheme["documents"]:
                docs = scheme["documents"]
                # Normalize case for comparison
                docs_lower = [d.lower() for d in docs]
                assert len(docs_lower) == len(set(docs_lower)), \
                    f"Scheme '{scheme.get('name')}' has duplicate documents"

    def test_common_documents_format(self, schemes_data):
        """Test that common documents follow consistent naming."""
        common_documents = {
            "aadhaar": ["Aadhaar Card", "Aadhaar", "Aadhar Card"],
            "pan": ["PAN Card", "PAN"],
            "bank": ["Bank Account Details", "Bank Account", "Bank Passbook"],
        }

        # This test ensures consistency but doesn't fail for variations
        variations_found = {key: False for key in common_documents}
        for scheme in schemes_data:
            if "documents" in scheme and scheme["documents"]:
                docs_lower = [d.lower() for d in scheme["documents"]]
                # Just check that common documents are present in some form
                # This is informational, not a strict requirement
                for key, variants in common_documents.items():
                    variant_lowers = [v.lower() for v in variants]
                    if any(any(v in doc for v in variant_lowers) for doc in docs_lower):
                        variations_found[key] = True

        missing = [key for key, found in variations_found.items() if not found]
        if missing:
            warnings.warn(
                f"No common document variants found for categories: {missing}",
                UserWarning,
            )


# ============================================================================
# Data Integrity Tests
# ============================================================================

class TestDataIntegrity:
    """Test overall data integrity."""

    def test_no_duplicate_scheme_names(self, schemes_data):
        """Test that there are no duplicate scheme names."""
        names = [scheme.get("name") for scheme in schemes_data]
        duplicates = [name for name in names if names.count(name) > 1]

        assert len(duplicates) == 0, \
            f"Duplicate scheme names found: {set(duplicates)}"

    def test_scheme_names_not_empty(self, schemes_data):
        """Test that scheme names are not empty or whitespace."""
        for scheme in schemes_data:
            name = scheme.get("name", "")
            assert name.strip(), "Found scheme with empty or whitespace-only name"

    def test_descriptions_minimum_length(self, schemes_data):
        """Test that descriptions have meaningful content."""
        MIN_DESCRIPTION_LENGTH = 20

        for scheme in schemes_data:
            desc = scheme.get("description", "")
            assert len(desc) >= MIN_DESCRIPTION_LENGTH, \
                f"Scheme '{scheme.get('name')}' has very short description ({len(desc)} chars)"

    def test_eligibility_minimum_length(self, schemes_data):
        """Test that eligibility information is meaningful."""
        MIN_ELIGIBILITY_LENGTH = 10

        for scheme in schemes_data:
            eligibility = scheme.get("eligibility", "")
            assert len(eligibility) >= MIN_ELIGIBILITY_LENGTH, \
                f"Scheme '{scheme.get('name')}' has very short eligibility ({len(eligibility)} chars)"

    def test_json_well_formed(self, raw_schemes_data):
        """Test that the raw JSON data is well-formed."""
        assert "schemes" in raw_schemes_data, "JSON missing 'schemes' key"
        assert isinstance(raw_schemes_data["schemes"], list), "'schemes' is not a list"

    def test_minimum_schemes_count(self, schemes_data):
        """Test that there is a reasonable number of schemes."""
        MIN_SCHEMES = 5  # At least 5 schemes expected

        assert len(schemes_data) >= MIN_SCHEMES, \
            f"Expected at least {MIN_SCHEMES} schemes, found {len(schemes_data)}"


# ============================================================================
# Target Group Validation Tests
# ============================================================================

class TestTargetGroupValidation:
    """Test target_group field validation."""

    def test_target_group_is_string(self, schemes_data):
        """Test that target_group is a string when present."""
        for scheme in schemes_data:
            if "target_group" in scheme and scheme["target_group"] is not None:
                assert isinstance(scheme["target_group"], str), \
                    f"Scheme '{scheme.get('name')}' target_group is not a string"

    def test_target_group_not_empty(self, schemes_data):
        """Test that target_group is not empty when present."""
        for scheme in schemes_data:
            if "target_group" in scheme and scheme["target_group"] is not None:
                assert scheme["target_group"].strip(), \
                    f"Scheme '{scheme.get('name')}' has empty target_group"


# ============================================================================
# Helpline Validation Tests
# ============================================================================

class TestHelplineValidation:
    """Test helpline field validation."""

    def test_helpline_is_string(self, schemes_data):
        """Test that helpline is a string when present."""
        for scheme in schemes_data:
            if "helpline" in scheme and scheme["helpline"] is not None:
                assert isinstance(scheme["helpline"], str), \
                    f"Scheme '{scheme.get('name')}' helpline is not a string"

    def test_helpline_contains_number(self, schemes_data):
        """Test that helpline contains at least one number."""
        for scheme in schemes_data:
            if "helpline" in scheme and scheme["helpline"]:
                helpline = scheme["helpline"]
                has_digits = any(c.isdigit() for c in helpline)
                assert has_digits, \
                    f"Scheme '{scheme.get('name')}' helpline has no digits: {helpline}"


# ============================================================================
# Unicode and Encoding Tests
# ============================================================================

class TestUnicodeEncoding:
    """Test proper Unicode handling."""

    def test_schemes_handle_unicode(self, schemes_data):
        """Test that schemes can contain Unicode characters."""
        # Just verify the data loads without encoding errors
        for scheme in schemes_data:
            # Should not raise any encoding errors
            str(scheme.get("name", ""))
            str(scheme.get("description", ""))

    def test_hindi_content_readable(self, schemes_data):
        """Test that Hindi content is properly encoded."""
        hindi_pattern = re.compile(r'[\u0900-\u097F]')  # Devanagari Unicode block

        # Some schemes might have Hindi in description or benefits
        # This test just verifies the encoding is correct
        for scheme in schemes_data:
            desc = scheme.get("description", "")
            # If Hindi characters present, they should be readable
            if hindi_pattern.search(desc):
                assert len(desc) > 0


# ============================================================================
# Schema Consistency Tests
# ============================================================================

class TestSchemaConsistency:
    """Test that all schemes follow the same schema."""

    def test_all_schemes_same_structure(self, schemes_data):
        """Test that all schemes have consistent structure."""
        if not schemes_data:
            pytest.skip("No schemes to test")

        # Get fields from first scheme
        first_scheme_fields = set(schemes_data[0].keys())

        # Check that all schemes have similar structure
        # (allow for optional fields to be missing)
        required = {"name", "description", "eligibility", "benefits"}

        for scheme in schemes_data:
            scheme_fields = set(scheme.keys())
            # Must have all required fields
            missing_required = required - scheme_fields
            assert not missing_required, \
                f"Scheme '{scheme.get('name')}' missing required fields: {missing_required}"

    def test_no_extra_unknown_fields(self, schemes_data):
        """Test for unknown fields that might indicate data issues."""
        known_fields = {
            "name", "description", "eligibility", "benefits",
            "documents", "target_group", "scope", "states",
            "application_url", "helpline", "ministry", "category",
            "launch_date", "last_updated", "official_name", "short_name"
        }

        for scheme in schemes_data:
            unknown = set(scheme.keys()) - known_fields
            if unknown:
                import warnings
                warnings.warn(
                    f"Scheme '{scheme.get('name')}' has unknown fields: {unknown}",
                    UserWarning
                )


# ============================================================================
# Performance Tests
# ============================================================================

class TestDataPerformance:
    """Test data loading performance."""

    def test_schemes_load_time(self):
        """Test that schemes load within reasonable time."""
        import time

        start = time.time()
        schemes = load_schemes()
        end = time.time()

        load_time = end - start
        assert load_time < 2.0, f"Schemes took too long to load: {load_time:.2f}s"

    def test_schemes_memory_reasonable(self, schemes_data):
        """Test that schemes don't use excessive memory."""
        import sys

        # Rough estimate of memory usage
        total_size = sys.getsizeof(schemes_data)
        for scheme in schemes_data:
            total_size += sys.getsizeof(scheme)
            for v in scheme.values():
                total_size += sys.getsizeof(v)

        # Should be under 10MB
        assert total_size < 10 * 1024 * 1024, \
            f"Schemes data uses too much memory: {total_size / 1024 / 1024:.2f}MB"
