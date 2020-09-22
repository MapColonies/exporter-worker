schema = {
    "type": "object",
    "properties": {
        "filename": {"type": "string"},
        "url": {"type": "string"},
        "bbox": {"type": "array",
                 "items": {
                     "type": "number"
                 }
                 }
    }
}

