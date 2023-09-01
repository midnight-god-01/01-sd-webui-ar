import contextlib
from pathlib import Path
import gradio as gr
from math import gcd

# Define symbols and constants
BASE_PATH = scripts.basedir()
CALCULATOR_SYMBOL = "\U0001F4D0"
SWITCH_VALUES_SYMBOL = "\U000021C5"
DIMENSIONS_SYMBOL = "\u2B07\ufe0f"
IMAGE_DIMENSIONS_SYMBOL = "\U0001F5BC"
REVERSE_LOGIC_SYMBOL = "\U0001F503"
ROUND_SYMBOL = "\U0001F50D"
IMAGE_ROUNDING_MULTIPLIER = 4

# Global variable for reverse logic mode
is_reverse_logic_mode = False

# Define classes for buttons
class ResButton(ToolButton):
    def __init__(self, res=(512, 512), **kwargs):
        super().__init__(**kwargs)
        self.w, self.h = res

    def reset(self):
        return [self.w, self.h]

class ARButton(ToolButton):
    def __init__(self, ar=1.0, **kwargs):
        super().__init__(**kwargs)
        self.ar = ar

    def apply(self, w, h):
        if is_reverse_logic_mode:
            w, h = self._reverse_calculate_sides(w, h)
        else:
            w, h = self._calculate_sides(w, h)
        return list(map(round, [w, h]))

    def _reverse_calculate_sides(self, w, h):
        if self.ar > 1.0:
            h = w / self.ar
        elif self.ar < 1.0:
            w = h * self.ar
        else:
            new_value = max([w, h])
            w, h = new_value, new_value
        return w, h

    def _calculate_sides(self, w, h):
        if self.ar > 1.0:
            w = h * self.ar
        elif self.ar < 1.0:
            h = w / self.ar
        else:
            new_value = min([w, h])
            w, h = new_value, new_value
        return w, h

    def reset(self, w, h):
        return [self.res, self.res]

# Define functions for parsing files
def parse_aspect_ratios_file(filename):
    labels, values, comments = [], [], []
    file = Path(BASE_PATH, filename)

    if not file.exists():
        return labels, values, comments

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return labels, values, comments

    for line in lines:
        if line.startswith("#"):
            continue

        label, value = line.strip().split(",")
        comment = ""
        if "#" in value:
            value, comment = value.split("#")

        labels.append(label)
        values.append(eval(value))
        comments.append(comment)

    return labels, values, comments

def parse_resolutions_file(filename):
    labels, values, comments = [], [], []
    file = Path(BASE_PATH, filename)

    if not file exists():
        return labels, values, comments

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return labels, values, comments

    for line in lines:
        if line.startswith("#"):
            continue

        label, width, height = line.strip().split(",")
        comment = ""
        if "#" in height:
            height, comment = height.split("#")

        resolution = (width, height)

        labels.append(label)
        values.append(resolution)
        comments.append(comment)

    return labels, values, comments

# Define functions for writing files
def write_aspect_ratios_file(filename):
    aspect_ratios = [
        "3:2, 3/2      # Photography\n",
        "4:3, 4/3      # Television photography\n",
        "16:9, 16/9    # Television photography\n",
        "1.85:1, 1.85  # Cinematography\n",
        "2.39:1, 2.39  # Cinematography",
    ]
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(aspect_ratios)

def write_resolutions_file(filename):
    resolutions = [
        "512, 512, 512     # 512x512\n",
        "640, 640, 640     # 640x640\n",
        "768, 768, 768     # 768x768\n",
        "896, 896, 896     # 896x896\n",
        "1024, 1024, 1024  # 1024x1024",
    ]
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(resolutions)

def write_js_titles_file(button_titles):
    filename = Path(BASE_PATH, "javascript", "button_titles.js")
    content = [
        "// Do not put custom titles here. This file is overwritten each time the WebUI is started.\n"
    ]
    content.append("arsp__ar_button_titles = {\n")
    counter = 0
    while counter < len(button_titles[0]):
        content.append(
            f'    "{button_titles[0][counter]}" : "{button_titles[1][counter]}",\n'
        )
        counter = counter + 1
    content.append("}")

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(content)

def get_reduced_ratio(n, d):
    n, d = list(map(int, (n, d)))

    if n == d:
        return "1:1"

    if n < d:
        div = gcd(d, n)
    else:
        div = gcd(n, d)

    w = int(n) // div
    h = int(d) // div

    if w == 8 and h == 5:
        w = 16
        h = 10

    return f"{w}:{h}"

def solve_aspect_ratio(w, h, n, d):
    if w != 0 and w:
        return round(w / (n / d))
    elif h != 0 and h:
        return round(h * (n / d))
    else:
        return 0

# Define the main class for the Aspect Ratio Script
class AspectRatioScript(scripts.Script):
    def __init__(self):
        super().__init__()

    def read_aspect_ratios(self):
        ar_file = Path(BASE_PATH, "aspect_ratios.txt")
        if not ar_file.exists():
            write_aspect_ratios_file(ar_file)

        (
            self.aspect_ratio_labels,
            aspect_ratios,
            self.aspect_ratio_comments,
        ) = parse_aspect_ratios_file("aspect_ratios.txt")
        self.aspect_ratios = list(map(float, aspect_ratios))

    def read_resolutions(self):
        res_file = Path(BASE_PATH, "resolutions.txt")
        if not res_file.exists():
            write_resolutions_file(res_file)

        self.res_labels, res, self.res_comments = parse_resolutions_file(
            "resolutions.txt"
        )
        self.res = [list(map(int, r)) for r in res]

    def title(self):
        return "Aspect Ratio picker"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Column(
            elem_id=f'arsp__{"img" if is_img2img else "txt"}2img_container_aspect_ratio'
        ):
            self.read_aspect_ratios()
            with gr.Row(
                elem_id=f'arsp__{"img" if is_img2img else "txt"}2img_row_aspect_ratio'
            ):
                arc_show_logic = ToolButton(
                    value=REVERSE_LOGIC_SYMBOL,
                    visible=True,
                    variant="secondary",
                    elem_id="arsp__arc_show_logic_button",
                )
                arc_hide_logic = ToolButton(
                    value=REVERSE_LOGIC_SYMBOL,
                    visible=False,
                    variant="primary",
                    elem_id="arsp__arc_hide_logic_button",
                )

                # Aspect Ratio buttons
                ar_btns = [
                    ARButton(ar=ar, value=label)
                    for ar, label in zip(
                        self.aspect_ratios,
                        self.aspect_ratio_labels,
                    )
                ]

                with contextlib.suppress(AttributeError):
                    for b in ar_btns:
                        if is_img2img:
                            resolution = [self.i2i_w, self.i2i_h]
                        else:
                            resolution = [self.t2i_w, self.t2i_h]

                        b.click(
                            b.apply,
                            inputs=resolution,
                            outputs=resolution,
                        )

            self.read_resolutions()
            with gr.Row(
                elem_id=f'arsp__{"img" if is_img2img else "txt"}2img_row_resolutions'
            ):
                # Toggle calculator display button
                arc_show_calculator = ToolButton(
                    value=CALCULATOR_SYMBOL,
                    visible=True,
                    variant="secondary",
                    elem_id="arsp__arc_show_calculator_button",
                )
                arc_hide_calculator = ToolButton(
                    value=CALCULATOR_SYMBOL,
                    visible=False,
                    variant="primary",
                    elem_id="arsp__arc_hide_calculator_button",
                )

                btns = [
                    ResButton(res=res, value=label)
                    for res, label in zip(self.res, self.res_labels)
                ]
                with contextlib.suppress(AttributeError):
                    for b in btns:
                        if is_img2img:
                            resolution = [self.i2i_w, self.i2i_h]
                        else:
                            resolution = [self.t2i_w, self.t2i_h]

                        b.click(
                            b.reset,
                            outputs=resolution,
                        )

            # Write button_titles.js with labels and comments read from aspect ratios and resolutions files
            button_titles = [self.aspect_ratio_labels + self.res_labels]
            button_titles.append(self.aspect_ratio_comments + self.res_comments)
            write_js_titles_file(button_titles)

            # dummy components needed for JS function
            dummy_text1 = gr.Text(visible=False)
            dummy_text2 = gr.Text(visible=False)
            dummy_text3 = gr.Text(visible=False)
            dummy_text4 = gr.Text(visible=False)

            # Aspect Ratio Calculator
            with gr.Column(
                visible=False, variant="panel", elem_id="arsp__arc_panel"
            ) as arc_panel:
                arc_title_heading = gr.Markdown(value="#### Aspect Ratio Calculator")
                with gr.Row():
                    with gr.Column(min_width=150):
                        arc_width1 = gr.Number(label="Width 1")
                        arc_height1 = gr.Number(label="Height 1")

                    with gr.Column(min_width=150):
                        arc_desired_width = gr.Number(label="Width 2")
                        arc_desired_height = gr.Number(label="Height 2")

                    with gr.Column(min_width=150):
                        arc_ar_display = gr.Markdown(value="Aspect Ratio:", elem_id="arsp__arc_ar_display_text")
                        with gr.Row(
                            elem_id=f'arsp__{"img" if is_img2img else "txt"}2img_arc_tool_buttons'
                        ):
                            # Switch resolution values button
                            arc_swap = ToolButton(value=SWITCH_VALUES_SYMBOL)
                            arc_swap.click(
                                lambda w, h, w2, h2: (h, w, h2, w2),
                                inputs=[
                                    arc_width1,
                                    arc_height1,
                                    arc_desired_width,
                                    arc_desired_height,
                                ],
                                outputs=[
                                    arc_width1,
                                    arc_height1,
                                    arc_desired_width,
                                    arc_desired_height,
                                ],
                            )
                            with contextlib.suppress(AttributeError):
                                if is_img2img:
                                    resolution = [self.i2i_w, self.i2i_h]
                                    arc_get_img2img_dim = ToolButton(
                                        value=DIMENSIONS_SYMBOL
                                    )
                                    arc_get_img2img_dim.click(
                                        lambda w, h: (w, h),
                                        inputs=resolution,
                                        outputs=[arc_width1, arc_height1],
                                    )
                                else:
                                    resolution = [self.t2i_w, self.t2i_h]
                                    arc_get_txt2img_dim = ToolButton(
                                        value=DIMENSIONS_SYMBOL
                                    )
                                    arc_get_txt2img_dim.click(
                                        lambda w, h: (w, h),
                                        inputs=resolution,
                                        outputs=[arc_width1, arc_height1],
                                    )

                            arc_round = ToolButton(value=ROUND_SYMBOL)

                            if is_img2img:
                                with contextlib.suppress(AttributeError):
                                    # Javascript function to select image element from current img2img tab
                                    current_tab_image = """
                                        function current_tab_image(...args) {
                                            const tab_index = get_img2img_tab_index();
                                            // Get current tab
                                            const current_tab = get_tab(tab_index);
                                            // Get image element from current tab
                                            return current_tab.querySelector("img");
                                        }
                                    """
                                    # Javascript function to get image width and height from an image element
                                    get_img_dimensions = """
                                        function get_img_dimensions(img) {
                                            return [img.naturalWidth, img.naturalHeight];
                                        }
                                    """
                                    # Create javascript display function for text to display width and height from image
                                    arc_img_resolution_display = gr.Text(
                                        visible=False, elem_id="arc_img_resolution_display"
                                    )
                                    arc_img_resolution_display.html(
                                        f'<script>{current_tab_image}{get_img_dimensions}</script>'
                                    )
                                    # Javascript function to display width and height from image
                                    arc_round.click(
                                        arc_img_resolution_display.html,
                                        inputs=[
                                            arc_img_resolution_display,
                                            'get_img_dimensions(current_tab_image())'
                                        ],
                                    )

                            with contextlib.suppress(AttributeError):
                                # Javascript function to select text element from current txt2img tab
                                current_tab_text = """
                                    function current_tab_text(...args) {
                                        const tab_index = get_txt2img_tab_index();
                                        // Get current tab
                                        const current_tab = get_tab(tab_index);
                                        // Get text element from current tab
                                        return current_tab.querySelector("textarea");
                                    }
                                """
                                # Javascript function to get width and height from a text element
                                get_txt_dimensions = """
                                    function get_txt_dimensions(text) {
                                        const lines = text.value.split("\\n");
                                        const width = lines.reduce((max, line) => Math.max(max, line.length), 0);
                                        const height = lines.length;
                                        return [width, height];
                                    }
                                """
                                # Create javascript display function for text to display width and height from text
                                arc_txt_resolution_display = gr.Text(
                                    visible=False, elem_id="arc_txt_resolution_display"
                                )
                                arc_txt_resolution_display.html(
                                    f'<script>{current_tab_text}{get_txt_dimensions}</script>'
                                )
                                # Javascript function to display width and height from text
                                arc_round.click(
                                    arc_txt_resolution_display.html,
                                    inputs=[
                                        arc_txt_resolution_display,
                                        'get_txt_dimensions(current_tab_text())'
                                    ],
                                )

                            # Button to calculate aspect ratio
                            arc_calc_button = gr.Button(
                                text="Calculate",
                                elem_id="arsp__arc_calc_button",
                            )
                            arc_calc_button.click(
                                self._calculate_ar,
                                inputs=[
                                    arc_width1,
                                    arc_height1,
                                    arc_desired_width,
                                    arc_desired_height,
                                    arc_ar_display,
                                    arc_width1, arc_height1,
                                    arc_round,
                                    dummy_text1, dummy_text2, dummy_text3, dummy_text4
                                ],
                            )

                            # Display calculated values as 0:0
                            arc_ar_display.set_text("0:0")

                # Aspect Ratio Table
                with gr.Column(
                    visible=False, variant="panel", elem_id="arsp__arc_table_panel"
                ):
                    with gr.Table():
                        self.arc_res_table = gr.Table(
                            ["Name", "Resolution", "Aspect Ratio"]
                        )

                # Build the Calculator layout
                arc_calculator_layout = gr.Layout(
                    [
                        arc_title_heading,
                        arc_show_logic,
                        arc_hide_logic,
                        arc_width1,
                        arc_height1,
                        arc_desired_width,
                        arc_desired_height,
                        arc_swap,
                        arc_round,
                        arc_calc_button,
                        arc_ar_display,
                        arc_img_resolution_display,
                        arc_txt_resolution_display,
                        arc_calculator_layout,
                    ],
                    elem_id="arsp__arc_calculator_layout",
                )

            # Resolutions
            with gr.Column(
                visible=False, variant="panel", elem_id="arsp__arc_resolution_panel"
            ):
                # Width and Height
                res_title_heading = gr.Markdown(
                    value="#### Image Resolution Picker"
                )
                res_width1 = gr.Number(label="Width", value=self.res[0][0])
                res_height1 = gr.Number(label="Height", value=self.res[0][1])

                # Toggle Advanced Settings
                res_show_advanced = ToolButton(
                    value="Show Advanced",
                    variant="primary",
                )
                res_show_advanced.click(
                    res_show_advanced.toggle,
                    elem_id="arsp__arc_advanced_panel",
                )

                # Advanced Settings
                with gr.Column(
                    visible=False, variant="panel", elem_id="arsp__arc_advanced_panel"
                ):
                    # AR Symbol
                    res_ar_symbol = gr.Text(value="Aspect Ratio:")
                    res_ar_symbol.elem_id = "arsp__arc_ar_symbol"

                    # Aspect Ratio dropdown
                    res_ar_dropdown = gr.Dropdown(
                        choices=[
                            get_reduced_ratio(self.res[0][0], self.res[0][1])
                        ],
                        elem_id="arsp__arc_ar_dropdown",
                    )

                    # Custom Aspect Ratio
                    res_ar_custom = gr.Textbox(
                        label="Custom AR", elem_id="arsp__arc_ar_custom"
                    )
                    res_ar_custom.placeholder = "e.g., 16:9"
                    res_ar_custom_tooltip = gr.Text(
                        value="You can enter custom aspect ratios in the format of W:H (e.g., 16:9).",
                        elem_id="arsp__arc_ar_custom_tooltip",
                    )

                    # Generate resolutions from AR
                    res_generate_button = gr.Button(
                        text="Generate",
                        elem_id="arsp__arc_generate_button",
                    )
                    res_generate_button.click(
                        self._generate_resolutions,
                        inputs=[
                            res_width1,
                            res_height1,
                            res_ar_dropdown,
                            res_ar_custom,
                            res_ar_symbol,
                            res_ar_custom_tooltip,
                        ],
                    )

                    # AR Tooltip
                    res_ar_tooltip = gr.Text(
                        value="Aspect Ratio Tooltip",
                        elem_id="arsp__arc_ar_tooltip",
                    )

                    # Calculate aspect ratio from width and height
                    res_calc_button = gr.Button(
                        text="Calculate",
                        elem_id="arsp__arc_ar_calc_button",
                    )
                    res_calc_button.click(
                        self._calculate_res_ar,
                        inputs=[
                            res_width1,
                            res_height1,
                            res_ar_symbol,
                            res_ar_dropdown,
                            res_ar_custom,
                            res_ar_custom_tooltip,
                        ],
                    )

                    # Create the layout for the Advanced Settings panel
                    res_advanced_layout = gr.Layout(
                        [
                            res_ar_symbol,
                            res_ar_dropdown,
                            res_ar_custom,
                            res_ar_custom_tooltip,
                            res_generate_button,
                            res_ar_tooltip,
                            res_calc_button,
                        ],
                        elem_id="arsp__arc_advanced_layout",
                    )

                # Resolution Table
                with gr.Column(
                    visible=False, variant="panel", elem_id="arsp__arc_table_panel"
                ):
                    with gr.Table():
                        self.res_res_table = gr.Table(
                            ["Name", "Resolution", "Aspect Ratio"]
                        )

                # Build the Resolution layout
                res_layout = gr.Layout(
                    [
                        res_title_heading,
                        res_width1,
                        res_height1,
                        res_show_advanced,
                        res_advanced_layout,
                        res_res_table,
                    ],
                    elem_id="arsp__arc_resolution_layout",
                )

            # Create a layout for the Aspect Ratio Script
            ar_script_layout = gr.Layout(
                [arc_show_calculator, arc_hide_calculator, ar_btns, arc_panel, res_layout],
                elem_id="arsp__arc_script_layout",
            )

        # Create the Aspect Ratio Script
        ar_script = AspectRatioScript()
        ar_script.layout = ar_script_layout
        return ar_script

    def run(self, inputs, output, *args, **kwargs):
        self.i2i_w, self.i2i_h = 512, 512
        self.t2i_w, self.t2i_h = 256, 256
        return super().run(inputs, output, *args, **kwargs)

    def _calculate_ar(self, w, h, w2, h2, display, round_button, dummy1, dummy2, dummy3, dummy4):
        round_mode = round_button.is_active()
        desired_ar = (w2 / h2) if h2 > 0 else 0
        calculated_ar = (w / h) if h > 0 else 0
        calculated_ar = round(calculated_ar, 2) if round_mode else calculated_ar

        if is_reverse_logic_mode:
            w, h, w2, h2 = h, w, h2, w2

        display.set_text(f"{w}:{h}")

    def _generate_resolutions(
        self,
        w1,
        h1,
        ar_dropdown,
        ar_custom,
        ar_symbol,
        ar_custom_tooltip,
        round_button,
        dummy1, dummy2, dummy3, dummy4
    ):
        round_mode = round_button.is_active()
        ar_choice = ar_dropdown.value
        ar_choice = ar_custom if ar_choice == "Custom" else ar_choice
        ar_choice = ar_choice.strip()

        # Parse custom aspect ratio
        if ":" in ar_choice:
            try:
                w_ratio, h_ratio = map(int, ar_choice.split(":"))
            except ValueError:
                ar_symbol.set_text("Aspect Ratio: (Invalid)")
                return
        else:
            ar_symbol.set_text("Aspect Ratio: (Invalid)")
            return

        # Calculate new width and height based on the selected aspect ratio
        new_w = w1
        new_h = h1

        if ar_choice == "Custom":
            ar_symbol.set_text("Aspect Ratio: (Custom)")

            # Check for valid custom aspect ratio input
            if not ar_custom:
                ar_custom_tooltip.set_text("You must enter a custom aspect ratio.")
                return

            ar_custom_tooltip.set_text("")
        else:
            ar_symbol.set_text(f"Aspect Ratio: {w_ratio}:{h_ratio}")

            # Calculate new width and height
            if w_ratio != 0 and w_ratio:
                new_w = h1 * w_ratio / h_ratio
            elif h_ratio != 0 and h_ratio:
                new_h = w1 * h_ratio / w_ratio

            # Round the values if necessary
            if round_mode:
                new_w = round(new_w)
                new_h = round(new_h)

        ar_custom_tooltip.set_text("")
        w_ratio = int(w_ratio)
        h_ratio = int(h_ratio)
        display = ar_symbol.get_text().split(" ")
        resolution_name = f"{w1}x{h1} ({w_ratio}:{h_ratio})"

        # Update the resolution dropdown
        ar_dropdown.add_choice(resolution_name, display)
        ar_dropdown.set_value(resolution_name)

        # Add the resolution to the table
        self.res_res_table.add_row(
            [resolution_name, [w1, h1], f"{w_ratio}:{h_ratio}"]
        )

    def _calculate_res_ar(
        self, w1, h1, ar_symbol, ar_dropdown, ar_custom, ar_custom_tooltip
    ):
        ar_choice = ar_dropdown.value
        ar_choice = ar_custom if ar_choice == "Custom" else ar_choice
        ar_choice = ar_choice.strip()

        # Parse custom aspect ratio
        if ":" in ar_choice:
            try:
                w_ratio, h_ratio = map(int, ar_choice.split(":"))
            except ValueError:
                ar_symbol.set_text("Aspect Ratio: (Invalid)")
                return
        else:
            ar_symbol.set_text("Aspect Ratio: (Invalid)")
            return

        ar_symbol.set_text(f"Aspect Ratio: {w_ratio}:{h_ratio}")

        # Calculate new width and height
        if w_ratio != 0 and w_ratio:
            new_w = h1 * w_ratio / h_ratio
        elif h_ratio != 0 and h_ratio:
            new_h = w1 * h_ratio / w_ratio

        display = ar_symbol.get_text().split(" ")
        ar_choice = ar_choice.strip()
        resolution_name = f"{w1}x{h1} ({w_ratio}:{h_ratio})"
        ar_custom_tooltip.set_text("")
        w_ratio = int(w_ratio)
        h_ratio = int(h_ratio)
        display = ar_symbol.get_text().split(" ")
        ar_choice = ar_choice.strip()
        resolution_name = f"{w1}x{h1} ({w_ratio}:{h_ratio})"
        ar_dropdown.add_choice(resolution_name, display)
        ar_dropdown.set_value(resolution_name)
        self.res_res_table.add_row([resolution_name, [w1, h1], f"{w_ratio}:{h_ratio}"])

# Define the Gradio interface
def create_gradio_interface():
    # Main title
    main_title = gr.Markdown(value="## Stable Diffusion - Aspect Ratio and Resolution Picker")

    # Subtitle
    subtitle = gr.Markdown(
        value="Choose aspect ratios and resolutions for your text-to-image generation."
    )

    # Create the Image-to-Image and Text-to-Image tabs
    img2img_tab = AspectRatioScript().ui(is_img2img=True)
    txt2img_tab = AspectRatioScript().ui(is_img2img=False)

    # Create the tab group
    tab_group = gr.TabGroup(
        [
            gr.Tab(img2img_tab, "Image-to-Image", is_selected=True),
            gr.Tab(txt2img_tab, "Text-to-Image"),
        ]
    )

    # Create the Gradio interface
    gr_interface = gr.Interface(
        [main_title, subtitle, tab_group],
        inputs=None,
        outputs=None,
        layout="vertical",
    )

    return gr_interface

# Run the Gradio interface
if __name__ == "__main__":
    gr_interface = create_gradio_interface()
    gr_interface.launch()

