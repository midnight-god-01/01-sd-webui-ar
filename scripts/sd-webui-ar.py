import contextlib
from pathlib import Path
import gradio as gr
import modules.scripts as scripts
from modules.ui_components import ToolButton
from math import gcd

aspect_ratios_dir = scripts.basedir()

CALCULATOR_SYMBOL = "\U0001F4D0"  # 📐
SWITCH_VALUES_SYMBOL = "\U000021C5"  # ⇅
DIMENSIONS_SYMBOL = "\u2B07\ufe0f"  # ⬇️
IMAGE_DIMENSIONS_SYMBOL = "\U0001F5BC"  # 🖼
REVERSE_LOGIC_SYMBOL = "\U0001F503"  # 🔃

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
        if self.ar > 1.0:
            w = self.ar * h
        elif self.ar < 1.0:
            h = w / self.ar
        else:
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
        "16:9, 16/9 # Set width based on 16:9 ratio to height\n",
        "1.85, 1.85 # US widescreen cinema aspect ratio\n",
        "11:8, 1.38 # Academy standard aspect ratio\n",
        "14:9, 1.56 # Aspect ratio used in some TVs\n",
        "16:10, 1.6 # Common computer monitor aspect ratio\n",
        "19:16, 1.19 # Specialized aspect ratio fox movietone\n",
        "2:1, 2.0 # Univisium aspect ratio\n",
        "2:3, 0.67 # Vertical photo aspect ratio\n",
        "21:9, 2.33 # Cinematic widescreen aspect ratio\n",
        "3:2, 1.5 # Classic photo aspect ratio\n",
        "3:5, 0.6 # Tall and narrow aspect ratio\n",
        "32:9, 3.56 # Ultrawide screen aspect ratio\n",
        "4:3, 1.33 # Standard TV and monitor aspect ratio\n",
        "5:3, 1.67 # Super 16mm film aspect ratio\n",
        "5:4, 1.25 # Medium format photo aspect ratio\n",
        "6:13, 0.46 # Uncommon aspect ratio\n",
        "70mm, 2.2 # 70mm film aspect ratio\n",
        "9:16, 0.56 # Portrait mode aspect ratio\n",
        "DCI, 1.9 # Digital IMAX aspect ratio\n",
        "IMAX, 1.43 # IMAX format aspect ratio\n",
        "PV, 4.0 # Polyvision aspect ratio\n",
        "UPV70, 2.76 # Ultra Panavision 70 aspect ratio\n",
        "𝜑, 1.6180 # Golden ratio aspect ratio\n",
        "δ, 2.414 # Silver ratio aspect ratio\n"
    ]
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(aspect_ratios)

def write_resolutions_file(filename):
    resolutions = [
        "1:1, 512, 512\n",
        "3:2, 768, 512\n",
        "9:16, 403, 716\n",
        "XL1:1, 1024, 1024\n",
        "XL5:4, 1152, 896\n",
        "XL3:2, 1216, 832\n",
        "XL16:9, 1344, 768\n",
        "XL21:9, 1536, 640\n"
    ]
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(resolutions)

def write_js_titles_file(button_titles):
    filename = Path(aspect_ratios_dir, "javascript", "button_titles.js")
    content = [
        "// Do not put custom titles here. This file is overwritten each time the WebUI is started.\n"
    ]
    content.append("ar_button_titles = {\n")
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

class AspectRatioScript(scripts.Script):
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

        # TODO: check for duplicates

        # TODO: check for invalid values

        # TODO: use comments as tooltips
        # see https://github.com/alemelis/sd-webui-ar/issues/5

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
                                # For img2img tab
                                if is_img2img:
                                    # Get slider dimensions button
                                    resolution = [self.i2i_w, self.i2i_h]
                                    arc_get_img2img_dim = ToolButton(
                                        value=DIMENSIONS_SYMBOL
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
                                    arc_get_image_dim = ToolButton(
                                        value=IMAGE_DIMENSIONS_SYMBOL
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
                                    arc_get_txt2img_dim = ToolButton(
                                        value=DIMENSIONS_SYMBOL
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
                    arc_calc_height = gr.Button(value="Calculate Height", scale=0, full_width=False)

                    arc_calc_height.click(
                        lambda w2, w1, h1: (solve_aspect_ratio(w2, 0, w1, h1)),
                        inputs=[arc_desired_width, arc_width1, arc_height1],
                        outputs=[arc_desired_height],
                    )
                    arc_calc_width = gr.Button(value="Calculate Width", scale=0, full_width=False)

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
                            lambda w2, h2: (w2, h2),
                            inputs=[arc_desired_width, arc_desired_height],
                            outputs=resolution,
                        )

            # Show calculator pane (and reset number input values)
            arc_show_calculator.click(
                lambda: [
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(value=512),
                    gr.update(value=512),
                    gr.update(value=0),
                    gr.update(value=0),
                    gr.update(value="Aspect Ratio: **1:1**"),
                ],
                None,
                [
                    arc_panel,
                    arc_show_calculator,
                    arc_hide_calculator,
                    arc_width1,
                    arc_height1,
                    arc_desired_width,
                    arc_desired_height,
                    arc_ar_display,
                ],
            )
            # Hide calculator pane
            arc_hide_calculator.click(
                lambda: [
                    gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(visible=False),
                ],
                None,
                [arc_panel, arc_show_calculator, arc_hide_calculator],
            )

    # https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/7456#issuecomment-1414465888
    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_width":
            self.t2i_w = component
        if kwargs.get("elem_id") == "txt2img_height":
            self.t2i_h = component

        if kwargs.get("elem_id") == "img2img_width":
            self.i2i_w = component
        if kwargs.get("elem_id") == "img2img_height":
            self.i2i_h = component

        if kwargs.get("elem_id") == "img2img_image":
            self.image = [component]
        if kwargs.get("elem_id") == "img2img_sketch":
            self.image.append(component)
        if kwargs.get("elem_id") == "img2maskimg":
            self.image.append(component)
        if kwargs.get("elem_id") == "inpaint_sketch":
            self.image.append(component)
        if kwargs.get("elem_id") == "img_inpaint_base":
            self.image.append(component)
