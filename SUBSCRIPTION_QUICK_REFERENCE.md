# Quick Reference - Seller Subscription System

## 🔍 View Subscription Status (Dashboard Display)

```python
from subscription_helpers import get_subscription_info

# In dashboard route
info = get_subscription_info(user_id)
if info:
    # Display to user
    plan_name = info['plan_name']          # e.g., 'Growth'
    ads_used = info['ads_used']            # e.g., 3
    ad_limit = info['ad_limit']            # e.g., 15
    remaining = info['remaining']          # e.g., 12
    end_date = info['end_date']            # datetime object
    status = info['status']                # 'active' or 'expired'
```

---

## 🛡️ Check Before Allowing Boost

```python
from subscription_helpers import can_user_boost_ad, mark_expired_subscriptions

# In boost route
mark_expired_subscriptions(user_id)
can_boost, plan_name, remaining = can_user_boost_ad(user_id)

if not can_boost:
    flash("Subscription boost limit reached. Upgrade plan or buy individual boost.", "error")
    return redirect(url_for("my_listings"))

# Otherwise, proceed with boost, then:
from subscription_helpers import increment_subscription_boost_count, get_user_active_subscription

sub = get_user_active_subscription(user_id)
increment_subscription_boost_count(user_id, sub['id'])
```

---

## 💳 Create Subscription After Payment

```python
from subscription_helpers import (
    create_user_subscription,
    record_subscription_transaction
)

# After payment succeeds
subscription_id = create_user_subscription(
    user_id=user_id,
    plan_name=selected_plan,  # 'Starter', 'Growth', 'Pro', or 'Business'
    duration_days=30
)

# Log the transaction
record_subscription_transaction(
    user_id=user_id,
    plan_name=selected_plan,
    amount=plan_prices[selected_plan],
    duration_days=30,
    payment_status='success',
    transaction_id=payment_id,
    payment_method='UPI'  # or other method
)

# Subscription is now active
flash(f"✅ Subscription activated! You have {plan_limits[selected_plan]} boosts.", "success")
return redirect(url_for("subscription_success"))
```

---

## 📊 Plan Details (Hardcoded in subscription_helpers.py)

```python
PLANS = {
    'Starter': {'ad_limit': 5, 'amount': 149, 'days': 30},
    'Growth': {'ad_limit': 15, 'amount': 299, 'days': 30},
    'Pro': {'ad_limit': 40, 'amount': 599, 'days': 30},
    'Business': {'ad_limit': -1, 'amount': 999, 'days': 30}  # -1 = unlimited
}
```

---

## 🧪 Quick Test

```bash
python test_subscription_system.py
```

Expected output: **9/9 tests passed** ✅

---

## 🗄️ Database Tables Schema

### user_subscriptions
```sql
id, user_id, plan_name, ad_limit, ads_used, 
start_date, end_date, status, created_at, updated_at
```

### subscription_transactions
```sql
id, user_id, plan_name, amount, duration_days,
payment_method, payment_status, transaction_id, created_at
```

### ad_boosts (enhanced)
```sql
-- Added field:
subscription_id  -- NULL if individual boost, subscription_id if subscription boost
```

---

## 🔗 Routes

| Method | Route | Purpose |
|--------|-------|---------|
| GET | /seller-packages | Display plans |
| POST | /subscription-payment | Handle plan selection |
| POST | /process-subscription-payment | Create subscription |
| GET | /subscription-success | Success redirect |

---

## 🎯 Common Tasks

**Check if user has active subscription:**
```python
from subscription_helpers import get_user_active_subscription
sub = get_user_active_subscription(user_id)
has_subscription = sub is not None
```

**Mark expired subscriptions:**
```python
from subscription_helpers import mark_expired_subscriptions
mark_expired_subscriptions(user_id)  # Auto-runs on login & dashboard
```

**Display in template:**
```html
{% if subscription %}
    <div class="subscription-badge">
        <strong>{{ subscription.plan_name }}</strong>
        Used: {{ subscription.ads_used }}/{{ subscription.ad_limit if subscription.ad_limit != -1 else '∞' }}
        Expires: {{ subscription.end_date.strftime('%Y-%m-%d') }}
    </div>
{% else %}
    <div class="no-subscription">
        <a href="/seller-packages">Get a subscription plan</a>
    </div>
{% endif %}
```

---

## ⚠️ Common Mistakes

❌ **Don't:** Call create_user_subscription without verifying payment
✅ **Do:** Only call after payment confirmation

❌ **Don't:** Forget to increment ads_used after subscription boost
✅ **Do:** Always call increment_subscription_boost_count()

❌ **Don't:** Check subscription once and cache it
✅ **Do:** Always call mark_expired_subscriptions() first in routes

❌ **Don't:** Use hardcoded ad_limit values
✅ **Do:** Get from database via get_subscription_info()

---

## 📝 Logging Payment

```python
record_subscription_transaction(
    user_id,
    plan_name,  # Must be 'Starter', 'Growth', 'Pro', or 'Business'
    amount,     # Float like 299.0
    duration_days,  # Usually 30
    payment_status,  # 'success' or 'failed'
    transaction_id,  # Unique ID from payment gateway
    payment_method   # 'UPI', 'Card', 'NetBanking', or 'Wallet'
)
```

---

**Last Updated:** 2026-03-25  
**Status:** All features working ✅
