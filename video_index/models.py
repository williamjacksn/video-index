import datetime
import fort
import logging
import pathlib

log = logging.getLogger(__name__)


class VideoIndexModel(fort.SQLiteDatabase):
    _version: int = None

    def _table_exists(self, table_name: str) -> bool:
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
        if t and t == 'table_name':
            return True
        return False

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
