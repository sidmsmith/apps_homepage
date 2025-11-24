# Theming Extraction Guide

This guide explains how to extract theming from a webpage that requires authentication or is already open in your browser.

## Method 1: Browser Console Script (Recommended for Authenticated Pages)

### Step 1: Open the Page
1. Open the website you want to extract theming from in Chrome
2. Make sure you're logged in and on the page you want to scrape
3. The page should be fully loaded

### Step 2: Open Developer Tools
1. Press `F12` or right-click and select "Inspect"
2. Go to the **Console** tab

### Step 3: Run the Extraction Script
1. Open the file `extract_theming_from_browser.js` in a text editor
2. Copy the **entire contents** of the file
3. Paste it into the browser console
4. Press `Enter`

### Step 4: Save the Output
The script will automatically:
- Extract all CSS variables from the page
- Extract color values, fonts, and styling
- Copy the JSON output to your clipboard

**Option A: Save from Clipboard**
1. Open a text editor (Notepad, VS Code, etc.)
2. Paste (Ctrl+V)
3. Save as `theming.json`

**Option B: Use Console to Download**
After running the script, in the console run:
```javascript
const blob = new Blob([JSON.stringify(window.extractedTheming, null, 2)], {type: "application/json"});
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "theming.json";
a.click();
```

This will automatically download `theming.json` to your Downloads folder.

### Step 5: Apply the Theming
Once you have `theming.json`:
```bash
python apps_homepage/apply_theming.py theming.json
```

This will automatically update `apps_homepage/index.html` with the extracted theming.

---

## Method 2: Direct URL Scraping (For Public Pages)

If the page is public (no authentication required):

```bash
python apps_homepage/scrape_theming.py https://example.com
```

This will create:
- `scraped_theming.json` - Full theming data
- `theming_suggestions.json` - Suggested colors and CSS variables

---

## What Gets Extracted?

The script extracts:
- ✅ CSS Custom Properties (CSS Variables)
- ✅ Color values (hex, rgb, rgba, hsl)
- ✅ Font families
- ✅ Background colors and gradients
- ✅ Border colors
- ✅ Computed styles from body/html elements
- ✅ Container/card background colors

---

## Tips

1. **Make sure the page is fully loaded** before running the script
2. **Extract from the actual page** you want to style (not a login page)
3. **Check the console output** for warnings or errors
4. **Review the extracted theming.json** to ensure it has the values you need
5. The script works with any website, including authenticated pages

---

## Troubleshooting

**Issue: Script doesn't copy to clipboard**
- Check if your browser allows clipboard access
- Manually copy the JSON from the console output
- Or access `window.extractedTheming` in the console

**Issue: Missing CSS variables**
- Some sites use inline styles instead of CSS variables
- The script still extracts computed styles from elements
- You may need to manually add some values to the JSON

**Issue: Apply script doesn't work**
- Make sure `theming.json` is valid JSON
- Check the file path is correct
- Review the console output for specific errors


