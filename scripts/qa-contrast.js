// Computed, opaque-surface text contrast audit; images and browser UI need human review.
(() => {
  const channels = value => (value.match(/[\d.]+/g) || []).map(Number);
  const luminance = rgb => rgb.slice(0, 3).map(value => {
    value /= 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  }).reduce((total, value, index) => total + value * [0.2126, 0.7152, 0.0722][index], 0);
  const surface = element => {
    for (let node = element; node; node = node.parentElement) {
      const color = channels(getComputedStyle(node).backgroundColor);
      if (color.length === 3 || color[3] === 1) return color;
    }
    return [255, 255, 255];
  };
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const failures = [];
  let checked = 0;
  let minimum = 21;
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const element = node.parentElement;
    if (!node.textContent.trim() || !element || element.closest('script,style,noscript,.skip-link,[aria-hidden="true"]')) continue;
    const style = getComputedStyle(element);
    if (!element.getClientRects().length || style.visibility === 'hidden' || style.opacity === '0') continue;
    const foreground = luminance(channels(style.color));
    const background = luminance(surface(element));
    const ratio = (Math.max(foreground, background) + 0.05) / (Math.min(foreground, background) + 0.05);
    const size = parseFloat(style.fontSize);
    const large = size >= 24 || (size >= 18.667 && parseInt(style.fontWeight, 10) >= 700);
    const threshold = large ? 3 : 4.5;
    checked++;
    minimum = Math.min(minimum, ratio);
    if (ratio < threshold) failures.push({text: node.textContent.trim().slice(0, 100), ratio, threshold, color: style.color});
  }
  return {checked, minimum, failures};
})()
