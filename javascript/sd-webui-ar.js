const ar_button_titles = {
  "Calc": "Show or hide the aspect ratio calculator",
  "\u{21c5}": "Swap width and height values",
  "\u2B07\ufe0f": "Get dimensions from txt2img/img2img sliders",
  "\u{1f5bc}": "Get dimensions from image on the current img2img tab",
  "Calculate Height": "Calculate new height based on source aspect ratio",
  "Calculate Width": "Calculate new width based on source aspect ratio",
  "Apply": "Apply calculated width and height to txt2img/img2img sliders"
};

function setTooltips() {
  const buttons = document.querySelectorAll('#txt2img_container_aspect_ratio button, #img2img_container_aspect_ratio button');
  buttons.forEach(elem => {
    const tooltip = ar_button_titles[elem.textContent];
    if (tooltip) {
      elem.title = tooltip;
    }
  });
}

// Check for updates when the UI is updated
onUiUpdate(setTooltips);
