from wtforms.widgets import html_params


def radio_input(field, *args, **kwargs):
    html = ['<div class="radio-input-wrapper">', f"<div>{field.label}</div>"]
    for choice in field.choices:
        html.extend(
            [
                f"<span>{choice}</span>"
                f'<input type="radio" name="{field.name}" value="{choice}" required>',
            ]
        )
    html.append("</div>")
    return "".join(html)
