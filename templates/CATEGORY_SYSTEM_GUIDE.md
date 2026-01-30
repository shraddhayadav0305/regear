# ReGear - Category System Guide

## Overview
This document explains the new hierarchical category system for the ReGear marketplace, similar to OLX's category structure.

## File Structure

### New Files Created:
1. **categories.html** - Main categories page (first level)
2. **subcategories.html** - Subcategories page (second level)
3. **Updated addpost.html** - Enhanced post ad form with category parameters

### Updated Files:
1. **homepg.html** - Updated Sell button to link to categories.html

---

## User Flow

### Step 1: Click "Sell" Button
- User clicks the yellow "Sell" button in the navbar or footer
- Redirects to: `categories.html`

### Step 2: Select Main Category
The user sees 8 main categories:
1. **Electronics** - Mobiles, Computers, Cameras & more
2. **Appliances** - TVs, Fridges, ACs & Washing Machines
3. **Mobile Phones** - Phones, Accessories & Tablets
4. **Computers & Laptops** - Laptops, Desktops & Components
5. **Cameras & Lenses** - DSLR, Mirrorless & Lenses
6. **Games & Entertainment** - Consoles, Games & Accessories
7. **Audio** - Headphones, Speakers & Audio Systems

Each category is interactive with hover effects showing:
- Category icon
- Category name
- Brief description
- Arrow indicator

**URL Format**: `categories.html`

### Step 3: Select Subcategory
- Clicking on a category redirects to: `subcategories.html?category=CategoryName`
- User sees specific subcategories for that category
- Search functionality to filter subcategories

#### Subcategories by Main Category:

**Electronics:**
- Mobile Phones
- Tablets
- Laptops
- Desktops
- Cameras
- Headphones
- Smartwatches
- Accessories

**Mobile:**
- Mobile Phones
- Mobile Phone Accessories
- Tablets
- Chargers & Cables
- Covers & Cases
- Screen Protectors
- Power Banks
- Phone Holders

**Appliances:**
- TVs
- Video - Audio
- Kitchen & Other Appliances
- Fridges
- Washing Machines
- ACs
- Microwaves
- Ovens

**Computers:**
- Laptops
- Desktops
- Computer Accessories
- Hard Disks, Printers & Monitors
- Graphics Cards
- Processors
- RAM
- Motherboards

**Cameras:**
- DSLR Cameras
- Mirrorless Cameras
- Compact Cameras
- Lenses
- Tripods & Stands
- Camera Bags
- Lighting Equipment
- Memory Cards

**Games:**
- Gaming Consoles
- Games & Software
- Gaming Accessories
- Gaming Laptops
- Gaming Headsets
- Gaming Keyboards
- Gaming Mice
- Gaming Chairs

**Audio:**
- Headphones
- Earbuds
- Speakers
- Amplifiers
- Microphones
- Audio Cables
- Audio Interfaces
- Studio Monitors

**URL Format**: `subcategories.html?category=Electronics&subcategory=Mobile%20Phones`

### Step 4: Post an Ad
- Clicking on a subcategory redirects to: `addpost.html?category=MainCategory&subcategory=SubcategoryName`
- The form displays:
  - Primary Category (read-only)
  - Sub Category (read-only)
  - Ad Title (max 80 characters)
  - Condition (Brand New, Like New, Used-Good, Used-Fair)
  - Description (max 2000 characters)
  - Price (USD)
  - Photo Upload (up to 5 photos)
  - Seller Details (Name, Phone)

**Features:**
- Progress bar showing the 5-step process
- Photo preview with remove functionality
- Real-time character count
- Success message on submission
- Automatic redirect to dashboard

---

## Key Features

### 1. Interactive Categories
- Smooth hover animations
- Icons for visual appeal
- Responsive grid layout
- Search functionality in categories page

### 2. Enhanced Form
- Multi-section form layout
- Condition options with descriptions
- Photo upload with preview
- Real-time validation
- Progress indicator

### 3. User-Friendly Design
- Breadcrumb navigation
- Back buttons for easy navigation
- Mobile-responsive layout
- Consistent styling with existing site
- Color scheme: Dark blue (#002f34), Yellow (#ffcc00), Light blue (#0066cc)

### 4. Technical Features
- URL parameters for tracking category selection
- localStorage support (ready to be implemented)
- Form validation
- Loading states
- Success notifications

---

## Navigation Paths

```
homepg.html
    ↓ (Click Sell Button)
categories.html
    ↓ (Click on a category)
subcategories.html?category=X
    ↓ (Click on a subcategory)
addpost.html?category=X&subcategory=Y
    ↓ (Submit form)
dashboard.html
```

---

## Styling & Color Scheme

- **Primary Color**: #002f34 (Dark Navy)
- **Secondary Color**: #0066cc (Bright Blue)
- **Accent Color**: #ffcc00 (Yellow)
- **Background**: #f8f9fa (Light Gray)
- **Border**: #e8e8e8 (Light Gray)

---

## Browser Compatibility
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Future Enhancements
1. Save drafts functionality
2. Category suggestions based on user history
3. Analytics tracking for popular categories
4. Dynamic subcategory loading from database
5. Multi-select categories
6. Category-specific fields and questions

---

## Testing Checklist

- [ ] Click Sell button → categories.html loads
- [ ] Search for category works
- [ ] Select a category → subcategories.html loads with correct category
- [ ] Select subcategory → addpost.html loads with category parameters
- [ ] Form displays correct category and subcategory
- [ ] Photo upload works (max 5 files)
- [ ] Submit form → dashboard loads
- [ ] Mobile responsiveness on all pages
- [ ] Back buttons work correctly
- [ ] Breadcrumb navigation works

---

## Files Modified/Created

### Created:
- `categories.html` (7.2 KB)
- `subcategories.html` (12.1 KB)
- `addpost.html` (completely rewritten, 13.5 KB)

### Modified:
- `homepg.html` (2 links updated)

---

**Last Updated**: January 19, 2026
**Version**: 1.0
