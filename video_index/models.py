import datetime
import fastcore.xml as fx
import fort
import logging
import pathlib
import zoneinfo


log = logging.getLogger(__name__)


class Location:
    col_count: int = 3
    thead: fx.FT = fx.Thead(
        fx.Tr(
            fx.Th('Root folder'),
            fx.Th('Last scan started'),
            fx.Th('Last scan completed')
        )
    )

    def __init__(self, root_folder: str, last_scan_started_at: datetime.datetime, last_scan_completed_at: datetime.datetime):
        self.root_folder = root_folder
        self.last_scan_started_at = last_scan_started_at
        self.last_scan_completed_at = last_scan_completed_at

    @property
    def tr(self) -> fx.FT:
        return fx.Tr()(
            fx.Td(fx.Code(self.root_folder)),
            fx.Td(self.last_scan_started_at.astimezone(zoneinfo.ZoneInfo('America/Chicago'))),
            fx.Td(self.last_scan_completed_at.astimezone(zoneinfo.ZoneInfo('America/Chicago')))
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

    def locations_add(self, root_folder: str):
        sql = '''
            insert into locations (root_folder) values (:root_folder)
            on conflict (root_folder) do nothing
        '''
        params = {
            'root_folder': root_folder,
        }
        self.u(sql, params)

    def locations_list(self) -> list[Location]:
        sql = '''
            select root_folder, last_scan_started_at, last_scan_completed_at
            from locations
            order by root_folder
        '''
        return [
            Location(
                row['root_folder'],
                datetime.datetime.fromisoformat(row['last_scan_started_at'] or '2000-01-01T00:00:00Z'),
                datetime.datetime.fromisoformat(row['last_scan_completed_at'] or '2000-01-01T00:00:00Z'),
            )
            for row in self.q(sql)
        ]

    def migrate(self):
        log.info(f'Database schema version is {self.version}')
        if self.version < 1:
            log.info('Migrating to database schema version 1')
            self.u('''
                create table schema_versions (
                    schema_version int,
                    migration_applied_at text
                )
            ''')
            self.version = 1
        if self.version < 2:
            log.info('Migrating to database schema version 2')
            self.u('''
                create table locations (
                    root_folder text primary key,
                    last_scan_started_at text,
                    last_scan_completed_at text
                )
            ''')
            self.version = 2

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
