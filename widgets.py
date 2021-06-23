from wtforms.widgets import html_params


def radio_input_widget(field, *args, **kwargs):
    html = ['<div class="radio-input-wrapper">']
    for id_, choice_label in field.choices:
        html.extend(
            [   '<label>',
                    f'<input type="radio" name="{field.name}" value="{id_}" required>',
                    f'<span>{choice_label}</span>'
                '</label>'
            ]
        )
    html.append("</div>")
    return "".join(html)
