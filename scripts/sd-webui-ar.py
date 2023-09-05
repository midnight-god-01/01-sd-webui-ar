import contextlib
from pathlib import Path
import gradio as gr
import modules.scripts as scripts
from modules.ui_components import ToolButton
from math import gcd

aspect_ratios_dir =  scripts.basedir()
get_calculator_symbol = "\U0001F4D0" # 📐
switch_values_symbol = "\U000021C5" # ⇅
get_dimensions_symbol = "\u2B07\ufe0f" # ⬇️
get_image_dimensions_symbol = "\U0001F5BC" # 🖼
get_reverse_logic_symbol = "\U0001F503" # 🔃
get_round_symbol = "\U0001F50D" # 🔍
IMAGE_ROUNDING_MULTIPLIER = 4

class ResButton(gr.Button):
    def __init__(self, res=(512, 512), **kwargs):
        super().__init__(**kwargs)
        self.w, self.h = res

    def reset(self):
        return [self.w, self.h]

class ARButton(gr.Button):
    def __init__(self, ar=1.0, **kwargs):
        super().__init__(**kwargs)
        self.ar = ar

    def apply(self, w, h):
        if self.ar > 1.0:  # fix height, change width
            w = self.ar * h
        elif self.ar < 1.0:  # fix width, change height
            h = w / self.ar
        else:  # set minimum dimension to both
            min_dim = min([w, h])
            w, h = min_dim, min_dim
        return list(map(round, [w, h]))

    def reset(self, w, h):
        return [self.res, self.res]

def parse_aspect_ratios_file(filename):
    labels, values, comments = [], [], []
    file = Path(aspect_ratios_dir, filename)
    
    if not file.exists():
        return labels, values, comments

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return labels, values, comments

    for line in lines:
        if line.startswith("#"):
            continue

        if ',' not in line:
            continue

        try:
            label, value = line.strip().split(",")
            comment = ""
            if "#" in value:
                value, comment = value.split("#")
        except ValueError:
            print(f"skipping badly formatted line in aspect ratios file: {line}")
            continue

        labels.append(label)
        values.append(eval(value))
        comments.append(comment)

    return labels, values, comments

def parse_resolutions_file(filename):
    labels, values, comments = [], [], []
    file = Path(aspect_ratios_dir, filename)
    
    if not file.exists():
        return labels, values, comments

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return labels, values, comments

    for line in lines:
        if line.startswith("#"):
            continue

        if ',' not in line:
            continue

        try:
            label, width, height = line.strip().split(",")
            comment = ""
            if "#" in height:
                height, comment = height.split("#")
        except ValueError:
            print(f"skipping badly formatted line in resolutions file: {line}")
            continue

        resolution = (width, height)

        labels.append(label)
        values.append(resolution)
        comments.append(comment)

    return labels, values, comments

def write_aspect_ratios_file(filename):
    aspect_ratios = [
        "1:1, 1.0 # 1:1 ratio based on minimum dimension\n",
        "3:2, 3/2 # Set width based on 3:2 ratio to height\n",
        "4:3, 4/3 # Set width based on 4:3 ratio to height\n",
        "16:9, 16/9 # Set width based on 16:9 ratio to height",
    ]
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(aspect_ratios)

def write_resolutions_file(filename):
    resolutions = [
        "1, 512, 512 # 1:1 square\n",
        "2, 768, 512 # 3:2 landscape\n",
        "3, 403, 716 # 9:16 portrait",
    ]
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(resolutions)

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

class AspectRatioScript:
    def __init__(self):
        self.aspect_ratio_labels = []
        self.aspect_ratios = []
        self.aspect_ratio_comments = []

        self.res_labels = []
        self.res = []
        self.res_comments = []

        self.t2i_w = None
        self.t2i_h = None
        self.i2i_w = None
        self.i2i_h = None
        self.image = None

    def read_aspect_ratios(self):
        ar_file = Path(aspect_ratios_dir, "aspect_ratios.txt")
        if not ar_file.exists():
            write_aspect_ratios_file(ar_file)

        (
            self.aspect_ratio_labels,
            aspect_ratios,
            self.aspect_ratio_comments,
        ) = parse_aspect_ratios_file("aspect_ratios.txt")
        self.aspect_ratios = list(map(float, aspect_ratios))

    def read_resolutions(self):
        res_file = Path(aspect_ratios_dir, "resolutions.txt")
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
            elem_id=f'{"img" if is_img2img else "txt"}2img_container_aspect_ratio'
        ):
            self.read_aspect_ratios()
            with gr.Row(
                elem_id=f'{"img" if is_img2img else "txt"}2img_row_aspect_ratio'
            ):
                gr.HTML(
                    visible=True,
                    elem_id="arc_empty_space",
                )

                # Aspect Ratio buttons
                btns = [
                    ARButton(ar=ar, value=label)
                    for ar, label in zip(
                        self.aspect_ratios,
                        self.aspect_ratio_labels,
                    )
                ]

                with contextlib.suppress(AttributeError):
                    for b in btns:
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
                elem_id=f'{"img" if is_img2img else "txt"}2img_row_resolutions'
            ):
                # Toggle calculator display button
                arc_show_calculator = gr.Button(
                    value="Calc",
                    visible=True,
                    variant="secondary",
                    elem_id="arc_show_calculator_button",
                )
                arc_hide_calculator = gr.Button(
                    value="Calc",
                    visible=False,
                    variant="primary",
                    elem_id="arc_hide_calculator_button",
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
                visible=False, variant="panel", elem_id="arc_panel"
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
                        arc_ar_display = gr.Markdown(value="Aspect Ratio:")
                        with gr.Row(
                            elem_id=f'{"img" if is_img2img else "txt"}2img_arc_tool_buttons'
                        ):
                            # Switch resolution values button
                            arc_swap = ResButton(value=switch_values_symbol)
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
                                # For img2img tab
                                if is_img2img:
                                    # Get slider dimensions button
                                    resolution = [self.i2i_w, self.i2i_h]
                                    arc_get_img2img_dim = ResButton(
                                        value=get_dimensions_symbol
                                    )
                                    arc_get_img2img_dim.click(
                                        lambda w, h: (w, h),
                                        inputs=resolution,
                                        outputs=[arc_width1, arc_height1],
                                    )

                                    # Javascript function to select image element from current img2img tab
                                    current_tab_image = """
                                        function current_tab_image(...args) {
                                            const tab_index = get_img2img_tab_index();
                                            // Get current tab's image (on Batch tab, use image from img2img tab)
                                            if (tab_index == 5) {
                                                image = args[0];
                                            } else {
                                                image = args[tab_index];
                                            }
                                            // On Inpaint tab, select just the image and drop the mask
                                            if (tab_index == 2 && image !== null) {
                                                image = image["image"];
                                            }
                                            return [image, null, null, null, null];
                                        }
                                    """

                                    # Get image dimensions
                                    def get_dims(
                                        img: list,
                                        dummy_text1,
                                        dummy_text2,
                                        dummy_text3,
                                        dummy_text4,
                                    ):
                                        if img:
                                            width = img.size[0]
                                            height = img.size[1]
                                            return width, height
                                        else:
                                            return 0, 0

                                    # Get image dimensions button
                                    arc_get_image_dim = ResButton(
                                        value=get_image_dimensions_symbol
                                    )
                                    arc_get_image_dim.click(
                                        fn=get_dims,
                                        inputs=self.image,
                                        outputs=[arc_width1, arc_height1],
                                        _js=current_tab_image,
                                    )

                                else:
                                    # For txt2img tab
                                    # Get slider dimensions button
                                    resolution = [self.t2i_w, self.t2i_h]
                                    arc_get_txt2img_dim = ResButton(
                                        value=get_dimensions_symbol
                                    )
                                    arc_get_txt2img_dim.click(
                                        lambda w, h: (w, h),
                                        inputs=resolution,
                                        outputs=[arc_width1, arc_height1],
                                    )

                    # Update aspect ratio display on change
                    arc_width1.change(
                        lambda w, h: (f"Aspect Ratio: **{get_reduced_ratio(w,h)}**"),
                        inputs=[arc_width1, arc_height1],
                        outputs=[arc_ar_display],
                    )
                    arc_height1.change(
                        lambda w, h: (f"Aspect Ratio: **{get_reduced_ratio(w,h)}**"),
                        inputs=[arc_width1, arc_height1],
                        outputs=[arc_ar_display],
                    )

                with gr.Row():
                    # Calculate and Apply buttons
                    arc_calc_height = gr.Button(value="Calculate Height", scale=0)
                    
                    arc_calc_height.click(
                        lambda w2, w1, h1: (solve_aspect_ratio(w2, 0, w1, h1)),
                        inputs=[arc_desired_width, arc_width1, arc_height1],
                        outputs=[arc_desired_height],
                    )
                    arc_calc_width = gr.Button(value="Calculate Width", scale=0)

                    arc_calc_width.click(
                        lambda h2, w1, h1: (solve_aspect_ratio(0, h2, w1, h1)),
                        inputs=[arc_desired_height, arc_width1, arc_height1],
                        outputs=[arc_desired_width],
                    )
                    arc_apply_params = gr.Button(value="Apply")
                    with contextlib.suppress(AttributeError):
                        if is_img2img:
                            resolution = [self.i2i_w, self.i2i_h]
                        else:
                            resolution = [self.t2i_w, self.t2i_h]

                        arc_apply_params.click(
                            arc_apply_params.click,
                            inputs=[
                                arc_width1,
                                arc_height1,
                                arc_desired_width,
                                arc_desired_height,
                            ],
                            outputs=resolution,
                        )

                    # Round calculations
                    arc_round = gr.Button(value=get_round_symbol)
                    arc_round.click(
                        lambda w, h: [round(w), round(h)],
                        inputs=[arc_desired_width, arc_desired_height],
                        outputs=[arc_desired_width, arc_desired_height],
                    )

                with gr.Row():
                    with gr.Column(min_width=150):
                        arc_desired_width_label = gr.Text(
                            value="Desired Width", visible=True
                        )
                        arc_desired_width_output = gr.Text(
                            value="0", visible=True
                        )

                    with gr.Column(min_width=150):
                        arc_desired_height_label = gr.Text(
                            value="Desired Height", visible=True
                        )
                        arc_desired_height_output = gr.Text(
                            value="0", visible=True
                        )

                with gr.Row():
                    # Javascript function to select image element from current img2img tab
                    current_tab_image = """
                        function current_tab_image(...args) {
                            const tab_index = get_img2img_tab_index();
                            // Get current tab's image (on Batch tab, use image from img2img tab)
                            if (tab_index == 5) {
                                image = args[0];
                            } else {
                                image = args[tab_index];
                            }
                            // On Inpaint tab, select just the image and drop the mask
                            if (tab_index == 2 && image !== null) {
                                image = image["image"];
                            }
                            return [image, null, null, null, null];
                        }
                    """

                    arc_get_image_dim = ResButton(value=get_image_dimensions_symbol)
                    arc_get_image_dim.click(
                        fn=get_dims,
                        inputs=self.image,
                        outputs=[
                            arc_desired_width_output,
                            arc_desired_height_output,
                        ],
                        _js=current_tab_image,
                    )

                    arc_get_calculator = gr.Button(value=get_calculator_symbol)
                    arc_get_calculator.click(
                        gr.disable,
                        inputs=[arc_get_calculator],
                        outputs=[arc_get_calculator],
                    )

                with gr.Row(
                    elem_id=f'{"img" if is_img2img else "txt"}2img_arc_tool_buttons'
                ):
                    # Round calculation button
                    arc_round = ResButton(value=get_round_symbol)
                    arc_round.click(
                        lambda w, h: [
                            round(w / IMAGE_ROUNDING_MULTIPLIER)
                            * IMAGE_ROUNDING_MULTIPLIER,
                            round(h / IMAGE_ROUNDING_MULTIPLIER)
                            * IMAGE_ROUNDING_MULTIPLIER,
                        ],
                        inputs=[
                            arc_desired_width_output,
                            arc_desired_height_output,
                        ],
                        outputs=[
                            arc_desired_width_output,
                            arc_desired_height_output,
                        ],
                    )

                with gr.Row(
                    elem_id=f'{"img" if is_img2img else "txt"}2img_arc_tool_buttons'
                ):
                    # Javascript function to select image element from current img2img tab
                    current_tab_image = """
                        function current_tab_image(...args) {
                            const tab_index = get_img2img_tab_index();
                            // Get current tab's image (on Batch tab, use image from img2img tab)
                            if (tab_index == 5) {
                                image = args[0];
                            } else {
                                image = args[tab_index];
                            }
                            // On Inpaint tab, select just the image and drop the mask
                            if (tab_index == 2 && image !== null) {
                                image = image["image"];
                            }
                            return [image, null, null, null, null];
                        }
                    """

                    arc_get_img2img_dim = ResButton(
                        value=get_dimensions_symbol
                    )
                    arc_get_img2img_dim.click(
                        lambda w, h: [w, h],
                        inputs=[arc_i2i_w, arc_i2i_h],
                        outputs=[
                            arc_i2i_w,
                            arc_i2i_h,
                        ],
                        _js=current_tab_image,
                    )

                with gr.Row():
                    # Javascript function to select image element from current img2img tab
                    current_tab_image = """
                        function current_tab_image(...args) {
                            const tab_index = get_img2img_tab_index();
                            // Get current tab's image (on Batch tab, use image from img2img tab)
                            if (tab_index == 5) {
                                image = args[0];
                            } else {
                                image = args[tab_index];
                            }
                            // On Inpaint tab, select just the image and drop the mask
                            if (tab_index == 2 && image !== null) {
                                image = image["image"];
                            }
                            return [image, null, null, null, null];
                        }
                    """

                    arc_get_image_dim = ResButton(value=get_image_dimensions_symbol)
                    arc_get_image_dim.click(
                        fn=get_dims,
                        inputs=self.image,
                        outputs=[arc_i2i_w, arc_i2i_h],
                        _js=current_tab_image,
                    )

                arc_show_calculator.click(
                    gr.show,
                    inputs=[
                        arc_show_calculator,
                        arc_hide_calculator,
                        arc_panel,
                        arc_get_calculator,
                    ],
                    outputs=[
                        arc_show_calculator,
                        arc_hide_calculator,
                        arc_panel,
                        arc_get_calculator,
                    ],
                )

                arc_hide_calculator.click(
                    gr.hide,
                    inputs=[
                        arc_show_calculator,
                        arc_hide_calculator,
                        arc_panel,
                        arc_get_calculator,
                    ],
                    outputs=[
                        arc_show_calculator,
                        arc_hide_calculator,
                        arc_panel,
                        arc_get_calculator,
                    ],
                )

                arc_calc_height.click(
                    arc_calc_height.click,
                    inputs=[
                        arc_desired_height,
                        arc_desired_width,
                        arc_width1,
                        arc_height1,
                    ],
                    outputs=[arc_desired_height, arc_desired_width],
                )
                arc_calc_width.click(
                    arc_calc_width.click,
                    inputs=[
                        arc_desired_width,
                        arc_desired_height,
                        arc_width1,
                        arc_height1,
                    ],
                    outputs=[arc_desired_width, arc_desired_height],
                )

                arc_panel.append(arc_title_heading)
                arc_panel.append(arc_width1)
                arc_panel.append(arc_height1)
                arc_panel.append(arc_desired_width)
                arc_panel.append(arc_desired_height)
                arc_panel.append(arc_ar_display)
                arc_panel.append(arc_swap)
                arc_panel.append(arc_calc_height)
                arc_panel.append(arc_calc_width)
                arc_panel.append(arc_apply_params)
                arc_panel.append(arc_round)
                arc_panel.append(arc_get_img2img_dim)
                arc_panel.append(arc_get_calculator)
                arc_panel.append(arc_hide_calculator)
                arc_panel.append(arc_show_calculator)
                arc_panel.append(arc_get_image_dim)

                arc_panel.append(dummy_text1)
                arc_panel.append(dummy_text2)
                arc_panel.append(dummy_text3)
                arc_panel.append(dummy_text4)

            with gr.Row(
                elem_id=f'{"img" if is_img2img else "txt"}2img_row_buttons'
            ):
                with gr.Column(min_width=50):
                    gr.Button(
                        label="Reset",
                        variant="primary",
                        click=[
                            arc_width1.reset,
                            arc_height1.reset,
                            arc_desired_width.reset,
                            arc_desired_height.reset,
                        ],
                    )

                    gr.Button(
                        label="Clear",
                        variant="danger",
                        click=[
                            arc_width1.clear,
                            arc_height1.clear,
                            arc_desired_width.clear,
                            arc_desired_height.clear,
                        ],
                    )

                    gr.Button(
                        label="Undo",
                        variant="warning",
                        click=[
                            arc_width1.undo,
                            arc_height1.undo,
                            arc_desired_width.undo,
                            arc_desired_height.undo,
                        ],
                    )

                with gr.Column(min_width=50):
                    arc_calculator = gr.Button(
                        label=get_calculator_symbol,
                        variant="info",
                        click=gr.toggle,
                        elem_id="arc_show_calculator_button",
                    )
                    arc_calculator.click(
                        gr.disable,
                        inputs=[arc_calculator],
                        outputs=[arc_calculator],
                    )

                    arc_img_tool = gr.Button(
                        label=get_image_dimensions_symbol,
                        variant="info",
                        click=gr.toggle,
                        elem_id="arc_show_calculator_button",
                    )
                    arc_img_tool.click(
                        gr.disable,
                        inputs=[arc_img_tool],
                        outputs=[arc_img_tool],
                    )

            # Toggle calculator display button
            arc_show_calculator = gr.Button(
                value="Calc",
                visible=True,
                variant="secondary",
                elem_id="arc_show_calculator_button",
            )
            arc_hide_calculator = gr.Button(
                value="Calc",
                visible=False,
                variant="primary",
                elem_id="arc_hide_calculator_button",
            )
            arc_hide_calculator.click(
                gr.show,
                inputs=[
                    arc_show_calculator,
                    arc_hide_calculator,
                    arc_panel,
                    arc_get_calculator,
                ],
                outputs=[
                    arc_show_calculator,
                    arc_hide_calculator,
                    arc_panel,
                    arc_get_calculator,
                ],
            )

            arc_show_calculator.click(
                gr.hide,
                inputs=[
                    arc_show_calculator,
                    arc_hide_calculator,
                    arc_panel,
                    arc_get_calculator,
                ],
                outputs=[
                    arc_show_calculator,
                    arc_hide_calculator,
                    arc_panel,
                    arc_get_calculator,
                ],
            )

            # Update values from calculator
            arc_desired_width.change(
                lambda w: (arc_width1, w),
                inputs=[arc_desired_width, arc_width1],
                outputs=[arc_width1],
            )

            arc_desired_height.change(
                lambda h: (arc_height1, h),
                inputs=[arc_desired_height, arc_height1],
                outputs=[arc_height1],
            )

            arc_apply_params.click(
                gr.click,
                inputs=[
                    arc_width1,
                    arc_height1,
                    arc_desired_width,
                    arc_desired_height,
                ],
                outputs=resolution,
            )

            # Update aspect ratio display on change
            arc_width1.change(
                lambda w, h: (f"Aspect Ratio: **{get_reduced_ratio(w,h)}**"),
                inputs=[arc_width1, arc_height1],
                outputs=[arc_ar_display],
            )
            arc_height1.change(
                lambda w, h: (f"Aspect Ratio: **{get_reduced_ratio(w,h)}**"),
                inputs=[arc_width1, arc_height1],
                outputs=[arc_ar_display],
            )

            # Calculate and Apply buttons
            arc_calc_height.click(
                gr.click,
                inputs=[
                    arc_desired_height,
                    arc_desired_width,
                    arc_width1,
                    arc_height1,
                ],
                outputs=[arc_desired_height, arc_desired_width],
            )
            arc_calc_width.click(
                gr.click,
                inputs=[
                    arc_desired_width,
                    arc_desired_height,
                    arc_width1,
                    arc_height1,
                ],
                outputs=[arc_desired_width, arc_desired_height],
            )

            arc_round.click(
                gr.click,
                inputs=[
                    arc_desired_width_output,
                    arc_desired_height_output,
                ],
                outputs=[
                    arc_desired_width_output,
                    arc_desired_height_output,
                ],
            )

            arc_get_calculator.click(
                gr.disable,
                inputs=[arc_get_calculator],
                outputs=[arc_get_calculator],
            )

            arc_get_img_tool.click(
                gr.disable,
                inputs=[arc_get_img_tool],
                outputs=[arc_get_img_tool],
            )

            arc_apply_params.click(
                gr.click,
                inputs=[
                    arc_width1,
                    arc_height1,
                    arc_desired_width,
                    arc_desired_height,
                ],
                outputs=resolution,
            )

            arc_round.click(
                gr.click,
                inputs=[
                    arc_desired_width_output,
                    arc_desired_height_output,
                ],
                outputs=[
                    arc_desired_width_output,
                    arc_desired_height_output,
                ],
            )

            arc_get_calculator.click(
                gr.disable,
                inputs=[arc_get_calculator],
                outputs=[arc_get_calculator],
            )

            arc_get_img_tool.click(
                gr.disable,
                inputs=[arc_get_img_tool],
                outputs=[arc_get_img_tool],
            )

            arc_apply_params.click(
                gr.click,
                inputs=[
                    arc_width1,
                    arc_height1,
                    arc_desired_width,
                    arc_desired_height,
                ],
                outputs=resolution,
            )

            with gr.Row():
                # Javascript function to select image element from current img2img tab
                current_tab_image = """
                    function current_tab_image(...args) {
                        const tab_index = get_img2img_tab_index();
                        // Get current tab's image (on Batch tab, use image from img2img tab)
                        if (tab_index == 5) {
                            image = args[0];
                        } else {
                            image = args[tab_index];
                        }
                        // On Inpaint tab, select just the image and drop the mask
                        if (tab_index == 2 && image !== null) {
                            image = image["image"];
                        }
                        return [image, null, null, null, null];
                    }
                """

                arc_get_image_dim = ResButton(
                    value=get_image_dimensions_symbol
                )
                arc_get_image_dim.click(
                    fn=get_dims,
                    inputs=self.image,
                    outputs=[arc_i2i_w, arc_i2i_h],
                    _js=current_tab_image,
                )

            arc_show_calculator.click(
                gr.show,
                inputs=[
                    arc_show_calculator,
                    arc_hide_calculator,
                    arc_panel,
                    arc_get_calculator,
                ],
                outputs=[
                    arc_show_calculator,
                    arc_hide_calculator,
                    arc_panel,
                    arc_get_calculator,
                ],
            )

            arc_hide_calculator.click(
                gr.hide,
                inputs=[
                    arc_show_calculator,
                    arc_hide_calculator,
                    arc_panel,
                    arc_get_calculator,
                ],
                outputs=[
                    arc_show_calculator,
                    arc_hide_calculator,
                    arc_panel,
                    arc_get_calculator,
                ],
            )

            arc_calc_height.click(
                gr.click,
                inputs=[
                    arc_desired_height,
                    arc_desired_width,
                    arc_width1,
                    arc_height1,
                ],
                outputs=[arc_desired_height, arc_desired_width],
            )
            arc_calc_width.click(
                gr.click,
                inputs=[
                    arc_desired_width,
                    arc_desired_height,
                    arc_width1,
                    arc_height1,
                ],
                outputs=[arc_desired_width, arc_desired_height],
            )

            arc_round.click(
                gr.click,
                inputs=[
                    arc_desired_width_output,
                    arc_desired_height_output,
                ],
                outputs=[
                    arc_desired_width_output,
                    arc_desired_height_output,
                ],
            )

            arc_get_calculator.click(
                gr.disable,
                inputs=[arc_get_calculator],
                outputs=[arc_get_calculator],
            )

            arc_get_img_tool.click(
                gr.disable,
                inputs=[arc_get_img_tool],
                outputs=[arc_get_img_tool],
            )

    def on_input_change(self, params):
        self.t2i_w, self.t2i_h, self.i2i_w, self.i2i_h, self.image = (
            params["text2img_width"],
            params["text2img_height"],
            params["img2img_width"],
            params["img2img_height"],
            params["image"],
        )

    def on_init(self):
        self.t2i_w, self.t2i_h, self.i2i_w, self.i2i_h, self.image = (
            0,
            0,
            0,
            0,
            None,
        )

def write_js_titles_file(titles):
    with open("button_titles.js", "w", encoding="utf-8") as f:
        f.write("var button_titles = [")
        f.write(
            ",\n                ".join(
                ['"' + '", "'.join([str(c).strip() for c in r]) + '"' for r in titles]
            )
        )
        f.write("];")

if __name__ == "__main__":
    def custom_code_callback(params):
        print(params)
    gr.Interface(
        custom_code_callback,
        [
            gr.Textbox("image_path", label="Image Path", default="image.jpg"),
            gr.Textbox("prompt", label="Prompt", default="A beautiful sunset scene."),
            gr.Button("Generate Image"),
        ],
        live=True,
    ).launch()
