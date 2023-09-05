Your documentation is already quite informative, but here are some further improvements for clarity and readability:

# Stable Diffusion WebUI Aspect Ratio Selector

An extension for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui.git) that enhances the interface by introducing image aspect ratio selector buttons.

## Fork Features

This extension offers several enhancements:

- New button `🔃` for calculating height and width inversely:
  - Normal mode: `1024x1024 and 16:9 = 1820x1024`
  - Reverse mode: `1024x1024 and 16:9 = 1024x576`
- New button `🔍` for rounding dimensions to the nearest multiples of 4 (`1023x101` => `1024x100`)
- New styles (Some styles have been moved to the original extension)
- Improved resolution presets (Calculated by the formula: `f(x) = 512 + (1024-512)/4*x, 0 <= x <= 4`)
- Enhanced ratios presets (Sourced from [Wikipedia](https://en.wikipedia.org/wiki/Aspect_ratio_(image)))
- Renamed `Calc` button to `📐`
- Compatible with the original extension

![UI Screenshot](https://media.discordapp.net/attachments/1124020774055981108/1125719548587417630/image.png)

## Updates

- **20/02/2023** :warning: **Important Update**: This release will reset your local configuration files (`aspect_ratios.txt` and `resolutions.txt`) and create new default configurations. You can freely modify and preserve these settings in the future. For more information, please read [here](https://github.com/alemelis/sd-webui-ar/issues/9).

## Installation

To install this extension, follow these steps:

1. Navigate to the `Extensions` tab within your Stable Diffusion WebUI.
2. Select `Install from URL`.
3. Paste the following URL: `[https://github.com/alemelis/sd-webui-ar](https://github.com/midnight-god-01/sd-webui-ar.git)`.
4. Click `Install`.

Once installed, your user interface will resemble the following:

![UI Screenshot](https://user-images.githubusercontent.com/4661737/228946744-dbffc4c6-8a3f-4a42-8e47-1056b3558afc.png)

## Usage

Utilizing the aspect ratio selector is straightforward:

1. Click on the desired aspect ratio button. If the aspect ratio is greater than 1, the script adjusts the width and maintains the height. If the aspect ratio is less than 1, the width changes while the height remains constant.
2. To reset the image resolution, simply click one of the buttons on the second row.

### Configuration

Aspect ratios can be defined in the `/sd-webui-ar/aspect_ratios.txt` file. For example:

```
1:1, 1.0
3:2, 3/2
4:3, 4/3
16:9, 16/9
```

Lines starting with `#` are considered comments and are ignored by the extension. To use a custom value, uncomment the relevant line by removing the `#`. A custom aspect ratio is defined as `button-label, aspect-ratio-value # comment`. You can set the `aspect-ratio-value` as a fraction, float, or integer. The `# comment` is optional, and the `button-label` can be customized as desired.

Resolutions presets are configured in the `resolutions.txt` file:

```
1, 512, 512 # 1:1 square
2, 768, 512 # 3:2 landscape
3, 403, 716 # 9:16 portrait 
```

The format is `button-label, width, height, # optional comment`. Lines starting with `#` are ignored.

## Calculator Panel

The calculator enables you to calculate new width or height values based on the aspect ratio of source dimensions. Here's a step-by-step guide:

1. Click `📐` to reveal or hide the aspect ratio calculator.
2. Set the source dimensions manually or use buttons to fetch them from sliders or an input image component.
3. Click `🔃` to swap the width and height if needed.
4. Specify the desired width or height and then click either `Calculate Height` or `Calculate Width` to compute the missing value.
5. Click `Apply` to transmit the values to the txt2txt/img2img sliders.

![Calculator Usage](https://user-images.githubusercontent.com/121050401/229391634-4ec06027-e603-4672-bad9-ec77647b0941.gif)

With these improvements, your documentation is more user-friendly and comprehensive.
