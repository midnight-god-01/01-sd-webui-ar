# Stable Diffusion WebUI Aspect Ratio Selector Extension

Elevate your [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui.git) experience with the Aspect Ratio Selector extension.

## Updates
- **09/09/2023** : Automatic 1111 Version: v1.6.0 support, lobe theme version: 3.0.4 support, added more aspect ratios to the main code, improved code organization, and more.

- **20/02/2023** :warning: **Important Update**: This update will replace your local configuration files (`aspect_ratios.txt` and `resolutions.txt`) with new default ones. These can be easily customized and preserved for future use. For detailed instructions, please refer to [this link](https://github.com/alemelis/sd-webui-ar/issues/9).

## Installation

You can install the Aspect Ratio Selector extension using one of the following methods:

### Method 1: Install from URL

1. Navigate to the `Extensions` tab.
2. Select `Install from URL`.
3. Paste the following URL: `(https://github.com/midnight-god-01/sd-webui-ar.git)`.
4. Click on `Install`.

### Method 2: Install with Git Clone (Alternative)

1. Open your terminal or command prompt.
2. Navigate to the directory where you want to install the extension.
3. Run the following command to clone the extension repository:

```bash
git clone https://github.com/midnight-god-01/sd-webui-ar.git
```

4. Once the cloning process is complete, you can use the extension as described in the "Usage" section below.

Here's a sneak peek of the user interface after installing this extension:

https://github.com/midnight-god-01/01-sd-webui-ar/blob/main/Screenshots/Screenshot%202023-09-09%20221729.png

## Usage

- Simply click on the aspect ratio button of your choice. If the aspect ratio is greater than 1, the script adjusts the width while keeping the height fixed. Conversely, if the aspect ratio is less than 1, it changes the height while keeping the width fixed.
- You can reset the image resolution by clicking on one of the buttons in the second row.

### Configuration

You can define aspect ratios in the `/sd-webui-ar/aspect_ratios.txt` file. For example:

```
1:1, 1.0
3:2, 3/2
4:3, 4/3
16:9, 16/9
# 6:13, 6/13
# 9:16, 9/16
# 3:5, 3/5
# 2:3, 2/3
# 19:16, 19/16 # fox movietone
# 5:4, 5/4 # medium format photo
# 11:8, 11/8 # academy standard
# IMAX, 1.43
# 14:9, 14/9
# 16:10, 16/10
# 𝜑, 1.6180 # golden ratio
# 5:3, 5/3 # super 16mm
# 1.85, 1.85 # US widescreen cinema
# DCI, 1.9 # digital imax
# 2:1, 2.0 # univisium
# 70mm, 2.2
# 21:9, 21/9 # cinematic wide screen
# δ, 2.414 # silver ratio
# UPV70, 2.76 # ultra panavision 70
# 32:9, 32/9 # ultra wide screen
# PV, 4.0 # polyvision
```

Lines starting with `#` are treated as comments and are not read by the extension. To use a custom value, simply uncomment the respective line by removing the `#` at the beginning. A custom aspect ratio is defined as `button-label, aspect-ratio-value # comment`. You can choose any label for the button. It's recommended to set the `aspect-ratio-value` as a fraction, but integers or floats work as well. The `# comment` is optional.

Resolution presets can be defined in the `resolutions.txt` file:

```
1, 512, 512 # 1:1 square
2, 768, 512 # 3:2 landscape
3, 403, 716 # 9:16 portrait 
```

Use the format `button-label, width, height, # optional comment`. Again, lines starting with `#` are ignored.

## Calculator Panel

The calculator allows you to determine new width or height values based on the aspect ratio of source dimensions. Here's how it works:

- Click `Calc` to show or hide the aspect ratio calculator.
- Set the source dimensions:
  - Enter them manually.
  - Click ⬇️ to get source dimensions from txt2img/img2img sliders.
  - Click 🖼️ to get source dimensions from the input image component on the current tab.
- Click ⇅ to swap the width and height if needed.
- Specify the desired width or height and click either `Calculate Height` or `Calculate Width` to compute the missing value.
- Click `Apply` to transfer the values to the txt2txt/img2img sliders.

https://github.com/midnight-god-01/01-sd-webui-ar/blob/main/Screenshots/Screenshot%202023-09-09%20221858.png 

Enjoy the enhanced functionality of your Stable Diffusion WebUI with the Aspect Ratio Selector extension!

