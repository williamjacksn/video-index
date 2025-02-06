import fastcore.xml as fx
import video_index.versions as v


def _base(body_content: tuple[fx.FT]) -> fx.FT:
    return fx.Html(
        fx.Head(
            fx.Meta(charset='utf-8'),
            fx.Meta(name='viewport', content='width=device-width, initial-scale=1, shrink-to-fit=no'),
            fx.Title('Video Index'),
            fx.Link(
                href='/favicon.svg',
                rel='icon'
            ),
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
            fx.Div(cls='container-fluid')(*body_content),
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


def favicon():
    content = fx.Svg(
        cls='bi bi-film',
        fill='currentColor',
        height='16',
        viewBox='0 0 16 16',
        width='16',
        xmlns='http://www.w3.org/2000/svg'
    )(
        fx.ft(
            'path',
            d='M0 1a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1zm4 0v6h8V1zm8 8H4v6h8zM1 1v2h2V1zm2 3H1v2h2zM1 7v2h2V7zm2 3H1v2h2zm-2 3v2h2v-2zM15 1h-2v2h2zm-2 3v2h2V4zm2 3h-2v2h2zm-2 3v2h2v-2zm2 3h-2v2h2z'
        )
    )
    return fx.to_xml((content,))


def index():
    content = fx.Div(cls='pt-3 row')(
        fx.Div(cls='col')(
            fx.H1(
                fx.I(cls='bi-person-raised-hand'),
                ' Hello!'
            )
        )
    )
    return fx.to_xml(_base((content,)))
