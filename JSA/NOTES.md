# JSA notes

## `probe.py` mojibake boundary

`get_json_from_url` in `probe.py` was changed to decode JSA response bytes as UTF-8 explicitly before parsing JSON. The change is intended to prevent mojibake caused by implicit HTTP response decoding.

The program has not been tested after this change.
