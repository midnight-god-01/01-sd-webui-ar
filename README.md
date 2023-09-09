# Stable Diffusion WebUI Aspect Ratio Selector Extension

Enhance your [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui.git) experience with the Aspect Ratio Selector extension.

## Updates
- **09/09/2023**: We now support Automatic 1111 Version: v1.6.0 and Lobe Theme Version: 3.0.4. We've added more aspect ratios to the main code, improved code organization, and more.

- **20/02/2023** :warning: **Important Update**: This update will replace your local configuration files (`aspect_ratios.txt` and `resolutions.txt`) with new default ones. Don't worry; these can be easily customized and preserved for future use. For detailed instructions, please refer to [this link](https://github.com/alemelis/sd-webui-ar/issues/9).

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

![Screenshot](https://github.com/midnight-god-01/01-sd-webui-ar/blob/main/Screenshots/Screenshot%202023-09-09%20221729.png)

## Usage

Using the Aspect Ratio Selector extension is straightforward:

- Simply click on the aspect ratio button of your choice. The script adjusts the width while keeping the height fixed for aspect ratios greater than 1, and vice versa for aspect ratios less than 1.
- You can reset the image resolution by clicking on one of the buttons in the second row.

### Configuration

Customize aspect ratios in the `/sd-webui-ar/aspect_ratios.txt` file, like this:

```
1:1, 1.0
3:2, 3/2
4:3, 4/3
16:9, 16/9
# 6:13, 6/13
# 9:16, 9/16
# ...
```

Lines starting with `#` are treated as comments and are ignored. To use a custom value, uncomment the respective line by removing the `#`. A custom aspect ratio is defined as `button-label, aspect-ratio-value # comment`. You can choose any label for the button, and it's recommended to set the `aspect-ratio-value` as a fraction, but integers or floats work as well.

Resolution presets can be defined in the `resolutions.txt` file:

```
1, 512, 512 # 1:1 square
2, 768, 512 # 3:2 landscape
3, 403, 716 # 9:16 portrait 
```

Use the format `button-label, width, height, # optional comment`. Lines starting with `#` are ignored.

## Calculator Panel

The calculator helps you determine new width or height values based on the aspect ratio of source dimensions. Here's how it works:

- Click `Calc` to show or hide the aspect ratio calculator.
- Set the source dimensions manually or from other sources.
- Swap the width and height if needed.
- Specify the desired width or height and click either `Calculate Height` or `Calculate Width` to compute the missing value.
- Click `Apply` to transfer the values to the txt2txt/img2img sliders.

![Calculator](https://github.com/midnight-god-01/01-sd-webui-ar/blob/main/Screenshots/Screenshot%202023-09-09%20221858.png)

Enjoy the enhanced functionality of your Stable Diffusion WebUI with the Aspect Ratio Selector extension!
