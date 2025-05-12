import flask
import htpy
import video_index.models as m
import video_index.versions as v


def _base(content: htpy.Node) -> htpy.Element:
    return htpy.html(lang="en")[
        htpy.head[
            htpy.meta(charset="utf-8"),
            htpy.meta(
                name="viewport",
                content="width=device-width, initial-scale=1, shrink-to-fit=no",
            ),
            htpy.title["Video Index"],
            htpy.link(href=flask.url_for("favicon"), rel="icon"),
            htpy.link(
                crossorigin="anonymous",
                href=f"https://unpkg.com/bootstrap@{v.bs}/dist/css/bootstrap.css",
                rel="stylesheet",
            ),
            htpy.link(
                crossorigin="anonymous",
                href=f"https://unpkg.com/bootstrap-icons@{v.bi}/font/bootstrap-icons.css",
                rel="stylesheet",
            ),
        ],
        htpy.body[
            htpy.div(".top-0.end-0.m-3.position-absolute.z-n1")[
                htpy.small(".badge.text-bg-dark")[
                    htpy.span(".d-inline.d-sm-none")["xs"],
                    htpy.span(".d-none.d-sm-inline.d-md-none")["sm"],
                    htpy.span(".d-none.d-md-inline.d-lg-none")["md"],
                    htpy.span(".d-none.d-lg-inline.d-xl-none")["lg"],
                    htpy.span(".d-none.d-xl-inline.d-xxl-none")["xl"],
                    htpy.span(".d-none.d-xxl-inline")["xxl"],
                ],
            ],
            htpy.div(".container-fluid")[content],
            htpy.script(
                crossorigin="anonymous",
                src=f"https://unpkg.com/bootstrap@{v.bs}/dist/js/bootstrap.bundle.js",
            ),
            htpy.script(
                crossorigin="anonymous",
                src=f"https://unpkg.com/htmx.org@{v.hx}/dist/htmx.js",
            ),
        ],
    ]


def _nav(active_page: str = "files") -> htpy.Element:
    pages = [
        {
            "title": "Files",
            "href": flask.url_for("index"),
            "active": active_page == "files",
        },
        {
            "title": "Locations",
            "href": flask.url_for("locations"),
            "active": active_page == "locations",
        },
        {
            "title": "Suffixes",
            "href": flask.url_for("suffixes"),
            "active": active_page == "suffixes",
        },
    ]
    page_elements = []
    for p in pages:
        if p.get("active"):
            cls = ".active.nav-link"
        else:
            cls = ".nav-link"
        page_elements.append(
            htpy.li(".nav-item")[htpy.a(cls, href=p.get("href"))[p.get("title")]]
        )
    return htpy.nav(".align-items-center.pt-3.row")[
        htpy.div(".col-12")[htpy.ul(".nav.nav-tabs")[page_elements],]
    ]


def favicon() -> str:
    svg_path = (
        "M0 1a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1zm4 0v6h8V1zm8 8H4v6h8zM1 "
        "1v2h2V1zm2 3H1v2h2zM1 7v2h2V7zm2 3H1v2h2zm-2 3v2h2v-2zM15 1h-2v2h2zm-2 3v2h2V4zm2 3h-2v2h2zm-2 "
        "3v2h2v-2zm2 3h-2v2h2z"
    )
    content = htpy.svg(
        ".bi.bi-film",
        fill="currentColor",
        height="16",
        viewBox="0 0 16 16",
        width="16",
        xmlns="http://www.w3.org/2000/svg",
    )[htpy.path(d=svg_path)]
    return str(content)


def files_editable_note(file: m.File) -> str:
    return str(file.editable_note)


def files_list(files: list[m.File]) -> str:
    if len(files) < 1:
        return str(
            htpy.div(".col.pb-3")[
                "No files found. Adjust your filters or scan a ",
                htpy.a(href=flask.url_for("locations"))["location"],
                " and enable a ",
                htpy.a(href=flask.url_for("suffixes"))["suffix"],
                " first.",
            ]
        )

    cards = []
    last_path = ""
    for i, f in enumerate(files):
        if i < 5:
            cards.append(f.card)
            last_path = f.file_path
        else:
            cards.append(
                htpy.div(
                    ".col.pb-3",
                    hx_include="#card-filters",
                    hx_post=flask.url_for("files_cards", after=last_path),
                    hx_swap="outerHTML",
                    hx_trigger="revealed",
                )
            )
    return str(htpy.fragment[cards])


def files_update_notes(file: m.File) -> str:
    return str(file.notes_control)


def index() -> str:
    return str(
        _base(
            [
                _nav(active_page="files"),
                htpy.form(
                    "#card-filters.align-items-center.pt-3.row",
                    hx_target="#video-cards",
                )[
                    htpy.div(".col-auto")[
                        htpy.input(
                            ".form-control.mb-2",
                            hx_post=flask.url_for("files_cards"),
                            hx_trigger="search, keyup changed delay:300ms",
                            name="q",
                            placeholder="Search...",
                            type="search",
                        )
                    ],
                    htpy.div(".col-auto")[
                        htpy.div(".form-check.form-switch.mb-2")[
                            htpy.input(
                                "#missing-notes-only.form-check-input",
                                hx_post=flask.url_for("files_cards"),
                                name="missing-notes-only",
                                type="checkbox",
                            ),
                            htpy.label(".form-check-Label", for_="missing-notes-only")[
                                "Only show files missing notes"
                            ],
                        ]
                    ],
                ],
                htpy.div(
                    "#video-cards.pt-3.row.row-cols-1.row-cols-sm-2.row-cols-lg-3.row-cols-xxl-4",
                    hx_include="#card-filters",
                    hx_post=flask.url_for("files_cards"),
                    hx_trigger="load",
                ),
            ]
        )
    )


def locations(locs: list[m.Location]) -> str:
    trs = []
    if locs:
        for loc in locs:
            trs.append(loc.tr)
    else:
        trs.append(
            htpy.tr[
                htpy.td(".text-center", colspan=m.Location.col_count)[
                    "No locations found"
                ]
            ]
        )
    return str(
        _base(
            [
                _nav(active_page="locations"),
                htpy.form(
                    ".g-1.pt-3.row",
                    action=flask.url_for("locations_add"),
                    method="post",
                )[
                    htpy.div(".col-auto")[
                        htpy.input(
                            ".form-control",
                            name="root-folder",
                            required=True,
                            type="text",
                        )
                    ],
                    htpy.div(".col-auto")[
                        htpy.button(".btn.btn-outline-primary", type="submit")[
                            htpy.i(".bi-folder-plus"),
                            " Add location",
                        ]
                    ],
                ],
                htpy.div(".pt-3.row")[
                    htpy.div(".col")[
                        htpy.table(".align-middle.d-block.table")[
                            m.Location.thead, htpy.tbody[trs]
                        ]
                    ]
                ],
            ]
        )
    )


def suffixes(suffix_counts: list[m.SuffixCount]) -> str:
    if suffix_counts:
        content = htpy.table(".align-middle.d-block.table")[
            m.SuffixCount.thead, htpy.tbody[[s.tr for s in suffix_counts]]
        ]
    else:
        content = [
            "No suffixes found. Scan a ",
            htpy.a(href=flask.url_for("locations"))["location"],
            " first.",
        ]
    return str(
        _base(
            [
                _nav(active_page="suffixes"),
                htpy.div(".pt-3.row")[htpy.div(".col")[content]],
            ]
        )
    )
