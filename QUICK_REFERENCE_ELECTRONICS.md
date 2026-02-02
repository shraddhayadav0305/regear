# ⚡ Quick Reference - Electronics Categories

## 🎯 18 Main Categories Overview

```
📱 Mobiles & Smartphones (16 items)
💻 Laptops & Computers (13 items)
⚙️ Computer Hardware (13 items)
⌨️ Peripherals & Accessories (14 items)
🖥️ Monitors & Displays (11 items)
🎧 Audio & Sound (13 items)
📷 Cameras & Optics (14 items)
🖨️ Printers & Scanners (11 items)
🎮 Gaming Hardware (11 items)
🌐 Networking Equipment (10 items)
🔌 Smart Devices & IoT (11 items)
📺 TVs & Displays (12 items)
🍳 Kitchen Appliances (17 items)
❄️ Home Appliances (13 items)
🔧 Electronic Components (15 items)
🔍 Testing & Tools (12 items)
🔋 Batteries & Power (12 items)
🧵 Networking Cables (12 items)
```

---

## 📱 Popular Subcategories by Category

### Mobiles & Smartphones
```
iPhone | Samsung | OnePlus | Xiaomi | Realme
Oppo | Vivo | Motorola | Nokia | Other Mobiles
Mobile Accessories | Phone Chargers | Screen Protectors
Phone Cases | Power Banks | Phone Stands
```

### Laptops & Computers
```
Gaming Laptops | Business Laptops | MacBooks | Ultrabooks
Budget Laptops | Desktop Computers | Gaming PCs
All-in-One PCs | Mini PCs | Workstations
Tablets | iPads | Android Tablets
```

### Computer Hardware
```
Graphics Cards (GPU) | Processors (CPU) | Motherboards
RAM Memory | Solid State Drives (SSD) | Hard Disk Drives (HDD)
Power Supply Units | CPU Coolers | Computer Cases
Fans & Cooling | BIOS Chips | Server Hardware
Networking Cards
```

### Audio & Sound
```
Headphones | Earbuds | Wireless Earbuds | Gaming Headsets
Studio Headphones | Noise Cancelling Headphones
Speakers | Bluetooth Speakers | Studio Monitors
Subwoofers | Microphones | Audio Interfaces | Amplifiers
```

### Gaming Hardware
```
Gaming Consoles | PlayStation | Xbox | Nintendo Switch
Gaming Controllers | VR Headsets | Gaming Chairs
Racing Wheels | Arcade Sticks | Gaming Desks | Gaming Lamps
```

---

## 🔍 Search Examples

### Finding Products
```
Search: "iPhone"        → Shows Mobiles & Smartphones category
Search: "Laptop"        → Shows Laptops & Computers category
Search: "Graphics"      → Shows Computer Hardware category
Search: "Monitor"       → Shows Monitors & Displays category
Search: "Headphone"     → Shows Audio & Sound category
Search: "Smart"         → Shows Smart Devices & IoT category
Search: "Appliance"     → Shows Kitchen/Home Appliances categories
```

---

## 💰 Typical Price Ranges (2nd Hand)

### High Value Items
- Gaming Laptops: ₹30,000 - ₹80,000
- Desktop Gaming PCs: ₹40,000 - ₹120,000
- Graphics Cards (High-end): ₹15,000 - ₹50,000
- 4K Monitors: ₹15,000 - ₹40,000
- DSLR Cameras: ₹20,000 - ₹60,000

### Mid-Range Items
- Regular Laptops: ₹15,000 - ₹40,000
- Monitors: ₹5,000 - ₹15,000
- Printers: ₹5,000 - ₹20,000
- Gaming Headsets: ₹2,000 - ₹8,000
- Smart TVs: ₹10,000 - ₹40,000

### Budget Items
- Phones: ₹5,000 - ₹30,000
- Keyboards & Mouse: ₹500 - ₹3,000
- Phone Chargers: ₹200 - ₹1,000
- USB Cables: ₹100 - ₹500
- Power Banks: ₹1,000 - ₹4,000

---

## 🚀 How to Post a Listing

### Step 1: Navigate
```
Click "Sell" in navbar → /sell
```

### Step 2: Choose Category
```
Example: Click "Mobiles & Smartphones"
URL: /subcategories?category=Mobiles%20%26%20Smartphones
```

### Step 3: Choose Subcategory
```
Example: Click "iPhone"
Saves to session and navigates to /post-ad-form
```

### Step 4: Fill Form
```
✓ Title: "iPhone 13 Pro 256GB Space Gray"
✓ Condition: "Used" or "Like New"
✓ Description: "Excellent condition, minimal scratches"
✓ Price: ₹45000
✓ Location: "Mumbai"
✓ Phone: "9876543210"
✓ Photos: Upload up to 5 images
```

### Step 5: Submit
```
Click "Post Ad" → Database saves listing
Redirect to "My Listings"
```

---

## 🎯 Category Quick Links

```
/sell                                → All categories
/subcategories?category=Mobiles%20%26%20Smartphones
/subcategories?category=Laptops%20%26%20Computers
/subcategories?category=Computer%20Hardware
/subcategories?category=Peripherals%20%26%20Accessories
/subcategories?category=Monitors%20%26%20Displays
/subcategories?category=Audio%20%26%20Sound
/subcategories?category=Cameras%20%26%20Optics
/subcategories?category=Gaming%20Hardware
/subcategories?category=Smart%20Devices%20%26%20IoT
```

---

## 📊 Category Distribution

| Type | Count |
|------|-------|
| **Computing** | 6 categories |
| **Audio/Video** | 4 categories |
| **Appliances** | 2 categories |
| **Components** | 3 categories |
| **Smart/IoT** | 1 category |
| **Tools/Testing** | 1 category |
| **Power/Cables** | 2 categories |
| **Total** | **18 categories** |

---

## ✅ Best Practices for Sellers

### Do:
✅ Use specific subcategories (iPhone, Samsung, etc.)  
✅ Upload clear product photos  
✅ Mention condition clearly (New/Used/Like New)  
✅ Be honest about price and quality  
✅ Respond to inquiries promptly  
✅ Update listing status when sold  

### Don't:
❌ Use generic category names  
❌ Upload blurry photos  
❌ Hide product conditions  
❌ Overprice used items significantly  
❌ Post duplicate listings  
❌ Mislead about specifications  

---

## 🔐 Category Security

All categories are:
- ✅ Validated on backend
- ✅ Stored in session securely
- ✅ Saved to database correctly
- ✅ Protected with authentication
- ✅ XSS-safe via Jinja2 templating

---

## 📞 Technical Details

### Backend Routes
```
GET  /api/categories         → Returns all categories (JSON)
GET  /sell                   → Show category selection
GET  /subcategories          → Show subcategories
POST /save-category          → Save selection (auth required)
GET  /post-ad-form           → Show ad form (auth required)
POST /post-ad-form           → Submit listing (auth required)
```

### Frontend Files
```
templates/categories.html    → Category selection page
templates/subcategories.html → Subcategory selection
templates/addpost.html       → Ad posting form
```

### Database Table
```
listings (18 columns)
├─ category: VARCHAR(100)      -- Main category
├─ subcategory: VARCHAR(100)   -- Specific subcategory
├─ title, description, price
├─ location, phone, email
├─ condition, photos
├─ created_at, status
└─ user_id (foreign key)
```

---

## 🎉 Summary

Your ReGear marketplace is now **exclusively electronics & hardware focused** with:

- **18 main categories** covering all electronics
- **218+ detailed subcategories** for specific items
- **Perfect for second-hand hardware trading**
- **Easy search and discovery**
- **Professional OLX-like interface**
- **Secure authentication & database**
- **Mobile-responsive design**

**Status: ✅ Ready to Go Live!**

Start posting electronics today! 🚀
