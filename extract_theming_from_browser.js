/**
 * Browser Console Script to Extract Theming from Current Page
 * 
 * Instructions:
 * 1. Open the page you want to scrape in Chrome
 * 2. Open Developer Tools (F12)
 * 3. Go to the Console tab
 * 4. Paste this entire script and press Enter
 * 5. The theming data will be logged and copied to clipboard
 * 6. Save it to a JSON file or copy the output
 */

(function extractTheming() {
  console.log('🎨 Extracting theming from current page...');
  
  // Extract CSS variables from computed styles
  const rootStyles = getComputedStyle(document.documentElement);
  const cssVariables = {};
  const allStyles = Array.from(document.styleSheets);
  
  // Get CSS custom properties from :root
  for (let i = 0; i < rootStyles.length; i++) {
    const propName = rootStyles[i];
    if (propName.startsWith('--')) {
      cssVariables[propName] = rootStyles.getPropertyValue(propName).trim();
    }
  }
  
  // Also extract from style tags and stylesheets
  try {
    Array.from(document.styleSheets).forEach(sheet => {
      try {
        Array.from(sheet.cssRules || []).forEach(rule => {
          if (rule.selectorText === ':root' && rule.style) {
            for (let i = 0; i < rule.style.length; i++) {
              const prop = rule.style[i];
              if (prop.startsWith('--')) {
                cssVariables[prop] = rule.style.getPropertyValue(prop).trim();
              }
            }
          }
        });
      } catch (e) {
        // Cross-origin stylesheet, skip
      }
    });
  } catch (e) {
    console.warn('Could not access all stylesheets:', e);
  }
  
  // Extract colors from computed styles of body and main elements
  const bodyStyles = getComputedStyle(document.body);
  const htmlStyles = getComputedStyle(document.documentElement);
  
  const extractColors = (styles) => {
    const colors = {};
    const colorProps = ['color', 'backgroundColor', 'borderColor', 'background'];
    
    colorProps.forEach(prop => {
      try {
        const value = styles.getPropertyValue(prop) || styles[prop];
        if (value && value !== 'rgba(0, 0, 0, 0)' && value !== 'transparent') {
          colors[prop] = value;
        }
      } catch (e) {}
    });
    
    return colors;
  };
  
  // Extract fonts
  const fonts = {
    body: bodyStyles.fontFamily,
    html: htmlStyles.fontFamily
  };
  
  // Find all color values in inline styles and stylesheets
  const allColors = new Set();
  const colorRegex = /#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\b|rgba?\([^)]+\)|hsl[a]?\([^)]+\)/g;
  
  // Extract from style tags
  document.querySelectorAll('style').forEach(styleTag => {
    const matches = styleTag.textContent.match(colorRegex);
    if (matches) matches.forEach(c => allColors.add(c));
  });
  
  // Extract background gradients
  const backgroundGradients = [];
  [bodyStyles.background, bodyStyles.backgroundImage].forEach(bg => {
    if (bg && bg.includes('gradient')) {
      backgroundGradients.push(bg);
    }
  });
  
  // Get card/container background colors by finding common container elements
  const containerSelectors = ['.card', '.container', '.main', '.content', '[class*="card"]', '[class*="container"]'];
  const containerBgColors = new Set();
  
  containerSelectors.forEach(selector => {
    try {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        const bg = getComputedStyle(el).backgroundColor;
        if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
          containerBgColors.add(bg);
        }
      });
    } catch (e) {}
  });
  
  // Compile theming data
  const theming = {
    url: window.location.href,
    timestamp: new Date().toISOString(),
    css_variables: cssVariables,
    colors: {
      body: extractColors(bodyStyles),
      html: extractColors(htmlStyles),
      all_hex: Array.from(allColors).filter(c => c.startsWith('#')),
      all_rgb: Array.from(allColors).filter(c => c.includes('rgb')),
      container_backgrounds: Array.from(containerBgColors)
    },
    fonts: fonts,
    background_gradients: backgroundGradients,
    computed_styles: {
      body_background: bodyStyles.backgroundColor || bodyStyles.background,
      body_color: bodyStyles.color,
      html_background: htmlStyles.backgroundColor || htmlStyles.background,
    }
  };
  
  // Find primary/brand colors by looking at common CSS variable names
  const suggestedColors = {
    primary: cssVariables['--primary'] || cssVariables['--primary-color'] || cssVariables['--color-primary'],
    secondary: cssVariables['--secondary'] || cssVariables['--secondary-color'],
    background: cssVariables['--bg-dark'] || cssVariables['--background'] || cssVariables['--bg'] || bodyStyles.backgroundColor,
    card_bg: cssVariables['--card-bg'] || cssVariables['--card-background'],
    text: cssVariables['--text'] || cssVariables['--text-color'] || cssVariables['--color-text'] || bodyStyles.color,
    border: cssVariables['--border'] || cssVariables['--border-color'],
  };
  
  // Clean up undefined values
  Object.keys(suggestedColors).forEach(key => {
    if (!suggestedColors[key]) delete suggestedColors[key];
  });
  
  const output = {
    theming: theming,
    suggested_colors: suggestedColors,
    suggestions: {
      css_variables_to_use: Object.keys(cssVariables).slice(0, 20), // First 20 variables
      primary_font: fonts.body || fonts.html,
      background_color: bodyStyles.backgroundColor || htmlStyles.backgroundColor,
    }
  };
  
  // Output results
  console.log('✅ Theming extraction complete!');
  console.log('📊 Results:', output);
  console.log('\n💡 Suggested Colors:', suggestedColors);
  console.log('\n📋 Full theming data has been copied to clipboard.');
  console.log('\nTo save to file, run:');
  console.log('  navigator.clipboard.readText().then(text => {');
  console.log('    const blob = new Blob([text], {type: "application/json"});');
  console.log('    const url = URL.createObjectURL(blob);');
  console.log('    const a = document.createElement("a");');
  console.log('    a.href = url; a.download = "theming.json"; a.click();');
  console.log('  });');
  
  // Copy to clipboard as JSON
  const jsonString = JSON.stringify(output, null, 2);
  navigator.clipboard.writeText(jsonString).then(() => {
    console.log('✅ JSON copied to clipboard!');
    console.log('\n📥 To download directly, run this in console:');
    console.log(`
const blob = new Blob([JSON.stringify(window.extractedTheming, null, 2)], {type: "application/json"});
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "theming.json";
a.click();
console.log("✅ Download started!");
    `.trim());
  }).catch(() => {
    console.log('⚠️ Could not copy to clipboard automatically.');
    console.log('\n📄 Full JSON Output:');
    console.log(jsonString);
  });
  
  // Return for manual access
  window.extractedTheming = output;
  console.log('\n💾 Data also saved to window.extractedTheming');
  console.log('\n💡 Access it anytime with: JSON.stringify(window.extractedTheming, null, 2)');
  
  // Auto-download function (optional - uncomment to enable)
  // Uncomment these lines if you want automatic download:
  /*
  try {
    const blob = new Blob([jsonString], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `theming-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    console.log('✅ File downloaded automatically!');
  } catch (e) {
    console.log('⚠️ Auto-download failed, but data is in clipboard and window.extractedTheming');
  }
  */
  
  return output;
})();

