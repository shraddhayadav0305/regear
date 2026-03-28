#!/usr/bin/env python3
"""Test the Boost Recommendation System logic"""

def test_boost_recommendations():
    """Test various scenarios for boost recommendations"""

    test_cases = [
        # (ad_age, view_count, messages_count, boost_expires, expected_recommendation)
        (1, 5, 0, None, 'never-boosted'),  # Too new for urgent conditions, but never boosted
        (3, 5, 0, None, 'low-views'),  # Low views, old enough
        (3, 0, 0, None, 'no-activity'),  # No views takes priority over low views
        (3, 2, 1, None, 'low-views'),  # Low views but has messages
        (6, 15, 2, None, 'decay'),  # Old ad, not recently boosted
        (2, 25, 3, None, 'performing-well'),  # Good performance
        (1, 0, 0, None, 'never-boosted'),  # Too new for no-activity, never boosted
        (4, 8, 1, None, 'low-views'),  # Low views
        (7, 20, 5, '2024-01-01 10:00:00', 'decay'),  # Old boost, needs reboost
        (2, 12, 2, '2024-12-01 10:00:00', None),  # Recent boost, no recommendation
        (10, 3, 0, '2024-05-20 10:00:00', 'reboost-ready'),  # Old boost, ready for reboost
    ]

    print("Testing Boost Recommendation Logic:")
    print("=" * 50)

    for i, (ad_age, view_count, messages_count, boost_expires, expected) in enumerate(test_cases, 1):
        # Simulate the corrected JavaScript logic
        recommendation = None

        # Calculate days since last boost
        days_since_last_boost = None
        if boost_expires:
            # For testing, assume current date is 2024-06-01
            current_date = '2024-06-01'
            if boost_expires < current_date:
                days_since_last_boost = 30  # Assume old boost
            else:
                days_since_last_boost = 0

        # Apply logic in correct priority order
        if view_count < 10 and ad_age >= 2:
            recommendation = 'low-views'
        elif view_count == 0 or (messages_count == 0 and ad_age >= 2):
            recommendation = 'no-activity'
        elif ad_age >= 5 and (not boost_expires or days_since_last_boost >= 3):
            recommendation = 'decay'
        elif boost_expires and days_since_last_boost >= 3:
            recommendation = 'reboost-ready'
        elif not boost_expires:
            recommendation = 'never-boosted'
        elif view_count >= 20 and ad_age >= 1:
            recommendation = 'performing-well'

        status = "✓" if recommendation == expected else "✗"
        print(f"Test {i}: {status} Age:{ad_age}d Views:{view_count} Msg:{messages_count} Boost:{boost_expires} → {recommendation} (expected: {expected})")

if __name__ == "__main__":
    test_boost_recommendations()