#!/usr/bin/env python3
"""Replace boost_packages.html with the professional 5-plan version."""

template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Boost Your Listing – ReGear Marketplace</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 40px 20px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    .container-boost {
      max-width: 1100px;
      margin: 0 auto;
    }

    .header-section {
      color: white;
      text-align: center;
      margin-bottom: 50px;
      animation: slideDown 0.6s ease-out;
    }

    .header-section h1 {
      font-weight: 800;
      font-size: 2.8rem;
      margin-bottom: 15px;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }

    .header-section p {
      font-size: 1.15rem;
      opacity: 0.95;
      margin-bottom: 10px;
    }

    .header-section small {
      display: block;
      opacity: 0.85;
      font-size: 0.95rem;
    }

    .listing-preview {
      background: white;
      border-radius: 15px;
      padding: 25px;
      margin-bottom: 45px;
      box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
      display: flex;
      gap: 25px;
      align-items: center;
      animation: slideUp 0.6s ease-out;
    }

    .preview-image {
      flex-shrink: 0;
      position: relative;
    }

    .preview-image img {
      width: 120px;
      height: 120px;
      object-fit: cover;
      border-radius: 10px;
      border: 3px solid #f0f0f0;
    }

    .preview-info {
      flex-grow: 1;
    }

    .preview-info h3 {
      color: #333;
      margin-bottom: 8px;
      font-weight: 700;
    }

    .preview-info .price {
      font-size: 1.4rem;
      color: #667eea;
      font-weight: 800;
      margin-bottom: 8px;
    }

    .preview-info .meta {
      color: #666;
      font-size: 0.95rem;
    }

    .preview-info .badge {
      display: inline-block;
      margin-right: 8px;
      margin-top: 10px;
    }

    .plans-section {
      margin-bottom: 40px;
    }

    .section-title {
      color: white;
      text-align: center;
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 10px;
      text-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }

    .section-subtitle {
      color: rgba(255, 255, 255, 0.9);
      text-align: center;
      font-size: 0.95rem;
      margin-bottom: 40px;
    }

    .plans-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 25px;
      margin-bottom: 45px;
    }

    .plan-card {
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      display: flex;
      flex-direction: column;
      height: 100%;
      animation: fadeInUp 0.6s ease-out forwards;
    }

    .plan-card:nth-child(1) { animation-delay: 0.1s; }
    .plan-card:nth-child(2) { animation-delay: 0.15s; }
    .plan-card:nth-child(3) { animation-delay: 0.2s; }
    .plan-card:nth-child(4) { animation-delay: 0.25s; }
    .plan-card:nth-child(5) { animation-delay: 0.3s; }

    .plan-card:hover {
      transform: translateY(-12px) scale(1.02);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
    }

    .plan-card.featured {
      border: 2px solid #667eea;
      transform: scale(1.05);
    }

    .plan-card.featured:hover {
      transform: translateY(-12px) scale(1.07);
    }

    .plan-header {
      padding: 20px;
      color: white;
      text-align: center;
      position: relative;
      overflow: hidden;
    }

    .plan-header.starter { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .plan-header.standard { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .plan-header.premium { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .plan-header.featured { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    .plan-header.super { background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%); }

    .plan-badge {
      position: absolute;
      top: -8px;
      right: -40px;
      background: rgba(255, 255, 255, 0.3);
      color: white;
      padding: 5px 40px;
      font-size: 0.75rem;
      font-weight: 800;
      transform: rotate(45deg);
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .plan-name {
      font-size: 1.3rem;
      font-weight: 800;
      margin: 0 0 8px 0;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .plan-duration {
      font-size: 0.9rem;
      opacity: 0.95;
      margin-bottom: 8px;
    }

    .plan-price {
      font-size: 2rem;
      font-weight: 900;
      margin: 12px 0 0 0;
    }

    .plan-price-period {
      font-size: 0.85rem;
      opacity: 0.9;
    }

    .recommended-ribbon {
      position: absolute;
      top: 20px;
      left: -35px;
      background: #ffd700;
      color: #333;
      padding: 6px 40px;
      font-size: 0.75rem;
      font-weight: 900;
      transform: rotate(-45deg);
      text-transform: uppercase;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
      letter-spacing: 1.5px;
    }

    .plan-body {
      padding: 25px;
      flex-grow: 1;
      display: flex;
      flex-direction: column;
    }

    .plan-benefits {
      list-style: none;
      margin-bottom: 20px;
    }

    .plan-benefits li {
      padding: 10px 0;
      padding-left: 28px;
      position: relative;
      color: #555;
      font-size: 0.95rem;
      line-height: 1.4;
    }

    .plan-benefits li:before {
      content: "✓";
      position: absolute;
      left: 0;
      color: #667eea;
      font-weight: 900;
      font-size: 1.1rem;
    }

    .plan-card.standard .plan-benefits li:before { color: #f5576c; }
    .plan-card.premium .plan-benefits li:before { color: #00f2fe; }
    .plan-card.featured .plan-benefits li:before { color: #ff8e53; }
    .plan-card.super .plan-benefits li:before { color: #ff6b6b; }

    .reach-estimate {
      background: #f5f5f5;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 20px;
      text-align: center;
      font-size: 0.85rem;
      color: #666;
    }

    .reach-estimate strong {
      color: #667eea;
      font-weight: 700;
    }

    .visibility-progress {
      margin-bottom: 15px;
    }

    .visibility-label {
      font-size: 0.75rem;
      color: #999;
      text-transform: uppercase;
      font-weight: 600;
      margin-bottom: 5px;
    }

    .progress {
      height: 6px;
      background-color: #e0e0e0;
      border-radius: 10px;
      overflow: hidden;
    }

    .progress-bar {
      background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
      transition: width 0.3s ease;
    }

    .plan-card.standard .progress-bar { background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); }
    .plan-card.premium .progress-bar { background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); }
    .plan-card.featured .progress-bar { background: linear-gradient(90deg, #fa709a 0%, #fee140 100%); }
    .plan-card.super .progress-bar { background: linear-gradient(90deg, #ff6b6b 0%, #ff8e53 100%); }

    .plan-footer {
      margin-top: auto;
      padding-top: 20px;
      border-top: 1px solid #f0f0f0;
    }

    .plan-button {
      width: 100%;
      padding: 12px;
      border: none;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.95rem;
      cursor: pointer;
      transition: all 0.3s ease;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: white;
      text-decoration: none;
      display: block;
    }

    .plan-button.starter { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .plan-button.standard { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .plan-button.premium { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .plan-button.featured { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    .plan-button.super { background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%); }

    .plan-button:hover {
      transform: scale(1.02);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
      color: white;
      text-decoration: none;
    }

    .comparison-section {
      background: white;
      border-radius: 12px;
      padding: 30px;
      margin-bottom: 40px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      animation: slideUp 0.8s ease-out 0.5s both;
    }

    .comparison-section h3 {
      text-align: center;
      margin-bottom: 25px;
      color: #333;
      font-weight: 700;
    }

    .comparison-table {
      width: 100%;
      border-collapse: collapse;
    }

    .comparison-table th,
    .comparison-table td {
      padding: 12px;
      text-align: center;
      border-bottom: 1px solid #f0f0f0;
      font-size: 0.9rem;
    }

    .comparison-table th {
      background: #f9f9f9;
      font-weight: 700;
      color: #333;
    }

    .comparison-table td:first-child {
      text-align: left;
      color: #666;
      font-weight: 600;
    }

    .comparison-table .check {
      color: #4caf50;
      font-weight: 900;
      font-size: 1.1rem;
    }

    .comparison-table .x {
      color: #ccc;
      font-weight: 700;
    }

    .features-section {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 30px;
      color: white;
      margin-bottom: 40px;
      backdrop-filter: blur(10px);
      animation: slideUp 0.8s ease-out 0.6s both;
    }

    .features-section h3 {
      text-align: center;
      margin-bottom: 25px;
      font-size: 1.4rem;
      font-weight: 800;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
    }

    .feature-item {
      text-align: center;
      padding: 15px;
    }

    .feature-icon {
      font-size: 2.5rem;
      margin-bottom: 10px;
    }

    .feature-name {
      font-weight: 700;
      margin-bottom: 5px;
    }

    .feature-desc {
      font-size: 0.85rem;
      opacity: 0.9;
    }

    .footer-section {
      text-align: center;
      color: white;
      margin-top: 50px;
      animation: fadeIn 0.8s ease-out 0.7s both;
    }

    .footer-section a {
      color: white;
      text-decoration: none;
      font-weight: 600;
      border-bottom: 2px solid white;
      padding-bottom: 2px;
    }

    .footer-section a:hover {
      opacity: 0.8;
    }

    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateY(-30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @keyframes fadeIn {
      from {
        opacity: 0;
      }
      to {
        opacity: 1;
      }
    }

    @media (max-width: 768px) {
      .header-section h1 { font-size: 1.8rem; }
      .plans-grid { grid-template-columns: 1fr; }
      .plan-card.featured { transform: scale(1); }
      .plan-card.featured:hover { transform: translateY(-8px) scale(1.02); }
      .listing-preview { flex-direction: column; gap: 15px; }
      .preview-image img { width: 100%; height: auto; max-width: 200px; }
      .comparison-table { font-size: 0.8rem; }
      .comparison-table th, .comparison-table td { padding: 8px; }
      .features-grid { grid-template-columns: repeat(2, 1fr); }
    }
  </style>
</head>
<body>
  <div class="container-boost">
    <div class="header-section">
      <h1>🚀 Boost Your Listing</h1>
      <p>Get more visibility and reach thousands of buyers</p>
      <small>Choose a plan that works for you</small>
    </div>

    {% if listing %}
    <div class="listing-preview">
      <div class="preview-image">
        {% set img = (listing.photos.split(',')[0] if listing.photos else '') %}
        {% if img %}
          <img src="{{ img|imgurl }}" alt="{{ listing.title }}">
        {% else %}
          <img src="/static/css/placeholder.png" alt="No image">
        {% endif %}
      </div>
      <div class="preview-info">
        <h3>{{ listing.title }}</h3>
        <div class="price">₹{{ listing.price }}</div>
        <div class="meta">
          📍 {{ listing.location or 'India' }} • 
          🏷️ {{ listing.category }} / {{ listing.subcategory }}
        </div>
        <div>
          <span class="badge bg-info">Active</span>
          {% if listing.view_count %}
          <span class="badge bg-secondary">👁️ {{ listing.view_count }} views</span>
          {% endif %}
        </div>
      </div>
    </div>
    {% endif %}

    <div class="plans-section">
      <div class="section-title">💎 Choose Your Boost Package</div>
      <div class="section-subtitle">Prices in INR | Valid for selected duration</div>

      <div class="plans-grid">
        <!-- Starter Plan -->
        <div class="plan-card starter">
          <div class="plan-header starter">
            <div class="plan-name">🌱 Starter</div>
            <div class="plan-duration">Quick Start</div>
            <div class="plan-price">₹<strong>29</strong><span class="plan-price-period"> / 2 days</span></div>
          </div>
          <div class="plan-body">
            <div class="reach-estimate">Estimated reach: <strong>2x</strong> more views</div>
            <div class="visibility-progress">
              <div class="visibility-label">Visibility Level</div>
              <div class="progress"><div class="progress-bar" role="progressbar" style="width: 40%;"></div></div>
            </div>
            <ul class="plan-benefits">
              <li>Basic visibility boost</li>
              <li>Category listing</li>
              <li>2 day duration</li>
              <li>Best for testing</li>
            </ul>
            <div class="plan-footer">
              <form method="POST" action="{{ url_for('apply_boost', listing_id=listing.id) }}" style="display:inline;">
                <input type="hidden" name="days" value="2">
                <input type="hidden" name="price" value="29">
                <input type="hidden" name="boost_type" value="starter">
                <input type="hidden" name="boost_priority" value="1">
                <button type="submit" class="plan-button starter">SELECT PLAN</button>
              </form>
            </div>
          </div>
        </div>

        <!-- Standard Plan -->
        <div class="plan-card standard featured">
          <div class="recommended-ribbon">⭐ BEST VALUE</div>
          <div class="plan-header standard">
            <div class="plan-name">⭐ Standard</div>
            <div class="plan-duration">Most Popular</div>
            <div class="plan-price">₹<strong>99</strong><span class="plan-price-period"> / 7 days</span></div>
          </div>
          <div class="plan-body">
            <div class="reach-estimate">Estimated reach: <strong>5x</strong> more views</div>
            <div class="visibility-progress">
              <div class="visibility-label">Visibility Level</div>
              <div class="progress"><div class="progress-bar" role="progressbar" style="width: 70%;"></div></div>
            </div>
            <ul class="plan-benefits">
              <li>Top in category</li>
              <li>Higher search ranking</li>
              <li>7 day duration</li>
              <li>Great conversion rate</li>
              <li>Most popular choice</li>
            </ul>
            <div class="plan-footer">
              <form method="POST" action="{{ url_for('apply_boost', listing_id=listing.id) }}" style="display:inline;">
                <input type="hidden" name="days" value="7">
                <input type="hidden" name="price" value="99">
                <input type="hidden" name="boost_type" value="standard">
                <input type="hidden" name="boost_priority" value="2">
                <button type="submit" class="plan-button standard">SELECT PLAN</button>
              </form>
            </div>
          </div>
        </div>

        <!-- Premium Plan -->
        <div class="plan-card premium">
          <div class="plan-header premium">
            <div class="plan-name">👑 Premium</div>
            <div class="plan-duration">Power Seller</div>
            <div class="plan-price">₹<strong>199</strong><span class="plan-price-period"> / 15 days</span></div>
          </div>
          <div class="plan-body">
            <div class="reach-estimate">Estimated reach: <strong>10x</strong> more views</div>
            <div class="visibility-progress">
              <div class="visibility-label">Visibility Level</div>
              <div class="progress"><div class="progress-bar" role="progressbar" style="width: 85%;"></div></div>
            </div>
            <ul class="plan-benefits">
              <li>Priority in search results</li>
              <li>More impressions guaranteed</li>
              <li>15 day duration</li>
              <li>Enhanced visibility</li>
              <li>Pro seller feature</li>
            </ul>
            <div class="plan-footer">
              <form method="POST" action="{{ url_for('apply_boost', listing_id=listing.id) }}" style="display:inline;">
                <input type="hidden" name="days" value="15">
                <input type="hidden" name="price" value="199">
                <input type="hidden" name="boost_type" value="premium">
                <input type="hidden" name="boost_priority" value="3">
                <button type="submit" class="plan-button premium">SELECT PLAN</button>
              </form>
            </div>
          </div>
        </div>

        <!-- Featured Plan -->
        <div class="plan-card featured">
          <div class="plan-header featured">
            <div class="plan-name">🌟 Featured</div>
            <div class="plan-duration">Homepage Star</div>
            <div class="plan-price">₹<strong>299</strong><span class="plan-price-period"> / 30 days</span></div>
          </div>
          <div class="plan-body">
            <div class="reach-estimate">Estimated reach: <strong>20x</strong> more views</div>
            <div class="visibility-progress">
              <div class="visibility-label">Visibility Level</div>
              <div class="progress"><div class="progress-bar" role="progressbar" style="width: 95%;"></div></div>
            </div>
            <ul class="plan-benefits">
              <li>Featured on homepage</li>
              <li>Highlighted card design</li>
              <li>30 day duration</li>
              <li>"Featured" badge display</li>
              <li>Maximum visibility</li>
            </ul>
            <div class="plan-footer">
              <form method="POST" action="{{ url_for('apply_boost', listing_id=listing.id) }}" style="display:inline;">
                <input type="hidden" name="days" value="30">
                <input type="hidden" name="price" value="299">
                <input type="hidden" name="boost_type" value="featured">
                <input type="hidden" name="boost_priority" value="3">
                <input type="hidden" name="is_featured" value="1">
                <button type="submit" class="plan-button featured">SELECT PLAN</button>
              </form>
            </div>
          </div>
        </div>

        <!-- Super Boost Plan -->
        <div class="plan-card super">
          <div class="plan-badge">🔥 HOTTEST</div>
          <div class="plan-header super">
            <div class="plan-name">🔥 Super Boost</div>
            <div class="plan-duration">Highest Priority</div>
            <div class="plan-price">₹<strong>499</strong><span class="plan-price-period"> / 7 days</span></div>
          </div>
          <div class="plan-body">
            <div class="reach-estimate">Estimated reach: <strong>50x</strong> more views</div>
            <div class="visibility-progress">
              <div class="visibility-label">Visibility Level</div>
              <div class="progress"><div class="progress-bar" role="progressbar" style="width: 100%;"></div></div>
            </div>
            <ul class="plan-benefits">
              <li>Always on top</li>
              <li>Homepage + Category + Search</li>
              <li>Urgent seller badge</li>
              <li>7 day intensive boost</li>
              <li>Maximum reach & urgency</li>
            </ul>
            <div class="plan-footer">
              <form method="POST" action="{{ url_for('apply_boost', listing_id=listing.id) }}" style="display:inline;">
                <input type="hidden" name="days" value="7">
                <input type="hidden" name="price" value="499">
                <input type="hidden" name="boost_type" value="super">
                <input type="hidden" name="boost_priority" value="5">
                <input type="hidden" name="is_urgent" value="1">
                <button type="submit" class="plan-button super">SELECT PLAN</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison Table -->
    <div class="comparison-section">
      <h3>📊 Plan Comparison</h3>
      <div style="overflow-x: auto;">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>Features</th>
              <th>Starter</th>
              <th>Standard</th>
              <th>Premium</th>
              <th>Featured</th>
              <th>Super Boost</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Price</td>
              <td>₹29</td>
              <td>₹99</td>
              <td>₹199</td>
              <td>₹299</td>
              <td>₹499</td>
            </tr>
            <tr>
              <td>Duration</td>
              <td>2 days</td>
              <td>7 days</td>
              <td>15 days</td>
              <td>30 days</td>
              <td>7 days</td>
            </tr>
            <tr>
              <td>Category Listing</td>
              <td><span class="check">✓</span></td>
              <td><span class="check">✓</span></td>
              <td><span class="check">✓</span></td>
              <td><span class="check">✓</span></td>
              <td><span class="check">✓</span></td>
            </tr>
            <tr>
              <td>Search Priority</td>
              <td><span class="x">—</span></td>
              <td><span class="check">✓</span></td>
              <td><span class="check">✓</span></td>
              <td><span class="check">✓</span></td>
              <td><span class="check">✓</span></td>
            </tr>
            <tr>
              <td>Homepage Featured</td>
              <td><span class="x">—</span></td>
              <td><span class="x">—</span></td>
              <td><span class="x">—</span></td>
              <td><span class="check">✓</span></td>
              <td><span class="check">✓</span></td>
            </tr>
            <tr>
              <td>Urgent Badge</td>
              <td><span class="x">—</span></td>
              <td><span class="x">—</span></td>
              <td><span class="x">—</span></td>
              <td><span class="x">—</span></td>
              <td><span class="check">✓</span></td>
            </tr>
            <tr>
              <td>Always on Top</td>
              <td><span class="x">—</span></td>
              <td><span class="x">—</span></td>
              <td><span class="x">—</span></td>
              <td><span class="x">—</span></td>
              <td><span class="check">✓</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <h3>✨ What You Get With Any Boost</h3>
      <div class="features-grid">
        <div class="feature-item">
          <div class="feature-icon">📈</div>
          <div class="feature-name">More Views</div>
          <div class="feature-desc">Reach thousands of potential buyers</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">⏰</div>
          <div class="feature-name">Auto Renew</div>
          <div class="feature-desc">Optional auto-refresh every 24 hours</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📊</div>
          <div class="feature-name">Performance Stats</div>
          <div class="feature-desc">Track views and engagement</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🎯</div>
          <div class="feature-name">Targeted Reach</div>
          <div class="feature-desc">Show in relevant searches</div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer-section">
      <p style="margin-bottom: 15px;">Have questions? <a href="mailto:support@regear.in">Contact us</a></p>
      <p><a href="{{ url_for('my_listings') }}">← Back to My Listings</a></p>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Write the template to the file
with open('templates/boost_packages.html', 'w', encoding='utf-8') as f:
    f.write(template_content)

print("✅ boost_packages.html has been updated successfully!")
print("  - 5 professional boost plans")
print("  - Enhanced UI with animations")
print("  - Comparison table")
print("  - Professional gradient backgrounds")
print("  - Responsive design")
