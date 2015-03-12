profiles_worker = [
    ("default", "Default"),
    ("default_evio", "Default, with event streams"),
    ("plain", "Plain"),
    ("plain_evio", "Plain, with event streams"),
]

profiles_segment = [
    ("default", "Minimal"),
    ("full", "Full"),
]

profiles_seg_variable = [
    ("default", "Default"),
    ("Parameter", "Default, with value"),
    ("minimal", "Minimal"),
    ("parameter2", "Minimal, with value"),
    ("input", "Input"),
    ("parameter_input", "Input, with value"),
    ("Output", "Output"),
    ("parameter_output", "Output, with value"),
    ("full", "Full"),
]

profiles_seg_pushbuffer = [
    ("default", "Minimal"),
    ("Parameter", "Minimal, with value"),
    ("input", "Input"),
    ("parameter_input", "Input, with value"),
    ("full", "Full"),
]

profiles_seg_pullbuffer = [
    ("default", "Minimal"),
    ("Parameter", "Minimal, with value"),
    ("Output", "Output"),
    ("parameter_output", "Output, with value"),
    ("full", "Full"),
]

profiletypes = {
    "drone": [("default", "Minimal")],
    "spydermap": [("default", "Minimal")],
    "worker": profiles_worker,
    "segment": profiles_segment,
    "segment-variable": profiles_seg_variable,
    "segment-pushbuffer": profiles_seg_pushbuffer,
    "segment-pullbuffer": profiles_seg_pullbuffer,
}
