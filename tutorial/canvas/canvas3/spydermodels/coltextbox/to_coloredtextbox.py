from coloredtextbox import coloredtextbox


def to_coloredtextbox(ctb):
    textcolor = ctb.textcolor.r / 255.0, ctb.textcolor.g / 255.0, ctb.textcolor.b / 255.0, ctb.textcolor.a / 255.0
    boxcolor = ctb.boxcolor.r / 255.0, ctb.boxcolor.g / 255.0, ctb.boxcolor.b / 255.0, ctb.boxcolor.a / 255.0
    return coloredtextbox(
        ctb.text,
        textcolor,
        ctb.box.x,
        ctb.box.y,
        ctb.box.sizex,
        ctb.box.sizey,
        ctb.box.mode,
        boxcolor,
    )