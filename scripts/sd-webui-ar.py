import contextlib
from pathlib import Path
import gradio as gr
import modules.scripts as scripts
from modules.ui_components import ToolButton
from math import gcd

BASE_PATH = scripts.basedir()
CALCULATOR_SYMBOL = "\U0001F4D0"  # 📐
SWITCH_VALUES_SYMBOL = "\U000021C5"  # ⇅
DIMENSIONS_SYMBOL = "\u2B07\ufe0f"  # ⬇️
IMAGE_DIMENSIONS_SYMBOL = "\U0001F5BC"  # 🖼
REVERSE_LOGIC_SYMBOL = "\U0001F503"  # 🔃
ROUND_SYMBOL = "\U0001F50D"  # 🔍
IMAGE_ROUNDING_MULTIPLIER = 4

is_reverse_logic_mode = False  # FIXME: Global value


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


def parse_file(filename, parse_function):
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

        parts = line.strip().split("#")
        label, value = parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""

        # Extract the numeric part (e.g., "3:2" -> "3.0:2.0" -> (3.0, 2.0))
        numeric_parts = parts[0].split(":")
        if len(numeric_parts) == 2:
            numeric_value = parse_function(float(numeric_parts[0]) / float(numeric_parts[1]))
        else:
            numeric_value = 0.0

        labels.append(label)
        values.append(numeric_value)
        comments.append(value)

    return labels, values, comments


def write_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(data)


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
    if w:
        return round(w / (n / d))
    elif h:
        return round(h * (n / d))
    else:
        return 0


class AspectRatioScript(scripts.Script):
    def __init__(self):
        super().__init__()
        self.aspect_ratio_labels = []
        self.aspect_ratios = []
        self.aspect_ratio_comments = []
        self.res_labels = []
        self.res = []
        self.res_comments = []

    def read_aspect_ratios(self):
        ar_file = Path(BASE_PATH, "aspect_ratios.txt")
        if not ar_file.exists():
            self.write_aspect_ratios_file(ar_file)

        (
            self.aspect_ratio_labels,
            aspect_ratios,
            self.aspect_ratio_comments,
        ) = parse_file("aspect_ratios.txt", float)
        self.aspect_ratios = aspect_ratios

        # TODO: check for duplicates
        # TODO: check for invalid values
        # TODO: use comments as tooltips

    def read_resolutions(self):
        res_file = Path(BASE_PATH, "resolutions.txt")
        if not res_file.exists():
            self.write_resolutions_file(res_file)

        self.res_labels, res, self.res_comments = parse_file(
            "resolutions.txt", lambda x: list(map(int, x.split(',')))
        )
        self.res = res

    def write_aspect_ratios_file(self, filename):
        aspect_ratios = [
            "3:2, 3/2      # Photography\n",
            "4:3, 4/3      # Television photography\n",
            "16:9, 16/9    # Television photography\n",
            "1.85:1, 1.85  # Cinematography\n",
            "2.39:1, 2.39  # Cinematography",
        ]
        write_file(filename, aspect_ratios)

    def write_resolutions_file(self, filename):
        resolutions = [
            "512, 512, 512     # 512x512\n",
            "640, 640, 640     # 640x640\n",
            "768, 768, 768     # 768x768\n",
            "896, 896, 896     # 896x896\n",
            "1024, 1024, 1024  # 1024x1024",
        ]
        write_file(filename, resolutions)

    def write_js_titles_file(self, button_titles):
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
            self.write_js_titles_file(button_titles)

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
                    arc_calc_height = gr.Button(value="Calculate Height").style(
                        full_width=False
                    )
                    arc_calc_height.click(
                        lambda w, h: solve_aspect_ratio(w, h, arc_desired_width, arc_desired_height),
                        inputs=[arc_width1, arc_height1, arc_desired_width, arc_desired_height],
                        outputs=[arc_desired_height],
                    )

                    arc_apply = gr.Button(value="Apply").style(full_width=False)
                    arc_apply.click(
                        lambda w, h: solve_aspect_ratio(w, h, arc_width1, arc_height1),
                        inputs=[arc_width1, arc_height1, arc_width1, arc_height1],
                        outputs=[arc_desired_width, arc_desired_height],
                    )

                with gr.Row():
                    # Aspect Ratio options
                    arc_option_button = gr.Button(value="Aspect Ratio Options").style(
                        full_width=False
                    )
                    arc_options = gr.MultiCheckbox(
                        ["3:2", "4:3", "16:9", "1.85:1", "2.39:1"],
                        elem_id="arsp__arc_options",
                    )
                    arc_option_button.click(
                        arc_options.toggle_display, inputs=[arc_options]
                    )

                with gr.Row():
                    # Save custom aspect ratio button
                    arc_custom_save = gr.Button(value="Save Custom AR").style(
                        full_width=False
                    )
                    arc_custom_save.click(
                        lambda value, elem_id, ars: self.save_custom_aspect_ratio(
                            value, elem_id, ars
                        ),
                        inputs=[
                            arc_options.value,
                            arc_options.elem_id,
                            arc_options.choices,
                        ],
                    )

                with gr.Row():
                    # View saved aspect ratios button
                    arc_view_saved = gr.Button(value="View Saved ARs").style(
                        full_width=False
                    )
                    arc_view_saved.click(self.view_saved_aspect_ratios)

                with gr.Row():
                    # Delete custom aspect ratio button
                    arc_delete_custom = gr.Button(value="Delete Custom AR").style(
                        full_width=False
                    )
                    arc_delete_custom.click(
                        self.delete_custom_aspect_ratio, inputs=[arc_options]
                    )

            arc_show_calculator.click(
                arc_panel.toggle_display, inputs=[arc_panel]
            )
            arc_hide_calculator.click(
                arc_panel.toggle_display, inputs=[arc_panel]
            )

            arc_show_logic.click(
                self.toggle_reverse_logic,
                inputs=[
                    arc_hide_logic,
                    arc_show_logic,
                    arc_swap,
                    arc_get_image_dim,
                    arc_get_img2img_dim,
                    arc_get_txt2img_dim,
                    arc_round,
                    arc_show_calculator,
                    arc_hide_calculator,
                ],
                outputs=[
                    arc_hide_logic,
                    arc_show_logic,
                    arc_swap,
                    arc_get_image_dim,
                    arc_get_img2img_dim,
                    arc_get_txt2img_dim,
                    arc_round,
                    arc_show_calculator,
                    arc_hide_calculator,
                ],
            )
            arc_hide_logic.click(
                self.toggle_reverse_logic,
                inputs=[
                    arc_hide_logic,
                    arc_show_logic,
                    arc_swap,
                    arc_get_image_dim,
                    arc_get_img2img_dim,
                    arc_get_txt2img_dim,
                    arc_round,
                    arc_show_calculator,
                    arc_hide_calculator,
                ],
                outputs=[
                    arc_hide_logic,
                    arc_show_logic,
                    arc_swap,
                    arc_get_image_dim,
                    arc_get_img2img_dim,
                    arc_get_txt2img_dim,
                    arc_round,
                    arc_show_calculator,
                    arc_hide_calculator,
                ],
            )

            arc_round.click(
                self.toggle_rounding,
                inputs=[
                    arc_round,
                ],
                outputs=[
                    arc_round,
                ],
            )

            return [
                arc_show_logic,
                arc_hide_logic,
                arc_show_calculator,
                arc_hide_calculator,
                arc_swap,
                arc_width1,
                arc_height1,
                arc_desired_width,
                arc_desired_height,
                arc_ar_display,
                arc_calc_height,
                arc_apply,
                arc_option_button,
                arc_options,
                arc_custom_save,
                arc_view_saved,
                arc_delete_custom,
                arc_panel,
                arc_round,
                arc_get_img2img_dim,
                arc_get_txt2img_dim,
                arc_get_image_dim,
            ]

    def save_custom_aspect_ratio(self, value, elem_id, ars):
        if value and elem_id and ars:
            aspect_ratios = []
            labels = []
            aspect_ratios, labels, _ = parse_file("aspect_ratios.txt", float)

            if labels:
                if elem_id in labels:
                    index = labels.index(elem_id)
                    aspect_ratios[index] = value
                else:
                    aspect_ratios.append(value)
                    labels.append(elem_id)

            with open(
                Path(BASE_PATH, "aspect_ratios.txt"), "w", encoding="utf-8"
            ) as f:
                for ar, label in zip(aspect_ratios, labels):
                    f.write(f"{label},{ar}\n")

    def delete_custom_aspect_ratio(self, selected_options):
        options = selected_options.value
        labels, ars, _ = parse_file("aspect_ratios.txt", float)

        for option in options:
            if option in labels:
                index = labels.index(option)
                del labels[index]
                del ars[index]

        with open(Path(BASE_PATH, "aspect_ratios.txt"), "w", encoding="utf-8") as f:
            for label, ar in zip(labels, ars):
                f.write(f"{label},{ar}\n")

    def toggle_rounding(self, arc_round):
        global IMAGE_ROUNDING_MULTIPLIER
        if IMAGE_ROUNDING_MULTIPLIER == 1:
            IMAGE_ROUNDING_MULTIPLIER = 4
        else:
            IMAGE_ROUNDING_MULTIPLIER = 1
        arc_round.value = f"🔍 {IMAGE_ROUNDING_MULTIPLIER}x"

    def toggle_reverse_logic(self, *args):
        global is_reverse_logic_mode
        is_reverse_logic_mode = not is_reverse_logic_mode
        if is_reverse_logic_mode:
            args[0].visible = False
            args[1].visible = True
        else:
            args[0].visible = True
            args[1].visible = False

    def view_saved_aspect_ratios(self):
        content = Path(BASE_PATH, "aspect_ratios.txt").read_text(
            encoding="utf-8"
        )

        gr.interface.Interface(
            gr.Row(
                gr.Markdown(value="#### Saved Aspect Ratios"),
                gr.Textbox(
                    value=content,
                    elem_id="arsp__aspect_ratios_content_text",
                ),
            ),
            live=True,
        )

    def get_reduced_ratio(self, n, d):
        return get_reduced_ratio(n, d)

    def show_ar_input(self):
        if is_reverse_logic_mode:
            return gr.Row(
                gr.Text("AR:"),
                gr.TextInput(
                    placeholder="Aspect Ratio",
                    elem_id="arsp__arc_ar_input",
                    style="box-sizing: border-box; padding: 10px; width: 100%;"
                )
            )
        return []

    def pre_image(self, *, batch, module, **kwargs):
        self.read_aspect_ratios()
        self.read_resolutions()

    def load_defaults(self, *, batch, module, **kwargs):
        self.read_aspect_ratios()
        self.read_resolutions()
        for i in range(8):
            kwargs["image" + str(i)] = None

        if "txt2txt_image" in kwargs:
            kwargs["txt2txt_image"] = None
        if "img2img_inpaint_image" in kwargs:
            kwargs["img2img_inpaint_image"] = None

    def load_image(self, *, batch, module, **kwargs):
        self.read_aspect_ratios()
        self.read_resolutions()

    def get_panel_container(self, module):
        return module["panel_arcs"]

    def compute_aspect_ratio(self, aspect_ratio, width, height):
        aspect_ratio = self.aspect_ratios[aspect_ratio]

        if aspect_ratio > 1.0:
            height = width / aspect_ratio
        elif aspect_ratio < 1.0:
            width = height * aspect_ratio
        else:
            new_value = min([width, height])
            width, height = new_value, new_value

        return width, height

    def image2image(self, *, i2i_w, i2i_h, **kwargs):
        # check AR aspect_ratio
        ar = kwargs.get("ar")
        if ar is not None:
            i2i_w, i2i_h = self.compute_aspect_ratio(ar, i2i_w, i2i_h)

        return i2i_w, i2i_h

    def image2text(self, *, i2t_w, i2t_h, **kwargs):
        # check AR aspect_ratio
        ar = kwargs.get("ar")
        if ar is not None:
            i2t_w, i2t_h = self.compute_aspect_ratio(ar, i2t_w, i2t_h)

        return i2t_w, i2t_h

    def text2image(self, *, t2i_w, t2i_h, **kwargs):
        # check AR aspect_ratio
        ar = kwargs.get("ar")
        if ar is not None:
            t2i_w, t2i_h = self.compute_aspect_ratio(ar, t2i_w, t2i_h)

        return t2i_w, t2i_h

    def text2text(self, *, t2t_w, t2t_h, **kwargs):
        # check AR aspect_ratio
        ar = kwargs.get("ar")
        if ar is not None:
            t2t_w, t2t_h = self.compute_aspect_ratio(ar, t2t_w, t2t_h)

        return t2t_w, t2t_h
