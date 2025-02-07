import datetime
import fastcore.xml as fx
import flask
import fort
import logging
import pathlib
import zoneinfo

log = logging.getLogger(__name__)
tz = zoneinfo.ZoneInfo('America/Chicago')


class File:
    def __init__(self, file_path: pathlib.Path, suffix: str, notes: str):
        self.file_path = file_path
        self.suffix = suffix
        self.notes = notes


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
                file_path, suffix, scanned, last_scanned_at
            ) values (
                :file_path, :suffix, 1, :last_scanned_at
            )
        '''
        params = {
            'file_path': str(file_path),
            'suffix': file_path.suffix,
            'last_scanned_at': datetime.datetime.now(datetime.UTC).isoformat(),
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
                    suffix text,
                    scanned integer,
                    last_scanned_at text,
                    notes text
                )
            ''')
            self.version = 1

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
