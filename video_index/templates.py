import fastcore.xml as fx
import video_index.versions as v


def _base(body_content: tuple[fx.FT]) -> fx.FT:
    return fx.Html(
        fx.Head(
            fx.Meta(charset='utf-8'),
            fx.Meta(name='viewport', content='width=device-width, initial-scale=1, shrink-to-fit=no'),
            fx.Title('Video Index'),
            fx.Link(
                crossorigin='anonymous',
                href=f'https://unpkg.com/bootstrap@{v.bs}/dist/css/bootstrap.css',
                integrity='sha384-qAlWxD5RDF+aEdUc1Z7GR/tE4zYjX1Igo/LrIexlnzM6G63a6F1fXZWpZKSrSW86',
                rel='stylesheet'
            ),
            fx.Link(
                crossorigin='anonymous',
                href=f'https://unpkg.com/bootstrap-icons@{v.bi}/font/bootstrap-icons.css',
                integrity='sha384-tViUnnbYAV00FLIhhi3v/dWt3Jxw4gZQcNoSCxCIFNJVCx7/D55/wXsrNIRANwdD',
                rel='stylesheet'
            )
        ),
        fx.Body(
            fx.Div(
                fx.Div(
                    fx.Div(
                        *body_content,
                        klass='col'
                    ),
                    klass='row'
                ),
                klass='container-fluid'
            ),
            fx.Script(
                crossorigin='anonymous',
                integrity='sha384-5xO2n1cyGKAe630nacBqFQxWoXjUIkhoc/FxQrWM07EIZ3TuqkAsusDeyPDOIeid',
                src=f'https://unpkg.com/bootstrap@{v.bs}/dist/js/bootstrap.bundle.js'
            ),
            fx.Script(
                crossorigin='anonymous',
                integrity='sha384-oeUn82QNXPuVkGCkcrInrS1twIxKhkZiFfr2TdiuObZ3n3yIeMiqcRzkIcguaof1',
                src=f'https://unpkg.com/htmx.org@{v.hx}/dist/htmx.js'
            )
        ),
        lang='en'
    )


def index():
    content = fx.Div('Hello!'),
    return fx.to_xml(_base(content))
