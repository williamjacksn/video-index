import flask
import fastcore.xml as fx
import video_index.models as m
import video_index.versions as v


def _base(*args: fx.FT) -> fx.FT:
    return fx.Html(
        fx.Head(
            fx.Meta(charset='utf-8'),
            fx.Meta(name='viewport', content='width=device-width, initial-scale=1, shrink-to-fit=no'),
            fx.Title('Video Index'),
            fx.Link(
                href=flask.url_for('favicon'),
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
            fx.Div(cls='container-fluid')(*args),
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


def _nav(active_page: str = 'home') -> fx.FT:
    pages = [
        {
            'title': 'Home',
            'href': flask.url_for('index'),
            'active': active_page == 'home',
        },
        {
            'title': 'Locations',
            'href': flask.url_for('locations'),
            'active': active_page == 'locations',
        }
    ]
    nav_ul = fx.Ul(cls='nav nav-tabs')
    for p in pages:
        cls = 'nav-link'
        if p.get('active'):
            cls = f'{cls} active'
        nav_ul(
            fx.Li(cls='nav-item')(
                fx.A(cls=cls, href=p.get('href'))(p.get('title'))
            )
        )
    return fx.Div(cls='pt-3 row')(
        fx.Div(cls='col-12')(
            nav_ul
        )
    )


def favicon() -> str:
    svg_path = ('M0 1a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1zm4 0v6h8V1zm8 8H4v6h8zM1 '
                '1v2h2V1zm2 3H1v2h2zM1 7v2h2V7zm2 3H1v2h2zm-2 3v2h2v-2zM15 1h-2v2h2zm-2 3v2h2V4zm2 3h-2v2h2zm-2 '
                '3v2h2v-2zm2 3h-2v2h2z')
    content = fx.Svg(
        cls='bi bi-film',
        fill='currentColor',
        height='16',
        viewBox='0 0 16 16',
        width='16',
        xmlns='http://www.w3.org/2000/svg'
    )(
        fx.ft('path', d=svg_path)
    )
    return fx.to_xml((content,))


def index() -> str:
    return fx.to_xml(_base(_nav()))


def locations(locs: list[m.Location]) -> str:
    tbody = fx.Tbody()
    if locs:
        for loc in locs:
            tbody(loc.tr)
    else:
        tbody(
            fx.Tr(
                fx.Td(cls='text-center', colspan=m.Location.col_count)('No locations found')
            )
        )
    return fx.to_xml(_base(
        _nav(active_page='locations'),
        fx.Form(action=flask.url_for('locations_add'), cls='g-1 pt-3 row', method='post')(
            fx.Div(cls='col-auto')(
                fx.Input(cls='form-control', name='root-folder', required=True, type='text')
            ),
            fx.Div(cls='col-auto')(
                fx.Button(cls='btn btn-outline-primary', type='submit')(
                    fx.I(cls='bi-folder-plus'),
                    ' Add location')
            )
        ),
        fx.Div(cls='pt-3 row')(
            fx.Div(cls='col')(
                fx.Table(cls='d-block table')(
                    m.Location.thead,
                    tbody
                )
            )
        )
    ))
