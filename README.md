# Stable Diffusion WebUI Aspect Ratio Selector

This is an extension for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui.git) that adds image aspect ratio selector buttons.

## Updates

- **20/02/2023**: :warning: This update will remove your local configuration files (`aspect_ratios.txt` and `resolutions.txt`) and create new default ones. These can then be freely modified and preserved in the future. For more information, read [here](https://github.com/alemelis/sd-webui-ar/issues/9).

## Installation

To install this extension, follow these steps:

1. Browse to the `Extensions` tab.
2. Go to `Install from URL`.
3. Paste in the following URL: `https://github.com/midnight-god-01/sd-webui-ar.git`.
4. Click `Install`.

After installing this extension, your UI will look like this:

![Screenshot 2023-03-30 at 20 37 56](https://user-images.githubusercontent.com/4661737/228946744-dbffc4c6-8a3f-4a42-8e47-1056b3558afc.png)

## Usage

Here's how to use the aspect ratio selector:

- Click on the aspect ratio button you want to set. If the aspect ratio is greater than 1, the script fixes the width and changes the height. If it's smaller than 1, the width changes while the height is fixed.
- You can reset the image resolution by clicking on one of the buttons on the second row.

### Configuration

You can define aspect ratios in the `/sd-webui-ar/aspect_ratios.txt` file. For example:

```
1:1, 1.0
3:2, 3/2
4:3, 4/3
16:9, 16/9
```

Lines starting with `#` are comments and will be ignored by the extension. To use a custom value, uncomment the relevant line by removing the `#`. A custom aspect ratio is defined as `button-label, aspect-ratio-value # comment`. You can set the `aspect-ratio-value` as a fraction, float, or int. The `# comment` is optional, and the `button-label` can be anything you like.

Resolutions presets are defined in the `resolutions.txt` file:

```
1, 512, 512 # 1:1 square
2, 768, 512 # 3:2 landscape
3, 403, 716 # 9:16 portrait 
```

The format is `button-label, width, height, # optional comment`. Lines starting with `#` are ignored.

## Calculator Panel

You can use the calculator to determine new width or height values based on the aspect ratio of source dimensions. Here's how it works:

- Click `Calc` to show or hide the aspect ratio calculator.
- Set the source dimensions manually or use the buttons to get them from sliders or an input image component.
- Click ⇅ to swap the width and height if desired.
- Set the desired width or height, then click either `Calculate Height` or `Calculate Width` to calculate the missing value.
- Click `Apply` to send the values to the txt2txt/img2img sliders.

![Basic usage of the aspect ratio calculator](https://user-images.githubusercontent.com/121050401/229391634-4ec06027-e603-4672-bad9-ec77647b0941.gif)

