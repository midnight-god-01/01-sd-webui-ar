import contextlib
from pathlib import Path
import gradio as gr
import modules.scripts as scripts
from modules.ui_components import ToolButton
from math import gcd

# Define icons
BASE_PATH = scripts.basedir()
CALCULATOR_SYMBOL = "\U0001F4D0"  # 📐
SWITCH_VALUES_SYMBOL = "\U000021C5"  # ⇅
DIMENSIONS_SYMBOL = "\u2B07\ufe0f"  # ⬇️
IMAGE_DIMENSIONS_SYMBOL = "\U0001F5BC"  # 🖼
REVERSE_LOGIC_SYMBOL = "\U0001F503"  # 🔃
ROUND_SYMBOL = "\U0001F50D"  # 🔍

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

def write_js_titles_file(button_titles):
    filename = Path(BASE_PATH, "javascript", "button_titles.js")
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
            elem_id=f'{"img" if is_img2img else "txt"}2img_container_aspect_ratio'
        ):
            self.aspect_ratios = list(map(float, self.aspect_ratios))
            aspect_ratio_labels = self.aspect_ratio_labels
            self.ar_button_titles = [
                self.AR_NAME,
                self.AR_CALCULATOR,
                self.AR_SWITCH_VALUES,
                self.AR_DIMENSIONS,
                self.AR_IMAGE_DIMENSIONS,
                self.AR_REVERSE_LOGIC,
                self.AR_ROUND,
            ]
            aspect_ratio_labels.extend(self.ar_button_titles)

            self.aspects, _ = gr.radio(
                aspect_ratio_labels,
                default=self.aspect_ratios[0],
                label="Aspect ratio",
                elem_id="aspect_ratio",
            )

            gr.html(f'<br><span class="icon">{DIMENSIONS_SYMBOL}</span><br>')

            self.dimensions, self.ar_calc = gr.columns(
                2,
                [
                    gr.textbox(
                        aspect_ratio_labels[
                            aspect_ratio_labels.index(
                                self.AR_CALCULATOR
                            )
                        ],
                        default="",
                        label="Width",
                        elem_id="ar_width",
                    ),
                    gr.textbox(
                        aspect_ratio_labels[
                            aspect_ratio_labels.index(
                                self.AR_CALCULATOR
                            )
                        ],
                        default="",
                        label="Height",
                        elem_id="ar_height",
                    ),
                ],
            )

            gr.button(
                "Apply",
                elem_id="calculate_aspect_ratio",
                width=250,
                outline=True,
                primary=True,
            )

            ar_options, _ = gr.columns(
                2,
                [
                    gr.checkbox(
                        aspect_ratio_labels[
                            aspect_ratio_labels.index(
                                self.AR_SWITCH_VALUES
                            )
                        ],
                        default=False,
                        label="Switch values",
                        elem_id="ar_switch_values",
                    ),
                    gr.checkbox(
                        aspect_ratio_labels[
                            aspect_ratio_labels.index(
                                self.AR_DIMENSIONS
                            )
                        ],
                        default=False,
                        label="Change dimensions",
                        elem_id="ar_change_dimensions",
                    ),
                ],
            )

            gr.html(f'<br><span class="icon">{REVERSE_LOGIC_SYMBOL}</span><br>')

            gr.button(
                "Apply",
                elem_id="reverse_logic_aspect_ratio",
                width=250,
                outline=True,
                primary=True,
            )

            gr.button(
                "Reset",
                elem_id="reset_aspect_ratio",
                width=250,
                secondary=True,
                outline=True,
            )

            gr.html(f'<br><span class="icon">{IMAGE_DIMENSIONS_SYMBOL}</span><br>')

            ar_options, _ = gr.columns(
                2,
                [
                    gr.checkbox(
                        aspect_ratio_labels[
                            aspect_ratio_labels.index(
                                self.AR_IMAGE_DIMENSIONS
                            )
                        ],
                        default=False,
                        label="Use image dimensions",
                        elem_id="ar_use_image_dimensions",
                    ),
                    gr.checkbox(
                        aspect_ratio_labels[
                            aspect_ratio_labels.index(
                                self.AR_REVERSE_LOGIC
                            )
                        ],
                        default=False,
                        label="Reverse logic",
                        elem_id="ar_reverse_logic",
                    ),
                ],
            )

            gr.button(
                "Apply",
                elem_id="ar_image_dimensions_aspect_ratio",
                width=250,
                outline=True,
                primary=True,
            )

            gr.html(f'<br><span class="icon">{ROUND_SYMBOL}</span><br>')

            gr.button(
                "Apply",
                elem_id="ar_round_aspect_ratio",
                width=250,
                outline=True,
                primary=True,
            )

            gr.button(
                "Reset",
                elem_id="reset_aspect_ratio",
                width=250,
                secondary=True,
                outline=True,
            )

            gr.button(
                "Write to file",
                elem_id="write_aspect_ratios",
                width=250,
                secondary=True,
                outline=True,
            )

            gr.html(
                f'<br><span class="icon">{CALCULATOR_SYMBOL}</span><br><br>'
            )

            gr.button(
                "Reset",
                elem_id="reset_calculator",
                width=250,
                secondary=True,
                outline=True,
            )

        return self

    def run(self, img, txt2img, txt):
        if self.ar_button_titles.index(self.ar_button) < 4:
            if self.ar_button_titles.index(self.ar_button) == 0:
                if self.ar_button == self.aspect_ratios[0]:
                    return txt2img if txt else img

            if self.ar_button == self.aspect_ratios[0]:
                new_ar = ResButton(self.ar_calc).reset()
                ar = [
                    new_ar[0] / new_ar[1],
                    solve_aspect_ratio(
                        new_ar[0], new_ar[1], 16, 9
                    ),
                ]
                img.resize(ar)
            elif self.ar_button == self.aspect_ratios[1]:
                new_ar = ResButton(self.ar_calc).reset()
                ar = [
                    new_ar[0] / new_ar[1],
                    solve_aspect_ratio(
                        new_ar[0], new_ar[1], 4, 3
                    ),
                ]
                img.resize(ar)
            elif self.ar_button == self.aspect_ratios[2]:
                new_ar = ResButton(self.ar_calc).reset()
                ar = [
                    new_ar[0] / new_ar[1],
                    solve_aspect_ratio(
                        new_ar[0], new_ar[1], 3, 2
                    ),
                ]
                img.resize(ar)
            elif self.ar_button == self.aspect_ratios[3]:
                new_ar = ResButton(self.ar_calc).reset()
                ar = [
                    new_ar[0] / new_ar[1],
                    solve_aspect_ratio(
                        new_ar[0], new_ar[1], 1, 1
                    ),
                ]
                img.resize(ar)
            return txt2img if txt else img
        else:
            if self.ar_button == self.aspect_ratios[4]:
                if not txt:
                    return img
                if self.ar_button == self.aspect_ratios[4]:
                    if txt2img:
                        return img
                    return txt2img
            if self.ar_button == self.aspect_ratios[5]:
                if not txt:
                    return img
                if self.ar_button == self.aspect_ratios[5]:
                    if txt2img:
                        return img
                    return txt2img
            if self.ar_button == self.aspect_ratios[6]:
                new_ar = ResButton(self.ar_calc).reset()
                ar = [
                    new_ar[0] / new_ar[1],
                    solve_aspect_ratio(
                        new_ar[0], new_ar[1], 4, 3
                    ),
                ]
                if not txt:
                    return img.resize(ar)
                if self.ar_button == self.aspect_ratios[6]:
                    if txt2img:
                        return img.resize(ar)
                    if self.switch_values:
                        return txt2img.resize(ar)
                    return img
            return txt2img if txt else img

    def ar_switch(self, w, h):
        return [h, w]

    def ar_change(self, w, h):
        return [w, h]

    def ar_reverse(self, w, h):
        return [h, w]

    def ar_round(self, w, h):
        return [w, h]

class ScriptChooser(scripts.Script):
    def title(self):
        return "Script chooser"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        scripts.read_scripts()
        return scripts.scripts

    def run(self, img, txt2img, txt):
        return img

class Titlebar(ToolButton):
    def __init__(self, value="", **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def run(self):
        return self.value

class AspectRatio(gr.Interface):
    def __init__(self):
        self.AR_NAME = "Aspect ratio picker"
        self.AR_CALCULATOR = "Calculator"
        self.AR_SWITCH_VALUES = "Switch values"
        self.AR_DIMENSIONS = "Change dimensions"
        self.AR_IMAGE_DIMENSIONS = "Use image dimensions"
        self.AR_REVERSE_LOGIC = "Reverse logic"
        self.AR_ROUND = "Round"

        self.add_titlebar()
        self.add_footer()

    def add_titlebar(self):
        titlebar = Titlebar(
            "Aspect Ratio Picker", elem_id="aspect_ratio_titlebar"
        )
        self.add_elements([titlebar])

    def add_footer(self):
        footer = gr.Row(
            [
                gr.Column(
                    [
                        gr.Button(
                            "Reset",
                            elem_id="reset_ar",
                            width=250,
                            secondary=True,
                            outline=True,
                        )
                    ]
                ),
                gr.Column(
                    [
                        gr.Button(
                            "Write to file",
                            elem_id="write_ar",
                            width=250,
                            secondary=True,
                            outline=True,
                        )
                    ]
                ),
            ],
            elem_id="ar_footer",
        )
        self.add_elements([footer])

    def get_button_titles(self):
        button_titles = [
            ["1:1", "16:9", "4:3", "3:2"],
            [
                self.AR_NAME,
                self.AR_CALCULATOR,
                self.AR_SWITCH_VALUES,
                self.AR_DIMENSIONS,
                self.AR_IMAGE_DIMENSIONS,
                self.AR_REVERSE_LOGIC,
                self.AR_ROUND,
            ],
        ]
        return button_titles

def add_aspect_ratio_ui(scripts, AR_NAME, AR_CALCULATOR, AR_SWITCH_VALUES, AR_DIMENSIONS, AR_IMAGE_DIMENSIONS, AR_REVERSE_LOGIC, AR_ROUND):
    titlebar = AspectRatio(
        AR_NAME, AR_CALCULATOR, AR_SWITCH_VALUES, AR_DIMENSIONS, AR_IMAGE_DIMENSIONS, AR_REVERSE_LOGIC, AR_ROUND, scripts
    )
    titlebar.display()
    return titlebar


@contextlib.contextmanager
def no_stdout():
    with open(os.devnull, "w") as fnull:
        with contextlib.redirect_stdout(fnull):
            yield


aspect_ratio_script = AspectRatioScript()
aspect_ratio_script.display()

if __name__ == "__main__":
    gr.interface.Interface(run_multiple=True).launch()
