#!/usr/bin/env python
"""
Simple test file to verify pytest setup.
"""

import pytest

def test_simple_assertion():
    """Simple test to verify pytest is working."""
    assert 1 + 1 == 2

class TestSimple:
    """Simple test class."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        assert True
        
    def test_with_client(self, client):
        """Test with Flask client."""
        response = client.get('/')
        # Should get some response (even if it's a redirect or error)
        assert response is not None
