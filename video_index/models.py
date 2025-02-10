import datetime
import fastcore.xml as fx
import flask
import fort
import logging
import pathlib
import secrets
import zoneinfo

log = logging.getLogger(__name__)
tz = zoneinfo.ZoneInfo('America/Chicago')


class File:
    def __init__(self, file_path: pathlib.Path, file_id: str, notes: str):
        self.file_path = file_path
        self.id = file_id
        self.notes = notes

    @property
    def card(self) -> fx.FT:
        return fx.Div(cls='col pb-3')(
            fx.Div(cls='card h-100')(
                fx.Video(cls='card-img-top', controls=True, preload='metadata',
                         src=flask.url_for('files_get', file_id=self.id)),
                fx.Div(cls='card-body')(
                    fx.H5(cls='card-title')(self.file_path.name),
                    fx.H6(cls='card-subtitle mb-2 text-body-secondary')(
                        fx.Small(self.file_path.parent)
                    ),
                    self.notes_control,
                )
            )
        )

    @property
    def editable_note(self) -> fx.FT:
        return fx.Form(hx_post=flask.url_for('files_update_notes', file_id=self.id), hx_swap='outerHTML')(
            fx.Input(name='file-id', type='hidden', value=self.id),
            fx.Textarea(cls='form-control mb-2', name='notes')(self.notes),
            fx.Button(cls='btn btn-outline-primary', type='submit')('Save')
        )

    @property
    def notes_control(self) -> fx.FT:
        return fx.P(cls='card-text', hx_get=flask.url_for('files_editable_note', file_id=self.id),
                    hx_swap='outerHTML', role='button')(
            self.notes or '(No notes)'
        )


class Location:
    col_count: int = 4
    thead: fx.FT = fx.Thead(
        fx.Tr(
            fx.Th('Root folder'),
            fx.Th('Last scan started'),
            fx.Th('Last scan completed'),
            fx.Th()
        )
    )

    def __init__(self, root_folder: pathlib.Path, last_scan_started_at: datetime.datetime, last_scan_completed_at: datetime.datetime):
        self.root_folder = root_folder
        self.last_scan_started_at = last_scan_started_at
        self.last_scan_completed_at = last_scan_completed_at

    @property
    def tr(self) -> fx.FT:
        return fx.Tr()(
            fx.Td(fx.Code(self.root_folder)),
            fx.Td(self.last_scan_started_at.astimezone(tz) if self.last_scan_started_at else ''),
            fx.Td(self.last_scan_completed_at.astimezone(tz) if self.last_scan_completed_at else ''),
            fx.Td(
                fx.Button(cls='btn btn-outline-primary btn-sm', hx_post=flask.url_for('locations_scan'),
                          name='root-folder', title='Scan now', value=self.root_folder, type='button')(
                    fx.I(cls='bi-search')
                )
            )
        )


class SuffixCount:
    thead: fx.FT = fx.Thead(
        fx.Tr(
            fx.Th('Suffix'),
            fx.Th('Scanned files'),
            fx.Th(cls='text-center')('Enabled')
        )
    )

    def __init__(self, suffix: str, count: int, enabled: bool):
        self.suffix = suffix
        self.count = count
        self.enabled = enabled

    @property
    def tr(self) -> fx.FT:
        return fx.Tr(
            fx.Td(fx.Code(self.suffix)),
            fx.Td(cls='text-end')(self.count),
            fx.Td(cls='ps-4 text-center')(
                fx.Div(cls='form-check form-switch')(
                    fx.Input(checked=self.enabled, cls='form-check-input', hx_post=flask.url_for('suffixes_enable'),
                             name=f'enabled{self.suffix}', type='checkbox'),
                )
            )
        )


class VideoIndexModel(fort.SQLiteDatabase):
    _version: int = None

    def _table_exists(self, table_name: str) -> bool:
        log.debug(f'Searching database for table {table_name!r}')
        sql = '''
            select name
            from sqlite_master
            where type = 'table'
            and name = :name
        '''
        params = {
            'name': table_name,
        }
        t = self.q_val(sql, params)
        if t and t == table_name:
            log.debug(f'Table {table_name!r} found')
            return True
        log.debug(f'Table {table_name!r} not found')
        return False

    def files_add(self, file_path: pathlib.Path):
        sql = '''
            insert into files (
                file_path, id, suffix, last_scanned_at
            ) values (
                :file_path, :id, :suffix, :last_scanned_at
            ) on conflict (file_path) do update set
                scanned = 1, last_scanned_at = excluded.last_scanned_at
        '''
        params = {
            'file_path': str(file_path),
            'id': secrets.token_urlsafe(8),
            'suffix': file_path.suffix,
            'last_scanned_at': datetime.datetime.now(datetime.UTC).isoformat(),
        }
        self.u(sql, params)

    def files_get(self, file_id: str) -> File|None:
        sql = '''
            select file_path, id, notes
            from files
            where id = :id
        '''
        params = {
            'id': file_id,
        }
        f = self.q_one(sql, params)
        if f:
            return File(pathlib.Path(f['file_path']).resolve(), f['id'], f['notes'])

    def files_list(self, after: str = '', missing_notes_only: bool = False, q: str = None) -> list[File]:
        where_clause = 'f.scanned = 1 and s.enabled = 1 and f.file_path > :after'
        if missing_notes_only:
            where_clause = f'{where_clause} and length(f.notes) = 0'
        if q:
            where_clause = f'''
                {where_clause} and
                instr(lower(f.file_path || ' ' || f.notes), lower(:q)) > 0
            '''
        sql = f'''
            select f.file_path, f.id, f.last_scanned_at, f.notes
            from files f
            join suffixes s on s.suffix = f.suffix
            where {where_clause}
            order by f.file_path limit 6
        '''
        params = {
            'after': after,
            'q': q,
        }
        return [
            File(pathlib.Path(row['file_path']).resolve(), row['id'], row['notes'])
            for row in self.q(sql, params)
        ]

    def files_update_notes(self, file_id: str, notes: str):
        sql = '''
            update files
            set notes = :notes
            where id = :id
        '''
        params = {
            'id': file_id,
            'notes': notes,
        }
        self.u(sql, params)

    def locations_add(self, root_folder: str):
        sql = '''
            insert into locations (root_folder) values (:root_folder)
            on conflict (root_folder) do nothing
        '''
        params = {
            'root_folder': root_folder,
        }
        self.u(sql, params)

    def locations_get(self, root_folder: pathlib.Path) -> Location|None:
        sql = '''
            select root_folder, last_scan_started_at, last_scan_completed_at
            from locations
            where root_folder = :root_folder
        '''
        params = {
            'root_folder': str(root_folder),
        }
        row = self.q_one(sql, params)
        if row:
            return Location(
                pathlib.Path(row['root_folder']).resolve(),
                datetime.datetime.fromisoformat(row['last_scan_started_at']) if row['last_scan_started_at'] else None,
                datetime.datetime.fromisoformat(row['last_scan_completed_at']) if row['last_scan_completed_at'] else None
            )

    def locations_list(self) -> list[Location]:
        sql = '''
            select root_folder, last_scan_started_at, last_scan_completed_at
            from locations
            order by root_folder
        '''
        return [
            Location(
                pathlib.Path(row['root_folder']).resolve(),
                datetime.datetime.fromisoformat(row['last_scan_started_at']) if row['last_scan_started_at'] else None,
                datetime.datetime.fromisoformat(row['last_scan_completed_at']) if row['last_scan_completed_at'] else None
            )
            for row in self.q(sql)
        ]

    def locations_scan_complete(self, root_folder: pathlib.Path):
        sql = '''
            update locations
            set last_scan_completed_at = :last_scan_completed_at
            where root_folder = :root_folder
        '''
        params = {
            'root_folder': str(root_folder),
            'last_scan_completed_at': datetime.datetime.now(datetime.UTC).isoformat(),
        }
        self.u(sql, params)
        sql = '''
            delete from files
            where instr(file_path, :root_folder) = 1
            and scanned = 0
        '''
        self.u(sql, params)

    def locations_scan_start(self, root_folder: pathlib.Path):
        sql = '''
            update locations
            set last_scan_started_at = :last_scan_started_at, last_scan_completed_at = null
            where root_folder = :root_folder
        '''
        params = {
            'root_folder': str(root_folder),
            'last_scan_started_at': datetime.datetime.now(datetime.UTC).isoformat(),
        }
        self.u(sql, params)
        sql = '''
            update files
            set scanned = 0
            where instr(file_path, :root_folder) = 1
        '''
        self.u(sql, params)

    def migrate(self):
        log.info(f'Database schema version is {self.version}')
        if self.version < 1:
            log.info('Migrating to database schema version 1')
            self.u('''
                create table schema_versions (
                    schema_version integer,
                    migration_applied_at text
                )
            ''')
            self.u('''
                create table locations (
                    root_folder text primary key,
                    last_scan_started_at text,
                    last_scan_completed_at text
                )
            ''')
            self.u('''
                create table files (
                    file_path text primary key,
                    id text not null,
                    suffix text not null,
                    scanned integer not null default 1,
                    last_scanned_at text not null,
                    notes text not null default ''
                )
            ''')
            self.u('''
                create table suffixes (
                    suffix text primary key,
                    enabled integer not null default 0
                )
            ''')
            self.version = 1

    def suffixes_count(self) -> list[SuffixCount]:
        sql = '''
            with c as (
                select suffix, count(*) file_count
                from files
                where length(suffix) > 0
                group by suffix
            )
            select c.suffix, c.file_count, coalesce(s.enabled, 0) as enabled
            from c
            left join suffixes s on s.suffix = c.suffix
            order by c.suffix
        '''
        return [SuffixCount(row['suffix'], row['file_count'], bool(row['enabled'])) for row in self.q(sql)]

    def suffixes_enable(self, suffix: str, enabled: bool):
        sql = '''
            insert into suffixes (suffix, enabled) values (:suffix, :enabled)
            on conflict (suffix) do update set enabled = excluded.enabled
        '''
        params = {
            'suffix': suffix,
            'enabled': int(enabled),
        }
        self.u(sql, params)

    @property
    def version(self) -> int:
        if self._version is None:
            if self._table_exists('schema_versions'):
                sql = '''
                    select schema_version
                    from schema_versions
                    order by migration_applied_at desc
                    limit 1
                '''
                self._version = self.q_val(sql) or 0
            else:
                self._version = 0
        return self._version

    @version.setter
    def version(self, value: int):
        sql = '''
            insert into schema_versions (
                schema_version, migration_applied_at
            ) values (
                :schema_version, :migration_applied_at
            )
        '''
        params = {
            'migration_applied_at': datetime.datetime.now(tz=datetime.UTC).isoformat(),
            'schema_version': value,
        }
        self.u(sql, params)
        self._version = value


def get_model() -> VideoIndexModel:
    db_path = pathlib.Path().resolve() / '.local/video-index.db'
    return VideoIndexModel(db_path)
