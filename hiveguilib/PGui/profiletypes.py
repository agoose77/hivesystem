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
  ("parameter", "Default, with value"),
  ("minimal", "Minimal"),
  ("parameter2", "Minimal, with value"),
  ("input", "Input"),
  ("parameter_input", "Input, with value"),
  ("output", "Output"),
  ("parameter_output", "Output, with value"),
  ("full", "Full"),
]

profiles_seg_pushbuffer = [
  ("default", "Minimal"),
  ("parameter", "Minimal, with value"),
  ("input", "Input"),
  ("parameter_input", "Input, with value"),
  ("full", "Full"),
]

profiles_seg_pullbuffer = [
  ("default", "Minimal"),
  ("parameter", "Minimal, with value"),
  ("output", "Output"),
  ("parameter_output", "Output, with value"),
  ("full", "Full"),
]

profiletypes = {
  "drone": [("default","Minimal")],
  "spydermap": [("default","Minimal")],
  "worker" : profiles_worker,
  "segment": profiles_segment,
  "segment-variable": profiles_seg_variable,
  "segment-pushbuffer": profiles_seg_pushbuffer,
  "segment-pullbuffer": profiles_seg_pullbuffer,
}
