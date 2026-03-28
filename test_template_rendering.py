#!/usr/bin/env python3
"""
Simple syntax validation for my_listings.html template
"""

import os
import re

def validate_template_syntax():
    """Basic syntax validation for the template"""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'my_listings.html')

    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print("✅ Template file read successfully")
        print(f"File size: {len(content)} characters")

        # Check for basic template structure (extends dashboard.html)
        if not content.strip().startswith('{% extends "dashboard.html" %}'):
            print("❌ Not extending dashboard.html template")
            return False
        print("✅ Template extends dashboard.html")

        # Check for closing block tag
        if '{% endblock %}' not in content:
            print("❌ Missing endblock tag")
            return False
        print("✅ Endblock tag found")

        # Check for Jinja2 blocks
        if '{% extends' not in content:
            print("❌ Missing template extension")
            return False
        print("✅ Template extension found")

        if '{% block content %}' not in content or '{% endblock %}' not in content:
            print("❌ Missing content block")
            return False
        print("✅ Content block found")

        # Check for boost recommendation elements
        boost_elements = [
            'boost-recommendation-badge-container',
            'boost-hint-container',
            'boost-status-container',
            'boost-recommendation-badge',
            'boost-hint',
            'boost-status',
            'boost-btn-recommended'
        ]

        missing_elements = []
        for element in boost_elements:
            if element not in content:
                missing_elements.append(element)

        if missing_elements:
            print(f"❌ Missing boost elements: {', '.join(missing_elements)}")
            return False
        print("✅ All boost recommendation elements found")

        # Check for JavaScript boost logic
        if 'analyzeBoostRecommendations' not in content:
            print("❌ Missing boost recommendation JavaScript function")
            return False
        print("✅ Boost recommendation JavaScript function found")

        # Check for CSS styles
        css_classes = [
            'boost-recommendation-badge',
            'low-views',
            'no-activity',
            'decay',
            'never-boosted',
            'performing-well'
        ]

        missing_css = []
        for css_class in css_classes:
            if f'.{css_class}' not in content:
                missing_css.append(css_class)

        if missing_css:
            print(f"❌ Missing CSS classes: {', '.join(missing_css)}")
            return False
        print("✅ All boost recommendation CSS classes found")

        return True

    except Exception as e:
        print(f"❌ Error reading template: {str(e)}")
        return False

if __name__ == '__main__':
    print("Validating my_listings.html template syntax...")
    success = validate_template_syntax()
    if success:
        print("\n🎉 Template validation passed!")
    else:
        print("\n💥 Template validation failed!")
        exit(1)