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


def _nav(active_page: str = 'files') -> fx.FT:
    pages = [
        {
            'title': 'Files',
            'href': flask.url_for('index'),
            'active': active_page == 'files',
        },
        {
            'title': 'Locations',
            'href': flask.url_for('locations'),
            'active': active_page == 'locations',
        },
        {
            'title': 'Suffixes',
            'href': flask.url_for('suffixes'),
            'active': active_page == 'suffixes',
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
    return fx.Nav(cls='pt-3 row')(
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


def files_editable_note(file: m.File) -> str:
    return fx.to_xml(file.editable_note)


def files_list(files: list[m.File]) -> str:
    cards = []
    for i, f in enumerate(files):
        last_id = ''
        if i < 5:
            cards.append(f.card)
            last_id = f.id
        else:
            form = fx.Div(cls='card mb-2', hx_include='#card-filters', hx_post=flask.url_for('files_cards'),
                          hx_swap='outerHTML', hx_trigger='revealed')(
                fx.Input(name='after', type='hidden', value=last_id)
            )
            cards.append(form)
    return ''.join(map(fx.to_xml, cards))


def files_update_notes(file: m.File) -> str:
    return fx.to_xml(file.notes_control)


def index(files: list[m.File]) -> str:
    content_col = fx.Div(cls='col-12 col-sm-9 col-md-7 col-lg-6 col-xl-5 col-xxl-4')
    if files:
        content_col(
            fx.Form(hx_target='#video-cards', id='card-filters')(
                fx.Input(cls='form-control mb-2', hx_post=flask.url_for('files_cards'),
                         hx_trigger='search, keyup changed delay:300ms', name='q', placeholder='Search...',
                         type='search'),
                fx.Div(cls='form-check form-switch mb-2')(
                    fx.Input(cls='form-check-input', hx_post=flask.url_for('files_cards'), id='missing-notes-only',
                             name='missing-notes-only', type='checkbox'),
                    fx.Label(cls='form-check-Label', _for='missing-notes-only')('Only show files missing notes')
                )
            ),
            fx.Div(hx_include='previous form', hx_post=flask.url_for('files_cards'), hx_trigger='load',
                   id='video-cards'),
        )
    else:
        content_col(
            'No files found. Scan a ',
            fx.A(href=flask.url_for('locations'))('location'),
            ' and enable a ',
            fx.A(href=flask.url_for('suffixes'))('suffix'),
            ' first.'
        )
    return fx.to_xml(_base(
        _nav(active_page='files'),
        fx.Main(cls='pt-3 row')(content_col)
    ))


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
                fx.Table(cls='align-middle d-block table')(
                    m.Location.thead,
                    tbody
                )
            )
        )
    ))


def suffixes(suffix_counts: list[m.SuffixCount]) -> str:
    content_col = fx.Div(cls='col')
    if suffix_counts:
        content_col(
            fx.Table(cls='align-middle d-block table')(
                m.SuffixCount.thead,
                fx.Tbody(*(s.tr for s in suffix_counts))
            )
        )
    else:
        content_col(
            'No suffixes found. Scan a ',
            fx.A(href=flask.url_for('locations'))('location'),
            ' first.'
        )
    return fx.to_xml(_base(
        _nav(active_page='suffixes'),
        fx.Div(cls='pt-3 row')(content_col)
    ))
