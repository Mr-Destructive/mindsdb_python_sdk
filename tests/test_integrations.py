import sys
import unittest
import os
import os.path
import time
import json
from subprocess import Popen
import psutil
from mindsdb_sdk import SDK
import common


def get_integration_creds():
    _var_name = 'DATABASE_CREDENTIALS_STRINGIFIED_JSON'
    _var_value = os.getenv(_var_name)
    if _var_value is None:
        with open(os.path.join(os.path.expanduser("~"), '.mindsdb_credentials.json'), 'r') as fp:
            _var_value = fp.read()
    assert _var_value is not None, _var_name + ' ' + 'is not set'
    return json.loads(_var_value)


class TestDatasources(unittest.TestCase):
    start_backend = True

    @classmethod
    def setUpClass(cls):
        if cls.start_backend:
            cls.sp = Popen(
                ['python', '-m', 'mindsdb', '--api', 'http'],
                close_fds=True
            )
            time.sleep(40)
        cls.sdk = SDK('http://localhost:47334')
        cls.integrations = cls.sdk.integrations
        if common.ENV in ('all', 'cloud'):
            cloud_host = common.CLOUD_HOST
            cloud_user, cloud_pass = common.generate_credentials(cloud_host)
            cls.cloud_sdk = SDK(cloud_host, user=cloud_user, password=cloud_pass)
            cls.cloud_integrations = cls.cloud_sdk.integrations

        # need to have a uniq name for each launch to avoid race condition in cloud
        # mongo_darwin_python_3.8
        cls.integration_suffix = f"{sys.platform}_python{sys.version.split(' ')[0]}_{hash(os.uname())}"
        cls.integration_creds = get_integration_creds()

    @classmethod
    def tearDownClass(cls):
        if cls.start_backend:
            try:
                conns = psutil.net_connections()
                pid = [x.pid for x in conns if x.status == 'LISTEN' and x.laddr[1] == 47334 and x.pid is not None]
                if len(pid) > 0:
                    os.kill(pid[0], 9)
                cls.sp.kill()
            except Exception:
                pass
            time.sleep(40)

    def list_info(self, integrations):
        intg_arr = integrations.list_integrations()
        self.assertTrue(isinstance(intg_arr,list))

    def add_integration(self, _type, integrations):
        origin_name = f"{_type}_{self.integration_suffix}"
        try:
            del integrations[origin_name]
        except Exception as e:
            print(f"Attempting to delete {origin_name} has finished with {e}")

        integration_params = self.integration_creds[_type]
        integration_params["type"] = _type
        integration_params["publish"] = False
        integration_params["user"] = "original_user"
        integrations[origin_name] = {"params": integration_params}
        self.assertTrue(isinstance(integrations[origin_name].get_info(), dict))
        self.assertTrue(len(integrations[origin_name]) > 5)

    def update_integration(self, _type, integrations, to_update={'user': 'updated_user'}):
        origin_name = f"{_type}_{self.integration_suffix}"
        integration = integrations[origin_name]
        self.assertTrue(integration is not None)
        update_params = self.integration_creds[_type]
        update_params["type"] = _type
        # update_params["user"] = "updated_user"
        if to_update is not None:
            update_params.update(to_update)

        integration.update({"params": update_params})

        self.assertTrue(isinstance(integration.get_info(), dict))
        if to_update is not None:
            for k in to_update:
                self.assertTrue(integration.get_info()[k] == to_update[k])

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_1_list_info_local(self):
        self.list_info(self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_2_add_clickhouse_local(self):
        self.add_integration("clickhouse", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_3_update_clickhouse_local(self):
        self.update_integration("clickhouse", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_4_add_mysql_local(self):
        self.add_integration("mysql", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_5_update_mysql_local(self):
        self.update_integration("mysql", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_6_add_mongo_local(self):
        self.add_integration("mongodb", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_7_update_mongo_local(self):
        self.update_integration("mongodb", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_8_add_mariadb_local(self):
        self.add_integration("mariadb", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_9_update_mariadb_local(self):
        self.update_integration("mariadb", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_10_add_postgres_local(self):
        self.add_integration("postgres", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_11_update_postgres_local(self):
        self.update_integration("postgres", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_12_add_snowflake_local(self):
        self.add_integration("snowflake", self.integrations)

    @unittest.skipIf(common.ENV == 'cloud', "launched for cloud")
    def test_13_update_snowflake_local(self):
        self.update_integration("snowflake", self.integrations, to_update={'test': True})

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_1_list_info_cloud(self):
        self.list_info(self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_2_clickhouse_cloud(self):
        self.add_integration("clickhouse", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_3_update_clickhouse_cloud(self):
        self.update_integration("clickhouse", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_4_add_myslq_cloud(self):
        self.add_integration("mysql", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_5_update_mysql_cloud(self):
        self.update_integration("mysql", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_6_add_mongo_cloud(self):
        self.add_integration("mongodb", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_7_update_mongo_cloud(self):
        self.update_integration("mongodb", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_8_add_mariadb_cloud(self):
        self.add_integration("mariadb", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_9_update_mariadb_cloud(self):
        self.update_integration("mariadb", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_10_add_postgres_cloud(self):
        self.add_integration("postgres", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_11_update_postgres_cloud(self):
        self.update_integration("postgres", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_12_add_snowflake_cloud(self):
        self.add_integration("snowflake", self.cloud_integrations)

    @unittest.skipIf(common.ENV == 'local', "launched for local")
    def test_13_update_snowflake_cloud(self):
        self.update_integration("snowflake", self.cloud_integrations, to_update={'test': True})


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[-1] == "--no_backend_instance":
        # need to remove if from arg list
        # mustn't provide it into unittest.main
        sys.argv.pop()
        TestDatasources.start_backend = False
    unittest.main()
